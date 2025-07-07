# iMac Dimmer Ubuntu

ESP32-C3 based brightness control system for iMac displays with both web interface and serial communication.

## Features

- **Web Interface**: Modern web-based brightness control with real-time updates
- **Serial Communication**: Python script integration for system-level control
- **Keyboard Shortcuts**: System-wide brightness control via hotkeys
- **Auto-dimming Timer**: Scheduled brightness adjustments
- **Systemd Service**: Background service for brightness restoration

## Hardware

- ESP32-C3 SuperMini Board
- Connected to iMac display brightness control
- PWM output on GPIO3
- Status LED on GPIO8

## Project Structure

```
├── src/
│   └── main.cpp              # ESP32 firmware (web + serial)
├── scripts/
│   ├── imacdisplay.py        # Python control script
│   └── test_serial.py        # Serial communication test
├── systemd/
│   └── brightness.service    # Systemd service file
├── platformio.ini            # PlatformIO configuration
└── README.md                 # This file
```

## Installation

### 1. Flash ESP32 Firmware

```bash
# Build and upload firmware
cd /home/hkr/Documents/PlatformIO/Projects/iMacDimmerUbuntu
pio run --target upload
```

### 2. Install Python Script

```bash
# Copy script to system location
sudo cp scripts/imacdisplay.py /usr/local/bin/
sudo chmod +x /usr/local/bin/imacdisplay.py
```

### 3. Install Systemd Service

```bash
# Copy and enable service
sudo cp systemd/brightness.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable brightness.service
sudo systemctl start brightness.service
```

## Usage

### Web Interface

1. Connect ESP32 to WiFi (automatic on boot)
2. Access web interface at ESP32's IP address
3. Use slider or preset buttons to control brightness

### Command Line

```bash
# Get current brightness
imacdisplay.py -g

# Set brightness to 50%
imacdisplay.py -s 50

# Increase brightness by 10%
imacdisplay.py -i 10

# Decrease brightness by 10%
imacdisplay.py -d 10
```

### Keyboard Shortcuts

Configure keyboard shortcuts in your desktop environment to call:
- `imacdisplay.py -i 10` (brightness up)
- `imacdisplay.py -d 10` (brightness down)

## Configuration

### WiFi Settings
Edit `src/main.cpp` to change WiFi credentials:
```cpp
const char* ssid = "YourWiFiNetwork";
const char* password = "YourWiFiPassword";
```

### Serial Port
The script auto-detects the ESP32 device. To force a specific port:
```bash
imacdisplay.py -p /dev/ttyACM0 -s 50
```

## Safety Features

- Minimum brightness warning at 5%
- Safe default brightness (70%) on startup
- Graceful fallback to serial-only mode if WiFi fails
- Automatic WiFi reconnection

## Troubleshooting

### Serial Communication Issues
1. Check if ESP32 is connected: `ls /dev/ttyACM*`
2. Test with: `python3 scripts/test_serial.py`
3. Kill conflicting processes: `sudo lsof /dev/ttyACM0`

### Web Interface Not Working
1. Check ESP32 serial output for IP address
2. Verify WiFi credentials in firmware
3. Ensure firewall allows port 80

### Service Not Starting
```bash
# Check service status
systemctl status brightness.service

# View logs
journalctl -u brightness.service
```

## Development

### Building
```bash
pio run
```

### Monitoring
```bash
pio device monitor
```

### Testing
```bash
# Test serial communication
python3 scripts/test_serial.py

# Test Python script
python3 scripts/imacdisplay.py -g
```