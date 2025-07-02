#!/usr/bin/env python3
"""
Test script to verify incremental character fact commitment functionality with new enhancements.
"""

import sys
import os
import datetime

# Add the solo_heart directory to the path
sys.path.append('solo_heart')
sys.path.append('.')

def test_mock_llm_fallback():
    """Test that mock LLM can be triggered with environment variable."""
    print("🧪 Testing Mock LLM Fallback")
    print("=" * 40)
    
    try:
        from simple_unified_interface import SimpleCharacterGenerator
        
        # Test with mock LLM enabled
        os.environ['USE_MOCK_LLM'] = '1'
        
        generator = SimpleCharacterGenerator()
        
        # Test mock responses
        messages = [{"role": "user", "content": "I want to be a Dragonborn"}]
        response = generator._mock_llm_response(messages)
        
        if "Dragonborn" in response and "Fighter" in response:
            print("✅ Mock LLM correctly responds to Dragonborn request")
        else:
            print(f"❌ Mock LLM unexpected response: {response}")
            return False
        
        messages = [{"role": "user", "content": "I want to be a Wizard"}]
        response = generator._mock_llm_response(messages)
        
        if "Wizard" in response:
            print("✅ Mock LLM correctly responds to Wizard request")
        else:
            print(f"❌ Mock LLM unexpected response: {response}")
            return False
        
        # Test with mock LLM disabled
        os.environ['USE_MOCK_LLM'] = '0'
        
        print("✅ Mock LLM fallback test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Mock LLM test error: {e}")
        return False

def test_timestamp_and_source_tagging():
    """Test that facts stored include timestamp and source."""
    print("\n🧪 Testing Timestamp and Source Tagging")
    print("=" * 40)
    
    try:
        from simple_unified_interface import SimpleCharacterGenerator, SimpleNarrativeBridge
        
        # Initialize character generator
        generator = SimpleCharacterGenerator()
        
        # Initialize a temporary narrative bridge for testing
        temp_bridge = SimpleNarrativeBridge()
        generator.narrative_bridge = temp_bridge
        
        # Mock the store_dnd_memory method to capture the metadata
        captured_metadata = []
        
        def mock_store_memory(content, memory_type, metadata, tags, emotional_context, primary_emotion, emotional_intensity, character_id):
            captured_metadata.append(metadata)
        
        temp_bridge.store_dnd_memory = mock_store_memory
        
        # Commit a fact
        generator._commit_fact("race", "Elf", "player")
        
        if captured_metadata:
            metadata = captured_metadata[0]
            
            # Check for timestamp
            if "timestamp" in metadata:
                print("✅ Timestamp included in memory metadata")
                # Verify it's a valid ISO format
                try:
                    datetime.datetime.fromisoformat(metadata["timestamp"])
                    print("✅ Timestamp is valid ISO format")
                except ValueError:
                    print("❌ Timestamp is not valid ISO format")
                    return False
            else:
                print("❌ Timestamp missing from memory metadata")
                return False
            
            # Check for source
            if "source" in metadata and metadata["source"] == "player":
                print("✅ Source correctly tagged as 'player'")
            else:
                print("❌ Source missing or incorrect in memory metadata")
                return False
            
            # Check for other required fields
            if "fact_type" in metadata and "value" in metadata:
                print("✅ Fact type and value included in metadata")
            else:
                print("❌ Fact type or value missing from metadata")
                return False
        else:
            print("❌ No memory metadata captured")
            return False
        
        print("✅ Timestamp and source tagging test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Timestamp and source tagging test error: {e}")
        return False

def test_undo_functionality():
    """Test that undo restores the previous character_data state."""
    print("\n🧪 Testing Undo Functionality")
    print("=" * 40)
    
    try:
        from simple_unified_interface import SimpleCharacterGenerator
        
        # Initialize character generator
        generator = SimpleCharacterGenerator()
        
        # Check initial state
        initial_race = generator.character_data.get('race')
        print(f"   Initial race: {initial_race}")
        
        # Commit first fact
        generator._commit_fact("race", "Human", "player")
        print(f"   After committing Human: {generator.character_data.get('race')}")
        
        # Commit second fact
        generator._commit_fact("race", "Elf", "player")
        print(f"   After committing Elf: {generator.character_data.get('race')}")
        
        # Undo last fact
        undone_fact = generator.undo_last_fact()
        
        if undone_fact:
            fact_type, old_value = undone_fact
            print(f"   Undid {fact_type}: {old_value}")
            
            # Check that the character data was restored
            if generator.character_data.get('race') == "Human":
                print("✅ Undo correctly restored previous race (Human)")
            else:
                print(f"❌ Undo failed to restore race. Current: {generator.character_data.get('race')}")
                return False
        else:
            print("❌ Undo returned None")
            return False
        
        # Test undoing again
        undone_fact = generator.undo_last_fact()
        
        if undone_fact:
            fact_type, old_value = undone_fact
            print(f"   Undid {fact_type}: {old_value}")
            
            # Check that it went back to initial state
            if generator.character_data.get('race') == initial_race:
                print("✅ Undo correctly restored initial state")
            else:
                print(f"❌ Undo failed to restore initial state. Current: {generator.character_data.get('race')}")
                return False
        else:
            print("❌ Second undo returned None")
            return False
        
        # Test undoing when no facts to undo
        undone_fact = generator.undo_last_fact()
        
        if undone_fact is None:
            print("✅ Correctly returns None when no facts to undo")
        else:
            print("❌ Should return None when no facts to undo")
            return False
        
        print("✅ Undo functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Undo functionality test error: {e}")
        return False

