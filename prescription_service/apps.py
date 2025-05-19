from django.apps import AppConfig


class PrescriptionServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prescription_service'
    verbose_name = 'Prescription Service'
    
    def ready(self):
        # Import signal handlers
        pass
