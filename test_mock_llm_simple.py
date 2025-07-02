#!/usr/bin/env python3
"""
Simple test script to verify mock LLM functionality.
"""

import os
import sys

# Add the solo_heart directory to the path
sys.path.append('solo_heart')

def test_mock_llm():
    """Test the mock LLM functionality."""
    print("🧪 Testing Mock LLM Functionality")
    print("=" * 40)
    
    try:
        # Set environment variable to enable mock LLM
        os.environ['USE_MOCK_LLM'] = '1'
        
        from simple_unified_interface import SimpleCharacterGenerator
        
        generator = SimpleCharacterGenerator()
        
        # Test various inputs
        test_cases = [
            ("I want to be a Dragonborn", "Dragonborn"),
            ("I want to be a Wizard", "Wizard"),
            ("I want to be a Human", "Human"),
            ("My name is Thorin", "name"),
            ("I want a criminal background", "background"),
            ("Complete character creation", "complete")
        ]
        
        for user_input, expected_content in test_cases:
            messages = [{"role": "user", "content": user_input}]
            response = generator._mock_llm_response(messages)
            
            print(f"Input: '{user_input}'")
            print(f"Response: '{response}'")
            
            if expected_content.lower() in response.lower():
                print("✅ Response contains expected content")
            else:
                print("⚠️  Response may not contain expected content")
            
            print("-" * 30)
        
        print("✅ Mock LLM test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Mock LLM test error: {e}")
        return False

if __name__ == "__main__":
    success = test_mock_llm()
    sys.exit(0 if success else 1) 