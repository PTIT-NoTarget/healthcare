from rest_framework import serializers
from .models import LaboratoryTechnician
from auth_service.serializers import UserSerializer


class LaboratoryTechnicianSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = LaboratoryTechnician
        fields = ['id', 'user', 'employee_id', 'specialization', 'laboratory_name', 'certification'] 