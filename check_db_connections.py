import os
import sys
import django
import time
import pymongo
import psycopg2
import mysql.connector

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

def check_mysql_connection():
    """Check if MySQL connection is working"""
    print("\nChecking MySQL connection...")
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="healthcare",
            password="healthcare_password",
            database="healthcare_users"
        )
        if conn.is_connected():
            print("✅ MySQL connection successful!")
            conn.close()
            return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

def check_postgres_connection():
    """Check if PostgreSQL connection is working"""
    print("\nChecking PostgreSQL connection...")
    try:
        # Make sure to specify the database name and disable SSL
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="healthcare",
            password="healthcare_password",
            database="healthcare_pharmacy",
            sslmode='disable'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result[0] == 1:
            print("✅ PostgreSQL connection successful!")
            cursor.close()
            conn.close()
            return True
        else:
            print("❌ PostgreSQL connection failed: unexpected result")
            return False
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def check_mongodb_connection():
    """Check if MongoDB connection is working"""
    print("\nChecking MongoDB connection...")
    try:
        # Connect without authentication for development setup
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        print("✅ MongoDB connection successful!")
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def main():
    print("=== Database Connection Checker ===")
    
    mysql_ok = check_mysql_connection()
    postgres_ok = check_postgres_connection()
    mongodb_ok = check_mongodb_connection()
    
    print("\n=== Summary ===")
    print(f"MySQL: {'✅ Connected' if mysql_ok else '❌ Failed'}")
    print(f"PostgreSQL: {'✅ Connected' if postgres_ok else '❌ Failed'}")
    print(f"MongoDB: {'✅ Connected' if mongodb_ok else '❌ Failed'}")
    
    if mysql_ok and postgres_ok and mongodb_ok:
        print("\n🎉 All database connections successful! Your application is ready to run.")
    else:
        print("\n⚠️ Some database connections failed. Please check your Docker containers and configurations.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 