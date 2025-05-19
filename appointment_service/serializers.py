from rest_framework import serializers
from .models import TimeSlot, AppointmentType, Appointment, Reminder, RecurringPattern


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AppointmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentType
        fields = '__all__'
        read_only_fields = ['type_id', 'created_at', 'updated_at']


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ReminderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['appointment', 'reminder_type', 'scheduled_time']


class AppointmentSerializer(serializers.ModelSerializer):
    time_slot_details = TimeSlotSerializer(source='time_slot', read_only=True)
    appointment_type_details = AppointmentTypeSerializer(source='appointment_type', read_only=True)
    reminders = ReminderSerializer(many=True, read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['appointment_id', 'created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    reminders = ReminderCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Appointment
        fields = [
            'patient_id', 'provider_id', 'provider_type', 'appointment_type', 
            'time_slot', 'reason', 'notes', 'reminders'
        ]
        read_only_fields = ['appointment_id']
    
    def create(self, validated_data):
        # Extract reminders data if present
        reminders_data = validated_data.pop('reminders', [])
        
        # Create the appointment
        appointment = Appointment.objects.create(**validated_data)
        
        # Create reminders if provided
        for reminder_data in reminders_data:
            Reminder.objects.create(appointment=appointment, **reminder_data)
        
        return appointment


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['time_slot', 'status', 'notes']


class RecurringPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringPattern
        fields = '__all__'
        read_only_fields = ['pattern_id', 'created_at', 'updated_at']
        

class ProviderScheduleSerializer(serializers.Serializer):
    provider_id = serializers.CharField(max_length=50)
    provider_type = serializers.ChoiceField(choices=[
        ('DOCTOR', 'Doctor'),
        ('NURSE', 'Nurse'),
        ('LAB_TECHNICIAN', 'Laboratory Technician')
    ])
    date = serializers.DateField()


class CancelAppointmentSerializer(serializers.Serializer):
    cancellation_reason = serializers.CharField(allow_blank=False)
    cancelled_by = serializers.CharField(max_length=50) 