# dashboard/context_processors.py
from dashboard.models import Department, JobRole, Employee, MailTemplate
from visitors.models import VisitRequest, VisitType
from django.utils import timezone

def admin_sidebar_stats(request):
    """
    Provides global stats for the Admin Sidebar Live Overview.
    Only calculated if the user is a superuser or admin.
    """
    if not request.user.is_authenticated or not (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'):
        return {}

    try:
        # Organization scoping
        org = getattr(request, 'organization', None)
        if not org:
            return {}

        # Core counts for Admin Overview (Scoped)
        total_employees = Employee.objects.filter(organization=org).count()
        total_departments = Department.objects.filter(organization=org).count()
        
        # Visitor stats for Admin (Today - Scoped)
        today = timezone.localtime().date()
        today_visitors = VisitRequest.objects.filter(organization=org, visit_date=today).count()
        
        # Pending requests requiring attention (Scoped)
        pending_requests = VisitRequest.objects.filter(organization=org, status='pending').count()

        return {
            'admin_stats': {
                'total_employees': total_employees,
                'total_departments': total_departments,
                'today_visitors': today_visitors,
                'pending_requests': pending_requests,
            }
        }
    except Exception:
        return {
            'admin_stats': {
                'total_employees': 0,
                'total_departments': 0,
                'today_visitors': 0,
                'pending_requests': 0,
            }
        }
