from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientPolicyViewSet,
    InsuranceClaimViewSet
)

router = DefaultRouter()
router.register(r'patient-policies', PatientPolicyViewSet, basename='patientpolicy')
router.register(r'claims', InsuranceClaimViewSet, basename='insuranceclaim')

urlpatterns = [
    path('', include(router.urls)),
    # Internal endpoints are defined as actions on their respective viewsets:
    # - InsuranceClaimViewSet:
    #   - POST /api/insurance/claims/internal/initiate/
    #   - POST /api/insurance/claims/{pk}/internal/adjudication-update/
    # - PatientPolicyViewSet:
    #   - POST /api/insurance/patient-policies/{pk}/verify/ (for admin)
]

