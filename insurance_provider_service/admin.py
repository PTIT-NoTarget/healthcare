from django.contrib import admin
from .models import InsuranceProvider


@admin.register(InsuranceProvider)
class InsuranceProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'provider_id_number', 'user_id', 'contact_email', 'contact_phone')
    search_fields = ('company_name', 'provider_id_number', 'contact_email')
    list_filter = ('company_name', 'is_active',)

