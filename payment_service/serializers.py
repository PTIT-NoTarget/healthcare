from rest_framework import serializers
from .models import PaymentTransaction, InsuranceClaimProcessing

class PaymentTransactionSerializer(serializers.ModelSerializer):
    insurance_claim = serializers.PrimaryKeyRelatedField(read_only=True) # Or a nested serializer if preferred

    class Meta:
        model = PaymentTransaction
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'amount_due_by_patient', 'amount_covered_by_insurance', 'payment_status')

class PaymentTransactionCreateSerializer(serializers.Serializer):
    patient_id = serializers.CharField(max_length=100)
    service_type = serializers.ChoiceField(choices=PaymentTransaction.SERVICE_TYPE_CHOICES)
    originating_service_record_id = serializers.CharField(max_length=100)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    insurance_provider_id = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    transaction_details = serializers.JSONField(required=False, help_text="A list of billable items, e.g., [{'name': 'item1', 'quantity': 1, 'price': '10.00'}]")

class InsuranceClaimProcessingSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceClaimProcessing
        fields = '__all__'
        read_only_fields = ('submitted_at', 'last_updated_at')
