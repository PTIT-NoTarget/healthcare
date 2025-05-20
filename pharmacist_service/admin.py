from django.contrib import admin
from .models import Pharmacist


@admin.register(Pharmacist)
class PharmacistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'pharmacist_id', 'license_number', 'specialization', 'pharmacy_id')
    search_fields = ('user_id', 'pharmacist_id', 'license_number', 'pharmacy_id')
    list_filter = ('specialization', 'is_active')