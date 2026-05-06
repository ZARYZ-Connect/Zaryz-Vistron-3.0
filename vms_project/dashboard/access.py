# dashboard/utils/access.py

from django.http import Http404


def require_org_user(request):
    """
    Ensures:
    - User is authenticated
    - User belongs to an organization
    - Request is NOT from platform domain
    """
    if not request.user.is_authenticated:
        raise Http404("Authentication required")

    organization = getattr(request, "organization", None)

    if not organization:
        raise Http404("Organization not resolved")

    if request.user.organization_id != organization.id:
        raise Http404("Cross-organization access blocked")

    return organization
