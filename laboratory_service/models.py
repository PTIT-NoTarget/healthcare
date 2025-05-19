from django.db import models
from django.utils import timezone


class Laboratory(models.Model):
    """Model for laboratory information"""
    lab_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'laboratories'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.lab_id})"


class LabTest(models.Model):
    """Model for laboratory test types"""
    test_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    turn_around_time = models.IntegerField(help_text="Time in hours")  # Typical time to complete test
    sample_type = models.CharField(max_length=50)  # Blood, Urine, etc.
    instructions = models.TextField(blank=True, null=True)
    reference_ranges = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lab_tests'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.test_id})"


class LabOrder(models.Model):
    """Model for laboratory test orders"""
    order_id = models.CharField(max_length=20, unique=True)
    patient_id = models.CharField(max_length=50)
    doctor_id = models.CharField(max_length=50)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, related_name='orders')
    ordered_date = models.DateTimeField(default=timezone.now)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('ORDERED', 'Ordered'),
            ('SCHEDULED', 'Scheduled'),
            ('SAMPLE_COLLECTED', 'Sample Collected'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('REPORTED', 'Reported'),
            ('CANCELLED', 'Cancelled')
        ],
        default='ORDERED'
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ('ROUTINE', 'Routine'),
            ('URGENT', 'Urgent'),
            ('STAT', 'STAT')  # Immediate attention
        ],
        default='ROUTINE'
    )
    notes = models.TextField(blank=True, null=True)
    clinical_information = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lab_orders'
        ordering = ['-ordered_date']
    
    def __str__(self):
        return f"Order {self.order_id} for Patient {self.patient_id}"


class LabOrderTest(models.Model):
    """Model for individual tests within an order"""
    order = models.ForeignKey(LabOrder, on_delete=models.CASCADE, related_name='tests')
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('REPORTED', 'Reported'),
            ('CANCELLED', 'Cancelled')
        ],
        default='PENDING'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lab_order_tests'
        unique_together = ('order', 'test')
    
    def __str__(self):
        return f"{self.test.name} for Order {self.order.order_id}"


class TestResult(models.Model):
    """Model for test results"""
    result_id = models.CharField(max_length=20, unique=True)
    order_test = models.OneToOneField(LabOrderTest, on_delete=models.CASCADE, related_name='result')
    result_value = models.TextField()
    unit = models.CharField(max_length=50, blank=True, null=True)
    reference_range = models.CharField(max_length=100, blank=True, null=True)
    abnormal_flag = models.CharField(
        max_length=10,
        choices=[
            ('LOW', 'Low'),
            ('NORMAL', 'Normal'),
            ('HIGH', 'High'),
            ('CRITICAL', 'Critical'),
            ('NA', 'Not Applicable')
        ],
        default='NA'
    )
    comments = models.TextField(blank=True, null=True)
    performed_by = models.CharField(max_length=50)  # ID of lab technician
    verified_by = models.CharField(max_length=50, blank=True, null=True)  # ID of verifier
    performed_date = models.DateTimeField(default=timezone.now)
    verified_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'test_results'
    
    def __str__(self):
        return f"Result {self.result_id} for {self.order_test.test.name}"
