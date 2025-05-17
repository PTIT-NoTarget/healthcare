from django.db import models

class Doctor(models.Model):
    user_id = models.IntegerField(unique=True)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Doctor {self.user_id} - {self.specialization}"
