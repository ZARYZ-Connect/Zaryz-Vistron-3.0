"""
Django settings for vms_project.
FINAL STABLE DEV CONFIG (SaaS + Nginx + Gunicorn ready)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# BASE DIR
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env (optional for dev)
load_dotenv(BASE_DIR / ".env")

# -----------------------------------------------------------------------------
# ENV
# -----------------------------------------------------------------------------
DJANGO_ENV = os.getenv("DJANGO_ENV", "dev").lower()
DEBUG = DJANGO_ENV == "dev"

# Safety guard: crash loudly if running in production with insecure defaults
if not DEBUG:
    _raw_key = os.getenv("DJANGO_SECRET_KEY", "")
    if not _raw_key or _raw_key == "dev-insecure-secret-key" or "REPLACE_WITH" in _raw_key:
        raise RuntimeError(
            "\n[SECURITY ERROR] DJANGO_SECRET_KEY is not set or is using the dev default.\n"
            "Set a strong secret key in your .env file before running in production."
        )

# -----------------------------------------------------------------------------
# SECURITY
# -----------------------------------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-secret-key")

# -----------------------------------------------------------------------------
# ALLOWED HOSTS (SaaS READY — wildcard subdomain support)
# -----------------------------------------------------------------------------
# In .env set: ALLOWED_HOSTS=vistron.zaryz.in,.zaryz.in,localhost
# Django supports leading-dot notation: '.zaryz.in' matches ALL *.zaryz.in subdomains
env_hosts = os.getenv("ALLOWED_HOSTS", "*" if DEBUG else "")
ALLOWED_HOSTS = [h.strip() for h in env_hosts.split(",") if h.strip()]

# -----------------------------------------------------------------------------
# PROXY / NGINX
# -----------------------------------------------------------------------------
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -----------------------------------------------------------------------------
# CSRF & SESSION (🔥 THIS FIXES YOUR ADMIN LOGIN ISSUE 🔥)
# -----------------------------------------------------------------------------
# In .env set: CSRF_TRUSTED_ORIGINS=https://vistron.zaryz.in,https://*.zaryz.in
# Django 4.x+ supports https://*.zaryz.in wildcard in CSRF_TRUSTED_ORIGINS
env_csrf = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in env_csrf.split(",") if o.strip()]
# PLATFORM DOMAIN (SaaS READY)
PLATFORM_DOMAIN = os.getenv("PLATFORM_DOMAIN", "vistron.zaryz.in")

# CSRF_COOKIE_DOMAIN = None
# SESSION_COOKIE_DOMAIN = None

if DEBUG:
    CSRF_COOKIE_DOMAIN = None
    SESSION_COOKIE_DOMAIN = None
else:
    CSRF_COOKIE_DOMAIN = ".zaryz.in"
    SESSION_COOKIE_DOMAIN = ".zaryz.in"

# CSRF_COOKIE_DOMAIN = ".zaryz.in"
# SESSION_COOKIE_DOMAIN = ".zaryz.in"

# HTTP for now (when SSL is added → set True)
# CSRF_COOKIE_SECURE = False
# SESSION_COOKIE_SECURE = False

# -----------------------------------------------------------------------------
# APPLICATIONS
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    'django_extensions',
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "crispy_forms",
    "crispy_bootstrap5",

    # Core SaaS app
    "organizations",

    # Project apps
    "accounts",
    "visitors",
    "security",
    "dashboard",
    "api",
    "landing",
]

# -----------------------------------------------------------------------------
# MIDDLEWARE
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    # 🔥 MUST BE FIRST — resolves org from domain
    "organizations.middleware.OrganizationMiddleware",

    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise: serves static files from Gunicorn (no Nginx config needed)
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -----------------------------------------------------------------------------
# URL / WSGI
# -----------------------------------------------------------------------------
ROOT_URLCONF = "vms_project.urls"
WSGI_APPLICATION = "vms_project.wsgi.application"

# -----------------------------------------------------------------------------
# TEMPLATES
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # REQUIRED
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "security.context_processors.security_stats",
                "dashboard.context_processors.admin_sidebar_stats",
            ],
        },
    },
]


# -----------------------------------------------------------------------------
# DATABASE (POSTGRESQL)
# -----------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
        "CONN_MAX_AGE": 60,
    }
}

# ----------------------------------------------------------------
# LANDING APP SETTINGS
# ----------------------------------------------------------------
LANDING_CONTACT_RATE_LIMIT = 3
LANDING_CACHE_TTL = 300

# -----------------------------------------------------------------------------
# ADMINS (Recipient for support/contact mails)
# -----------------------------------------------------------------------------
ADMINS = [('Admin', os.getenv("ADMIN_EMAIL", "admin@example.com"))]


# -----------------------------------------------------------------------------
# PASSWORD VALIDATORS
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# INTERNATIONALIZATION
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# STATIC & MEDIA
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise: serve static files via Gunicorn (no Nginx config needed)
# AUTOREFRESH = True → WhiteNoise re-checks staticfiles on every request,
#   so 'collectstatic' changes are picked up WITHOUT restarting Gunicorn.
WHITENOISE_AUTOREFRESH = True
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR / "media")
DEFAULT_LOGO_URL = "https://demo-vistron.zaryz.in/static/img/logo.png"

# -----------------------------------------------------------------------------
# AUTH
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# -----------------------------------------------------------------------------
# CRISPY FORMS
# -----------------------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# -----------------------------------------------------------------------------
# DJANGO REST FRAMEWORK
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}


# -----------------------------------------------------------------------------
# EMAIL (GLOBAL FALLBACK)
# -----------------------------------------------------------------------------
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False") == "True"

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "VMS <no-reply@example.com>",
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

if DEBUG:
    # Use in-memory cache in dev so Redis is not required
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

# -----------------------------------------------------------------------------
# CONTACT FORM MAILER  (landing page only — fully isolated from VMS EMAIL_* above)
# These settings are NEVER referenced by any VMS core feature.
# Fill the corresponding variables in your .env file.
# -----------------------------------------------------------------------------
CONTACT_EMAIL_HOST          = os.environ.get("CONTACT_EMAIL_HOST", "smtp.office365.com")
CONTACT_EMAIL_PORT          = int(os.environ.get("CONTACT_EMAIL_PORT", "587"))
CONTACT_EMAIL_HOST_USER     = os.environ.get("CONTACT_EMAIL_HOST_USER", "connect@zaryz.com")
CONTACT_EMAIL_HOST_PASSWORD = os.environ.get("CONTACT_EMAIL_HOST_PASSWORD", "")
CONTACT_EMAIL_USE_TLS       = os.environ.get("CONTACT_EMAIL_USE_TLS", "True") == "True"
# Company inbox that receives new contact-form lead notifications
CONTACT_EMAIL_RECEIVER      = os.environ.get("CONTACT_EMAIL_RECEIVER", "vms@zaryz.com")
