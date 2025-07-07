#!/usr/bin/env python3
import os
import time

def raw_serial_test():
    print("🔧 Raw Serial Test")
    print("==================")
    
    try:
        print("Opening /dev/ttyACM0 directly...")
        
        # Try direct file access
        with open('/dev/ttyACM0', 'wb', buffering=0) as serial_out:
            with open('/dev/ttyACM0', 'rb', buffering=0) as serial_in:
                print("✅ Direct file access opened")
                
                # Send version command
                print("📤 Sending 'version\\n' directly...")
                serial_out.write(b'version\n')
                
                print("📥 Reading response for 5 seconds...")
                start_time = time.time()
                while time.time() - start_time < 5:
                    try:
                        # Non-blocking read
                        os.set_blocking(serial_in.fileno(), False)
                        data = serial_in.read(1024)
                        if data:
                            print(f"📨 Received: {data}")
                    except (OSError, BlockingIOError):
                        pass
                    time.sleep(0.1)
                
        print("✅ Raw test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    raw_serial_test()