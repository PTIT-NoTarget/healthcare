from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
import requests  # Make sure requests is imported

from .models import UserRole
from .serializers import AdminCreateUserSerializer, PatientRegisterSerializer, UserSerializer, ProfileUpdateSerializer

User = get_user_model()


class PatientRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PatientRegisterSerializer


class AdminCreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AdminCreateUserSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.role == UserRole.ADMINISTRATOR:
            return Response(
                {"error": "Only administrators can create staff accounts"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # This now only creates the User object
            role = serializer.validated_data.get('role')
            user_id = user.id

            service_payload = {'user_id': user_id}
            service_endpoint = None

            if role == UserRole.DOCTOR:
                service_endpoint = 'http://localhost:8000/api/doctors/create/'
                service_payload['specialization'] = serializer.validated_data.get('specialization')
                service_payload['license_number'] = serializer.validated_data.get('license_number')
            elif role == UserRole.NURSE:
                service_endpoint = 'http://localhost:8000/api/nurses/create/'  # Assuming this will be the create endpoint for nurses
                service_payload['department'] = serializer.validated_data.get('department')
                service_payload['nurse_id'] = serializer.validated_data.get('nurse_id')

            if service_endpoint:
                try:
                    api_response = requests.post(service_endpoint, json=service_payload)
                    api_response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
                except requests.exceptions.RequestException as e:
                    user.delete()  # Rollback user creation if service call fails
                    return Response(
                        {"error": f"Failed to create {role.lower()} record: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            user_serializer = UserSerializer(user)
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


# New view for internal service communication
class InternalUserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Changed to AllowAny
    lookup_field = 'id'

