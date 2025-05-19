from django.db import models
from django.utils import timezone


class TimeSlot(models.Model):
    """Model for appointment time slots"""
    provider_id = models.CharField(max_length=50)  # ID of the doctor or other healthcare provider
    provider_type = models.CharField(
        max_length=20,
        choices=[
            ('DOCTOR', 'Doctor'),
            ('NURSE', 'Nurse'),
            ('LAB_TECHNICIAN', 'Laboratory Technician')
        ]
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'time_slots'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['provider_id']),
            models.Index(fields=['start_time']),
            models.Index(fields=['is_available'])
        ]
    
    def __str__(self):
        return f"{self.provider_type} {self.provider_id} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class AppointmentType(models.Model):
    """Model for types of appointments"""
    type_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.IntegerField()
    color_code = models.CharField(max_length=7, default="#3498db")  # Hex color code
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointment_types'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.duration_minutes} mins)"


class Appointment(models.Model):
    """Model for appointments"""
    appointment_id = models.CharField(max_length=20, unique=True)
    patient_id = models.CharField(max_length=50)
    provider_id = models.CharField(max_length=50)  # ID of the doctor or other provider
    provider_type = models.CharField(
        max_length=20,
        choices=[
            ('DOCTOR', 'Doctor'),
            ('NURSE', 'Nurse'),
            ('LAB_TECHNICIAN', 'Laboratory Technician')
        ]
    )
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.PROTECT)
    time_slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='appointment')
    status = models.CharField(
        max_length=20,
        choices=[
            ('SCHEDULED', 'Scheduled'),
            ('CONFIRMED', 'Confirmed'),
            ('CHECKED_IN', 'Checked In'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled'),
            ('NO_SHOW', 'No Show')
        ],
        default='SCHEDULED'
    )
    reason = models.TextField()
    notes = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=50)  # ID of the user who created the appointment
    cancelled_by = models.CharField(max_length=50, blank=True, null=True)  # ID of the user who cancelled
    cancellation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointments'
        ordering = ['-time_slot__start_time']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['provider_id']),
            models.Index(fields=['status'])
        ]
    
    def __str__(self):
        return f"Appointment {self.appointment_id} - {self.patient_id} with {self.provider_type} {self.provider_id}"
    
    def save(self, *args, **kwargs):
        # When an appointment is saved, mark the time slot as unavailable
        self.time_slot.is_available = False
        self.time_slot.save()
        super().save(*args, **kwargs)


class Reminder(models.Model):
    """Model for appointment reminders"""
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(
        max_length=20,
        choices=[
            ('EMAIL', 'Email'),
            ('SMS', 'SMS'),
            ('PUSH', 'Push Notification')
        ]
    )
    scheduled_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('SENT', 'Sent'),
            ('FAILED', 'Failed'),
            ('CANCELLED', 'Cancelled')
        ],
        default='PENDING'
    )
    sent_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reminders'
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"{self.reminder_type} reminder for appointment {self.appointment.appointment_id}"


class RecurringPattern(models.Model):
    """Model for recurring appointment patterns"""
    pattern_id = models.CharField(max_length=20, unique=True)
    provider_id = models.CharField(max_length=50)
    provider_type = models.CharField(
        max_length=20,
        choices=[
            ('DOCTOR', 'Doctor'),
            ('NURSE', 'Nurse'),
            ('LAB_TECHNICIAN', 'Laboratory Technician')
        ]
    )
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ('MONDAY', 'Monday'),
            ('TUESDAY', 'Tuesday'),
            ('WEDNESDAY', 'Wednesday'),
            ('THURSDAY', 'Thursday'),
            ('FRIDAY', 'Friday'),
            ('SATURDAY', 'Saturday'),
            ('SUNDAY', 'Sunday')
        ]
    )
    start_time = models.TimeField()  # Time of day
    end_time = models.TimeField()    # Time of day
    slot_duration_minutes = models.IntegerField()
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'recurring_patterns'
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.provider_type} {self.provider_id} - {self.day_of_week} {self.start_time.strftime('%H:%M')} to {self.end_time.strftime('%H:%M')}"
