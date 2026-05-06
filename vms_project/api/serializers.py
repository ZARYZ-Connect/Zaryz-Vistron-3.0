from rest_framework import serializers
from visitors.models import VisitRequest

class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitRequest
        fields = '__all__'
