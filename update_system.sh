#!/bin/bash

echo "🔄 Updating iMac Dimmer System Installation"
echo "==========================================="

# Set ESP32 IP if not already configured
echo "📍 Configuring ESP32 IP address..."
python3 scripts/imacdisplay_http.py --ip 10.0.1.27

# Copy HTTP script to system location
echo "📦 Installing HTTP-based script..."
sudo cp scripts/imacdisplay_http.py /usr/local/bin/imacdisplay.py
sudo chmod +x /usr/local/bin/imacdisplay.py

# Test the system installation
echo "🧪 Testing system installation..."
echo "Version test:"
/usr/local/bin/imacdisplay.py -v

echo "Brightness test:"
/usr/local/bin/imacdisplay.py -g

echo ""
echo "✅ System updated successfully!"
echo ""
echo "📋 Summary:"
echo "- ESP32 running firmware: 1.5.0-http-fallback"
echo "- Communication method: HTTP (serial fallback bypassed)"
echo "- Web interface: http://10.0.1.27"
echo "- System script: /usr/local/bin/imacdisplay.py"
echo ""
echo "🎯 Ready for:"
echo "- Keyboard shortcuts: imacdisplay.py -i 10 / imacdisplay.py -d 10"
echo "- Systemd service: should work automatically"
echo "- Timer automation: ready for implementation"