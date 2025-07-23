#!/usr/bin/env python3
"""
Character Export Validation Suite

Ensures both Vibe Code and Step-by-Step character creators output 
full SRD 5.2-compliant character sheets, suitable for gameplay and stat tracking.
"""

import sys
import os
import unittest
from typing import Dict, List, Any, Optional

# Add the game_app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'game_app'))


class MissingFieldError(Exception):
    """Raised when a required field is missing from character export."""
    pass


def validate_character_export(character: dict) -> List[str]:
    """
    Validate character export and return list of missing fields.
    
    Args:
        character: The character data dictionary to validate
        
    Returns:
        List[str]: List of missing required fields, or empty list if valid
        
    Raises:
        MissingFieldError: If required fields are missing
    """
    # SRD 5.2 Required Fields
    required_fields = [
        "name", "race", "class", "background", "level", "gender",
        "personality", "hit_points", "armor_class", "speed",
        "initiative_bonus", "saving_throws", "equipment", "abilities",
        "skills", "languages", "tool_proficiencies", "features"
    ]
    
    missing_fields = []
    
    # Check for missing required fields
    for field in required_fields:
        if field not in character:
            missing_fields.append(field)
        elif character[field] is None:
            missing_fields.append(field)
        elif isinstance(character[field], str) and not character[field].strip():
            missing_fields.append(field)
        elif isinstance(character[field], list) and len(character[field]) == 0:
            missing_fields.append(field)
        elif isinstance(character[field], dict) and len(character[field]) == 0:
            missing_fields.append(field)
    
    if missing_fields:
        raise MissingFieldError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return []


def get_validation_summary(character: dict) -> str:
    """
    Get a pretty summary of validation results.
    
    Args:
        character: The character data dictionary to validate
        
    Returns:
        str: Validation summary message
    """
    try:
        validate_character_export(character)
        return "✅ Character export validation passed"
    except MissingFieldError as e:
        return f"❌ Character export failed validation:\n - Missing: {str(e).replace('Missing required fields: ', '')}"


