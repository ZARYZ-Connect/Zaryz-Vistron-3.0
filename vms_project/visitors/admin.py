from django.contrib import admin
from .models import VisitRequest, VisitType, OTP


# =================================================
# VISIT TYPE ADMIN
# =================================================
@admin.register(VisitType)
class VisitTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "organization")
    list_filter = ("organization",)
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # SUPER ADMIN → ALL ORGS
        if request.user.is_superuser:
            return qs

        # TENANT ADMIN → OWN ORG ONLY
        if hasattr(request, "organization") and request.organization:
            return qs.filter(organization=request.organization)

        return qs.none()

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.organization = request.organization
        super().save_model(request, obj, form, change)


# =================================================
# VISIT REQUEST ADMIN
# =================================================
@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "phone",
        "visit_type",
        "status",
        "created_at",
    )

    list_filter = ("status", "organization", "visit_type")
    search_fields = ("full_name", "phone")
    readonly_fields = ("created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # SUPER ADMIN → ALL DATA
        if request.user.is_superuser:
            return qs

        # TENANT ADMIN → ONLY OWN ORG
        if hasattr(request, "organization") and request.organization:
            return qs.filter(organization=request.organization)

        return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.organization != request.organization:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.organization != request.organization:
            return False
        return True


# =================================================
# OTP ADMIN (READ-ONLY – SECURITY LOGS)
# =================================================
@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = (
        "visit",
        "code",
        "created_at",
        "expires_at",
    )

    readonly_fields = (
        "visit",
        "code",
        "created_at",
        "expires_at",
    )

    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # SUPER ADMIN → ALL
        if request.user.is_superuser:
            return qs

        # TENANT ADMIN → OTPs of own org visitors
        if hasattr(request, "organization") and request.organization:
            return qs.filter(visit__organization=request.organization)

        return qs.none()

    def has_add_permission(self, request):
        return False  # OTPs must be system-generated

    def has_delete_permission(self, request, obj=None):
        return False  # Security logs must never be deleted

