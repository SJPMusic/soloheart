#!/usr/bin/env python3
"""
Status checker for SoloHeart
Quickly check if the game server is running and healthy.
"""

import requests
import sys
import json
from datetime import datetime

def check_server_status():
    """Check the status of the SoloHeart game server."""
    print("🔍 Checking SoloHeart server status...")
    print("=" * 40)
    
    # Check if server is responding
    try:
        response = requests.get("http://localhost:5001/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding")
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - is it running?")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False
    
    # Check health endpoint
    try:
        health_response = requests.get("http://localhost:5001/api/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health check passed: {health_data['status']}")
            print(f"   Ollama: {'✅' if health_data['ollama_healthy'] else '❌'}")
            print(f"   Game: {'✅' if health_data['game_healthy'] else '❌'}")
            print(f"   Timestamp: {health_data['timestamp']}")
        else:
            print(f"❌ Health check failed with status {health_response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to health endpoint")
    except Exception as e:
        print(f"❌ Error checking health: {e}")
    
    # Check Ollama directly
    try:
        ollama_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if ollama_response.status_code == 200:
            models = ollama_response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            if 'llama3' in model_names or 'llama3:latest' in model_names:
                print("✅ Ollama is running with llama3 model")
            else:
                print("⚠️ Ollama is running but llama3 model not found")
                print("💡 Run: ollama pull llama3")
        else:
            print("❌ Ollama health check failed")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
    
    print("\n🌐 Game should be available at: http://localhost:5001")
    return True

def main():
    """Main function."""
    if check_server_status():
        print("\n✅ SoloHeart is running properly!")
        sys.exit(0)
    else:
        print("\n❌ SoloHeart is not running properly")
        print("💡 Try starting with: python launch_with_monitor.py")
        sys.exit(1)

if __name__ == '__main__':
    main() 