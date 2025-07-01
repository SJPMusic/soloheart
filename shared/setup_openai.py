#!/usr/bin/env python3
"""
OpenAI API Setup for DnD 5E AI-Powered Game
===========================================

This script helps you set up your OpenAI API key for the DnD game.
"""

import os
import getpass
from pathlib import Path

def setup_openai_api():
    """Set up OpenAI API key"""
    print("🤖 OpenAI API Setup for DnD 5E AI-Powered Game")
    print("=" * 50)
    
    # Check if API key already exists
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ OpenAI API key already found: {api_key[:8]}...")
        print("You can now run the game with ChatGPT-quality responses!")
        return True
    
    print("\n📋 To use ChatGPT-quality responses, you need an OpenAI API key.")
    print("\n🔑 How to get your API key:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Sign in or create an account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the key (it starts with 'sk-')")
    print("\n💰 Cost: Very cheap - typically $1-5/month for heavy usage")
    
    # Get API key from user
    print("\n" + "=" * 50)
    api_key = getpass.getpass("Enter your OpenAI API key (starts with 'sk-'): ").strip()
    
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format. API keys should start with 'sk-'")
        return False
    
    # Save to .env file
    env_file = Path('.env')
    if env_file.exists():
        # Read existing .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Check if OPENAI_API_KEY already exists
        api_key_exists = any(line.startswith('OPENAI_API_KEY=') for line in lines)
        
        if api_key_exists:
            # Update existing line
            with open(env_file, 'w') as f:
                for line in lines:
                    if line.startswith('OPENAI_API_KEY='):
                        f.write(f'OPENAI_API_KEY={api_key}\n')
                    else:
                        f.write(line)
        else:
            # Add new line
            with open(env_file, 'a') as f:
                f.write(f'\nOPENAI_API_KEY={api_key}\n')
    else:
        # Create new .env file
        with open(env_file, 'w') as f:
            f.write(f'OPENAI_API_KEY={api_key}\n')
    
    print(f"✅ API key saved to .env file")
    print("\n🎮 You can now run the game with:")
    print("   source venv/bin/activate && python3 gui_interface.py")
    
    return True

def test_openai_connection():
    """Test the OpenAI connection"""
    try:
        from openai import OpenAI
        client = OpenAI()
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Hello, DnD world!'"}],
            max_tokens=10
        )
        
        print("✅ OpenAI connection successful!")
        print(f"Test response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

if __name__ == "__main__":
    if setup_openai_api():
        print("\n🧪 Testing connection...")
        test_openai_connection()
    else:
        print("\n❌ Setup incomplete. Please try again.") 