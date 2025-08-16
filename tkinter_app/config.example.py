# Configuration file for macOS System Monitoring App
# Copy this file to config.py and update with your settings

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_TIMEOUT = 30
API_RETRY_ATTEMPTS = 3

# Screenshot Settings
SCREENSHOT_ENABLED = True
SCREENSHOT_INTERVAL = 300  # seconds (5 minutes)
SCREENSHOT_QUALITY = 80    # JPEG quality (1-100)
SCREENSHOT_RESIZE = (1280, 720)  # Resize to save space, None for original size

# System Monitoring Settings
MONITOR_APPLICATIONS = True
MONITOR_WEBSITES = True
MONITOR_IDLE_TIME = True
IDLE_THRESHOLD = 300  # seconds (5 minutes)

# Application Monitoring
APP_MONITOR_INTERVAL = 10  # seconds
EXCLUDE_APPS = [
    "System Preferences",
    "Activity Monitor",
    "Console",
    "Keychain Access"
]

# Website Monitoring
WEBSITE_MONITOR_INTERVAL = 5  # seconds
TRACK_BROWSER_TABS = True
SUPPORTED_BROWSERS = [
    "Safari",
    "Google Chrome",
    "Firefox",
    "Microsoft Edge"
]

# UI Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_RESIZABLE = True
THEME = "light"  # light or dark
ALWAYS_ON_TOP = False

# Security Settings
ENCRYPT_DATA = True
STORE_CREDENTIALS = True  # Store in macOS Keychain
SESSION_TIMEOUT = 3600  # seconds (1 hour)

# Logging Settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "system_monitor.log"
LOG_MAX_SIZE = 10485760  # 10MB
LOG_BACKUP_COUNT = 5

# Data Storage
LOCAL_DB_PATH = "local_data.db"
SYNC_INTERVAL = 60  # seconds
OFFLINE_MODE = True  # Allow offline operation

# Notification Settings
SHOW_NOTIFICATIONS = True
NOTIFICATION_SOUND = True
BREAK_REMINDERS = True
BREAK_INTERVAL = 3600  # seconds (1 hour) 