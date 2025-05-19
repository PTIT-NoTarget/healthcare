from rest_framework import generics, permissions, status
from rest_framework.response import Response
import requests
from .models import Doctor
from .serializers import DoctorSerializer
from .permissions import IsDoctorOrAdmin, IsAdminUser

class DoctorCreateView(generics.CreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]

class DoctorDetailView(generics.RetrieveUpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsDoctorOrAdmin]

class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for doctor in queryset:
            doctor_data = DoctorSerializer(doctor).data
            try:
                auth_service_url = f'http://localhost:8000/api/auth/internal/user/{doctor.user_id}/'
                response = requests.get(auth_service_url)
                response.raise_for_status()
                user_data = response.json()

                doctor_data['username'] = user_data.get('username')
                doctor_data['email'] = user_data.get('email')
                doctor_data['first_name'] = user_data.get('first_name')
                doctor_data['last_name'] = user_data.get('last_name')
                doctor_data['phone_number'] = user_data.get('phone_number')
            except requests.exceptions.RequestException as e:
                doctor_data['username'] = 'N/A'
                doctor_data['email'] = 'N/A'
                doctor_data['first_name'] = 'N/A'
                doctor_data['last_name'] = 'N/A'
                doctor_data['phone_number'] = 'N/A'
            except Exception as e:
                doctor_data['username'] = 'Error'
                doctor_data['email'] = 'Error'
                doctor_data['first_name'] = 'Error'
                doctor_data['last_name'] = 'Error'
                doctor_data['phone_number'] = 'Error'

            data.append(doctor_data)
        return Response(data)

