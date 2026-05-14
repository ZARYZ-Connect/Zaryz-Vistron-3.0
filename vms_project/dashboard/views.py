# dashboard/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django import forms
from django.contrib.auth.hashers import make_password
import csv
import io
from django.db import transaction
from accounts.models import User
from visitors.models import VisitRequest, VisitType
from visitors.utils import save_qr_to_filefield
from .models import Employee, Department, JobRole, MailTemplate
from organizations.models import OrganizationMailConfig
from django.contrib import messages
from .forms import OrganizationMailConfigForm
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
import json
from django.db.models import Q
# ==================================================
# SAAS SECURITY GUARDS (CRITICAL)
# ==================================================

def require_org_admin(request):
    """
    Verifies the request comes from a valid tenant domain AND the user has admin rights.

    SECURITY RULES:
    - organization MUST be resolved by the middleware (domain-based) — no domain fallback.
    - The user's org must match the domain's org (no cross-org access).
    - The user must have admin or superuser role.
    - Superusers must ALSO be on a valid tenant domain (use /admin for platform tasks).
    """
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    # organization MUST come from the middleware — no auto-resolve fallbacks.
    organization = getattr(request, "organization", None)

    if not organization:
        raise Http404(
            "No organization is registered for this domain. "
            "Please access the application through your organization's URL."
        )

    # Cross-org access prevention (superusers are also bound to their tenant domain)
    if not request.user.is_superuser and request.user.organization_id != organization.id:
        raise Http404("Access denied: you do not belong to this organization.")

    if not (request.user.role == "admin" or request.user.is_superuser):
        raise Http404("Admin privileges required.")

    return organization


def require_security_user(request):
    """
    Verifies the request comes from a valid tenant domain AND the user has security/reception rights.
    """
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    # organization MUST come from the middleware — no auto-resolve fallbacks.
    organization = getattr(request, "organization", None)

    if not organization:
        raise Http404(
            "No organization is registered for this domain. "
            "Please access the application through your organization's URL."
        )

    if not request.user.is_superuser and request.user.organization_id != organization.id:
        raise Http404("Cross-organization access denied.")

    if request.user.role not in ["security", "reception"] and not request.user.is_superuser:
        raise Http404("Security access only.")

    return organization


# ==================================================
# ADMIN DASHBOARD
# ==================================================

