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


class MedicationItem(models.Model):
    medicine_id = models.CharField(max_length=50)
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)  # e.g., "3 times a day"
    duration = models.CharField(max_length=100)  # e.g., "7 days"
    instructions = models.TextField()

    class Meta:
        pass


class MedicationItemForm(forms.ModelForm):
    class Meta:
        model = MedicationItem
        fields = '__all__'


class Prescription(models.Model):
    prescription_id = models.CharField(max_length=50, unique=True)
    patient_id = models.CharField(max_length=50)
    doctor_id = models.CharField(max_length=50)
    date_prescribed = models.DateTimeField(auto_now_add=True)
    diagnosis = models.TextField()
    medications = models.ArrayField(
        model_container=MedicationItem,
        model_form_class=MedicationItemForm
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('CREATED', 'Created'),
            ('DISPENSED', 'Dispensed'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled')
        ],
        default='CREATED'
    )
    notes = models.TextField(blank=True, null=True)
    pharmacy_id = models.CharField(max_length=50, blank=True, null=True)  # Optional, if sent to a specific pharmacy
    dispense_date = models.DateTimeField(blank=True, null=True)
    is_refillable = models.BooleanField(default=False)
    refill_count = models.IntegerField(default=0)
    max_refills = models.IntegerField(default=0)
    
    # Additional metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions'
    
    def __str__(self):
        return f"Prescription {self.prescription_id} for Patient {self.patient_id}"
