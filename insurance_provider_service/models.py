from django.db import models
from auth_service.models import User


class InsuranceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='insurance_provider')
    company_name = models.CharField(max_length=100)
    provider_id = models.CharField(max_length=30, unique=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.company_name} - {self.provider_id}" 