@login_required
def admin_dashboard(request):

    org = require_org_admin(request)

    timeframe = request.GET.get("timeframe", "daily")

    all_visitors = VisitRequest.objects.filter(organization=org)
    visitors = all_visitors

    # ===== GROUP BASED ON TIMEFRAME =====
    if timeframe == "weekly":
        group = TruncWeek("visit_date")

    elif timeframe == "monthly":
        group = TruncMonth("visit_date")

    elif timeframe == "yearly":
        group = TruncYear("visit_date")

    else:
        timeframe = "daily"
        group = TruncDay("visit_date")

    analytics = (
        visitors
        .annotate(period=group)
        .values("period")
        .annotate(total=Count("id"))
        .order_by("period")
    )

    labels = []
    values = []

    for row in analytics:
        period = row["period"]

        if timeframe == "yearly":
            label = period.strftime("%Y")

        elif timeframe == "monthly":
            label = period.strftime("%b %Y")

        elif timeframe == "weekly":
            label = "Week " + period.strftime("%W %Y")

        else:
            label = period.strftime("%d %b")

        labels.append(label)
        values.append(row["total"])

    chart_data = {
        "labels": labels,
        "values": values
    }

    context = {

        "active_menu": "dashboard",
        "timeframe": timeframe,

        "total": all_visitors.count(),
        "pending": all_visitors.filter(status="pending").count(),
        "approved": all_visitors.filter(status="approved").count(),

        "employees_count": Employee.objects.filter(organization=org).count(),

        "security_count": User.objects.filter(
            organization=org,
            role__in=["security", "reception"]
        ).count(),

        "chart_data": chart_data,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(chart_data)

    return render(request, "dashboard/admin_dashboard.html", context)


# ==================================================
# VISITORS – ADMIN FLOW
# ==================================================

@login_required
def visitor_list(request):
    org = require_org_admin(request)

    # Get filter params
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    visits_queryset = VisitRequest.objects.filter(
        organization=org
    ).order_by("-visit_date")

    # Apply filters
    if search_query:
        visits_queryset = visits_queryset.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    if status_filter:
        visits_queryset = visits_queryset.filter(status=status_filter)
    
    if start_date:
        visits_queryset = visits_queryset.filter(visit_date__gte=start_date)
    
    if end_date:
        visits_queryset = visits_queryset.filter(visit_date__lte=end_date)

    # NEW: Handle export directly within the list view
    if request.GET.get('export') == 'true':
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="visitors_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(["Name", "Email", "Phone", "Visit Date", "Status", "Meeting With"])
        
        for v in visits_queryset:
            whom = v.whom_to_meet_employee.name if v.whom_to_meet_employee else (v.whom_to_meet.get_full_name() if v.whom_to_meet else "")
            writer.writerow([v.full_name, v.email, v.phone, v.visit_date, v.status, whom])
        return response

    per_page = request.GET.get('per_page', '5')
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 5

    paginator = Paginator(visits_queryset, per_page)

    page_number = request.GET.get("page")
    visits = paginator.get_page(page_number)

    # Stats for the new dashboard bar
    today = timezone.localdate()
    pending_count = VisitRequest.objects.filter(organization=org, status="pending").count()
    checked_in_count = VisitRequest.objects.filter(organization=org, status="checked_in").count()
    today_count = VisitRequest.objects.filter(organization=org, visit_date=today).count()

    context = {
        "visits": visits,
        "page_title": "Total Visitors",
        "show_export": True,
        "export_url": "dashboard:export_visitors_csv",
        "search_query": search_query,
        "status_filter": status_filter,
        "start_date": start_date,
        "end_date": end_date,
        "pending_count": pending_count,
        "checked_in_count": checked_in_count,
        "today_count": today_count,
    }

    return render(request, "dashboard/visitor_list.html", context)

@login_required
def visitor_list_by_status(request, status):

    org = require_org_admin(request)

    status = status.lower().strip()

    allowed_status = [
        "pending",
        "approved",
        "checked_in",
        "checked_out",
        "rejected"
    ]

    if status not in allowed_status:
        raise Http404("Invalid visitor status")

    visits_queryset = VisitRequest.objects.filter(
        organization=org,
        status=status
    ).order_by("-visit_date")

    per_page = request.GET.get('per_page', '5')
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 5

    paginator = Paginator(visits_queryset, per_page)

    page_number = request.GET.get("page")
    visits = paginator.get_page(page_number)

    title_map = {
        "pending": "Pending Visitors",
        "approved": "Approved Visitors",
        "checked_in": "Checked-In Visitors",
        "checked_out": "Checked-Out Visitors",
        "rejected": "Rejected Visitors",
    }

    context = {
        "visits": visits,
        "page_title": title_map.get(status, "Visitors"),
        "show_export": False,
        "export_url": None,
    }

    return render(request, "dashboard/visitor_list.html", context)

@login_required
def visitor_detail(request, pk):
    org = require_org_admin(request)
    visit = get_object_or_404(VisitRequest, pk=pk, organization=org)
    return render(request, "dashboard/visitor_detail.html", {"visit": visit})


@require_POST
@login_required
def visitor_approve(request, pk):
    org = require_org_admin(request)
    visit = get_object_or_404(VisitRequest, pk=pk, organization=org)

    if visit.status != "pending":
        return redirect("dashboard:visitor_detail", pk=visit.pk)

    visit.status = "approved"
    visit.badge_id = visit.badge_id or f"BADGE-{visit.id:06d}"
    qr_target_url = request.build_absolute_uri(reverse("security:badge_detail", args=[visit.id]))
    save_qr_to_filefield(visit, qr_target_url, field_name="qr_code")
    visit.save()

    return redirect("dashboard:visitor_detail", pk=visit.pk)


@require_POST
@login_required
def visitor_reject(request, pk):
    org = require_org_admin(request)
    visit = get_object_or_404(VisitRequest, pk=pk, organization=org)

    if visit.status != "pending":
        return redirect("dashboard:visitor_detail", pk=visit.pk)

    visit.status = "rejected"
    visit.save()

    return redirect("dashboard:visitor_detail", pk=visit.pk)


@login_required
def export_visitors_csv(request):
    org = require_org_admin(request)
    
    # Get filter params from GET
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    visits = VisitRequest.objects.filter(organization=org).order_by("-visit_date")

    # Apply same filters as the list view
    if search_query:
        visits = visits.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    if status_filter:
        visits = visits.filter(status=status_filter)
    if start_date:
        visits = visits.filter(visit_date__gte=start_date)
    if end_date:
        visits = visits.filter(visit_date__lte=end_date)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=filtered_visitors.csv"

    writer = csv.writer(response)
    writer.writerow(["Name", "Email", "Phone", "Visit Date", "Status", "Badge ID", "Whom to Meet"])

    for v in visits:
        whom = ""
        if v.whom_to_meet_employee:
            whom = v.whom_to_meet_employee.name
        elif v.whom_to_meet:
            whom = v.whom_to_meet.get_full_name()

        writer.writerow([
            v.full_name,
            v.email,
            v.phone,
            v.visit_date,
            v.status,
            v.badge_id or "",
            whom
        ])

    return response


# ==================================================
# SECURITY DASHBOARD + CHECK-IN / CHECK-OUT
# ==================================================

@login_required
def security_dashboard(request):
    org = require_security_user(request)

    today = timezone.localdate()

    visits_queryset = VisitRequest.objects.filter(
        organization=org,
        visit_date=today,
        status__in=["approved", "checked_in"]
    ).order_by("start_time")

    # Calculate counts for sidebar stats
    security_counts = {
        "total": VisitRequest.objects.filter(organization=org, visit_date=today).count(),
        "checked_in": VisitRequest.objects.filter(organization=org, visit_date=today, status="checked_in").count(),
        "awaiting": VisitRequest.objects.filter(organization=org, visit_date=today, status="approved").count(),
        "checked_out": VisitRequest.objects.filter(organization=org, visit_date=today, status="checked_out").count(),
    }

    visits = visits_queryset

    return render(request, "dashboard/security_dashboard.html", {
        "visits": visits,
        "security_counts": security_counts
    })


@require_POST
@login_required
def security_checkin(request, pk):
    org = require_security_user(request)
    visit = get_object_or_404(
        VisitRequest,
        pk=pk,
        organization=org,
        status="approved"
    )

    visit.status = "checked_in"
    visit.actual_checkin = timezone.now()
    visit.save()

    return redirect("dashboard:security_dashboard")


@require_POST
@login_required
def security_checkout(request, pk):
    org = require_security_user(request)
    visit = get_object_or_404(
        VisitRequest,
        pk=pk,
        organization=org,
        status="checked_in"
    )

    visit.status = "checked_out"
    visit.actual_checkout = timezone.now()
    visit.save()

    return redirect("dashboard:security_dashboard")


# ==================================================
# EMPLOYEES
# ==================================================

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["employee_id", "name", "email", "phone", "department", "job_role"]

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

    def clean_employee_id(self):
        emp_id = self.cleaned_data.get("employee_id")
        if self.organization:
            qs = Employee.objects.filter(
                organization=self.organization,
                employee_id=emp_id
            )
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise forms.ValidationError(
                    "An employee with this ID already exists in your organization."
                )
        return emp_id


@login_required
def employee_list(request):
    org = require_org_admin(request)
    employees = Employee.objects.filter(organization=org)
    departments_count = Department.objects.filter(organization=org).count()
    job_roles_count = JobRole.objects.filter(organization=org).count()
    
    return render(
        request,
        "dashboard/employee_list.html",
        {
            "employees": employees,
            "departments_count": departments_count,
            "job_roles_count": job_roles_count,
        },
    )


@login_required
def employee_add(request):
    org = require_org_admin(request)
    form = EmployeeForm(request.POST or None, organization=org)
    if request.method == "POST" and form.is_valid():
        emp = form.save(commit=False)
        emp.organization = org
        emp.save()
        messages.success(request, "Employee added successfully.")
        return redirect("dashboard:employee_list")
    return render(request, "dashboard/employee_form.html", {"form": form, "is_new": True})


@login_required
def employee_edit(request, pk):
    org = require_org_admin(request)
    emp = get_object_or_404(Employee, pk=pk, organization=org)
    form = EmployeeForm(request.POST or None, instance=emp, organization=org)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Employee updated successfully.")
        return redirect("dashboard:employee_list")
    return render(request, "dashboard/employee_form.html", {"form": form, "is_new": False})


@login_required
def employee_delete(request, pk):
    org = require_org_admin(request)
    emp = get_object_or_404(Employee, pk=pk, organization=org)
    if request.method == "POST":
        emp.delete()
        return redirect("dashboard:employee_list")
    return render(request, "dashboard/employee_delete_confirm.html", {"item": emp})



@login_required
def employee_import_template(request):
    org = require_org_admin(request)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=employee_import_template.csv"

    writer = csv.writer(response)
    writer.writerow(["employee_id", "name", "email", "phone", "department", "job_role"])

    # Optional example row
    writer.writerow(["EMP-001", "John Doe", "john@example.com", "9876543210", "IT", "Developer"])

    return response


@login_required
def employee_import(request):
    org = require_org_admin(request)

    if request.method != "POST":
        return redirect("dashboard:employee_list")

    file = request.FILES.get("file")
    if not file:
        messages.error(request, "No file selected.")
        return redirect("dashboard:employee_list")

    decoded = file.read().decode("utf-8")
    io_string = io.StringIO(decoded)
    reader = csv.DictReader(io_string)

    success_count = 0
    error_rows = []

    for idx, row in enumerate(reader, start=2):  # start=2 because header is row 1
        try:
            emp_id = row.get("employee_id", "").strip()
            name = row.get("name", "").strip()
            email = row.get("email", "").strip()
            phone = row.get("phone", "").strip()
            dept_name = row.get("department", "").strip()
            role_name = row.get("job_role", "").strip()

            if not emp_id or not name:
                raise Exception("Employee ID and Name are required")

            if Employee.objects.filter(organization=org, employee_id=emp_id).exists():
                raise Exception("Employee ID already exists")

            department = None
            if dept_name:
                department = Department.objects.filter(
                    organization=org,
                    name__iexact=dept_name
                ).first()
                if not department:
                    raise Exception(f"Department '{dept_name}' not found")

            job_role = None
            if role_name:
                job_role = JobRole.objects.filter(
                    organization=org,
                    name__iexact=role_name
                ).first()
                if not job_role:
                    raise Exception(f"Job Role '{role_name}' not found")

            Employee.objects.create(
                organization=org,
                employee_id=emp_id,
                name=name,
                email=email,
                phone=phone,
                department=department,
                job_role=job_role
            )

            success_count += 1

        except Exception as e:
            row["error"] = str(e)
            row["row_number"] = idx
            error_rows.append(row)

    # If errors exist → generate error file
    if error_rows:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=employee_import_errors.csv"

        writer = csv.writer(response)
        writer.writerow(["row_number", "employee_id", "name", "email", "phone", "department", "job_role", "error"])

        for row in error_rows:
            writer.writerow([
                row.get("row_number"),
                row.get("employee_id"),
                row.get("name"),
                row.get("email"),
                row.get("phone"),
                row.get("department"),
                row.get("job_role"),
                row.get("error"),
            ])

        return response

    messages.success(request, f"{success_count} employees imported successfully.")
    return redirect("dashboard:employee_list")


# ==================================================
# DEPARTMENTS / JOB ROLES / VISIT TYPES / MAIL TEMPLATES
# ==================================================

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if self.organization:
            qs = Department.objects.filter(organization=self.organization, name__iexact=name)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f"A department named '{name}' already exists.")
        return name


