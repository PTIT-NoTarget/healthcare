from django.contrib import admin
from .models import Medicine


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_name', 'manufacturer', 'dosage_form', 
                   'strength', 'ndc_code', 'price', 'requires_prescription')
    search_fields = ('name', 'generic_name', 'ndc_code', 'manufacturer')
    list_filter = ('dosage_form', 'requires_prescription', 'is_controlled_substance') 