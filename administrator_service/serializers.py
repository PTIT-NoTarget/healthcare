from rest_framework import serializers
from .models import Administrator
from auth_service.serializers import UserSerializer


class AdministratorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Administrator
        fields = ['id', 'user', 'employee_id', 'department', 'access_level'] 