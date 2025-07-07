#!/usr/bin/env python3
import serial
import argparse
import sys
import time
from pathlib import Path
import json
import glob
import traceback

def get_config_file():
    return Path.home() / '.config' / 'imacdisplay.conf'

def find_esp32_device():
    """Try to automatically detect the ESP32-C3 device port."""
    # Common ESP32 device patterns
    patterns = ['/dev/ttyACM*', '/dev/ttyUSB*']
    devices = []

    for pattern in patterns:
        devices.extend(glob.glob(pattern))

    # Prioritize ACM devices first (ESP32-C3), then USB devices (older ESP32)
    for dev in sorted(devices):
        if 'ACM' in dev:
            return dev
    for dev in devices:
        return dev

    # If no devices found, return the default
    return '/dev/ttyACM0'  # Default to ACM for ESP32-C3

def load_config():
    config_file = get_config_file()
    try:
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)

            # Check if the configured port exists, otherwise try to find it
            if not Path(config['port']).exists():
                print(f"Configured port {config['port']} not found, searching for ESP32...")
                config['port'] = find_esp32_device()

            return config
    except Exception as e:
        print(f"Error loading config: {e}")

    # Default configuration with auto-detection
    default_port = find_esp32_device()
    print(f"Using auto-detected port: {default_port}")
    return {'port': default_port, 'last_brightness': 70}

def save_config(brightness=None, port=None):
    config_file = get_config_file()
    config = load_config()

    if brightness is not None:
        config['last_brightness'] = brightness

    if port is not None:
        config['port'] = port

    try:
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Error saving config: {e}")

def setup_serial(port=None, exclusive=True):
    if port is None:
        config = load_config()
        port = config['port']

    try:
        # Close any existing port first
        try:
            ser.close()
        except:
            pass
        ser = serial.Serial(port, 115200, timeout=2, exclusive=exclusive, 
                          dsrdtr=False, rtscts=False)
        time.sleep(2)  # Wait for ESP32 to be ready after potential reset
        return ser
    except serial.SerialException as e:
        # If exclusive lock failed, try non-exclusive if requested
        if "Could not exclusively lock" in str(e) and exclusive:
            print("Port is in use, trying non-exclusive access...")
            return setup_serial(port, exclusive=False)
        else:
            print(f"Error: Could not open serial port {port}")
            print(f"Details: {e}")

            # Try to auto-detect if the specified port failed
            if port != '/dev/ttyACM0' and port != '/dev/ttyUSB0':
                print("Trying to auto-detect ESP32 device...")
                new_port = find_esp32_device()
                if new_port and new_port != port:
                    print(f"Found device at {new_port}, trying that instead.")
                    save_config(port=new_port)
                    return setup_serial(new_port, exclusive=exclusive)

            return None

        return None

def set_brightness(ser, value):
    """Set brightness with safety limits - reads response"""
    try:
        value = max(5, min(100, value)) # Keep safety limits

        print(f"Sending brightness command: {value}")
        command = f"{value}\n"
        ser.write(command.encode())
        ser.flush() # Ensure data is sent

        # --- Add code to read the response ---
        # Wait briefly for the response (adjust timeout if needed)
        # ser.timeout = 1 # Set read timeout (optional, uses the default from setup_serial if not set)
        response = ser.readline().decode().strip()
        if response:
            print(f"Received response: {response}")
        else:
            print("Warning: No response received from ESP32 (timeout?).")
        # --- End added code ---

        print(f"Set brightness to {value}%")
        save_config(value)
        return value
    except Exception as e:
        print(f"Error setting brightness: {e}")
        traceback.print_exc() # Print detailed traceback
        return None
    # finally: # No longer needed as readline handles waiting
    #     pass

def get_brightness():
    """Get last saved brightness value"""
    config = load_config()
    return config.get('last_brightness', 70)

def main():
    parser = argparse.ArgumentParser(description='iMac Display Brightness Control')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--set', type=int, help='Set brightness (5-100)')
    group.add_argument('-g', '--get', action='store_true', help='Get current brightness')
    group.add_argument('-i', '--increment', type=int, help='Increase brightness by amount')
    group.add_argument('-d', '--decrement', type=int, help='Decrease brightness by amount')
    group.add_argument('-v', '--version', action='store_true', help='Get firmware version info')
    parser.add_argument('-p', '--port', help='Serial port (default: auto-detect)')
    parser.add_argument('--non-exclusive', action='store_true', help='Use non-exclusive access to serial port')
    parser.add_argument('--allow-zero', action='store_true', help='Allow setting brightness to 0')
    args = parser.parse_args()

    print(f"Command arguments: {args}")

    if args.get:
        # Simply print the current brightness value
        print(f"Current brightness: {get_brightness()}")
        return
    
    if args.version:
        # Get version via serial connection
        ser = None
        try:
            ser = setup_serial(args.port, exclusive=not args.non_exclusive)
            if ser:
                print("Getting firmware version...")
                ser.write(b"version\n")
                ser.flush()
                time.sleep(0.5)  # Wait for response
                response = ser.readline().decode().strip()
                if response:
                    print(f"Firmware response: {response}")
                else:
                    print("No version response from ESP32")
            else:
                print("Could not connect to ESP32")
        except Exception as e:
            print(f"Error getting version: {e}")
        finally:
            if ser:
                ser.close()
        return

    # For set, increment, or decrement, we need the serial connection
    ser = None
    try:
        ser = setup_serial(args.port, exclusive=not args.non_exclusive)
        if not ser and not args.non_exclusive:
            print("Retrying with non-exclusive access...")
            ser = setup_serial(args.port, exclusive=False)
        if ser:
            current = get_brightness()
            print(f"Current brightness: {current}")

            if args.set is not None:
                new_value = args.set
                print(f"Setting brightness to {new_value}")
                if args.allow_zero or new_value > 0:
                    set_brightness(ser, new_value)
            elif args.increment is not None:
                new_value = min(current + args.increment, 100)
                set_brightness(ser, new_value)
            elif args.decrement is not None:
                if args.allow_zero:
                    new_value = max(current - args.decrement, 0)
                else:
                    new_value = max(current - args.decrement, 5)
                set_brightness(ser, new_value)
        else:
            print("Failed to open serial connection")
    finally:
        if ser:
            ser.close()
            print("Serial connection closed")

if __name__ == '__main__':
        main()
