#!/bin/bash

echo "🌙 Installing Auto-Dimmer System"
echo "================================"

# Install required packages
echo "📦 Installing required packages..."
sudo apt update
sudo apt install -y xprintidle

# Copy auto-dimmer script
echo "📝 Installing auto-dimmer script..."
sudo cp scripts/auto_dimmer.py /usr/local/bin/
sudo chmod +x /usr/local/bin/auto_dimmer.py

# Install systemd service
echo "🔧 Installing systemd service..."
sudo cp systemd/auto-dimmer.service /etc/systemd/system/
sudo systemctl daemon-reload

# Test the auto-dimmer
echo "🧪 Testing auto-dimmer..."
echo "Current system status:"
python3 scripts/auto_dimmer.py --status

echo ""
echo "Testing idle detection:"
python3 scripts/auto_dimmer.py --test

echo ""
echo "💾 Saving default configuration..."
python3 scripts/auto_dimmer.py --config

echo ""
echo "🎯 Auto-dimmer installation options:"
echo ""
echo "1. Enable auto-dimmer service (starts automatically):"
echo "   sudo systemctl enable auto-dimmer.service"
echo "   sudo systemctl start auto-dimmer.service"
echo ""
echo "2. Run auto-dimmer manually:"
echo "   auto_dimmer.py --minutes 10 --level 5"
echo ""
echo "3. Test auto-dimmer (safe mode):"
echo "   auto_dimmer.py --test"
echo ""
echo "Configuration options:"
echo "  --minutes N    : Idle minutes before dimming (default: 10)"
echo "  --level N      : Brightness level when dimmed (default: 5%)"
echo "  --interval N   : Check interval in seconds (default: 30)"
echo ""
echo "✅ Auto-dimmer installation complete!"