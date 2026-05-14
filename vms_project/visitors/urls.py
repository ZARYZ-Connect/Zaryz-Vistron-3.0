from django.urls import path
from . import views

app_name = "visitors"

urlpatterns = [

    # ------------------------------------------------------------------
    # PLATFORM / ORG HOME
    # vistron.zaryz.com
    # demo-vistron.zaryz.com
    # ------------------------------------------------------------------
    path("", views.home, name="home"),

    # ------------------------------------------------------------------
    # 🔥 ORG-AWARE VISITOR REGISTRATION (DOMAIN BASED)
    # demo-vistron.zaryz.com/register/
    # ------------------------------------------------------------------
    path("register/", views.visit_register, name="visit_register"),

    # ------------------------------------------------------------------
    # OTP VALIDATION (SESSION BASED, ORG FROM MIDDLEWARE)
    # demo-vistron.zaryz.com/otp/
    # ------------------------------------------------------------------
    path("otp/", views.otp_validate, name="otp_validate"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    # ------------------------------------------------------------------
    # EMAIL APPROVAL (UUID BASED, ORG RESOLVED INTERNALLY)
    # demo-vistron.zaryz.com/approve/<uuid>/<token>/
    # ------------------------------------------------------------------
    path(
        "approve/<uuid:uuid>/<str:token>/",
        views.approve,
        name="approve",
    ),

    # ------------------------------------------------------------------
    # VISITOR PHOTO (SECURE, ORG ISOLATED)
    # demo-vistron.zaryz.com/visitor-photo/<uuid>/
    # ------------------------------------------------------------------
    path(
        "visitor-photo/<uuid:uuid>/",
        views.serve_visitor_photo,
        name="visitor_photo",
    ),

    # 🔥 ADD THIS NEW ROUTE
    path(
        "ajax/employees/",
        views.get_department_employees,
        name="get_department_employees",
    ),

    # 🎫 QR PASS VIEW
    path(
        "qr-pass/<uuid:uuid>/",
        views.qr_pass,
        name="qr_pass",
    ),
]
