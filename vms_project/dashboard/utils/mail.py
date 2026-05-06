# dashboard/utils/mail.py

from django.template import Template, Context
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.staticfiles.storage import staticfiles_storage

from dashboard.models import MailTemplate

import os
import sys


# --------------------------------------------------
# HELPER: Make absolute URL
# --------------------------------------------------

def _absolute(request, value):
    if not value:
        return None
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return request.build_absolute_uri(value) if request else value


# --------------------------------------------------
# HELPER: Convert HTML to clean text
# --------------------------------------------------

def _text_from_html(html):
    text = strip_tags(html).strip()
    import re
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text


# --------------------------------------------------
# Render Template From DB
# --------------------------------------------------

DEFAULT_TEMPLATES = {
    "otp_email": {
        "title": "OTP Verification",
        "subject": "Your Verification Code – {{ organization_name }}",
        "body": "<p>Hi {{ visitor_name }},</p><p>Your one-time verification code is: <strong style='font-size:1.5em;letter-spacing:4px;'>{{ otp_code }}</strong></p><p>This code is valid for <strong>{{ otp_minutes }} minutes</strong>. Do not share it with anyone.</p><p>Regards,<br>{{ organization_name }} Team</p>"
    },
    "visitor_thanks": {
        "title": "Registration Complete",
        "subject": "Visit Registration Confirmed – {{ organization_name }}",
        "body": "<p>Hi {{ visitor_name }},</p><p>Your visit request has been successfully submitted and is awaiting approval.</p><p><strong>Visit Date:</strong> {{ visit_date }}<br><strong>Time:</strong> {{ visit_start_time }} – {{ visit_end_time }}</p><p>You will receive another email once your visit has been approved or rejected.</p><p>Regards,<br>{{ organization_name }} Team</p>"
    },
    "approver_notify": {
        "title": "Approval Required",
        "subject": "Action Required: Visitor {{ visitor_name }} is waiting – {{ organization_name }}",
        "body": "<p>Hi {{ approver_name }},</p><p><strong>{{ visitor_name }}</strong> has registered for a visit and is waiting for your approval.</p><table style='border-collapse:collapse;width:100%;'><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Visit Date</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ visit_date }}</td></tr><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Time</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ visit_start_time }} – {{ visit_end_time }}</td></tr><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Purpose</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ purpose }}</td></tr><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Phone</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ visitor_phone }}</td></tr></table><p><a href='{{ approve_url }}' style='display:inline-block;padding:10px 20px;background:#6366f1;color:white;text-decoration:none;border-radius:8px;margin-top:12px;'>Approve Visit</a> &nbsp; <a href='{{ reject_url }}' style='display:inline-block;padding:10px 20px;background:#ef4444;color:white;text-decoration:none;border-radius:8px;margin-top:12px;'>Reject Visit</a></p><p>Regards,<br>{{ organization_name }} Team</p>"
    },
    "approval_result": {
        "title": "Visit Status Update",
        "subject": "Your Visit Request has been {{ status|title }} – {{ organization_name }}",
        "body": "<p>Hi {{ visitor_name }},</p><p>Your visit request has been <strong>{{ status }}</strong>.</p>{% if status == 'approved' %}<p>Please use the QR code below to check in at the reception.</p>{% if qr_url %}<p><img src='{{ qr_url }}' style='width:200px;height:200px;' /></p>{% endif %}<p><strong>Badge ID:</strong> {{ badge_id }}</p>{% else %}<p><strong>Reason:</strong> {{ reason }}</p>{% endif %}<p>Regards,<br>{{ organization_name }} Team</p>"
    },
    "checkin_receipt": {
        "title": "Check-in Confirmation",
        "subject": "You have checked in at {{ organization_name }}",
        "body": "<p>Hi {{ visitor_name }},</p><p>You have successfully <strong>checked in</strong> at {{ organization_name }}.</p><table style='border-collapse:collapse;width:100%;'><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Badge ID</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ badge_id }}</td></tr><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Check-in Time</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ checkin_time }}</td></tr><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Visit Date</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ visit_date }}</td></tr></table><p>Please return your badge when you leave. Thank you for visiting!</p><p>Regards,<br>{{ organization_name }} Team</p>"
    },
    "employee_visitor_checkin": {
        "title": "Visitor Checked In",
        "subject": "Your visitor {{ visitor_name }} has arrived – {{ organization_name }}",
        "body": "<p>Hi {{ employee_name }},</p><p>Your visitor <strong>{{ visitor_name }}</strong> has checked in and is at the reception.</p><table style='border-collapse:collapse;width:100%;'><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Badge ID</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ badge_id }}</td></tr><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Arrived At</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ checkin_time }}</td></tr></table><p>Please come to the reception to receive your visitor.</p><p>Regards,<br>{{ organization_name }} Team</p>"
    },
    "checkout_receipt": {
        "title": "Check-out Confirmation",
        "subject": "Visit completed at {{ organization_name }} – Thank you!",
        "body": "<p>Hi {{ visitor_name }},</p><p>You have successfully <strong>checked out</strong> from {{ organization_name }}. Thank you for your visit!</p><table style='border-collapse:collapse;width:100%;'><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Badge ID</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ badge_id }}</td></tr><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Check-in Time</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ checkin_time }}</td></tr><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Check-out Time</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ checkout_time }}</td></tr><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Visit Date</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ visit_date }}</td></tr></table><p>We hope to see you again soon!</p><p>Regards,<br>{{ organization_name }} Team</p>"
    },
    "employee_visitor_checkout": {
        "title": "Visitor Checked Out",
        "subject": "Your visitor {{ visitor_name }} has left – {{ organization_name }}",
        "body": "<p>Hi {{ employee_name }},</p><p>Your visitor <strong>{{ visitor_name }}</strong> has checked out from {{ organization_name }}.</p><table style='border-collapse:collapse;width:100%;'><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Badge ID</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ badge_id }}</td></tr><tr><td style='padding:6px;border:1px solid #ddd;'><strong>Check-out Time</strong></td><td style='padding:6px;border:1px solid #ddd;'>{{ checkout_time }}</td></tr></table><p>Regards,<br>{{ organization_name }} Team</p>"
    },
}

