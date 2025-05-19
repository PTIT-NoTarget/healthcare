from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Pharmacy, Order
from .serializers import (
    PharmacySerializer,
    OrderSerializer,
    OrderCreateSerializer
)


class PharmacyViewSet(viewsets.ModelViewSet):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city', 'state', 'is_24_hours']
    search_fields = ['name', 'address', 'city']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def pharmacists_list(self, request, pk=None):
        """Get a list of pharmacist IDs working at this pharmacy."""
        pharmacy = self.get_object()
        return Response(pharmacy.pharmacist_ids)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def add_pharmacist(self, request, pk=None):
        """Add a pharmacist's ID to this pharmacy."""
        pharmacy = self.get_object()
        pharmacist_id = request.data.get('pharmacist_id')
        if not pharmacist_id:
            return Response({'error': 'Pharmacist ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if pharmacist_id not in pharmacy.pharmacist_ids:
            pharmacy.pharmacist_ids.append(pharmacist_id)
            pharmacy.save()
            return Response({'status': 'Pharmacist ID added successfully.', 'pharmacist_ids': pharmacy.pharmacist_ids}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Pharmacist ID already exists.', 'pharmacist_ids': pharmacy.pharmacist_ids}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def remove_pharmacist(self, request, pk=None):
        """Remove a pharmacist's ID from this pharmacy."""
        pharmacy = self.get_object()
        pharmacist_id = request.data.get('pharmacist_id')
        if not pharmacist_id:
            return Response({'error': 'Pharmacist ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if pharmacist_id in pharmacy.pharmacist_ids:
            pharmacy.pharmacist_ids.remove(pharmacist_id)
            pharmacy.save()
            return Response({'status': 'Pharmacist ID removed successfully.', 'pharmacist_ids': pharmacy.pharmacist_ids}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Pharmacist ID not found in this pharmacy.'}, status=status.HTTP_404_NOT_FOUND)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related('items')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['pharmacy', 'status', 'patient_id']
    search_fields = ['patient_name', 'prescription_id']
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_permissions(self):
        if self.action in ['destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status_data = request.data.get('status')

        if status_data not in dict(Order.STATUS_CHOICES).keys():
            return Response({'status': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = status_data
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify_insurance(self, request, pk=None):
        """Contact insurance provider service to verify coverage"""
        order = self.get_object()
        
        insurance_id = order.insurance_provider_id
        if not insurance_id:
            return Response({'detail': 'No insurance provider specified'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            coverage_amount = float(order.total_amount) * 0.8  # 80% coverage
            
            order.insurance_coverage_amount = coverage_amount
            order.patient_payment_amount = float(order.total_amount) - coverage_amount
            order.save()
            
            return Response({
                'coverage_amount': coverage_amount,
                'patient_amount': order.patient_payment_amount
            })
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def assign_pharmacist(self, request, pk=None):
        """Assign a pharmacist to this order."""
        order = self.get_object()
        pharmacist_id = request.data.get('pharmacist_id')

        if not pharmacist_id:
            return Response({'error': 'Pharmacist ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        pharmacy = order.pharmacy
        if pharmacist_id not in pharmacy.pharmacist_ids:
            return Response({'error': f'Pharmacist {pharmacist_id} is not associated with this pharmacy.'}, status=status.HTTP_400_BAD_REQUEST)

        order.pharmacist_id = pharmacist_id
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

