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

def start_server(script_name, port, description):
    """Start a Flask server in a subprocess."""
    try:
        print(f"🚀 Starting {description} on port {port}...")
        process = subprocess.Popen([
            sys.executable, script_name
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        if process.poll() is None:
            print(f"✅ {description} started successfully!")
            return process
        else:
            print(f"❌ Failed to start {description}")
            return None
    except Exception as e:
        print(f"❌ Error starting {description}: {e}")
        return None

def main():
    print("🎲 SoloHeart - AI Adventure Game")
    print("=" * 40)
    
    # Check if .env exists and configure Gemma3
    if not os.path.exists('.env'):
        print("🔧 First time setup - configuring Gemma3 LLM service")
        print("Make sure LM Studio is running with Gemma3 model available")
        print("Install LM Studio from: https://lmstudio.ai")
        print("Then load a Gemma3 model in LM Studio")
        
        # Create .env file with Gemma3 configuration
        with open('.env', 'w') as f:
            f.write("GEMMA3_MODEL=gemma3\n")
            f.write("GEMMA3_BASE_URL=http://localhost:1234/v1\n")
            f.write("GEMMA3_ENDPOINT=http://localhost:1234/v1/chat/completions\n")
        
        print("✅ Gemma3 configuration complete!")
        print("💡 Make sure LM Studio is running before starting the game")
    
    print("🚀 Starting game servers...")
    
    # Start both servers
    try:
        # Start the start screen interface (port 5001)
        start_screen_process = start_server(
            'start_screen_interface.py', 
            5001, 
            'Game Launcher'
        )
        
        if not start_screen_process:
            print("❌ Failed to start game launcher. Please try again.")
            return
        
        # Start the narrative interface (port 5002)
        narrative_process = start_server(
            'narrative_focused_interface.py', 
            5002, 
            'Game Engine'
        )
        
        if not narrative_process:
            print("❌ Failed to start game engine. Please try again.")
            start_screen_process.terminate()
            return
        
        print("✅ Both game servers started!")
        print("🌐 Opening game in browser...")
        webbrowser.open('http://localhost:5001')
        
        print("\n🎮 How to play:")
        print("1. Click 'Start New Campaign'")
        print("2. Choose 'Natural Language' for character creation")
        print("3. Describe your character concept")
        print("4. Start your adventure!")
        print("\n🛑 Press Ctrl+C to stop")
        
        # Keep both processes running
        try:
            while True:
                time.sleep(1)
                
                # Check if either process has died
                if start_screen_process.poll() is not None:
                    print("❌ Game launcher stopped unexpectedly")
                    break
                    
                if narrative_process.poll() is not None:
                    print("❌ Game engine stopped unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutting down game servers...")
            
            # Terminate both processes
            if start_screen_process:
                start_screen_process.terminate()
                start_screen_process.wait()
                
            if narrative_process:
                narrative_process.terminate()
                narrative_process.wait()
                
            print("✅ Game stopped!")
        
    except Exception as e:
        print(f"❌ Error starting game: {e}")
        print("Please try again.")

if __name__ == '__main__':
    main()
