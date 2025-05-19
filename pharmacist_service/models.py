from django.db import models
from auth_service.models import User


class Pharmacist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacist')
    license_number = models.CharField(max_length=30, unique=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    pharmacy_id = models.CharField(max_length=50, blank=True, null=True)  # Changed from pharmacy_name
    is_active = models.BooleanField(default=True)  # Added
    contact_phone = models.CharField(max_length=20, blank=True, null=True)  # Added
    contact_email = models.EmailField(blank=True, null=True)  # Added

    def __str__(self):
        return f"{self.user.username} - {self.license_number}"
