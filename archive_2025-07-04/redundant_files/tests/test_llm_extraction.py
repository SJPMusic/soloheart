#!/usr/bin/env python3
"""
Test script for LLM-driven character fact extraction.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_unified_interface import SimpleCharacterGenerator

def test_llm_extraction():
    """Test the LLM-driven character fact extraction."""
    
    # Create a character generator instance
    generator = SimpleCharacterGenerator()
    
    # Test cases with different character descriptions
    test_cases = [
        {
            "name": "Seraphina - Half-Elf Rogue",
            "description": "My character is Seraphina. She's a 23-year-old half-elf who grew up in a monastery high in the mountains. Trained as a healer, she abandoned her vows after discovering the monks were keeping dangerous secrets buried beneath the chapel. She now wanders with only a worn traveler's cloak, a hidden dagger, and an old journal filled with cryptic prophecies. Seraphina is gentle by nature but quick to act when others are in danger. She's searching for truth—and perhaps redemption."
        },
        {
            "name": "Kaelen - Human Fighter",
            "description": "My character is Kaelen. He's 35, a former blacksmith who lost everything when his forge was burned down in a raid. He has a badly scarred left arm and a deep distrust of authority. Kaelen carries a massive hammer—his own creation—and wears a leather apron like armor. He doesn't call himself a warrior, but when things go bad, he's the first to step in. He's loyal to those who earn it, and he's searching for the raiders who destroyed his home, hoping for justice… or revenge."
        },
        {
            "name": "John - Simple Human",
            "description": "My character is John. He is 19 years old. His parents were murdered by bandits when he was young. He is a human fighter who wields his father's sword and carries his mother's prayer pendant."
        }
    ]
    
    print("🤖 Testing LLM-Driven Character Fact Extraction")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        print(f"Input: {test_case['description'][:100]}...")
        
        # Extract facts using LLM
        result = generator._extract_and_commit_facts_immediately(test_case['description'])
        
        print(f"\n✅ Committed Facts:")
        for fact_type, value in result['committed'].items():
            print(f"  {fact_type}: {value}")
        
        print(f"\n📊 Character Data Summary:")
        char_data = generator.get_character_data()
        for key, value in char_data.items():
            if value and value not in [None, "", [], {}]:
                print(f"  {key}: {value}")
        
        # Reset for next test
        generator = SimpleCharacterGenerator()
        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_llm_extraction() 