from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
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
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Return the pharmacist profile of the current user
        """
        if hasattr(request.user, 'pharmacist'):
            serializer = self.get_serializer(request.user.pharmacist)
            return Response(serializer.data)
        return Response({"detail": "User is not a pharmacist"}, status=404) 