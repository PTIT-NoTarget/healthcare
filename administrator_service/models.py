from django.db import models
from auth_service.models import User


class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='administrator')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    access_level = models.IntegerField(default=1)  # Higher numbers mean more access

    def __str__(self):
        return f"{self.user.username} - Admin ({self.employee_id})" 