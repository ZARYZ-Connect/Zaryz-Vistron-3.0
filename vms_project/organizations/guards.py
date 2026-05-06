from django.http import Http404, HttpResponseForbidden


def require_organization(request):
    """
    Blocks access if organization is missing
    """
    if not hasattr(request, "organization") or request.organization is None:
        raise Http404("Organization not resolved")


def require_super_admin(request):
    """
    Allows only platform super admin
    """
    if not request.user.is_authenticated or not request.user.is_super_admin():
        return HttpResponseForbidden("Super admin access only")


def require_org_admin(request):
    """
    Allows only tenant admin of that organization
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentication required")

    if request.organization is None:
        return HttpResponseForbidden("Invalid organization")

    if request.user.organization != request.organization:
        return HttpResponseForbidden("Cross-organization access denied")

    if not request.user.is_org_admin():
        return HttpResponseForbidden("Organization admin only")