class JobRoleForm(forms.ModelForm):
    class Meta:
        model = JobRole
        fields = ["department", "name"]

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)
        if self.organization:
            self.fields["department"].queryset = Department.objects.filter(organization=self.organization)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if self.organization:
            qs = JobRole.objects.filter(organization=self.organization, name__iexact=name)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f"A job role named '{name}' already exists.")
        return name


class VisitTypeForm(forms.ModelForm):
    class Meta:
        model = VisitType
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if self.organization:
            qs = VisitType.objects.filter(organization=self.organization, name__iexact=name)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f"A visit type named '{name}' already exists.")
        return name


class MailTemplateForm(forms.ModelForm):
    class Meta:
        model = MailTemplate
        fields = ["key", "title", "subject", "body"]

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

    def clean_key(self):
        key = self.cleaned_data.get("key")
        if self.organization:
            qs = MailTemplate.objects.filter(organization=self.organization, key__iexact=key)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f"A mail template with key '{key}' already exists.")
        return key


# ==================================================
# SECURITY / RECEPTION USERS
# ==================================================

class SecurityUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]


@login_required
def security_user_list(request):
    org = require_org_admin(request)
    users = User.objects.filter(
        organization=org,
        role__in=["security", "reception"]
    )
    return render(request, "dashboard/security_user_list.html", {"users": users})


