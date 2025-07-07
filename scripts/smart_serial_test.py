#!/usr/bin/env python3
import serial
import time

def smart_serial_test():
    try:
        print("🧠 Smart Serial Test")
        print("===================")
        
        print("Opening serial port...")
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2, dsrdtr=False, rtscts=False)
        print("✅ Port opened")
        
        print("Waiting for ESP32 response...")
        time.sleep(1)
        
        # Read any initial bootloader messages
        if ser.in_waiting > 0:
            initial_data = ser.read(ser.in_waiting()).decode('utf-8', errors='ignore')
            print(f"📨 Initial data: {repr(initial_data)}")
            
            if "ESP-ROM:" in initial_data:
                print("⚠️  ESP32 is in bootloader mode!")
                print("🔄 Attempting to restart ESP32 into firmware mode...")
                
                # Try to exit bootloader by sending Ctrl+C or reset sequence
                ser.write(b'\x03')  # Ctrl+C
                time.sleep(0.5)
                
                # Wait for potential restart
                print("⏳ Waiting for firmware to start...")
                time.sleep(3)
                
                # Clear any additional bootloader messages
                if ser.in_waiting > 0:
                    bootloader_data = ser.read(ser.in_waiting()).decode('utf-8', errors='ignore')
                    print(f"📨 Bootloader data: {repr(bootloader_data)}")
                
                # Now try our firmware commands
                print("📤 Trying firmware commands...")
                ser.write(b"version\n")
                ser.flush()
                
                time.sleep(1)
                if ser.in_waiting > 0:
                    response = ser.read(ser.in_waiting()).decode('utf-8', errors='ignore')
                    print(f"📨 Firmware response: {repr(response)}")
                    
                    if "Firmware:" in response:
                        print("✅ ESP32 is now running our firmware!")
                    else:
                        print("❌ ESP32 is still in bootloader mode")
                else:
                    print("❌ No response from firmware")
        else:
            print("📤 No initial data, trying commands directly...")
            ser.write(b"version\n")
            ser.flush()
            
            time.sleep(1)
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting()).decode('utf-8', errors='ignore')
                print(f"📨 Direct response: {repr(response)}")
        
        ser.close()
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    smart_serial_test()