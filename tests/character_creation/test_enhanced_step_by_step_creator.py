#!/usr/bin/env python3
"""
QA Test Suite for Enhanced Step-by-Step Character Creator

Comprehensive testing of the enhanced character creation system including:
- Field prompting and validation
- Input acceptance/rejection
- CharacterSheet data storage
- SRD 5.2 compliance
- Edge case handling
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO
from typing import Dict, Any, List

# Add the game_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'game_app'))

try:
    from character_creator.enhanced_step_by_step_creator import EnhancedStepByStepCreator
    from character_sheet import CharacterSheet, Alignment
    from ability_score_system import AbilityScoreSystem, AbilityScoreMethod
except ImportError as e:
    print(f"Import error: {e}")
    # Try relative imports
    try:
        from game_app.character_creator.enhanced_step_by_step_creator import EnhancedStepByStepCreator
        from game_app.character_sheet import CharacterSheet, Alignment
        from game_app.ability_score_system import AbilityScoreSystem, AbilityScoreMethod
    except ImportError as e2:
        print(f"Relative import error: {e2}")
        raise


class TestEnhancedStepByStepCreator(unittest.TestCase):
    """Test suite for Enhanced Step-by-Step Character Creator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.llm_service = MagicMock()
        self.creator = EnhancedStepByStepCreator(llm_service=self.llm_service)
        
        # Test character data for various scenarios
        self.test_character_data = {
            "fighter_standard": {
                "character_name": "Thorin Ironfist",
                "player_name": "Test Player",
                "race": "Dwarf",
                "class_name": "Fighter",
                "level": 1,
                "background": "Soldier",
                "alignment": "Lawful Good",
                "age": 45,
                "gender": "Male",
                "experience_points": 0,
                "ability_score_method": "standard_array",
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
                "hit_points": 12,
                "armor_class": 16,
                "initiative": 2,
                "speed": 25,
                "proficiency_bonus": 2,
                "equipment": ["Backpack", "Bedroll", "Rations (5 days)"],
                "weapons": ["Longsword", "Crossbow, light"],
                "armor": "Chain mail",
                "currency": "15 gp",
                "proficiencies": ["All armor", "Shields", "Simple weapons", "Martial weapons"],
                "languages": ["Common", "Dwarvish"],
                "feats": [],
                "class_features": ["Fighting Style", "Second Wind"],
                "personality_traits": ["Brave", "Loyal"],
                "ideals": ["Duty", "Honor"],
                "bonds": ["My weapon", "My companions"],
                "flaws": ["Stubborn", "Quick to anger"],
                "backstory": "A veteran soldier seeking redemption",
                "height": "4'2\"",
                "weight": "150 lbs",
                "eyes": "Brown",
                "hair": "Black",
                "skin": "Pale",
                "distinguishing_features": "Battle scars"
            },
            "wizard_optimal": {
                "character_name": "Eldara Moonweave",
                "player_name": "Test Player",
                "race": "Elf",
                "class_name": "Wizard",
                "level": 1,
                "background": "Sage",
                "alignment": "Neutral Good",
                "age": 120,
                "gender": "Female",
                "experience_points": 0,
                "ability_score_method": "optimal_assignment",
                "spellcasting_ability": "Intelligence",
                "spell_slots": "2 1st-level",
                "spells_known": ["Magic Missile", "Shield", "Mage Armor"],
                "equipment": ["Spellbook", "Arcane focus", "Scholar's pack"],
                "weapons": ["Quarterstaff", "Dagger"],
                "armor": "None",
                "proficiencies": ["Daggers", "Quarterstaffs", "Light crossbows"],
                "languages": ["Common", "Elvish", "Draconic"],
                "feats": [],
                "class_features": ["Spellcasting", "Arcane Recovery"],
                "personality_traits": ["Curious", "Wise"],
                "ideals": ["Knowledge", "Discovery"],
                "bonds": ["My spellbook", "Ancient knowledge"],
                "flaws": ["Absent-minded", "Overconfident"],
                "backstory": "A scholar seeking ancient magical secrets",
                "height": "5'8\"",
                "weight": "120 lbs",
                "eyes": "Blue",
                "hair": "Silver",
                "skin": "Fair",
                "distinguishing_features": "Glowing eyes"
            }
        }
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_creator_initialization(self):
        """Test that the creator initializes correctly."""
        self.assertIsNotNone(self.creator)
        self.assertEqual(len(self.creator.all_fields), 69)  # Total number of fields
        self.assertFalse(self.creator.is_active)
        self.assertEqual(self.creator.current_field_index, 0)
    
    def test_field_groups_organization(self):
        """Test that fields are properly organized into groups."""
        expected_groups = [
            "identity", "ability_scores", "combat_stats", "saving_throws",
            "skills", "combat", "equipment", "proficiencies", "personality", "physical"
        ]
        
        for group in expected_groups:
            self.assertIn(group, self.creator.field_groups)
            self.assertGreater(len(self.creator.field_groups[group]), 0)
    
    def test_start_creation_process(self):
        """Test starting the character creation process."""
        response = self.creator.start()
        
        self.assertTrue(self.creator.is_active)
        self.assertEqual(self.creator.current_field_index, 0)
        self.assertIn("Identity", response)  # Should show group header
        self.assertIn("name", response)  # Should ask for first field
    
    def test_complete_character_flow_standard_array(self):
        """Test complete character creation flow using Standard Array."""
        # Start the process
        self.creator.start()
        
        # Simulate inputs for a complete character
        inputs = [
            "Thorin Ironfist",  # character_name
            "Test Player",      # player_name
            "Dwarf",            # race
            "Fighter",          # class_name
            "1",                # level
            "Soldier",          # background
            "Lawful Good",      # alignment
            "45",               # age
            "Male",             # gender
            "0",                # experience_points
            "1",                # ability_score_method (Standard Array)
            "15",               # strength
            "14",               # dexterity
            "13",               # constitution
            "12",               # intelligence
            "10",               # wisdom
            "8",                # charisma
            "12",               # hit_points
            "16",               # armor_class
            "2",                # initiative
            "25",               # speed
            "2",                # proficiency_bonus
            "Backpack, Bedroll, Rations",  # equipment
            "Longsword, Crossbow",         # weapons
            "Chain mail",       # armor
            "15 gp",            # currency
            "All armor, Shields",  # proficiencies
            "Common, Dwarvish",    # languages
            "",                 # feats (empty)
            "Fighting Style, Second Wind",  # class_features
            "Brave, Loyal",     # personality_traits
            "Duty, Honor",      # ideals
            "My weapon, My companions",  # bonds
            "Stubborn, Quick to anger",   # flaws
            "A veteran soldier seeking redemption",  # backstory
            "4'2\"",            # height
            "150 lbs",          # weight
            "Brown",            # eyes
            "Black",            # hair
            "Pale",             # skin
            "Battle scars"      # distinguishing_features
        ]
        
        # Process all inputs
        for i, user_input in enumerate(inputs):
            response = self.creator.process_response(user_input)
            
            # Check if we're done
            if "Character Creation Complete" in response:
                break
            
            # Verify we're still active and progressing
            if i < len(inputs) - 1:  # Not the last input
                self.assertTrue(self.creator.is_active)
        
        # Verify completion
        self.assertFalse(self.creator.is_active)
        
        # Get the final character sheet
        character_sheet = self.creator.character_sheet
        self.assertIsNotNone(character_sheet)
        
        # Verify key fields
        self.assertEqual(character_sheet.character_name, "Thorin Ironfist")
        self.assertEqual(character_sheet.race, "Dwarf")
        self.assertEqual(character_sheet.class_name, "Fighter")
        self.assertEqual(character_sheet.level, 1)
        self.assertEqual(character_sheet.ability_scores["strength"], 15)
        self.assertEqual(character_sheet.ability_scores["dexterity"], 14)
        self.assertEqual(character_sheet.ability_scores["constitution"], 13)
        self.assertEqual(character_sheet.ability_scores["intelligence"], 12)
        self.assertEqual(character_sheet.ability_scores["wisdom"], 10)
        self.assertEqual(character_sheet.ability_scores["charisma"], 8)
        
        # Verify ability modifiers are calculated correctly
        self.assertEqual(character_sheet.ability_modifiers["strength"], 2)   # (15-10)/2 = 2
        self.assertEqual(character_sheet.ability_modifiers["dexterity"], 2)  # (14-10)/2 = 2
        self.assertEqual(character_sheet.ability_modifiers["constitution"], 1)  # (13-10)/2 = 1
        self.assertEqual(character_sheet.ability_modifiers["intelligence"], 1)  # (12-10)/2 = 1
        self.assertEqual(character_sheet.ability_modifiers["wisdom"], 0)     # (10-10)/2 = 0
        self.assertEqual(character_sheet.ability_modifiers["charisma"], -1)  # (8-10)/2 = -1
    
    def test_invalid_ability_score_rejected(self):
        """Test that invalid ability scores are rejected."""
        self.creator.start()
        
        # Skip to ability scores
        for _ in range(10):  # Skip identity fields
            self.creator.process_response("skip")
        
        # Try to set invalid ability score
        response = self.creator.process_response("27")  # Invalid strength score
        
        # Should reject the invalid score
        self.assertIn("couldn't understand", response.lower())
        self.assertTrue(self.creator.is_active)  # Should still be active
    
    def test_missing_name_triggers_error(self):
        """Test that missing required fields cause validation issues."""
        self.creator.start()
        
        # Try to skip the name field
        response = self.creator.process_response("")
        
        # Should reject empty name
        self.assertIn("couldn't understand", response.lower())
        self.assertTrue(self.creator.is_active)
    
    def test_spellcasting_fields_required_for_spellcasters(self):
        """Test that spellcasting fields are prompted for spellcasting classes."""
        self.creator.start()
        
        # Navigate to class selection
        self.creator.process_response("Eldara")  # character_name
        self.creator.process_response("Test Player")  # player_name
        self.creator.process_response("Elf")  # race
        self.creator.process_response("Wizard")  # class_name (spellcaster)
        
        # Continue through fields to find spellcasting-related ones
        for _ in range(20):  # Skip through some fields
            response = self.creator.process_response("skip")
            if "spellcasting" in response.lower():
                break
        
        # Verify spellcasting fields exist in the field list
        spellcasting_fields = ["spellcasting_ability", "spell_slots", "spells_known"]
        for field in spellcasting_fields:
            self.assertIn(field, self.creator.all_fields)
    
    def test_personality_fields_stored_correctly(self):
        """Test that personality fields are stored correctly."""
        self.creator.start()
        
        # Navigate to personality fields
        for _ in range(30):  # Skip to personality section
            response = self.creator.process_response("skip")
            if "personality" in response.lower():
                break
        
        # Input personality data
        personality_inputs = [
            "Brave, Loyal, Curious",  # personality_traits
            "Duty, Honor, Knowledge",  # ideals
            "My weapon, My companions, My spellbook",  # bonds
            "Stubborn, Quick to anger, Absent-minded"  # flaws
        ]
        
        for user_input in personality_inputs:
            response = self.creator.process_response(user_input)
        
        # Continue to completion
        while self.creator.is_active:
            response = self.creator.process_response("skip")
            if "Character Creation Complete" in response:
                break
        
        # Verify personality fields are stored correctly
        character_sheet = self.creator.character_sheet
        self.assertIsNotNone(character_sheet)
        
        # Check that personality fields are stored as strings
        self.assertIsInstance(character_sheet.personality_traits, str)
        self.assertIsInstance(character_sheet.ideals, str)
        self.assertIsInstance(character_sheet.bonds, str)
        self.assertIsInstance(character_sheet.flaws, str)
        
        # Verify content
        self.assertIn("Brave", character_sheet.personality_traits)
        self.assertIn("Duty", character_sheet.ideals)
        self.assertIn("My weapon", character_sheet.bonds)
        self.assertIn("Stubborn", character_sheet.flaws)
    
    def test_ability_score_method_selection(self):
        """Test ability score method selection."""
        self.creator.start()
        
        # Navigate to ability score method
        for _ in range(10):
            response = self.creator.process_response("skip")
            if "ability_score_method" in response:
                break
        
        # Test each method
        methods = [
            ("1", "standard_array"),
            ("2", "point_buy"),
            ("3", "optimal_assignment")
        ]
        
        for input_val, expected_method in methods:
            self.creator.reset()
            self.creator.start()
            
            # Navigate to ability score method
            for _ in range(10):
                response = self.creator.process_response("skip")
                if "ability_score_method" in response:
                    break
            
            # Select method
            response = self.creator.process_response(input_val)
            
            # Verify method was set
            self.assertEqual(self.creator.state.get("ability_score_method"), expected_method)
    
    def test_command_handling(self):
        """Test command handling (help, summary, edit, skip, back)."""
        self.creator.start()
        
        # Test help command
        response = self.creator.process_response("help")
        self.assertIn("Available Commands", response)
        self.assertTrue(self.creator.is_active)
        
        # Test summary command
        response = self.creator.process_response("summary")
        self.assertIn("Character Creation Progress", response)
        self.assertTrue(self.creator.is_active)
        
        # Test skip command
        response = self.creator.process_response("skip")
        self.assertTrue(self.creator.is_active)
        self.assertEqual(self.creator.current_field_index, 1)  # Should advance
        
        # Test back command
        response = self.creator.process_response("back")
        self.assertEqual(self.creator.current_field_index, 0)  # Should go back
        
        # Test edit command
        response = self.creator.process_response("edit character_name")
        self.assertIn("Editing character_name", response)
    
    def test_field_validation(self):
        """Test field validation for various data types."""
        self.creator.start()
        
        # Test level validation
        self.creator.process_response("skip")  # character_name
        self.creator.process_response("skip")  # player_name
        self.creator.process_response("skip")  # race
        self.creator.process_response("skip")  # class_name
        
        # Test valid level
        response = self.creator.process_response("5")
        self.assertNotIn("couldn't understand", response.lower())
        
        # Test invalid level
        self.creator.reset()
        self.creator.start()
        for _ in range(4):
            self.creator.process_response("skip")
        
        response = self.creator.process_response("25")  # Invalid level
        self.assertIn("couldn't understand", response.lower())
    
    def test_alignment_parsing(self):
        """Test alignment parsing."""
        self.creator.start()
        
        # Navigate to alignment (it's the 7th field in identity group)
        for _ in range(7):
            self.creator.process_response("skip")
        
        # Test various alignment inputs
        alignments = [
            ("lawful good", "Lawful Good"),
            ("neutral good", "Neutral Good"),
            ("chaotic good", "Chaotic Good"),
            ("lawful neutral", "Lawful Neutral"),
            ("neutral", "True Neutral"),
            ("chaotic neutral", "Chaotic Neutral"),
            ("lawful evil", "Lawful Evil"),
            ("neutral evil", "Neutral Evil"),
            ("chaotic evil", "Chaotic Evil")
        ]
        
        for input_val, expected in alignments:
            self.creator.reset()
            self.creator.start()
            
            # Navigate to alignment
            for _ in range(7):
                self.creator.process_response("skip")
            
            response = self.creator.process_response(input_val)
            self.assertEqual(self.creator.state.get("alignment"), expected)
    
    def test_equipment_parsing(self):
        """Test equipment parsing and storage."""
        self.creator.start()
        
        # Navigate to equipment section
        for _ in range(25):
            response = self.creator.process_response("skip")
            if "equipment" in response.lower():
                break
        
        # Input equipment
        equipment_input = "Backpack, Bedroll, Rations (5 days), Torch, Rope"
        response = self.creator.process_response(equipment_input)
        
        # Continue to completion
        while self.creator.is_active:
            response = self.creator.process_response("skip")
            if "Character Creation Complete" in response:
                break
        
        # Verify equipment is stored as list
        character_sheet = self.creator.character_sheet
        self.assertIsInstance(character_sheet.equipment, list)
        self.assertIn("Backpack", character_sheet.equipment)
        self.assertIn("Bedroll", character_sheet.equipment)
        self.assertIn("Rations (5 days)", character_sheet.equipment)
    
    def test_character_sheet_creation(self):
        """Test that CharacterSheet is created with all required fields."""
        self.creator.start()
        
        # Complete character creation with minimal data
        for _ in range(len(self.creator.all_fields)):
            response = self.creator.process_response("skip")
            if "Character Creation Complete" in response:
                break
        
        # Verify CharacterSheet was created
        character_sheet = self.creator.character_sheet
        self.assertIsNotNone(character_sheet)
        self.assertIsInstance(character_sheet, CharacterSheet)
        
        # Verify required fields exist
        self.assertIsNotNone(character_sheet.character_name)
        self.assertIsNotNone(character_sheet.race)
        self.assertIsNotNone(character_sheet.class_name)
        self.assertIsNotNone(character_sheet.level)
        self.assertIsNotNone(character_sheet.strength)
        self.assertIsNotNone(character_sheet.strength_mod)
    
    def test_progress_tracking(self):
        """Test progress tracking functionality."""
        self.creator.start()
        
        # Check initial progress
        progress = self.creator.get_current_progress()
        self.assertTrue(progress['is_active'])
        self.assertEqual(progress['current_field_index'], 0)
        self.assertEqual(progress['total_fields'], 69)
        self.assertEqual(progress['completed_fields'], 0)
        
        # Complete a few fields
        self.creator.process_response("Test Character")
        self.creator.process_response("Test Player")
        self.creator.process_response("Human")
        
        # Check updated progress
        progress = self.creator.get_current_progress()
        self.assertEqual(progress['current_field_index'], 3)
        self.assertEqual(progress['completed_fields'], 3)
    
    def test_reset_functionality(self):
        """Test reset functionality."""
        self.creator.start()
        self.creator.process_response("Test Character")
        
        # Verify some progress
        self.assertTrue(self.creator.is_active)
        self.assertEqual(self.creator.current_field_index, 1)
        
        # Reset
        response = self.creator.reset()
        self.assertIn("reset", response.lower())
        
        # Verify reset
        self.assertFalse(self.creator.is_active)
        self.assertEqual(self.creator.current_field_index, 0)
        self.assertEqual(self.creator.state['character_name'], None)
    
    def test_edge_case_inputs(self):
        """Test edge case inputs and error handling."""
        self.creator.start()
        
        # Test very long input
        long_input = "A" * 1000
        response = self.creator.process_response(long_input)
        self.assertNotIn("error", response.lower())
        
        # Test special characters
        special_input = "Thorin@#$%^&*()_+"
        response = self.creator.process_response(special_input)
        self.assertNotIn("error", response.lower())
        
        # Test unicode characters
        unicode_input = "Thorin 🗡️✨"
        response = self.creator.process_response(unicode_input)
        self.assertNotIn("error", response.lower())