@login_required
def security_user_add(request):
    org = require_org_admin(request)
    form = SecurityUserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.organization = org
        user.role = "security"
        if form.cleaned_data["password"]:
            user.password = make_password(form.cleaned_data["password"])
        user.save()
        return redirect("dashboard:security_user_list")
    return render(request, "dashboard/security_user_form.html", {"form": form, "is_new": True})


@login_required
def security_user_edit(request, pk):
    org = require_org_admin(request)
    user = get_object_or_404(User, pk=pk, organization=org)
    form = SecurityUserForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        u = form.save(commit=False)
        if form.cleaned_data["password"]:
            u.password = make_password(form.cleaned_data["password"])
        u.save()
        return redirect("dashboard:security_user_list")
    return render(request, "dashboard/security_user_form.html", {"form": form, "is_new": False})


@login_required
def security_user_delete(request, pk):
    org = require_org_admin(request)
    user = get_object_or_404(User, pk=pk, organization=org)
    if request.method == "POST":
        user.delete()
        return redirect("dashboard:security_user_list")
    return render(request, "dashboard/security_user_delete_confirm.html", {"item": user})


# ==================================================
# AJAX
# ==================================================

@login_required
def employees_by_department(request, dept_id):
    org = require_org_admin(request)
    employees = Employee.objects.filter(
        organization=org,
        department_id=dept_id
    ).values("id", "name")
    return JsonResponse(list(employees), safe=False)


