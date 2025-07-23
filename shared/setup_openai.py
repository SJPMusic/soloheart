#!/usr/bin/env python3
"""
Gemma3 LLM Service Setup for SoloHeart

This script helps you set up Gemma3 for local LLM functionality.
"""

import requests
import json

def setup_gemma3_service():
    """Set up Gemma3 LLM service"""
    print("🤖 Gemma3 LLM Service Setup for SoloHeart")
    print("=" * 50)
    
    # Check if LM Studio is running
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json().get('data', [])
            model_names = [model.get('id', '') for model in models]
            if any('gemma' in name.lower() for name in model_names):
                print("✅ Gemma3 service found with Gemma3 model")
                print(f"   Available models: {model_names}")
                return True
            else:
                print("⚠️  Gemma3 service found but Gemma3 model not available")
                print("Please load a Gemma3 model in LM Studio")
                return False
        else:
            print("❌ Gemma3 service not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Gemma3 service: {e}")
        print("Please make sure LM Studio is running: https://lmstudio.ai")
        return False
    
    print("\n📋 To use local LLM responses, you need Gemma3 with a Gemma3 model.")
    print("\n🔧 How to set up Gemma3:")
    print("1. Install LM Studio from https://lmstudio.ai")
    print("2. Start LM Studio")
    print("3. Load a Gemma3 model in LM Studio")
    print("\n💰 Cost: Free - runs entirely on your local machine")
    
    # Save to .env file
    env_file = Path('.env')
    if env_file.exists():
        # Read existing .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Check if GEMMA3_MODEL already exists
        model_exists = any(line.startswith('GEMMA3_MODEL=') for line in lines)
        
        if model_exists:
            # Update existing line
            with open(env_file, 'w') as f:
                for line in lines:
                    if line.startswith('GEMMA3_MODEL='):
                        f.write('GEMMA3_MODEL=gemma3\n')
                    else:
                        f.write(line)
        else:
            # Add new line
            with open(env_file, 'a') as f:
                f.write('\nGEMMA3_MODEL=gemma3\n')
                f.write('GEMMA3_BASE_URL=http://localhost:1234\n')
    else:
        # Create new .env file
        with open(env_file, 'w') as f:
            f.write('GEMMA3_MODEL=gemma3\n')
            f.write('GEMMA3_BASE_URL=http://localhost:1234\n')
    
    print(f"✅ Gemma3 configuration saved to .env file")
    print("\n🎮 You can now run the game with:")
    print("   python solo_heart/simple_unified_interface.py")
    
    return True

def test_gemma3_connection():
    """Test the Gemma3 connection"""
    try:
        from gemma3_llm_service import chat_completion
        
        # Simple test call
        response = chat_completion([
            {"role": "user", "content": "Say 'Hello, SoloHeart world!'"}
        ], max_tokens=10)
        
        print("✅ Gemma3 connection successful!")
        print(f"Test response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Gemma3 connection failed: {e}")
        return False

if __name__ == "__main__":
    if setup_gemma3_service():
        print("\n🧪 Testing connection...")
        test_gemma3_connection()
    else:
        print("\n❌ Setup incomplete. Please try again.") 