from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentTransactionViewSet, InsuranceClaimProcessingViewSet

router = DefaultRouter()
router.register(r'transactions', PaymentTransactionViewSet, basename='paymenttransaction')
router.register(r'insurance-claims', InsuranceClaimProcessingViewSet, basename='insuranceclaim')

urlpatterns = [
    path('', include(router.urls)),
    # Note: The internal transaction creation is now an action within PaymentTransactionViewSet
    # and will be accessible via the router-generated URL for that action (e.g., /api/payments/transactions/internal/initiate/)
]
