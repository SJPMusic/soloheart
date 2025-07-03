#!/usr/bin/env python3
"""
Test script to verify character creation endpoint is working
"""

import requests
import json
import time

def test_character_creation():
    """Test the character creation endpoint"""
    
    print("🧪 Testing Character Creation Endpoint")
    print("=" * 50)
    
    # Test data
    test_data = {
        "description": "I want to create a brave human fighter named Thorin who is a noble warrior",
        "campaign_name": "Test Campaign"
    }
    
    try:
        print("📡 Making request to /api/character/vibe-code/start...")
        print(f"📝 Test data: {test_data}")
        
        # Make the request
        response = requests.post(
            "http://localhost:5001/api/character/vibe-code/start",
            json=test_data,
            timeout=60  # 60 second timeout
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📄 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {json.dumps(result, indent=2)}")
            
            # Assert HTTP 200
            assert response.status_code == 200, f"Expected HTTP 200, got {response.status_code}"
            
            if result.get('success'):
                print("🎉 Character creation started successfully!")
                
                # Verify the response includes race/class prompt
                message = result.get('message', '')
                if 'race' in message.lower() or 'class' in message.lower():
                    print("✅ Response includes race/class prompt")
                else:
                    print("⚠️  Response may not include race/class prompt")
                    print(f"Message content: {message[:200]}...")
                
                return True
            else:
                print(f"❌ Character creation failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running on port 5001?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_utility_functions():
    """Test the utility functions directly"""
    
    print("\n🧪 Testing Utility Functions Directly")
    print("=" * 50)
    
    try:
        from utils.character_fact_extraction import extract_race_from_text, extract_class_from_text
        
        # Test race extraction
        race_tests = [
            ("I am a Half-Elf ranger", "Half-Elf"),
            ("My character is a Dragonborn", "Dragonborn"),
            ("I'm an elf", "Elf"),
            ("Half-elf", "Half-Elf"),
            ("Tiefling", "Tiefling"),
            ("I want to be a Half-Orc barbarian", "Half-Orc"),
            ("I'm a human fighter", "Human"),
            ("Dwarf cleric", "Dwarf")
        ]
        
        for input_text, expected_race in race_tests:
            result = extract_race_from_text(input_text)
            if result == expected_race:
                print(f"   ✅ PASS: '{input_text}' → {result}")
            else:
                print(f"   ❌ FAIL: '{input_text}' → {result} (expected {expected_race})")
                return False
        
        # Test class extraction
        class_tests = [
            ("I am a Half-Elf ranger", "Ranger"),
            ("My character is a Dragonborn barbarian", "Barbarian"),
            ("I'm an elf wizard", "Wizard"),
            ("Half-elf rogue", "Rogue"),
            ("Tiefling warlock", "Warlock"),
            ("I want to be a Half-Orc fighter", "Fighter"),
            ("I'm a human cleric", "Cleric"),
            ("Dwarf paladin", "Paladin")
        ]
        
        for input_text, expected_class in class_tests:
            result = extract_class_from_text(input_text)
            if result == expected_class:
                print(f"   ✅ PASS: '{input_text}' → {result}")
            else:
                print(f"   ❌ FAIL: '{input_text}' → {result} (expected {expected_class})")
                return False
        
        print("   ✅ All utility function tests passed!")
        return True
        
    except ImportError as e:
        print(f"   ❌ FAIL: Could not import utility functions: {e}")
        return False
    except Exception as e:
        print(f"   ❌ FAIL: Error testing utility functions: {e}")
        return False

def test_race_extraction():
    """Test race extraction logic with various inputs"""
    
    print("\n🧪 Testing Race Extraction Logic")
    print("=" * 50)
    
    test_cases = [
        {
            "input": "I am a Half-Elf ranger",
            "expected": "Half-Elf",
            "description": "Half-Elf should be detected, not Elf"
        },
        {
            "input": "My character is a Dragonborn",
            "expected": "Dragonborn", 
            "description": "Dragonborn should be detected correctly"
        },
        {
            "input": "I'm an elf",
            "expected": "Elf",
            "description": "Elf should be detected correctly"
        },
        {
            "input": "Half-elf",
            "expected": "Half-Elf",
            "description": "Simple Half-elf input should work"
        },
        {
            "input": "Tiefling",
            "expected": "Tiefling",
            "description": "Tiefling should be detected correctly"
        },
        {
            "input": "I want to be a Half-Orc barbarian",
            "expected": "Half-Orc",
            "description": "Half-Orc should be detected, not Orc"
        },
        {
            "input": "I'm a human fighter",
            "expected": "Human",
            "description": "Human should be detected correctly"
        },
        {
            "input": "Dwarf cleric",
            "expected": "Dwarf",
            "description": "Dwarf should be detected correctly"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"   Input: '{test_case['input']}'")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            # Start character creation
            start_response = requests.post(
                "http://localhost:5001/api/character/vibe-code/start",
                json={"description": "Test character", "campaign_name": "Test Campaign"},
                timeout=30
            )
            
            if start_response.status_code != 200:
                print(f"   ❌ Failed to start character creation: {start_response.status_code}")
                all_passed = False
                continue
            
            # Continue with race input
            continue_response = requests.post(
                "http://localhost:5001/api/character/vibe-code/continue",
                json={"user_input": test_case['input']},
                timeout=30
            )
            
            if continue_response.status_code == 200:
                result = continue_response.json()
                if result.get('success'):
                    # Check if the response indicates the correct race was detected
                    message = result.get('message', '').lower()
                    expected_lower = test_case['expected'].lower()
                    
                    # Look for confirmation of the expected race
                    if f"you are a {expected_lower}" in message or f"excellent! you are a {expected_lower}" in message:
                        print(f"   ✅ PASS: Correctly detected {test_case['expected']}")
                    else:
                        print(f"   ❌ FAIL: Expected {test_case['expected']}, but response doesn't confirm it")
                        print(f"   Response: {result.get('message', '')[:100]}...")
                        all_passed = False
                else:
                    print(f"   ❌ FAIL: Request failed: {result.get('message', 'Unknown error')}")
                    all_passed = False
            else:
                print(f"   ❌ FAIL: HTTP {continue_response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ FAIL: Exception: {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("🚀 Starting character creation endpoint test...")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Test utility functions first
    utility_success = test_utility_functions()
    
    # Test race extraction
    race_success = test_race_extraction()
    
    # Test main character creation flow
    creation_success = test_character_creation()
    
    if utility_success and race_success and creation_success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure the server is running: python simple_unified_interface.py")
        print("2. Check that Ollama is running: ollama list")
        print("3. Verify port 5001 is free: lsof -i :5001")
        print("4. Check server logs for errors")
        print("5. Verify utility functions are working correctly") 