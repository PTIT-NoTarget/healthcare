-- Create all PostgreSQL databases
CREATE DATABASE healthcare_laboratory;
CREATE DATABASE healthcare_insurance;
CREATE DATABASE healthcare_payment;
CREATE DATABASE healthcare_appointment;

-- Grant privileges to the healthcare user
GRANT ALL PRIVILEGES ON DATABASE healthcare_pharmacy TO healthcare;
GRANT ALL PRIVILEGES ON DATABASE healthcare_laboratory TO healthcare;
GRANT ALL PRIVILEGES ON DATABASE healthcare_insurance TO healthcare;
GRANT ALL PRIVILEGES ON DATABASE healthcare_payment TO healthcare;
GRANT ALL PRIVILEGES ON DATABASE healthcare_appointment TO healthcare; 