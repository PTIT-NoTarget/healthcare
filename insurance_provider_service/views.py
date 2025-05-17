from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import InsuranceProvider
from .serializers import InsuranceProviderSerializer
from .permissions import IsInsuranceProvider


class InsuranceProviderViewSet(viewsets.ModelViewSet):
    queryset = InsuranceProvider.objects.all()
    serializer_class = InsuranceProviderSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        elif self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsInsuranceProvider]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Return the insurance provider profile of the current user
        """
        if hasattr(request.user, 'insurance_provider'):
            serializer = self.get_serializer(request.user.insurance_provider)
            return Response(serializer.data)
        return Response({"detail": "User is not an insurance provider"}, status=404) 