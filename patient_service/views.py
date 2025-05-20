from rest_framework import generics, permissions, status
from rest_framework.response import Response
import requests
from .models import Patient
from .serializers import PatientSerializer
from .permissions import IsPatientOwnerOrStaff

class PatientCreateView(generics.CreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]  # Since this is called internally during registration

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # user_id is now expected to be in the validated_data from the request body
        serializer.save()

class PatientDetailView(generics.RetrieveUpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]

class PatientListView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Check if the user is authenticated before accessing role attribute
        if self.request.user.is_authenticated:
            # Check if the user has a role attribute and is a patient
            if hasattr(self.request.user, 'role') and self.request.user.role == 'PATIENT':
                return Patient.objects.filter(user_id=self.request.user.id)
        # Return all patients for unauthenticated users or non-patient users
        return Patient.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for patient in queryset:
            patient_data = PatientSerializer(patient).data
            try:
                auth_service_url = f'http://localhost:8000/api/auth/internal/user/{patient.user_id}/'
                response = requests.get(auth_service_url)
                response.raise_for_status()
                user_data = response.json()

                patient_data['username'] = user_data.get('username')
                patient_data['email'] = user_data.get('email')
                patient_data['first_name'] = user_data.get('first_name')
                patient_data['last_name'] = user_data.get('last_name')
                patient_data['phone_number'] = user_data.get('phone_number')
            except requests.exceptions.RequestException as e:
                patient_data['username'] = 'N/A'
                patient_data['email'] = 'N/A'
                patient_data['first_name'] = 'N/A'
                patient_data['last_name'] = 'N/A'
                patient_data['phone_number'] = 'N/A'
            except Exception as e:
                patient_data['username'] = 'Error'
                patient_data['email'] = 'Error'
                patient_data['first_name'] = 'Error'
                patient_data['last_name'] = 'Error'
                patient_data['phone_number'] = 'Error'

            data.append(patient_data)
        return Response(data)

