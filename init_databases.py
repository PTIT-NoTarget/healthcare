import os
import time
import subprocess
# from mysql.connector import connect as mysql_connect
import psycopg2

print("=== Initializing Healthcare Databases ===")

# Wait for database services to be fully up
print("Waiting for database services to be ready...")
time.sleep(5)  # Give containers time to initialize

# Initialize PostgreSQL
print("\n=== Initializing PostgreSQL ===")
try:
    # First connect as postgres default user
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        user="healthcare",
        password="healthcare_password",
        database="postgres"
    )
    conn.autocommit = True  # Important for creating databases
    cursor = conn.cursor()
    
    # Databases to create
    databases_to_create = [
        'healthcare_pharmacy',
        'healthcare_insurance',
        'healthcare_laboratory',
        'healthcare_payment',
        'healthcare_appointment' # Added based on settings.py
    ]
    
    # Check if user already exists
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname='healthcare'")
    user_exists = cursor.fetchone()
    
    if not user_exists:
        print("Creating PostgreSQL user 'healthcare'...")
        cursor.execute("CREATE USER healthcare WITH PASSWORD 'healthcare_password'")
    else:
        print("PostgreSQL user 'healthcare' already exists.")
    
    for db_name in databases_to_create:
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        db_exists = cursor.fetchone()
        
        if not db_exists:
            print(f"Creating PostgreSQL database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO healthcare")
        else:
            print(f"PostgreSQL database '{db_name}' already exists.")
    print("✅ PostgreSQL initialization complete.")
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ PostgreSQL initialization failed: {e}")

# Initialize MongoDB
print("\n=== Initializing MongoDB ===")
try:
    # Use the mongo shell to create user and database
    mongo_init_script = """
    db.getSiblingDB('admin').auth('healthcare', 'healthcare_password');
    db = db.getSiblingDB('healthcare_medicines');
    db.createCollection('medicines');
    """
    
    with open('mongo_init.js', 'w') as f:
        f.write(mongo_init_script)
    
    # Run mongo shell command
    print("Running MongoDB initialization script...")
    subprocess.run([
        'docker', 'exec', 'healthcare_mongodb', 
        'mongosh', '-u', 'healthcare', '-p', 'healthcare_password', '--authenticationDatabase', 'admin',
        '--file', '/mongo_init.js'
    ], check=False)
    
    print("✅ MongoDB initialization complete.")
except Exception as e:
    print(f"❌ MongoDB initialization failed: {e}")

print("\n=== Database Initialization Complete ===")
print("You can now run your Django application with the configured databases.") 