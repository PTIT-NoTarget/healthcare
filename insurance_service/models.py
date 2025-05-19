from django.db import models
from django.utils.translation import gettext_lazy as _

class PatientPolicy(models.Model):
    POLICY_STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('pending_verification', _('Pending Verification')),
        ('expired', _('Expired')),
    ]
    patient_id = models.CharField(max_length=100, db_index=True, help_text=_("Corresponds to the patient's ID in the User/Patient service"))
    insurance_provider_company_id = models.CharField(max_length=100, db_index=True, help_text=_("ID of the InsuranceProviderCompany from insurance_provider_service"))
    policy_number = models.CharField(max_length=100, help_text=_("Patient's policy number with the insurer"))
    policy_holder_name = models.CharField(max_length=255, blank=True, null=True, help_text=_("Name of the primary policy holder if different from patient"))
    effective_date = models.DateField()
    expiration_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=POLICY_STATUS_CHOICES, default='pending_verification')
    coverage_details = models.JSONField(default=dict, blank=True, help_text=_('e.g., {"deductible_total": 1000, "deductible_met": 200, "co_pay_percentage": 20, "out_of_pocket_max": 5000}'))
    verification_notes = models.TextField(blank=True, null=True, help_text=_("Notes from policy verification process"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Policy {self.policy_number} for Patient {self.patient_id} (Provider ID: {self.insurance_provider_company_id})"

    class Meta:
        db_table = "insurance_patient_policies"
        verbose_name = _("Patient Insurance Policy")
        verbose_name_plural = _("Patient Insurance Policies")
        unique_together = [('patient_id', 'insurance_provider_company_id', 'policy_number')]
        ordering = ['patient_id', '-effective_date']

class InsuranceClaim(models.Model):
    CLAIM_STATUS_CHOICES = [
        ('received', _('Received for Processing')),
        ('pending_submission_to_insurer', _('Pending Submission to External Insurer')),
        ('submitted_to_insurer', _('Submitted to External Insurer')),
        ('processing_by_insurer', _('Processing by External Insurer')),
        ('adjudicated_approved', _('Adjudicated - Approved by Insurer')),
        ('adjudicated_rejected', _('Adjudicated - Rejected by Insurer')),
        ('adjudicated_requires_info', _('Adjudicated - Requires More Information')),
        ('payment_processed_by_insurer', _('Payment Processed by Insurer')),
        ('closed_paid', _('Closed - Paid')),
        ('closed_rejected', _('Closed - Rejected')),
        ('error_processing', _('Error During Internal Processing')),
        ('error_submission', _('Error During Submission to Insurer')),
    ]

    policy = models.ForeignKey(PatientPolicy, on_delete=models.PROTECT, related_name='claims', help_text=_("The patient policy this claim is against"))
    payment_transaction_id = models.CharField(max_length=100, unique=True, db_index=True, help_text=_("ID of the PaymentTransaction from Payment Service"))
    claim_submission_date = models.DateTimeField(auto_now_add=True, help_text=_("Date this claim was recorded in our system"))
    service_date_start = models.DateField(help_text=_("Start date when the healthcare service was rendered"))
    service_date_end = models.DateField(blank=True, null=True, help_text=_("End date for services spanning multiple days"))
    billed_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text=_("Total amount billed for the service/items by the healthcare provider"))
    claimed_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text=_("Amount submitted to insurance for coverage (can be same as billed or adjusted)"))
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text=_("Amount approved by the insurer"))
    patient_responsibility_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text=_("Portion of the bill the patient is responsible for after insurance"))
    status = models.CharField(max_length=40, choices=CLAIM_STATUS_CHOICES, default='received')
    insurer_claim_reference_id = models.CharField(max_length=100, blank=True, null=True, db_index=True, help_text=_("Claim Reference ID from the external insurance company"))
    processing_notes = models.TextField(blank=True, null=True, help_text=_("Internal notes or notes from insurer during processing"))
    rejection_reason_code = models.CharField(max_length=50, blank=True, null=True, help_text=_("Standardized rejection code from insurer"))
    rejection_reason_description = models.TextField(blank=True, null=True, help_text=_("Detailed description of rejection reason"))
    claimed_items_details = models.JSONField(default=list, help_text=_("List of items/services claimed, e.g., from payment_transaction.transaction_details"))
    last_updated_at = models.DateTimeField(auto_now=True)
    submitted_to_insurer_at = models.DateTimeField(null=True, blank=True, help_text=_("Timestamp when the claim was actually sent to the external insurer"))
    adjudication_completed_at = models.DateTimeField(null=True, blank=True, help_text=_("Timestamp when the insurer completed adjudication"))

    def __str__(self):
        return f"Claim for Policy {self.policy.policy_number} (Payment Tx: {self.payment_transaction_id}) - Status: {self.status}"

    class Meta:
        db_table = "insurance_service_claims"
        verbose_name = _("Insurance Claim")
        verbose_name_plural = _("Insurance Claims")
        ordering = ['-claim_submission_date']