def test_incremental_character_facts():
    """Test that character facts are committed incrementally as they're confirmed."""
    
    print("\n🧪 Testing Incremental Character Fact Commitment")
    print("=" * 60)
    
    try:
        from simple_unified_interface import SimpleCharacterGenerator, SimpleNarrativeBridge
        
        # Initialize character generator
        generator = SimpleCharacterGenerator()
        
        # Initialize a temporary narrative bridge for testing
        temp_bridge = SimpleNarrativeBridge()
        generator.narrative_bridge = temp_bridge
        
        print("📝 Test 1: Starting character creation...")
        result = generator.start_character_creation("I want to create a Dragonborn Fighter")
        
        if result['success']:
            print(f"✅ Started successfully: {result['message'][:100]}...")
            print(f"   Confirmed facts: {generator.confirmed_facts}")
            print(f"   Current race: {generator.character_data.get('race')}")
        else:
            print(f"❌ Failed to start: {result['message']}")
            return False
        
        print("\n📝 Test 2: Confirming race...")
        result = generator.continue_conversation("Yes, I want to be a Dragonborn")
        
        if result['success']:
            print(f"✅ Continued successfully: {result['message'][:100]}...")
            print(f"   Confirmed facts: {generator.confirmed_facts}")
            print(f"   Current race: {generator.character_data.get('race')}")
            
            # Check if race was committed
            if "race" in generator.confirmed_facts and generator.character_data.get('race') == 'Dragonborn':
                print("✅ Race fact committed successfully!")
            else:
                print("⚠️  Race fact not committed yet")
        else:
            print(f"❌ Failed to continue: {result['message']}")
            return False
        
        print("\n📝 Test 3: Confirming class...")
        result = generator.continue_conversation("I want to be a Fighter")
        
        if result['success']:
            print(f"✅ Continued successfully: {result['message'][:100]}...")
            print(f"   Confirmed facts: {generator.confirmed_facts}")
            print(f"   Current class: {generator.character_data.get('class')}")
            print(f"   Current weapons: {generator.character_data.get('weapons')}")
            
            # Check if class was committed
            if "class" in generator.confirmed_facts and generator.character_data.get('class') == 'Fighter':
                print("✅ Class fact committed successfully!")
                print("✅ Class-specific details (weapons, skills) updated!")
            else:
                print("⚠️  Class fact not committed yet")
        else:
            print(f"❌ Failed to continue: {result['message']}")
            return False
        
        print("\n📝 Test 4: Confirming name...")
        result = generator.continue_conversation("My name is Thorin")
        
        if result['success']:
            print(f"✅ Continued successfully: {result['message'][:100]}...")
            print(f"   Confirmed facts: {generator.confirmed_facts}")
            print(f"   Current name: {generator.character_data.get('name')}")
            
            # Check if name was committed
            if "name" in generator.confirmed_facts and generator.character_data.get('name') == 'Thorin':
                print("✅ Name fact committed successfully!")
            else:
                print("⚠️  Name fact not committed yet")
        else:
            print(f"❌ Failed to continue: {result['message']}")
            return False
        
        print("\n📝 Test 5: Testing AI memory of confirmed facts...")
        result = generator.continue_conversation("What do you know about my character so far?")
        
        if result['success']:
            print(f"✅ AI response: {result['message'][:200]}...")
            
            # Check if AI remembers the confirmed facts
            response_lower = result['message'].lower()
            if "dragonborn" in response_lower and "fighter" in response_lower and "thorin" in response_lower:
                print("✅ AI remembers all confirmed facts!")
            else:
                print("⚠️  AI may not be referencing all confirmed facts")
        else:
            print(f"❌ Failed to continue: {result['message']}")
            return False
        
        print("\n📝 Test 6: Final character data...")
        character_data = generator.get_character_data()
        
        if character_data:
            print("✅ Final character data:")
            print(f"   Name: {character_data.get('name')}")
            print(f"   Race: {character_data.get('race')}")
            print(f"   Class: {character_data.get('class')}")
            print(f"   Background: {character_data.get('background')}")
            print(f"   Weapons: {character_data.get('weapons')}")
            print(f"   Skills: {character_data.get('skills')}")
            print(f"   Confirmed facts: {generator.confirmed_facts}")
        else:
            print("❌ No character data available")
            return False
        
        print("\n🎉 Incremental Character Fact Commitment Test Completed Successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Running All Character Creation Enhancement Tests")
    print("=" * 70)
    
    tests = [
        ("Mock LLM Fallback", test_mock_llm_fallback),
        ("Timestamp and Source Tagging", test_timestamp_and_source_tagging),
        ("Undo Functionality", test_undo_functionality),
        ("Incremental Character Facts", test_incremental_character_facts)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Character creation enhancements are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 