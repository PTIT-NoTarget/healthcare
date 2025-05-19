from djongo import models
from django import forms
import json


class ListField(models.Field):
    """Custom field to store lists in MongoDB compatible with djongo 1.3.6"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return json.loads(value)
    
    def to_python(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return json.loads(value)
    
    def get_prep_value(self, value):
        if value is None:
            return []
        return json.dumps(value)


class VitalSign(models.Model):
    """Model to store vital signs for a medical record"""
    temperature = models.FloatField(null=True, blank=True)  # in Celsius
    heart_rate = models.IntegerField(null=True, blank=True)  # beats per minute
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)  # mmHg
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)  # mmHg
    respiratory_rate = models.IntegerField(null=True, blank=True)  # breaths per minute
    oxygen_saturation = models.IntegerField(null=True, blank=True)  # percentage
    height = models.FloatField(null=True, blank=True)  # in cm
    weight = models.FloatField(null=True, blank=True)  # in kg
    bmi = models.FloatField(null=True, blank=True)  # Body Mass Index
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True


class VitalSignForm(forms.ModelForm):
    class Meta:
        model = VitalSign
        fields = '__all__'


class Note(models.Model):
    """Model to store notes in a medical record"""
    note_type = models.CharField(max_length=50)  # progress, assessment, plan, etc.
    content = models.TextField()
    author = models.CharField(max_length=50)  # ID of the healthcare provider
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = '__all__'


class Attachment(models.Model):
    """Model to store attachments in a medical record"""
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)  # image, pdf, doc, etc.
    description = models.TextField(blank=True, null=True)
    file_url = models.URLField()  # URL to the file in storage
    uploaded_by = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = '__all__'


class MedicalRecord(models.Model):
    """Main model for storing medical records"""
    record_id = models.CharField(max_length=50, unique=True)
    patient_id = models.CharField(max_length=50)
    visit_date = models.DateTimeField()
    visit_type = models.CharField(
        max_length=50, 
        choices=[
            ('INITIAL', 'Initial Visit'),
            ('FOLLOW_UP', 'Follow-up Visit'),
            ('EMERGENCY', 'Emergency Visit'),
            ('ROUTINE', 'Routine Checkup'),
            ('SPECIALIST', 'Specialist Consultation'),
            ('SURGERY', 'Surgical Procedure'),
            ('TELEMEDICINE', 'Telemedicine Visit')
        ]
    )
    provider_id = models.CharField(max_length=50)  # Doctor/Healthcare provider ID
    chief_complaint = models.TextField()
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    
    # MongoDB specific fields using ArrayField for embedded documents
    vital_signs = models.ArrayField(
        model_container=VitalSign,
        model_form_class=VitalSignForm,
        blank=True, null=True
    )
    
    notes = models.ArrayField(
        model_container=Note,
        model_form_class=NoteForm,
        blank=True, null=True
    )
    
    attachments = models.ArrayField(
        model_container=Attachment,
        model_form_class=AttachmentForm,
        blank=True, null=True
    )
    
    # Additional fields
    allergies = ListField(default=list)
    medications = ListField(default=list)  # Current medications
    procedures = ListField(default=list)   # Procedures performed
    lab_results = ListField(default=list)  # References to lab reports
    
    # Status and metadata
    status = models.CharField(
        max_length=20,
        choices=[
            ('DRAFT', 'Draft'),
            ('ACTIVE', 'Active'),
            ('COMPLETED', 'Completed'),
            ('ARCHIVED', 'Archived')
        ],
        default='DRAFT'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medical_records'
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['record_id']),
            models.Index(fields=['visit_date']),
            models.Index(fields=['provider_id'])
        ]
    
    def __str__(self):
        return f"Record {self.record_id} for Patient {self.patient_id}"
