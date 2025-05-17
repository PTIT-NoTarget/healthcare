from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Administrator
from .serializers import AdministratorSerializer
from .permissions import IsAdministrator, IsHighLevelAdministrator


class AdministratorViewSet(viewsets.ModelViewSet):
    queryset = Administrator.objects.all()
    serializer_class = AdministratorSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsHighLevelAdministrator]
        else:
            permission_classes = [IsAdministrator]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Return the administrator profile of the current user
        """
        if hasattr(request.user, 'administrator'):
            serializer = self.get_serializer(request.user.administrator)
            return Response(serializer.data)
        return Response({"detail": "User is not an administrator"}, status=404) 