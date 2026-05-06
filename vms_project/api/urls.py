from django.urls import path
from . import views

urlpatterns = [
    path('visits/', views.VisitListAPI.as_view(), name='api_visits'),
    path('stats/7days/', views.visits_last_7_days, name='api_7days'),
]
