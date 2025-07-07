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
    """Try to discover ESP32 IP address using multiple methods"""
    import socket
    import subprocess
    import re
    
    def check_ip(ip):
        try:
            response = requests.get(f"http://{ip}/version", timeout=1)
            if response.status_code == 200 and "firmware_version" in response.text:
                return ip
        except:
            pass
        return None
    
    print("🔍 Discovering ESP32...")
    
    # Method 1: Check ARP table for known MAC address prefix (ESP32 OUI)
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # Look for Espressif MAC addresses (common OUIs: 10:00:3b, 24:6f:28, etc.)
            esp_ouis = ['10:00:3b', '24:6f:28', '30:ae:a4', '7c:df:a1', 'cc:50:e3']
            for line in result.stdout.split('\n'):
                for oui in esp_ouis:
                    if oui in line.lower():
                        ip_match = re.search(r'\(([\d.]+)\)', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            print(f"📡 Found ESP32 MAC in ARP table: {ip}")
                            if check_ip(ip):
                                return ip
    except:
        pass
    
    # Method 2: mDNS discovery
    try:
        result = subprocess.run(['avahi-browse', '-t', '-r', '_http._tcp'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'esp32' in line.lower() or 'arduino' in line.lower():
                    ip_match = re.search(r'address = \[([\d.]+)\]', line)
                    if ip_match:
                        ip = ip_match.group(1)
                        print(f"📡 Found ESP32 via mDNS: {ip}")
                        if check_ip(ip):
                            return ip
    except:
        pass
    
    # Method 3: Network scan (local networks only)
    try:
        # Get all local network interfaces
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=5)
        networks = []
        for line in result.stdout.split('\n'):
            match = re.search(r'(\d+\.\d+\.\d+)\.\d+/\d+.*src (\d+\.\d+\.\d+\.\d+)', line)
            if match and not match.group(1).startswith('169.254'):  # Skip link-local
                networks.append(match.group(1))
        
        networks = list(set(networks))  # Remove duplicates
        print(f"🌐 Scanning networks: {networks}")
        
        # Quick scan of common device IPs
        common_endings = [27, 100, 101, 102, 200, 201, 202, 150, 151, 152]
        for network in networks[:3]:  # Limit to 3 networks
            for ending in common_endings:
                ip = f"{network}.{ending}"
                if check_ip(ip):
                    print(f"📡 Found ESP32 via network scan: {ip}")
                    return ip
    except:
        pass
    
    return None

def try_hostname_first():
    """Try to connect via mDNS hostname first"""
    try:
        response = requests.get("http://imacdimmer.local/version", timeout=3)
        if response.status_code == 200 and "firmware_version" in response.text:
            return "imacdimmer.local"
    except:
        pass
    return None

def http_request(endpoint, params=None):
    config = load_config()
    esp32_address = config.get('esp32_ip')
    
    # Always try hostname first (mDNS)
    hostname = try_hostname_first()
    if hostname:
        esp32_address = hostname
        # Update config to remember this works
        save_config(esp32_ip=hostname)
    
    # If no address or hostname failed, discover
    if not esp32_address or esp32_address == '192.168.1.100':
        print("ESP32 address not configured. Trying to discover...")
        discovered_ip = discover_esp32()
        if discovered_ip:
            esp32_address = discovered_ip
            save_config(esp32_ip=esp32_address)
        else:
            print("Could not discover ESP32. Please check your network connection.")
            return None
    
    # Try the request
    def try_request(address):
        try:
            url = f"http://{address}{endpoint}"
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                return response.text
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
        except requests.exceptions.ConnectionError:
            return None
        except Exception as e:
            print(f"HTTP request failed: {e}")
            return None
    
    # Try current address
    result = try_request(esp32_address)
    if result:
        return result
    
    # If failed, try hostname as fallback
    if esp32_address != "imacdimmer.local":
        print(f"Could not connect to ESP32 at {esp32_address}")
        print("Trying hostname: imacdimmer.local...")
        result = try_request("imacdimmer.local")
        if result:
            save_config(esp32_ip="imacdimmer.local")
            return result
    
    # If still failed, try discovery
    print("Trying to discover ESP32...")
    discovered_ip = discover_esp32()
    if discovered_ip and discovered_ip != esp32_address:
        save_config(esp32_ip=discovered_ip)
        result = try_request(discovered_ip)
        if result:
            return result
    
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