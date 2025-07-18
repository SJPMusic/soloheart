#!/usr/bin/env python3
"""
Demonstration script for the enhanced Vibe Code character creation system.
Shows how to use mock LLM fallback, timestamp/source tagging, and undo functionality.
"""

import os
import sys
import json

# Add the solo_heart directory to the path
sys.path.append('SoloHeart')

def demo_mock_llm_fallback():
    """Demonstrate the mock LLM fallback functionality."""
    print("🎭 DEMO: Mock LLM Fallback")
    print("=" * 50)
    
    # Enable mock LLM
    os.environ['USE_MOCK_LLM'] = '1'
    
    from simple_unified_interface import SimpleCharacterGenerator
    
    generator = SimpleCharacterGenerator()
    
    print("Starting character creation with mock LLM...")
    result = generator.start_character_creation("I want to create a mysterious character")
    
    print(f"AI Response: {result['message']}")
    print(f"Success: {result['success']}")
    
    print("\nContinuing conversation...")
    result = generator.continue_conversation("I want to be a Dragonborn")
    
    print(f"AI Response: {result['message']}")
    print(f"Confirmed facts: {generator.confirmed_facts}")
    print(f"Character race: {generator.character_data.get('race')}")
    
    # Disable mock LLM
    os.environ['USE_MOCK_LLM'] = '0'
    
    print("\n✅ Mock LLM demo completed!")

def demo_timestamp_and_source_tagging():
    """Demonstrate timestamp and source tagging functionality."""
    print("\n🕒 DEMO: Timestamp and Source Tagging")
    print("=" * 50)
    
    from simple_unified_interface import SimpleCharacterGenerator, SimpleNarrativeBridge
    
    generator = SimpleCharacterGenerator()
    
    # Create a mock narrative bridge to capture memory entries
    class MockNarrativeBridge:
        def __init__(self):
            self.memory_entries = []
        
        def store_dnd_memory(self, content, memory_type, metadata, tags, emotional_context, primary_emotion, emotional_intensity, character_id):
            self.memory_entries.append({
                'content': content,
                'metadata': metadata,
                'tags': tags
            })
    
    mock_bridge = MockNarrativeBridge()
    generator.narrative_bridge = mock_bridge
    
    print("Committing character facts with different sources...")
    
    # Commit facts with different sources
    generator._commit_fact("race", "Elf", "player")
    generator._commit_fact("class", "Wizard", "AI")
    generator._commit_fact("name", "Gandalf", "correction")
    
    print(f"Memory entries created: {len(mock_bridge.memory_entries)}")
    
    for i, entry in enumerate(mock_bridge.memory_entries, 1):
        print(f"\nEntry {i}:")
        print(f"  Content: {entry['content']}")
        print(f"  Source: {entry['metadata']['source']}")
        print(f"  Timestamp: {entry['metadata']['timestamp']}")
        print(f"  Tags: {entry['tags']}")
    
    print("\n✅ Timestamp and source tagging demo completed!")

def demo_undo_functionality():
    """Demonstrate the undo functionality."""
    print("\n↩️  DEMO: Undo Functionality")
    print("=" * 50)
    
    from simple_unified_interface import SimpleCharacterGenerator
    
    generator = SimpleCharacterGenerator()
    
    print("Initial character state:")
    print(f"  Race: {generator.character_data.get('race')}")
    print(f"  Class: {generator.character_data.get('class')}")
    print(f"  Name: {generator.character_data.get('name')}")
    
    print("\nCommitting facts...")
    
    # Commit several facts
    generator._commit_fact("race", "Human", "player")
    print(f"  After committing Human: {generator.character_data.get('race')}")
    
    generator._commit_fact("class", "Fighter", "player")
    print(f"  After committing Fighter: {generator.character_data.get('class')}")
    
    generator._commit_fact("name", "Aragorn", "player")
    print(f"  After committing Aragorn: {generator.character_data.get('name')}")
    
    print(f"\nFact history length: {len(generator.fact_history)}")
    
    print("\nUndoing facts...")
    
    # Undo the last fact (name)
    undone = generator.undo_last_fact()
    if undone:
        fact_type, old_value = undone
        print(f"  Undid {fact_type}: {old_value}")
        print(f"  Current name: {generator.character_data.get('name')}")
    
    # Undo the class
    undone = generator.undo_last_fact()
    if undone:
        fact_type, old_value = undone
        print(f"  Undid {fact_type}: {old_value}")
        print(f"  Current class: {generator.character_data.get('class')}")
    
    # Undo the race
    undone = generator.undo_last_fact()
    if undone:
        fact_type, old_value = undone
        print(f"  Undid {fact_type}: {old_value}")
        print(f"  Current race: {generator.character_data.get('race')}")
    
    print("\nFinal character state:")
    print(f"  Race: {generator.character_data.get('race')}")
    print(f"  Class: {generator.character_data.get('class')}")
    print(f"  Name: {generator.character_data.get('name')}")
    
    print("\n✅ Undo functionality demo completed!")

def demo_incremental_fact_commitment():
    """Demonstrate incremental fact commitment."""
    print("\n📝 DEMO: Incremental Fact Commitment")
    print("=" * 50)
    
    from simple_unified_interface import SimpleCharacterGenerator
    
    generator = SimpleCharacterGenerator()
    
    print("Starting character creation...")
    
    # Simulate a conversation where facts are detected and committed
    conversation_pairs = [
        ("I want to be a Dragonborn", "You are a Dragonborn. What class would you like?"),
        ("I want to be a Paladin", "You are a Dragonborn Paladin. What's your name?"),
        ("My name is Thorin", "Great name! What background do you want?"),
        ("I want a noble background", "Perfect! Character creation complete!")
    ]
    
    for user_input, ai_response in conversation_pairs:
        print(f"\nUser: {user_input}")
        print(f"AI: {ai_response}")
        
        # Detect and commit facts from this exchange
        generator._detect_and_commit_facts(user_input, ai_response)
        
        print(f"Confirmed facts: {generator.confirmed_facts}")
        print(f"Character data: {generator.character_data}")
    
    print("\nFinal character:")
    character_data = generator.get_character_data()
    for key, value in character_data.items():
        if key in ['name', 'race', 'class', 'background', 'personality']:
            print(f"  {key.title()}: {value}")
    
    print("\n✅ Incremental fact commitment demo completed!")

def main():
    """Run all demonstrations."""
    print("🎲 Enhanced Vibe Code Character Creation System Demo")
    print("=" * 70)
    print("This demo shows the new enhancements:")
    print("1. Mock LLM Fallback (for offline testing)")
    print("2. Timestamp and Source Tagging")
    print("3. Undo Last Character Fact")
    print("4. Incremental Fact Commitment")
    print("=" * 70)
    
    try:
        demo_mock_llm_fallback()
        demo_timestamp_and_source_tagging()
        demo_undo_functionality()
        demo_incremental_fact_commitment()
        
        print("\n" + "=" * 70)
        print("🎉 All demonstrations completed successfully!")
        print("\nTo use these features in your game:")
        print("1. Set USE_MOCK_LLM=1 for offline testing")
        print("2. Facts are automatically timestamped and source-tagged")
        print("3. Use the undo API endpoint to revert changes")
        print("4. Facts are committed incrementally as detected")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 