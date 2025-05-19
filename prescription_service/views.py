from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Prescription
from .serializers import PrescriptionSerializer
from .permissions import IsDoctorUser, IsPrescriptionDoctor, IsPrescriptionPatient, IsPharmacistUser
import uuid
from django.utils import timezone


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient_id', 'doctor_id', 'status', 'pharmacy_id', 'is_refillable']
    search_fields = ['prescription_id', 'diagnosis', 'notes']
    ordering_fields = ['date_prescribed', 'created_at', 'updated_at']
    
    def get_permissions(self):
        if self.action == 'create':
            # Only doctors can create prescriptions
            permission_classes = [IsDoctorUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only the doctor who created the prescription can modify or delete it
            permission_classes = [IsPrescriptionDoctor]
        elif self.action == 'dispense':
            # Only pharmacists can dispense prescriptions
            permission_classes = [IsPharmacistUser]
        elif self.action in ['list', 'retrieve']:
            # Doctors, patients (their own), pharmacists can view prescriptions
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Default to authenticated for other actions
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Generate a unique prescription ID
        prescription_id = f"PRE-{uuid.uuid4().hex[:8].upper()}"
        # Set the doctor_id from the current user
        serializer.save(prescription_id=prescription_id, doctor_id=str(self.request.user.id))
    
    @action(detail=True, methods=['post'])
    def dispense(self, request, pk=None):
        """Mark a prescription as dispensed by a pharmacy"""
        prescription = self.get_object()
        
        # Check if prescription is already dispensed
        if prescription.status not in ['CREATED']:
            return Response(
                {"error": "Prescription cannot be dispensed. Current status: " + prescription.status},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update prescription with pharmacy info
        prescription.status = 'DISPENSED'
        prescription.pharmacy_id = request.data.get('pharmacy_id')
        prescription.dispense_date = timezone.now()
        prescription.save()
        
        serializer = self.get_serializer(prescription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a prescription as completed"""
        prescription = self.get_object()
        
        # Check if prescription can be completed
        if prescription.status not in ['DISPENSED']:
            return Response(
                {"error": "Prescription cannot be completed. Current status: " + prescription.status},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prescription.status = 'COMPLETED'
        prescription.save()
        
        serializer = self.get_serializer(prescription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a prescription"""
        prescription = self.get_object()
        
        # Check if prescription can be cancelled
        if prescription.status not in ['CREATED', 'DISPENSED']:
            return Response(
                {"error": "Prescription cannot be cancelled. Current status: " + prescription.status},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prescription.status = 'CANCELLED'
        prescription.save()
        
        serializer = self.get_serializer(prescription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refill(self, request, pk=None):
        """Request a refill for a prescription"""
        prescription = self.get_object()
        
        # Check if prescription is refillable and has refills left
        if not prescription.is_refillable:
            return Response(
                {"error": "This prescription is not refillable"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if prescription.refill_count >= prescription.max_refills:
            return Response(
                {"error": "Maximum number of refills reached"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Increment refill count
        prescription.refill_count += 1
        prescription.save()
        
        serializer = self.get_serializer(prescription)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def patient_prescriptions(self, request):
        """Get all prescriptions for a specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response(
                {"error": "Patient ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prescriptions = Prescription.objects.filter(patient_id=patient_id)
        serializer = self.get_serializer(prescriptions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def doctor_prescriptions(self, request):
        """Get all prescriptions created by a specific doctor"""
        doctor_id = request.query_params.get('doctor_id')
        if not doctor_id:
            return Response(
                {"error": "Doctor ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prescriptions = Prescription.objects.filter(doctor_id=doctor_id)
        serializer = self.get_serializer(prescriptions, many=True)
        return Response(serializer.data)
