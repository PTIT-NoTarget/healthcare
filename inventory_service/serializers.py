from rest_framework import serializers
from .models import InventoryItem

class InventoryItemSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()
    needs_reorder = serializers.ReadOnlyField()

    class Meta:
        model = InventoryItem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class InventoryItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'item_name') # item_name might be fetched or validated against medicine service

    def validate(self, data):
        # Example: If item_type is medicine, ensure item_id (medicine_id) is provided and valid (pseudo-code)
        # if data.get('item_type') == 'medicine':
        #     medicine_id = data.get('item_id')
        #     if not medicine_id:
        #         raise serializers.ValidationError("Medicine ID is required for items of type 'medicine'.")
        #     # Here you might call the medicine_service to validate medicine_id and fetch item_name
        #     # For now, we assume item_name is provided or handled elsewhere if denormalized.
        return data

