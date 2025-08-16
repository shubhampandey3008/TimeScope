#!/usr/bin/env python3
"""
Helper script to run the Employee Monitoring System UI

This script will start both the FastAPI backend and Streamlit frontend.
Run this script to start the complete application.
"""

import subprocess
import sys
import os
import time
import signal
from threading import Thread

def run_fastapi():
    """Run the FastAPI backend server"""
    print("🚀 Starting FastAPI backend server...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n⏹️  FastAPI server stopped")
    except Exception as e:
        print(f"❌ Error starting FastAPI server: {e}")

def run_streamlit():
    """Run the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    try:
        # Wait a bit for FastAPI to start
        time.sleep(3)
        subprocess.run([
            sys.executable, "-m", "streamlit", 
            "run", 
            "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "127.0.0.1"
        ])
    except KeyboardInterrupt:
        print("\n⏹️  Streamlit frontend stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit frontend: {e}")

def main():
    print("🏢 Employee Monitoring System")
    print("=" * 50)
    print("Starting both FastAPI backend and Streamlit frontend...")
    print("\n📡 Backend API will be available at: http://localhost:8000")
    print("🌐 Frontend UI will be available at: http://localhost:8501")
    print("\nPress Ctrl+C to stop both servers")
    print("=" * 50)
    
    # Start FastAPI in a separate thread
    fastapi_thread = Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    try:
        # Run Streamlit in the main thread
        run_streamlit()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        print("✅ Both servers stopped successfully!")

if __name__ == "__main__":
    main() 