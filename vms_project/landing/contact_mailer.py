"""
landing/contact_mailer.py
=========================
Isolated SMTP mailer for the landing-page contact form.

Rules:
  - ONLY reads from CONTACT_EMAIL_* settings.
  - NEVER imports or references EMAIL_HOST / EMAIL_HOST_USER or any
    other VMS-core mail setting.
  - Uses django.core.mail.get_connection() to build a private SMTP
    connection that is completely separate from Django's default backend.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_contact_connection():
    """
    Build and return an SMTP connection using only the CONTACT_EMAIL_*
    settings.  This connection is never shared with the VMS mail system.
    fail_silently=True ensures a broken SMTP config never raises an
    unhandled exception that would surface as a 500 to the visitor.
    """
    return get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=settings.CONTACT_EMAIL_HOST,
        port=settings.CONTACT_EMAIL_PORT,
        username=settings.CONTACT_EMAIL_HOST_USER,
        password=settings.CONTACT_EMAIL_HOST_PASSWORD,
        use_tls=settings.CONTACT_EMAIL_USE_TLS,
        fail_silently=True,
    )


def _send(subject: str, html_content: str, to: list[str]) -> bool:
    """
    Send a single email through the isolated contact SMTP connection.
    Supports HTML with a fallback plain-text version.
    Always returns True/False — never raises to the caller.
    """
    try:
        password = getattr(settings, "CONTACT_EMAIL_HOST_PASSWORD", "")
        if not password:
            logger.warning(
                "contact_mailer: CONTACT_EMAIL_HOST_PASSWORD is not set — "
                "email to %s will be skipped.", to
            )
            return False

        # Create a fallback plain-text version from the HTML
        text_content = strip_tags(html_content)

        connection = _get_contact_connection()
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=f"Zaryz Vistron <{settings.CONTACT_EMAIL_HOST_USER}>",
            to=to,
            connection=connection,
        )
        msg.attach_alternative(html_content, "text/html")
        sent = msg.send(fail_silently=False)
        logger.info("contact_mailer: sent '%s' to %s (result=%s)", subject, to, sent)
        return bool(sent)
    except Exception as exc:
        logger.error(
            "contact_mailer: failed to send email to %s — %s",
            to,
            exc,
            exc_info=True,
        )
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def send_contact_acknowledgement(user_name: str, user_email: str) -> bool:
    """
    Send a thank-you acknowledgement to the person who submitted the form.
    """
    subject = "We received your message — Zaryz Vistron"
    html_content = render_to_string(
        "landing/emails/acknowledgement.html",
        {"user_name": user_name}
    )
    return _send(subject=subject, html_content=html_content, to=[user_email])


def send_contact_admin_alert(
    name: str,
    email: str,
    phone: str,
    company: str,
    message: str,
) -> bool:
    """
    Send a structured lead-details notification to the company inbox.
    """
    subject = f"[New Lead] Contact Form Submission from {name}"
    html_content = render_to_string(
        "landing/emails/admin_alert.html",
        {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "message": message,
        }
    )
    return _send(
        subject=subject,
        html_content=html_content,
        to=[settings.CONTACT_EMAIL_RECEIVER],
    )

