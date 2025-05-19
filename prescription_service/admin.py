from django.contrib import admin
from .models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('prescription_id', 'patient_id', 'doctor_id', 'date_prescribed', 'status')
    list_filter = ('status', 'is_refillable', 'date_prescribed')
    search_fields = ('prescription_id', 'patient_id', 'doctor_id', 'diagnosis')
    readonly_fields = ('prescription_id', 'created_at', 'updated_at')
