
    db.getSiblingDB('admin').auth('healthcare', 'healthcare_password');
    db = db.getSiblingDB('healthcare_medicines');
    db.createCollection('medicines');
    