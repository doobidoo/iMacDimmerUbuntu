#!/usr/bin/env python3
import serial
import time

try:
    print("Testing serial connection...")
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=3)
    print("Serial port opened successfully")
    
    # Send a simple command
    print("Sending 'version' command...")
    ser.write(b"version\n")
    ser.flush()
    
    # Read response with timeout
    print("Reading response...")
    response = ser.readline()
    print(f"Response: {response}")
    
    ser.close()
    print("Test completed")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()