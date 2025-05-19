from django.contrib import admin
from .models import Pharmacy, Order, OrderItem


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'phone', 'email', 'license_number', 'is_24_hours')
    search_fields = ('name', 'address', 'city', 'license_number')
    list_filter = ('state', 'is_24_hours')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('inventory_item_id', 'medicine_name', 'quantity', 'unit_price', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'pharmacy', 'patient_name', 'status', 'order_date', 'total_amount')
    search_fields = ('patient_name', 'pharmacy__name')
    list_filter = ('status', 'pharmacy', 'order_date')
    inlines = [OrderItemInline]

