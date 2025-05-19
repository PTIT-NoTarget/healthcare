from django.contrib import admin
from .models import MedicalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('record_id', 'patient_id', 'provider_id', 'visit_date', 'visit_type', 'status')
    list_filter = ('status', 'visit_type', 'visit_date')
    search_fields = ('record_id', 'patient_id', 'provider_id', 'diagnosis', 'chief_complaint')
    readonly_fields = ('record_id', 'created_at', 'updated_at')
