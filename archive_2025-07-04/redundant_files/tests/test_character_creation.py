#!/usr/bin/env python3
"""
Test script for character creation and race detection
"""

import requests
import json
import time

def test_character_creation():
    """Test the character creation flow."""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Character Creation Flow")
    print("=" * 50)
    
    # Test 1: Start character creation
    print("1. Starting character creation...")
    response = requests.post(f"{base_url}/api/character/vibe-code/start", 
                           json={"description": "I want to create a character", "campaign_name": "Test Campaign"})
    
    if response.status_code != 200:
        print(f"❌ Failed to start character creation: {response.status_code}")
        return False
    
    data = response.json()
    print(f"✅ Started: {data.get('message', '')[:100]}...")
    
    # Test 2: Set race
    print("\n2. Setting race to Human...")
    response = requests.post(f"{base_url}/api/character/vibe-code/continue", 
                           json={"user_input": "I am a human"})
    
    if response.status_code != 200:
        print(f"❌ Failed to set race: {response.status_code}")
        return False
    
    data = response.json()
    print(f"✅ Response: {data.get('message', '')[:100]}...")
    
    # Test 3: Verify race was set
    print("\n3. Verifying race was set...")
    response = requests.post(f"{base_url}/api/character/vibe-code/continue", 
                           json={"user_input": "What race am I?"})
    
    if response.status_code != 200:
        print(f"❌ Failed to verify race: {response.status_code}")
        return False
    
    data = response.json()
    message = data.get('message', '')
    print(f"✅ Response: {message[:200]}...")
    
    # Check if race is mentioned in the response
    if 'human' in message.lower():
        print("✅ Race detection working!")
    else:
        print("⚠️ Race not clearly mentioned in response")
    
    # Test 4: Get character data
    print("\n4. Getting character data...")
    response = requests.post(f"{base_url}/api/character/vibe-code/complete", 
                           json={})
    
    if response.status_code != 200:
        print(f"❌ Failed to get character data: {response.status_code}")
        return False
    
    data = response.json()
    character_data = data.get('character_data', {})
    
    if character_data.get('race', '').lower() == 'human':
        print("✅ Character data shows Human race!")
        print(f"   Character: {character_data.get('name', 'Unknown')} the {character_data.get('race', 'Unknown')} {character_data.get('class', 'Unknown')}")
    else:
        print(f"⚠️ Character data shows race as: {character_data.get('race', 'Unknown')}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_character_creation()
        if success:
            print("\n🎉 Character creation test completed successfully!")
        else:
            print("\n❌ Character creation test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}") 