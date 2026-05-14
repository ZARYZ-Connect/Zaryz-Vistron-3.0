from django.contrib import admin
from django.core.exceptions import ValidationError
from organizations.models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "domain", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "domain")
    ordering = ("name",)

    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "Organization Details",
            {
                "fields": (
                    "name",
                    "code",
                    "domain",
                    "is_active",
                )
            },
        ),
        (
            "System Info",
            {
                "fields": ("created_at",),
            },
        ),
    )

    # --------------------------------------------------
    # 🔐 PLATFORM-ONLY ACCESS
    # --------------------------------------------------
    def has_module_permission(self, request):
        return getattr(request, "is_platform", False)

    def has_view_permission(self, request, obj=None):
        return getattr(request, "is_platform", False)

    def has_add_permission(self, request):
        return getattr(request, "is_platform", False)

    def has_change_permission(self, request, obj=None):
        return getattr(request, "is_platform", False)

    def has_delete_permission(self, request, obj=None):
        return getattr(request, "is_platform", False)

    # --------------------------------------------------
    # ⚙ AUTO-GENERATE DOMAIN & CODE
    # --------------------------------------------------
    def save_model(self, request, obj, form, change):
        """
        Auto-generates:
        - code  → slug format
        - domain → <code>-vistron.zaryz.in
        """

        if not obj.code:
            obj.code = obj.name.lower().replace(" ", "-")

        obj.code = obj.code.lower().strip()

        obj.domain = f"{obj.code}-vistron.zaryz.in"

        # Safety check
        if Organization.objects.exclude(pk=obj.pk).filter(domain=obj.domain).exists():
            raise ValidationError("Organization domain already exists.")

        super().save_model(request, obj, form, change)

    # --------------------------------------------------
    # 🧠 ADMIN UX MESSAGE (CNAME GUIDE)
    # --------------------------------------------------
    def render_change_form(self, request, context, *args, **kwargs):
        context["adminform"].form.fields["domain"].help_text = (
            "CNAME record required:<br>"
            "<b>Host:</b> &lt;your-subdomain&gt;<br>"
            "<b>Target:</b> vistron.zaryz.in"
        )
        return super().render_change_form(request, context, *args, **kwargs)
