from django.db import models

class Patient(models.Model):
    user_id = models.IntegerField(unique=True)
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=5)
    medical_history = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Patient {self.user_id}"
