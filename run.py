#!/usr/bin/env python3
"""
SoloHeart - Single Entry Point Launcher
=======================================

This is the ONLY way to launch SoloHeart. All other launcher scripts should be removed.

Features:
- Health checks before launch
- Graceful error handling
- Automatic browser opening
- Clear error messages
- Port conflict detection
- Offline mode support
- Data file validation
"""

import os
import sys
import json
import time
import socket
import webbrowser
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add the game_app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'game_app'))

class SoloHeartLauncher:
    """Main launcher class for SoloHeart."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.game_app_dir = self.project_root / 'game_app'
        self.port = 5001
        self.server_started = False
        
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        if sys.version_info < (3, 9):
            print("❌ Python 3.9 or higher is required")
            print(f"   Current version: {sys.version}")
            return False
        print(f"✅ Python version: {sys.version.split()[0]}")
        return True
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        required_packages = [
            ('flask', 'Flask'),
            ('flask_cors', 'Flask-CORS'),
            ('dotenv', 'python-dotenv'),
            ('requests', 'requests')
        ]
        missing_packages = []
        
        for package, display_name in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(display_name)
        
        if missing_packages:
            print("❌ Missing required dependencies:")
            for package in missing_packages:
                print(f"   - {package}")
            print("\n💡 Install with: pip install -r requirements.txt")
            return False
        
        print("✅ All required dependencies installed")
        return True
    
    def check_data_files(self) -> bool:
        """Check if required data files exist and are valid."""
        data_files = [
            'game_app/character_schema.json',
            'srd_data/classes.json',
            'srd_data/monsters.json'
        ]
        
        for file_path in data_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                print(f"❌ Missing data file: {file_path}")
                return False
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in {file_path}: {e}")
                return False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                return False
        
        print("✅ All data files valid")
        return True
    
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def find_available_port(self, start_port: int = 5001, max_attempts: int = 10) -> Optional[int]:
        """Find an available port starting from start_port."""
        for port in range(start_port, start_port + max_attempts):
            if self.check_port_available(port):
                return port
        return None
    
    def check_ports(self) -> bool:
        """Check if required ports are available."""
        self.port = self.find_available_port(5001)
        if not self.port:
            print("❌ No available ports found in range 5001-5010")
            print("   Please stop other services or free up ports")
            return False
        
        if self.port != 5001:
            print(f"⚠️  Port 5001 in use, using port {self.port}")
        else:
            print(f"✅ Port {self.port} available")
        return True
    
    def check_llm_service(self) -> Optional[Dict[str, Any]]:
        """Check if Gemma3 service is available (optional)."""
        try:
            import requests
            response = requests.get('http://localhost:1234/v1/models', timeout=2)
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                model_names = [m.get('id', '') for m in models]
                print("✅ Gemma3 service available via LM Studio")
                print(f"   Available models: {model_names}")
                return {'type': 'gemma3', 'models': models}
        except Exception:
            pass
        
        print("⚠️  No Gemma3 service detected")
        print("   SoloHeart will run in offline mode")
        print("   Install LM Studio with Gemma3 for AI features")
        return None
    
    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            'campaign_saves',
            'character_saves',
            'logs'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
    
    def open_browser(self) -> None:
        """Open browser after server starts."""
        time.sleep(2)
        try:
            webbrowser.open(f'http://localhost:{self.port}')
            print(f"🌐 Opening SoloHeart in your browser...")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print(f"   Please open: http://localhost:{self.port}")
    
    def start_server(self) -> bool:
        """Start the SoloHeart server."""
        try:
            print(f"\n🚀 Starting SoloHeart on port {self.port}...")
            
            # Create necessary directories
            self.create_directories()
            
            # Start browser thread
            browser_thread = threading.Thread(target=self.open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Import and start the Flask app
            try:
                from main_app import app
                print("✅ SoloHeart started successfully!")
                print(f"🎮 Access the game at: http://localhost:{self.port}")
                print("🛑 Press Ctrl+C to stop")
                
                # Run the Flask app
                app.run(debug=False, host='0.0.0.0', port=self.port)
                return True
                
            except ImportError as e:
                print(f"❌ Error importing Flask app: {e}")
                print("   This might be a dependency or path issue")
                return False
                
        except KeyboardInterrupt:
            print("\n🛑 SoloHeart stopped by user")
            return True
        except Exception as e:
            print(f"❌ Error starting SoloHeart: {e}")
            return False
    
    def run_health_checks(self) -> bool:
        """Run all health checks."""
        checks = [
            ("Python Version", self.check_python_version),
            ("Dependencies", self.check_dependencies),
            ("Data Files", self.check_data_files),
            ("Ports", self.check_ports),
        ]
        
        for check_name, check_func in checks:
            print(f"\n🔍 Checking {check_name}...")
            if not check_func():
                print(f"\n❌ {check_name} check failed")
                print("   Please fix the issue and try again")
                return False
        
        # Optional LLM check
        print(f"\n🔍 Checking LLM Service...")
        self.check_llm_service()
        
        return True
    
    def main(self) -> int:
        """Main launcher function."""
        print("🎲 SoloHeart Launcher")
        print("=" * 50)
        
        # Run health checks
        if not self.run_health_checks():
            return 1
        
        # Start server
        if not self.start_server():
            return 1
        
        return 0

def main():
    """Entry point."""
    launcher = SoloHeartLauncher()
    return launcher.main()

if __name__ == "__main__":
    sys.exit(main()) 