def public_employees_by_department(request, dept_id):
    organization = getattr(request, "organization", None)
    if not organization:
        return JsonResponse({"employees": []})

    department = get_object_or_404(
        Department,
        id=dept_id,
        organization=organization
    )
    employees = Employee.objects.filter(
        organization=department.organization,
        department=department
    ).values("id", "name")
    return JsonResponse({
        "employees": list(employees)
    })



# ==================================================
# DEPARTMENTS
# ==================================================

@login_required
def department_list(request):
    org = require_org_admin(request)
    items = Department.objects.filter(organization=org)
    total_employees = Employee.objects.filter(organization=org).count()
    return render(
        request,
        "dashboard/department_list.html",
        {
            "items": items,
            "total_employees": total_employees,
        },
    )

@login_required
def department_add(request):
    org = require_org_admin(request)
    form = DepartmentForm(request.POST or None, organization=org)
    if request.method == "POST" and form.is_valid():
        dept = form.save(commit=False)
        dept.organization = org
        dept.save()
        messages.success(request, "Department added successfully.")
        return redirect("dashboard:department_list")
    return render(
        request,
        "dashboard/department_form.html",
        {"form": form, "is_new": True},
    )


@login_required
def department_edit(request, pk):
    org = require_org_admin(request)
    dept = get_object_or_404(Department, pk=pk, organization=org)
    form = DepartmentForm(request.POST or None, instance=dept, organization=org)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Department updated successfully.")
        return redirect("dashboard:department_list")
    return render(
        request,
        "dashboard/department_form.html",
        {"form": form, "is_new": False},
    )


@login_required
def department_delete(request, pk):
    org = require_org_admin(request)
    dept = get_object_or_404(Department, pk=pk, organization=org)
    if request.method == "POST":
        dept.delete()
        return redirect("dashboard:department_list")
    return render(
        request,
        "dashboard/department_delete_confirm.html",
        {"item": dept},
    )


# ==================================================
# JOB ROLES
# ==================================================

@login_required
def jobrole_list(request):
    org = require_org_admin(request)
    items = JobRole.objects.filter(organization=org)
    return render(
        request,
        "dashboard/jobrole_list.html",
        {"items": items},
    )


@login_required
def jobrole_add(request):
    org = require_org_admin(request)
    form = JobRoleForm(request.POST or None, organization=org)
    if request.method == "POST" and form.is_valid():
        role = form.save(commit=False)
        role.organization = org
        role.save()
        messages.success(request, "Job role added successfully.")
        return redirect("dashboard:jobrole_list")
    return render(
        request,
        "dashboard/jobrole_form.html",
        {"form": form, "is_new": True},
    )


@login_required
def jobrole_edit(request, pk):
    org = require_org_admin(request)
    role = get_object_or_404(JobRole, pk=pk, organization=org)
    form = JobRoleForm(request.POST or None, instance=role, organization=org)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Job role updated successfully.")
        return redirect("dashboard:jobrole_list")
    return render(
        request,
        "dashboard/jobrole_form.html",
        {"form": form, "is_new": False},
    )


