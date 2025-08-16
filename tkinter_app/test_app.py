#!/usr/bin/env python3
"""
Test script for the macOS System Monitoring & Time Tracking App
"""

import sys
import os
import traceback

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.api_client import APIClient
        print("✅ APIClient imported successfully")
    except Exception as e:
        print(f"❌ APIClient import failed: {e}")
        return False
    
    try:
        from src.auth import AuthManager
        print("✅ AuthManager imported successfully")
    except Exception as e:
        print(f"❌ AuthManager import failed: {e}")
        return False
    
    try:
        from src.system_monitor import SystemMonitor
        print("✅ SystemMonitor imported successfully")
    except Exception as e:
        print(f"❌ SystemMonitor import failed: {e}")
        return False
    
    try:
        from src.screenshot_manager import ScreenshotManager
        print("✅ ScreenshotManager imported successfully")
    except Exception as e:
        print(f"❌ ScreenshotManager import failed: {e}")
        return False
    
    try:
        from src.app_controller import AppController
        print("✅ AppController imported successfully")
    except Exception as e:
        print(f"❌ AppController import failed: {e}")
        return False
    
    try:
        from src.ui.main_window import MainWindow
        print("✅ MainWindow imported successfully")
    except Exception as e:
        print(f"❌ MainWindow import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        import config
        print("✅ Configuration loaded successfully")
        print(f"   API Base URL: {config.API_BASE_URL}")
        print(f"   Screenshot Enabled: {config.SCREENSHOT_ENABLED}")
        print(f"   Monitor Applications: {config.MONITOR_APPLICATIONS}")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_components():
    """Test basic component initialization"""
    print("\nTesting component initialization...")
    
    try:
        from src.api_client import APIClient
        api_client = APIClient()
        print("✅ APIClient initialized successfully")
    except Exception as e:
        print(f"❌ APIClient initialization failed: {e}")
        return False
    
    try:
        from src.auth import AuthManager
        auth_manager = AuthManager()
        print("✅ AuthManager initialized successfully")
    except Exception as e:
        print(f"❌ AuthManager initialization failed: {e}")
        return False
    
    try:
        from src.system_monitor import SystemMonitor
        system_monitor = SystemMonitor()
        print("✅ SystemMonitor initialized successfully")
    except Exception as e:
        print(f"❌ SystemMonitor initialization failed: {e}")
        return False
    
    try:
        from src.screenshot_manager import ScreenshotManager
        screenshot_manager = ScreenshotManager()
        print("✅ ScreenshotManager initialized successfully")
        print(f"   Screenshot available: {screenshot_manager.is_screenshot_available()}")
    except Exception as e:
        print(f"❌ ScreenshotManager initialization failed: {e}")
        return False
    
    return True

def test_app_controller():
    """Test app controller initialization"""
    print("\nTesting AppController...")
    
    try:
        from src.app_controller import AppController
        app_controller = AppController()
        print("✅ AppController initialized successfully")
        
        # Test status
        status = app_controller.get_status()
        print(f"   Status: {status}")
        
        return True
    except Exception as e:
        print(f"❌ AppController initialization failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("macOS System Monitoring & Time Tracking App - Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config,
        test_components,
        test_app_controller
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 