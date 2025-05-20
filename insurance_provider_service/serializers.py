from rest_framework import serializers
from .models import InsuranceProvider

class InsuranceProviderSerializer(serializers.ModelSerializer):
    # Add fields for user data
    username = serializers.CharField(read_only=True, required=False)
    email = serializers.EmailField(read_only=True, required=False)
    first_name = serializers.CharField(read_only=True, required=False)
    last_name = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = InsuranceProvider
        fields = [
            'id',
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
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