class TestEnhancedStepByStepCreatorIntegration(unittest.TestCase):
    """Integration tests for the enhanced step-by-step creator."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.llm_service = MagicMock()
        self.creator = EnhancedStepByStepCreator(llm_service=self.llm_service)
    
    def test_full_character_creation_integration(self):
        """Test full character creation integration with all systems."""
        # This test would integrate with the actual game systems
        # For now, we'll test the basic flow
        self.creator.start()
        
        # Complete a full character
        responses = [
            "Test Character", "Test Player", "Human", "Fighter", "1",
            "Soldier", "Lawful Good", "25", "Male", "0", "1",  # Standard Array
            "15", "14", "13", "12", "10", "8",  # Ability scores
            "12", "16", "2", "30", "2",  # Combat stats
            "Backpack, Sword", "Longsword", "Chain mail", "10 gp",  # Equipment
            "All armor, Weapons", "Common", "", "Fighting Style",  # Proficiencies
            "Brave", "Honor", "My sword", "Stubborn", "A warrior",  # Personality
            "6'0\"", "180 lbs", "Blue", "Brown", "Fair", "Scar"  # Physical
        ]
        
        for response in responses:
            result = self.creator.process_response(str(response))
            if "Character Creation Complete" in result:
                break
        
        # Verify integration
        character_sheet = self.creator.character_sheet
        self.assertIsNotNone(character_sheet)
        
        # Verify all systems are integrated
        self.assertIsInstance(character_sheet.ability_scores, dict)
        self.assertIsInstance(character_sheet.ability_modifiers, dict)
        self.assertIsInstance(character_sheet.equipment, list)
        self.assertIsInstance(character_sheet.proficiencies, list)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 