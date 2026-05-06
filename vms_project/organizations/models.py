from django.db import models


class Organization(models.Model):
    name = models.CharField(
        max_length=255,
        help_text="Full company name (e.g., Demo Company Pvt Ltd)"
    )

    code = models.SlugField(
        unique=True,
        help_text="Short unique code used internally (e.g., demo, abc)"
    )

    domain = models.CharField(
        max_length=255,
        unique=True,
        help_text="Full domain mapped to this organization (e.g., demo-vistron.zaryz.in)"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Disable organization access without deleting data"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return f"{self.name} ({self.domain})"


class OrganizationMailConfig(models.Model):
    organization = models.OneToOneField(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="mail_config",
    )

    smtp_host = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    port = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)

    from_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Optional override sender email",
    )

    is_active = models.BooleanField(
        default=False,
        help_text="Enable tenant SMTP",
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mail Config - {self.organization.name}"


