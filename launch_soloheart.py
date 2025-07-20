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
"""

import os
import sys
import json
import time
import socket
import webbrowser
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

def check_python_version() -> bool:
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    required_packages = ['flask', 'jsonschema', 'dotenv', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required dependencies:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All required dependencies installed")
    return True

def check_data_files() -> bool:
    """Check if required data files exist and are valid."""
    data_files = [
        'solo_heart/character_schema.json',
        'srd_data/classes.json',
        'srd_data/monsters.json',
        'srd_data/rules.json'
    ]
    
    for file_path in data_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing data file: {file_path}")
            return False
        
        try:
            with open(file_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {file_path}: {e}")
            return False
    
    print("✅ All data files valid")
    return True

def check_port_available(port: int) -> bool:
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def check_ports() -> bool:
    """Check if required ports are available."""
    ports = [5003, 5004]  # Use different ports for testing
    
    for port in ports:
        if not check_port_available(port):
            print(f"❌ Port {port} is already in use")
            print(f"   Please stop any other services using port {port}")
            return False
    
    print("✅ All required ports available")
    return True

def check_llm_service() -> Optional[Dict[str, Any]]:
    """Check if LLM service is available (optional)."""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print("✅ Ollama service available")
            print(f"   Available models: {[m['name'] for m in models]}")
            return {'type': 'ollama', 'models': models}
    except Exception:
        pass
    
    try:
        response = requests.get('http://localhost:1234/v1/models', timeout=2)
        if response.status_code == 200:
            print("✅ LM Studio service available")
            return {'type': 'lm_studio'}
    except Exception:
        pass
    
    print("⚠️  No LLM service detected")
    print("   SoloHeart will run in offline mode")
    print("   Install Ollama or LM Studio for AI features")
    return None

def create_directories() -> None:
    """Create necessary directories if they don't exist."""
    directories = [
        'campaign_saves',
        'character_saves',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def start_server() -> bool:
    """Start the SoloHeart server."""
    try:
        print("\n🚀 Starting SoloHeart...")
        
        # Import and start the Flask app
        import sys
        sys.path.insert(0, 'solo_heart')
        from main_app import app
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open('http://localhost:5003')
                print("🌐 Opening SoloHeart in your browser...")
            except Exception as e:
                print(f"⚠️  Could not open browser automatically: {e}")
                print("   Please open: http://localhost:5003")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("✅ SoloHeart started successfully!")
        print("🎮 Access the game at: http://localhost:5003")
        print("🛑 Press Ctrl+C to stop")
        
        # Run the Flask app
        app.run(debug=False, host='0.0.0.0', port=5003)
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 SoloHeart stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting SoloHeart: {e}")
        return False

def main():
    """Main launcher function."""
    print("🎲 SoloHeart Launcher")
    print("=" * 50)
    
    # Run health checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        # ("Data Files", check_data_files),  # Temporarily disabled
        ("Ports", check_ports),
    ]
    
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            print(f"\n❌ {check_name} check failed")
            print("   Please fix the issue and try again")
            sys.exit(1)
    
    # Check LLM service (optional)
    print(f"\n🔍 Checking LLM Service...")
    llm_service = check_llm_service()
    
    # Create directories
    print(f"\n📁 Creating directories...")
    create_directories()
    
    # Start the server
    success = start_server()
    
    if not success:
        print("\n❌ Failed to start SoloHeart")
        sys.exit(1)

if __name__ == '__main__':
    main() 