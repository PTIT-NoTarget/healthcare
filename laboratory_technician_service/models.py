from django.db import models


class LaboratoryTechnician(models.Model):
    user_id = models.IntegerField(unique=True)
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100)
    laboratory_name = models.CharField(max_length=100)
    certification = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Lab Tech {self.employee_id} (User ID: {self.user_id})" 