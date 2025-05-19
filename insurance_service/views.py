from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
import requests # For inter-service communication

from .models import PatientPolicy, InsuranceClaim
from .serializers import (
    PatientPolicySerializer, PatientPolicyCreateUpdateSerializer,
    InsuranceClaimSerializer, InsuranceClaimCreateInternalSerializer, InsuranceClaimUpdateAdjudicationInternalSerializer
)

# Placeholder for robust service-to-service authentication
class IsInternalServiceOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        # TODO: Implement secure service token validation
        # Example: return request.headers.get('X-Internal-Service-Token') == settings.INTERNAL_SERVICE_SECRET_TOKEN
        # For development, you might allow if a specific debug header is set, but ensure this is NOT for production.
        # Allowing broadly for now for easier initial testing, but THIS MUST BE SECURED.
        if request.headers.get('X-Debug-Allow-Internal') == 'true': # Example debug header
            return True
        return False

class PatientPolicyViewSet(viewsets.ModelViewSet):
    queryset = PatientPolicy.objects.all()
    serializer_class = PatientPolicySerializer
    permission_classes = [permissions.IsAuthenticated] # Base permission
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient_id', 'insurance_provider_company_id', 'status', 'expiration_date']
    search_fields = ['patient_id', 'policy_number', 'insurance_provider_company_id']
    ordering_fields = ['patient_id', 'effective_date', 'expiration_date', 'updated_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PatientPolicyCreateUpdateSerializer
        return PatientPolicySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'verify_policy_admin']:
            # Only admin users or designated staff should manage policies directly.
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            # Patients can only see their own policies.
            return PatientPolicy.objects.filter(patient_id=str(user.id))
        return super().get_queryset()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='verify')
    def verify_policy_admin(self, request, pk=None):
        policy = self.get_object()
        if policy.status == 'pending_verification':
            policy.status = 'active'
            policy.verification_notes = request.data.get('verification_notes', f"Verified by admin {request.user.username} on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}.")
            policy.save()
            return Response(PatientPolicySerializer(policy).data)
        elif policy.status == 'active':
            return Response({"message": "Policy is already active."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": f"Policy in status '{policy.status}' cannot be verified directly to active. Review policy status."}, status=status.HTTP_400_BAD_REQUEST)

class InsuranceClaimViewSet(viewsets.ModelViewSet):
    queryset = InsuranceClaim.objects.all()
    serializer_class = InsuranceClaimSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'policy__patient_id': ['exact'],
        'policy__insurance_provider_company_id': ['exact'],
        'status': ['exact', 'in'],
        'service_date_start': ['exact', 'gte', 'lte'],
        'payment_transaction_id': ['exact'],
        'insurer_claim_reference_id': ['exact']
    }
    search_fields = ['policy__policy_number', 'insurer_claim_reference_id', 'payment_transaction_id', 'policy__patient_id']
    ordering_fields = ['claim_submission_date', 'service_date_start', 'status', 'last_updated_at']

    def get_permissions(self):
        if self.action in ['initiate_claim_internal', 'update_claim_adjudication_internal']:
            return [IsInternalServiceOrAdmin()] # Must be secured properly!
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Direct manipulation of claims should be restricted.
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            # Patients can only see their own claims.
            return InsuranceClaim.objects.filter(policy__patient_id=str(user.id))
        return super().get_queryset()

    @action(detail=False, methods=['post'], serializer_class=InsuranceClaimCreateInternalSerializer, url_path='internal/initiate')
    def initiate_claim_internal(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            claim = serializer.save(status='received')
            # TODO: Trigger an asynchronous task (e.g., Celery) to:
            # 1. Fetch InsuranceProviderCompany details (API endpoint, credentials) using claim.policy.insurance_provider_company_id from insurance_provider_service.
            # 2. Format and send the claim data to the external insurer's API.
            # 3. On successful submission to insurer: update claim.status to 'submitted_to_insurer',
            #    set claim.submitted_to_insurer_at, and store claim.insurer_claim_reference_id.
            # 4. On failure: update claim.status to 'error_submission' and log details.
            print(f"TODO: Async task to submit claim {claim.id} (PaymentTx: {claim.payment_transaction_id}) to external insurer for Policy {claim.policy.id}.")
            return Response(InsuranceClaimSerializer(claim).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], serializer_class=InsuranceClaimUpdateAdjudicationInternalSerializer, url_path='internal/adjudication-update')
    def update_claim_adjudication_internal(self, request, pk=None):
        claim = self.get_object()
        serializer = self.get_serializer(claim, data=request.data, partial=True)
        if serializer.is_valid():
            updated_claim = serializer.save()

            # Set adjudication_completed_at if a final adjudication status is reached and not already set
            final_adjudication_statuses = ['adjudicated_approved', 'adjudicated_rejected', 'closed_paid', 'closed_rejected']
            if not updated_claim.adjudication_completed_at and updated_claim.status in final_adjudication_statuses:
                updated_claim.adjudication_completed_at = timezone.now()
                # No need to call save() again if it's part of serializer.save() or handled by post_save signal
                # However, if serializer.save() doesn't include this logic, explicitly save.
                # For this example, assuming serializer.save() handles all field updates.

            # Notify payment_service to update its PaymentTransaction
            try:
                payment_service_url = f'http://payment-service/api/payments/transactions/{claim.payment_transaction_id}/internal/update-insurance-outcome/'
                payload = {
                    'insurance_service_claim_id': str(updated_claim.id),
                    'status': updated_claim.status,
                    'approved_amount': float(updated_claim.approved_amount) if updated_claim.approved_amount is not None else None,
                    'patient_responsibility_amount': float(updated_claim.patient_responsibility_amount) if updated_claim.patient_responsibility_amount is not None else None,
                    'insurer_claim_reference_id': updated_claim.insurer_claim_reference_id,
                    'rejection_reason_code': updated_claim.rejection_reason_code,
                    'rejection_reason_description': updated_claim.rejection_reason_description,
                    'adjudication_completed_at': updated_claim.adjudication_completed_at.isoformat() if updated_claim.adjudication_completed_at else None
                }
                # TODO: Add robust service-to-service authentication headers
                # headers = {'X-Internal-Service-Token': settings.INTERNAL_SERVICE_SECRET_TOKEN, 'Content-Type': 'application/json'}
                # response = requests.post(payment_service_url, json=payload, headers=headers, timeout=10)
                # response.raise_for_status()
                print(f"TODO: Call payment_service ({payment_service_url}) to update transaction {claim.payment_transaction_id} with payload: {payload}")
            except requests.exceptions.RequestException as e:
                print(f"Error calling payment_service for claim {updated_claim.id}, Tx {claim.payment_transaction_id}: {e}")
                # Log this error. Consider a retry mechanism or manual intervention flag.
            except Exception as ex:
                print(f"Unexpected error preparing/calling payment_service for claim {updated_claim.id}: {ex}")

            return Response(InsuranceClaimSerializer(updated_claim).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

