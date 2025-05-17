# Healthcare Microservice System

A comprehensive healthcare management system built with Django and multiple database backends.

## Architecture

This system uses a microservice architecture with multiple databases:

- **MySQL**: Used for user-related services (auth, doctor, nurse, patient, administrator, etc.)
- **PostgreSQL**: Used for pharmacy service (pharmacies, inventory, orders)
- **MongoDB**: Used for medicine service (medicine catalog with detailed information)

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- pip

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd healthcare
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Start the database containers:
   ```
   docker-compose up -d
   ```

4. Wait for the containers to initialize (about 10-15 seconds)

5. Run migrations:
   ```
   python manage.py migrate --database=default
   python manage.py migrate --database=medicine_db
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

### Running in Docker

To run the application with Docker networking:

```
python run_in_docker.py
```

This script will:
1. Update the database connection settings to use Docker container names
2. Run migrations
3. Start the development server

## Services

### User Services
- **Auth Service**: Core user authentication and authorization
- **Doctor Service**: Doctor profiles and specializations
- **Nurse Service**: Nurse profiles and departments
- **Patient Service**: Patient profiles and medical records
- **Administrator Service**: System administrators with access control
- **Pharmacist Service**: Pharmacist profiles and certifications
- **Insurance Provider Service**: Insurance company representatives
- **Laboratory Technician Service**: Lab technicians and specializations

### Data Services
- **Medicine Service**: Comprehensive medicine database with MongoDB
- **Pharmacy Service**: Pharmacy management with inventory and orders

## Database Schema

Each service has its own models and database tables. The system uses Django's database router to direct queries to the appropriate database.

## API Documentation

Each service exposes RESTful APIs for CRUD operations and specialized endpoints. Authentication is handled through JWT tokens.

## Troubleshooting

If you encounter database connection issues:

1. Run the connection check script:
   ```
   python check_db_connections.py
   ```

2. Make sure Docker containers are running:
   ```
   docker ps
   ```

3. Check container logs:
   ```
   docker-compose logs
   ``` 