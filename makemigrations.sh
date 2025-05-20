#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Generate migrations for all services
echo "Generating migrations for all services..."
python manage.py makemigrations auth_service
python manage.py makemigrations doctor_service
python manage.py makemigrations nurse_service
python manage.py makemigrations patient_service
python manage.py makemigrations administrator_service
python manage.py makemigrations pharmacist_service
python manage.py makemigrations insurance_provider_service
python manage.py makemigrations laboratory_technician_service
python manage.py makemigrations medicine_service
python manage.py makemigrations pharmacy_service
python manage.py makemigrations inventory_service
python manage.py makemigrations payment_service
python manage.py makemigrations insurance_service
python manage.py makemigrations prescription_service
python manage.py makemigrations medical_record_service
python manage.py makemigrations laboratory_service
python manage.py makemigrations template_service
python manage.py makemigrations appointment_service

# Deactivate virtual environment
deactivate

echo "Migrations generated successfully!" 