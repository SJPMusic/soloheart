#!/usr/bin/env python3
"""
Test script to verify improved vibe code character creation functionality.
"""

import sys
import os

# Add the solo_heart directory to the path
sys.path.append('SoloHeart')
sys.path.append('.')

def test_vibe_code_character_creation():
    """Test that the vibe code character creation properly tracks conversation state."""
    
    print("🧪 Testing Improved Vibe Code Character Creation")
    print("=" * 60)
    
    try:
        from simple_unified_interface import SimpleCharacterGenerator
        
        # Initialize character generator
        generator = SimpleCharacterGenerator()
        
        # Test 1: Start character creation
        print("📝 Test 1: Starting character creation...")
        result = generator.start_character_creation("I want to create a Human Fighter named Thorin")
        
        if result['success']:
            print(f"✅ Started successfully: {result['message'][:100]}...")
        else:
            print(f"❌ Failed to start: {result['message']}")
            return False
        
        # Test 2: Continue with more details
        print("\n📝 Test 2: Adding more character details...")
        result = generator.continue_conversation("I want to be a Folk Hero background")
        
        if result['success']:
            print(f"✅ Continued successfully: {result['message'][:100]}...")
        else:
            print(f"❌ Failed to continue: {result['message']}")
            return False
        
        # Test 3: Add personality details
        print("\n📝 Test 3: Adding personality details...")
        result = generator.continue_conversation("I'm brave and loyal, with a strong sense of justice")
        
        if result['success']:
            print(f"✅ Added personality: {result['message'][:100]}...")
        else:
            print(f"❌ Failed to add personality: {result['message']}")
            return False
        
        # Test 4: Check if it asks for race again (should not)
        print("\n📝 Test 4: Testing if it remembers race...")
        result = generator.continue_conversation("What else do you need to know?")
        
        if result['success']:
            print(f"✅ Response: {result['message'][:200]}...")
            
            # Check if it asks for race again
            if "race" in result['message'].lower() and "human" not in result['message'].lower():
                print("⚠️  Warning: AI might be asking for race again")
            else:
                print("✅ Good: AI seems to remember the race")
        else:
            print(f"❌ Failed: {result['message']}")
            return False
        
        # Test 5: Complete character creation
        print("\n📝 Test 5: Completing character creation...")
        result = generator.continue_conversation("I think that's everything, complete the character")
        
        if result['success']:
            print(f"✅ Completion response: {result['message'][:200]}...")
            
            if result['is_complete']:
                print("✅ Character creation marked as complete!")
                
                # Test 6: Extract character data
                print("\n📝 Test 6: Extracting character data...")
                character_data = generator.get_character_data()
                
                if character_data:
                    print("✅ Character data extracted successfully!")
                    print(f"   Name: {character_data.get('name', 'Unknown')}")
                    print(f"   Race: {character_data.get('race', 'Unknown')}")
                    print(f"   Class: {character_data.get('class', 'Unknown')}")
                    print(f"   Background: {character_data.get('background', 'Unknown')}")
                    print(f"   Personality: {character_data.get('personality', 'Unknown')[:50]}...")
                else:
                    print("❌ Failed to extract character data")
                    return False
            else:
                print("⚠️  Character creation not marked as complete")
        else:
            print(f"❌ Failed to complete: {result['message']}")
            return False
        
        print("\n🎉 Vibe Code Character Creation Test Completed Successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        return False

if __name__ == "__main__":
    success = test_vibe_code_character_creation()
    sys.exit(0 if success else 1) 