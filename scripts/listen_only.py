#!/usr/bin/env python3
import serial
import time

def listen_to_esp32():
    try:
        print("👂 ESP32 Listen-Only Test")
        print("=========================")
        
        print("Opening serial port in listen-only mode...")
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.5, dsrdtr=False, rtscts=False)
        print("✅ Port opened")
        
        print("Listening for ESP32 output for 15 seconds...")
        start_time = time.time()
        data_received = False
        
        while time.time() - start_time < 15:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                print(f"📨 Received: {data}")
                data_received = True
            time.sleep(0.1)
        
        if not data_received:
            print("❌ No data received from ESP32")
            print("💡 ESP32 might not be outputting anything or there's a connection issue")
        
        ser.close()
        print("✅ Listening completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    listen_to_esp32()