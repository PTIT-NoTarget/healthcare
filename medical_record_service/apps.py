from django.apps import AppConfig


class MedicalRecordServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medical_record_service'
    verbose_name = 'Medical Record Service'
    
    def ready(self):
        # Import signal handlers
        pass