def _wrap_html(body_html, context):
    org_name = context.get("organization_name", "ZARYZ VISTRON")
    if org_name.upper() == "ZARYZ VISTRON" or org_name == "VMS":
        logo_html = '<span style="color: #7c4dff;">ZARYZ VISTRON</span>'
        org_name = '© 2026 <span style="color: #7c4dff;">Zaryz</span> Vistron'
    else:
        logo_html = org_name

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; margin: 0; padding: 0;">
    <div style="width: 100%; padding: 40px 0; background-color: #f8fafc;">
        <div style="max-width: 600px; background-color: #ffffff; margin: 0 auto; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 50px rgba(124, 77, 255, 0.08); border: 1px solid #eef2f6;">
            
            <div style="background-color: #ffffff; padding: 35px 20px; text-align: center; border-bottom: 1px solid #f8fafc;">
                 <div style="color: #7c4dff; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">{logo_html}</div>
            </div>
            
            <div style="padding: 40px 30px; font-size: 15px; color: #475569; line-height: 1.6;">
                {body_html}
            </div>
            
            <div style="background-color: #fcfcfd; padding: 30px; text-align: center; border-top: 1px solid #f1f5f9;">
                <p style="font-size: 12px; color: #94a3b8; font-weight: 500; margin: 0;">{org_name}. All rights reserved.</p>
                <p style="font-size: 11px; color: #cbd5e1; margin-top: 8px;">Lead Alert Service — Automated System Notification</p>
            </div>
        </div>
    </div>
