#!/usr/bin/env python3
"""
SoloHeart Launcher with Monitor
Launches the game with robust monitoring and auto-restart capabilities.
"""

import os
import sys
import subprocess
import webbrowser
import time
import signal
from server_monitor import ServerMonitor

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import psutil
        import requests
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install psutil requests")
        return False

def check_ollama():
    """Check if Ollama is installed and running."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            if 'llama3' in model_names or 'llama3:latest' in model_names:
                print("✅ Ollama is running with llama3 model")
                return True
            else:
                print("⚠️ Ollama is running but llama3 model not found")
                print("💡 Run: ollama pull llama3")
                return False
        else:
            print("❌ Ollama health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print("💡 Please start Ollama with: brew services start ollama")
        print("💡 Or install with: brew install ollama")
        return False
    except Exception as e:
        print(f"❌ Ollama check error: {e}")
        return False

def main():
    """Main launcher function."""
    print("🎲 SoloHeart - Robust Game Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama():
        print("\nYou can still run the game, but AI features will be limited.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n🚀 Starting SoloHeart with monitoring...")
    
    # Create monitor
    monitor = ServerMonitor()
    
    def signal_handler(signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        if monitor:
            monitor.stop_monitoring()
        sys.exit(0)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start monitoring
        if monitor.start_monitoring():
            print("✅ Game started with monitoring!")
            print("🌐 Opening in browser...")
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(3)
                webbrowser.open('http://localhost:5001')
            
            import threading
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            print("\n🎮 How to play:")
            print("1. Click 'Start New Campaign'")
            print("2. Choose 'Vibe Code' for natural language character creation")
            print("3. Describe your character concept")
            print("4. Start your adventure!")
            print("\n📊 Monitoring active - server will auto-restart if needed")
            print("🛑 Press Ctrl+C to stop")
            
            # Keep the main thread alive
            while monitor.running:
                time.sleep(1)
                
        else:
            print("❌ Failed to start game with monitoring")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Game stopped by user")
    except Exception as e:
        print(f"❌ Error starting game: {e}")
        sys.exit(1)
    finally:
        if monitor:
            monitor.stop_monitoring()

if __name__ == '__main__':
    main() 