from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from auth_service.models import UserRole

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'phone_number', 'role', 'created_at', 'updated_at')
        read_only_fields = ('id', 'role', 'created_at', 'updated_at')

class PatientRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    date_of_birth = serializers.DateField(write_only=True, required=True)
    blood_type = serializers.CharField(write_only=True, required=True, max_length=5)
    medical_history = serializers.CharField(write_only=True, required=False, allow_blank=True)
    emergency_contact = serializers.CharField(write_only=True, required=True, max_length=100)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name',
                 'last_name', 'phone_number', 'date_of_birth', 'blood_type',
                 'medical_history', 'emergency_contact')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove non-User model fields
        patient_data = {
            'date_of_birth': validated_data.pop('date_of_birth').isoformat(), # Convert date to ISO format string
            'blood_type': validated_data.pop('blood_type'),
            'medical_history': validated_data.pop('medical_history', ''),
            'emergency_contact': validated_data.pop('emergency_contact')
        }
        validated_data.pop('password2')
        validated_data['role'] = UserRole.PATIENT

        # Create user
        user = User.objects.create_user(**validated_data)

        # Create patient record
        import requests
        patient_data['user_id'] = user.id
        try:
            response = requests.post(
                'http://localhost:8000/api/patients/create/',
                json=patient_data
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            user.delete()
            raise serializers.ValidationError(f"Failed to create patient record: {e}")

        return user

class AdminCreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=UserRole.choices, required=True)

    # Doctor specific fields
    specialization = serializers.CharField(write_only=True, required=False, allow_blank=False, max_length=100)
    license_number = serializers.CharField(write_only=True, required=False, allow_blank=False, max_length=100)

    # Nurse specific fields
    department = serializers.CharField(write_only=True, required=False, allow_blank=False, max_length=100)
    nurse_id = serializers.CharField(write_only=True, required=False, allow_blank=False, max_length=50)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name',
                  'phone_number', 'role', 'specialization', 'license_number',
                  'department', 'nurse_id')

    def validate(self, attrs):
        role = attrs.get('role')
        if role == UserRole.DOCTOR:
            if not attrs.get('specialization'):
                raise serializers.ValidationError({"specialization": "Specialization is required for doctors."})
            if not attrs.get('license_number'):
                raise serializers.ValidationError({"license_number": "License number is required for doctors."})
            attrs.pop('department', None)
            attrs.pop('nurse_id', None)
        elif role == UserRole.NURSE:
            if not attrs.get('department'):
                raise serializers.ValidationError({"department": "Department is required for nurses."})
            if not attrs.get('nurse_id'):
                raise serializers.ValidationError({"nurse_id": "Nurse ID is required for nurses."})
            attrs.pop('specialization', None)
            attrs.pop('license_number', None)
        else:
            attrs.pop('specialization', None)
            attrs.pop('license_number', None)
            attrs.pop('department', None)
            attrs.pop('nurse_id', None)
        return attrs

    def create(self, validated_data):
        user_fields_data = {
            'username': validated_data.get('username'),
            'email': validated_data.get('email'),
            'password': validated_data.get('password'),
            'role': validated_data.get('role'),
            'first_name': validated_data.get('first_name'),
            'last_name': validated_data.get('last_name'),
            'phone_number': validated_data.get('phone_number'),
        }
        cleaned_user_data = {k: v for k, v in user_fields_data.items() if v is not None}

        user = User.objects.create_user(**cleaned_user_data)
        return user

