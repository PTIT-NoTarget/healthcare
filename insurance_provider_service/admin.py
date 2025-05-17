from django.contrib import admin
from .models import InsuranceProvider


@admin.register(InsuranceProvider)
class InsuranceProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'provider_id', 'contact_email', 'contact_phone')
    search_fields = ('user__username', 'company_name', 'provider_id', 'contact_email')
    list_filter = ('company_name',) 