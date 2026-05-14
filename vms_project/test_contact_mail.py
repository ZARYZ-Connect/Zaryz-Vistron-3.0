"""
Test script — sends both contact form emails using real SMTP credentials.
Run: python test_contact_mail.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vms_project.settings")
django.setup()

from django.conf import settings
from landing.contact_mailer import send_contact_acknowledgement, send_contact_admin_alert

# ── Demo visitor details ──────────────────────────────────────────────────────
DEMO_NAME    = "Rahul Sharma"
DEMO_EMAIL   = "rahul.sharma@demotest.com"
DEMO_PHONE   = "+91 98765 43210"
DEMO_COMPANY = "Acme Pvt Ltd"
DEMO_MESSAGE = (
    "Hi, I came across Zaryz Vistron and I am interested in scheduling "
    "a demo for our office of 500 employees. "
    "Could you please schedule a call at your earliest convenience?"
)
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 55)
print("  CONTACT FORM — LIVE EMAIL TEST")
print("=" * 55)
print(f"  SMTP Host  : {settings.CONTACT_EMAIL_HOST}:{settings.CONTACT_EMAIL_PORT}")
print(f"  Sending AS : {settings.CONTACT_EMAIL_HOST_USER}")
print(f"  Alert TO   : {settings.CONTACT_EMAIL_RECEIVER}")
print("=" * 55)
print()

# 1) Acknowledgement to the visitor
print(f"[1/2] Sending acknowledgement to visitor...")
print(f"      To : {DEMO_EMAIL}")
ok1 = send_contact_acknowledgement(
    user_name=DEMO_NAME,
    user_email=DEMO_EMAIL,
)
print(f"      Result : {'SUCCESS' if ok1 else 'FAILED'}")
print()

# 2) Lead alert to the company inbox
print(f"[2/2] Sending lead alert to receiver...")
print(f"      To : {settings.CONTACT_EMAIL_RECEIVER}")
ok2 = send_contact_admin_alert(
    name=DEMO_NAME,
    email=DEMO_EMAIL,
    phone=DEMO_PHONE,
    company=DEMO_COMPANY,
    message=DEMO_MESSAGE,
)
print(f"      Result : {'SUCCESS' if ok2 else 'FAILED'}")
print()

print("=" * 55)
if ok1 and ok2:
    print("  ALL EMAILS SENT SUCCESSFULLY")
else:
    print("  ONE OR MORE EMAILS FAILED — check traceback above")
print("=" * 55)
