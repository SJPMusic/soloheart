#!/usr/bin/env python3
"""
Robust SoloHeart Server Launcher
Handles process management, debugging, and error recovery.
"""

import os
import sys
import subprocess
import time
import signal
import atexit
import requests
import threading
from pathlib import Path

class SoloHeartLauncher:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.process = None
        self.server_url = "http://localhost:5001"
        
    def check_dependencies(self):
        """Check if all required dependencies are available."""
        print("🔍 Checking dependencies...")
        
        # Check virtual environment
        venv_path = self.script_dir / "venv"
        if not venv_path.exists():
            print("❌ Virtual environment not found")
            print("Please run: python -m venv venv")
            return False
        
        # Check Python executable
        if sys.platform == "win32":
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            python_path = venv_path / "bin" / "python"
        
        if not python_path.exists():
            print(f"❌ Python not found at: {python_path}")
            return False
        
        # Check main app
        main_app_path = self.script_dir / "game_app" / "main_app.py"
        if not main_app_path.exists():
            print(f"❌ Main app not found at: {main_app_path}")
            return False
        
        print("✅ All dependencies found")
        return True
    
    def kill_existing_processes(self):
        """Kill any existing SoloHeart processes."""
        print("🛑 Checking for existing processes...")
        
        try:
            # Kill processes by name
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                             capture_output=True, check=False)
            else:
                subprocess.run(["pkill", "-f", "main_app.py"], 
                             capture_output=True, check=False)
            
            # Wait a moment for processes to terminate
            time.sleep(2)
            
            # Check if port is still in use
            if self.is_port_in_use():
                print("⚠️  Port 5001 still in use, trying to force kill...")
                subprocess.run(["lsof", "-ti:5001", "|", "xargs", "kill", "-9"], 
                             shell=True, capture_output=True, check=False)
                time.sleep(1)
            
        except Exception as e:
            print(f"⚠️  Error killing processes: {e}")
    
    def is_port_in_use(self):
        """Check if port 5001 is in use."""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=1)
            return response.status_code == 200
        except:
            return False
    
    def start_server(self):
        """Start the SoloHeart server."""
        print("🚀 Starting SoloHeart Server...")
        
        # Change to the SoloHeart directory
        os.chdir(self.script_dir)
        
        # Get Python path
        if sys.platform == "win32":
            python_path = self.script_dir / "venv" / "Scripts" / "python.exe"
        else:
            python_path = self.script_dir / "venv" / "bin" / "python"
        
        # Get main app path
        main_app_path = self.script_dir / "game_app" / "main_app.py"
        
        print(f"✅ Using Python: {python_path}")
        print(f"✅ Main app: {main_app_path}")
        print(f"🌐 Server will run on: {self.server_url}")
        print("📝 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        try:
            # Start the server process
            self.process = subprocess.Popen([
                str(python_path), str(main_app_path)
            ], cwd=str(self.script_dir))
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            for i in range(30):  # Wait up to 30 seconds
                if self.is_port_in_use():
                    print("✅ Server is running successfully!")
                    print(f"🌐 Open your browser to: {self.server_url}")
                    return True
                time.sleep(1)
                if i % 5 == 0:
                    print(f"⏳ Still waiting... ({i+1}/30 seconds)")
            
            print("❌ Server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def monitor_server(self):
        """Monitor the server process."""
        if not self.process:
            return
        
        try:
            # Wait for the process to complete
            self.process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            self.stop_server()
    
    def stop_server(self):
        """Stop the server process."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                print("✅ Server stopped gracefully")
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing server...")
                self.process.kill()
                self.process.wait()
                print("✅ Server force stopped")
            except Exception as e:
                print(f"⚠️  Error stopping server: {e}")
    
    def run(self):
        """Main launcher method."""
        try:
            # Check dependencies
            if not self.check_dependencies():
                return False
            
            # Kill existing processes
            self.kill_existing_processes()
            
            # Start server
            if not self.start_server():
                return False
            
            # Monitor server
            self.monitor_server()
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
            self.stop_server()
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            self.stop_server()
            return False
        
        return True

def main():
    """Main entry point."""
    launcher = SoloHeartLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 