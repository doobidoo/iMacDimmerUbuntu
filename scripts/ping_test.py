#!/usr/bin/env python3
import serial
import time

def ping_esp32():
    try:
        print("🏓 ESP32 Ping Test")
        print("==================")
        
        print("Opening serial port...")
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2, dsrdtr=False, rtscts=False)
        print("✅ Port opened")
        
        print("Waiting for ESP32 to be ready...")
        time.sleep(3)
        
        # Clear any existing data
        if ser.in_waiting > 0:
            existing = ser.read(ser.in_waiting)
            print(f"Cleared existing data: {existing}")
        
        # Send ping
        print("📤 Sending 'ping' command...")
        ser.write(b"ping\n")
        ser.flush()
        
        # Wait for pong
        print("📥 Waiting for 'pong' response...")
        response = ser.readline()
        if response:
            print(f"✅ Response: {response.decode().strip()}")
        else:
            print("❌ No response")
        
        # Try version command
        print("\n📤 Sending 'version' command...")
        ser.write(b"version\n")
        ser.flush()
        
        response = ser.readline()
        if response:
            print(f"✅ Version response: {response.decode().strip()}")
        else:
            print("❌ No version response")
        
        ser.close()
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ping_esp32()