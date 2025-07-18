#!/usr/bin/env python3
"""
Simple test for character generator
"""

import os
import sys
from simple_unified_interface import SimpleCharacterGenerator

def test_character_generator():
    print("Testing character generator...")
    
    generator = SimpleCharacterGenerator()
    
    # Test starting character creation
    print("Starting character creation...")
    result = generator.start_character_creation("A brave warrior", "test")
    print(f"Result: {result}")
    
    if result['success']:
        print("Success! Character creation started.")
    else:
        print(f"Failed: {result['message']}")

if __name__ == "__main__":
    test_character_generator() 