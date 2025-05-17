from django.contrib import admin
from .models import Pharmacy, Inventory, Order, OrderItem


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'phone', 'email', 'license_number', 'is_24_hours')
    search_fields = ('name', 'address', 'city', 'license_number')
    list_filter = ('state', 'is_24_hours')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('pharmacy', 'medicine_name', 'quantity', 'batch_number', 'expiration_date', 'selling_price')
    search_fields = ('pharmacy__name', 'medicine_name', 'batch_number')
    list_filter = ('pharmacy', 'expiration_date')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('medicine_id', 'medicine_name', 'quantity', 'unit_price', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'pharmacy', 'patient_name', 'status', 'order_date', 'total_amount')
    search_fields = ('patient_name', 'pharmacy__name')
    list_filter = ('status', 'pharmacy', 'order_date')
    inlines = [OrderItemInline] 