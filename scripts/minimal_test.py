#!/usr/bin/env python3
import serial
import time
import sys

try:
    print("Step 1: Opening serial port...")
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1, dsrdtr=False, rtscts=False)
    print("✅ Port opened successfully")
    
    print("Step 2: Checking port status...")
    print(f"  - Port: {ser.port}")
    print(f"  - Baudrate: {ser.baudrate}")
    print(f"  - Is open: {ser.is_open}")
    print(f"  - Timeout: {ser.timeout}")
    
    print("Step 3: Waiting 3 seconds...")
    time.sleep(3)
    
    print("Step 4: Closing port...")
    ser.close()
    print("✅ Test completed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()