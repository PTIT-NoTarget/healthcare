from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta, date
from django.utils import timezone
import uuid

from .models import TimeSlot, AppointmentType, Appointment, Reminder, RecurringPattern
from .serializers import (
    TimeSlotSerializer,
    AppointmentTypeSerializer,
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentUpdateSerializer,
    ReminderSerializer,
    RecurringPatternSerializer,
    ProviderScheduleSerializer,
    CancelAppointmentSerializer
)
from .permissions import (
    IsProvider,
    IsAppointmentProvider,
    IsAppointmentPatient,
    IsPatient,
    IsAdministrator,
    IsTimeSlotProvider,
    IsRecurringPatternProvider
)


class AppointmentTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for appointment types
    """
    queryset = AppointmentType.objects.all()
    serializer_class = AppointmentTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'duration_minutes']
    search_fields = ['name', 'type_id', 'description']
    ordering_fields = ['name', 'duration_minutes']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdministrator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Generate a unique type ID
        type_id = f"AT-{uuid.uuid4().hex[:6].upper()}"
        serializer.save(type_id=type_id)


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    API endpoint for time slots
    """
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['provider_id', 'provider_type', 'is_available']
    ordering_fields = ['start_time', 'end_time']
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = [IsProvider | IsAdministrator]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsTimeSlotProvider | IsAdministrator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # If provider is creating slots, use their ID
        if self.request.user.role in ['DOCTOR', 'NURSE', 'LAB_TECHNICIAN']:
            serializer.save(provider_id=str(self.request.user.id))
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available time slots for a specific period and provider"""
        provider_id = request.query_params.get('provider_id')
        provider_type = request.query_params.get('provider_type')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date:
            return Response(
                {"error": "Start date is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            
            # If end_date is not provided, default to 7 days after start_date
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            else:
                end_datetime = start_datetime + timedelta(days=7)
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            
            # Make start time at the beginning of the day
            start_datetime = start_datetime.replace(hour=0, minute=0, second=0)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start building the filter
        filter_kwargs = {
            'is_available': True,
            'start_time__gte': start_datetime,
            'end_time__lte': end_datetime
        }
        
        if provider_id:
            filter_kwargs['provider_id'] = provider_id
        
        if provider_type:
            filter_kwargs['provider_type'] = provider_type
        
        time_slots = TimeSlot.objects.filter(**filter_kwargs).order_by('start_time')
        serializer = self.get_serializer(time_slots, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate_from_pattern(self, request):
        """Generate time slots from a recurring pattern"""
        pattern_id = request.data.get('pattern_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not pattern_id:
            return Response(
                {"error": "Recurring pattern ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not start_date:
            return Response(
                {"error": "Start date is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pattern = RecurringPattern.objects.get(pattern_id=pattern_id)
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            if end_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                # Default to 4 weeks if end date is not provided
                end_date_obj = start_date_obj + timedelta(weeks=4)
        except RecurringPattern.DoesNotExist:
            return Response(
                {"error": "Recurring pattern not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Only the provider or an administrator can generate slots from their pattern
        if (pattern.provider_id != str(request.user.id) and 
            request.user.role not in [UserRole.ADMINISTRATOR]):
            return Response(
                {"error": "You don't have permission to generate slots from this pattern"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Define day of week mapping
        day_mapping = {
            'MONDAY': 0, 'TUESDAY': 1, 'WEDNESDAY': 2, 'THURSDAY': 3,
            'FRIDAY': 4, 'SATURDAY': 5, 'SUNDAY': 6
        }
        
        pattern_day = day_mapping[pattern.day_of_week]
        
        # Calculate dates for the specified day of week in the date range
        current_date = start_date_obj
        if current_date.weekday() != pattern_day:
            # Move to the next occurrence of the pattern's day of week
            days_ahead = (pattern_day - current_date.weekday()) % 7
            current_date = current_date + timedelta(days=days_ahead)
        
        # Generate slots for each applicable date
        created_slots = []
        while current_date <= end_date_obj:
            # Create datetime objects for the start and end times on this date
            start_datetime = datetime.combine(current_date, pattern.start_time)
            end_datetime = datetime.combine(current_date, pattern.end_time)
            
            # Generate slots at interval specified by slot_duration_minutes
            slot_start = start_datetime
            while slot_start < end_datetime:
                slot_end = slot_start + timedelta(minutes=pattern.slot_duration_minutes)
                
                # Don't create slots that extend beyond the pattern's end time
                if slot_end > end_datetime:
                    break
                
                # Check if a slot already exists for this provider and time
                existing_slot = TimeSlot.objects.filter(
                    provider_id=pattern.provider_id,
                    provider_type=pattern.provider_type,
                    start_time=slot_start,
                    end_time=slot_end
                ).exists()
                
                if not existing_slot:
                    time_slot = TimeSlot.objects.create(
                        provider_id=pattern.provider_id,
                        provider_type=pattern.provider_type,
                        start_time=slot_start,
                        end_time=slot_end,
                        is_available=True
                    )
                    created_slots.append(time_slot)
                
                # Move to the next slot start time
                slot_start = slot_end
            
            # Move to the next occurrence of the pattern's day of week
            current_date = current_date + timedelta(days=7)
        
        # Return the created slots
        serializer = self.get_serializer(created_slots, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for appointments
    """
    queryset = Appointment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient_id', 'provider_id', 'provider_type', 'status', 'appointment_type']
    search_fields = ['appointment_id', 'reason', 'notes']
    ordering_fields = ['time_slot__start_time', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AppointmentUpdateSerializer
        return AppointmentSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Both patients and providers can create appointments
            permission_classes = [IsPatient | IsProvider | IsAdministrator]
        elif self.action in ['update', 'partial_update']:
            # Only the provider of the appointment or admin can update it
            permission_classes = [IsAppointmentProvider | IsAdministrator]
        elif self.action == 'destroy':
            # Only administrators can delete appointments
            permission_classes = [IsAdministrator]
        elif self.action in ['list', 'retrieve']:
            # The provider and the patient can view the appointment
            permission_classes = [IsAppointmentProvider | IsAppointmentPatient | IsAdministrator]
        else:
            # Default to requiring authentication
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Generate a unique appointment ID
        appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
        
        # If patient is creating the appointment, use their ID
        if self.request.user.role == UserRole.PATIENT:
            serializer.save(
                appointment_id=appointment_id, 
                patient_id=str(self.request.user.id),
                created_by=str(self.request.user.id)
            )
        elif self.request.user.role in [UserRole.DOCTOR, UserRole.NURSE, UserRole.LAB_TECHNICIAN]:
            # If provider is creating the appointment, use their ID if it matches
            if 'provider_id' not in serializer.validated_data:
                serializer.save(
                    appointment_id=appointment_id,
                    provider_id=str(self.request.user.id),
                    provider_type=self.request.user.role,
                    created_by=str(self.request.user.id)
                )
            else:
                # Using the provided provider_id
                serializer.save(
                    appointment_id=appointment_id,
                    created_by=str(self.request.user.id)
                )
        else:
            # Administrator or other role
            serializer.save(
                appointment_id=appointment_id,
                created_by=str(self.request.user.id)
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment"""
        appointment = self.get_object()
        
        serializer = CancelAppointmentSerializer(data=request.data)
        if serializer.is_valid():
            # Check if the appointment can be cancelled
            if appointment.status in ['COMPLETED', 'CANCELLED', 'NO_SHOW']:
                return Response(
                    {"error": f"Cannot cancel appointment in {appointment.status} status"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update appointment status
            appointment.status = 'CANCELLED'
            appointment.cancellation_reason = serializer.validated_data['cancellation_reason']
            appointment.cancelled_by = serializer.validated_data['cancelled_by']
            appointment.save()
            
            # Mark the time slot as available again
            time_slot = appointment.time_slot
            time_slot.is_available = True
            time_slot.save()
            
            # Cancel any pending reminders
            Reminder.objects.filter(
                appointment=appointment, 
                status='PENDING'
            ).update(status='CANCELLED')
            
            # Return the updated appointment
            response_serializer = self.get_serializer(appointment)
            return Response(response_serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in a patient for their appointment"""
        appointment = self.get_object()
        
        # Check if the appointment can be checked in
        if appointment.status != 'CONFIRMED':
            return Response(
                {"error": f"Cannot check in appointment in {appointment.status} status"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update appointment status
        appointment.status = 'CHECKED_IN'
        appointment.save()
        
        # Return the updated appointment
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark an appointment as completed"""
        appointment = self.get_object()
        
        # Check if the appointment can be completed
        if appointment.status not in ['CHECKED_IN', 'IN_PROGRESS']:
            return Response(
                {"error": f"Cannot complete appointment in {appointment.status} status"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update appointment status
        appointment.status = 'COMPLETED'
        appointment.save()
        
        # Return the updated appointment
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def patient_appointments(self, request):
        """Get all appointments for a specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response(
                {"error": "Patient ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If the user is a patient, they can only access their own appointments
        if request.user.role == UserRole.PATIENT and str(request.user.id) != patient_id:
            return Response(
                {"error": "You can only access your own appointments"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointments = Appointment.objects.filter(patient_id=patient_id)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def provider_appointments(self, request):
        """Get all appointments for a specific provider"""
        provider_id = request.query_params.get('provider_id')
        if not provider_id:
            return Response(
                {"error": "Provider ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If the user is a provider, they can only access their own appointments
        if request.user.role in [UserRole.DOCTOR, UserRole.NURSE, UserRole.LAB_TECHNICIAN] and str(request.user.id) != provider_id:
            return Response(
                {"error": "You can only access your own appointments"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointments = Appointment.objects.filter(provider_id=provider_id)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def daily_schedule(self, request):
        """Get the daily schedule for a provider"""
        serializer = ProviderScheduleSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        provider_id = serializer.validated_data['provider_id']
        provider_type = serializer.validated_data['provider_type']
        date_param = serializer.validated_data['date']
        
        # If the user is a provider, they can only access their own schedule
        if request.user.role in [UserRole.DOCTOR, UserRole.NURSE, UserRole.LAB_TECHNICIAN] and str(request.user.id) != provider_id:
            return Response(
                {"error": "You can only access your own schedule"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all time slots for the provider on the specified date
        day_start = datetime.combine(date_param, datetime.min.time())
        day_end = datetime.combine(date_param, datetime.max.time())
        
        # Get all appointments for the provider on the specified date
        appointments = Appointment.objects.filter(
            provider_id=provider_id,
            provider_type=provider_type,
            time_slot__start_time__gte=day_start,
            time_slot__start_time__lte=day_end
        ).order_by('time_slot__start_time')
        
        # Get all available time slots for the provider on the specified date
        available_slots = TimeSlot.objects.filter(
            provider_id=provider_id,
            provider_type=provider_type,
            start_time__gte=day_start,
            start_time__lte=day_end,
            is_available=True
        ).order_by('start_time')
        
        # Return both appointments and available slots
        appointment_serializer = self.get_serializer(appointments, many=True)
        timeslot_serializer = TimeSlotSerializer(available_slots, many=True)
        
        return Response({
            'appointments': appointment_serializer.data,
            'available_slots': timeslot_serializer.data
        })


class ReminderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for appointment reminders
    """
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['appointment__appointment_id', 'reminder_type', 'status']
    ordering_fields = ['scheduled_time']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdministrator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def mark_sent(self, request, pk=None):
        """Mark a reminder as sent"""
        reminder = self.get_object()
        
        # Check if the reminder can be marked as sent
        if reminder.status != 'PENDING':
            return Response(
                {"error": f"Cannot mark reminder in {reminder.status} status as sent"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update reminder status
        reminder.status = 'SENT'
        reminder.sent_time = timezone.now()
        reminder.save()
        
        # Return the updated reminder
        serializer = self.get_serializer(reminder)
        return Response(serializer.data)


class RecurringPatternViewSet(viewsets.ModelViewSet):
    """
    API endpoint for recurring appointment patterns
    """
    queryset = RecurringPattern.objects.all()
    serializer_class = RecurringPatternSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['provider_id', 'provider_type', 'day_of_week', 'is_active']
    search_fields = ['pattern_id', 'provider_id']
    ordering_fields = ['day_of_week', 'start_time']
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsProvider | IsAdministrator]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsRecurringPatternProvider | IsAdministrator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Generate a unique pattern ID
        pattern_id = f"PATTERN-{uuid.uuid4().hex[:6].upper()}"
        
        # If provider is creating the pattern, use their ID
        if self.request.user.role in [UserRole.DOCTOR, UserRole.NURSE, UserRole.LAB_TECHNICIAN]:
            serializer.save(
                pattern_id=pattern_id,
                provider_id=str(self.request.user.id),
                provider_type=self.request.user.role
            )
        else:
            serializer.save(pattern_id=pattern_id)
