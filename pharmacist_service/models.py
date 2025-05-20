from django.db import models


class Pharmacist(models.Model):
    user_id = models.IntegerField(unique=True)
    pharmacist_id = models.CharField(max_length=50, unique=True)  # Add unique identifier
    license_number = models.CharField(max_length=30, unique=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    pharmacy_id = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pharmacist {self.pharmacist_id} - {self.license_number}"
