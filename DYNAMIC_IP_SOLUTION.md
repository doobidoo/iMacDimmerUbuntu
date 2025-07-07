# Dynamic IP Address Solution

## Problem
ESP32 devices often get different IP addresses when they reconnect to WiFi, breaking brightness control automation.

## Our Multi-Layer Solution

### 1. **mDNS Hostname** (Primary Method)
- ESP32 registers as `imacdimmer.local`
- Works automatically on most networks
- No IP address needed - uses hostname resolution

### 2. **MAC Address Detection** (Fallback #1)
- Scans ARP table for Espressif device MAC addresses
- Identifies ESP32 by its unique hardware signature
- Works even when IP changes

### 3. **Network Discovery** (Fallback #2)
- Intelligent network scanning
- Only scans local networks (not internet)
- Checks common device IP ranges

### 4. **Configuration Cache** (Performance)
- Remembers last working connection method
- Tries known-good address first
- Auto-updates when device moves

## Implementation Details

### ESP32 Firmware Features:
```cpp
// mDNS registration
MDNS.begin("imacdimmer");
MDNS.addService("http", "tcp", 80);
```

### Python Script Features:
```python
# Priority order:
1. Try imacdimmer.local (mDNS)
2. Try cached IP address
3. Scan ARP table for ESP32 MAC
4. Network discovery scan
5. Update cache with working method
```

## Usage Examples

### Automatic Discovery
```bash
# Script automatically finds ESP32, no setup needed
imacdisplay.py -s 70

# Force discovery and save new location
imacdisplay.py --discover
```

### Manual Configuration (if needed)
```bash
# Set specific IP if discovery fails
imacdisplay.py --ip 192.168.1.100

# Use hostname (recommended)
imacdisplay.py --ip imacdimmer.local
```

## Network Compatibility

### ✅ **Works Best On:**
- Home networks with mDNS support
- Networks where ARP table is accessible
- Standard DHCP configurations

### ⚠️ **May Need Manual Setup:**
- Corporate networks with mDNS blocked
- Networks with restricted ARP access
- Very strict firewall configurations

### 🔧 **Corporate Network Workaround:**
```bash
# Find ESP32 IP manually, then:
imacdisplay.py --ip <actual_ip_address>
```

## Benefits

1. **Zero Configuration**: Works out of the box in most cases
2. **Robust Fallbacks**: Multiple discovery methods
3. **Performance**: Caches working methods
4. **Flexibility**: Manual override available
5. **Future Proof**: Adapts to network changes

## Testing

```bash
# Test all discovery methods
python3 scripts/hybrid_test.py

# Test hostname resolution
ping imacdimmer.local

# Test current configuration
imacdisplay.py -v
```

This solution ensures your brightness controls keep working even when:
- Router reboots and reassigns IPs
- Network configuration changes
- You move to different networks
- DHCP lease expires and renews