from django.db import models


class Pharmacy(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    hours_of_operation = models.JSONField(default=dict)  # Store as JSON
    license_number = models.CharField(max_length=50, unique=True)
    is_24_hours = models.BooleanField(default=False)
    pharmacist_ids = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Pharmacies'
        db_table = 'pharmacies'


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    )
    
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='orders')
    patient_id = models.CharField(max_length=50)  # Reference to Patient from User service
    patient_name = models.CharField(max_length=200)
    doctor_id = models.CharField(max_length=50, blank=True, null=True)  # Reference to Doctor
    doctor_name = models.CharField(max_length=200, blank=True, null=True)
    prescription_id = models.CharField(max_length=50, blank=True, null=True)
    pharmacist_id = models.CharField(max_length=50, blank=True, null=True)
    prescription_image_url = models.URLField(blank=True, null=True)
    delivery_address = models.TextField(blank=True, null=True)
    estimated_delivery_time = models.DateTimeField(blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    insurance_provider_id = models.CharField(max_length=50, blank=True, null=True)
    insurance_coverage_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    patient_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.patient_name}"
    
    class Meta:
        db_table = 'pharmacy_orders'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    inventory_item_id = models.CharField(max_length=100, help_text="ID of the InventoryItem from inventory_service")
    medicine_name = models.CharField(max_length=200)  # Denormalized for convenience in orders
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.medicine_name} x {self.quantity}"
    
    class Meta:
        db_table = 'pharmacy_order_items'
