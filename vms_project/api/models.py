from django.db import models
import uuid


class ApiKey(models.Model):
    """
    API key per organization (SaaS-safe)
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE
    )

    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization} - {self.key}"