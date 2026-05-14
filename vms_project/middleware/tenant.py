from django.http import Http404
from organizations.models import Organization


class TenantMiddleware:
    """
    Resolves organization based on subdomain.

    Examples:
    - vistron.zaryz.com           -> No organization (public / super admin)
    - abc-vistron.zaryz.com       -> Organization(code='abc')
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]  # remove port
        parts = host.split(".")

        request.organization = None  # default

        # -------------------------
        # LOCAL SUBDOMAINS (e.g. info.localhost)
        # -------------------------
        if (host.endswith(".localhost") or host.endswith(".127.0.0.1")) and len(parts) >= 2:
            org_code = parts[0]
            try:
                request.organization = Organization.objects.get(code=org_code, is_active=True)
            except Organization.DoesNotExist:
                pass

        # -------------------------
        # PRODUCTION SUBDOMAINS (e.g. abc-vistron.zaryz.com)
        # -------------------------
        if not request.organization and len(parts) >= 3:
            subdomain = parts[0]
            if subdomain.endswith("-vistron"):
                org_code = subdomain.replace("-vistron", "")
                try:
                    request.organization = Organization.objects.get(code=org_code, is_active=True)
                except Organization.DoesNotExist:
                    raise Http404("Organization not found")

        # -------------------------
        # INTELLIGENT DEV FALLBACK
        # -------------------------
        from django.conf import settings
        if not request.organization and settings.DEBUG:
            # If we're on localhost/root and no org matched, pick the first one for development ease
            if host in ("localhost", "127.0.0.1") or not parts:
                request.organization = Organization.objects.filter(is_active=True).first()

        return self.get_response(request)