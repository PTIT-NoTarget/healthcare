from django.apps import AppConfig


class LaboratoryServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'laboratory_service'
    verbose_name = 'Laboratory Service'
    
    def ready(self):
        # Import signal handlers
        pass
