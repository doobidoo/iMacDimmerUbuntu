#!/usr/bin/env python3
import requests
import argparse
import sys
import json
from pathlib import Path

def get_config_file():
    return Path.home() / '.config' / 'imacdisplay.conf'

def load_config():
    config_file = get_config_file()
    try:
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
            return config
    except Exception as e:
        print(f"Error loading config: {e}")
    
    # Default configuration with your ESP32 IP
    return {'esp32_ip': '10.0.1.27', 'last_brightness': 70}

def save_config(brightness=None, esp32_ip=None):
    config_file = get_config_file()
    config = load_config()
    
    if brightness is not None:
        config['last_brightness'] = brightness
    
    if esp32_ip is not None:
        config['esp32_ip'] = esp32_ip
    
    try:
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Error saving config: {e}")

def discover_esp32():
    """Try to discover ESP32 IP address"""
    # Try common IP ranges
    import socket
    import threading
    import time
    
    def check_ip(ip):
        try:
            response = requests.get(f"http://{ip}/version", timeout=2)
            if response.status_code == 200 and "firmware_version" in response.text:
                print(f"Found ESP32 at {ip}")
                return ip
        except:
            pass
        return None
    
    # Get local network
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    network = '.'.join(local_ip.split('.')[:-1])
    
    print(f"Scanning network {network}.x for ESP32...")
    
    # Check common IPs first
    common_ips = [f"{network}.{i}" for i in [100, 101, 102, 200, 201, 202]]
    for ip in common_ips:
        result = check_ip(ip)
        if result:
            return result
    
    return None

def http_request(endpoint, params=None):
    config = load_config()
    esp32_ip = config.get('esp32_ip')
    
    if not esp32_ip or esp32_ip == '192.168.1.100':
        print("ESP32 IP not configured. Trying to discover...")
        discovered_ip = discover_esp32()
        if discovered_ip:
            esp32_ip = discovered_ip
            save_config(esp32_ip=esp32_ip)
        else:
            print("Could not discover ESP32. Please check your network connection.")
            return None
    
    try:
        url = f"http://{esp32_ip}{endpoint}"
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.text
        else:
            print(f"HTTP Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to ESP32 at {esp32_ip}")
        print("Trying to discover ESP32...")
        discovered_ip = discover_esp32()
        if discovered_ip and discovered_ip != esp32_ip:
            save_config(esp32_ip=discovered_ip)
            try:
                url = f"http://{discovered_ip}{endpoint}"
                response = requests.get(url, params=params, timeout=5)
                return response.text
            except:
                pass
        return None
    except Exception as e:
        print(f"HTTP request failed: {e}")
        return None

def get_brightness():
    """Get last saved brightness value"""
    config = load_config()
    return config.get('last_brightness', 70)

def set_brightness_http(value):
    """Set brightness via HTTP"""
    response = http_request("/serial", {"cmd": str(value)})
    if response and "Brightness set to" in response:
        save_config(brightness=value)
        print(response)
        return value
    else:
        print(f"Failed to set brightness: {response}")
        return None

def main():
    parser = argparse.ArgumentParser(description='iMac Display Brightness Control (HTTP)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--set', type=int, help='Set brightness (5-100)')
    group.add_argument('-g', '--get', action='store_true', help='Get current brightness')
    group.add_argument('-i', '--increment', type=int, help='Increase brightness by amount')
    group.add_argument('-d', '--decrement', type=int, help='Decrease brightness by amount')
    group.add_argument('-v', '--version', action='store_true', help='Get firmware version info')
    group.add_argument('--ping', action='store_true', help='Ping ESP32')
    parser.add_argument('--ip', help='ESP32 IP address')
    parser.add_argument('--discover', action='store_true', help='Discover ESP32 IP address')
    
    args = parser.parse_args()
    
    print(f"Command arguments: {args}")
    
    if args.ip:
        save_config(esp32_ip=args.ip)
        print(f"ESP32 IP set to: {args.ip}")
        return
    
    if args.discover:
        ip = discover_esp32()
        if ip:
            save_config(esp32_ip=ip)
            print(f"ESP32 discovered and saved: {ip}")
        else:
            print("ESP32 not found")
        return
    
    if args.get:
        # Get current brightness from ESP32
        response = http_request("/serial", {"cmd": "get"})
        if response:
            print(response)
        else:
            print(f"Current brightness: {get_brightness()}% (cached)")
        return
    
    if args.version:
        response = http_request("/serial", {"cmd": "version"})
        if response:
            print(f"Version: {response}")
        else:
            print("Could not get version from ESP32")
        return
    
    if args.ping:
        response = http_request("/serial", {"cmd": "ping"})
        if response:
            print(f"Ping response: {response}")
        else:
            print("ESP32 did not respond to ping")
        return
    
    # Handle brightness changes
    current = get_brightness()
    new_value = None
    
    if args.set is not None:
        new_value = args.set
    elif args.increment is not None:
        new_value = min(current + args.increment, 100)
    elif args.decrement is not None:
        new_value = max(current - args.decrement, 5)
    
    if new_value is not None:
        print(f"Current brightness: {current}%")
        print(f"Setting brightness to: {new_value}%")
        set_brightness_http(new_value)

if __name__ == '__main__':
    main()