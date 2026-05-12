# vms_project/urls.py

from django.shortcuts import render
from django.contrib import admin
from django.urls import path, include, reverse
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect


# ---------------------------------------------------
# ROOT ROUTER (IMPORTANT FOR SAAS)
# ---------------------------------------------------
# ---------------------------------------------------
# ROOT ROUTER (SaaS CORE)
# ---------------------------------------------------
from landing.views import LandingPageView

def root_router(request):
    """
    Decides what to show at the root '/' based on the domain resolved by OrganizationMiddleware.

    - Tenant domain  → login page (if unauthenticated) or dashboard (if authenticated)
    - Platform domain → marketing landing page
    - Anything else   → admin (should only be reached by superusers)
    """
    if getattr(request, "organization", None):
        # 🏢 Tenant domain → go to login or dashboard
        if request.user.is_authenticated:
            return HttpResponseRedirect("/dashboard/")
        return HttpResponseRedirect("/accounts/login/")

    if getattr(request, "is_platform", False):
        # 🌐 Platform domain → marketing landing page
        return LandingPageView.as_view()(request)

    # Fallback — should not be reached in normal operation
    return HttpResponseRedirect("/admin/")


# ---------------------------------------------------
# PLATFORM MARKETING PROTECTOR
# ---------------------------------------------------
from django.http import Http404

def platform_only(view_func):
    """
    Decorator to restrict marketing views to the platform domain only.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not getattr(request, "is_platform", False):
            raise Http404("Marketing pages are only available on the main platform domain.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ---------------------------------------------------
# PLATFORM MARKETING PAGES
# ---------------------------------------------------
@platform_only
def features_page(request):
    return render(request, "platform/features.html")

@platform_only
def pricing_page(request):
    return render(request, "platform/pricing.html")

@platform_only
def contact_page(request):
    return render(request, "platform/contact.html")


# ---------------------------------------------------
# URLPATTERNS
# ---------------------------------------------------
urlpatterns = [

    # ---------------------------------------------------
    # ROOT ROUTING (MUST BE FIRST)
    # ---------------------------------------------------
    path('', root_router, name='root'),

    # ---------------------------------------------------
    # MARKETING & LANDING
    # ---------------------------------------------------
    path('site/', include('landing.urls')),
    path("features/", features_page),
    path("pricing/", pricing_page),
    path("contact/", contact_page),
    path("home/", platform_only(lambda request: render(request, "platform/index.html"))),
    
    # ---------------------------------------------------
    # ADMIN
    # ---------------------------------------------------
    path("admin/", admin.site.urls),

    # ---------------------------------------------------
    # AUTH & ACCOUNTS
    # ---------------------------------------------------
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),

    # ---------------------------------------------------
    # SECURITY / RECEPTION
    # ---------------------------------------------------
    path("security/", include(("security.urls", "security"), namespace="security")),

    # ---------------------------------------------------
    # DASHBOARD (ORG ADMINS)
    # ---------------------------------------------------
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),

    # ---------------------------------------------------
    # VISITORS
    # ---------------------------------------------------
    path("visitors/", include("visitors.urls")),
    
    # Resolves missing favicon 404
    path("favicon.ico", lambda request: HttpResponseRedirect('/static/img/logo.png')),

    # ---------------------------------------------------
    # API
    # ---------------------------------------------------
    path("api/", include(("api.urls", "api"), namespace="api")),
]


# ---------------------------------------------------
# STATIC & MEDIA (DEV ONLY)
# ---------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
