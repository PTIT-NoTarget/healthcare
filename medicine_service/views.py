from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Medicine
from .serializers import MedicineSerializer, MedicineDetailSerializer


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dosage_form', 'requires_prescription', 'is_controlled_substance', 'manufacturer']
    search_fields = ['name', 'generic_name', 'ndc_code', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MedicineDetailSerializer
        return MedicineSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def prescription_required(self, request):
        medicines = Medicine.objects.filter(requires_prescription=True)
        serializer = self.get_serializer(medicines, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def controlled_substances(self, request):
        medicines = Medicine.objects.filter(is_controlled_substance=True)
        serializer = self.get_serializer(medicines, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def over_the_counter(self, request):
        medicines = Medicine.objects.filter(requires_prescription=False)
        serializer = self.get_serializer(medicines, many=True)
        return Response(serializer.data) 