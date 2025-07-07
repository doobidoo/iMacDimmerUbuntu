#!/bin/bash

# iMac Dimmer Ubuntu Installation Script

set -e

echo "🔧 iMac Dimmer Ubuntu Installation"
echo "=================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   exit 1
fi

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Project directory: $PROJECT_DIR"

# Install Python script
echo "📦 Installing Python control script..."
sudo cp "$PROJECT_DIR/scripts/imacdisplay.py" /usr/local/bin/
sudo chmod +x /usr/local/bin/imacdisplay.py
echo "✅ Python script installed to /usr/local/bin/imacdisplay.py"

# Install systemd service
echo "🔧 Installing systemd service..."
sudo cp "$PROJECT_DIR/systemd/brightness.service" /etc/systemd/system/
sudo systemctl daemon-reload
echo "✅ Systemd service installed"

# Enable and start service
echo "🚀 Enabling and starting brightness service..."
sudo systemctl enable brightness.service
sudo systemctl start brightness.service
echo "✅ Service enabled and started"

# Check service status
echo "📊 Service status:"
sudo systemctl status brightness.service --no-pager -l

# Test Python script
echo "🧪 Testing Python script..."
if /usr/local/bin/imacdisplay.py -g; then
    echo "✅ Python script test passed"
else
    echo "⚠️  Python script test failed - check ESP32 connection"
fi

# Create user config directory
echo "📁 Creating user config directory..."
mkdir -p ~/.config
echo "✅ Config directory ready"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Flash ESP32 firmware: pio run --target upload"
echo "2. Configure keyboard shortcuts to use: imacdisplay.py -i 10 / imacdisplay.py -d 10"
echo "3. Access web interface at ESP32's IP address"
echo ""
echo "Commands:"
echo "  Get brightness: imacdisplay.py -g"
echo "  Set brightness: imacdisplay.py -s 50"
echo "  Increase: imacdisplay.py -i 10"
echo "  Decrease: imacdisplay.py -d 10"