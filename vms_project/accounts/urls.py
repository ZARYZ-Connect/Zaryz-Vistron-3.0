from django.urls import path
from .views import CustomLoginView, profile, magic_login
from django.contrib.auth.views import LogoutView

app_name = 'accounts'
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='visitors:home'), name='logout'),
    path('profile/', profile, name='profile'),
    path('magic-login/', magic_login, name='magic_login'),
]
