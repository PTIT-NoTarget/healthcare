from rest_framework import serializers
from .models import Doctor

class DoctorSerializer(serializers.ModelSerializer):
    # Fields from auth_service
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    phone_number = serializers.CharField(read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'user_id', 'username', 'email', 'first_name', 'last_name', 'phone_number',
            'specialization', 'license_number', 'created_at', 'updated_at'
        ]
