#!/usr/bin/env python3
"""
Launcher for the Unified SoloHeart Narrative Interface
"""

import os
import sys
import subprocess
import webbrowser
import time

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import requests
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install flask requests")
        return False

def check_ollama_service():
    """Check if Ollama service is available."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            if 'llama3' in model_names:
                print("✅ Ollama service found with LLaMA 3 model")
                return True
            else:
                print("⚠️  Ollama service found but LLaMA 3 model not available")
                print("Please run: ollama pull llama3")
                return False
        else:
            print("❌ Ollama service not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama service: {e}")
        print("Please make sure Ollama is running: https://ollama.ai")
        return False

def main():
    """Main launcher function."""
    print("🎲 SoloHeart - Unified Narrative Interface")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Ollama service
    if not check_ollama_service():
        print("\nOllama service is required for AI features. Please start Ollama first.")
        return
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n🚀 Starting the game server...")
    
    try:
        # Start the Flask server
        from unified_narrative_interface import app
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5001')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("✅ Game started!")
        print("🌐 Opening in browser...")
        print("�� How to play:")
        print("1. Click 'Start New Campaign'")
        print("2. Choose 'Vibe Code' for natural language character creation")
        print("3. Describe your character concept")
        print("4. Start your adventure!")
        print("🛑 Press Ctrl+C to stop")
        
        # Run the Flask app
        app.run(debug=False, host='0.0.0.0', port=5001)
        
    except KeyboardInterrupt:
        print("\n🛑 Game stopped by user")
    except Exception as e:
        print(f"❌ Error starting game: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