@login_required
def jobrole_delete(request, pk):
    org = require_org_admin(request)
    role = get_object_or_404(JobRole, pk=pk, organization=org)
    if request.method == "POST":
        role.delete()
        return redirect("dashboard:jobrole_list")
    return render(
        request,
        "dashboard/jobrole_delete_confirm.html",
        {"item": role},
    )


# ==================================================
# VISIT TYPES
# ==================================================

@login_required
def visittype_list(request):
    org = require_org_admin(request)
    items = VisitType.objects.filter(organization=org)
    return render(
        request,
        "dashboard/visittype_list.html",
        {"items": items},
    )


@login_required
def visittype_add(request):
    org = require_org_admin(request)
    form = VisitTypeForm(request.POST or None, organization=org)
    if request.method == "POST" and form.is_valid():
        vt = form.save(commit=False)
        vt.organization = org
        vt.save()
        messages.success(request, "Visit type added successfully.")
        return redirect("dashboard:visittype_list")
    return render(
        request,
        "dashboard/visittype_form.html",
        {"form": form, "is_new": True},
    )


@login_required
def visittype_edit(request, pk):
    org = require_org_admin(request)
    vt = get_object_or_404(VisitType, pk=pk, organization=org)
    form = VisitTypeForm(request.POST or None, instance=vt, organization=org)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Visit type updated successfully.")
        return redirect("dashboard:visittype_list")
    return render(
        request,
        "dashboard/visittype_form.html",
        {"form": form, "is_new": False},
    )


@login_required
def visittype_delete(request, pk):
    org = require_org_admin(request)
    vt = get_object_or_404(VisitType, pk=pk, organization=org)
    if request.method == "POST":
        vt.delete()
        return redirect("dashboard:visittype_list")
    return render(
        request,
        "dashboard/visittype_delete_confirm.html",
        {"item": vt},
    )

# ==================================================
# MAIL TEMPLATES
# ==================================================

@login_required
def mailtemplate_list(request):
    org = require_org_admin(request)
    items = MailTemplate.objects.filter(organization=org)

    return render(
        request,
        "dashboard/mailtemplate_list.html",
        {"items": items},
    )


@login_required
def mailtemplate_add(request):
    org = require_org_admin(request)
    form = MailTemplateForm(request.POST or None, organization=org)

    if request.method == "POST" and form.is_valid():
        tpl = form.save(commit=False)
        tpl.organization = org
        tpl.save()
        messages.success(request, "Mail template added successfully.")
        return redirect("dashboard:mailtemplate_list")

    return render(
        request,
        "dashboard/mailtemplate_form.html",
        {
            "form": form,
            "is_new": True,
        },
    )


@login_required
def mailtemplate_edit(request, pk):
    org = require_org_admin(request)
    template = get_object_or_404(MailTemplate, pk=pk, organization=org)

    form = MailTemplateForm(request.POST or None, instance=template, organization=org)

    if request.method == "POST" and form.is_valid():
        # 🔒 SECURITY: prevent key change even if HTML is edited
        form.instance.key = template.key

        form.save()
        return redirect("dashboard:mailtemplate_list")

    return render(
        request,
        "dashboard/mailtemplate_form.html",
        {
            "form": form,
            "is_new": False,
        },
    )


@login_required
def mailtemplate_delete(request, pk):
    org = require_org_admin(request)
    tpl = get_object_or_404(MailTemplate, pk=pk, organization=org)
    if request.method == "POST":
        tpl.delete()
        return redirect("dashboard:mailtemplate_list")
    return render(
        request,
        "dashboard/mailtemplate_delete_confirm.html",
        {"item": tpl},
    )



# ==================================================
# ADMIN DASHBOARD – MAIL SETTINGS
# ==================================================

@login_required
def mail_settings(request):
    org = require_org_admin(request)

    config = OrganizationMailConfig.objects.filter(
        organization=org
    ).first()

    is_edit = request.GET.get("edit") == "1"

    if request.method == "POST":
        form = OrganizationMailConfigForm(
            request.POST,
            instance=config,
        )

        if form.is_valid():
            cfg = form.save(commit=False)

            if not form.cleaned_data.get("password") and config:
                cfg.password = config.password

            cfg.organization = org
            cfg.is_active = bool(cfg.smtp_host)
            cfg.save()

            messages.success(request, "Mail settings saved successfully.")
            return redirect("dashboard:mail_settings")

    else:
        form = OrganizationMailConfigForm(instance=config)

    return render(
        request,
        "dashboard/mail_settings.html",
        {
            "form": form,
            "config": config,
            "is_edit": is_edit or not config,
            "active_menu": "mail_settings",
        },
    )



