#!/usr/bin/env python3
import serial
import time
import sys

def monitor_serial():
    try:
        print("Opening serial port for monitoring...")
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1, dsrdtr=False, rtscts=False)
        print("✅ Port opened, monitoring for 10 seconds...")
        
        start_time = time.time()
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                print(f"📨 Received: {data}")
            time.sleep(0.1)
        
        print("\n📤 Now sending 'version' command...")
        ser.write(b"version\n")
        ser.flush()
        print("✅ Command sent, waiting for response...")
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < 5:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                print(f"📨 Response: {data}")
                break
            time.sleep(0.1)
        else:
            print("❌ No response to version command")
        
        ser.close()
        print("✅ Monitoring completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    monitor_serial()