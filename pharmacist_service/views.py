from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
import requests
from .models import Pharmacist
from .serializers import PharmacistSerializer
from .permissions import IsPharmacist


class PharmacistViewSet(viewsets.ModelViewSet):
    queryset = Pharmacist.objects.all()
    serializer_class = PharmacistSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        elif self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsPharmacist]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for pharmacist in queryset:
            pharmacist_data = PharmacistSerializer(pharmacist).data
            try:
                # Fetch user details from auth service
                auth_service_url = f'http://localhost:8000/api/auth/internal/user/{pharmacist.user_id}/'
                response = requests.get(auth_service_url)
                response.raise_for_status()
                user_data = response.json()
                
                # Add user data to the pharmacist data
                pharmacist_data['username'] = user_data.get('username')
                pharmacist_data['email'] = user_data.get('email')
                pharmacist_data['first_name'] = user_data.get('first_name')
                pharmacist_data['last_name'] = user_data.get('last_name')
            except Exception as e:
                # Handle case when auth service is unavailable
                pharmacist_data['username'] = 'N/A'
                pharmacist_data['email'] = 'N/A'
                pharmacist_data['first_name'] = 'N/A'
                pharmacist_data['last_name'] = 'N/A'
                
            data.append(pharmacist_data)
        return Response(data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Fetch user details from auth service
        try:
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
            
        return Response(data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activate(self, request, pk=None):
        """Activate a pharmacist"""
        pharmacist = self.get_object()
        pharmacist.is_active = True
        pharmacist.save()
        serializer = self.get_serializer(pharmacist)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """Deactivate a pharmacist"""
        pharmacist = self.get_object()
        pharmacist.is_active = False
        pharmacist.save()
        serializer = self.get_serializer(pharmacist)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Return the pharmacist profile of the current user
        """
        try:
            # Get user_id from request JWT token or session
            user_id = request.user.id
            pharmacist = Pharmacist.objects.get(user_id=user_id)
            serializer = self.get_serializer(pharmacist)
            data = serializer.data
            
            # Add user data directly from the request.user
            data['username'] = request.user.username
            data['email'] = request.user.email
            data['first_name'] = request.user.first_name
            data['last_name'] = request.user.last_name
            
            return Response(data)
        except Pharmacist.DoesNotExist:
            return Response({"detail": "User is not a pharmacist"}, status=404)

