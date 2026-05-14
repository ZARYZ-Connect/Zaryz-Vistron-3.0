# security/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from visitors.models import VisitRequest
from django.http import JsonResponse
from django.urls import reverse
from django.core.mail import send_mail
from dashboard.utils.mail import send_mail_template
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from urllib.parse import urlparse, parse_qs
import uuid as _uuid
import datetime
from django.db.models import Q
from django.core.paginator import Paginator


def security_required(user):
    return (user.is_authenticated and user.role in ('security', 'reception')) or user.is_superuser


# ------------------------------------------------------
# Helper: build detailed timing info (used by QR + badge)
# ------------------------------------------------------
def build_visit_timing_info(visit):

    now_local = timezone.now()
    today_local = timezone.localdate()

    visit_date = getattr(visit, 'visit_date', None)
    start_time = getattr(visit, 'start_time', None)
    end_time = getattr(visit, 'end_time', None)

    MAX_EARLY_MINUTES = 30
    MIN_REMAINING_MINUTES = 15

    def fmt_date(d):
        return d.strftime('%d-%m-%Y') if d else None

    def fmt_time(t):
        return t.strftime('%I:%M %p') if t else None

    date_str = fmt_date(visit_date)
    start_str = fmt_time(start_time)
    end_str = fmt_time(end_time)

    # Scheduled display (metadata only)
    if start_str and end_str:
        time_str = f"{start_str} - {end_str}"
    elif start_str:
        time_str = start_str
    elif end_str:
        time_str = f"until {end_str}"
    else:
        time_str = None

    if date_str and time_str:
        scheduled_display = f"{date_str}, {time_str}"
    elif date_str:
        scheduled_display = date_str
    elif time_str:
        scheduled_display = time_str
    else:
        scheduled_display = None

    # No schedule at all
    if not visit_date and not start_time and not end_time:
        return {
            'allowed': True,
            'message': 'Visit valid. No schedule restrictions.',
            'scheduled': None,
        }

    # Date rules
    if visit_date:
        if visit_date < today_local:
            return {
                'allowed': False,
                'message': 'Visit expired.',
                'scheduled': scheduled_display,
            }

        if visit_date > today_local:
            return {
                'allowed': False,
                'message': 'Visit scheduled for a future date.',
                'scheduled': scheduled_display,
            }

    start_dt = None
    end_dt = None

    if visit_date and start_time:
        start_dt = timezone.make_aware(
            datetime.datetime.combine(visit_date, start_time)
        )

    if visit_date and end_time:
        end_dt = timezone.make_aware(
            datetime.datetime.combine(visit_date, end_time)
        )

    if start_dt and not end_dt:
        end_dt = start_dt + datetime.timedelta(hours=2)

    # Expired window
    if end_dt:
        remaining_minutes = int((end_dt - now_local).total_seconds() / 60)

        if remaining_minutes < 0:
            return {
                'allowed': False,
                'message': 'Visit window has already ended.',
                'scheduled': scheduled_display,
            }

        if remaining_minutes < MIN_REMAINING_MINUTES:
            return {
                'allowed': False,
                'message': 'Visit window is about to close. Entry not permitted.',
                'scheduled': scheduled_display,
            }

    # Early / Late / On-time
    if start_dt:
        diff_minutes = int((start_dt - now_local).total_seconds() / 60)

        if now_local < start_dt:
            if diff_minutes > MAX_EARLY_MINUTES:
                return {
                    'allowed': False,
                    'message': f'Visitor arrived {diff_minutes} minutes early.',
                    'scheduled': scheduled_display,
                }
            else:
                return {
                    'allowed': True,
                    'message': f'Visitor arrived {diff_minutes} minutes early.',
                    'scheduled': scheduled_display,
                }

        else:
            late_minutes = int((now_local - start_dt).total_seconds() / 60)

            if late_minutes == 0:
                return {
                    'allowed': True,
                    'message': 'Visitor arrived on time.',
                    'scheduled': scheduled_display,
                }
            else:
                return {
                    'allowed': True,
                    'message': f'Visitor arrived {late_minutes} minutes late.',
                    'scheduled': scheduled_display,
                }

    return {
        'allowed': True,
        'message': 'Visit valid.',
        'scheduled': scheduled_display,
    }

# ------------------------------------------------------
# Dashboard + lists
# ------------------------------------------------------
@login_required
@user_passes_test(security_required)
def security_dashboard(request):
    today = timezone.localdate()

    todays_qs = VisitRequest.objects.filter(
        Q(visit_date=today) | Q(created_at__date=today)
    )

    counts = {
        'total': todays_qs.count(),
        'checked_in': todays_qs.filter(status='checked_in').count(),
        'awaiting': todays_qs.filter(status='approved').count(),
        'checked_out': todays_qs.filter(status='checked_out').count(),
    }

    visits_qs = todays_qs.order_by('-created_at')

    per_page = request.GET.get('per_page', '5')
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 5

    paginator = Paginator(visits_qs, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'security/dashboard.html',
        {
            'security_counts': counts,
            'todays': page_obj,
        }
    )


