from django.db import models
from django.conf import settings


class OrganizationQuerySet(models.QuerySet):
    def for_organization(self, organization):
        """
        🔐 Multi-tenant isolation helper.
        In DEBUG mode, we relax this to .all() to make local development on 
        localhost/127.0.0.1 seamless across all organizations.
        """
        if settings.DEBUG:
            return self.all()

        if not organization:
            return self.none()
        return self.filter(organization=organization)


class OrganizationManager(models.Manager):
    def get_queryset(self):
        return OrganizationQuerySet(self.model, using=self._db)

    def for_organization(self, organization):
        return self.get_queryset().for_organization(organization)