</body>
</html>"""


def render_mail_template(key, context, org=None):
    try:
        if org:
            tpl = MailTemplate.objects.get(key=key, organization=org)
        else:
            tpl = MailTemplate.objects.get(key=key)
        subject_template = tpl.subject
        body_template = tpl.body
    except MailTemplate.DoesNotExist:
        defaults = DEFAULT_TEMPLATES.get(key, {"subject": f"[{key}] Notification", "body": f"Notification for {key}"})
        subject_template = defaults["subject"]
        body_template = defaults["body"]
        
        if org and key in DEFAULT_TEMPLATES:
            try:
                MailTemplate.objects.create(
                    organization=org,
                    key=key,
                    title=DEFAULT_TEMPLATES[key].get("title", key),
                    subject=subject_template,
                    body=body_template
                )
            except Exception:
                pass

    subject = Template(subject_template).render(Context(context))
    raw_html = Template(body_template).render(Context(context))
    text = _text_from_html(raw_html)
    html = _wrap_html(raw_html, context)

    return subject, text, html





# --------------------------------------------------
# Get SMTP (Org specific or fallback)
# --------------------------------------------------

def _get_smtp_connection(org):
    try:
        cfg = org.mail_config
        if cfg.is_active and cfg.smtp_host:
            return get_connection(
                host=cfg.smtp_host,
                port=cfg.port,
                username=cfg.username,
                password=cfg.password,
                use_tls=cfg.use_tls,
                use_ssl=cfg.use_ssl,
                fail_silently=True,
            )
    except Exception:
        pass

    try:
        return get_connection(fail_silently=True)
    except Exception:
        pass

    return get_connection(
        backend="django.core.mail.backends.console.EmailBackend"
    )


# --------------------------------------------------
# MAIN SEND FUNCTION
# --------------------------------------------------

def send_mail_template(
    key,
    to_list,
    context,
    request=None,
    fail_silently=False,
):
    if isinstance(to_list, str):
        to_list = [to_list]

    org = getattr(request, "organization", None)
    if not org:
        raise RuntimeError("Organization not found in request")

    if settings.DEBUG:
        print(f"\n[MAIL LOG] ATTEMPTING TO SEND '{key}' TO {to_list}...", flush=True)

    ctx = dict(context)

    # --------------------------------------------------
    # ✅ SAFE ABSOLUTE LOGO (NO CID)
    # --------------------------------------------------

    if request:
        ctx["logo_url"] = request.build_absolute_uri(
            staticfiles_storage.url("img/logo.png")
        )
    else:
        ctx["logo_url"] = getattr(
            settings,
            "DEFAULT_LOGO_URL",
            ""
        )

    ctx.setdefault(
        "organization_name",
        getattr(settings, "PLATFORM_NAME", "VMS"),
    )

    # Make important URLs absolute
    for k in ["approve_url", "reject_url", "badge_url", "qr_url"]:
        if ctx.get(k):
            ctx[k] = _absolute(request, ctx[k])

    subject, text, html = render_mail_template(key, ctx, org=org)

    connection = _get_smtp_connection(org)

    from_email = (
        org.mail_config.from_email
        if hasattr(org, "mail_config") and org.mail_config.from_email
        else settings.DEFAULT_FROM_EMAIL
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=from_email,
        to=to_list,
        connection=connection,
    )

    msg.attach_alternative(html, "text/html")
    
    # 📝 DEBUG ECHO: Always show in terminal for easier local development
    if settings.DEBUG:
        print(f"\n[DEBUG EMAIL] To: {to_list} | Subject: {subject}", flush=True)
        print(f"[DEBUG EMAIL] Body (Text): {text[:200]}...", flush=True)

        # Print specific URLs if they exist for easy copy-paste
        for k in ["approve_url", "reject_url", "badge_url", "qr_url"]:
            if k in ctx:
                print(f"🔗 {k.replace('_', ' ').upper()}: {ctx[k]}", flush=True)

        if "otp_code" in context:
            print(f">>>>>> OTP CODE: {context['otp_code']} <<<<<<\n", flush=True)
        sys.stdout.flush()

    return msg.send(fail_silently=fail_silently)

