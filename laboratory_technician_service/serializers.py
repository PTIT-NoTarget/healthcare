from rest_framework import serializers
from .models import LaboratoryTechnician


class LaboratoryTechnicianSerializer(serializers.ModelSerializer):
    # Add read-only fields for user data
    username = serializers.CharField(read_only=True, required=False)
    email = serializers.EmailField(read_only=True, required=False)
    first_name = serializers.CharField(read_only=True, required=False)
    last_name = serializers.CharField(read_only=True, required=False)
    
    class Meta:
        model = LaboratoryTechnician
        fields = [
            'id', 'user_id', 'username', 'email', 'first_name', 'last_name',
            'employee_id', 'specialization', 'laboratory_name', 'certification',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 