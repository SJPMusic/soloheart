#!/usr/bin/env python3
"""
Launcher for SoloHeart Game
Starts both the start screen interface and the game interface.
"""

import subprocess
import sys
import time
import os
import signal
import threading

def start_server(script_name, port, description):
    """Start a Flask server in a subprocess."""
    try:
        print(f"🚀 Starting {description} on port {port}...")
        process = subprocess.Popen([
            sys.executable, script_name
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Wait a moment for the server to start
        time.sleep(2)
        
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
    """Main launcher function."""
    print("🎲 SoloHeart Game Launcher")
    print("=" * 40)
    
    # Start the start screen interface (port 5001)
    start_screen_process = start_server(
        'start_screen_interface.py', 
        5001, 
        'Start Screen Interface'
    )
    
    if not start_screen_process:
        print("❌ Failed to start start screen interface. Exiting.")
        return
    
    # Start the game interface (port 5002)
    game_process = start_server(
        'narrative_focused_interface.py', 
        5002, 
        'Game Interface'
    )
    
    if not game_process:
        print("❌ Failed to start game interface. Exiting.")
        start_screen_process.terminate()
        return
    
    print("\n🎮 Game servers are running!")
    print("📱 Start Screen: http://localhost:5001")
    print("🎲 Game Interface: http://localhost:5002")
    print("\nPress Ctrl+C to stop all servers")
    
    try:
        # Keep the main process running
        while True:
            time.sleep(1)
            
            # Check if either process has died
            if start_screen_process.poll() is not None:
                print("❌ Start screen interface stopped unexpectedly")
                break
                
            if game_process.poll() is not None:
                print("❌ Game interface stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        
        # Terminate both processes
        if start_screen_process:
            start_screen_process.terminate()
            start_screen_process.wait()
            
        if game_process:
            game_process.terminate()
            game_process.wait()
            
        print("✅ All servers stopped")

if __name__ == '__main__':
    main() 