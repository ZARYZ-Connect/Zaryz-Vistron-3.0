# organizations/middleware.py

from django.http import HttpResponse
from django.shortcuts import render
from organizations.models import Organization
from django.conf import settings


class OrganizationMiddleware:
    """
    Resolves the correct organization (tenant) from the incoming request host.

    Resolution order:
        1. /admin/* paths  → always pass through as platform super-admin
        2. localhost / IP  → platform mode (dev convenience)
        3. Exact platform domain (e.g. vistron.zaryz.in) → platform / landing page
        4. Known tenant domain stored in DB (exact match on Organization.domain)
        5. Subdomain-slug match: <slug>-<platform_subdomain>.<base_domain>
           e.g.  st-vistron.zaryz.in  →  slug="st"  →  lookup by Organization.code
        6. Nothing matched → 404 Tenant Not Found (registered tenants only)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_ip(host: str) -> bool:
        """Return True when host looks like an IPv4 address."""
        parts = host.split(".")
        return len(parts) == 4 and all(p.isdigit() for p in parts)

    @staticmethod
    def _extract_tenant_slug(host: str, platform_domain: str) -> str | None:
        """
        Given:
            host            = "st-vistron.zaryz.in"
            platform_domain = "vistron.zaryz.in"

        Returns "st" so we can look the tenant up by Organization.code.

        Returns None if the host does not follow the expected pattern.
        """
        # --- Pattern A: <slug>.<platform_domain>  (subdomain style) ---
        # e.g.  st.vistron.zaryz.in
        subdomain_suffix = "." + platform_domain
        if host.endswith(subdomain_suffix):
            slug = host[: -len(subdomain_suffix)]
            if slug and "." not in slug:          # single-level slug only
                return slug

        # --- Pattern B: <slug>-<platform_subdomain>.<base_domain>  (hyphen style) ---
        # e.g.  st-vistron.zaryz.in  where platform = vistron.zaryz.in
        parts = platform_domain.split(".", 1)     # ["vistron", "zaryz.in"]
        if len(parts) == 2:
            platform_sub, base_domain = parts[0], parts[1]
            hyphen_suffix = f"-{platform_sub}.{base_domain}"
            if host.endswith(hyphen_suffix):
                slug = host[: -len(hyphen_suffix)]
                if slug and "." not in slug:
                    return slug

        return None

    # ------------------------------------------------------------------
    # main
    # ------------------------------------------------------------------

    def __call__(self, request):

        # ── 1. Admin paths → always allow, mark as platform ────────────
        if request.path.startswith("/admin"):
            request.organization = None
            request.is_platform = True
            request.is_super_admin = True
            return self.get_response(request)

        host = request.get_host().split(":")[0].lower().strip()
        platform_domain = settings.PLATFORM_DOMAIN.lower().strip()

        print(f"[OrganizationMiddleware] host='{host}'  platform='{platform_domain}'  path='{request.path}'")

        # ── 2. localhost / raw IP → platform (dev only) ─────────────────
        if host in ("127.0.0.1", "localhost") or self._is_ip(host):
            request.organization = None
            request.is_platform = True
            request.is_super_admin = True
            print("[OrganizationMiddleware] → localhost/IP: platform mode")
            return self.get_response(request)

        # ── 3. Exact platform domain → marketing landing ─────────────────
        if host == platform_domain:
            request.organization = None
            request.is_platform = True
            request.is_super_admin = False
            print("[OrganizationMiddleware] → exact platform domain: platform mode")
            return self.get_response(request)

        # ── 4. Exact domain match in DB ──────────────────────────────────
        try:
            org = Organization.objects.get(domain=host, is_active=True)
            request.organization = org
            request.is_platform = False
            request.is_super_admin = False
            print(f"[OrganizationMiddleware] → exact domain match: '{org.name}'")
            return self.get_response(request)
        except Organization.DoesNotExist:
            pass  # continue to slug-based resolution

        # ── 5. Slug-based subdomain resolution ──────────────────────────
        slug = self._extract_tenant_slug(host, platform_domain)
        if slug:
            try:
                org = Organization.objects.get(code=slug, is_active=True)
                request.organization = org
                request.is_platform = False
                request.is_super_admin = False
                print(f"[OrganizationMiddleware] → slug '{slug}' matched org: '{org.name}'")
                return self.get_response(request)
            except Organization.DoesNotExist:
                pass  # slug exists in URL but no active org with that code

        # ── 6. No match → 404 Tenant Not Found ──────────────────────────
        print(f"[OrganizationMiddleware] → '{host}' is not a registered tenant: 404")
        return render(
            request,
            "organizations/tenant_not_found.html",
            {
                "host": host,
                "platform_domain": platform_domain,
                "platform_url": f"https://{platform_domain}",
            },
            status=404,
        )
