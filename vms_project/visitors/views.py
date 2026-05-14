# visitors/views.py

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.http import Http404, HttpResponse, HttpResponseNotFound

from datetime import timedelta
import random, string, threading, os, base64, time

from django.core.files.base import ContentFile

from .forms import VisitRequestForm
from .models import VisitRequest, OTP, VisitType
from .utils import (
    make_approval_token,
    load_approval_token,
    save_qr_to_filefield,
)

from dashboard.utils.mail import send_mail_template


# ==================================================
# HELPERS
# ==================================================

def _save_photo_from_dataurl(dataurl, name_prefix="visitor"):
    try:
        header, imgstr = dataurl.split(";base64,")
        ext = header.split("/")[-1]
        return ContentFile(
            base64.b64decode(imgstr),
            name=f"{name_prefix}_{int(time.time())}.{ext}",
        )
    except Exception:
        return None


def _time_range(visit):
    if visit.start_time and visit.end_time:
        return f"{visit.start_time.strftime('%H:%M')} - {visit.end_time.strftime('%H:%M')}"
    if visit.start_time:
        return visit.start_time.strftime('%H:%M')
    return ""


def require_organization(request):
    organization = getattr(request, "organization", None)
    
    # 🛠️ DEV FALLBACK: If on localhost/debug, auto-pick first org to skip domain requirements
    if not organization and settings.DEBUG:
        from organizations.models import Organization
        organization = Organization.objects.filter(is_active=True).first()
        if organization:
            request.organization = organization

    if not organization:
        raise Http404("Organization not resolved")
    return organization


# ==================================================
# PLATFORM / TENANT HOME
# ==================================================

def home(request):
    """
    Main domain (vistron.zaryz.com) -> Platform landing
    Tenant domain (*.vistron.zaryz.com) -> Visitor home
    """
    # 🛠️ DEV FALLBACK: If on localhost/debug, auto-pick first org to skip domain requirements
    if not getattr(request, "organization", None) and settings.DEBUG:
        from organizations.models import Organization
        request.organization = Organization.objects.filter(is_active=True).first()

    if getattr(request, "organization", None):
        if not request.organization.is_active:
            raise Http404("Organization inactive")

        return render(

            request,
            "visitors/index.html",
            {
                "organization": request.organization,
                "org_code": request.organization.code,
            },
        )

    return render(request, "platform/index.html")


# ==================================================
# VISITOR REGISTRATION
# ==================================================

def visit_register(request):
    organization = require_organization(request)
    current_step = 1  # default

    if request.method == "POST":
        form = VisitRequestForm(
            request.POST,
            request.FILES,
            organization=organization
        )

        form.instance.organization = organization

        if form.is_valid():
            visit = form.save(commit=False)
            visit.status = "pending"

            # Photo handling
            photo_data = form.cleaned_data.get("photo")
            if isinstance(photo_data, str) and photo_data.startswith("data:image"):
                photo_file = _save_photo_from_dataurl(photo_data)
                if photo_file:
                    visit.photo.save(photo_file.name, photo_file, save=False)

            visit.save()

            # OTP
            code = "".join(random.choices(string.digits, k=6))
            OTP.objects.create(
                visit=visit,
                code=code,
                expires_at=timezone.now() + timedelta(minutes=5),
            )

            if settings.DEBUG:
                request.session["DEV_LAST_OTP"] = code

            send_mail_template(
                "otp_email",
                visit.email,
                {
                    "visitor_name": visit.full_name,
                    "otp_code": code,
                    "otp_minutes": 5,
                },
                request=request,
            )

            request.session["visit_id"] = visit.id
            return redirect("visitors:otp_validate")

        # 🔥 DETECT WHICH STEP HAS ERRORS
        if any(field in form.errors for field in ["visit_type", "visit_date", "start_time", "end_time"]):
            current_step = 2
        elif any(field in form.errors for field in ["department", "whom_to_meet_employee", "purpose"]):
            current_step = 3
        elif "photo" in form.errors:
            current_step = 4
        else:
            current_step = 1

    else:
        form = VisitRequestForm(organization=organization)

    return render(
        request,
        "visitors/register.html",
        {
            "form": form,
            "organization": organization,
            "org_code": organization.code,
            "current_step": current_step,   # 🔥 IMPORTANT
        },
    )



