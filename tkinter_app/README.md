# macOS System Monitoring & Time Tracking App

A local macOS application for employee time tracking with system monitoring capabilities including application tracking, website monitoring, and automatic screenshot capture.

## Features

- **Employee Authentication**: Secure login system with credential storage
- **Time Tracking**: Start/stop timer with project and task assignment
- **System Monitoring**: 
  - Track active applications
  - Monitor website visits (Safari, Chrome, Firefox)
  - Capture periodic screenshots
  - Detect idle time
- **Project Management**: View assigned projects and tasks
- **Real-time Data**: Sync with backend API for time entries and screenshots
- **Offline Mode**: Works without internet connection
- **Security**: Encrypted data storage and secure credential management

## Project Structure

```
system_tracking_app/
├── main.py                 # Application entry point
├── config.py               # Configuration settings
├── config.example.py       # Configuration template
├── requirements.txt        # Python dependencies
├── run.sh                  # Quick start script
├── test_app.py            # Test suite
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── src/                   # Source code
│   ├── __init__.py
│   ├── api_client.py      # Backend API communication
│   ├── auth.py            # Authentication & credential management
│   ├── system_monitor.py  # System monitoring (apps, websites, idle)
│   ├── screenshot_manager.py # Screenshot capture & upload
│   ├── app_controller.py  # Main application controller
│   └── ui/                # User interface
│       ├── __init__.py
│       └── main_window.py # Main GUI window
├── logs/                  # Application logs
├── data/                  # Local data storage
├── screenshots/           # Captured screenshots
└── venv/                  # Virtual environment
```

## Requirements

- macOS 10.14 or later
- Python 3.8 or later
- Backend API server (optional - works offline)

## Quick Start

1. **Easy Installation** (recommended):
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

2. **Manual Installation**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create directories
   mkdir -p logs data screenshots
   
   # Run the application
   python main.py
   ```

## Configuration

The application will automatically create `config.py` from `config.example.py` on first run. Key settings:

- **API_BASE_URL**: Backend API endpoint (default: http://localhost:8000/api/v1)
- **SCREENSHOT_ENABLED**: Enable/disable screenshot capture
- **SCREENSHOT_INTERVAL**: Screenshot frequency in seconds (default: 300)
- **MONITOR_APPLICATIONS**: Enable application monitoring
- **MONITOR_WEBSITES**: Enable website monitoring
- **OFFLINE_MODE**: Allow offline operation

## Usage

1. **Launch the application**:
   ```bash
   python main.py
   ```

2. **Login**: Enter your employee credentials (or use demo mode if offline)

3. **Select Project & Task**: Choose from your assigned projects and tasks

4. **Start Tracking**: Click "Start Tracking" to begin monitoring

5. **Monitor Activity**: View real-time activity in the main window:
   - Current application usage
   - Website visits
   - Time tracking
   - System information

6. **Manual Screenshots**: Take screenshots manually using the "Take Screenshot" button

7. **Stop Tracking**: Click "Stop Tracking" to end the session

## Features in Detail

### System Monitoring
- **Application Tracking**: Monitors active applications and usage time
- **Website Monitoring**: Tracks website visits in Safari, Chrome, and Firefox
- **Idle Detection**: Detects when the system is idle
- **Activity Logging**: Maintains detailed activity logs

### Screenshot Management
- **Automatic Capture**: Takes screenshots at configured intervals
- **Manual Capture**: On-demand screenshot functionality
- **Compression**: Optimizes file sizes with quality settings
- **Upload**: Automatically uploads to backend server
- **Local Storage**: Keeps local copies with cleanup

### Security & Privacy
- **Encrypted Storage**: All sensitive data is encrypted
- **Keychain Integration**: Secure credential storage in macOS Keychain
- **Privacy Controls**: Respects system privacy settings
- **Configurable Monitoring**: Enable/disable specific monitoring features

## Testing

Run the test suite to verify installation:
```bash
python test_app.py
```

## Permissions

The app requires the following macOS permissions:
- **Screen Recording**: For screenshot capture
- **Accessibility**: For application monitoring
- **Full Disk Access**: For comprehensive system monitoring

Grant these permissions in System Preferences > Security & Privacy > Privacy.

## Troubleshooting

### Common Issues

1. **Permission Denied**: Grant required permissions in System Preferences
2. **API Connection Failed**: Check backend server or enable offline mode
3. **Screenshot Not Working**: Ensure Screen Recording permission is granted
4. **App Monitoring Issues**: Grant Accessibility permission

### Logs

Check application logs in `logs/system_monitor.log` for detailed error information.

## Development

### Running Tests
```bash
python test_app.py
```

### Project Architecture
- **AppController**: Main application coordinator
- **APIClient**: Backend communication
- **AuthManager**: Authentication and security
- **SystemMonitor**: System activity monitoring
- **ScreenshotManager**: Screenshot capture and management
- **MainWindow**: GUI interface

## License

This project is for internal use only. All rights reserved. 