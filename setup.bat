@echo off
REM Windows setup script with virtual environment

echo Starting Docker containers...
docker-compose down
docker-compose up -d

echo Waiting for databases to be ready...
timeout /t 30 /nobreak

echo Generating migrations for all services...
call makemigrations.bat

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Running migrations...

REM Default database migrations (MySQL)
python manage.py migrate

REM Migrations for all the service-specific databases
python manage.py migrate --database=pharmacy_db
python manage.py migrate --database=medicine_db
python manage.py migrate --database=prescription_db
python manage.py migrate --database=medical_record_db
python manage.py migrate --database=laboratory_db
python manage.py migrate --database=inventory_db
python manage.py migrate --database=insurance_db
python manage.py migrate --database=payment_db
python manage.py migrate --database=appointment_db

echo Checking MySQL tables...
docker exec healthcare_mysql mysql -u healthcare -phealthcare_password -e "USE healthcare_users; SHOW TABLES;"

echo Checking PostgreSQL tables...
docker exec healthcare_postgres psql -U healthcare -d healthcare_pharmacy -c "\dt"
docker exec healthcare_postgres psql -U healthcare -d healthcare_laboratory -c "\dt"
docker exec healthcare_postgres psql -U healthcare -d healthcare_insurance -c "\dt"
docker exec healthcare_postgres psql -U healthcare -d healthcare_payment -c "\dt"
docker exec healthcare_postgres psql -U healthcare -d healthcare_appointment -c "\dt"

echo Checking MongoDB collections...
docker exec healthcare_mongodb mongosh --quiet --eval "db.getMongo().getDBNames()"
docker exec healthcare_mongodb mongosh healthcare_medicines --quiet --eval "db.getCollectionNames()"
docker exec healthcare_mongodb mongosh healthcare_prescriptions --quiet --eval "db.getCollectionNames()"
docker exec healthcare_mongodb mongosh healthcare_medical_records --quiet --eval "db.getCollectionNames()"
docker exec healthcare_mongodb mongosh healthcare_inventory --quiet --eval "db.getCollectionNames()"

echo Deactivating virtual environment...
deactivate

echo Setup complete! 