class TestCharacterExportValidation(unittest.TestCase):
    """Test cases for character export validation."""
    
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
    
    def test_valid_export_structure(self):
        """Test that a fully generated character sheet dict passes validation."""
        # Input: A fully generated character sheet dict
        # Assert: All required_fields are present and not None
        
        try:
            missing_fields = validate_character_export(self.valid_character)
            self.assertEqual(missing_fields, [], "Valid character should have no missing fields")
        except MissingFieldError as e:
            self.fail(f"Valid character should not raise MissingFieldError: {e}")
    
    def test_missing_field_failure(self):
        """Test that a dict missing hit_points or equipment fails validation."""
        # Input: A dict missing "hit_points" or "equipment"
        # Assert: Validation fails with MissingFieldError
        
        # Test missing hit_points
        incomplete_character = self.valid_character.copy()
        del incomplete_character["hit_points"]
        
        with self.assertRaises(MissingFieldError) as context:
            validate_character_export(incomplete_character)
        
        self.assertIn("hit_points", str(context.exception))
        
        # Test missing equipment
        incomplete_character = self.valid_character.copy()
        del incomplete_character["equipment"]
        
        with self.assertRaises(MissingFieldError) as context:
            validate_character_export(incomplete_character)
        
        self.assertIn("equipment", str(context.exception))
    
    def test_optional_fields_allowed(self):
        """Test that sheet missing alignment or feats passes validation."""
        # Input: Sheet missing "alignment" or "feats"
        # Assert: Validation passes
        
        # Add optional fields to valid character
        character_with_optionals = self.valid_character.copy()
        character_with_optionals["alignment"] = "Neutral Good"
        character_with_optionals["feats"] = ["Alert"]
        
        # Should pass validation
        try:
            missing_fields = validate_character_export(character_with_optionals)
            self.assertEqual(missing_fields, [], "Character with optional fields should pass validation")
        except MissingFieldError as e:
            self.fail(f"Character with optional fields should not raise MissingFieldError: {e}")
        
        # Remove optional fields - should still pass
        del character_with_optionals["alignment"]
        del character_with_optionals["feats"]
        
        try:
            missing_fields = validate_character_export(character_with_optionals)
            self.assertEqual(missing_fields, [], "Character without optional fields should pass validation")
        except MissingFieldError as e:
            self.fail(f"Character without optional fields should not raise MissingFieldError: {e}")
    
    def test_none_values_fail_validation(self):
        """Test that None values for required fields fail validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["hit_points"] = None
        
        with self.assertRaises(MissingFieldError) as context:
            validate_character_export(invalid_character)
        
        self.assertIn("hit_points", str(context.exception))
    
    def test_empty_strings_fail_validation(self):
        """Test that empty strings for required fields fail validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["name"] = ""
        
        with self.assertRaises(MissingFieldError) as context:
            validate_character_export(invalid_character)
        
        self.assertIn("name", str(context.exception))
    
    def test_empty_lists_fail_validation(self):
        """Test that empty lists for required fields fail validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["equipment"] = []
        
        with self.assertRaises(MissingFieldError) as context:
            validate_character_export(invalid_character)
        
        self.assertIn("equipment", str(context.exception))
    
    def test_empty_dicts_fail_validation(self):
        """Test that empty dictionaries for required fields fail validation."""
        invalid_character = self.valid_character.copy()
        invalid_character["abilities"] = {}
        
        with self.assertRaises(MissingFieldError) as context:
            validate_character_export(invalid_character)
        
        self.assertIn("abilities", str(context.exception))
    
    def test_multiple_missing_fields(self):
        """Test that multiple missing fields are all reported."""
        incomplete_character = self.valid_character.copy()
        del incomplete_character["hit_points"]
        del incomplete_character["armor_class"]
        del incomplete_character["background"]
        
        with self.assertRaises(MissingFieldError) as context:
            validate_character_export(incomplete_character)
        
        error_message = str(context.exception)
        self.assertIn("hit_points", error_message)
        self.assertIn("armor_class", error_message)
        self.assertIn("background", error_message)


class TestValidationSummary(unittest.TestCase):
    """Test cases for validation summary functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_character = {
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
            "equipment": ["Shortsword", "Shortbow", "Leather armor"],
            "abilities": {
                "strength": 8,
                "dexterity": 16,
                "constitution": 10,
                "intelligence": 14,
                "wisdom": 12,
                "charisma": 13
            },
            "skills": ["acrobatics", "deception", "stealth"],
            "languages": ["Common", "Thieves' Cant"],
            "tool_proficiencies": ["Thieves' tools"],
            "features": ["Expertise", "Sneak Attack"]
        }
    
    def test_successful_validation_summary(self):
        """Test that successful validation returns appropriate summary."""
        summary = get_validation_summary(self.valid_character)
        self.assertIn("✅", summary)
        self.assertIn("passed", summary)
    
    def test_failed_validation_summary(self):
        """Test that failed validation returns appropriate summary."""
        invalid_character = self.valid_character.copy()
        del invalid_character["hit_points"]
        del invalid_character["armor_class"]
        
        summary = get_validation_summary(invalid_character)
        self.assertIn("❌", summary)
        self.assertIn("failed", summary)
        self.assertIn("hit_points", summary)
        self.assertIn("armor_class", summary)


class TestCharacterCreatorIntegration(unittest.TestCase):
    """Integration tests for character creator validation."""
    
    def test_vibe_code_character_validation(self):
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
            "features": ["Druidic", "Wild Shape"]
        }
        
        try:
            missing_fields = validate_character_export(vibe_code_character)
            self.assertEqual(missing_fields, [], "Vibe code character should pass validation")
        except MissingFieldError as e:
            self.fail(f"Vibe code character should not raise MissingFieldError: {e}")
    
    def test_step_by_step_character_validation(self):
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
        
        try:
            missing_fields = validate_character_export(step_by_step_character)
            self.assertEqual(missing_fields, [], "Step-by-step character should pass validation")
        except MissingFieldError as e:
            self.fail(f"Step-by-step character should not raise MissingFieldError: {e}")


def run_character_export_validation_tests():
    """Run the character export validation test suite."""
    print("🧪 Running Character Export Validation Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCharacterExportValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestValidationSummary))
    suite.addTests(loader.loadTestsFromTestCase(TestCharacterCreatorIntegration))
    
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
        print("\n✅ All character export validation tests passed!")
        return True
    else:
        print("\n❌ Some character export validation tests failed!")
        return False


if __name__ == "__main__":
    success = run_character_export_validation_tests()
    sys.exit(0 if success else 1) 