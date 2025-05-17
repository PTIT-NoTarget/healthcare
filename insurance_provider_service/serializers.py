from rest_framework import serializers
from .models import InsuranceProvider
from auth_service.serializers import UserSerializer


class InsuranceProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = InsuranceProvider
        fields = ['id', 'user', 'company_name', 'provider_id', 'contact_email', 'contact_phone'] 