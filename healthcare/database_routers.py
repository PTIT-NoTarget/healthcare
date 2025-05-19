class DatabaseRouter:
    """
    A router to control database operations for different applications
    """
    def db_for_read(self, model, **hints):
        """
        Point all operations on medicine_service models to mongodb,
        pharmacy_service models to PostgreSQL, and all others to MySQL
        """
        if model._meta.app_label == 'medicine_service':
            return 'medicine_db'
        elif model._meta.app_label == 'pharmacy_service':
            return 'pharmacy_db'
        elif model._meta.app_label == 'prescription_service':
            return 'prescription_db'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Point all operations on medicine_service models to mongodb,
        pharmacy_service models to PostgreSQL, and all others to MySQL
        """
        if model._meta.app_label == 'medicine_service':
            return 'medicine_db'
        elif model._meta.app_label == 'pharmacy_service':
            return 'pharmacy_db'
        elif model._meta.app_label == 'prescription_service':
            return 'prescription_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the same database
        or if the relation is allowed between different databases
        """
        # Allow relations within same database
        if obj1._meta.app_label == obj2._meta.app_label:
            return True
        
        # Special case: allow relations between Pharmacy and related models from other apps
        # This is needed for the API to work between services
        return None  # Default to the Django behavior

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure that the medicine_service models only appear in the mongodb,
        pharmacy_service only in PostgreSQL, and everything else in MySQL
        """
        if app_label == 'medicine_service':
            return db == 'medicine_db'
        elif app_label == 'pharmacy_service':
            return db == 'pharmacy_db'
        elif app_label == 'prescription_service':
            return db == 'prescription_db'
        return db == 'default' 