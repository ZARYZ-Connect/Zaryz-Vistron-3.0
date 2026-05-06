# security/urls.py
from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('', views.security_dashboard, name='security_dashboard'),
    path('scan-qr/', views.scan_qr, name='scan_qr'),
    path('verify-qr/', views.verify_qr, name='verify_qr'),
    path('badge-lookup/', views.badge_lookup, name='badge_lookup'),
    path('badge/<int:visit_id>/', views.badge_detail, name='badge_detail'),
    path('checkin/<int:visit_id>/', views.checkin, name='checkin'),
    path('checkout/<int:visit_id>/', views.checkout, name='checkout'),

    # NEW list pages
    path('today/', views.all_today_list, name='all_today_list'),
    path('checked-in/', views.checked_in_list, name='checked_in_list'),
    path('awaiting/', views.awaiting_list, name='awaiting_list'),
    path('checked-out/', views.checked_out_list, name='checked_out_list'),
]
