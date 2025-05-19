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
        elif model._meta.app_label == 'medical_record_service':
            return 'medical_record_db'
        elif model._meta.app_label == 'laboratory_service':
            return 'laboratory_db'
        elif model._meta.app_label == 'inventory_service':
            return 'inventory_db'
        elif model._meta.app_label == 'insurance_service':
            return 'insurance_db'
        elif model._meta.app_label == 'payment_service':
            return 'payment_db'
        elif model._meta.app_label == 'appointment_service':
            return 'appointment_db'
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
        elif model._meta.app_label == 'medical_record_service':
            return 'medical_record_db'
        elif model._meta.app_label == 'laboratory_service':
            return 'laboratory_db'
        elif model._meta.app_label == 'inventory_service':
            return 'inventory_db'
        elif model._meta.app_label == 'insurance_service':
            return 'insurance_db'
        elif model._meta.app_label == 'payment_service':
            return 'payment_db'
        elif model._meta.app_label == 'appointment_service':
            return 'appointment_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the same database
        or if the relation is allowed between different databases
        """
        # Allow relations within same database
        if obj1._meta.app_label == obj2._meta.app_label:
            return True
        
        # Allow relations within PostgreSQL databases
        if obj1._meta.app_label in ['pharmacy_service', 'laboratory_service', 'insurance_service', 'payment_service', 'appointment_service'] and \
           obj2._meta.app_label in ['pharmacy_service', 'laboratory_service', 'insurance_service', 'payment_service', 'appointment_service']:
            return True

        # Allow relations within MongoDB databases
        if obj1._meta.app_label in ['medicine_service', 'prescription_service', 'medical_record_service', 'inventory_service'] and \
           obj2._meta.app_label in ['medicine_service', 'prescription_service', 'medical_record_service', 'inventory_service']:
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
        elif app_label == 'medical_record_service':
            return db == 'medical_record_db'
        elif app_label == 'laboratory_service':
            return db == 'laboratory_db'
        elif app_label == 'inventory_service':
            return db == 'inventory_db'
        elif app_label == 'insurance_service':
            return db == 'insurance_db'
        elif app_label == 'payment_service':
            return db == 'payment_db'
        elif app_label == 'appointment_service':
            return db == 'appointment_db'
        # For auth_*, patient_*, doctor_*, nurse_*, pharmacist_*, administrator_*,
        # insurance_provider_*, laboratory_technician_* services, they use the 'default' database (MySQL)
        # So, if app_label is one of them, it should migrate only if db is 'default'
        if app_label in ['auth_service', 'patient_service', 'doctor_service', 'nurse_service',
                          'pharmacist_service', 'administrator_service', 'insurance_provider_service',
                          'laboratory_technician_service']:
            return db == 'default'
        # Fallback for any other app_labels not explicitly handled, though all current ones are.
        return db == 'default'

