#!/usr/bin/env python3
"""
Automate final Confrontation Log integration and verification
Copies build output to Flask static directory and runs tests
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    """Automate Confrontation Log integration"""
    print("🔧 Setting up Confrontation Log integration...\n")
    
    # Define paths
    base_dir = os.path.dirname(__file__)
    source_file = os.path.join(base_dir, '..', 'page-ui', 'website', 'public', 'static', 'confrontation-log-client.js')
    target_dir = os.path.join(base_dir, 'static', 'js')
    target_file = os.path.join(target_dir, 'confrontation-log-client.js')
    
    # 1. Check if source file exists
    print("📁 Checking build output...")
    if not os.path.exists(source_file):
        print(f"❌ Missing build output: {source_file}")
        print("💡 Please run: cd ../page-ui/website && npm run build:log")
        return False
    
    print(f"✅ Build output found: {source_file}")
    
    # 2. Create target directory if it doesn't exist
    print("\n📂 Creating target directory...")
    os.makedirs(target_dir, exist_ok=True)
    print(f"✅ Target directory ready: {target_dir}")
    
    # 3. Copy the file from source to destination
    print("\n📋 Copying hydration script...")
    try:
        shutil.copy2(source_file, target_file)
        print(f"✅ File copied: {target_file}")
    except Exception as e:
        print(f"❌ Copy failed: {e}")
        return False
    
    # 4. Confirm the file exists at the destination
    print("\n🔍 Verifying copy...")
    if not os.path.exists(target_file):
        print("❌ Copy failed: File not found at destination")
        return False
    
    file_size = os.path.getsize(target_file)
    print(f"✅ File verified: {target_file} ({file_size} bytes)")
    
    # 5. Run the test script to verify hydration setup
    print("\n🧪 Running verification tests...")
    test_script = os.path.join(base_dir, 'test_confrontation_log_enhancements.py')
    
    if not os.path.exists(test_script):
        print(f"❌ Test script not found: {test_script}")
        return False
    
    # Run the test script
    import subprocess
    try:
        result = subprocess.run([sys.executable, test_script], 
                              capture_output=True, text=True, cwd=base_dir)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("\n🎉 Confrontation Log integration complete!")
            print("✅ All tests passed")
            return True
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 