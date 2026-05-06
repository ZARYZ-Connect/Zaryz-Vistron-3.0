from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    # -------------------------------------------------
    # LIST VIEW
    # -------------------------------------------------
    list_display = (
        "username",
        "email",
        "role",
        "organization",
        "is_staff",
        "is_active",
    )

    list_filter = ("role", "organization", "is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("username",)

    # -------------------------------------------------
    # EDIT VIEW
    # -------------------------------------------------
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Company Access",
            {
                "fields": (
                    "organization",
                    "role",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # -------------------------------------------------
    # ADD USER VIEW
    # -------------------------------------------------
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "organization",
                    "role",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    # -------------------------------------------------
    # 🔐 SAAS DATA ISOLATION (CRITICAL)
    # -------------------------------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # ✅ SUPER ADMIN → SEE EVERYTHING
        if getattr(request, "is_super_admin", False):
            return qs

        # ✅ TENANT ADMIN → SEE ONLY OWN ORG USERS
        if hasattr(request, "organization") and request.organization:
            return qs.filter(organization=request.organization)

        return qs.none()

    def save_model(self, request, obj, form, change):
        # 🔒 TENANT ADMIN SAFETY
        if not getattr(request, "is_super_admin", False):
            obj.organization = request.organization
            obj.is_superuser = False
            obj.is_staff = True

        super().save_model(request, obj, form, change)

    def has_view_permission(self, request, obj=None):
        if getattr(request, "is_super_admin", False):
            return True

        if obj and obj.organization != request.organization:
            return False

        return True

    def has_change_permission(self, request, obj=None):
        if getattr(request, "is_super_admin", False):
            return True

        if obj and obj.organization != request.organization:
            return False

        return True

    def has_delete_permission(self, request, obj=None):
        if getattr(request, "is_super_admin", False):
            return True

        if obj and obj.organization != request.organization:
            return False

        return True
