#!/usr/bin/env python3
"""
Test to verify that the character creator remembers details when using the real OpenAI API.
"""

import os
import sys
import json

# Add the solo_heart directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SoloHeart'))

def test_real_api_character_memory():
    """Test that the character creator remembers details with real API."""
    print("🧠 Testing Real API Character Memory")
    print("=" * 50)
    
    # Set up environment to use real API
    os.environ['USE_MOCK_LLM'] = '0'
    from SoloHeart.simple_unified_interface import SimpleCharacterGenerator
    
    # Initialize character generator
    generator = SimpleCharacterGenerator()
    
    print("\n📝 Test 1: Initial character description with multiple details")
    print("-" * 50)
    
    # Start with a description that includes multiple character details
    result = generator.start_character_creation("I want to be an elven wizard named Gandalf with a sage background")
    print(f"Player: I want to be an elven wizard named Gandalf with a sage background")
    print(f"AI: {result['message']}")
    print(f"Confirmed facts: {generator.confirmed_facts}")
    print(f"Character data: {generator.character_data}")
    
    # Check if facts were detected and committed
    expected_facts = {'race', 'class', 'name', 'background'}
    detected_facts = generator.confirmed_facts
    print(f"Expected facts: {expected_facts}")
    print(f"Detected facts: {detected_facts}")
    
    if detected_facts.issuperset(expected_facts):
        print("✅ All expected facts were detected and committed!")
    else:
        missing = expected_facts - detected_facts
        print(f"❌ Missing facts: {missing}")
    
    print("\n📝 Test 2: Continue conversation - AI should not ask for confirmed details")
    print("-" * 50)
    
    # Continue the conversation
    result = generator.continue_conversation("I'm ready to start my adventure")
    print(f"Player: I'm ready to start my adventure")
    print(f"AI: {result['message']}")
    print(f"Confirmed facts: {generator.confirmed_facts}")
    
    # Check if the AI response mentions the confirmed details
    response_lower = result['message'].lower()
    mentions_elf = 'elf' in response_lower or 'elven' in response_lower
    mentions_wizard = 'wizard' in response_lower
    mentions_gandalf = 'gandalf' in response_lower
    mentions_sage = 'sage' in response_lower
    
    print(f"Mentions Elf: {mentions_elf}")
    print(f"Mentions Wizard: {mentions_wizard}")
    print(f"Mentions Gandalf: {mentions_gandalf}")
    print(f"Mentions Sage: {mentions_sage}")
    
    if mentions_elf and mentions_wizard and mentions_gandalf and mentions_sage:
        print("✅ AI correctly referenced all confirmed character details!")
    else:
        print("❌ AI did not reference all confirmed character details")
    
    print("\n📝 Test 3: Check character completion")
    print("-" * 50)
    
    is_complete = generator.is_character_complete()
    print(f"Character complete: {is_complete}")
    
    if is_complete:
        print("✅ Character is complete with all required details!")
        
        # Show character summary
        summary = generator.get_character_summary()
        print(f"\nCharacter Summary:\n{summary}")
    else:
        print("❌ Character is not complete")
        missing = generator._get_unknown_facts_list()
        print(f"Missing: {missing}")
    
    print("\n🎉 Test Complete!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        test_real_api_character_memory()
        print("\n✅ Real API character memory test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 