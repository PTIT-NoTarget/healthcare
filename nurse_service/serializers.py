from rest_framework import serializers
from .models import Nurse

class NurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nurse
        fields = ['id', 'user_id', 'department', 'nurse_id', 'created_at', 'updated_at']
