#!/usr/bin/env python3
import serial
import time
import re

def wait_for_esp32_boot():
    try:
        print("🚀 ESP32 Boot-Aware Test")
        print("========================")
        
        print("Opening serial port...")
        ser = serial.Serial()
        ser.port = '/dev/ttyACM0'
        ser.baudrate = 115200
        ser.timeout = 1
        ser.dsrdtr = False
        ser.rtscts = False
        ser.xonxoff = False
        ser.open()
        print("✅ Port opened")
        
        print("Waiting for ESP32 to complete boot sequence...")
        boot_complete = False
        start_time = time.time()
        
        # Look for signs that the ESP32 has booted into our firmware
        while time.time() - start_time < 15:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                print(f"📨 Boot data: {repr(data)}")
                
                # Look for our firmware startup message
                if "iMac Dimmer Starting" in data or "Heartbeat:" in data:
                    print("✅ ESP32 has booted into our firmware!")
                    boot_complete = True
                    break
                    
                # Look for bootloader messages
                if "ESP-ROM:" in data or "Build:" in data:
                    print("⚠️  ESP32 is in bootloader mode")
            
            time.sleep(0.5)
        
        if not boot_complete:
            print("❌ ESP32 did not complete boot into our firmware")
            print("💡 It might be stuck in bootloader mode")
        else:
            # Clear any remaining data
            time.sleep(1)
            ser.reset_input_buffer()
            
            # Now try our commands
            print("\n📤 Sending 'version' command...")
            ser.write(b"version\n")
            ser.flush()
            
            time.sleep(1)
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting()).decode('utf-8', errors='ignore')
                print(f"✅ Version response: {repr(response)}")
            else:
                print("❌ No version response")
        
        ser.close()
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    wait_for_esp32_boot()