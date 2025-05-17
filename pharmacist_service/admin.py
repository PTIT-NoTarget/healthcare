from django.contrib import admin
from .models import Pharmacist


@admin.register(Pharmacist)
class PharmacistAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'specialization', 'pharmacy_name')
    search_fields = ('user__username', 'user__email', 'license_number', 'pharmacy_name')
    list_filter = ('specialization', 'pharmacy_name') 