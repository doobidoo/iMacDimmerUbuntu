# iMac Dimmer Ubuntu v1.6.0

**🚀 Advanced ESP32-C3 brightness control system with zero-maintenance dynamic IP discovery**

A comprehensive solution for controlling iMac display brightness using ESP32-C3 with automatic network adaptation, multiple communication methods, and robust failover mechanisms.

## 🏗️ System Architecture

```
┌─────────────────┐    WiFi     ┌──────────────────┐    PWM    ┌─────────────────┐
│   Ubuntu PC     │◄──────────►│  ESP32-C3 Mini   │◄─────────►│  iMac Display   │
│                 │             │                  │           │   Brightness    │
│ • Python Script │             │ • Web Interface  │           │    Control      │
│ • Keyboard      │             │ • HTTP API       │           │                 │
│ • Systemd       │             │ • mDNS Service   │           │                 │
│ • Web Browser   │             │ • Version Track  │           │                 │
└─────────────────┘             └──────────────────┘           └─────────────────┘
         │                               │
         │ HTTP API                      │ imacdimmer.local
         │ imacdisplay.py -s 70         │ http://imacdimmer.local
         │                               │
         └───────────────────────────────┘
```

## ✨ Key Features

### 🌐 **Dynamic Network Discovery**
- **mDNS hostname**: Access via `imacdimmer.local` - no IP needed
- **Automatic IP discovery**: Finds ESP32 even when network changes
- **Multi-layer fallback**: MAC detection, network scanning, cached addresses
- **Zero maintenance**: Works across router reboots and DHCP changes

### 🔗 **Dual Communication Methods**
- **HTTP-based control**: Robust web API with `/serial` endpoint
- **Modern web interface**: Real-time brightness control with presets
- **ESP32-C3 compatible**: Bypasses bootloader serial communication issues
- **Version tracking**: Firmware verification and update management

### 🎛️ **Complete System Integration**
- **Keyboard shortcuts**: System-wide hotkey support
- **Systemd service**: Background brightness restoration
- **Timer automation**: Scheduled brightness adjustments
- **Configuration caching**: Performance optimization with smart defaults

## 🔧 Hardware Requirements

<div align="center">
  <img src="images/esp32-c3-supermini.webp" alt="ESP32-C3 SuperMini Board" width="400"/>
  <p><em>ESP32-C3 SuperMini Development Board</em></p>
</div>

### **Required Components:**
- **ESP32-C3 SuperMini Board** (shown above)
- **GPIO3**: PWM output for brightness control
- **GPIO8**: Status LED
- **WiFi connection**: For web interface and mDNS

### **Board Specifications:**
- **Microcontroller**: ESP32-C3 (160MHz, 320KB RAM)
- **Flash Memory**: 4MB
- **WiFi**: 802.11 b/g/n (2.4GHz)
- **USB**: USB-C for programming and power
- **Size**: Ultra-compact form factor
- **GPIO**: 13 digital I/O pins

## 📂 Project Structure

```
iMacDimmerUbuntu/
├── src/
│   └── main.cpp                    # ESP32 firmware v1.6.0
├── scripts/
│   ├── imacdisplay_http.py        # Smart discovery Python script
│   ├── ping_test.py               # Network connectivity tests
│   └── hybrid_test.py             # Communication diagnostics
├── systemd/
│   └── brightness.service         # System service configuration
├── DYNAMIC_IP_SOLUTION.md         # Detailed technical documentation
├── final_install.sh               # Automated installation script
├── platformio.ini                 # PlatformIO build configuration
└── README.md                      # This file
```

## 🚀 Quick Start

### **One-Command Installation**

```bash
# Clone and install everything automatically
git clone https://github.com/doobidoo/iMacDimmerUbuntu.git
cd iMacDimmerUbuntu
./final_install.sh
```

The installation script will:
- ✅ Test ESP32 connectivity
- ✅ Configure optimal communication method
- ✅ Install system scripts with dynamic discovery
- ✅ Set up systemd service
- ✅ Verify complete functionality

## 📋 Manual Installation Steps

### 1. **Flash ESP32 Firmware**

```bash
# Build and upload v1.6.0 firmware
~/.platformio/penv/bin/platformio run --target upload
```

### 2. **Configure Network Access**

```bash
# Option A: Use mDNS hostname (recommended)
python3 scripts/imacdisplay_http.py --ip imacdimmer.local

# Option B: Auto-discover ESP32
python3 scripts/imacdisplay_http.py --discover

# Option C: Manual IP configuration
python3 scripts/imacdisplay_http.py --ip 192.168.1.100
```

### 3. **Install System Integration**

```bash
# Install system script
sudo cp scripts/imacdisplay_http.py /usr/local/bin/imacdisplay.py
sudo chmod +x /usr/local/bin/imacdisplay.py

# Install and start service
sudo cp systemd/brightness.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable brightness.service
sudo systemctl start brightness.service
```

## 🎯 Usage Examples

### **Command Line Interface**

```bash
# Brightness control
imacdisplay.py -s 70          # Set to 70%
imacdisplay.py -g             # Get current brightness
imacdisplay.py -i 10          # Increase by 10%
imacdisplay.py -d 10          # Decrease by 10%

# System diagnostics
imacdisplay.py -v             # Get firmware version
imacdisplay.py --ping         # Test ESP32 connectivity
imacdisplay.py --discover     # Find and save ESP32 location

# Network configuration
imacdisplay.py --ip imacdimmer.local    # Use hostname
imacdisplay.py --ip 192.168.1.27        # Use specific IP
```

