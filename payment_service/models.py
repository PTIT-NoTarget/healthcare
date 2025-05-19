from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class PaymentTransaction(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('pharmacy', _('Pharmacy Order')),
        ('hospital_fee', _('Hospital Fee')),
        ('consultation', _('Doctor Consultation')),
        # Add other service types as needed
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing_insurance', _('Processing Insurance')),
        ('awaiting_patient_payment', _('Awaiting Patient Payment')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('canceled', _('Canceled')),
    ]

    patient_id = models.CharField(max_length=100, help_text=_("ID of the patient from the User service"))
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    originating_service_record_id = models.CharField(max_length=100, help_text=_("ID of the record in the originating service, e.g., Order ID, Appointment ID"))

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    insurance_provider_id = models.CharField(max_length=100, blank=True, null=True, help_text=_("ID of the insurance provider, if any"))
    amount_covered_by_insurance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_due_by_patient = models.DecimalField(max_digits=10, decimal_places=2)

    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_details = models.JSONField(default=dict, blank=True, null=True, help_text=_("Details of billable items")) # Stores list of items, prices, etc.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.service_type} ({self.originating_service_record_id}) - Patient {self.patient_id} - Status: {self.payment_status}"

    class Meta:
        db_table = "payment_transactions"
        ordering = ["-created_at"]

class InsuranceClaimProcessing(models.Model):
    CLAIM_STATUS_CHOICES = [
        ('submitted', _('Submitted to Insurer')),
        ('processing', _('Insurer Processing')),
        ('approved', _('Approved by Insurer')),
        ('rejected', _('Rejected by Insurer')),
        ('requires_information', _('Requires More Information')),
        ('paid', _('Paid by Insurer')),
    ]
    payment_transaction = models.OneToOneField(PaymentTransaction, on_delete=models.CASCADE, related_name='insurance_claim')
    insurance_provider_id = models.CharField(max_length=100, help_text=_("ID of the insurance provider"))
    claim_identifier = models.CharField(max_length=255, blank=True, null=True, help_text=_("Identifier for the claim given by the insurer"))
    status = models.CharField(max_length=30, choices=CLAIM_STATUS_CHOICES, default='submitted')
    amount_claimed = models.DecimalField(max_digits=10, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Claim for Transaction {self.payment_transaction.id} - Provider {self.insurance_provider_id} - Status: {self.status}"

    class Meta:
        db_table = "insurance_claims_processing"
        ordering = ["-submitted_at"]

