from django.contrib import admin
from .models import InventoryItem

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'item_type', 'quantity', 'location_id', 'location_type', 'expiration_date', 'is_expired', 'needs_reorder')
    list_filter = ('item_type', 'location_type', 'expiration_date', 'status')
    search_fields = ('item_name', 'item_id', 'location_id', 'batch_number', 'serial_number')
    readonly_fields = ('is_expired', 'needs_reorder', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': (('item_name', 'item_id', 'medicine_detail_id'), 'item_type', 'description', 'manufacturer')
        }),
        ('Location & Quantity', {
            'fields': (('location_id', 'location_type'), ('quantity', 'unit_of_measure'))
        }),
        ('Tracking & Financials', {
            'fields': (('batch_number', 'serial_number'), 'expiration_date', ('purchase_price', 'selling_price'))
        }),
        ('Stock Management', {
            'fields': ('reorder_level', 'supplier_id', 'last_restock_date', 'status')
        }),
        ('Audit & Notes', {
            'fields': ('notes', ('created_at', 'updated_at'))
        }),
    )
