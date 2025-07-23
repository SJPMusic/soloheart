#!/usr/bin/env python3
"""
Character Export Format Validator

Tests that character data generated via Vibe Code or Step-by-Step creation
includes all SRD 5.2 required fields and is formatted correctly for gameplay use.
"""

import sys
import os
import json
import unittest
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add the game_app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'game_app'))

# Import the validator utility
from character_validator import validate_character_export





class TestCharacterExportFormat(unittest.TestCase):
    """Test cases for character export format validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_character = {
            "name": "Elira",
            "race": "Elf",
            "class": "Druid",
            "background": "Folk Hero",
            "level": 1,
            "gender": "Female",
            "personality": "Curious and protective of nature",
            "hit_points": 10,
            "armor_class": 14,
            "speed": 30,
            "initiative_bonus": 2,
            "saving_throws": ["intelligence", "wisdom"],
            "equipment": ["Quarterstaff", "Leather armor", "Explorer's pack"],
            "abilities": {
                "strength": 10,
                "dexterity": 14,
                "constitution": 12,
                "intelligence": 13,
                "wisdom": 16,
                "charisma": 8
            },
            "skills": ["nature", "perception", "survival"],
            "languages": ["Common", "Elvish", "Druidic"],
            "tool_proficiencies": ["Herbalism kit"],
            "features": ["Druidic", "Wild Shape"]
        }
    
    def test_valid_full_character(self):
        """Test that a complete character passes validation."""
        is_valid, errors = validate_character_export(self.valid_character)
        
        self.assertTrue(is_valid, f"Valid character should pass validation. Errors: {errors}")
        self.assertEqual(len(errors), 0, f"Valid character should have no errors. Errors: {errors}")
    
    def test_incomplete_character_missing_hit_points(self):
        """Test that character missing hit_points fails validation."""
        incomplete_character = self.valid_character.copy()
        del incomplete_character["hit_points"]
        
        is_valid, errors = validate_character_export(incomplete_character)
        
        self.assertFalse(is_valid, "Character missing hit_points should fail validation")
        self.assertIn("Missing required field: hit_points", errors)
    
    def test_incomplete_character_missing_background(self):
        """Test that character missing background fails validation."""
        incomplete_character = self.valid_character.copy()
        del incomplete_character["background"]
        
        is_valid, errors = validate_character_export(incomplete_character)
        
        self.assertFalse(is_valid, "Character missing background should fail validation")
        self.assertIn("Missing required field: background", errors)
    
    def test_incomplete_character_missing_abilities(self):
        """Test that character missing abilities fails validation."""
        incomplete_character = self.valid_character.copy()
        del incomplete_character["abilities"]
        
        is_valid, errors = validate_character_export(incomplete_character)
        
        self.assertFalse(is_valid, "Character missing abilities should fail validation")
        self.assertIn("Missing required field: abilities", errors)
    
    def test_character_with_none_values(self):
        """Test that character with None values fails validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["hit_points"] = None
        
        is_valid, errors = validate_character_export(invalid_character)
        
        self.assertFalse(is_valid, "Character with None hit_points should fail validation")
        self.assertIn("Required field 'hit_points' cannot be None", errors)
    
    def test_character_with_empty_strings(self):
        """Test that character with empty strings fails validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["name"] = ""
        
        is_valid, errors = validate_character_export(invalid_character)
        
        self.assertFalse(is_valid, "Character with empty name should fail validation")
        self.assertIn("Required field 'name' cannot be empty string", errors)
    
    def test_character_with_empty_lists(self):
        """Test that character with empty lists fails validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["equipment"] = []
        
        is_valid, errors = validate_character_export(invalid_character)
        
        self.assertFalse(is_valid, "Character with empty equipment should fail validation")
        self.assertIn("Required field 'equipment' cannot be empty list", errors)
    
    def test_character_with_invalid_field_types(self):
        """Test that character with wrong field types fails validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["level"] = "1"  # Should be int
        
        is_valid, errors = validate_character_export(invalid_character)
        
        self.assertFalse(is_valid, "Character with string level should fail validation")
        self.assertTrue(any("Field 'level' must be an integer" in error for error in errors))
    
    def test_character_with_invalid_values(self):
        """Test that character with invalid values fails validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["level"] = 25  # Should be 1-20
        
        is_valid, errors = validate_character_export(invalid_character)
        
        self.assertFalse(is_valid, "Character with level 25 should fail validation")
        self.assertIn("Level must be between 1 and 20, got 25", errors)
    
    def test_character_with_invalid_race(self):
        """Test that character with invalid race fails validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["race"] = "Orc"  # Not in SRD
        
        is_valid, errors = validate_character_export(invalid_character)
        
        self.assertFalse(is_valid, "Character with invalid race should fail validation")
        self.assertTrue(any("Invalid race 'Orc'" in error for error in errors))
    
    def test_character_with_invalid_class(self):
        """Test that character with invalid class fails validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["class"] = "Mage"  # Not in SRD
        
        is_valid, errors = validate_character_export(invalid_character)
        
        self.assertFalse(is_valid, "Character with invalid class should fail validation")
        self.assertTrue(any("Invalid class 'Mage'" in error for error in errors))
    
    def test_character_with_invalid_gender(self):
        """Test that character with invalid gender fails validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["gender"] = "Other"  # Not in valid list
        
        is_valid, errors = validate_character_export(invalid_character)
        
        self.assertFalse(is_valid, "Character with invalid gender should fail validation")
        self.assertTrue(any("Invalid gender 'Other'" in error for error in errors))
    
    def test_character_with_invalid_abilities(self):
        """Test that character with invalid abilities fails validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["abilities"]["strength"] = 35  # Should be 1-30
        
        is_valid, errors = validate_character_export(invalid_character)
        
        self.assertFalse(is_valid, "Character with invalid ability score should fail validation")
        self.assertIn("Ability score 'strength' must be between 1 and 30, got 35", errors)
    
    def test_character_with_invalid_saving_throws(self):
        """Test that character with invalid saving throws fails validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["saving_throws"] = ["strength", "invalid_ability"]
        
        is_valid, errors = validate_character_export(invalid_character)
        
        self.assertFalse(is_valid, "Character with invalid saving throw should fail validation")
        self.assertTrue(any("Invalid saving throw 'invalid_ability'" in error for error in errors))
    
    def test_character_with_invalid_skills(self):
        """Test that character with invalid skills fails validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["skills"] = ["nature", "invalid_skill"]
        
        is_valid, errors = validate_character_export(invalid_character)
        
        self.assertFalse(is_valid, "Character with invalid skill should fail validation")
        self.assertTrue(any("Invalid skill 'invalid_skill'" in error for error in errors))
    
    def test_character_with_optional_fields(self):
        """Test that character with optional fields passes validation."""
        character_with_optionals = self.valid_character.copy()
        character_with_optionals["alignment"] = "Neutral Good"
        character_with_optionals["age"] = 25
        character_with_optionals["feats"] = ["Alert"]
        
        is_valid, errors = validate_character_export(character_with_optionals)
        
        self.assertTrue(is_valid, f"Character with optional fields should pass validation. Errors: {errors}")
        self.assertEqual(len(errors), 0, f"Character with optional fields should have no errors. Errors: {errors}")
    
    def test_character_with_none_optional_fields(self):
        """Test that character with None optional fields passes validation."""
        character_with_none_optionals = self.valid_character.copy()
        character_with_none_optionals["alignment"] = None
        character_with_none_optionals["age"] = None
        
        is_valid, errors = validate_character_export(character_with_none_optionals)
        
        self.assertTrue(is_valid, f"Character with None optional fields should pass validation. Errors: {errors}")
        self.assertEqual(len(errors), 0, f"Character with None optional fields should have no errors. Errors: {errors}")


