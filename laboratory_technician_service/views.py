from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
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
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Return the laboratory technician profile of the current user
        """
        if hasattr(request.user, 'laboratory_technician'):
            serializer = self.get_serializer(request.user.laboratory_technician)
            return Response(serializer.data)
        return Response({"detail": "User is not a laboratory technician"}, status=404) 