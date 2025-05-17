from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'user_id', 'date_of_birth', 'blood_type', 'medical_history', 'emergency_contact', 'created_at', 'updated_at']
