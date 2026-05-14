from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        # superuser or 'admin' role -> custom admin dashboard
        if user.is_authenticated and (user.is_superuser or getattr(user, 'role', None) == 'admin'):
            return reverse_lazy('dashboard:admin_dashboard')
        # security/reception -> security dashboard
        if user.is_authenticated and getattr(user, 'role', None) in ('security', 'reception'):
            return reverse_lazy('security:security_dashboard')
        # default -> visitor home
        return reverse_lazy('visitors:home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        return response


@login_required
def profile(request):
    """Profile view with role-based dashboard routing"""
    return render(request, 'accounts/profile.html', {
        'user': request.user,
    })


# Optional: Add a redirect view to route users to appropriate dashboard
@login_required
def dashboard_redirect(request):
    """Redirect users to their appropriate dashboard based on role"""
    user = request.user
    
    # Superuser or admin role
    if user.is_superuser or (hasattr(user, 'role') and user.role == 'admin'):
        return redirect('dashboard:admin_dashboard')
    
    # Security or reception role
    elif hasattr(user, 'role') and user.role in ['security', 'reception']:
        return redirect('security:security_dashboard')
    
    # Default fallback - you can create a general user dashboard
    else:
        return redirect('accounts:profile')
# Temporary magic login for testing
def magic_login(request):
    try:
        user = User.objects.get(username='likith')
        login(request, user)
        return redirect('dashboard:admin_dashboard')
    except Exception as e:
        return render(request, 'accounts/login.html', {'error': str(e)})
