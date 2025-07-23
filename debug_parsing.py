#!/usr/bin/env python3
"""
Debug script to test step-by-step parsing logic
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'game_app'))

from character_creator.step_by_step_mode import StepByStepCharacterCreator

def test_parsing():
    """Test the parsing logic directly."""
    
    print("🧪 Testing Step-by-Step Parsing Logic")
    print("=" * 50)
    
    # Create a step-by-step creator
    creator = StepByStepCharacterCreator()
    
    # Test cases
    test_cases = [
        ("race", "Human"),
        ("race", "Elf"),
        ("class", "Fighter"),
        ("class", "Wizard"),
        ("gender", "Male"),
        ("gender", "Female"),
        ("age", "25"),
        ("background", "Soldier"),
        ("personality", "Brave and loyal"),
        ("level", "1"),
        ("alignment", "Lawful Good"),
        ("name", "Thorin Stonefist")
    ]
    
    for field, user_input in test_cases:
        print(f"\nTesting: field='{field}', input='{user_input}'")
        
        # Test the parsing
        result = creator._parse_response(field, user_input)
        print(f"  Result: {result}")
        
        if result:
            print(f"  ✅ SUCCESS: Parsed '{user_input}' as '{result}' for field '{field}'")
        else:
            print(f"  ❌ FAILED: Could not parse '{user_input}' for field '{field}'")

if __name__ == "__main__":
    test_parsing() 