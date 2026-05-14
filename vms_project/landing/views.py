import logging
import threading

from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core.cache import cache
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

logger = logging.getLogger(__name__)

from .models import FAQ, GuideVideo, PricingPlan, ContactSubmission, BlogPost
from .forms import ContactForm
from .contact_mailer import send_contact_acknowledgement, send_contact_admin_alert


def _get_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return (x_forwarded.split(',')[0].strip()
            if x_forwarded else request.META.get('REMOTE_ADDR'))


def _is_rate_limited(ip: str) -> bool:
    key   = f"contact_ratelimit:{ip}"
    count = cache.get(key, 0)
    if count >= settings.LANDING_CONTACT_RATE_LIMIT:
        return True
    cache.set(key, count + 1, timeout=3600)
    return False


def _get_landing_data() -> dict:
    cache_key = "landing_page_data"
    data = cache.get(cache_key)
    if data is None:
        data = {
            'faqs': list(
                FAQ.objects.filter(is_published=True)
                   .values('id','question','answer','category')
            ),
            'videos': list(
                GuideVideo.objects.filter(is_published=True)
                          .values('id','title','description',
                                  'youtube_id','thumbnail_url',
                                  'duration_label')
            ),
            'pricing_plans': list(
                PricingPlan.objects.filter(is_published=True)
                           .values('id','name','monthly_price',
                                   'yearly_price','currency',
                                   'billing_note','features',
                                   'cta_label','cta_url',
                                   'is_highlighted')
            ),
        }
        cache.set(cache_key, data,
                  timeout=settings.LANDING_CACHE_TTL)
    return data


class LandingPageView(View):
    def get(self, request):
        context = {
            **_get_landing_data(),
            'contact_form': ContactForm(),
        }
        return render(request,
                      'platform/index.html', context)


class ContactFormView(View):
    """
    Handles the landing-page contact form submission.

    Uses the isolated contact_mailer (CONTACT_EMAIL_* settings only).
    Never touches or references the VMS core EMAIL_* configuration.
    """

    def get(self, request):
        return render(request, 'platform/contact.html')

    @method_decorator(csrf_protect)
    def post(self, request):
        form = ContactForm(request.POST)
        ip   = _get_ip(request)

        if not form.is_valid():
            return JsonResponse(
                {'success': False, 'errors': form.errors},
                status=400
            )

        if _is_rate_limited(ip):
            return JsonResponse(
                {'success': False,
                 'message': 'Too many submissions. Try again later.'},
                status=429
            )

        data = form.cleaned_data

        # Optional extra fields (not in the current form model but passed
        # from the frontend; fall back gracefully if absent)
        phone   = data.get('phone', '')
        company = data.get('company', '')

        # Persist submission to database safely
        try:
            ContactSubmission.objects.create(
                full_name  = data['full_name'],
                email      = data['email'],
                phone      = phone,
                company    = company,
                subject    = data.get('subject', ''),
                message    = data['message'],
                ip_address = ip,
            )
        except Exception as e:
            logger.error("Failed to save contact submission: %s", str(e), exc_info=True)
            return JsonResponse(
                {'success': False, 'message': 'Internal database error. Please try again later.'},
                status=500
            )

        # ── Send both emails via the isolated CONTACT_* SMTP connection ──
        # Use a background thread to prevent the SMTP request from blocking the user response

        def send_emails_bg():
            try:
                ack_sent = send_contact_acknowledgement(
                    user_name  = data['full_name'],
                    user_email = data['email'],
                )
                alert_sent = send_contact_admin_alert(
                    name    = data['full_name'],
                    email   = data['email'],
                    phone   = phone,
                    company = company,
                    message = data['message'],
                )
                if not ack_sent or not alert_sent:
                    logger.warning(

                        "ContactFormView: one or more emails failed "
                        "(ack=%s, alert=%s) for %s",
                        ack_sent, alert_sent, data['email'],
                    )
            except Exception:
                logger.exception(

                    "ContactFormView: unexpected error while sending contact emails "
                    "for %s", data['email']
                )

        # Fire and forget the background task
        threading.Thread(target=send_emails_bg, daemon=True).start()


        return JsonResponse({
            'success': True,
            'message': "Thanks! We'll get back to you soon.",
        })



class VideoListView(View):
    def get(self, request):
        videos = GuideVideo.objects.filter(is_published=True)
        return render(request, 'platform/videos.html', {'videos': videos})


class BlogListView(View):
    def get(self, request):
        posts = BlogPost.objects.filter(is_published=True)
        return render(request, 'platform/blog_list.html', {'posts': posts})


class BlogDetailView(View):
    def get(self, request, slug):
        post = BlogPost.objects.get(slug=slug, is_published=True)
        return render(request, 'platform/blog_detail.html', {'post': post})


class PrivacyPolicyView(View):
    def get(self, request):
        return render(request, 'platform/privacy.html')
