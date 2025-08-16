import psutil
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import subprocess
import re
from collections import defaultdict, deque

try:
    from AppKit import NSWorkspace
    from Foundation import NSBundle
    import Quartz
except ImportError:
    NSWorkspace = None
    NSBundle = None
    Quartz = None

try:
    import config
except ImportError:
    import config.example as config

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Monitors system activity including applications and websites"""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.app_usage = defaultdict(float)  # app_name -> total_seconds
        self.website_usage = defaultdict(float)  # domain -> total_seconds
        self.activity_log = deque(maxlen=1000)  # Recent activity entries
        self.current_app = None
        self.current_website = None
        self.last_activity_time = datetime.now()
        self.idle_start_time = None
        self.session_start = None
        
        # Check macOS frameworks availability
        self.macos_available = all([NSWorkspace, NSBundle, Quartz])
        if not self.macos_available:
            logger.warning("macOS frameworks not available - limited monitoring capabilities")
    
    def start_monitoring(self):
        """Start system monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.session_start = datetime.now()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("System monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                current_time = datetime.now()
                
                # Check for idle time
                if self._is_system_idle():
                    if not self.idle_start_time:
                        self.idle_start_time = current_time
                else:
                    if self.idle_start_time:
                        # System is active again
                        idle_duration = (current_time - self.idle_start_time).total_seconds()
                        self._log_activity("system_idle", f"Idle for {idle_duration:.1f}s", idle_duration)
                        self.idle_start_time = None
                    
                    # Monitor active application
                    if config.MONITOR_APPLICATIONS:
                        self._monitor_applications()
                    
                    # Monitor websites
                    if config.MONITOR_WEBSITES:
                        self._monitor_websites()
                    else:
                        logger.debug("Website monitoring disabled in config")
                
                time.sleep(config.APP_MONITOR_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _is_system_idle(self) -> bool:
        """Check if system is idle"""
        try:
            if self.macos_available:
                # Use Quartz to get idle time
                idle_time = Quartz.CGEventSourceSecondsSinceLastEventType(
                    Quartz.kCGEventSourceStateHIDSystemState,
                    Quartz.kCGAnyInputEventType
                )
                return idle_time > config.IDLE_THRESHOLD
            else:
                # Fallback method - check CPU usage and other indicators
                cpu_percent = psutil.cpu_percent(interval=1)
                return cpu_percent < 5  # Very low CPU usage might indicate idle
        except Exception as e:
            logger.error(f"Error checking idle state: {e}")
            return False
    
    def _monitor_applications(self):
        """Monitor active applications"""
        try:
            if self.macos_available:
                # Use NSWorkspace to get frontmost application
                workspace = NSWorkspace.sharedWorkspace()
                active_app = workspace.frontmostApplication()
                
                if active_app:
                    app_name = active_app.localizedName()
                    bundle_id = active_app.bundleIdentifier()
                    
                    # Skip excluded apps
                    if app_name in config.EXCLUDE_APPS:
                        return
                    
                    # Track application usage
                    if self.current_app != app_name:
                        if self.current_app:
                            # Log previous app usage
                            duration = (datetime.now() - self.last_activity_time).total_seconds()
                            self.app_usage[self.current_app] += duration
                            self._log_activity("app_switch", f"From {self.current_app} to {app_name}", duration)
                        
                        self.current_app = app_name
                        self.last_activity_time = datetime.now()
                    
                    # Get additional app info
                    app_info = {
                        "name": app_name,
                        "bundle_id": bundle_id,
                        "pid": active_app.processIdentifier()
                    }
                    
                    return app_info
            else:
                # Fallback: use psutil to get processes
                return self._get_active_process_fallback()
                
        except Exception as e:
            logger.error(f"Error monitoring applications: {e}")
            return None
    
    def _get_active_process_fallback(self) -> Optional[Dict]:
        """Fallback method to get active process without macOS frameworks"""
        try:
            # Get processes sorted by CPU usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 0:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and get the most active
            if processes:
                active_proc = max(processes, key=lambda x: x['cpu_percent'])
                app_name = active_proc['name']
                
                if app_name not in config.EXCLUDE_APPS:
                    if self.current_app != app_name:
                        if self.current_app:
                            duration = (datetime.now() - self.last_activity_time).total_seconds()
                            self.app_usage[self.current_app] += duration
                            self._log_activity("app_switch", f"From {self.current_app} to {app_name}", duration)
                        
                        self.current_app = app_name
                        self.last_activity_time = datetime.now()
                    
                    return {
                        "name": app_name,
                        "pid": active_proc['pid'],
                        "cpu_percent": active_proc['cpu_percent']
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in fallback app monitoring: {e}")
            return None
    
    def _monitor_websites(self):
        """Monitor website visits in supported browsers"""
        try:
            logger.debug(f"Checking browsers: {config.SUPPORTED_BROWSERS}")
            
            # Check if any browser is currently the active app
            current_app = self.current_app
            logger.debug(f"Current active app: {current_app}")
            
            # Only check URL if a browser is active
            browser_active = False
            if current_app:
                for browser in config.SUPPORTED_BROWSERS:
                    if browser.lower() in current_app.lower() or current_app.lower() in browser.lower():
                        browser_active = True
                        logger.debug(f"Browser {browser} is active (app: {current_app})")
                        break
            
            if not browser_active:
                logger.debug("No browser is currently active")
                return None
            
            for browser in config.SUPPORTED_BROWSERS:
                logger.debug(f"Checking browser: {browser}")
                website = None
                
                if browser == "Safari" or "safari" in browser.lower():
                    website = self._get_safari_current_url()
                elif "chrome" in browser.lower():
                    website = self._get_chrome_current_url()
                elif "firefox" in browser.lower():
                    website = self._get_firefox_current_url()
                else:
                    logger.debug(f"Unsupported browser: {browser}")
                    continue
                
                if website:
                    logger.debug(f"Found website: {website}")
                    domain = self._extract_domain(website)
                    logger.debug(f"Extracted domain: {domain}")
                    if domain and domain != self.current_website:
                        if self.current_website:
                            # Log previous website usage
                            duration = (datetime.now() - self.last_activity_time).total_seconds()
                            self.website_usage[self.current_website] += duration
                            self._log_activity("website_switch", f"From {self.current_website} to {domain}", duration)
                            logger.info(f"Website switch: {self.current_website} -> {domain} ({duration:.1f}s)")
                        
                        self.current_website = domain
                        self.last_activity_time = datetime.now()
                        self._log_activity("website_visit", f"Visiting {domain}", 0)
                        logger.info(f"Now visiting: {domain}")
                    
                    return website
                else:
                    logger.debug(f"No website found for browser: {browser}")
            
            logger.debug("No active websites found in any browser")
            return None
            
        except Exception as e:
            logger.error(f"Error monitoring websites: {e}")
            return None
    
    def _get_safari_current_url(self) -> Optional[str]:
        """Get current URL from Safari"""
        try:
            script = '''
            tell application "Safari"
                if (count of windows) > 0 then
                    return URL of current tab of front window
                end if
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Error getting Safari URL: {e}")
        return None
    
    def _get_chrome_current_url(self) -> Optional[str]:
        """Get current URL from Chrome"""
        try:
            script = '''
            tell application "Google Chrome"
                if (count of windows) > 0 then
                    return URL of active tab of front window
                end if
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Error getting Chrome URL: {e}")
        return None
    
    def _get_firefox_current_url(self) -> Optional[str]:
        """Get current URL from Firefox (limited support)"""
        # Firefox doesn't support AppleScript as well as Safari/Chrome
        # This is a placeholder - would need browser extension or other method
        return None
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            # Simple regex to extract domain
            match = re.search(r'https?://(?:www\.)?([^/]+)', url)
            if match:
                return match.group(1)
        except Exception as e:
            logger.debug(f"Error extracting domain from {url}: {e}")
        return None
    
    def _log_activity(self, activity_type: str, description: str, duration: float = 0):
        """Log activity to the activity log"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "description": description,
            "duration": duration
        }
        self.activity_log.append(entry)
        logger.debug(f"Activity logged: {entry}")
    
    def get_app_usage_summary(self) -> Dict[str, float]:
        """Get application usage summary"""
        # Add current app usage if tracking
        if self.current_app and self.last_activity_time:
            current_duration = (datetime.now() - self.last_activity_time).total_seconds()
            summary = dict(self.app_usage)
            summary[self.current_app] = summary.get(self.current_app, 0) + current_duration
            return summary
        return dict(self.app_usage)
    
    def get_website_usage_summary(self) -> Dict[str, float]:
        """Get website usage summary"""
        # Add current website usage if tracking
        if self.current_website and self.last_activity_time:
            current_duration = (datetime.now() - self.last_activity_time).total_seconds()
            summary = dict(self.website_usage)
            summary[self.current_website] = summary.get(self.current_website, 0) + current_duration
            return summary
        return dict(self.website_usage)
    
    def get_activity_log(self, limit: int = 100) -> List[Dict]:
        """Get recent activity log"""
        return list(self.activity_log)[-limit:]
    
    def get_current_activity(self) -> Dict:
        """Get current activity information"""
        return {
            "current_app": self.current_app,
            "current_website": self.current_website,
            "is_idle": self.idle_start_time is not None,
            "idle_duration": (datetime.now() - self.idle_start_time).total_seconds() if self.idle_start_time else 0,
            "session_duration": (datetime.now() - self.session_start).total_seconds() if self.session_start else 0,
            "monitoring": self.monitoring
        }
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used / (1024**3),
                "memory_total_gb": memory.total / (1024**3),
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used / (1024**3),
                "disk_total_gb": disk.total / (1024**3),
                "process_count": len(psutil.pids())
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def reset_session(self):
        """Reset monitoring session"""
        self.app_usage.clear()
        self.website_usage.clear()
        self.activity_log.clear()
        self.current_app = None
        self.current_website = None
        self.session_start = datetime.now()
        self.last_activity_time = datetime.now()
        self.idle_start_time = None
        logger.info("Monitoring session reset")
    
    def format_usage_data_for_api(self) -> List[str]:
        """Format both app and website usage data in [name: time] format for API"""
        try:
            app_usage = self.get_app_usage_summary()
            website_usage = self.get_website_usage_summary()
            formatted_usage = []
            
            # Combine app and website usage into one dictionary
            combined_usage = {}
            
            # Add app usage (include ALL usage, no minimum threshold)
            for app_name, total_seconds in app_usage.items():
                if total_seconds > 0:  # Include any usage > 0
                    combined_usage[app_name] = total_seconds
            
            # Add website usage (include ALL usage, no minimum threshold)
            for website_domain, total_seconds in website_usage.items():
                if total_seconds > 0:  # Include any usage > 0
                    combined_usage[website_domain] = total_seconds
            
            # Sort by usage time (descending)
            sorted_usage = sorted(combined_usage.items(), key=lambda x: x[1], reverse=True)
            
            # Format as strings
            for name, total_seconds in sorted_usage:
                if total_seconds >= 60:
                    # Show minutes for longer sessions
                    minutes = round(total_seconds / 60, 1)
                    formatted_usage.append(f"{name}: {minutes}m")
                else:
                    # Show seconds for shorter sessions
                    seconds = round(total_seconds, 1)
                    formatted_usage.append(f"{name}: {seconds}s")
            
            logger.info(f"Formatted {len(formatted_usage)} usage entries from {len(app_usage)} apps + {len(website_usage)} websites")
            logger.info(f"App usage data: {dict(app_usage)}")
            logger.info(f"Website usage data: {dict(website_usage)}")
            return formatted_usage
            
        except Exception as e:
            logger.error(f"Error formatting usage data for API: {e}")
            return []
    
    def format_app_usage_for_api(self) -> List[str]:
        """Legacy method - use format_usage_data_for_api instead"""
        logger.warning("format_app_usage_for_api is deprecated, use format_usage_data_for_api")
        return self.format_usage_data_for_api()
    
    def export_session_data(self) -> Dict:
        """Export session data"""
        return {
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "session_duration": (datetime.now() - self.session_start).total_seconds() if self.session_start else 0,
            "app_usage": self.get_app_usage_summary(),
            "website_usage": self.get_website_usage_summary(),
            "activity_log": list(self.activity_log),
            "current_activity": self.get_current_activity(),
            "system_info": self.get_system_info()
        } 