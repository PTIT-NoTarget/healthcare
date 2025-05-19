from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import requests # For calling other services if needed
from django.utils import timezone # For service_date default

from .models import PaymentTransaction, InsuranceClaimProcessing
from .serializers import (
    PaymentTransactionSerializer,
    PaymentTransactionCreateSerializer,
    InsuranceClaimProcessingSerializer
)

class IsInternalServiceOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        # Replace with actual service-to-service auth (e.g., token check)
        # return request.headers.get('X-Internal-Service-Token') == 'YOUR_SECURE_SHARED_TOKEN'
        return False # Default deny for placeholder

class PaymentTransactionViewSet(viewsets.ModelViewSet):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient_id', 'service_type', 'insurance_provider_id', 'payment_status']
    search_fields = ['originating_service_record_id', 'patient_id']
    ordering_fields = ['created_at', 'total_amount']

    def get_permissions(self):
        if self.action == 'create_transaction_internal':
            return [IsInternalServiceOrAdmin()]
        if self.action == 'update_insurance_outcome_internal': # New internal action
            return [IsInternalServiceOrAdmin()]
        if self.action in ['list', 'retrieve'] and self.request.user.is_authenticated and not self.request.user.is_staff:
            return [permissions.IsAuthenticated()]
        if self.action == 'record_patient_payment' and self.request.user.is_authenticated:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and not user.is_staff and self.action in ['list', 'retrieve']:
            return PaymentTransaction.objects.filter(patient_id=str(user.id))
        return super().get_queryset()

    @action(detail=False, methods=['post'], serializer_class=PaymentTransactionCreateSerializer, url_path='internal/initiate')
    def create_transaction_internal(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            total_amount = validated_data['total_amount']
            insurance_provider_id = validated_data.get('insurance_provider_id')
            patient_id = validated_data['patient_id']

            transaction = PaymentTransaction.objects.create(
                patient_id=patient_id,
                service_type=validated_data['service_type'],
                originating_service_record_id=validated_data['originating_service_record_id'],
                total_amount=total_amount,
                insurance_provider_id=insurance_provider_id,
                transaction_details=validated_data.get('transaction_details', {}),
                amount_covered_by_insurance=0.00,
                amount_due_by_patient=total_amount,
                payment_status='pending'
            )

            if insurance_provider_id:
                transaction.payment_status = 'processing_insurance'
                # Create the InsuranceClaimProcessing record first
                claim_processing_record = InsuranceClaimProcessing.objects.create(
                    payment_transaction=transaction,
                    insurance_provider_id=insurance_provider_id,
                    amount_claimed=total_amount,
                    status='submitted' # Initial status in payment_service
                )
                transaction.save() # Save transaction status change

                # Now, call insurance_provider_service to initiate the actual claim
                try:
                    policy_id = insurance_provider_id
                    if not policy_id: # Should have been caught by `if insurance_provider_id:` but double check
                        raise ValueError("Policy ID is required to initiate an insurance claim.")

                    insurance_service_url = 'http://insurance-provider-service/api/insurance/claims/internal/initiate-claim/'
                    claim_payload = {
                        'policy': policy_id, # This should be the PatientPolicy ID
                        'payment_transaction_id': str(transaction.id),
                        'service_date': timezone.now().date().isoformat(), # Or from transaction_details if available
                        'billed_amount': float(total_amount),
                        'claimed_amount': float(total_amount), # Initially claim full amount
                        'claimed_items_details': validated_data.get('transaction_details', [])
                    }
                    print(f"TODO: Call insurance_provider_service ({insurance_service_url}) with payload: {claim_payload}")

                except requests.exceptions.RequestException as e:
                    print(f"Error calling insurance_provider_service for Tx {transaction.id}: {e}")
                    transaction.payment_status = 'failed' # Mark as failed if initial call fails
                    claim_processing_record.status = 'error_submission' # Custom status
                    claim_processing_record.notes = str(e)
                    claim_processing_record.save()
                except ValueError as ve:
                    print(f"ValueError during claim initiation for Tx {transaction.id}: {ve}")
                    transaction.payment_status = 'failed'
                    claim_processing_record.status = 'error_submission'
                    claim_processing_record.notes = str(ve)
                    claim_processing_record.save()
            else:
                transaction.payment_status = 'awaiting_patient_payment'

            transaction.save() # Ensure final state is saved
            return Response(PaymentTransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='internal/update-insurance-outcome')
    def update_insurance_outcome_internal(self, request, pk=None):
        """
        Internal endpoint for insurance_provider_service to callback/update payment_service
        about the outcome of an insurance claim.
        """
        transaction = self.get_object()
        if not hasattr(transaction, 'insurance_claim'):
            return Response({"error": "Transaction has no associated insurance claim processing record."}, status=status.HTTP_400_BAD_REQUEST)

        claim_processing_record = transaction.insurance_claim

        # Data from insurance_provider_service callback
        insurance_status = request.data.get('status') # e.g., 'approved', 'rejected', 'paid' from InsuranceClaim.status
        approved_amount_str = request.data.get('approved_amount')
        patient_responsibility_amount_str = request.data.get('patient_responsibility_amount')
        insurer_claim_id = request.data.get('insurer_claim_id') # Actual ID from external insurer
        rejection_reason = request.data.get('rejection_reason')
        processing_notes = request.data.get('processing_notes')

        try:
            approved_amount = float(approved_amount_str) if approved_amount_str is not None else 0.00
            patient_responsibility_amount = float(patient_responsibility_amount_str) if patient_responsibility_amount_str is not None else transaction.total_amount - approved_amount
        except (ValueError, TypeError):
            return Response({"error": "Invalid amount format in callback data."}, status=status.HTTP_400_BAD_REQUEST)

        # Update InsuranceClaimProcessing in payment_service
        claim_processing_record.status = insurance_status
        claim_processing_record.amount_approved = approved_amount
        claim_processing_record.rejection_reason = rejection_reason
        claim_processing_record.notes = processing_notes if processing_notes else claim_processing_record.notes
        claim_processing_record.save()

        # Update PaymentTransaction based on insurance outcome
        transaction.amount_covered_by_insurance = approved_amount
        transaction.amount_due_by_patient = patient_responsibility_amount

        if insurance_status == 'approved' or insurance_status == 'paid':
            if transaction.amount_due_by_patient <= 0:
                transaction.payment_status = 'completed'
            else:
                transaction.payment_status = 'awaiting_patient_payment'
        elif insurance_status == 'rejected':
            transaction.payment_status = 'awaiting_patient_payment' # Patient pays full amount
            transaction.amount_due_by_patient = transaction.total_amount # Ensure patient pays full on rejection
            transaction.amount_covered_by_insurance = 0.00
        elif insurance_status == 'error_processing' or insurance_status == 'requires_more_info':
            transaction.payment_status = 'processing_insurance' # Or a specific error/pending info status

        transaction.save()
        return Response(PaymentTransactionSerializer(transaction).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='simulate-insurance-update')
    def simulate_update_insurance_claim(self, request, pk=None):
        transaction = self.get_object()
        if not hasattr(transaction, 'insurance_claim'):
            return Response({"error": "No insurance claim associated."}, status=status.HTTP_400_BAD_REQUEST)

        claim = transaction.insurance_claim
        simulated_amount_approved = request.data.get('amount_approved', transaction.total_amount * 0.80)
        simulated_claim_status = request.data.get('claim_status', 'approved')
        patient_resp_amount = request.data.get('patient_responsibility_amount', float(transaction.total_amount) - float(simulated_amount_approved))

        try:
            simulated_amount_approved = float(simulated_amount_approved)
            patient_resp_amount = float(patient_resp_amount)
        except ValueError:
            return Response({"error": "Invalid amount_approved format."}, status=status.HTTP_400_BAD_REQUEST)

        callback_payload = {
            'status': simulated_claim_status,
            'approved_amount': simulated_amount_approved,
            'patient_responsibility_amount': patient_resp_amount,
            'insurer_claim_id': 'SIMULATED_INSURER_ID_123',
            'rejection_reason': request.data.get('rejection_reason')
        }
        return self.update_insurance_outcome_internal(request=type('Request', (), {'data': callback_payload})(), pk=pk)

    @action(detail=True, methods=['post'], url_path='record-patient-payment')
    def record_patient_payment(self, request, pk=None):
        transaction = self.get_object()
        if not request.user.is_staff and str(request.user.id) != transaction.patient_id:
            return Response({"error": "Not authorized for this transaction."}, status=status.HTTP_403_FORBIDDEN)

        if transaction.payment_status not in ['awaiting_patient_payment', 'pending', 'processing_insurance']:
            return Response({"error": f"Cannot record payment for status '{transaction.payment_status}'."}, status=status.HTTP_400_BAD_REQUEST)

        transaction.payment_status = 'completed'
        transaction.save()
        return Response(PaymentTransactionSerializer(transaction).data)

class InsuranceClaimProcessingViewSet(viewsets.ModelViewSet):
    queryset = InsuranceClaimProcessing.objects.all()
    serializer_class = InsuranceClaimProcessingSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['payment_transaction__patient_id', 'insurance_provider_id', 'status']
    search_fields = ['claim_identifier', 'payment_transaction__originating_service_record_id']
