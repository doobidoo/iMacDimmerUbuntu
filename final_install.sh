#!/bin/bash

echo "🚀 iMac Dimmer Final Installation"
echo "=================================="
echo ""

# Check if ESP32 is accessible
echo "🔍 Testing ESP32 connectivity..."

# Test hostname first
if ping -c 1 imacdimmer.local >/dev/null 2>&1; then
    echo "✅ mDNS hostname working: imacdimmer.local"
    ESP32_ADDRESS="imacdimmer.local"
else
    echo "⚠️  mDNS hostname not accessible, trying IP discovery..."
    
    # Try current IP
    if curl -s --connect-timeout 3 "http://10.0.1.27/version" >/dev/null 2>&1; then
        echo "✅ ESP32 found at: 10.0.1.27"
        ESP32_ADDRESS="10.0.1.27"
    else
        echo "❌ Could not find ESP32. Please check:"
        echo "   - ESP32 is powered on"
        echo "   - WiFi connection is working"
        echo "   - IP address hasn't changed"
        exit 1
    fi
fi

# Configure Python script
echo "📍 Configuring ESP32 address..."
python3 scripts/imacdisplay_http.py --ip "$ESP32_ADDRESS"

# Install system script
echo "📦 Installing system script..."
sudo cp scripts/imacdisplay_http.py /usr/local/bin/imacdisplay.py
sudo chmod +x /usr/local/bin/imacdisplay.py

# Test system installation
echo "🧪 Testing system installation..."
if /usr/local/bin/imacdisplay.py -v >/dev/null 2>&1; then
    echo "✅ System script working"
else
    echo "❌ System script test failed"
    exit 1
fi

# Update systemd service to use new script
echo "🔧 Updating systemd service..."
sudo systemctl restart brightness.service
sleep 2

if systemctl is-active --quiet brightness.service; then
    echo "✅ Systemd service running"
else
    echo "⚠️  Systemd service not running (check with: systemctl status brightness.service)"
fi

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "📋 Summary:"
echo "- ESP32 firmware: 1.6.0-dynamic-discovery"
echo "- ESP32 address: $ESP32_ADDRESS"
echo "- Communication: HTTP with dynamic discovery"
echo "- Web interface: http://$ESP32_ADDRESS"
echo "- System script: /usr/local/bin/imacdisplay.py"
echo ""
echo "🎯 Features Enabled:"
echo "✅ Dynamic IP discovery (handles IP changes automatically)"
echo "✅ mDNS hostname support (imacdimmer.local)"
echo "✅ HTTP-based communication (bypasses serial issues)"
echo "✅ Web interface for manual control"
echo "✅ System integration for automation"
echo ""
echo "🔧 Usage Examples:"
echo "# Manual brightness control"
echo "imacdisplay.py -s 70    # Set to 70%"
echo "imacdisplay.py -g       # Get current brightness"
echo "imacdisplay.py -i 10    # Increase by 10%"
echo "imacdisplay.py -d 10    # Decrease by 10%"
echo ""
echo "# System integration"
echo "systemctl status brightness.service  # Check service status"
echo ""
echo "# Keyboard shortcuts (configure in your desktop environment):"
echo "Brightness Up:   imacdisplay.py -i 10"
echo "Brightness Down: imacdisplay.py -d 10"
echo ""
echo "🌐 Web interface: http://$ESP32_ADDRESS"
echo ""
echo "🌙 Auto-Dimmer Installation:"
echo "To enable automatic brightness dimming after idle time:"
echo "1. Run: ./install_auto_dimmer.sh"
echo "2. Test: python3 scripts/test_auto_dimmer.py"
echo "3. Configure: auto_dimmer.py --minutes 10 --level 5 --config"
echo "4. Enable service: sudo systemctl enable auto-dimmer.service"
echo ""
echo "💡 The system now automatically handles IP address changes!"
echo "   No manual reconfiguration needed when network changes."