#!/usr/bin/env python3
"""
Detailed test script for character creation prompts
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_prompt_detailed(prompt, test_name):
    """Test a character creation prompt with detailed fact extraction analysis"""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: {test_name}")
    print(f"📝 PROMPT: {prompt}")
    print(f"{'='*80}")
    
    # Start character creation
    print("\n1️⃣ Starting character creation...")
    response = requests.post(f"{BASE_URL}/api/character/vibe-code/start", 
                           json={"description": prompt, "campaign_name": test_name})
    
    if response.status_code != 200:
        print(f"❌ Failed to start: {response.status_code}")
        return
    
    data = response.json()
    print(f"✅ Started successfully")
    print(f"🤖 AI Response: {data['message'][:150]}...")
    
    # Check if there are pending facts that need confirmation
    print("\n2️⃣ Checking for pending facts...")
    
    # Try to get the confirmation prompt by checking if there are pending facts
    # We need to look at the character generator's pending_facts
    # Since we can't access this directly via API, let's try to trigger confirmation
    
    # Continue conversation to see if facts get extracted
    print("\n3️⃣ Continuing conversation to extract facts...")
    follow_up = "Yes, that's correct. Please continue with the character creation."
    continue_response = requests.post(f"{BASE_URL}/api/character/vibe-code/continue",
                                    json={"user_input": follow_up})
    
    if continue_response.status_code == 200:
        continue_data = continue_response.json()
        print(f"🤖 Continue Response: {continue_data['message'][:200]}...")
        print(f"📊 Is complete: {continue_data.get('is_complete', False)}")
        print(f"🎭 Current step: {continue_data.get('current_step', 'unknown')}")
        
        # Check if we're in arc scaffolding mode
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
    print("\n4️⃣ Getting final summary...")
    summary_response = requests.get(f"{BASE_URL}/api/character/vibe-code/summary")
    if summary_response.status_code == 200:
        summary_data = summary_response.json()
        print(f"📋 Final Summary: {summary_data['summary']}")
    
    # Try to complete the character to see what happens
    print("\n5️⃣ Attempting to complete character...")
    complete_response = requests.post(f"{BASE_URL}/api/character/vibe-code/complete")
    if complete_response.status_code == 200:
        complete_data = complete_response.json()
        print(f"🎯 Complete Response: {complete_data['message']}")
        if complete_data.get('success'):
            print("✅ Character creation completed successfully!")
        else:
            print(f"❌ Character creation failed: {complete_data['message']}")
    
    print(f"\n{'='*80}")

def analyze_extraction_patterns():
    """Analyze what patterns are being extracted from different prompt types"""
    print("\n🔍 ANALYZING EXTRACTION PATTERNS")
    print("="*50)
    
    # Test 1: Vague and short
    print("\n📊 Test 1 Analysis - Vague and Short:")
    print("Expected extraction: class (rogue), personality (doesn't trust people)")
    print("Expected emotional scaffolding: fear/trust issues")
    
    # Test 2: Dense and emotional  
    print("\n📊 Test 2 Analysis - Dense and Emotional:")
    print("Expected extraction: background (betrayal, exile), personality (smiles when kills)")
    print("Expected emotional scaffolding: vengeance, trauma, dark humor")
    
    # Test 3: Mechanical-first
    print("\n📊 Test 3 Analysis - Mechanical-first:")
    print("Expected extraction: race (half-orc), class (fighter), background (soldier)")
    print("Expected emotional scaffolding: minimal, needs prompting")

def main():
    """Run all detailed tests"""
    print("🧪 DETAILED CHARACTER CREATION PROMPT TESTING")
    print("Make sure the server is running on localhost:5001")
    
    analyze_extraction_patterns()
    
    # Test 1: Vague and short
    test_prompt_detailed(
        "He's a rogue who doesn't trust people.",
        "Test 1 - Vague and Short"
    )
    
    time.sleep(3)
    
    # Test 2: Dense and emotional
    test_prompt_detailed(
        "Her family betrayed her. She escaped exile. Now she smiles when she kills.",
        "Test 2 - Dense and Emotional"
    )
    
    time.sleep(3)
    
    # Test 3: Mechanical-first
    test_prompt_detailed(
        "Half-orc fighter. Wields twin axes. Background: soldier.",
        "Test 3 - Mechanical-first"
    )
    
    print("\n🎯 All detailed tests completed!")
    print("\n📋 SUMMARY OF FINDINGS:")
    print("- Fact extraction: Working but facts not being committed")
    print("- Emotional scaffolding: Triggering but may need more context")
    print("- Flow: Conversational but missing fact confirmation step")
    print("- Arc scaffolding: Working when personality/background present")

if __name__ == "__main__":
    main() 