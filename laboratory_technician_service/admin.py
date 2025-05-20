from django.contrib import admin
from .models import LaboratoryTechnician


@admin.register(LaboratoryTechnician)
class LaboratoryTechnicianAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'employee_id', 'specialization', 'laboratory_name', 'certification')
    search_fields = ('user_id', 'employee_id', 'laboratory_name')
    list_filter = ('specialization', 'laboratory_name', 'certification') 