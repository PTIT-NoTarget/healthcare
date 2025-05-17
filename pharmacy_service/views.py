from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import requests
from django.db.models import F
from .models import Pharmacy, Inventory, Order, OrderItem
from .serializers import (
    PharmacySerializer,
    InventorySerializer,
    OrderSerializer,
    OrderItemSerializer,
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


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['pharmacy', 'medicine_id']
    search_fields = ['medicine_name', 'batch_number']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Return inventory items that are below reorder level"""
        low_stock_items = Inventory.objects.filter(quantity__lte=F('reorder_level'))
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Return inventory items that are expiring within 90 days"""
        from django.utils import timezone
        from datetime import timedelta
        
        expiry_threshold = timezone.now().date() + timedelta(days=90)
        expiring_items = Inventory.objects.filter(expiration_date__lte=expiry_threshold)
        serializer = self.get_serializer(expiring_items, many=True)
        return Response(serializer.data)


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
        status = request.data.get('status')
        
        if status not in dict(Order.STATUS_CHOICES).keys():
            return Response({'status': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = status
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify_insurance(self, request, pk=None):
        """Contact insurance provider service to verify coverage"""
        order = self.get_object()
        
        # This would be a real API call in production
        insurance_id = order.insurance_provider_id
        if not insurance_id:
            return Response({'detail': 'No insurance provider specified'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Example of how you would call the insurance provider service
        # In production, you would replace this with a real API call
        try:
            # response = requests.post(
            #    'http://insurance-provider-service/api/verify-coverage/',
            #    json={'patient_id': order.patient_id, 'total_amount': float(order.total_amount)}
            # )
            # coverage_amount = response.json().get('coverage_amount', 0)
            
            # Mock response for now
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