@login_required
@user_passes_test(security_required)
def checked_in_list(request):
    today = timezone.localdate()
    visits = VisitRequest.objects.filter(
        Q(visit_date=today) | Q(created_at__date=today),
        status='checked_in'
    ).order_by('-actual_checkin', '-created_at')

    per_page = request.GET.get('per_page', '5')
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 5

    paginator = Paginator(visits, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Checked-in Visitors (Today)',
        'visits': page_obj,
    }
    return render(request, 'security/status_list.html', context)


@login_required
@user_passes_test(security_required)
def awaiting_list(request):
    today = timezone.localdate()
    visits = VisitRequest.objects.filter(
        Q(visit_date=today) | Q(created_at__date=today),
        status='approved'
    ).order_by('-created_at')

    per_page = request.GET.get('per_page', '5')
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 5

    paginator = Paginator(visits, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Awaiting Visitors (Today)',
        'visits': page_obj,
    }
    return render(request, 'security/status_list.html', context)


@login_required
@user_passes_test(security_required)
def checked_out_list(request):
    today = timezone.localdate()
    visits = VisitRequest.objects.filter(
        Q(visit_date=today) | Q(created_at__date=today),
        status='checked_out'
    ).order_by('-actual_checkout', '-created_at')

    per_page = request.GET.get('per_page', '5')
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 5

    paginator = Paginator(visits, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Checked-out Visitors (Today)',
        'visits': page_obj,
    }
    return render(request, 'security/status_list.html', context)


@login_required
@user_passes_test(security_required)
def scan_qr(request):
    return render(request, 'security/scan_qr.html')

@login_required
@user_passes_test(security_required)
def all_today_list(request):
    today = timezone.localdate()

    visits = VisitRequest.objects.filter(
        Q(visit_date=today) | Q(created_at__date=today)
    ).order_by('-created_at')

    per_page = request.GET.get('per_page', '5')
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 5

    paginator = Paginator(visits, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'All Visitors (Today)',
        'visits': page_obj,
    }

    return render(request, 'security/status_list.html', context)


# ------------------------------------------------------
# QR VERIFY – uses build_visit_timing_info
# ------------------------------------------------------
@csrf_exempt
@login_required
@user_passes_test(security_required)
def verify_qr(request):
    """
    Returns JSON:
      { ok, allowed, message, redirect?, scheduled? }
    """
    # ---------- 1. Read payload ----------
    try:
        ct = (request.META.get('CONTENT_TYPE') or '').lower()
        if ct.startswith('application/json') or ct.startswith('text/json'):
            payload = json.loads(request.body.decode('utf-8') or '{}')
            code = (
                payload.get('uuid')
                or payload.get('code')
                or payload.get('qr')
                or payload.get('data')
            )
        else:
            code = (
                request.POST.get('uuid')
                or request.POST.get('code')
                or request.POST.get('qr')
                or request.POST.get('badge_id')
            )
    except Exception:
        return JsonResponse(
            {'ok': False, 'allowed': False, 'message': 'Invalid request body'},
            status=400
        )

    if not code:
        return JsonResponse(
            {'ok': False, 'allowed': False, 'message': "No 'code' provided"},
            status=400
        )

    scanned = str(code).strip().strip('"').strip("'")

    # ---------- 2. Normalize URL token if QR contains a link ----------
    try:
        parsed = urlparse(scanned)
        if parsed.scheme in ('http', 'https') and (parsed.path or parsed.query):
            parts = [p for p in parsed.path.split('/') if p]
            if parts:
                scanned = parts[-1]
            else:
                qs = parse_qs(parsed.query)
                for key in ('token', 'q', 'id', 'uuid', 'badge', 'badge_id'):
                    if qs.get(key):
                        scanned = qs.get(key)[0]
                        break
    except Exception:
        pass

    # ---------- 3. Find VisitRequest ----------
    visit = None
    
    # Try UUID first
    try:
        uuid_obj = _uuid.UUID(scanned)
        visit = VisitRequest.objects.filter(uuid=uuid_obj).first()
    except Exception:
        pass

    # NEW: Try numeric ID (often extracted from /badge/ID/ URL)
    if not visit and scanned.isdigit():
        visit = VisitRequest.objects.filter(id=int(scanned)).first()

    # Fallbacks for badge_id or partial paths
    if not visit:
        visit = VisitRequest.objects.filter(badge_id__iexact=scanned).first()
    if not visit:
        visit = VisitRequest.objects.filter(qr_code__icontains=scanned).first()
    if not visit:
        visit = VisitRequest.objects.filter(badge_id__icontains=scanned).first()
    if not visit:
        try:
            visit = VisitRequest.objects.filter(qr_code__iendswith=scanned).first()
        except Exception:
            pass

    if not visit:
        return JsonResponse(
            {'ok': False, 'allowed': False, 'message': 'No matching visitor found.'},
            status=404
        )

    # ---------- 4. Status checks ----------
    status = getattr(visit, 'status', None)
    if status == 'checked_out':
        return JsonResponse({
            'ok': True,
            'allowed': False,
            'message': 'Visitor has already checked out.'
        })

    if status == 'checked_in':
        timing = build_visit_timing_info(visit)
        return JsonResponse({
            'ok': True,
            'allowed': False,
            'message': 'Visitor already checked in.',
            'scheduled': timing.get('scheduled'),
            'redirect': reverse('security:badge_detail', args=[visit.id])
        })

    # ---------- 5. Timing rules via helper ----------
    timing = build_visit_timing_info(visit)

    if not timing['allowed']:
        return JsonResponse({
            'ok': True,
            'allowed': False,
            'message': timing['message'],
            'scheduled': timing['scheduled'],
        })

    return JsonResponse({
        'ok': True,
        'allowed': True,
        'message': timing['message'],
        'scheduled': timing['scheduled'],
        'redirect': reverse('security:badge_detail', args=[visit.id])
    })


