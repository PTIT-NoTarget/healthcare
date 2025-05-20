from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
import requests
from .models import LaboratoryTechnician
from .serializers import LaboratoryTechnicianSerializer
from .permissions import IsLaboratoryTechnician


class LaboratoryTechnicianViewSet(viewsets.ModelViewSet):
    queryset = LaboratoryTechnician.objects.all()
    serializer_class = LaboratoryTechnicianSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        elif self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsLaboratoryTechnician]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for tech in queryset:
            tech_data = LaboratoryTechnicianSerializer(tech).data
            try:
                # Fetch user details from auth service
                auth_service_url = f'http://localhost:8000/api/auth/internal/user/{tech.user_id}/'
                response = requests.get(auth_service_url)
                response.raise_for_status()
                user_data = response.json()
                
                # Add user data to the technician data
                tech_data['username'] = user_data.get('username')
                tech_data['email'] = user_data.get('email')
                tech_data['first_name'] = user_data.get('first_name')
                tech_data['last_name'] = user_data.get('last_name')
            except Exception as e:
                # Handle case when auth service is unavailable
                tech_data['username'] = 'N/A'
                tech_data['email'] = 'N/A'
                tech_data['first_name'] = 'N/A'
                tech_data['last_name'] = 'N/A'
                
            data.append(tech_data)
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
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Return the laboratory technician profile of the current user
        """
        try:
            # Get user_id from request JWT token or session
            user_id = request.user.id
            technician = LaboratoryTechnician.objects.get(user_id=user_id)
            serializer = self.get_serializer(technician)
            data = serializer.data
            
            # Add user data directly from the request.user
            data['username'] = request.user.username
            data['email'] = request.user.email
            data['first_name'] = request.user.first_name
            data['last_name'] = request.user.last_name
            
            return Response(data)
        except LaboratoryTechnician.DoesNotExist:
            return Response({"detail": "User is not a laboratory technician"}, status=404) 