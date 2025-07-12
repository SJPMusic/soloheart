#!/usr/bin/env python3
"""
Ollama LLM Service Setup for SoloHeart
======================================

This script helps you set up Ollama for local LLM functionality.
"""

import os
import getpass
from pathlib import Path

def setup_ollama_service():
    """Set up Ollama LLM service"""
    print("🤖 Ollama LLM Service Setup for SoloHeart")
    print("=" * 50)
    
    # Check if Ollama is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            if 'llama3' in model_names:
                print("✅ Ollama service found with LLaMA 3 model")
                print("You can now run the game with local LLM responses!")
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
    
    print("\n📋 To use local LLM responses, you need Ollama with LLaMA 3.")
    print("\n🔧 How to set up Ollama:")
    print("1. Install Ollama from https://ollama.ai")
    print("2. Start Ollama service")
    print("3. Pull the LLaMA 3 model: ollama pull llama3")
    print("\n💰 Cost: Free - runs entirely on your local machine")
    
    # Save to .env file
    env_file = Path('.env')
    if env_file.exists():
        # Read existing .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Check if OLLAMA_MODEL already exists
        model_exists = any(line.startswith('OLLAMA_MODEL=') for line in lines)
        
        if model_exists:
            # Update existing line
            with open(env_file, 'w') as f:
                for line in lines:
                    if line.startswith('OLLAMA_MODEL='):
                        f.write('OLLAMA_MODEL=llama3\n')
                    else:
                        f.write(line)
        else:
            # Add new line
            with open(env_file, 'a') as f:
                f.write('\nOLLAMA_MODEL=llama3\n')
                f.write('OLLAMA_BASE_URL=http://localhost:11434\n')
    else:
        # Create new .env file
        with open(env_file, 'w') as f:
            f.write('OLLAMA_MODEL=llama3\n')
            f.write('OLLAMA_BASE_URL=http://localhost:11434\n')
    
    print(f"✅ Ollama configuration saved to .env file")
    print("\n🎮 You can now run the game with:")
    print("   python solo_heart/simple_unified_interface.py")
    
    return True

def test_ollama_connection():
    """Test the Ollama connection"""
    try:
        from llm_interface.provider_factory import chat_completion
        
        # Simple test call
        response = chat_completion([
            {"role": "user", "content": "Say 'Hello, SoloHeart world!'"}
        ], max_tokens=10)
        
        print("✅ Ollama connection successful!")
        print(f"Test response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

if __name__ == "__main__":
    if setup_ollama_service():
        print("\n🧪 Testing connection...")
        test_ollama_connection()
    else:
        print("\n❌ Setup incomplete. Please try again.") 