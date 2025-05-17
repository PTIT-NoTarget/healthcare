from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'specialization', 'license_number', 'created_at', 'updated_at')
    search_fields = ('user_id', 'specialization', 'license_number')
    list_filter = ('specialization', 'created_at')
