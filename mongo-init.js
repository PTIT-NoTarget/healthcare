// Initialize MongoDB database for Medicine Service

db = db.getSiblingDB('healthcare_medicines');

// Create collection for medicines
db.createCollection('medicines');

// Create indexes for better query performance
db.medicines.createIndex({ "name": 1 });
db.medicines.createIndex({ "generic_name": 1 });
db.medicines.createIndex({ "ndc_code": 1 }, { unique: true });

print("MongoDB initialized for healthcare_medicines database!"); 