# ------------------------------------------------------
# Badge lookup – also uses build_visit_timing_info
# ------------------------------------------------------
@login_required
@user_passes_test(security_required)
def badge_lookup(request):
    visit = None
    time_info = None

    if request.method == 'POST':
        badge_id = request.POST.get('badge_id')
        visit = VisitRequest.objects.filter(badge_id=badge_id).first()
        if visit:
            time_info = build_visit_timing_info(visit)

    return render(request, 'security/badge_lookup.html', {
        'visit': visit,
        'time_info': time_info,
    })


@login_required
@user_passes_test(security_required)
def badge_detail(request, visit_id):
    organization = getattr(request, "organization", None)
    visit = get_object_or_404(
        VisitRequest.objects.for_organization(organization), 
        id=visit_id
    )
    return render(request, 'security/badge_detail.html', {'visit': visit})


import threading

@login_required
@user_passes_test(security_required)
def checkin(request, visit_id):

    organization = getattr(request, "organization", None)

    visit = get_object_or_404(
        VisitRequest.objects.for_organization(organization),
        id=visit_id
    )

    if visit.status == "checked_in":
        return redirect('security:security_dashboard')

    visit.status = 'checked_in'

    if not visit.actual_checkin:
        visit.actual_checkin = timezone.now()

    visit.save()

    context_common = {
        "visitor_name": visit.full_name,
        "badge_id": visit.badge_id,
        "checkin_time": visit.actual_checkin,
        "visit_date": visit.visit_date,
        "organization_name": visit.organization.name,
    }

    # Send emails in background thread (non-blocking UI)
    def send_notifications():

        # Visitor Email
        try:
            send_mail_template(
                    "checkin_receipt",
                    visit.email,
                    context_common,
                    request=request 
             )
        except Exception as e:
            print("Visitor check-in email failed:", str(e))

        # Employee Email
        if visit.whom_to_meet_employee and visit.whom_to_meet_employee.email:
            try:
                send_mail_template(
                    "employee_visitor_checkin",
                    visit.whom_to_meet_employee.email,
                    {
                        "employee_name": visit.whom_to_meet_employee.name,
                        **context_common
                    },
                    request=request
                )
            except Exception as e:
                print("Employee check-in email failed:", str(e))

    threading.Thread(target=send_notifications, daemon=True).start()

    return redirect('security:security_dashboard')



@login_required
@user_passes_test(security_required)
def checkout(request, visit_id):

    organization = getattr(request, "organization", None)

    visit = get_object_or_404(
        VisitRequest.objects.for_organization(organization),
        id=visit_id
    )

    if visit.status == "checked_out":
        return redirect('security:security_dashboard')

    visit.status = 'checked_out'

    if not visit.actual_checkin:
        visit.actual_checkin = timezone.now()

    visit.actual_checkout = timezone.now()
    visit.save()

    context_common = {
        "visitor_name": visit.full_name,
        "badge_id": visit.badge_id,
        "checkin_time": visit.actual_checkin,
        "checkout_time": visit.actual_checkout,
        "visit_date": visit.visit_date,
        "organization_name": visit.organization.name,
    }

    def send_notifications():

        # Visitor Email
        try:
            send_mail_template(
                "checkout_receipt",
                visit.email,
                context_common,
                request=request
            )
        except Exception as e:
            print("Visitor checkout email failed:", str(e))

        # Employee Email
        if visit.whom_to_meet_employee and visit.whom_to_meet_employee.email:
            try:
                send_mail_template(
                    "employee_visitor_checkout",
                    visit.whom_to_meet_employee.email,
                    {
                        "employee_name": visit.whom_to_meet_employee.name,
                        **context_common
                    },
                    request=request
                )
            except Exception as e:
                print("Employee checkout email failed:", str(e))

    threading.Thread(target=send_notifications, daemon=True).start()

    return redirect('security:security_dashboard')