# ==================================================
# OTP VALIDATION
# ==================================================

def otp_validate(request):
    organization = require_organization(request)
    # Check session first, fallback to POST payload if session dropped
    visit_id = request.session.get("visit_id") or request.POST.get("visit_id")

    if not visit_id:
        raise Http404("Invalid session. Please restart registration.")

    visit = get_object_or_404(
        VisitRequest.objects.for_organization(organization),
        id=visit_id,
    )

    if request.method == "POST":
        otp_code = request.POST.get("otp", "").strip()

        otp_obj = (
            OTP.objects.filter(
                visit=visit,
                code=otp_code,
                expires_at__gt=timezone.now(),
            )
            .order_by("-id")
            .first()
        )

        if not otp_obj:
            return render(
                request,
                "visitors/otp_validate.html",
                {"error": "Verification failed. Please try again."},
            )

        otp_obj.delete()

        send_mail_template(
            "visitor_thanks",
            visit.email,
            {
                "visitor_name": visit.full_name,
            "approver_name": visit.whom_to_meet_employee.name if visit.whom_to_meet_employee else "",
            "visit_date": visit.visit_date,
            "visit_start_time": visit.start_time,
            "visit_end_time": visit.end_time,
            "visit_id": visit.id,
            },
            request=request,
        )

        if visit.whom_to_meet_employee:
            approver = visit.whom_to_meet_employee

            token = make_approval_token(
                {"visit": str(visit.uuid), "org": str(organization.id)}
            )

            approve_url = request.build_absolute_uri(
                reverse("visitors:approve", args=[visit.uuid, token])
            )

            reject_url = f"{approve_url}?action=reject"

            photo_url = request.build_absolute_uri(
                reverse("visitors:visitor_photo", args=[visit.uuid])
            )

            send_mail_template(
                "approver_notify",
                approver.email,
                {
                    "approver_name": approver.name,
                    "visitor_name": visit.full_name,
                    "visit_date": visit.visit_date,
                    "visit_start_time": visit.start_time,
                    "visit_end_time": visit.end_time,
                    "visitor_phone": visit.phone,
                    "visitor_email": visit.email,
                    "purpose": visit.purpose,
                    "approve_url": approve_url,
                    "reject_url": reject_url,
                    "visitor_photo_url": photo_url,
                },
                request=request,
            )

        return render(request, "visitors/otp_success.html", {"visit": visit})

    return render(request, "visitors/otp_validate.html")


# ==================================================
# RESEND OTP (TENANT SAFE)
# ==================================================

