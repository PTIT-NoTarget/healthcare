from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Laboratory, LabTest, LabOrder, LabOrderTest, TestResult
from .serializers import (
    LaboratorySerializer, 
    LabTestSerializer, 
    LabOrderSerializer, 
    LabOrderCreateSerializer,
    LabOrderTestSerializer,
    TestResultSerializer,
    TestResultCreateSerializer
)
from .permissions import (
    IsLabTechnician, 
    IsDoctor, 
    IsTestOrderDoctor, 
    IsTestPatient, 
    IsAdministrator,
    IsMedicalStaff
)
import uuid
from django.utils import timezone


class LaboratoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for laboratories
    """
    queryset = Laboratory.objects.all()
    serializer_class = LaboratorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'is_active']
    search_fields = ['name', 'lab_id', 'department', 'location']
    ordering_fields = ['name', 'department']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdministrator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Generate a unique lab ID
        lab_id = f"LAB-{uuid.uuid4().hex[:6].upper()}"
        serializer.save(lab_id=lab_id)


class LabTestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for laboratory tests
    """
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'sample_type', 'is_active']
    search_fields = ['name', 'test_id', 'description', 'category']
    ordering_fields = ['name', 'category', 'price']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdministrator | IsLabTechnician]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Generate a unique test ID
        test_id = f"TEST-{uuid.uuid4().hex[:6].upper()}"
        serializer.save(test_id=test_id)


class LabOrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for laboratory orders
    """
    queryset = LabOrder.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient_id', 'doctor_id', 'laboratory', 'status', 'priority']
    search_fields = ['order_id', 'patient_id', 'doctor_id', 'notes']
    ordering_fields = ['ordered_date', 'scheduled_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LabOrderCreateSerializer
        return LabOrderSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Only doctors can create lab orders
            permission_classes = [IsDoctor]
        elif self.action in ['update', 'partial_update']:
            # Only doctors who created the order, lab techs, or admins can update it
            permission_classes = [IsTestOrderDoctor | IsLabTechnician | IsAdministrator]
        elif self.action == 'destroy':
            # Only administrators can delete orders
            permission_classes = [IsAdministrator]
        elif self.action in ['list', 'retrieve']:
            # Medical staff and the patient can view
            permission_classes = [IsMedicalStaff | IsTestPatient]
        else:
            # Default to requiring authentication
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Generate a unique order ID
        order_id = f"LO-{uuid.uuid4().hex[:8].upper()}"
        # Set the doctor_id from the current user
        serializer.save(order_id=order_id, doctor_id=str(self.request.user.id), status='ORDERED')
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update the status of a lab order"""
        lab_order = self.get_object()
        
        if 'status' not in request.data:
            return Response(
                {"error": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_status = request.data['status']
        valid_statuses = [choice[0] for choice in LabOrder._meta.get_field('status').choices]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Valid options are: {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Additional validation based on current status and user role
        current_status = lab_order.status
        user_role = request.user.role
        
        # Define valid status transitions
        if user_role == UserRole.LAB_TECHNICIAN:
            if current_status == 'ORDERED' and new_status not in ['SCHEDULED', 'CANCELLED']:
                return Response(
                    {"error": f"Cannot transition from {current_status} to {new_status} with your role"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif current_status == 'SCHEDULED' and new_status not in ['SAMPLE_COLLECTED', 'CANCELLED']:
                return Response(
                    {"error": f"Cannot transition from {current_status} to {new_status} with your role"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif current_status == 'SAMPLE_COLLECTED' and new_status not in ['IN_PROGRESS', 'CANCELLED']:
                return Response(
                    {"error": f"Cannot transition from {current_status} to {new_status} with your role"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif current_status == 'IN_PROGRESS' and new_status not in ['COMPLETED', 'CANCELLED']:
                return Response(
                    {"error": f"Cannot transition from {current_status} to {new_status} with your role"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif current_status == 'COMPLETED' and new_status not in ['REPORTED']:
                return Response(
                    {"error": f"Cannot transition from {current_status} to {new_status} with your role"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif user_role == UserRole.DOCTOR:
            if current_status != 'ORDERED' and new_status == 'CANCELLED':
                return Response(
                    {"error": f"Cannot cancel order in {current_status} status"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif current_status != 'ORDERED' and new_status != 'CANCELLED':
                return Response(
                    {"error": f"Doctors can only cancel orders, not update status to {new_status}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Update all related tests to a terminal status if necessary
        if new_status in ['CANCELLED']:
            lab_order.tests.all().update(status='CANCELLED')
        
        lab_order.status = new_status
        
        # Update scheduled date if we're scheduling
        if new_status == 'SCHEDULED' and 'scheduled_date' in request.data:
            lab_order.scheduled_date = request.data['scheduled_date']
        
        lab_order.save()
        
        serializer = self.get_serializer(lab_order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def patient_orders(self, request):
        """Get all lab orders for a specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response(
                {"error": "Patient ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If the user is a patient, they can only access their own orders
        if request.user.role == UserRole.PATIENT and str(request.user.id) != patient_id:
            return Response(
                {"error": "You can only access your own lab orders"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        orders = LabOrder.objects.filter(patient_id=patient_id)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def doctor_orders(self, request):
        """Get all lab orders created by a specific doctor"""
        doctor_id = request.query_params.get('doctor_id')
        if not doctor_id:
            return Response(
                {"error": "Doctor ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orders = LabOrder.objects.filter(doctor_id=doctor_id)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def laboratory_orders(self, request):
        """Get all lab orders for a specific laboratory"""
        laboratory_id = request.query_params.get('laboratory_id')
        if not laboratory_id:
            return Response(
                {"error": "Laboratory ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orders = LabOrder.objects.filter(laboratory_id=laboratory_id)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


class TestResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint for test results
    """
    queryset = TestResult.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['abnormal_flag', 'order_test__order__patient_id', 'order_test__order__doctor_id']
    search_fields = ['result_id', 'comments', 'order_test__order__order_id']
    ordering_fields = ['performed_date', 'verified_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TestResultCreateSerializer
        return TestResultSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            # Only lab technicians can create or update results
            permission_classes = [IsLabTechnician]
        elif self.action == 'destroy':
            # Only administrators can delete results
            permission_classes = [IsAdministrator]
        elif self.action in ['list', 'retrieve']:
            # Medical staff and the patient can view
            permission_classes = [IsMedicalStaff | IsTestPatient]
        else:
            # Default to requiring authentication
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Generate a unique result ID
        result_id = f"RES-{uuid.uuid4().hex[:8].upper()}"
        # Set the performed_by from the current user
        serializer.save(
            result_id=result_id, 
            performed_by=str(self.request.user.id),
            performed_date=timezone.now()
        )
        
        # Update the corresponding order test status
        order_test = serializer.validated_data['order_test']
        order_test.status = 'REPORTED'
        order_test.save()
        
        # Check if all tests in the order are reported, then update the order status
        order = order_test.order
        all_tests_reported = all(test.status == 'REPORTED' for test in order.tests.all())
        if all_tests_reported:
            order.status = 'REPORTED'
            order.save()
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a test result by another lab technician"""
        test_result = self.get_object()
        
        # Check if the result is already verified
        if test_result.verified_by:
            return Response(
                {"error": "This result has already been verified"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # A technician can't verify their own results
        if test_result.performed_by == str(request.user.id):
            return Response(
                {"error": "You cannot verify your own test results"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        test_result.verified_by = str(request.user.id)
        test_result.verified_date = timezone.now()
        test_result.save()
        
        serializer = self.get_serializer(test_result)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def patient_results(self, request):
        """Get all test results for a specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response(
                {"error": "Patient ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If the user is a patient, they can only access their own results
        if request.user.role == UserRole.PATIENT and str(request.user.id) != patient_id:
            return Response(
                {"error": "You can only access your own test results"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        results = TestResult.objects.filter(order_test__order__patient_id=patient_id)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
