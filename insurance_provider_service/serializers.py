from rest_framework import serializers
from .models import InsuranceProvider
from auth_service.serializers import UserSerializer # Assuming UserSerializer is available

class InsuranceProviderSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True) # Only include if user liaison profile is relevant for API output

    class Meta:
        model = InsuranceProvider
        fields = [
            'id',
            # 'user',
            'company_name',
            'provider_id_number',
            'contact_email',
            'contact_phone',
            'address',
            'website',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')
