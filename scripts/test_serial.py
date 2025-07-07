#!/usr/bin/env python3
import serial
import time
import sys

try:
    print("Opening serial port /dev/ttyACM0...")
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
    
    print("Waiting for ESP32 to be ready...")
    time.sleep(2)
    
    # Clear any pending data
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    print("Sending brightness command: 50")
    ser.write(b"50\n")
    ser.flush()
    
    print("Waiting for response...")
    start_time = time.time()
    while time.time() - start_time < 3:
        if ser.in_waiting > 0:
            response = ser.readline()
            print(f"Received: {response}")
            break
        time.sleep(0.1)
    else:
        print("No response received within 3 seconds")
    
    ser.close()
    print("Done")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()