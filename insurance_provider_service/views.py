from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
import requests
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
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for provider in queryset:
            provider_data = InsuranceProviderSerializer(provider).data
            
            # Only fetch user data if there's a user_id
            if provider.user_id:
                try:
                    # Fetch user details from auth service
                    auth_service_url = f'http://localhost:8000/api/auth/internal/user/{provider.user_id}/'
                    response = requests.get(auth_service_url)
                    response.raise_for_status()
                    user_data = response.json()
                    
                    # Add user data to the provider data
                    provider_data['username'] = user_data.get('username')
                    provider_data['email'] = user_data.get('email')
                    provider_data['first_name'] = user_data.get('first_name')
                    provider_data['last_name'] = user_data.get('last_name')
                except Exception as e:
                    # Handle case when auth service is unavailable
                    provider_data['username'] = 'N/A'
                    provider_data['email'] = 'N/A'
                    provider_data['first_name'] = 'N/A'
                    provider_data['last_name'] = 'N/A'
            else:
                # No user associated with this provider
                provider_data['username'] = None
                provider_data['email'] = None
                provider_data['first_name'] = None
                provider_data['last_name'] = None
                
            data.append(provider_data)
        return Response(data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Only fetch user data if there's a user_id
        if instance.user_id:
            try:
                # Fetch user details from auth service
                auth_service_url = f'http://localhost:8000/api/auth/internal/user/{instance.user_id}/'
                response = requests.get(auth_service_url)
                response.raise_for_status()
                user_data = response.json()
                
                # Add user data to the response
                data['username'] = user_data.get('username')
                data['email'] = user_data.get('email')
                data['first_name'] = user_data.get('first_name')
                data['last_name'] = user_data.get('last_name')
            except Exception as e:
                # Handle case when auth service is unavailable
                data['username'] = 'N/A'
                data['email'] = 'N/A'
                data['first_name'] = 'N/A'
                data['last_name'] = 'N/A'
        else:
            # No user associated with this provider
            data['username'] = None
            data['email'] = None
            data['first_name'] = None
            data['last_name'] = None
            
        return Response(data)
