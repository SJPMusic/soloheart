#!/usr/bin/env python3
"""
Test script for character creation prompts
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_prompt(prompt, test_name):
    """Test a character creation prompt and log results"""
    print(f"\n{'='*60}")
    print(f"TESTING: {test_name}")
    print(f"PROMPT: {prompt}")
    print(f"{'='*60}")
    
    # Start character creation
    print("\n1. Starting character creation...")
    response = requests.post(f"{BASE_URL}/api/character/vibe-code/start", 
                           json={"description": prompt, "campaign_name": test_name})
    
    if response.status_code != 200:
        print(f"❌ Failed to start: {response.status_code}")
        return
    
    data = response.json()
    print(f"✅ Started: {data['message'][:100]}...")
    
    # Get initial summary
    print("\n2. Getting initial summary...")
    summary_response = requests.get(f"{BASE_URL}/api/character/vibe-code/summary")
    if summary_response.status_code == 200:
        summary_data = summary_response.json()
        print(f"📋 Summary: {summary_data['summary']}")
    
    # Continue conversation with a follow-up
    print("\n3. Continuing conversation...")
    follow_up = "Tell me more about this character's background and motivations."
    continue_response = requests.post(f"{BASE_URL}/api/character/vibe-code/continue",
                                    json={"user_input": follow_up})
    
    if continue_response.status_code == 200:
        continue_data = continue_response.json()
        print(f"🤖 Response: {continue_data['message'][:200]}...")
        print(f"📊 Is complete: {continue_data.get('is_complete', False)}")
        print(f"🎭 Current step: {continue_data.get('current_step', 'unknown')}")
    
    # Get updated summary
    print("\n4. Getting updated summary...")
    summary_response = requests.get(f"{BASE_URL}/api/character/vibe-code/summary")
    if summary_response.status_code == 200:
        summary_data = summary_response.json()
        print(f"📋 Updated summary: {summary_data['summary']}")
    
    print(f"\n{'='*60}")

def main():
    """Run all tests"""
    print("🧪 Testing Character Creation Prompts")
    print("Make sure the server is running on localhost:5001")
    
    # Test 1: Vague and short
    test_prompt(
        "He's a rogue who doesn't trust people.",
        "Test 1 - Vague and Short"
    )
    
    time.sleep(2)
    
    # Test 2: Dense and emotional
    test_prompt(
        "Her family betrayed her. She escaped exile. Now she smiles when she kills.",
        "Test 2 - Dense and Emotional"
    )
    
    time.sleep(2)
    
    # Test 3: Mechanical-first
    test_prompt(
        "Half-orc fighter. Wields twin axes. Background: soldier.",
        "Test 3 - Mechanical-first"
    )
    
    print("\n🎯 All tests completed!")

if __name__ == "__main__":
    main() 