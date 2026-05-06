from django.urls import path
from .views import LandingPageView, ContactFormView, VideoListView, BlogListView, BlogDetailView, PrivacyPolicyView

urlpatterns = [
    path('',                      LandingPageView.as_view(),  name='landing'),

    # Landing-page contact form — two entry points:
    #   /contact/      (legacy, used by the HTML form & existing links)
    #   /api/contact/  (JSON API endpoint — isolated CONTACT_* SMTP mailer)
    path('contact/',              ContactFormView.as_view(),  name='contact_submit'),
    path('api/contact/',          ContactFormView.as_view(),  name='api_contact_submit'),

    path('videos/',               VideoListView.as_view(),    name='video_list'),
    path('blog/',                 BlogListView.as_view(),     name='blog_list'),
    path('blog/<slug:slug>/',     BlogDetailView.as_view(),    name='blog_detail'),
    path('privacy-policy/',       PrivacyPolicyView.as_view(), name='privacy_policy'),
]
