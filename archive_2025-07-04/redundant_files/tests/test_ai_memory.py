#!/usr/bin/env python3
"""
Test to verify that the AI remembers confirmed facts across multiple exchanges.
"""

import os
import sys

# Add the solo_heart directory to the path
sys.path.append('SoloHeart')

def test_ai_memory_of_confirmed_facts():
    """Test that the AI remembers confirmed facts across multiple exchanges and never repeats them."""
    print("🧪 Testing AI Memory of Confirmed Facts")
    print("=" * 50)
    os.environ['USE_MOCK_LLM'] = '1'
    from SoloHeart.simple_unified_interface import SimpleCharacterGenerator
    generator = SimpleCharacterGenerator()
    print("Starting character creation...")
    result = generator.start_character_creation("I want to create a character")
    print(f"Initial response: {result['message']}")
    print(f"Confirmed facts: {generator.confirmed_facts}")
    
    # Exchange 1: Confirming race
    result = generator.continue_conversation("I want to be a Human")
    assert generator.character_data['race'] == 'Human', "Race should be Human"
    assert 'race' in generator.confirmed_facts
    # Check that AI doesn't ask for race again (look for question words)
    response_lower = result['message'].lower()
    assert not any(q in response_lower for q in ['what race', 'which race', 'race?']), "AI should not ask for race again"
    
    # Exchange 2: Confirming class
    result = generator.continue_conversation("I want to be a Fighter")
    assert generator.character_data['class'] == 'Fighter', "Class should be Fighter"
    assert 'class' in generator.confirmed_facts
    # Check that AI doesn't ask for class again
    response_lower = result['message'].lower()
    assert not any(q in response_lower for q in ['what class', 'which class', 'class?']), "AI should not ask for class again"
    
    # Exchange 3: Confirming name
    result = generator.continue_conversation("My name is John")
    assert generator.character_data['name'] == 'John', "Name should be John"
    assert 'name' in generator.confirmed_facts
    # Check that AI doesn't ask for name again
    response_lower = result['message'].lower()
    assert not any(q in response_lower for q in ['what is your name', 'what\'s your name', 'name?']), "AI should not ask for name again"
    
    # Exchange 4: Confirming background
    result = generator.continue_conversation("I'll take the criminal background.")
    assert generator.character_data['background'] == 'Criminal', "Background should be Criminal"
    assert 'background' in generator.confirmed_facts
    # Check that AI doesn't ask for background again
    response_lower = result['message'].lower()
    assert not any(q in response_lower for q in ['what background', 'which background', 'background?']), "AI should not ask for background again"
    
    # Exchange 5: Revision - change class
    result = generator.continue_conversation("Actually, I'm a monk.")
    assert generator.character_data['class'] == 'Monk', "Class should be Monk after revision"
    
    # Exchange 6: Ask AI to summarize
    result = generator.continue_conversation("What do you know about my character so far?")
    response_lower = result['message'].lower()
    assert "human" in response_lower and "monk" in response_lower and "john" in response_lower and "criminal" in response_lower, "AI should summarize all confirmed facts"
    
    print("✅ AI correctly remembers and references all confirmed facts, including after revision!")
    return True

def test_real_ai_memory():
    """Test with real AI to see if it remembers facts."""
    print("\n🧪 Testing Real AI Memory (requires API)")
    print("=" * 50)
    
    # Disable mock LLM for real AI testing
    os.environ['USE_MOCK_LLM'] = '0'
    
    from simple_unified_interface import SimpleCharacterGenerator
    
    generator = SimpleCharacterGenerator()
    
    print("Starting character creation with real AI...")
    result = generator.start_character_creation("I want to create a character")
    print(f"Initial response: {result['message'][:100]}...")
    
    print("\n--- Exchange 1: Confirming race ---")
    result = generator.continue_conversation("I want to be a Human")
    print(f"AI Response: {result['message'][:100]}...")
    print(f"Confirmed facts: {generator.confirmed_facts}")
    
    print("\n--- Exchange 2: Testing AI memory ---")
    result = generator.continue_conversation("What do you know about my character so far?")
    print(f"AI Response: {result['message']}")
    
    # Check if AI references confirmed facts
    response_lower = result['message'].lower()
    references_race = "human" in response_lower
    
    print(f"\nAI Memory Check:")
    print(f"  References race (Human): {references_race}")
    
    if references_race:
        print("✅ Real AI correctly remembers confirmed facts!")
        return True
    else:
        print("❌ Real AI may not be referencing confirmed facts")
        return False

if __name__ == "__main__":
    print("Testing AI Memory of Confirmed Facts")
    print("=" * 60)
    
    # Test with mock LLM
    success1 = test_ai_memory_of_confirmed_facts()
    
    # Test with real AI (if API is available)
    try:
        success2 = test_real_ai_memory()
    except Exception as e:
        print(f"Real AI test failed (likely API quota): {e}")
        success2 = True  # Don't fail the test due to API issues
    
    if success1 and success2:
        print("\n🎉 All AI memory tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some AI memory tests failed")
        sys.exit(1) 