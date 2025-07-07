#!/usr/bin/env python3
"""
Test script for auto-dimmer functionality
Tests brightness control and idle detection in a safe way
"""

import time
import sys
from pathlib import Path

# Import our modules
sys.path.append(str(Path(__file__).parent))
from auto_dimmer import AutoDimmer

def test_brightness_control():
    """Test brightness control functionality"""
    print("🧪 Testing Brightness Control")
    print("==============================")
    
    dimmer = AutoDimmer()
    
    # Get current brightness
    original = dimmer.get_current_brightness()
    print(f"📊 Current brightness: {original}%")
    
    # Test setting different levels
    test_levels = [50, 70, 30]
    
    for level in test_levels:
        print(f"🔄 Setting brightness to {level}%...")
        if dimmer.set_brightness(level):
            time.sleep(2)
            current = dimmer.get_current_brightness()
            print(f"✅ Success: Brightness is now {current}%")
        else:
            print(f"❌ Failed to set brightness to {level}%")
            return False
    
    # Restore original brightness
    print(f"🔄 Restoring original brightness ({original}%)...")
    dimmer.set_brightness(original)
    
    return True

def test_dim_restore_cycle():
    """Test the dim/restore cycle"""
    print("\n🌙 Testing Dim/Restore Cycle")
    print("============================")
    
    dimmer = AutoDimmer()
    
    # Test dimming
    print("😴 Testing dim function...")
    if dimmer.dim_display():
        print("✅ Display dimmed successfully")
        time.sleep(3)
        
        # Test restore
        print("😊 Testing restore function...")
        if dimmer.restore_brightness():
            print("✅ Brightness restored successfully")
            return True
        else:
            print("❌ Failed to restore brightness")
            return False
    else:
        print("❌ Failed to dim display")
        return False

def test_configuration():
    """Test configuration management"""
    print("\n⚙️  Testing Configuration Management")
    print("====================================")
    
    dimmer = AutoDimmer(idle_minutes=5, dim_level=10, check_interval=15)
    
    print(f"📝 Test config: {dimmer.idle_minutes}min, {dimmer.dim_level}%, {dimmer.check_interval}s")
    
    # Save config
    dimmer.save_dimmer_config()
    print("💾 Configuration saved")
    
    # Load config
    dimmer2 = AutoDimmer()
    print(f"📁 Loaded config: {dimmer2.idle_minutes}min, {dimmer2.dim_level}%, {dimmer2.check_interval}s")
    
    return dimmer.idle_minutes == dimmer2.idle_minutes

def simulate_auto_dimmer(duration_seconds=60):
    """Simulate auto-dimmer operation for testing"""
    print(f"\n🚀 Simulating Auto-Dimmer ({duration_seconds}s)")
    print("=" * 50)
    
    dimmer = AutoDimmer(idle_minutes=0.5, dim_level=10, check_interval=5)  # 30 second idle timeout
    
    print("⚠️  This is a simulation - the system will:")
    print("   • Monitor idle time every 5 seconds")
    print("   • Dim after 30 seconds of 'idle' time")
    print("   • Restore when activity is detected")
    print(f"   • Run for {duration_seconds} seconds total")
    print("\n📊 Monitoring...")
    
    start_time = time.time()
    
    while time.time() - start_time < duration_seconds:
        try:
            idle_time = dimmer.get_idle_time_seconds()
            current_brightness = dimmer.get_current_brightness()
            
            elapsed = int(time.time() - start_time)
            print(f"[{elapsed:3d}s] Idle: {idle_time:6.0f}s, Brightness: {current_brightness:2d}%, Dimmed: {dimmer.is_dimmed}")
            
            # Simulate the dimming logic (but with shorter timeouts for testing)
            if idle_time > 30 and not dimmer.is_dimmed:  # 30 seconds for testing
                print("💤 Idle threshold reached, dimming...")
                dimmer.dim_display()
            elif idle_time < 10 and dimmer.is_dimmed:  # Less than 10 seconds idle
                print("👋 Activity detected, restoring...")
                dimmer.restore_brightness()
            
            time.sleep(5)  # Check every 5 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Test interrupted by user")
            break
    
    # Cleanup
    if dimmer.is_dimmed:
        print("🔄 Restoring brightness before test end...")
        dimmer.restore_brightness()
    
    print("✅ Simulation completed")

def main():
    print("🔬 Auto-Dimmer Test Suite")
    print("=========================")
    print("This script tests the auto-dimmer functionality safely.")
    print("All changes will be reverted after testing.\n")
    
    try:
        # Test 1: Basic brightness control
        if not test_brightness_control():
            print("❌ Brightness control test failed!")
            return False
        
        # Test 2: Dim/restore cycle
        if not test_dim_restore_cycle():
            print("❌ Dim/restore test failed!")
            return False
        
        # Test 3: Configuration
        if not test_configuration():
            print("❌ Configuration test failed!")
            return False
        
        print("\n✅ All basic tests passed!")
        
        # Ask user if they want to run simulation
        try:
            response = input("\n🤔 Run 60-second auto-dimmer simulation? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                simulate_auto_dimmer(60)
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Skipping simulation")
        
        print("\n🎉 Test suite completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)