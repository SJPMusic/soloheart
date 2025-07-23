#!/usr/bin/env python3
"""
Test script for step-by-step character creation
"""

import requests
import json
import time

def test_step_by_step_creation():
    """Test the complete step-by-step character creation flow."""
    
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    def add_delay():
        """Add a small delay to ensure session persistence."""
        time.sleep(0.1)
    
    print("🧪 Testing Step-by-Step Character Creation")
    print("=" * 50)
    
    # Step 1: Start character creation
    print("1. Starting character creation...")
    response = session.post(f"{base_url}/api/character/step-by-step/start", 
                           json={"user_input": "I want to create a character"})
    
    if response.status_code != 200:
        print(f"❌ Failed to start: {response.status_code}")
        return False
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Start failed: {data.get('message')}")
        return False
    
    print(f"✅ Started: {data.get('message', '')[:100]}...")
    
    # Step 2: Answer race
    print("\n2. Answering race...")
    response = session.post(f"{base_url}/api/character/step-by-step/continue", 
                           json={"user_input": "Human"})
    
    if response.status_code != 200:
        print(f"❌ Failed to continue: {response.status_code}")
        return False
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Continue failed: {data.get('message')}")
        return False
    
    print(f"✅ Race answered: {data.get('message', '')[:100]}...")
    print(f"   Progress: {data.get('progress', 0)}/9")
    
    add_delay()
    
    # Step 3: Answer class
    print("\n3. Answering class...")
    response = session.post(f"{base_url}/api/character/step-by-step/continue", 
                           json={"user_input": "Fighter"})
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Class failed: {data.get('message')}")
        return False
    
    print(f"✅ Class answered: {data.get('message', '')[:100]}...")
    print(f"   Progress: {data.get('progress', 0)}/9")
    
    add_delay()
    
    # Step 4: Answer gender
    print("\n4. Answering gender...")
    response = session.post(f"{base_url}/api/character/step-by-step/continue", 
                           json={"user_input": "Male"})
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Gender failed: {data.get('message')}")
        return False
    
    print(f"✅ Gender answered: {data.get('message', '')[:100]}...")
    print(f"   Progress: {data.get('progress', 0)}/9")
    
    add_delay()
    
    # Step 5: Answer age
    print("\n5. Answering age...")
    response = session.post(f"{base_url}/api/character/step-by-step/continue", 
                           json={"user_input": "25"})
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Age failed: {data.get('message')}")
        return False
    
    print(f"✅ Age answered: {data.get('message', '')[:100]}...")
    print(f"   Progress: {data.get('progress', 0)}/9")
    
    add_delay()
    
    # Step 6: Answer background
    print("\n6. Answering background...")
    response = session.post(f"{base_url}/api/character/step-by-step/continue", 
                           json={"user_input": "Soldier"})
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Background failed: {data.get('message')}")
        return False
    
    print(f"✅ Background answered: {data.get('message', '')[:100]}...")
    print(f"   Progress: {data.get('progress', 0)}/9")
    
    add_delay()
    
    # Step 7: Answer personality
    print("\n7. Answering personality...")
    response = session.post(f"{base_url}/api/character/step-by-step/continue", 
                           json={"user_input": "Brave and loyal"})
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Personality failed: {data.get('message')}")
        return False
    
    print(f"✅ Personality answered: {data.get('message', '')[:100]}...")
    print(f"   Progress: {data.get('progress', 0)}/9")
    
    add_delay()
    
    # Step 8: Answer level
    print("\n8. Answering level...")
    response = session.post(f"{base_url}/api/character/step-by-step/continue", 
                           json={"user_input": "1"})
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Level failed: {data.get('message')}")
        return False
    
    print(f"✅ Level answered: {data.get('message', '')[:100]}...")
    print(f"   Progress: {data.get('progress', 0)}/9")
    
    add_delay()
    
    # Step 9: Answer alignment
    print("\n9. Answering alignment...")
    response = session.post(f"{base_url}/api/character/step-by-step/continue", 
                           json={"user_input": "Lawful Good"})
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Alignment failed: {data.get('message')}")
        return False
    
    print(f"✅ Alignment answered: {data.get('message', '')[:100]}...")
    print(f"   Progress: {data.get('progress', 0)}/9")
    
    add_delay()
    
    # Step 10: Answer name
    print("\n10. Answering name...")
    response = session.post(f"{base_url}/api/character/step-by-step/continue", 
                           json={"user_input": "Thorin Stonefist"})
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Name failed: {data.get('message')}")
        return False
    
    print(f"✅ Name answered: {data.get('message', '')[:100]}...")
    print(f"   Progress: {data.get('progress', 0)}/9")
    
    # Check if character creation is complete
    if data.get('is_complete') or "Character Creation Complete" in data.get('message', ''):
        print("\n🎉 Character creation completed successfully!")
        character_data = data.get('character_data', {})
        if character_data:
            print(f"📋 Character: {character_data.get('name', 'Unknown')} - {character_data.get('race', 'Unknown')} {character_data.get('class', 'Unknown')}")
        else:
            print(f"📋 Character created successfully!")
        return True
    else:
        print("\n⚠️  Character creation not complete")
        return False

if __name__ == "__main__":
    success = test_step_by_step_creation()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        exit(1) 