@require_http_methods(["POST"])
def resend_otp(request):
    organization = require_organization(request)
    visit_id = request.session.get("visit_id")
    
    # Fallback to JSON payload if session dropped
    if not visit_id:
        import json
        try:
            payload = json.loads(request.body)
            visit_id = payload.get("visit_id")
        except Exception:
            pass

    if not visit_id:
        raise Http404("Invalid session")

    visit = get_object_or_404(
        VisitRequest.objects.for_organization(organization),
        id=visit_id,
    )

    # 🔒 RATE LIMIT: Allow resend only once every 60 seconds
    last_otp = OTP.objects.filter(visit=visit).order_by("-created_at").first()

    if last_otp and (timezone.now() - last_otp.created_at).total_seconds() < 30:
        return JsonResponse({
            "success": False,
            "message": "Please wait before requesting a new code."
        })

    # Generate new OTP
    code = "".join(random.choices(string.digits, k=6))

    OTP.objects.create(
        visit=visit,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    if settings.DEBUG:
        request.session["DEV_LAST_OTP"] = code

    send_mail_template(
        "otp_email",
        visit.email,
        {
            "visitor_name": visit.full_name,
            "otp_code": code,
            "otp_minutes": 5,
        },
        request=request,
    )

    return JsonResponse({
        "success": True,
        "message": "A new verification code has been sent."
    })

# ==================================================
# APPROVAL FLOW
# ==================================================

@require_http_methods(["GET", "POST"])
def approve(request, uuid, token):
    payload = load_approval_token(token)
    organization = require_organization(request)

    if str(organization.id) != payload.get("org"):
        raise Http404("Invalid approval domain")

    visit = get_object_or_404(
        VisitRequest.objects.for_organization(organization),
        uuid=uuid,
    )

    if visit.status != "pending":
        return render(
            request,
            "visitors/approve_already_done.html",
            {"visit": visit},
        )

    if request.method == "GET":
        return render(
            request,
            "visitors/approve_form.html",
            {"visit": visit, "token": token},
        )

    decision = request.POST.get("decision")

    if decision == "accept":
        visit.status = "approved"
        visit.badge_id = visit.badge_id or f"BADGE-{visit.id:06d}"

        qr_target_url = request.build_absolute_uri(reverse("security:badge_detail", args=[visit.id]))
        save_qr_to_filefield(visit, qr_target_url, field_name="qr_code")
        visit.save()

        qr_url = None
        if visit.qr_code:
            qr_url = request.build_absolute_uri(reverse("visitors:qr_pass", args=[visit.uuid]))

        action = "approved"

    elif decision == "reject":
        visit.status = "rejected"
        visit.save()

        qr_url = None
        action = "rejected"

    else:
        return redirect(request.path)

    threading.Thread(
        target=lambda: send_mail_template(
            "approval_result",
            visit.email,
            {
                "visitor_name": visit.full_name,
                "approver_name": visit.whom_to_meet_employee.name if visit.whom_to_meet_employee else "",
                "visit_date": visit.visit_date,
                "visit_start_time": visit.start_time,
                "visit_end_time": visit.end_time,
                "status": action,
                "badge_id": visit.badge_id if action == "approved" else "",
                "qr_url": qr_url,
                "reason": request.POST.get("reason", ""),
            },
            request=request,
        ),
        daemon=True,
    ).start()

    return render(
        request,
        "visitors/approve_done.html",
        {"visit": visit, "action": action},
    )


# ==================================================
# VISITOR PHOTO (ORG SAFE)
# ==================================================

def serve_visitor_photo(request, uuid):
    organization = require_organization(request)

    visit = get_object_or_404(
        VisitRequest.objects.for_organization(organization),
        uuid=uuid,
    )

    if visit.photo and hasattr(visit.photo, "path") and os.path.exists(visit.photo.path):
        with open(visit.photo.path, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")

    return serve_default_image()


def serve_default_image():
    for static_dir in settings.STATICFILES_DIRS:
        path = os.path.join(static_dir, "img", "default-visitor.jpg")
        if os.path.exists(path):
            with open(path, "rb") as f:
                return HttpResponse(f.read(), content_type="image/jpeg")

    return HttpResponseNotFound("Image not found")

# ==================================================
# AJAX: GET EMPLOYEES BY DEPARTMENT
# ==================================================

from django.http import JsonResponse
from dashboard.models import Employee

def get_department_employees(request):
    organization = getattr(request, "organization", None)
    dept_id = request.GET.get("department")

    if not organization or not dept_id:
        return JsonResponse({"employees": []})

    employees = Employee.objects.filter(
        organization=organization,
        department_id=dept_id
    )

    data = []
    for emp in employees:
        job = emp.job_role.name if emp.job_role else ""
        label = f"{emp.name} ({job})" if job else emp.name

        data.append({
            "id": emp.id,
            "name": label
        })

    return JsonResponse({"employees": data})

def qr_pass(request, uuid):
    organization = require_organization(request)
    visit = get_object_or_404(
        VisitRequest.objects.for_organization(organization),
        uuid=uuid,
    )
    
    # If not approved, can't see pass
    if visit.status not in ('approved', 'checked_in'):
        raise Http404("Pass not available for pending or rejected visits.")

    return render(request, "visitors/qr_pass.html", {
        "visit": visit,
        "organization": organization,
    })
