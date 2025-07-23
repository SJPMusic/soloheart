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

def check_gemma3_service():
    """Check if Gemma3 service is available."""
    try:
        import requests
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json().get('data', [])
            model_names = [model.get('id', '') for model in models]
            if any('gemma' in name.lower() for name in model_names):
                print("✅ Gemma3 service found with Gemma3 model")
                return True
            else:
                print("⚠️  Gemma3 service found but Gemma3 model not available")
                print("Please load a Gemma3 model in LM Studio")
                return False
        else:
            print("❌ Gemma3 service not responding")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Gemma3 service: {e}")
        print("Please make sure LM Studio is running: https://lmstudio.ai")
        return False
    except Exception as e:
        print(f"❌ Cannot connect to Gemma3 service: {e}")
        print("Please make sure LM Studio is running: https://lmstudio.ai")
        return False

def main():
    """Main launcher function."""
    print("🎲 SoloHeart - Unified Narrative Interface")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Gemma3 service
    if not check_gemma3_service():
        print("\nGemma3 service is required for AI features. Please start LM Studio first.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
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