class TestCharacterExportIntegration(unittest.TestCase):
    """Integration tests for character export validation."""
    
    def test_step_by_step_character_export(self):
        """Test that step-by-step character creation produces valid export."""
        # Simulate step-by-step character creation output
        step_by_step_character = {
            "name": "Thorne",
            "race": "Human",
            "class": "Rogue",
            "background": "Criminal",
            "level": 1,
            "gender": "Male",
            "personality": "Cautious and mysterious",
            "hit_points": 8,
            "armor_class": 15,
            "speed": 30,
            "initiative_bonus": 3,
            "saving_throws": ["dexterity", "intelligence"],
            "equipment": ["Shortsword", "Shortbow", "Leather armor", "Burglar's pack"],
            "abilities": {
                "strength": 8,
                "dexterity": 16,
                "constitution": 10,
                "intelligence": 14,
                "wisdom": 12,
                "charisma": 13
            },
            "skills": ["acrobatics", "deception", "insight", "intimidation", "investigation", "perception", "sleight of hand", "stealth"],
            "languages": ["Common", "Thieves' Cant"],
            "tool_proficiencies": ["Thieves' tools"],
            "features": ["Expertise", "Sneak Attack", "Thieves' Cant"]
        }
        
        is_valid, errors = validate_character_export(step_by_step_character)
        
        self.assertTrue(is_valid, f"Step-by-step character should pass validation. Errors: {errors}")
        self.assertEqual(len(errors), 0, f"Step-by-step character should have no errors. Errors: {errors}")
    
    def test_vibe_code_character_export(self):
        """Test that vibe code character creation produces valid export."""
        # Simulate vibe code character creation output
        vibe_code_character = {
            "name": "Elira",
            "race": "Elf",
            "class": "Druid",
            "background": "Folk Hero",
            "level": 1,
            "gender": "Female",
            "personality": "Curious and protective of nature",
            "hit_points": 10,
            "armor_class": 14,
            "speed": 30,
            "initiative_bonus": 2,
            "saving_throws": ["intelligence", "wisdom"],
            "equipment": ["Quarterstaff", "Leather armor", "Explorer's pack"],
            "abilities": {
                "strength": 10,
                "dexterity": 14,
                "constitution": 12,
                "intelligence": 13,
                "wisdom": 16,
                "charisma": 8
            },
            "skills": ["nature", "perception", "survival"],
            "languages": ["Common", "Elvish", "Druidic"],
            "tool_proficiencies": ["Herbalism kit"],
            "features": ["Druidic", "Wild Shape"],
            "alignment": "Neutral Good",
            "age": 25,
            "backstory": "Survived a forest fire and now protects nature"
        }
        
        is_valid, errors = validate_character_export(vibe_code_character)
        
        self.assertTrue(is_valid, f"Vibe code character should pass validation. Errors: {errors}")
        self.assertEqual(len(errors), 0, f"Vibe code character should have no errors. Errors: {errors}")


def run_character_export_tests():
    """Run the character export format test suite."""
    print("🧪 Running Character Export Format Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCharacterExportFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestCharacterExportIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All character export format tests passed!")
        return True
    else:
        print("\n❌ Some character export format tests failed!")
        return False


if __name__ == "__main__":
    success = run_character_export_tests()
    sys.exit(0 if success else 1) 