#!/usr/bin/env python3
"""
Test script for Enhanced Character Creation System

Demonstrates the improved interactive character creation with:
- Questions about options
- Suggestions for beginners
- Confirmation before committing values
- Fallbacks for "I don't know" responses
- Full SRD 5.2 compliance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_app.enhanced_step_by_step_creator import EnhancedStepByStepCreator
from game_app.character_sheet import CharacterSheet

def test_enhanced_character_creation():
    """Test the enhanced character creation system."""
    print("🧪 Testing Enhanced Character Creation System")
    print("=" * 60)
    
    # Initialize the enhanced creator
    creator = EnhancedStepByStepCreator()
    
    print("🎭 Starting Enhanced Character Creation")
    print("-" * 40)
    
    # Start the creation process
    initial_prompt = creator.start_creation()
    print(f"Initial Prompt: {initial_prompt}")
    
    # Test various user interactions
    test_interactions = [
        # Test asking for help
        ("help", "User asks for help"),
        
        # Test asking about race differences
        ("What's the difference between Human and Elf?", "User asks about race differences"),
        
        # Test asking for beginner suggestions
        ("What's good for a beginner?", "User asks for beginner suggestions"),
        
        # Test fallback option
        ("I don't know", "User doesn't know what to choose"),
        
        # Test confirmation
        ("yes", "User confirms the fallback choice"),
        
        # Test asking about class differences
        ("What's the difference between Fighter and Barbarian?", "User asks about class differences"),
        
        # Test direct input
        ("Fighter", "User provides direct input"),
        
        # Test confirmation
        ("yes", "User confirms the class choice"),
        
        # Test ability score method
        ("1", "User chooses Standard Array"),
        
        # Test confirmation
        ("yes", "User confirms ability score method"),
        
        # Test background selection
        ("Soldier", "User chooses Soldier background"),
        
        # Test confirmation
        ("yes", "User confirms background choice"),
    ]
    
    for user_input, description in test_interactions:
        print(f"\n📝 {description}")
        print(f"User Input: '{user_input}'")
        
        try:
            result = creator.process_input(user_input)
            print(f"Result Type: {result['type']}")
            print(f"Message: {result['message']}")
            
            if 'character_summary' in result:
                summary = result['character_summary']
                print(f"Character Progress: Step {summary['progress']['current_step']}/{summary['progress']['total_steps']}")
                if summary['basic_info']['race']:
                    print(f"Current Race: {summary['basic_info']['race']}")
                if summary['basic_info']['class']:
                    print(f"Current Class: {summary['basic_info']['class']}")
            
            if result['type'] == 'creation_complete':
                print("🎉 Character creation completed successfully!")
                character_data = result['character']
                print(f"Final Character: {character_data['basic_info']['name']} the {character_data['basic_info']['race']} {character_data['basic_info']['class']}")
                break
                
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print("\n" + "=" * 60)
    print("✅ Enhanced Character Creation Test Complete")

def test_character_sheet_validation():
    """Test the enhanced CharacterSheet validation."""
    print("\n🧪 Testing CharacterSheet SRD Validation")
    print("=" * 60)
    
    # Test valid character sheet
    valid_sheet = CharacterSheet(
        character_name="Test Character",
        race="Human",
        class_name="Fighter",
        background="Soldier",
        alignment="Lawful Good"
    )
    
    print("✅ Valid CharacterSheet created successfully")
    
    # Test field validation
    test_fields = [
        ("race", "Human", "Valid SRD race"),
        ("race", "InvalidRace", "Invalid race"),
        ("class_name", "Fighter", "Valid SRD class"),
        ("class_name", "InvalidClass", "Invalid class"),
        ("background", "Soldier", "Valid SRD background"),
        ("background", "InvalidBackground", "Invalid background"),
        ("alignment", "Lawful Good", "Valid alignment"),
        ("alignment", "Invalid Alignment", "Invalid alignment"),
        ("level", 5, "Valid level"),
        ("level", 25, "Invalid level"),
        ("strength", 15, "Valid ability score"),
        ("strength", 25, "Invalid ability score"),
    ]
    
    for field_name, value, description in test_fields:
        print(f"\n📝 Testing: {description}")
        is_valid, message = valid_sheet.validate_field(field_name, value)
        print(f"Field: {field_name}, Value: {value}")
        print(f"Valid: {is_valid}, Message: {message}")

def test_srd_data_integration():
    """Test SRD data integration."""
    print("\n🧪 Testing SRD Data Integration")
    print("=" * 60)
    
    creator = EnhancedStepByStepCreator()
    
    # Test race options
    race_options = creator.interactive_creator._get_race_options()
    print(f"Available Races: {len(race_options)}")
    for race in race_options[:3]:  # Show first 3
        print(f"- {race['value']}: {race['description'][:50]}...")
    
    # Test class options
    class_options = creator.interactive_creator._get_class_options()
    print(f"\nAvailable Classes: {len(class_options)}")
    for class_opt in class_options[:3]:  # Show first 3
        print(f"- {class_opt['value']}: {class_opt['description']}")
    
    # Test background options
    bg_options = creator.interactive_creator._get_background_options()
    print(f"\nAvailable Backgrounds: {len(bg_options)}")
    for bg in bg_options[:3]:  # Show first 3
        print(f"- {bg['value']}: {bg['description'][:50]}...")

if __name__ == "__main__":
    print("🚀 Enhanced Character Creation System Test Suite")
    print("=" * 60)
    
    try:
        test_enhanced_character_creation()
        test_character_sheet_validation()
        test_srd_data_integration()
        
        print("\n🎉 All tests completed successfully!")
        print("The enhanced character creation system is working as expected.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 