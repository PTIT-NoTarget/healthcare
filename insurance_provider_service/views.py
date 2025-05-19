from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import InsuranceProvider
from .serializers import InsuranceProviderSerializer

class InsuranceProviderViewSet(viewsets.ModelViewSet):
    queryset = InsuranceProvider.objects.filter(is_active=True)
    serializer_class = InsuranceProviderSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins manage insurance provider company details
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['company_name', 'provider_id_number']
    ordering_fields = ['company_name', 'created_at']