### **Web Interface**

<div align="center">
  <table>
    <tr>
      <td><strong>🌐 Access Methods</strong></td>
      <td><strong>🎛️ Interface Features</strong></td>
    </tr>
    <tr>
      <td>
        • <code>http://imacdimmer.local</code> (recommended)<br>
        • <code>http://[ESP32-IP-ADDRESS]</code><br>
        • Auto-discovery enabled
      </td>
      <td>
        • 🎚️ Real-time brightness slider<br>
        • 🎯 Quick preset buttons (5%, 20%, 50%, 70%, 100%)<br>
        • 📊 System information display<br>
        • 📡 WiFi status and signal strength<br>
        • 🔄 Firmware version verification
      </td>
    </tr>
  </table>
</div>

### **Keyboard Shortcuts**

Configure in your desktop environment:

| Action | Command |
|--------|---------|
| **Brightness Up** | `imacdisplay.py -i 10` |
| **Brightness Down** | `imacdisplay.py -d 10` |
| **Preset Dim** | `imacdisplay.py -s 20` |
| **Preset Bright** | `imacdisplay.py -s 80` |

## 🔧 Configuration

### **WiFi Credentials**

Edit `src/main.cpp` before flashing:

```cpp
const char* ssid = "YourWiFiNetwork";
const char* password = "YourWiFiPassword";
```

### **Network Discovery Methods**

The system automatically tries (in order):

1. **mDNS Hostname**: `imacdimmer.local`
2. **Cached Address**: Last known working connection
3. **ARP Table Scan**: ESP32 MAC address detection
4. **Network Discovery**: Intelligent local network scanning
5. **Manual Configuration**: User-specified addresses

## 🛡️ Safety & Reliability Features

### **Hardware Safety**
- ✅ Minimum brightness enforcement (5%)
- ✅ Safe startup brightness (70%)
- ✅ PWM output protection
- ✅ Status LED feedback

### **Network Resilience**
- ✅ Automatic WiFi reconnection
- ✅ mDNS service registration
- ✅ HTTP communication redundancy
- ✅ Configuration caching and recovery

### **System Integration**
- ✅ Systemd service with auto-restart
- ✅ Background brightness restoration
- ✅ Non-blocking communication timeouts
- ✅ Graceful degradation on failures

## 🔍 Troubleshooting

### **Network Connectivity**

```bash
# Test ESP32 discovery
python3 scripts/hybrid_test.py

# Test hostname resolution
ping imacdimmer.local

# Manual connectivity test
curl http://imacdimmer.local/version
```

### **System Service**

```bash
# Check service status
systemctl status brightness.service

# View service logs
journalctl -u brightness.service -f

# Restart service
sudo systemctl restart brightness.service
```

### **Firmware Issues**

```bash
# Check web interface
curl http://imacdimmer.local/version

# Verify firmware version
python3 scripts/imacdisplay_http.py -v

# Re-flash firmware if needed
~/.platformio/penv/bin/platformio run --target upload
```

## 🌐 Network Compatibility

### ✅ **Fully Compatible**
- Home networks with standard routers
- Networks with mDNS/Bonjour support
- Standard DHCP configurations
- Multi-VLAN setups with local access

### ⚠️ **Limited Compatibility**
- Corporate networks with mDNS blocked
- Networks with restricted ARP access
- Very strict firewall configurations

**Workaround**: Use manual IP configuration:
```bash
imacdisplay.py --ip [actual-esp32-ip]
```

## 🚀 Advanced Features

### **API Endpoints**

The ESP32 provides a RESTful API:

```bash
# Version information
GET /version

# WiFi and system status
GET /wifistatus

# Serial command emulation
GET /serial?cmd=version
GET /serial?cmd=get
GET /serial?cmd=50

# LED control
GET /led?pin=8&state=1

# Direct brightness control
GET /brightness?level=128
```

### **Configuration Management**

Settings are automatically cached in `~/.config/imacdisplay.conf`:

```json
{
  "esp32_ip": "imacdimmer.local",
  "last_brightness": 70
}
```

## 📊 Technical Specifications

| Component | Specification |
|-----------|---------------|
| **Microcontroller** | ESP32-C3 (160MHz, 320KB RAM) |
| **WiFi** | 802.11 b/g/n, 2.4GHz |
| **PWM Output** | GPIO3, 10kHz frequency, 8-bit resolution |
| **Communication** | HTTP/1.1, mDNS, WebSocket ready |
| **Power** | USB-C, 3.3V operation |
| **Flash Memory** | 4MB with OTA support |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with `python3 scripts/hybrid_test.py`
5. Submit a pull request

## 📄 License

This project is open source. See the repository for license details.

## 🎉 Acknowledgments

- **ESP32 Community**: For comprehensive hardware support
- **PlatformIO**: For excellent development environment
- **mDNS/Avahi**: For network service discovery

---

**🔗 Links**
- **Repository**: [github.com/doobidoo/iMacDimmerUbuntu](https://github.com/doobidoo/iMacDimmerUbuntu)
- **Technical Details**: [DYNAMIC_IP_SOLUTION.md](DYNAMIC_IP_SOLUTION.md)
- **Latest Release**: [v1.6.0](https://github.com/doobidoo/iMacDimmerUbuntu/releases/tag/v1.6.0)

*Built with ❤️ for the ESP32 and open source communities*