@login_required
def mail_test(request):
    org = require_org_admin(request)

    try:
        config = org.mail_config
    except OrganizationMailConfig.DoesNotExist:
        messages.error(request, "SMTP settings not configured.")
        return redirect("dashboard:mail_settings")

    if not config.is_active:
        messages.error(request, "SMTP is disabled.")
        return redirect("dashboard:mail_settings")

    try:
        backend = EmailBackend(
            host=config.smtp_host,
            port=config.port,
            username=config.username,
            password=config.password,
            use_tls=config.use_tls,
            use_ssl=config.use_ssl,
            timeout=20,
            fail_silently=False,
        )

        subject = f"SMTP Test Successful – {org.name}"
        body_html = f"""
            <h2 style="color: #0f172a; margin-top: 0;">Connection Verified!</h2>
            <p>Your SMTP configuration for <strong>{org.name}</strong> is working perfectly.</p>
            <p>All visitor notifications, OTPs, and alerts will now be sent using these settings.</p>
            <div style="margin-top: 25px; padding: 15px; background: #f9fafb; border-radius: 12px; border: 1px solid #f1f5f9;">
                <code style="color: #7c4dff; font-weight: 600;">Status: Active</code><br>
                <code style="color: #64748b;">Host: {config.smtp_host}</code>
            </div>
        """
        from dashboard.utils.mail import _wrap_html
        full_html = _wrap_html(body_html, {"organization_name": org.name})
        
        email = EmailMultiAlternatives(
            subject=subject,
            body="Your SMTP configuration is working correctly.",
            from_email=config.from_email or config.username,
            to=[request.user.email],
            connection=backend,
        )
        email.attach_alternative(full_html, "text/html")
        email.send()
        messages.success(request, "Test email sent successfully to your email.")

    except Exception as e:
        messages.error(request, f"SMTP Test Failed: {str(e)}")

    return redirect("dashboard:mail_settings")


@login_required
def mailtemplate_import_template(request):
    require_org_admin(request)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="mail_template_import_template.csv"'

    writer = csv.writer(response)
    # Header
    writer.writerow(["key", "title", "subject", "body"])
    # Example Row
    writer.writerow(["VISITOR_THANKS", "Thank You Email", "Thanks for visiting!", "Dear {{name}}, thank you for your visit."])

    return response


@login_required
def mailtemplate_import(request):
    org = require_org_admin(request)

    if request.method != "POST":
        return redirect("dashboard:mailtemplate_list")

    file = request.FILES.get("file")
    if not file:
        messages.error(request, "No file selected.")
        return redirect("dashboard:mailtemplate_list")

    try:
        decoded = file.read().decode("utf-8")
        io_string = io.StringIO(decoded)
        reader = csv.DictReader(io_string)

        success_count = 0
        error_rows = []

        for idx, row in enumerate(reader, start=2):
            try:
                key = row.get("key", "").strip()
                title = row.get("title", "").strip()
                subject = row.get("subject", "").strip()
                body = row.get("body", "").strip()

                if not key or not subject or not body:
                    raise Exception("Key, Subject, and Body are required")

                existing = MailTemplate.objects.filter(organization=org, key=key).first()
                if existing:
                    existing.title = title
                    existing.subject = subject
                    existing.body = body
                    existing.save()
                else:
                    MailTemplate.objects.create(
                        organization=org,
                        key=key,
                        title=title,
                        subject=subject,
                        body=body
                    )

                success_count += 1
            except Exception as e:
                row["error"] = str(e)
                row["row_number"] = idx
                error_rows.append(row)

        if error_rows:
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=mail_template_import_errors.csv"
            writer = csv.writer(response)
            writer.writerow(["row_number", "key", "title", "subject", "body", "error"])
            for r in error_rows:
                writer.writerow([r.get("row_number"), r.get("key"), r.get("title"), r.get("subject"), r.get("body"), r.get("error")])
            return response

        messages.success(request, f"{success_count} templates processed successfully.")
    except Exception as e:
        messages.error(request, f"Import Failed: {str(e)}")

    return redirect("dashboard:mailtemplate_list")
