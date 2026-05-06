from django.contrib.auth.models import AbstractUser
from django.db import models

from organizations.models import Organization
from dashboard.models import Department


class User(AbstractUser):
    """
    Custom User model with SaaS (multi-tenant) support.

    Rules:
    - SUPER ADMIN → organization = NULL
    - TENANT USERS → organization = REQUIRED
    """

    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),     # Platform owner
        ('admin', 'Organization Admin'),    # Tenant admin
        ('employee', 'Employee'),
        ('security', 'Security'),
        ('reception', 'Reception'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee'
    )

    # 🔒 Tenant isolation (VERY IMPORTANT)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users"
    )

    # Optional department inside an organization
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    phone = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='users/', blank=True, null=True)

    # ------------------------------------------------------------------
    # ROLE HELPERS (USED EVERYWHERE)
    # ------------------------------------------------------------------
    def is_super_admin(self):
        return self.role == 'super_admin'

    def is_org_admin(self):
        return self.role == 'admin'

    def is_staff_user(self):
        return self.role in ['employee', 'security', 'reception']

    @property
    def get_initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        if self.first_name:
            return f"{self.first_name[0]}{self.first_name[1] if len(self.first_name) > 1 else ''}".upper()
        return self.username[:2].upper()

    def __str__(self):
        return f"{self.username} ({self.role})"
