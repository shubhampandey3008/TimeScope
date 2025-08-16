#!/bin/bash

# macOS System Monitoring & Time Tracking App Runner

echo "Starting macOS System Monitoring & Time Tracking App..."

# Check if Python 3 is available
if ! command -v /usr/bin/python3 &> /dev/null; then
    echo "Error: System Python 3 is not available at /usr/bin/python3"
    exit 1
fi

# Check if tkinter is available
echo "Checking tkinter availability..."
if ! /usr/bin/python3 -c "import tkinter" 2>/dev/null; then
    echo "Error: tkinter is not available in system Python3"
    echo "Please install tkinter for system Python3"
    exit 1
fi

# Check if required packages are installed for system Python3
echo "Checking dependencies..."
/usr/bin/python3 -c "
import sys
required_packages = ['requests', 'PIL', 'psutil', 'pyautogui', 'pynput', 'dotenv', 'cryptography', 'keyring']
missing = []
for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)
if missing:
    print(f'Missing packages: {missing}')
    print('Installing missing packages...')
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user'] + missing)
else:
    print('✅ All dependencies are installed')
"

# Create config.py if it doesn't exist
if [ ! -f "config.py" ]; then
    echo "Creating config.py from example..."
    cp config.example.py config.py
    echo "Please review and update config.py before running the app."
fi

# Run the application with system Python3
echo "Launching application..."
export TK_SILENCE_DEPRECATION=1
/usr/bin/python3 main.py

echo "Application closed." 