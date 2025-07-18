#!/usr/bin/env python3
"""
Test script for the LLM character generator
"""

import os
from character_generator import CharacterGenerator

def test_character_generator():
    """Test the character generator functionality."""
    print("🧪 Testing LLM Character Generator...")
    
    # Check if OpenAI API key is available
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("   Please set your OpenAI API key to test the LLM integration")
        return
    
    # Initialize the generator
    generator = CharacterGenerator()
    
    if not generator.client:
        print("❌ Failed to initialize OpenAI client")
        return
    
    print("✅ OpenAI client initialized successfully")
    
    # Test 1: Start character creation
    print("\n1. Testing character creation start...")
    test_description = "I want to play a wise old dwarf cleric who's been a healer in his mountain community for decades. He's gruff but kind-hearted, with a long white beard and carries a holy symbol of Moradin."
    
    result = generator.start_character_creation(test_description, "Test Campaign")
    
    if result['success']:
        print("   ✅ Character creation started successfully")
        print(f"   DM Response: {result['message'][:100]}...")
        print(f"   Is Complete: {result['is_complete']}")
    else:
        print("   ❌ Failed to start character creation")
        return
    
    # Test 2: Continue conversation
    print("\n2. Testing conversation continuation...")
    follow_up = "He's not very strong but has great wisdom and healing magic. He's been through many battles and has a deep respect for life."
    
    result = generator.continue_conversation(follow_up)
    
    if result['success']:
        print("   ✅ Conversation continued successfully")
        print(f"   DM Response: {result['message'][:100]}...")
        print(f"   Is Complete: {result['is_complete']}")
    else:
        print("   ❌ Failed to continue conversation")
    
    # Test 3: Check character data
    print("\n3. Testing character data retrieval...")
    character_data = generator.get_character_data()
    
    if character_data:
        print("   ✅ Character data retrieved")
        print(f"   Name: {character_data.get('name', 'Unknown')}")
        print(f"   Class: {character_data.get('class', 'Unknown')}")
        print(f"   Race: {character_data.get('race', 'Unknown')}")
    else:
        print("   ❌ No character data available")
    
    print("\n✅ Character generator test completed!")

if __name__ == '__main__':
    test_character_generator() 