import os
import sys
import subprocess

# Set environment variables for Docker container names
os.environ['DB_HOST_MYSQL'] = 'mysql'
os.environ['DB_HOST_POSTGRES'] = 'postgres'
os.environ['DB_HOST_MONGODB'] = 'mongodb'

# Update Django settings to use Docker container names
settings_file = 'healthcare/settings.py'
with open(settings_file, 'r') as f:
    settings = f.read()

# Replace localhost with Docker container names
settings = settings.replace("'HOST': 'localhost',  # Use 'mysql'", "'HOST': os.environ.get('DB_HOST_MYSQL', 'localhost'),")
settings = settings.replace("'HOST': 'localhost',  # Use 'postgres'", "'HOST': os.environ.get('DB_HOST_POSTGRES', 'localhost'),")
settings = settings.replace("'host': 'mongodb://localhost:27017',  # Use", 
                           "'host': f\"mongodb://{os.environ.get('DB_HOST_MONGODB', 'localhost')}:27017\",  # Use")

with open(settings_file, 'w') as f:
    f.write(settings)

print("Django settings updated to use Docker container names.")

# Run migrations
print("\nRunning migrations...")
try:
    subprocess.run([sys.executable, 'manage.py', 'makemigrations'], check=True)
    subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
    print("✅ Migrations complete.")
except subprocess.CalledProcessError as e:
    print(f"❌ Migration failed: {e}")
    sys.exit(1)

# Run the development server
print("\nStarting development server...")
try:
    subprocess.run([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])
except KeyboardInterrupt:
    print("\nServer stopped.")
except Exception as e:
    print(f"❌ Server error: {e}")
    sys.exit(1) 