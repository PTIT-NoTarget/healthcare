// Initialize MongoDB databases
db = db.getSiblingDB('healthcare_medicines');
db = db.getSiblingDB('healthcare_prescriptions');
db = db.getSiblingDB('healthcare_medical_records');
db = db.getSiblingDB('healthcare_inventory');

// Create collections to ensure databases are created
db.getSiblingDB('healthcare_medicines').createCollection('medicines');
db.getSiblingDB('healthcare_prescriptions').createCollection('prescriptions');
db.getSiblingDB('healthcare_medical_records').createCollection('medical_records');
db.getSiblingDB('healthcare_inventory').createCollection('inventory'); 