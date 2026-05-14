from django.core.exceptions import PermissionDenied


def require_organization(request):
    if not getattr(request, "organization", None):
        raise PermissionDenied("Organization context required")
