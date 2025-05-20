from django.db import models


class Administrator(models.Model):
    user_id = models.IntegerField(unique=True)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    access_level = models.IntegerField(default=1)  # Higher numbers mean more access
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Admin {self.employee_id} (User ID: {self.user_id})" 