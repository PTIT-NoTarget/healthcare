from django.contrib import admin
from .models import PaymentTransaction, InsuranceClaimProcessing

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'service_type', 'originating_service_record_id', 'total_amount', 'amount_covered_by_insurance', 'amount_due_by_patient', 'payment_status', 'created_at')
    list_filter = ('service_type', 'payment_status', 'insurance_provider_id', 'created_at')
    search_fields = ('id', 'patient_id', 'originating_service_record_id')
    readonly_fields = ('created_at', 'updated_at', 'amount_covered_by_insurance', 'amount_due_by_patient')
    raw_id_fields = () # Use if you have ForeignKey to User or Patient profile for patient_id
    fieldsets = (
        ('Transaction Info', {
            'fields': (('patient_id', 'service_type'), 'originating_service_record_id', 'transaction_details')
        }),
        ('Financials', {
            'fields': ('total_amount', 'insurance_provider_id', 'amount_covered_by_insurance', 'amount_due_by_patient')
        }),
        ('Status', {
            'fields': ('payment_status',)
        }),
        ('Timestamps', {
            'fields': (('created_at', 'updated_at'),)
        }),
    )

@admin.register(InsuranceClaimProcessing)
class InsuranceClaimProcessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_transaction_id', 'insurance_provider_id', 'status', 'amount_claimed', 'amount_approved', 'submitted_at', 'last_updated_at')
    list_filter = ('status', 'insurance_provider_id', 'submitted_at')
    search_fields = ('id', 'payment_transaction__id', 'claim_identifier')
    readonly_fields = ('submitted_at', 'last_updated_at')
    raw_id_fields = ('payment_transaction',)

    def payment_transaction_id(self, obj):
        return obj.payment_transaction.id
    payment_transaction_id.short_description = 'Payment Transaction ID'
