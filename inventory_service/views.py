from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Q
from django.utils import timezone
from datetime import timedelta

from .models import InventoryItem
from .serializers import InventoryItemSerializer, InventoryItemCreateUpdateSerializer

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'item_type': ['exact'],
        'location_id': ['exact'],
        'location_type': ['exact'],
        'manufacturer': ['exact', 'icontains'],
        'supplier_id': ['exact'],
        'status': ['exact', 'icontains'],
        'expiration_date': ['exact', 'gte', 'lte'],
        'quantity': ['exact', 'gte', 'lte'],
    }
    search_fields = ['item_id', 'item_name', 'description', 'batch_number', 'serial_number']
    ordering_fields = ['item_name', 'quantity', 'expiration_date', 'created_at', 'updated_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InventoryItemCreateUpdateSerializer
        return InventoryItemSerializer

    def get_permissions(self):
        # Adjust permissions as needed, e.g., only admins or specific roles can create/update/delete
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser] # Or a custom permission
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Return inventory items that are at or below their reorder level."""
        low_stock_items = InventoryItem.objects.filter(quantity__lte=F('reorder_level'))
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Return inventory items that are expiring within a specified number of days (default 90)."""
        days_threshold = request.query_params.get('days', 90)
        try:
            days_threshold = int(days_threshold)
        except ValueError:
            return Response({"error": "Invalid days parameter."}, status=status.HTTP_400_BAD_REQUEST)

        expiry_threshold_date = timezone.now().date() + timedelta(days=days_threshold)
        expiring_items = InventoryItem.objects.filter(
            expiration_date__isnull=False,
            expiration_date__lte=expiry_threshold_date,
            expiration_date__gte=timezone.now().date() # Only include items not yet expired
        )
        serializer = self.get_serializer(expiring_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expired_items(self, request):
        """Return inventory items that have passed their expiration date."""
        expired = InventoryItem.objects.filter(
            expiration_date__isnull=False,
            expiration_date__lt=timezone.now().date()
        )
        serializer = self.get_serializer(expired, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def items_by_location(self, request):
        """Return inventory items filtered by location_id and/or location_type."""
        location_id = request.query_params.get('location_id')
        location_type = request.query_params.get('location_type')

        query = Q()
        if location_id:
            query &= Q(location_id=location_id)
        if location_type:
            query &= Q(location_type=location_type)

        if not query:
            return Response({"error": "Please provide location_id or location_type."}, status=status.HTTP_400_BAD_REQUEST)

        items = InventoryItem.objects.filter(query)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    # Potentially, an action to receive stock (adjust quantity up)
    @action(detail=True, methods=['post'])
    def receive_stock(self, request, pk=None):
        item = self.get_object()
        quantity_received = request.data.get('quantity')
        if quantity_received is None:
            return Response({"error": "Quantity is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quantity_received = int(quantity_received)
            if quantity_received <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        item.quantity = F('quantity') + quantity_received
        item.last_restock_date = timezone.now()
        item.save()
        item.refresh_from_db() # Refresh to get the updated quantity
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    # Potentially, an action to dispense/use stock (adjust quantity down)
    @action(detail=True, methods=['post'])
    def dispense_stock(self, request, pk=None):
        item = self.get_object()
        quantity_dispensed = request.data.get('quantity')
        if quantity_dispensed is None:
            return Response({"error": "Quantity is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quantity_dispensed = int(quantity_dispensed)
            if quantity_dispensed <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if item.quantity < quantity_dispensed:
            return Response({"error": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST)

        item.quantity = F('quantity') - quantity_dispensed
        item.save()
        item.refresh_from_db()
        serializer = self.get_serializer(item)
        return Response(serializer.data)
