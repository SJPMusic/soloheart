#!/usr/bin/env python3
"""
Simple SoloHeart Server Launcher
Just run: python start_server.py
"""

import os
import sys
import subprocess
import time
import signal
import atexit

def main():
    print("🚀 Starting SoloHeart Server...")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the SoloHeart directory
    os.chdir(script_dir)
    
    # Check if virtual environment exists
    venv_path = os.path.join(script_dir, 'venv')
    if not os.path.exists(venv_path):
        print("❌ Virtual environment not found. Please run: python -m venv venv")
        return
    
    # Activate virtual environment and start server
    if sys.platform == "win32":
        # Windows
        python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
        activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
    else:
        # macOS/Linux
        python_path = os.path.join(venv_path, 'bin', 'python')
        activate_script = os.path.join(venv_path, 'bin', 'activate')
    
    # Check if Python executable exists
    if not os.path.exists(python_path):
        print(f"❌ Python not found at: {python_path}")
        print("Please recreate virtual environment: rm -rf venv && python -m venv venv")
        return
    
    # Path to main_app.py
    main_app_path = os.path.join(script_dir, 'game_app', 'main_app.py')
    
    if not os.path.exists(main_app_path):
        print(f"❌ Main app not found at: {main_app_path}")
        return
    
    print(f"✅ Found Python: {python_path}")
    print(f"✅ Found main app: {main_app_path}")
    print("🌐 Starting server on http://localhost:5001")
    print("📝 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the server
        process = subprocess.Popen([
            python_path, main_app_path
        ], cwd=script_dir)
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            import requests
            response = requests.get('http://localhost:5001/health', timeout=5)
            if response.status_code == 200:
                print("✅ Server is running successfully!")
                print("🌐 Open your browser to: http://localhost:5001")
            else:
                print("⚠️  Server started but health check failed")
        except ImportError:
            print("✅ Server started (requests not available for health check)")
        except Exception as e:
            print(f"⚠️  Server started but health check failed: {e}")
        
        # Keep the script running
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        if 'process' in locals():
            process.terminate()
            process.wait()
        print("✅ Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main() 