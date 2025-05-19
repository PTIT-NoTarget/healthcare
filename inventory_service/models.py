from django.db import models
from django.utils.translation import gettext_lazy as _

class InventoryItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('medicine', _('Medicine')),
        ('supply', _('Medical Supply')),
        ('equipment', _('Medical Equipment')), # For durable items
    ]

    LOCATION_TYPE_CHOICES = [
        ('pharmacy', _('Pharmacy')),
        ('hospital_ward', _('Hospital Ward')),
        ('hospital_storage', _('Hospital Central Storage')),
        ('clinic', _('Clinic')),
    ]

    # General Item Information
    item_id = models.CharField(max_length=100, help_text=_("ID of the medicine (from Medicine service) or other supply/equipment"))
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='medicine')
    item_name = models.CharField(max_length=255, help_text=_("Name of the item (can be denormalized from medicine service or entered for supplies)"))
    description = models.TextField(blank=True, null=True)
    manufacturer = models.CharField(max_length=200, blank=True, null=True)

    # Location and Quantity
    location_id = models.CharField(max_length=100, help_text=_("ID of the pharmacy, hospital ward, or storage unit"))
    location_type = models.CharField(max_length=30, choices=LOCATION_TYPE_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    unit_of_measure = models.CharField(max_length=50, default='unit', help_text=_("e.g., tablets, ml, box, unit"))

    # Tracking and Financials
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True, help_text=_("For individual trackable items like equipment"))
    expiration_date = models.DateField(blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text=_("Optional: Can also be managed by pharmacy/billing service"))

    # Stock Management
    reorder_level = models.PositiveIntegerField(default=10)
    supplier_id = models.CharField(max_length=100, blank=True, null=True, help_text=_("Reference to a supplier service or ID"))
    last_restock_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, help_text=_("e.g., Available, Low Stock, Out of Stock, Recalled"))

    # Audit and Notes
    notes = models.TextField(blank=True, null=True)
    # Add a field to link to the original medicine definition if item_type is 'medicine'
    medicine_detail_id = models.CharField(max_length=100, blank=True, null=True, help_text=_("Corresponds to the ID in the Medicine service if this is a medicine"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Inventory Item')
        verbose_name_plural = _('Inventory Items')
        db_table = 'inventory_items'
        # Ensures that for a given location, an item (identified by item_id and potentially batch) is unique.
        # For items without batch (like some supplies or equipment), batch_number can be null or a default value.
        unique_together = [('location_id', 'location_type', 'item_id', 'batch_number', 'serial_number')]
        indexes = [
            models.Index(fields=['item_id', 'item_type']),
            models.Index(fields=['location_id', 'location_type']),
            models.Index(fields=['expiration_date']),
        ]

    def __str__(self):
        return f"{self.item_name} ({self.quantity} {self.unit_of_measure}) at {self.location_id} ({self.location_type})"

    @property
    def is_expired(self):
        from django.utils import timezone
        if self.expiration_date:
            return self.expiration_date < timezone.now().date()
        return False

    @property
    def needs_reorder(self):
        return self.quantity <= self.reorder_level
