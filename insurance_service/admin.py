from django.contrib import admin
from .models import PatientPolicy, InsuranceClaim

@admin.register(PatientPolicy)
class PatientPolicyAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'insurance_provider_company_id', 'policy_number', 'status', 'effective_date', 'expiration_date', 'updated_at')
    list_filter = ('status', 'insurance_provider_company_id', 'effective_date', 'expiration_date', 'updated_at')
    search_fields = ('patient_id', 'policy_number', 'insurance_provider_company_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('patient_id', 'insurance_provider_company_id', 'policy_number', 'policy_holder_name')
        }),
        ('Policy Details', {
            'fields': ('effective_date', 'expiration_date', 'status', 'coverage_details')
        }),
        ('Verification & Timestamps', {
            'fields': ('verification_notes', ('created_at', 'updated_at'))
        }),
    )

@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'policy_id', 'payment_transaction_id', 'status', 'insurer_claim_reference_id',
        'billed_amount', 'claimed_amount', 'approved_amount', 'patient_responsibility_amount',
        'service_date_start', 'claim_submission_date', 'adjudication_completed_at', 'last_updated_at'
    )
    list_filter = ('status', 'policy__insurance_provider_company_id', 'service_date_start', 'claim_submission_date', 'adjudication_completed_at')
    search_fields = ('policy__policy_number', 'payment_transaction_id', 'insurer_claim_reference_id', 'policy__patient_id')
    readonly_fields = ('claim_submission_date', 'last_updated_at', 'submitted_to_insurer_at', 'adjudication_completed_at')
    fieldsets = (
        (None, {
            'fields': ('policy', 'payment_transaction_id', 'insurer_claim_reference_id')
        }),
        ('Claim Details', {
            'fields': ('billed_amount', 'claimed_amount', 'approved_amount', 'patient_responsibility_amount')
        }),
        ('Service Dates & Status', {
            'fields': ('service_date_start', 'service_date_end', 'status')
        }),
        ('Timestamps', {
            'fields': ('claim_submission_date', 'submitted_to_insurer_at', 'adjudication_completed_at', 'last_updated_at')
        }),
    )
