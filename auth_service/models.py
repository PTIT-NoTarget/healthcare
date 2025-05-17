from django.contrib.auth.models import AbstractUser
from django.db import models

class UserRole(models.TextChoices):
    PATIENT = 'PATIENT', 'Patient'
    DOCTOR = 'DOCTOR', 'Doctor'
    NURSE = 'NURSE', 'Nurse'
    ADMINISTRATOR = 'ADMINISTRATOR', 'Administrator'
    PHARMACIST = 'PHARMACIST', 'Pharmacist'
    INSURANCE_PROVIDER = 'INSURANCE_PROVIDER', 'Insurance Provider'
    LAB_TECHNICIAN = 'LAB_TECHNICIAN', 'Laboratory Technician'

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(
        max_length=50,
        choices=UserRole.choices,
        default=UserRole.PATIENT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class FullName(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='full_names')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address