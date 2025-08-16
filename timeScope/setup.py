#!/usr/bin/env python3
"""
Setup script for Employee Monitoring System

This script will:
1. Initialize the database
2. Run database migrations
3. Create an initial admin user
"""

import subprocess
import sys
import os
from getpass import getpass

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def setup_database():
    """Setup database and run migrations"""
    print("📊 Setting up database...")
    
    # Check if alembic.ini exists
    if not os.path.exists("alembic.ini"):
        print("📝 Alembic not initialized. Initializing...")
        if not run_command("alembic init alembic", "Initialize Alembic"):
            return False
    
    # Run migrations
    if not run_command("alembic upgrade head", "Run database migrations"):
        return False
    
    return True

def create_admin_user():
    """Create initial admin user using the API"""
    print("\n👤 Setting up initial admin user...")
    
    print("Please provide details for the initial admin user:")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    email = input("Email: ")
    username = input("Username: ")
    password = getpass("Password: ")
    
    # Create a simple script to add the user
    script_content = f'''
import requests
import json

try:
    response = requests.post(
        "http://localhost:8000/api/v1/employees/",
        json={{
            "first_name": "{first_name}",
            "last_name": "{last_name}",
            "email": "{email}",
            "username": "{username}",
            "password": "{password}",
            "position": "Administrator"
        }},
        headers={{"Content-Type": "application/json"}}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Admin user created successfully!")
        print(f"👤 Username: {{data['username']}}")
        print(f"📧 Email: {{data['email']}}")
        print(f"🆔 ID: {{data['id']}}")
    else:
        print("❌ Failed to create admin user:")
        print(response.json())
        
except Exception as e:
    print(f"❌ Error creating admin user: {{e}}")
    print("⚠️  Make sure the FastAPI server is running on port 8000")
'''
    
    # Write and execute the script
    with open("temp_create_admin.py", "w") as f:
        f.write(script_content)
    
    print("\n🚀 Starting FastAPI server temporarily...")
    print("⚠️  This will start the server in the background. Press Ctrl+C when done.")
    
    try:
        # Start FastAPI server
        import subprocess
        import time
        
        server_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Create admin user
        subprocess.run([sys.executable, "temp_create_admin.py"])
        
        # Stop server
        server_process.terminate()
        server_process.wait()
        
        # Clean up
        os.remove("temp_create_admin.py")
        
    except KeyboardInterrupt:
        print("\n⏹️  Setup interrupted")
        if 'server_process' in locals():
            server_process.terminate()
        if os.path.exists("temp_create_admin.py"):
            os.remove("temp_create_admin.py")

def main():
    print("🏢 Employee Monitoring System Setup")
    print("=" * 50)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: No virtual environment detected")
        print("   It's recommended to run this in a virtual environment")
        if input("Continue anyway? (y/N): ").lower() != 'y':
            return
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Install dependencies"):
        print("❌ Failed to install dependencies. Please run 'pip install -r requirements.txt' manually.")
        return
    
    # Setup database
    if not setup_database():
        print("❌ Database setup failed. Please check your configuration.")
        return
    
    # Create admin user
    create_admin_user()
    
    print("\n🎉 Setup completed!")
    print("\n🚀 To start the application:")
    print("   python run_ui.py")
    print("\n🌐 Then visit:")
    print("   Frontend UI: http://localhost:8501")
    print("   API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 