#!/usr/bin/env python3
"""
Test script for the character schema and manager
"""

import json
from character_manager import CharacterManager
from character_sheet_renderer import CharacterSheetRenderer

def test_character_schema():
    """Test the character schema and manager functionality."""
    print("🧪 Testing Character Schema and Manager...")
    
    # Initialize components
    manager = CharacterManager()
    renderer = CharacterSheetRenderer()
    
    # Test 1: Create a basic character
    print("\n1. Testing character creation...")
    basic_info = {
        "name": "Thorgar Ironheart",
        "race": "Dwarf",
        "class": "Cleric",
        "background": "Acolyte",
        "alignment": "Lawful Good",
        "level": 1,
        "stats": {
            "strength": 12,
            "dexterity": 10,
            "constitution": 16,
            "intelligence": 13,
            "wisdom": 18,
            "charisma": 14
        }
    }
    
    character = manager.create_character(basic_info, "test_campaign")
    
    if character:
        print("   ✅ Character created successfully")
        print(f"   Name: {character['basic_info']['name']}")
        print(f"   Class: {character['basic_info']['class']}")
        print(f"   Level: {character['basic_info']['level']}")
    else:
        print("   ❌ Failed to create character")
        return
    
    # Test 2: Validate character
    print("\n2. Testing character validation...")
    is_valid = manager.validate_character(character)
    
    if is_valid:
        print("   ✅ Character validation passed")
    else:
        print("   ❌ Character validation failed")
        return
    
    # Test 3: Get character summary
    print("\n3. Testing character summary...")
    summary = manager.get_character_summary(character)
    
    print(f"   Character Summary:")
    print(f"   - Name: {summary['name']}")
    print(f"   - Race/Class: {summary['race']} {summary['class']}")
    print(f"   - Level: {summary['level']}")
    print(f"   - HP: {summary['hit_points']}/{summary['max_hit_points']}")
    print(f"   - AC: {summary['armor_class']}")
    print(f"   - Proficiency Bonus: +{summary['proficiency_bonus']}")
    
    # Test 4: Test character sheet rendering
    print("\n4. Testing character sheet rendering...")
    html = renderer.render_character_sheet(character)
    
    if html and len(html) > 1000:  # Basic check that HTML was generated
        print("   ✅ Character sheet HTML generated successfully")
        
        # Save HTML for inspection
        with open('test_character_sheet.html', 'w') as f:
            f.write(html)
        print("   📄 Character sheet saved to test_character_sheet.html")
    else:
        print("   ❌ Failed to generate character sheet HTML")
    
    # Test 5: Test character saving and loading
    print("\n5. Testing character save/load...")
    campaign_id = "test_campaign"
    
    # Save character
    save_success = manager.save_character(character, campaign_id)
    if save_success:
        print("   ✅ Character saved successfully")
    else:
        print("   ❌ Failed to save character")
        return
    
    # Load character
    loaded_character = manager.load_character(campaign_id)
    if loaded_character:
        print("   ✅ Character loaded successfully")
        print(f"   Loaded name: {loaded_character['basic_info']['name']}")
    else:
        print("   ❌ Failed to load character")
    
    # Test 6: Test character updates
    print("\n6. Testing character updates...")
    updates = {
        "basic_info": {
            "level": 2,
            "experience_points": 300
        },
        "combat_stats": {
            "hit_points": {
                "current": 18,
                "maximum": 18
            }
        }
    }
    
    updated_character = manager.update_character(character, updates)
    if updated_character:
        print("   ✅ Character updated successfully")
        print(f"   New level: {updated_character['basic_info']['level']}")
        print(f"   New HP: {updated_character['combat_stats']['hit_points']['current']}")
    else:
        print("   ❌ Failed to update character")
    
    print("\n✅ Character schema and manager test completed!")

if __name__ == '__main__':
    test_character_schema() 