from visitors.models import VisitRequest
from django.utils import timezone
from django.db.models import Q

def security_stats(request):
    if not request.user.is_authenticated:
        return {}
    
    try:
        if request.user.role not in ('security', 'reception') and not request.user.is_superuser:
            return {}
    except AttributeError:
        return {}

    organization = getattr(request, "organization", None)

    today = timezone.localdate()
    from django.db.models import Q
    todays_qs = VisitRequest.objects.filter(
        Q(visit_date=today) | Q(created_at__date=today)
    )
    
    if organization:
        todays_qs = todays_qs.filter(organization=organization)

    return {
        'security_counts': {
            'total': todays_qs.count(),
            'checked_in': todays_qs.filter(status='checked_in').count(),
            'awaiting': todays_qs.filter(status='approved').count(),
            'checked_out': todays_qs.filter(status='checked_out').count(),
        }
    }
