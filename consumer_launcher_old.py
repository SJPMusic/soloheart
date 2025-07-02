#!/usr/bin/env python3
"""
Consumer-Friendly Launcher for SoloHeart
Simple setup and launch for non-technical users.
"""

import subprocess
import sys
import time
import os
import webbrowser

def main():
    print("🎲 SoloHeart - AI Adventure Game")
    print("=" * 40)
    
    # Check if .env exists and has API key
    if not os.path.exists('.env'):
        print("🔑 First time setup - you need an OpenAI API key")
        print("Get one at: https://platform.openai.com/api-keys")
        api_key = input("Enter your API key (starts with 'sk-'): ").strip()
        
        if not api_key.startswith('sk-'):
            print("❌ Invalid API key format")
            return
            
        # Create .env file
        with open('.env', 'w') as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
            f.write("OPENAI_MODEL=gpt-4o-mini\n")
            f.write("FLASK_SECRET_KEY=your_secret_key_here\n")
            f.write("FLASK_ENV=production\n")
            f.write("DEBUG=False\n")
            f.write("HOST=0.0.0.0\n")
            f.write("PORT=5001\n")
        
        print("✅ Setup complete!")
    
    print("🚀 Starting game...")
    
    # Start the game
    try:
        process = subprocess.Popen([sys.executable, 'start_screen_interface.py'])
        time.sleep(3)
        
        print("✅ Game started!")
        print("🌐 Opening in browser...")
        webbrowser.open('http://localhost:5001')
        
        print("\n🎮 How to play:")
        print("1. Click 'Start New Campaign'")
        print("2. Choose 'Natural Language' for character creation")
        print("3. Describe your character concept")
        print("4. Start your adventure!")
        print("\n🛑 Press Ctrl+C to stop")
        
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping game...")
        process.terminate()
        print("✅ Game stopped!")

if __name__ == '__main__':
    main() 