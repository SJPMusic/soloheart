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
import requests

def check_ollama():
    """Check if Ollama is running and has the required model."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            if 'llama3:latest' in model_names:
                print("✅ Ollama is running with llama3 model")
                return True
            else:
                print("⚠️ Ollama is running but llama3 model not found")
                print("💡 Pulling llama3 model...")
                subprocess.run(["ollama", "pull", "llama3"], check=True)
                print("✅ llama3 model ready")
                return True
        else:
            print("❌ Ollama health check failed")
            return False
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def setup_environment():
    """Set up the Python environment and install dependencies."""
    print("🔧 Setting up Python environment...")
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    # Determine the pip path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
        python_path = os.path.join('venv', 'Scripts', 'python')
    else:  # Unix/Linux/macOS
        pip_path = os.path.join('venv', 'bin', 'pip')
        python_path = os.path.join('venv', 'bin', 'python')
    
    # Install dependencies
    print("📦 Installing dependencies...")
    requirements_file = 'solo_heart/requirements.txt'
    if os.path.exists(requirements_file):
        subprocess.run([pip_path, "install", "-r", requirements_file], check=True)
    else:
        # Fallback to main requirements.txt
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    
    return python_path

def main():
    print("🎲 SoloHeart - AI Adventure Game")
    print("=" * 40)
    
    # Check if .env exists and configure Ollama
    if not os.path.exists('.env'):
        print("🔧 First time setup - configuring Ollama LLM service")
        print("Make sure Ollama is running with LLaMA 3 model available")
        print("Install Ollama from: https://ollama.ai")
        print("Then run: ollama pull llama3")
        
        # Create .env file with Ollama configuration
        with open('.env', 'w') as f:
            f.write("OLLAMA_MODEL=llama3\n")
            f.write("OLLAMA_BASE_URL=http://localhost:11434\n")
            f.write("FLASK_SECRET_KEY=your_secret_key_here\n")
            f.write("FLASK_ENV=production\n")
            f.write("DEBUG=False\n")
            f.write("HOST=0.0.0.0\n")
            f.write("PORT=5001\n")
        
        print("✅ Ollama configuration complete!")
        print("💡 Make sure Ollama is running before starting the game")
    
    # Check Ollama
    if not check_ollama():
        print("\n❌ Ollama is not running or not properly configured")
        print("Please:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Start Ollama: brew services start ollama (macOS) or ollama serve")
        print("3. Pull the model: ollama pull llama3")
        print("4. Run this launcher again")
        return
    
    # Set up Python environment
    try:
        python_path = setup_environment()
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set up environment: {e}")
        return
    
    print("🚀 Starting game...")
    
    # Start the game
    try:
        # Set environment variables
        env = os.environ.copy()
        env['FLASK_APP'] = 'solo_heart/simple_unified_interface.py'
        env['FLASK_ENV'] = 'production'
        
        process = subprocess.Popen(
            [python_path, 'solo_heart/simple_unified_interface.py'],
            env=env
        )
        
        # Wait a bit for the server to start
        time.sleep(5)
        
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
    except Exception as e:
        print(f"❌ Failed to start game: {e}")

if __name__ == '__main__':
    main() 