#!/usr/bin/env python3
"""
macOS System Monitoring & Time Tracking Application

A local macOS application for employee time tracking with system monitoring 
capabilities including application tracking, website monitoring, and 
automatic screenshot capture.
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app_controller import AppController
from src.ui.main_window import MainWindow

try:
    import config
except ImportError:
    # Copy example config if config.py doesn't exist
    import shutil
    if not os.path.exists('config.py'):
        shutil.copy('config.example.py', 'config.py')
        print("Created config.py from config.example.py")
        print("Please review and update the configuration before running the app.")
    import config


def setup_directories():
    """Create necessary directories"""
    directories = [
        'screenshots',
        'logs',
        'data'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def check_permissions():
    """Check macOS permissions"""
    import subprocess
    
    print("Checking macOS permissions...")
    
    # Check if we have accessibility permissions
    try:
        result = subprocess.run([
            'osascript', '-e', 
            'tell application "System Events" to get name of first process'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠️  Accessibility permission required!")
            print("Please grant accessibility permissions in System Preferences > Security & Privacy > Privacy > Accessibility")
            return False
    except Exception as e:
        print(f"Could not check accessibility permissions: {e}")
    
    print("✅ Permissions check completed")
    return True


def main():
    """Main application entry point"""
    print("Starting macOS System Monitoring & Time Tracking App...")
    
    # Setup directories
    setup_directories()
    
    # Check permissions
    if not check_permissions():
        print("Please grant required permissions and restart the application.")
        return 1
    
    try:
        # Initialize application controller
        app_controller = AppController()
        
        # Create and run main window
        main_window = MainWindow(app_controller)
        
        print("Application started successfully!")
        print(f"API Endpoint: {config.API_BASE_URL}")
        print(f"Screenshot Enabled: {config.SCREENSHOT_ENABLED}")
        print(f"System Monitoring: {config.MONITOR_APPLICATIONS and config.MONITOR_WEBSITES}")
        
        # Run the application
        main_window.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Application error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 