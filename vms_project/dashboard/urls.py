from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [

    # ==================================================
    # PUBLIC AJAX (VISITOR SIDE) — MUST BE FIRST
    # ==================================================
    path(
        "ajax/public/employees/<int:dept_id>/",
        views.public_employees_by_department,
        name="public_employees_by_department",
    ),

    # ==================================================
    # ADMIN DASHBOARD
    # ==================================================
    path("", views.admin_dashboard, name="admin_dashboard"),

    # ==================================================
    # VISITORS – ADMIN
    # ==================================================
    # VISITORS – ADMIN
    path("visitors/", views.visitor_list, name="visitor_list"),

    path("visitors/export/", views.export_visitors_csv, name="export_visitors_csv"),

    path("visitors/<int:pk>/", views.visitor_detail, name="visitor_detail"),
    path("visitors/<int:pk>/approve/", views.visitor_approve, name="visitor_approve"),
    path("visitors/<int:pk>/reject/", views.visitor_reject, name="visitor_reject"),

    path("visitors/status/<str:status>/", views.visitor_list_by_status, name="visitor_list_by_status"),

    # ==================================================
    # SECURITY DASHBOARD
    # ==================================================
    path("security/", views.security_dashboard, name="security_dashboard"),
    path("security/<int:pk>/checkin/", views.security_checkin, name="security_checkin"),
    path("security/<int:pk>/checkout/", views.security_checkout, name="security_checkout"),

    # ==================================================
    # EMPLOYEES
    # ==================================================
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_add, name="employee_add"),
    path("employees/<int:pk>/edit/", views.employee_edit, name="employee_edit"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),

    # ==================================================
    # SECURITY USERS
    # ==================================================
    path("security-users/", views.security_user_list, name="security_user_list"),
    path("security-users/add/", views.security_user_add, name="security_user_add"),
    path("security-users/<int:pk>/edit/", views.security_user_edit, name="security_user_edit"),
    path("security-users/<int:pk>/delete/", views.security_user_delete, name="security_user_delete"),

    # ==================================================
    # ADMIN AJAX (INTERNAL ONLY)
    # ==================================================
    path(
        "ajax/employees-by-department/<int:dept_id>/",
        views.employees_by_department,
        name="employees_by_department",
    ),

    # ==================================================
    # DEPARTMENTS
    # ==================================================
    path("departments/", views.department_list, name="department_list"),
    path("departments/add/", views.department_add, name="department_add"),
    path("departments/<int:pk>/edit/", views.department_edit, name="department_edit"),
    path("departments/<int:pk>/delete/", views.department_delete, name="department_delete"),

    # ==================================================
    # JOB ROLES
    # ==================================================
    path("jobroles/", views.jobrole_list, name="jobrole_list"),
    path("jobroles/add/", views.jobrole_add, name="jobrole_add"),
    path("jobroles/<int:pk>/edit/", views.jobrole_edit, name="jobrole_edit"),
    path("jobroles/<int:pk>/delete/", views.jobrole_delete, name="jobrole_delete"),

    # ==================================================
    # VISIT TYPES
    # ==================================================
    path("visit-types/", views.visittype_list, name="visittype_list"),
    path("visit-types/add/", views.visittype_add, name="visittype_add"),
    path("visit-types/<int:pk>/edit/", views.visittype_edit, name="visittype_edit"),
    path("visit-types/<int:pk>/delete/", views.visittype_delete, name="visittype_delete"),

    # ==================================================
    # MAIL TEMPLATES
    # ==================================================
    path("mail-templates/", views.mailtemplate_list, name="mailtemplate_list"),
    path("mail-templates/add/", views.mailtemplate_add, name="mailtemplate_add"),
    path("mail-templates/<int:pk>/edit/", views.mailtemplate_edit, name="mailtemplate_edit"),
    path("mail-templates/<int:pk>/delete/", views.mailtemplate_delete, name="mailtemplate_delete"),
    
    # ==================================================
    # MAIL setting
    # ==================================================
    path("mail-settings/", views.mail_settings, name="mail_settings"),
    path("mail-settings/test/", views.mail_test, name="mail_test"),
    path("mail-templates/import/template/", views.mailtemplate_import_template, name="mailtemplate_import_template"),
    path("mail-templates/import/", views.mailtemplate_import, name="mailtemplate_import"),
    path("employees/import/template/", views.employee_import_template, name="employee_import_template"),
    path("employees/import/", views.employee_import, name="employee_import"),

]

