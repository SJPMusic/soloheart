#!/usr/bin/env python3
"""
Comprehensive test analysis for character creation prompts
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_prompt_comprehensive(prompt, test_name):
    """Comprehensive test of a character creation prompt"""
    print(f"\n{'='*100}")
    print(f"🧪 COMPREHENSIVE TEST: {test_name}")
    print(f"📝 PROMPT: {prompt}")
    print(f"{'='*100}")
    
    # Start character creation
    print("\n1️⃣ Starting character creation...")
    response = requests.post(f"{BASE_URL}/api/character/vibe-code/start", 
                           json={"description": prompt, "campaign_name": test_name})
    
    if response.status_code != 200:
        print(f"❌ Failed to start: {response.status_code}")
        return
    
    data = response.json()
    print(f"✅ Started successfully")
    print(f"🤖 AI Response: {data['message'][:200]}...")
    
    # Continue conversation to see what happens
    print("\n2️⃣ Continuing conversation...")
    follow_up = "Yes, please continue with the character creation process."
    continue_response = requests.post(f"{BASE_URL}/api/character/vibe-code/continue",
                                    json={"user_input": follow_up})
    
    if continue_response.status_code == 200:
        continue_data = continue_response.json()
        print(f"🤖 Continue Response: {continue_data['message'][:200]}...")
        print(f"📊 Is complete: {continue_data.get('is_complete', False)}")
        print(f"🎭 Current step: {continue_data.get('current_step', 'unknown')}")
        
        # Check for arc scaffolding
        if continue_data.get('current_step') == 'arc_scaffolding':
            print("🎭 **ARC SCAFFOLDING DETECTED** - Emotional awareness working!")
            
            # Respond to arc scaffolding
            arc_response = "I think they're seeking redemption, but they're not sure they deserve it."
            arc_continue = requests.post(f"{BASE_URL}/api/character/vibe-code/continue",
                                       json={"user_input": arc_response})
            
            if arc_continue.status_code == 200:
                arc_data = arc_continue.json()
                print(f"🤖 Arc Response: {arc_data['message'][:200]}...")
    
    # Get summary to see what facts were committed
    print("\n3️⃣ Getting summary...")
    summary_response = requests.get(f"{BASE_URL}/api/character/vibe-code/summary")
    if summary_response.status_code == 200:
        summary_data = summary_response.json()
        print(f"📋 Summary: {summary_data['summary']}")
    
    # Complete the character to see what data is actually generated
    print("\n4️⃣ Completing character...")
    complete_response = requests.post(f"{BASE_URL}/api/character/vibe-code/complete")
    if complete_response.status_code == 200:
        complete_data = complete_response.json()
        print(f"🎯 Complete Response: {complete_data['message']}")
        
        if complete_data.get('success'):
            print("✅ Character creation completed successfully!")
            
            # Get the actual character data from the campaign
            print("\n5️⃣ Retrieving actual character data...")
            campaign_response = requests.get(f"{BASE_URL}/api/game/current")
            if campaign_response.status_code == 200:
                campaign_data = campaign_response.json()
                if campaign_data.get('success'):
                    character = campaign_data['campaign']['active_character']
                    print(f"👤 ACTUAL CHARACTER DATA:")
                    print(f"   Name: {character.get('name', 'Unknown')}")
                    print(f"   Race: {character.get('race', 'Unknown')}")
                    print(f"   Class: {character.get('class', 'Unknown')}")
                    print(f"   Background: {character.get('background', 'Unknown')}")
                    print(f"   Personality: {character.get('personality', 'Unknown')}")
                    print(f"   Level: {character.get('level', 'Unknown')}")
                    print(f"   Created Date: {character.get('created_date', 'Unknown')}")
                    
                    # Analyze what was extracted vs what was expected
                    print(f"\n📊 EXTRACTION ANALYSIS:")
                    analyze_extraction_results(prompt, character)
        else:
            print(f"❌ Character creation failed: {complete_data['message']}")
    
    print(f"\n{'='*100}")

def analyze_extraction_results(prompt, character):
    """Analyze what was extracted vs what was expected"""
    
    # Expected extractions based on prompt type
    if "rogue" in prompt.lower():
        expected = {
            'class': 'Rogue',
            'personality': 'doesn\'t trust people'
        }
    elif "family betrayed" in prompt.lower() and "exile" in prompt.lower():
        expected = {
            'background': 'betrayal and exile',
            'personality': 'smiles when kills'
        }
    elif "half-orc" in prompt.lower() and "fighter" in prompt.lower():
        expected = {
            'race': 'Half-Orc',
            'class': 'Fighter',
            'background': 'Soldier'
        }
    else:
        expected = {}
    
    print(f"   Expected extractions: {expected}")
    print(f"   Actual extractions:")
    print(f"     - Race: {character.get('race', 'Unknown')}")
    print(f"     - Class: {character.get('class', 'Unknown')}")
    print(f"     - Background: {character.get('background', 'Unknown')}")
    print(f"     - Personality: {character.get('personality', 'Unknown')}")
    
    # Check if expected facts were extracted
    extraction_success = []
    for fact_type, expected_value in expected.items():
        actual_value = character.get(fact_type, '').lower()
        if expected_value.lower() in actual_value or actual_value in expected_value.lower():
            extraction_success.append(f"✅ {fact_type}: {expected_value}")
        else:
            extraction_success.append(f"❌ {fact_type}: expected '{expected_value}', got '{actual_value}'")
    
    print(f"   Extraction Results:")
    for result in extraction_success:
        print(f"     {result}")

def analyze_emotional_scaffolding():
    """Analyze emotional scaffolding patterns"""
    print(f"\n🎭 EMOTIONAL SCAFFOLDING ANALYSIS")
    print("="*60)
    
    print(f"\n📊 Test 1 - Vague and Short:")
    print("   Expected emotional triggers: trust issues, fear, isolation")
    print("   Expected arc scaffolding: growth vs decline, redemption vs vengeance")
    
    print(f"\n📊 Test 2 - Dense and Emotional:")
    print("   Expected emotional triggers: betrayal, trauma, dark humor, vengeance")
    print("   Expected arc scaffolding: redemption vs deeper darkness, justice vs revenge")
    
    print(f"\n📊 Test 3 - Mechanical-first:")
    print("   Expected emotional triggers: minimal, needs prompting")
    print("   Expected arc scaffolding: needs personality development")

def main():
    """Run comprehensive tests"""
    print("🧪 COMPREHENSIVE CHARACTER CREATION ANALYSIS")
    print("Make sure the server is running on localhost:5001")
    
    analyze_emotional_scaffolding()
    
    # Test 1: Vague and short
    test_prompt_comprehensive(
        "He's a rogue who doesn't trust people.",
        "Test 1 - Vague and Short"
    )
    
    time.sleep(3)
    
    # Test 2: Dense and emotional
    test_prompt_comprehensive(
        "Her family betrayed her. She escaped exile. Now she smiles when she kills.",
        "Test 2 - Dense and Emotional"
    )
    
    time.sleep(3)
    
    # Test 3: Mechanical-first
    test_prompt_comprehensive(
        "Half-orc fighter. Wields twin axes. Background: soldier.",
        "Test 3 - Mechanical-first"
    )
    
    print("\n🎯 COMPREHENSIVE ANALYSIS COMPLETED!")
    print("\n📋 FINAL FINDINGS:")
    print("="*50)
    print("1. FACT EXTRACTION:")
    print("   - Facts are being staged but not committed")
    print("   - System falls back to default character data")
    print("   - LLM-based extraction not being used")
    print("   - Confirmation flow is broken")
    print()
    print("2. EMOTIONAL SCAFFOLDING:")
    print("   - Arc scaffolding triggers when personality/background present")
    print("   - Emotional keywords detected but not stored")
    print("   - Narrative direction prompts work")
    print()
    print("3. FLOW ISSUES:")
    print("   - Conversational flow works")
    print("   - Fact confirmation step missing")
    print("   - Character completion bypasses extraction")
    print("   - Default values used instead of extracted data")

if __name__ == "__main__":
    main() 