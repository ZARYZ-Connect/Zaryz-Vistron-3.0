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
def root_router(request):
    if getattr(request, "organization", None):
        # Tenant domain → go to tenant visitor landing
        return HttpResponseRedirect("/visitors/")
    # Public domain → marketing landing
    return render(request, "platform/index.html")

# ---------------------------------------------------
# PLATFORM MARKETING PAGES
# ---------------------------------------------------
def features_page(request):
    return render(request, "platform/features.html")


def pricing_page(request):
    return render(request, "platform/pricing.html")


def contact_page(request):
    return render(request, "platform/contact.html")


# ---------------------------------------------------
# URLPATTERNS
# ---------------------------------------------------
urlpatterns = [

    # ---------------------------------------------------
    # LANDING (MUST BE FIRST)
    # ---------------------------------------------------
    path('', include('landing.urls')),

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

    # ---------------------------------------------------
    # PLATFORM MARKETING ROUTES
    # ---------------------------------------------------
    path("features/", features_page),
    path("pricing/", pricing_page),
    path("contact/", contact_page),
    path("home/", lambda request: render(request, "platform/index.html")),

    # ---------------------------------------------------
    # ROOT (MUST BE LAST)
    # ---------------------------------------------------
    path("", root_router),
]


# ---------------------------------------------------
# STATIC & MEDIA (DEV ONLY)
# ---------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
