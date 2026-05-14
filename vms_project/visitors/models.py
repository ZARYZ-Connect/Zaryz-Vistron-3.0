from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.managers import OrganizationManager
import uuid
import datetime


# ------------------------------------------------------------------
# VISIT TYPE (ORG SPECIFIC)
# ------------------------------------------------------------------
class VisitType(models.Model):
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='visit_types'
    )

    name = models.CharField(max_length=120)

    # 🔐 QUERY-LEVEL ISOLATION
    objects = OrganizationManager()

    class Meta:
        unique_together = ('organization', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.organization.code})"


# ------------------------------------------------------------------
# VISIT REQUEST (CORE BUSINESS MODEL)
# ------------------------------------------------------------------
class VisitRequest(models.Model):
    STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
    )

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='visits'
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=30)

    visit_type = models.ForeignKey(
        VisitType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    visit_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    whom_to_meet = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings'
    )

    whom_to_meet_employee = models.ForeignKey(
        'dashboard.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings_employee'
    )

    purpose = models.TextField(blank=True)

    photo = models.ImageField(
        upload_to='visitors/photos/',
        blank=True,
        null=True
    )

    qr_code = models.ImageField(
        upload_to='visitors/qrcodes/',
        blank=True,
        null=True
    )

    badge_id = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pending',
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    actual_checkin = models.DateTimeField(null=True, blank=True)
    actual_checkout = models.DateTimeField(null=True, blank=True)

    # 🔐 QUERY-LEVEL ISOLATION
    objects = OrganizationManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'visit_date']),
            models.Index(fields=['organization', 'status']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.organization.code}) - {self.visit_date}"

    def clean(self):
        if not self.organization_id or not self.visit_type_id:
            return

        if self.visit_type.organization_id != self.organization_id:
            raise ValidationError({
                "visit_type": "Invalid visit type for this organization"
            })

    @property
    def display_status(self):
        now = timezone.now()
        today = timezone.localdate()

        if self.status == 'checked_out':
            return 'Visit completed'

        if self.status == 'checked_in':
            if self.visit_date and self.end_time:
                try:
                    end_dt = timezone.make_aware(
                        datetime.datetime.combine(self.visit_date, self.end_time)
                    )
                    if now > end_dt:
                        return 'Inside (overstayed)'
                except Exception:
                    pass
            return 'Checked in'

        if self.status in ('approved', 'pending'):
            if self.visit_date and self.visit_date < today:
                return 'No show'
            return self.get_status_display()

        return self.get_status_display()


# ------------------------------------------------------------------
# OTP (VISITOR SECURITY FLOW)
# ------------------------------------------------------------------
class OTP(models.Model):
    visit = models.ForeignKey(
        VisitRequest,
        on_delete=models.CASCADE,
        related_name='otps'
    )

    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['expires_at']),
        ]

    def is_valid(self):
        return timezone.now() <= self.expires_at

    def __str__(self):
        return f"OTP for {self.visit.full_name} ({self.visit.organization.code})"
