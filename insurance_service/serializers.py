from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import PatientPolicy, InsuranceClaim

class PatientPolicySerializer(serializers.ModelSerializer):
    # Denormalized field for easier display, assuming insurance_provider_company_id is known
    # In a real scenario, frontend might fetch company name from insurance_provider_service
    # insurance_provider_company_name = serializers.CharField(read_only=True) # Example if denormalizing

    class Meta:
        model = PatientPolicy
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class PatientPolicyCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientPolicy
        fields = [
            'patient_id',
            'insurance_provider_company_id',
            'policy_number',
            'policy_holder_name',
            'effective_date',
            'expiration_date',
            'status',
            'coverage_details',
            'verification_notes'
        ]

    def validate(self, data):
        effective_date = data.get('effective_date')
        expiration_date = data.get('expiration_date')
        if effective_date and expiration_date and expiration_date < effective_date:
            raise serializers.ValidationError(_("Expiration date cannot be before effective date."))
        return data

    # Example validation if you had direct access or an internal API to check insurance_provider_company_id
    # def validate_insurance_provider_company_id(self, value):
    #     try:
    #         # response = requests.get(f'http://insurance-provider-service/api/companies/{value}/')
    #         # response.raise_for_status()
    #         # if not response.json().get('is_active'):
    #         #     raise serializers.ValidationError(_("Insurance provider company is not active."))
    #         pass # Placeholder for actual validation
    #     except Exception as e:
    #         raise serializers.ValidationError(_(f"Invalid insurance_provider_company_id: {e}"))
    #     return value

class InsuranceClaimSerializer(serializers.ModelSerializer):
    # Nested policy details for read-only purposes
    policy = PatientPolicySerializer(read_only=True)
    # Denormalized patient_id for easier filtering/display if needed, though already in policy
    patient_id = serializers.CharField(source='policy.patient_id', read_only=True)

    class Meta:
        model = InsuranceClaim
        fields = '__all__'
        read_only_fields = (
            'claim_submission_date',
            'last_updated_at',
            'submitted_to_insurer_at',
            'adjudication_completed_at'
        )

class InsuranceClaimCreateInternalSerializer(serializers.ModelSerializer):
    """Serializer for payment_service to initiate a claim in insurance_service."""
    class Meta:
        model = InsuranceClaim
        fields = [
            'policy',  # Expects PatientPolicy.id
            'payment_transaction_id',
            'service_date_start',
            'service_date_end',
            'billed_amount',
            'claimed_amount',
            'claimed_items_details'
        ]

    def validate_policy(self, value):
        if value.status != 'active':
            raise serializers.ValidationError(_(f"Claims can only be filed against active policies. Current status: {value.status}."))
        if value.expiration_date and value.expiration_date < timezone.now().date():
            raise serializers.ValidationError(_(f"Cannot file a claim against an expired policy. Expired on: {value.expiration_date}."))
        return value

    def validate(self, data):
        if data.get('service_date_end') and data.get('service_date_end') < data.get('service_date_start'):
            raise serializers.ValidationError("Service end date cannot be before service start date.")
        return data

class InsuranceClaimUpdateAdjudicationInternalSerializer(serializers.ModelSerializer):
    """Serializer for updating claim status and financial outcomes after insurer adjudication."""
    class Meta:
        model = InsuranceClaim
        fields = [
            'approved_amount',
            'patient_responsibility_amount',
            'status',
            'insurer_claim_reference_id',
            'processing_notes',
            'rejection_reason_code',
            'rejection_reason_description',
            'submitted_to_insurer_at', # Can be set when async task confirms submission
            'adjudication_completed_at' # Set when insurer provides final adjudication
        ]
        extra_kwargs = {
            field: {'required': False, 'allow_null': True} for field in fields
        }

    def validate_status(self, value):
        # Ensure the status being set is a valid choice from the model
        valid_statuses = [choice[0] for choice in InsuranceClaim.CLAIM_STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(_(f"Invalid claim status: '{value}'."))
        return value

    def validate(self, data):
        # Basic validation for financial amounts if provided
        approved_amount = data.get('approved_amount')
        patient_responsibility = data.get('patient_responsibility_amount')
        billed_amount = self.instance.billed_amount if self.instance else None # Get billed amount from existing instance

        if approved_amount is not None and approved_amount < 0:
            raise serializers.ValidationError({'approved_amount': _("Approved amount cannot be negative.")})
        if patient_responsibility is not None and patient_responsibility < 0:
            raise serializers.ValidationError({'patient_responsibility_amount': _("Patient responsibility amount cannot be negative.")})

        # If both are provided, they should ideally reconcile with the billed amount, but this logic can be complex
        # and might depend on the claim status (e.g., not relevant for a pending status).
        # if billed_amount and approved_amount is not None and patient_responsibility is not None:
        #     if approved_amount + patient_responsibility != billed_amount: # This might be too strict due to adjustments
        #         pass # Consider how to handle discrepancies or if this validation is needed here
        return data

