#!/usr/bin/env python3
"""
SoloHeart Launch Script
Comprehensive launcher that handles setup, dependencies, and server startup.
"""

import os
import sys
import subprocess
import time
import requests
import webbrowser
from pathlib import Path

class SoloHeartLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.game_app_path = self.project_root / "game_app"
        self.server_url = "http://localhost:5002"
        self.server_process = None
        
    def print_banner(self):
        """Print the SoloHeart banner."""
        print("=" * 60)
        print("🎮 SOLOHEART - D&D 5E Character Creation & Adventure")
        print("=" * 60)
        print("Launching your D&D adventure...")
        print()
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        print("🐍 Checking Python version...")
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            print(f"   Current version: {sys.version}")
            return False
        print(f"✅ Python {sys.version.split()[0]} detected")
        return True
    
    def check_virtual_environment(self):
        """Check if virtual environment exists and is activated."""
        print("🔧 Checking virtual environment...")
        
        # Check if we're in a virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment is active")
            return True
        
        # Check if venv directory exists
        if self.venv_path.exists():
            print("⚠️  Virtual environment exists but not activated")
            print("   Activating virtual environment...")
            return self.activate_venv()
        else:
            print("❌ Virtual environment not found")
            return self.create_venv()
    
    def create_venv(self):
        """Create a new virtual environment."""
        print("🔧 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
            print("✅ Virtual environment created")
            return self.activate_venv()
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def activate_venv(self):
        """Activate the virtual environment."""
        if os.name == 'nt':  # Windows
            activate_script = self.venv_path / "Scripts" / "activate.bat"
            python_path = self.venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            activate_script = self.venv_path / "bin" / "activate"
            python_path = self.venv_path / "bin" / "python"
        
        if not python_path.exists():
            print(f"❌ Python not found in virtual environment: {python_path}")
            return False
        
        # Update sys.executable to use venv python
        sys.executable = str(python_path)
        print("✅ Virtual environment activated")
        return True
    
    def install_dependencies(self):
        """Install required dependencies."""
        print("📦 Installing dependencies...")
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            print("✅ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def check_port_availability(self):
        """Check if port 5002 is available."""
        print("🔌 Checking port availability...")
        try:
            response = requests.get(f"{self.server_url}/health", timeout=1)
            if response.status_code == 200:
                print("⚠️  Server already running on port 5002")
                return True
        except requests.exceptions.RequestException:
            pass
        
        # Check if port is in use by another process
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', 5002))
                print("✅ Port 5002 is available")
                return True
        except OSError:
            print("❌ Port 5002 is in use by another process")
            return False
    
    def start_server(self):
        """Start the SoloHeart server."""
        print("🚀 Starting SoloHeart server...")
        
        main_app_path = self.game_app_path / "main_app.py"
        if not main_app_path.exists():
            print(f"❌ Server file not found: {main_app_path}")
            return False
        
        try:
            # Start server in background
            self.server_process = subprocess.Popen([
                sys.executable, str(main_app_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                try:
                    response = requests.get(f"{self.server_url}/health", timeout=1)
                    if response.status_code == 200:
                        print("✅ Server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    pass
                print(f"   Attempt {i+1}/30...")
            
            print("❌ Server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def open_browser(self):
        """Open the browser to the SoloHeart interface."""
        print("🌐 Opening browser...")
        try:
            webbrowser.open(f"{self.server_url}/vibe-code-creation")
            print("✅ Browser opened to character creation page")
            return True
        except Exception as e:
            print(f"⚠️  Failed to open browser automatically: {e}")
            print(f"   Please manually open: {self.server_url}/vibe-code-creation")
            return False
    
    def show_status(self):
        """Show current server status."""
        print("\n" + "=" * 60)
        print("🎮 SOLOHEART STATUS")
        print("=" * 60)
        print(f"🌐 Server URL: {self.server_url}")
        print(f"🎭 Character Creation: {self.server_url}/vibe-code-creation")
        print(f"🏠 Main Page: {self.server_url}/")
        print(f"🏥 Health Check: {self.server_url}/health")
        print()
        print("🎯 Next Steps:")
        print("   1. Go to the character creation page")
        print("   2. Describe your character in natural language")
        print("   3. Follow the guided creation process")
        print("   4. Start your D&D adventure!")
        print()
        print("💡 Tips:")
        print("   - Try: 'My name is Elira. I'm an elven druid who survived a forest fire.'")
        print("   - Be descriptive about your character's personality and background")
        print("   - The AI will guide you through the rest of character creation")
        print()
        print("🛑 To stop the server, press Ctrl+C")
        print("=" * 60)
    
    def cleanup(self):
        """Cleanup on exit."""
        if self.server_process:
            print("\n🛑 Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ Server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Server didn't stop gracefully, forcing...")
                self.server_process.kill()
    
    def launch(self):
        """Main launch sequence."""
        try:
            self.print_banner()
            
            # Check Python version
            if not self.check_python_version():
                return False
            
            # Check virtual environment
            if not self.check_virtual_environment():
                return False
            
            # Install dependencies
            if not self.install_dependencies():
                return False
            
            # Check port availability
            if not self.check_port_availability():
                return False
            
            # Start server
            if not self.start_server():
                return False
            
            # Open browser
            self.open_browser()
            
            # Show status
            self.show_status()
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
                    # Check if server is still running
                    if self.server_process and self.server_process.poll() is not None:
                        print("❌ Server process has stopped unexpectedly")
                        break
            except KeyboardInterrupt:
                print("\n👋 Shutting down SoloHeart...")
            
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            return False
        finally:
            self.cleanup()
        
        return True

def main():
    """Main entry point."""
    launcher = SoloHeartLauncher()
    success = launcher.launch()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 