#!/usr/bin/env python3
import serial
import time
import sys

def debug_serial():
    try:
        print("🔍 Serial Communication Debug")
        print("============================")
        
        # Open serial port
        print("Opening /dev/ttyACM0...")
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        print(f"✅ Serial port opened: {ser.is_open}")
        
        # Wait for ESP32 to be ready
        print("Waiting 2 seconds for ESP32...")
        time.sleep(2)
        
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        print("✅ Buffers cleared")
        
        # Check if there's any data already available
        if ser.in_waiting > 0:
            existing_data = ser.read(ser.in_waiting)
            print(f"📨 Found existing data: {existing_data}")
        
        # Send version command
        print("📤 Sending 'version' command...")
        ser.write(b"version\n")
        ser.flush()
        print("✅ Command sent")
        
        # Wait and read response
        print("📥 Waiting for response...")
        for i in range(10):  # Wait up to 10 seconds
            if ser.in_waiting > 0:
                response = ser.readline()
                print(f"📨 Response: {response}")
                break
            print(f"⏳ Waiting... ({i+1}/10)")
            time.sleep(1)
        else:
            print("❌ No response received")
            
        # Try sending a brightness command
        print("\n📤 Sending brightness command '50'...")
        ser.write(b"50\n")
        ser.flush()
        
        # Wait and read response
        print("📥 Waiting for brightness response...")
        for i in range(5):
            if ser.in_waiting > 0:
                response = ser.readline()
                print(f"📨 Brightness response: {response}")
                break
            print(f"⏳ Waiting... ({i+1}/5)")
            time.sleep(1)
        else:
            print("❌ No brightness response received")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'ser' in locals():
            ser.close()
            print("✅ Serial port closed")

if __name__ == "__main__":
    debug_serial()