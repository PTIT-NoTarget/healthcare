from django.db import models
from auth_service.models import User


class LaboratoryTechnician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='laboratory_technician')
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100)
    laboratory_name = models.CharField(max_length=100)
    certification = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.employee_id}" 