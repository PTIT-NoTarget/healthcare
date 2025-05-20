from rest_framework import serializers
from .models import Administrator


class AdministratorSerializer(serializers.ModelSerializer):
    # Add read-only fields for user data that will be populated from auth service
    username = serializers.CharField(read_only=True, required=False)
    email = serializers.EmailField(read_only=True, required=False)
    first_name = serializers.CharField(read_only=True, required=False)
    last_name = serializers.CharField(read_only=True, required=False)
    
    class Meta:
        model = Administrator
        fields = [
            'id', 'user_id', 'username', 'email', 'first_name', 'last_name',
            'employee_id', 'department', 'access_level', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 