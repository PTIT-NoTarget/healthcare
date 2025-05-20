from rest_framework import serializers
from .models import Pharmacist


class PharmacistSerializer(serializers.ModelSerializer):
    # Add read-only fields for user data
    username = serializers.CharField(read_only=True, required=False)
    email = serializers.EmailField(read_only=True, required=False)
    first_name = serializers.CharField(read_only=True, required=False)
    last_name = serializers.CharField(read_only=True, required=False)
    
    class Meta:
        model = Pharmacist
        fields = [
            'id', 'user_id', 'pharmacist_id', 'username', 'email', 'first_name', 'last_name',
            'license_number', 'specialization', 'pharmacy_id', 'is_active', 
            'contact_phone', 'contact_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
