#!/usr/bin/env python3
"""
Launcher for the Unified Solo DnD 5E Narrative Interface
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
        import openai
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install flask openai")
        return False

def check_api_key():
    """Check if OpenAI API key is set."""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    print("✅ OpenAI API key found")
    return True

def main():
    """Main launcher function."""
    print("🎲 Solo DnD 5E - Unified Narrative Interface")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check API key
    if not check_api_key():
        print("\nYou can still run the game, but AI features will be limited.")
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
