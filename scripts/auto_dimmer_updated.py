#!/usr/bin/env python3
"""
Automatic brightness dimmer with idle detection
Monitors user activity and dims display after configured idle time
"""

import time
import subprocess
import json
import argparse
import sys
import signal
from pathlib import Path
from datetime import datetime, timedelta

# Import our brightness control
# Try multiple import methods to handle different installation scenarios
try:
    # First try direct import (when both scripts are in same directory)
    from imacdisplay_http import http_request, save_config, load_config
except ImportError:
    try:
        # Try importing from system location
        sys.path.insert(0, '/usr/local/bin')
        from imacdisplay import http_request, save_config, load_config
    except ImportError:
        # Try importing from parent directory (development mode)
        sys.path.append(str(Path(__file__).parent))
        try:
            from imacdisplay_http import http_request, save_config, load_config
        except ImportError:
            print("Error: Could not import brightness control module")
            print("Make sure imacdisplay.py is installed in /usr/local/bin/")
            sys.exit(1)

class AutoDimmer:
    def __init__(self, idle_minutes=10, dim_level=0, check_interval=30):
        self.idle_minutes = idle_minutes
        self.dim_level = dim_level  # Brightness level when dimmed (can be 0 for complete black)
        self.check_interval = check_interval  # How often to check idle time (seconds)
        
        self.original_brightness = None
        self.is_dimmed = False
        self.running = True
        
        # Load configuration
        self.config_file = Path.home() / '.config' / 'auto_dimmer.json'
        self.load_dimmer_config()
        
    def load_dimmer_config(self):
        """Load auto-dimmer configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                self.idle_minutes = config.get('idle_minutes', self.idle_minutes)
                self.dim_level = config.get('dim_level', self.dim_level)
                self.check_interval = config.get('check_interval', self.check_interval)
                print(f"📁 Loaded config: {self.idle_minutes}min idle, dim to {self.dim_level}%")
        except Exception as e:
            print(f"⚠️  Config load error: {e}, using defaults")
    
    def save_dimmer_config(self):
        """Save auto-dimmer configuration"""
        try:
            config = {
                'idle_minutes': self.idle_minutes,
                'dim_level': self.dim_level,
                'check_interval': self.check_interval,
                'last_updated': datetime.now().isoformat()
            }
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠️  Config save error: {e}")
    
    def get_idle_time_seconds(self):
        """Get system idle time in seconds using multiple methods"""
        
        # Method 1: Try xprintidle (most accurate)
        try:
            result = subprocess.run(['xprintidle'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                idle_ms = int(result.stdout.strip())
                return idle_ms / 1000.0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ValueError):
            pass
        
        # Method 2: Try using who command (last user activity)
        try:
            result = subprocess.run(['who', '-u'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    # Parse the idle time from who output
                    for line in lines:
                        if 'old' in line:
                            # Extract time info and calculate idle time
                            parts = line.split()
                            if len(parts) >= 5:
                                idle_indicator = parts[4]
                                if ':' in idle_indicator:
                                    # Format like "01:23" means 1 hour 23 minutes idle
                                    hours, minutes = map(int, idle_indicator.split(':'))
                                    return (hours * 3600) + (minutes * 60)
                                elif idle_indicator.isdigit():
                                    # Number of minutes
                                    return int(idle_indicator) * 60
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
            pass
        
        # Method 3: Check X11 screen saver status
        try:
            result = subprocess.run(['xset', 'q'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Screen Saver' in line and 'disabled' not in line.lower():
                        # Screen saver is active, assume system is idle
                        return 999999  # Very high value to indicate idle
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
        
        # Method 4: Fallback - check if screen is locked
        try:
            # Check if gnome-screensaver is active
            result = subprocess.run(['gnome-screensaver-command', '--query'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'active' in result.stdout.lower():
                return 999999  # Screen is locked, consider as idle
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # If all methods fail, return 0 (not idle)
        print("⚠️  Could not determine idle time, assuming active")
        return 0
    
    def get_current_brightness(self):
        """Get current brightness from ESP32"""
        try:
            response = http_request("/serial", {"cmd": "get"})
            if response and "Current brightness:" in response:
                # Extract brightness percentage from response
                import re
                match = re.search(r'(\d+)%', response)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"⚠️  Error getting brightness: {e}")
        
        # Fallback to cached value
        config = load_config()
        return config.get('last_brightness', 70)
    
    def set_brightness(self, level):
        """Set brightness level"""
        try:
            response = http_request("/serial", {"cmd": str(level)})
            if response and "Brightness set to" in response:
                print(f"💡 Brightness set to {level}%")
                return True
            else:
                print(f"❌ Failed to set brightness: {response}")
                return False
        except Exception as e:
            print(f"❌ Error setting brightness: {e}")
            return False
    
    def dim_display(self):
        """Dim the display to minimum level"""
        if not self.is_dimmed:
            self.original_brightness = self.get_current_brightness()
            print(f"😴 Dimming display: {self.original_brightness}% → {self.dim_level}%")
            
            if self.set_brightness(self.dim_level):
                self.is_dimmed = True
                return True
        return False
    
    def restore_brightness(self):
        """Restore original brightness"""
        if self.is_dimmed and self.original_brightness is not None:
            # Safety feature: if original brightness was 0%, restore to 10% instead
            restore_level = self.original_brightness
            if self.original_brightness == 0:
                restore_level = 10
                print(f"🔆 Safety: Restoring to 10% instead of 0%")
            
            print(f"😊 Restoring brightness: {self.dim_level}% → {restore_level}%")
            
            if self.set_brightness(restore_level):
                self.is_dimmed = False
                self.original_brightness = None
                return True
        return False
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.running = False
        if self.is_dimmed:
            print("🔄 Restoring brightness before exit...")
            self.restore_brightness()
        sys.exit(0)
    
    def run_daemon(self):
        """Main daemon loop"""
        print(f"🚀 Auto-dimmer started")
        print(f"⏱️  Idle timeout: {self.idle_minutes} minutes")
        print(f"🌙 Dim level: {self.dim_level}%")
        print(f"🔄 Check interval: {self.check_interval} seconds")
        print(f"💾 Config file: {self.config_file}")
        print("📡 Testing ESP32 connection...")
        
        # Test ESP32 connection
        current_brightness = self.get_current_brightness()
        print(f"✅ ESP32 connected, current brightness: {current_brightness}%")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        idle_threshold_seconds = self.idle_minutes * 60
        last_activity_time = time.time()
        
        while self.running:
            try:
                current_idle = self.get_idle_time_seconds()
                current_time = time.time()
                
                print(f"🕐 {datetime.now().strftime('%H:%M:%S')} - "
                      f"Idle: {current_idle:.0f}s, Threshold: {idle_threshold_seconds}s, "
                      f"Dimmed: {self.is_dimmed}")
                
                # Safety check: if brightness is 0% and user is active, restore to 10%
                if current_idle < 60:  # User is active
                    if self.is_dimmed:
                        print("👋 User activity detected!")
                        self.restore_brightness()
                    else:
                        # Check if screen is at 0% even when not dimmed by auto-dimmer
                        current_brightness = self.get_current_brightness()
                        if current_brightness == 0:
                            print("🔆 Safety: Screen at 0%, restoring to 10%")
                            self.set_brightness(10)
                    last_activity_time = current_time
                
                # Check if we should dim (idle time exceeded threshold)
                elif current_idle > idle_threshold_seconds and not self.is_dimmed:
                    print(f"💤 System idle for {current_idle/60:.1f} minutes")
                    self.dim_display()
                
                # Update last activity time if not idle
                if current_idle < 60:
                    last_activity_time = current_time
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(self.check_interval)
        
        print("👋 Auto-dimmer stopped")

def main():
    parser = argparse.ArgumentParser(description='Automatic brightness dimmer with idle detection')
    parser.add_argument('-m', '--minutes', type=float, default=10, 
                       help='Minutes of idle time before dimming (default: 10)')
    parser.add_argument('-l', '--level', type=int, default=0,
                       help='Brightness level when dimmed (default: 0%%)')
    parser.add_argument('-i', '--interval', type=int, default=30,
                       help='Check interval in seconds (default: 30)')
    parser.add_argument('-t', '--test', action='store_true',
                       help='Test idle detection and exit')
    parser.add_argument('-s', '--status', action='store_true',
                       help='Show current status and exit')
    parser.add_argument('--config', action='store_true',
                       help='Save current settings to config file')
    
    args = parser.parse_args()
    
    dimmer = AutoDimmer(args.minutes, args.level, args.interval)
    
    if args.config:
        dimmer.save_dimmer_config()
        print(f"💾 Configuration saved to {dimmer.config_file}")
        return
    
    if args.status:
        idle_time = dimmer.get_idle_time_seconds()
        brightness = dimmer.get_current_brightness()
        print(f"📊 Status Report:")
        print(f"   Current idle time: {idle_time:.0f} seconds ({idle_time/60:.1f} minutes)")
        print(f"   Current brightness: {brightness}%")
        print(f"   Idle threshold: {dimmer.idle_minutes} minutes")
        print(f"   Dim level: {dimmer.dim_level}%")
        return
    
    if args.test:
        print("🧪 Testing idle detection...")
        for i in range(5):
            idle_time = dimmer.get_idle_time_seconds()
            print(f"   Test {i+1}: Idle time = {idle_time:.0f} seconds ({idle_time/60:.1f} minutes)")
            time.sleep(2)
        return
    
    # Run the daemon
    try:
        dimmer.run_daemon()
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()