from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Prescription
from .serializers import PrescriptionSerializer
import uuid
from django.utils import timezone
import requests


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient_id', 'doctor_id', 'pharmacy_id', 'is_refillable']
    search_fields = ['prescription_id', 'diagnosis', 'notes']
    ordering_fields = ['date_prescribed', 'created_at', 'updated_at']
    lookup_field = 'prescription_id'
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        # Generate a unique prescription ID
        prescription_id = f"PRE-{uuid.uuid4().hex[:8].upper()}"
        
        # Get doctor_id from request data or user ID if authenticated
        doctor_id = self.request.data.get('doctor_id')
        if not doctor_id and self.request.user.is_authenticated:
            doctor_id = str(self.request.user.id)
            
        serializer.save(prescription_id=prescription_id, doctor_id=doctor_id)
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to add medicine, doctor and patient details"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_object(self):
        """
        Returns the object the view is displaying.
        Override to support lookup by prescription_id.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Lookup by prescription_id instead of pk
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        
        obj = get_object_or_404(queryset, **filter_kwargs)
        return obj
    
    def list(self, request, *args, **kwargs):
        """Override list to add medicine, doctor and patient details"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def dispense(self, request, pk=None):
        """Mark a prescription as dispensed by a pharmacy"""
        prescription = self.get_object()
        
        # Update prescription with pharmacy info
        prescription.pharmacy_id = request.data.get('pharmacy_id')
        prescription.dispense_date = timezone.now()
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
