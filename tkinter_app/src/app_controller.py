import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

try:
    from .api_client import APIClient, APIException
    from .auth import AuthManager
    from .system_monitor import SystemMonitor
    from .screenshot_manager import ScreenshotManager
except ImportError:
    # For standalone testing
    from api_client import APIClient, APIException
    from auth import AuthManager
    from system_monitor import SystemMonitor
    from screenshot_manager import ScreenshotManager

try:
    import config
except ImportError:
    import config.example as config

logger = logging.getLogger(__name__)


class AppController:
    """Main application controller that coordinates all components"""
    
    def __init__(self):
        # Initialize components
        self.api_client = APIClient()
        self.auth_manager = AuthManager()
        self.system_monitor = SystemMonitor()
        self.screenshot_manager = ScreenshotManager(self.api_client)
        
        # State
        self.current_time_entry = None
        self.tracking_active = False
        self.sync_thread = None
        self.sync_running = False
        
        # Setup logging
        self.setup_logging()
        
        logger.info("Application controller initialized")
    
    def setup_logging(self):
        """Setup application logging"""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def login(self, username: str, password: str) -> bool:
        """Login user"""
        try:
            # Validate credentials locally first
            if not username or not password:
                raise ValueError("Username and password are required")
            
            if len(password) < 6:
                raise ValueError("Password must be at least 6 characters")
            
            # Test API connection first
            if not self.api_client.test_connection():
                logger.warning("API connection failed")
                if config.OFFLINE_MODE:
                    logger.info("Attempting offline login")
                    return self.auth_manager.login(username, password)
                else:
                    raise APIException("Cannot connect to API server")
            
            # Authenticate with API
            logger.info(f"Authenticating user: {username}")
            response = self.api_client.authenticate_employee(username, password)
            
            if response.get('access_token'):
                logger.info("Authentication successful, getting employee data")
                
                # Get employee data
                employee_data = self.api_client.get_employee()
                
                # Login to auth manager
                success = self.auth_manager.login(username, password, employee_data)
                
                if success:
                    # Start background sync
                    self.start_sync()
                    logger.info(f"User logged in successfully: {username}")
                    return True
            else:
                logger.warning("Authentication failed - no access token received")
                return False
            
            return False
            
        except APIException as e:
            logger.error(f"API authentication failed: {e}")
            # Only allow offline login for connection issues, not auth failures
            if "Cannot connect to API server" in str(e) and config.OFFLINE_MODE:
                logger.info("Connection failed, trying offline login")
                return self.auth_manager.login(username, password)
            return False
        except Exception as e:
            logger.error(f"Login failed: {e}")
            # For validation errors, don't fall back to offline mode
            if "Password must be at least" in str(e) or "Username and password" in str(e):
                return False
            # Only allow offline login for connection issues
            if config.OFFLINE_MODE:
                logger.info("Unexpected error, trying offline login")
                return self.auth_manager.login(username, password)
            return False
    
    def logout(self):
        """Logout user"""
        try:
            # Stop tracking if active
            if self.tracking_active:
                self.stop_tracking()
            
            # Stop sync
            self.stop_sync()
            
            # Logout from API
            self.api_client.logout()
            
            # Logout from auth manager
            self.auth_manager.logout()
            
            logger.info("User logged out successfully")
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
    
    def get_projects(self) -> List[Dict]:
        """Get user's projects"""
        try:
            if not self.auth_manager.is_session_valid():
                raise Exception("Session expired")
            
            # Check if we have an API token
            if not self.api_client.auth_token:
                logger.warning("No API authentication token available")
                return []
            
            response = self.api_client.get_projects()
            return response.get('projects', [])
            
        except APIException as e:
            logger.error(f"API error getting projects: {e}")
            # If it's an auth error, clear the token
            if "401" in str(e) or "Unauthorized" in str(e):
                self.api_client.auth_token = None
            return []
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []
    

    
    def start_tracking(self, project_id: int) -> bool:
        """Start time tracking"""
        try:
            if not self.auth_manager.is_session_valid():
                raise Exception("Session expired")
            
            if self.tracking_active:
                logger.warning("Tracking already active")
                return False
            
            # Start tracking via API
            response = self.api_client.start_time_tracking(str(project_id))
            
            # Debug logging to see what the API returns
            logger.info(f"Start tracking API response: {response}")
            
            # Check for various possible field names for the time entry ID
            time_entry_id = (response.get('time_entry_id') or 
                            response.get('id') or 
                            response.get('entry_id') or 
                            response.get('time_entry', {}).get('id'))
            
            if time_entry_id or response:  # If we get any response, consider it success
                self.current_time_entry = response
                self.tracking_active = True
                
                # Reset session to start fresh
                self.system_monitor.reset_session()
                
                # Start system monitoring
                self.system_monitor.start_monitoring()
                
                # Start screenshot capture
                if config.SCREENSHOT_ENABLED and time_entry_id:
                    self.screenshot_manager.start_capture(time_entry_id)
                
                logger.info(f"Time tracking started for project {project_id}")
                return True
            
            logger.warning(f"Start tracking failed - no valid response: {response}")
            return False
            
        except APIException as e:
            # Handle specific case of employee already having active time entry
            if "already has an active time entry" in str(e):
                logger.warning(f"Employee already has active time entry - checking current state")
                # Try to get the current active time entry
                try:
                    active_entry = self.api_client.get_active_time_entry(self.api_client.employee_id)
                    if active_entry:
                        logger.info(f"Found existing active time entry: {active_entry}")
                        self.current_time_entry = active_entry
                        self.tracking_active = True
                        
                        # Reset session to start fresh
                        self.system_monitor.reset_session()
                        
                        # Start local monitoring since tracking is already active on server
                        self.system_monitor.start_monitoring()
                        
                        # Start screenshot capture if time entry ID is available
                        time_entry_id = (active_entry.get('time_entry_id') or 
                                       active_entry.get('id') or 
                                       active_entry.get('entry_id'))
                        if config.SCREENSHOT_ENABLED and time_entry_id:
                            self.screenshot_manager.start_capture(time_entry_id)
                        
                        logger.info(f"Resumed tracking with existing time entry")
                        return True
                except Exception as get_error:
                    logger.error(f"Failed to get active time entry: {get_error}")
            
            logger.error(f"Error starting tracking: {e}")
            return False
        except Exception as e:
            logger.error(f"Error starting tracking: {e}")
            return False
    
    def stop_tracking(self) -> bool:
        """Stop time tracking"""
        try:
            if not self.tracking_active:
                logger.warning("No active tracking to stop")
                return False
            
            # Get app and website usage data before stopping monitoring
            usage_data = self.system_monitor.format_usage_data_for_api()
            logger.info(f"Usage data to send (apps + websites): {usage_data}")
            
            # Stop system monitoring
            self.system_monitor.stop_monitoring()
            
            # Stop screenshot capture
            self.screenshot_manager.stop_capture()
            
            # Stop tracking via API with usage data (apps + websites)
            time_entry_id = self.current_time_entry.get('time_entry_id') if self.current_time_entry else None
            response = self.api_client.stop_time_tracking(app_usage_data=usage_data)
            
            logger.info(f"Stop tracking API response: {response}")
            if response:
                # Export session data
                session_data = self.system_monitor.export_session_data()
                
                # Update time entry with monitoring data if needed (optional since app usage is now in stop call)
                if time_entry_id:
                    self.api_client.update_time_entry(time_entry_id, 
                        description=f"Session data: {session_data}")
                
                self.tracking_active = False
                self.current_time_entry = None
                
                logger.info("Time tracking stopped successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error stopping tracking: {e}")
            return False
    
    def get_current_activity(self) -> Dict:
        """Get current system activity"""
        try:
            return self.system_monitor.get_current_activity()
        except Exception as e:
            logger.error(f"Error getting current activity: {e}")
            return {}
    
    def get_app_usage_summary(self) -> Dict[str, float]:
        """Get application usage summary"""
        try:
            return self.system_monitor.get_app_usage_summary()
        except Exception as e:
            logger.error(f"Error getting app usage: {e}")
            return {}
    
    def get_website_usage_summary(self) -> Dict[str, float]:
        """Get website usage summary"""
        try:
            return self.system_monitor.get_website_usage_summary()
        except Exception as e:
            logger.error(f"Error getting website usage: {e}")
            return {}
    
    def take_manual_screenshot(self) -> bool:
        """Take manual screenshot"""
        try:
            screenshot_path = self.screenshot_manager.capture_manual_screenshot("Manual screenshot")
            return screenshot_path is not None
        except Exception as e:
            logger.error(f"Error taking manual screenshot: {e}")
            return False
    
    def get_time_summary(self) -> Dict:
        """Get time tracking summary"""
        try:
            if not self.auth_manager.is_session_valid():
                raise Exception("Session expired")
            
            return self.api_client.get_time_summary()
            
        except Exception as e:
            logger.error(f"Error getting time summary: {e}")
            return {}
    
    def get_screenshot_stats(self) -> Dict:
        """Get screenshot statistics"""
        try:
            return self.screenshot_manager.get_screenshot_stats()
        except Exception as e:
            logger.error(f"Error getting screenshot stats: {e}")
            return {}
    
    def start_sync(self):
        """Start background sync"""
        if self.sync_running:
            return
        
        self.sync_running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        logger.info("Background sync started")
    
    def stop_sync(self):
        """Stop background sync"""
        self.sync_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("Background sync stopped")
    
    def _sync_loop(self):
        """Background sync loop"""
        while self.sync_running:
            try:
                # Sync pending screenshots
                self.screenshot_manager.retry_failed_uploads()
                
                # Extend session if needed
                if self.auth_manager.is_session_valid():
                    self.auth_manager.extend_session()
                
                # Sleep for sync interval
                time.sleep(config.SYNC_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                time.sleep(30)  # Wait before retrying
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        try:
            return self.system_monitor.get_system_info()
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def get_activity_log(self, limit: int = 100) -> List[Dict]:
        """Get activity log"""
        try:
            return self.system_monitor.get_activity_log(limit)
        except Exception as e:
            logger.error(f"Error getting activity log: {e}")
            return []
    
    def export_session_data(self) -> Dict:
        """Export current session data"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'user': self.auth_manager.get_current_user(),
                'tracking_active': self.tracking_active,
                'current_time_entry': self.current_time_entry,
                'system_monitor_data': self.system_monitor.export_session_data(),
                'screenshot_stats': self.screenshot_manager.get_screenshot_stats(),
                'system_info': self.get_system_info()
            }
            return data
        except Exception as e:
            logger.error(f"Error exporting session data: {e}")
            return {}
    
    def is_tracking_active(self) -> bool:
        """Check if tracking is active"""
        return self.tracking_active
    
    def get_current_time_entry(self) -> Optional[Dict]:
        """Get current time entry"""
        return self.current_time_entry
    
    def cleanup_old_data(self):
        """Clean up old data"""
        try:
            # Clean up old screenshots
            self.screenshot_manager.cleanup_old_screenshots()
            
            # Reset system monitor session if needed
            if not self.tracking_active:
                self.system_monitor.reset_session()
            
            logger.info("Data cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_status(self) -> Dict:
        """Get application status"""
        return {
            'logged_in': self.auth_manager.is_logged_in(),
            'session_valid': self.auth_manager.is_session_valid(),
            'tracking_active': self.tracking_active,
            'monitoring_active': self.system_monitor.monitoring,
            'screenshot_capturing': self.screenshot_manager.capturing,
            'sync_running': self.sync_running,
            'api_connected': self.api_client.test_connection()
        }
    
    def shutdown(self):
        """Shutdown application"""
        try:
            logger.info("Shutting down application...")
            
            # Stop tracking
            if self.tracking_active:
                self.stop_tracking()
            
            # Stop system monitoring
            self.system_monitor.stop_monitoring()
            
            # Stop screenshot capture
            self.screenshot_manager.stop_capture()
            
            # Stop sync
            self.stop_sync()
            
            # Logout
            self.logout()
            
            # Cleanup
            self.cleanup_old_data()
            
            logger.info("Application shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}") 