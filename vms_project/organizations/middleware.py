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
        # 🔥 ALWAYS ALLOW PLATFORM ACCESS FOR ADMIN
        # This ensures you can manage Organizations regardless of the domain/IP used.
        if request.path.startswith('/admin'):
            request.organization = None
            request.is_platform = True
            request.is_super_admin = True
            return self.get_response(request)

        host = request.get_host().split(":")[0].lower()
        
        # 1. PLATFORM / SUPER ADMIN (Explicit match)
        platform_domains = [settings.PLATFORM_DOMAIN, '127.0.0.1', 'localhost']
        
        # Helper to check if host is an IP address
        is_ip = all(c.isdigit() or c == '.' for c in host) and host.count('.') == 3

        if host in platform_domains:
            # 🛠️ DEV FALLBACK: If on localhost/127.0.0.1 and in DEBUG mode, 
            # we allow falling back to the FIRST active organization to make 
            # development easier without subdomains.
            if settings.DEBUG:
                org = Organization.objects.filter(is_active=True).first()
                if org:
                    request.organization = org
                    request.is_platform = False
                    request.is_super_admin = False
                    print(f"DEBUG: Middleware: Platform Host Dev Fallback: '{org.name}'")
                    return self.get_response(request)

            request.organization = None
            request.is_platform = True
            request.is_super_admin = True
            return self.get_response(request)

        # 2. ORGANIZATION DOMAIN (DB DRIVEN)
        try:
            organization = Organization.objects.get(
                domain=host,
                is_active=True
            )
            request.organization = organization
            request.is_platform = False
            request.is_super_admin = False
            
        except Organization.DoesNotExist:
            # 🛠️ DEV FALLBACK: If no org is matched by subdomain/domain, 
            # and we are in DEBUG mode, pick the first active one.
            # This allows easy testing via IP address (Mobile/Tablet) or localhost.
            if settings.DEBUG:
                org = Organization.objects.filter(is_active=True).first()
                if org:
                    request.organization = org
                    request.is_platform = False
                    request.is_super_admin = False
                    print(f"DEBUG: Middleware: Auto-resolved organization '{org.name}' for host: {host}")
                else:
                    request.organization = None
                    request.is_platform = True
                    request.is_super_admin = True
            else:
                # Unknown or inactive domain in production
                raise Http404(f"Could not find active organization for domain: {host}")

        return self.get_response(request)
