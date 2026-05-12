# organizations/middleware.py

from django.http import Http404
from organizations.models import Organization
from django.conf import settings

class OrganizationMiddleware:
    """
    Resolves organization based on request domain.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. ALWAYS ALLOW ADMIN ACCESS (Platform level)
        if request.path.startswith('/admin'):
            request.organization = None
            request.is_platform = True
            request.is_super_admin = True
            return self.get_response(request)

        host = request.get_host().split(":")[0].lower()
        platform_domains = [settings.PLATFORM_DOMAIN.lower(), '127.0.0.1', 'localhost']
        
        # Helper to check if host is an IP address
        is_ip = all(c.isdigit() or c == '.' for c in host) and host.count('.') == 3
        
        print(f"DEBUG: Middleware: Host='{host}', is_ip={is_ip}, path='{request.path}'")

        # 2. PLATFORM / LANDING PAGE DOMAIN
        if host in platform_domains or is_ip:
            try:
                organization = Organization.objects.get(domain=host, is_active=True)
                request.organization = organization
                request.is_platform = False
                request.is_super_admin = False
                print(f"DEBUG: Middleware: Explicit Org match for IP/Platform host: {organization.name}")
                return self.get_response(request)
            except Organization.DoesNotExist:
                request.organization = None
                request.is_platform = True
                request.is_super_admin = True
                print(f"DEBUG: Middleware: No org match, treating as Platform.")
                return self.get_response(request)

        # 3. ORGANIZATION DOMAIN (DB DRIVEN)
        try:
            organization = Organization.objects.get(
                domain=host,
                is_active=True
            )
            request.organization = organization
            request.is_platform = False
            request.is_super_admin = False
            print(f"DEBUG: Middleware: Resolved Org by domain: {organization.name}")
            
        except Organization.DoesNotExist:
            if settings.DEBUG:
                org = Organization.objects.filter(is_active=True).first()
                if org:
                    request.organization = org
                    request.is_platform = False
                    request.is_super_admin = False
                    print(f"DEBUG: Middleware: Auto-resolved fallback Org: '{org.name}'")
                else:
                    request.organization = None
                    request.is_platform = True
                    request.is_super_admin = True
                    print(f"DEBUG: Middleware: No Org found, falling back to Platform.")
            else:
                raise Http404(f"Domain '{host}' is not registered.")

        return self.get_response(request)
