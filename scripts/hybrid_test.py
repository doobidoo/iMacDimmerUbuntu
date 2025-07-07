#!/usr/bin/env python3
import serial
import requests
import time
import sys

def get_esp32_ip():
    """Try to get ESP32 IP from common addresses"""
    common_ips = [
        "192.168.1.100", "192.168.1.101", "192.168.1.200",
        "192.168.0.100", "192.168.0.101", "192.168.0.200",
        "10.0.0.100", "10.0.0.101"
    ]
    
    for ip in common_ips:
        try:
            response = requests.get(f"http://{ip}/version", timeout=2)
            if response.status_code == 200:
                return ip
        except:
            continue
    return None

def test_serial():
    """Test serial communication"""
    try:
        print("🔌 Testing Serial Communication...")
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1, dsrdtr=False, rtscts=False)
        
        time.sleep(0.5)
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting()).decode('utf-8', errors='ignore')
            print(f"📨 Serial data: {repr(data)}")
            
            if "ESP-ROM:" in data:
                print("⚠️  ESP32 in bootloader mode - serial communication blocked")
                ser.close()
                return False
        
        ser.write(b"version\n")
        ser.flush()
        time.sleep(1)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting()).decode('utf-8', errors='ignore')
            print(f"✅ Serial response: {repr(response)}")
            ser.close()
            return True
        else:
            print("❌ No serial response")
            ser.close()
            return False
            
    except Exception as e:
        print(f"❌ Serial error: {e}")
        return False

def test_http():
    """Test HTTP communication"""
    try:
        print("🌐 Testing HTTP Communication...")
        esp32_ip = get_esp32_ip()
        
        if not esp32_ip:
            print("❌ Could not find ESP32 IP address")
            return False
        
        print(f"📍 Found ESP32 at: {esp32_ip}")
        
        # Test version
        response = requests.get(f"http://{esp32_ip}/serial?cmd=version", timeout=5)
        if response.status_code == 200:
            print(f"✅ HTTP version: {response.text}")
            return esp32_ip
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ HTTP error: {e}")
        return False

def main():
    print("🔍 ESP32 Communication Test")
    print("============================")
    
    # Test both methods
    serial_works = test_serial()
    http_result = test_http()
    
    print("\n📊 Results:")
    print(f"Serial communication: {'✅ Working' if serial_works else '❌ Failed'}")
    print(f"HTTP communication: {'✅ Working' if http_result else '❌ Failed'}")
    
    if http_result and not serial_works:
        print("\n💡 Recommendation: Use HTTP-based communication")
        print(f"   ESP32 IP: {http_result}")
        print("   Serial is blocked by bootloader mode")
    elif serial_works:
        print("\n💡 Recommendation: Serial communication is working")
    else:
        print("\n❌ Both serial and HTTP communication failed")

if __name__ == "__main__":
    main()