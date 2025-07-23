#!/usr/bin/env python3
"""
Test session persistence
"""

import requests
import json

def test_session():
    """Test if sessions are working."""
    
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    print("🧪 Testing Session Persistence")
    print("=" * 50)
    
    # Test 1: Start step-by-step
    print("1. Starting step-by-step...")
    response = session.post(f"{base_url}/api/character/step-by-step/start", 
                           json={"user_input": "I want to create a character"})
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 2: Continue with race
    print("\n2. Continuing with race...")
    response = session.post(f"{base_url}/api/character/step-by-step/continue", 
                           json={"user_input": "Human"})
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 3: Check if session is maintained
    print("\n3. Testing session maintenance...")
    response = session.post(f"{base_url}/api/character/step-by-step/continue", 
                           json={"user_input": "Fighter"})
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

if __name__ == "__main__":
    test_session() 