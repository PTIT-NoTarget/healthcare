from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import MedicalRecord
from .serializers import MedicalRecordSerializer, VitalSignSerializer, NoteSerializer, AttachmentSerializer
from .permissions import IsMedicalProvider, IsPatientOwner, IsRecordProvider, IsAdministrator
from auth_service.models import UserRole
import uuid
from django.utils import timezone


class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient_id', 'provider_id', 'status', 'visit_type']
    search_fields = ['record_id', 'diagnosis', 'chief_complaint', 'treatment_plan']
    ordering_fields = ['visit_date', 'created_at', 'updated_at']
    
    def get_permissions(self):
        if self.action == 'create':
            # Only medical providers can create records
            permission_classes = [IsMedicalProvider]
        elif self.action in ['update', 'partial_update']:
            # Only the provider who created the record can update it
            permission_classes = [IsRecordProvider]
        elif self.action == 'destroy':
            # Only administrators can delete records
            permission_classes = [IsAdministrator]
        elif self.action in ['list', 'retrieve']:
            # Patients can view their own records
            # Providers can view all records
            permission_classes = [IsMedicalProvider | IsPatientOwner]
        else:
            # Default to requiring authentication
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Generate a unique record ID
        record_id = f"MR-{uuid.uuid4().hex[:8].upper()}"
        # Set the provider_id from the current user
        serializer.save(record_id=record_id, provider_id=str(self.request.user.id))
    
    @action(detail=True, methods=['post'])
    def add_vital_sign(self, request, pk=None):
        """Add a vital sign measurement to the medical record"""
        medical_record = self.get_object()
        
        serializer = VitalSignSerializer(data=request.data)
        if serializer.is_valid():
            vital_sign_data = serializer.validated_data
            
            # Add timestamp if not provided
            if 'timestamp' not in vital_sign_data:
                vital_sign_data['timestamp'] = timezone.now()
            
            # Initialize vital_signs list if it doesn't exist
            if not medical_record.vital_signs:
                medical_record.vital_signs = []
            
            # Add the new vital sign
            medical_record.vital_signs.append(vital_sign_data)
            medical_record.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Add a note to the medical record"""
        medical_record = self.get_object()
        
        # Set the author as the current user ID if not provided
        if 'author' not in request.data:
            request.data['author'] = str(request.user.id)
        
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            note_data = serializer.validated_data
            
            # Add timestamp if not provided
            if 'timestamp' not in note_data:
                note_data['timestamp'] = timezone.now()
            
            # Initialize notes list if it doesn't exist
            if not medical_record.notes:
                medical_record.notes = []
            
            # Add the new note
            medical_record.notes.append(note_data)
            medical_record.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """Add an attachment to the medical record"""
        medical_record = self.get_object()
        
        # Set the uploader as the current user ID if not provided
        if 'uploaded_by' not in request.data:
            request.data['uploaded_by'] = str(request.user.id)
        
        serializer = AttachmentSerializer(data=request.data)
        if serializer.is_valid():
            attachment_data = serializer.validated_data
            
            # Add upload timestamp if not provided
            if 'uploaded_at' not in attachment_data:
                attachment_data['uploaded_at'] = timezone.now()
            
            # Initialize attachments list if it doesn't exist
            if not medical_record.attachments:
                medical_record.attachments = []
            
            # Add the new attachment
            medical_record.attachments.append(attachment_data)
            medical_record.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update the status of a medical record"""
        medical_record = self.get_object()
        
        if 'status' not in request.data:
            return Response(
                {"error": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_status = request.data['status']
        if new_status not in [status[0] for status in MedicalRecord._meta.get_field('status').choices]:
            return Response(
                {"error": f"Invalid status. Valid options are: {[status[0] for status in MedicalRecord._meta.get_field('status').choices]}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        medical_record.status = new_status
        medical_record.save()
        
        serializer = self.get_serializer(medical_record)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def patient_records(self, request):
        """Get all medical records for a specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response(
                {"error": "Patient ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If the user is a patient, they can only access their own records
        if request.user.role == UserRole.PATIENT and str(request.user.id) != patient_id:
            return Response(
                {"error": "You can only access your own medical records"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        records = MedicalRecord.objects.filter(patient_id=patient_id)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def provider_records(self, request):
        """Get all medical records created by a specific provider"""
        provider_id = request.query_params.get('provider_id')
        if not provider_id:
            return Response(
                {"error": "Provider ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        records = MedicalRecord.objects.filter(provider_id=provider_id)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)
