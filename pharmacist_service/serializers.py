from rest_framework import serializers
from .models import Pharmacist
from auth_service.serializers import UserSerializer


class PharmacistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Pharmacist
        fields = ['id', 'user', 'license_number', 'specialization', 'pharmacy_name'] 