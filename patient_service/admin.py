from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'date_of_birth', 'blood_type', 'emergency_contact', 'created_at')
    search_fields = ('user_id', 'blood_type', 'emergency_contact')
    list_filter = ('blood_type', 'created_at')
