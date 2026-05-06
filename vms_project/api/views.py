from rest_framework import generics, permissions
from .serializers import VisitSerializer
from visitors.models import VisitRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

class VisitListAPI(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = VisitRequest.objects.all()
    serializer_class = VisitSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def visits_last_7_days(request):
    today = timezone.now().date()
    data = []
    for i in range(7):
        d = today - timedelta(days=i)
        count = VisitRequest.objects.filter(visit_date=d).count()
        data.append({'date': d.isoformat(), 'count': count})
    return Response(list(reversed(data)))
