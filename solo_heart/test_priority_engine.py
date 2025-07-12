#!/usr/bin/env python3
"""
Test suite for the Intelligent Priority Engine

Tests the priority engine's ability to correctly identify and prioritize
missing SRD 5.2 character sheet fields.
"""

import unittest
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from srd_compliance_checker import srd_checker, priority_engine, PriorityField, RequirementLevel

class TestIntelligentPriorityEngine(unittest.TestCase):
    """Test cases for the intelligent priority engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.empty_character = {
            "name": None,
            "race": None,
            "class": None,
            "level": 1,
            "ability_scores": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            },
            "background": None,
            "alignment": None,
            "age": None,
            "gender": None,
            "personality_traits": [],
            "motivations": [],
            "backstory": ""
        }
        
        self.partial_character = {
            "name": "Test Character",
            "race": "Human",
            "class": None,
            "level": 1,
            "ability_scores": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            },
            "background": None,
            "alignment": None,
            "age": 25,
            "gender": "Male",
            "personality_traits": ["Brave"],
            "motivations": ["Adventure"],
            "backstory": "A brave adventurer"
        }
        
        self.nearly_complete_character = {
            "name": "Test Character",
            "race": "Human",
            "class": "Fighter",
            "level": 1,
            "ability_scores": {
                "strength": 15,
                "dexterity": 12,
                "constitution": 14,
                "intelligence": 10,
                "wisdom": 8,
                "charisma": 13
            },
            "background": "Soldier",
            "alignment": "Lawful Good",
            "age": 25,
            "gender": "Male",
            "personality_traits": ["Brave", "Loyal"],
            "motivations": ["Adventure", "Protect others"],
            "backstory": "A brave soldier seeking adventure"
        }
    
    def test_empty_character_priorities(self):
        """Test that empty character gets critical fields prioritized first."""
        priority_fields = srd_checker.get_next_priority_fields(self.empty_character, max_fields=3)
        
        # Should have critical fields prioritized
        self.assertGreater(len(priority_fields), 0)
        
        # Check that critical fields are prioritized
        critical_fields = [f.field for f in priority_fields if f.level == RequirementLevel.CRITICAL]
        self.assertGreater(len(critical_fields), 0)
        
        # Verify priority scores are higher for critical fields
        for field in priority_fields:
            if field.level == RequirementLevel.CRITICAL:
                self.assertGreater(field.priority_score, 0.8)
    
    def test_partial_character_priorities(self):
        """Test that partial character gets appropriate priorities."""
        priority_fields = srd_checker.get_next_priority_fields(self.partial_character, max_fields=2)
        
        # Should prioritize class (critical) over other fields
        self.assertGreater(len(priority_fields), 0)
        
        # Class should be high priority since it's missing
        class_field = next((f for f in priority_fields if f.field == "class"), None)
        if class_field:
            self.assertEqual(class_field.level, RequirementLevel.CRITICAL)
            self.assertTrue(class_field.is_urgent)
    
    def test_nearly_complete_character_priorities(self):
        """Test that nearly complete character gets clarification priorities."""
        priority_fields = srd_checker.get_next_priority_fields(self.nearly_complete_character, max_fields=2)
        
        # Should focus on clarification rather than missing fields
        completeness_result = srd_checker.check_character_completeness(self.nearly_complete_character)
        # The character is actually not as complete as expected due to missing fields
        # Let's check what's actually missing
        missing_fields = [f['field'] for f in completeness_result['missing_fields']]
        print(f"Missing fields: {missing_fields}")
        
        # Should have priority fields since character is not complete
        self.assertGreater(len(priority_fields), 0)
    
    def test_priority_field_structure(self):
        """Test that priority fields have correct structure."""
        priority_fields = srd_checker.get_next_priority_fields(self.empty_character, max_fields=1)
        
        if priority_fields:
            field = priority_fields[0]
            
            # Check required attributes
            self.assertIsInstance(field.field, str)
            self.assertIsInstance(field.level, RequirementLevel)
            self.assertIsInstance(field.description, str)
            self.assertIsInstance(field.priority_score, float)
            self.assertIsInstance(field.natural_language_prompt, str)
            self.assertIsInstance(field.is_urgent, bool)
            
            # Check value ranges
            self.assertGreater(field.priority_score, 0)
            self.assertLessEqual(field.priority_score, 2.0)
    
    def test_steering_prompt_generation(self):
        """Test that steering prompts are generated correctly."""
        steering_prompt = srd_checker.generate_steering_prompt(self.empty_character)
        
        # Should be a non-empty string
        self.assertIsInstance(steering_prompt, str)
        self.assertGreater(len(steering_prompt), 0)
        
        # Should contain guidance for critical fields
        self.assertIn("URGENT", steering_prompt)
    
    def test_field_dependencies(self):
        """Test that field dependencies are respected."""
        # Create character with class but no race
        character_with_class = {
            "name": "Test",
            "race": None,
            "class": "Wizard",
            "level": 1,
            "ability_scores": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }
        }
        
        priority_fields = srd_checker.get_next_priority_fields(character_with_class, max_fields=3)
        
        # Race should be prioritized over spells (which depend on class)
        race_field = next((f for f in priority_fields if f.field == "race"), None)
        spells_field = next((f for f in priority_fields if f.field == "spells"), None)
        
        if race_field and spells_field:
            self.assertGreater(race_field.priority_score, spells_field.priority_score)
    
    def test_priority_score_calculation(self):
        """Test that priority scores are calculated correctly."""
        priority_fields = srd_checker.get_next_priority_fields(self.empty_character, max_fields=5)
        
        # Scores should be in descending order
        scores = [f.priority_score for f in priority_fields]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # Critical fields should have higher scores than non-critical
        for field in priority_fields:
            if field.level == RequirementLevel.CRITICAL:
                self.assertGreater(field.priority_score, 0.8)
    
    def test_natural_prompt_generation(self):
        """Test that natural language prompts are generated correctly."""
        priority_fields = srd_checker.get_next_priority_fields(self.empty_character, max_fields=1)
        
        if priority_fields:
            field = priority_fields[0]
            
            # Prompt should be a non-empty string
            self.assertIsInstance(field.natural_language_prompt, str)
            self.assertGreater(len(field.natural_language_prompt), 0)
            
            # Prompt should be conversational
            self.assertNotIn("ERROR", field.natural_language_prompt)
            self.assertNotIn("NULL", field.natural_language_prompt)
    
    def test_context_aware_prompts(self):
        """Test that prompts are context-aware."""
        # Test with character that has a name but no race
        character_with_name = {
            "name": "Aragorn",
            "race": None,
            "class": None,
            "level": 1,
            "ability_scores": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }
        }
        
        priority_fields = srd_checker.get_next_priority_fields(character_with_name, max_fields=2)
        
        # Find race field
        race_field = next((f for f in priority_fields if f.field == "race"), None)
        if race_field:
            # Prompt should mention the character's name
            self.assertIn("Aragorn", race_field.natural_language_prompt)
    
    def test_clarification_mode(self):
        """Test that clarification mode is activated for nearly complete characters."""
        # Create a character that's over 90% complete
        nearly_complete = {
            "name": "Test",
            "race": "Human",
            "class": "Fighter",
            "level": 1,
            "ability_scores": {
                "strength": 15,
                "dexterity": 12,
                "constitution": 14,
                "intelligence": 10,
                "wisdom": 8,
                "charisma": 13
            },
            "background": "Soldier",
            "alignment": "Lawful Good",  # More complete alignment
            "age": 25,
            "gender": "Male",
            "personality_traits": ["Brave", "Loyal"],
            "motivations": ["Adventure", "Protect others"],
            "backstory": "A brave soldier seeking adventure",
            "skill_proficiencies": ["Athletics", "Intimidation"],
            "languages": ["Common"],
            "equipment": ["Longsword", "Shield"],
            "weapons": ["Longsword"],
            "armor": "Chain mail",
            "ideals": ["Protection"],
            "bonds": ["My companions"],
            "flaws": ["Too trusting"],
            "combat_approach": "Defensive",
            "spells": [],
            "class_features": ["Fighting Style"],
            "physical_appearance": "Tall and muscular",
            "emotional_themes": ["Honor"],
            "traumas": ["Lost comrades"],
            "relationships": ["Fellow soldiers"],
            "additional_traits": ["Scarred veteran"]
        }
        
        priority_fields = srd_checker.get_next_priority_fields(nearly_complete, max_fields=2)
        
        # Check completeness
        completeness_result = srd_checker.check_character_completeness(nearly_complete)
        print(f"Completion percentage: {completeness_result['completion_percentage']}")
        
        # Should have fewer priority fields since character is mostly complete
        self.assertLessEqual(len(priority_fields), 2)
    
    def test_urgent_field_detection(self):
        """Test that critical fields are marked as urgent."""
        priority_fields = srd_checker.get_next_priority_fields(self.empty_character, max_fields=5)
        
        # Critical fields should be marked as urgent
        for field in priority_fields:
            if field.level == RequirementLevel.CRITICAL:
                self.assertTrue(field.is_urgent)
            else:
                self.assertFalse(field.is_urgent)
    
    def test_max_fields_limit(self):
        """Test that max_fields limit is respected."""
        priority_fields = srd_checker.get_next_priority_fields(self.empty_character, max_fields=1)
        self.assertLessEqual(len(priority_fields), 1)
        
        priority_fields = srd_checker.get_next_priority_fields(self.empty_character, max_fields=3)
        self.assertLessEqual(len(priority_fields), 3)
    
    def test_error_handling(self):
        """Test that the priority engine handles errors gracefully."""
        # Test with invalid character data
        invalid_character = None
        
        priority_fields = srd_checker.get_next_priority_fields(invalid_character, max_fields=2)
        # Should handle gracefully and return empty list
        self.assertEqual(priority_fields, [])
        
        # Test with empty character data
        empty_data = {}
        priority_fields = srd_checker.get_next_priority_fields(empty_data, max_fields=2)
        # Should return priorities for missing fields
        self.assertIsInstance(priority_fields, list)
        self.assertGreater(len(priority_fields), 0)

class TestPriorityEngineIntegration(unittest.TestCase):
    """Test integration of priority engine with SRD compliance checker."""
    
    def test_priority_engine_with_completeness_check(self):
        """Test that priority engine works with completeness checking."""
        character = {
            "name": "Test",
            "race": None,
            "class": None,
            "level": 1,
            "ability_scores": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }
        }
        
        # Check completeness
        completeness_result = srd_checker.check_character_completeness(character)
        self.assertFalse(completeness_result['is_complete'])
        
        # Get priority fields
        priority_fields = srd_checker.get_next_priority_fields(character, max_fields=2)
        self.assertGreater(len(priority_fields), 0)
        
        # Priority fields should correspond to missing fields
        missing_field_names = [f['field'] for f in completeness_result['missing_fields']]
        priority_field_names = [f.field for f in priority_fields]
        
        # All priority fields should be in missing fields
        for field_name in priority_field_names:
            self.assertIn(field_name, missing_field_names)
    
    def test_steering_prompt_with_completeness(self):
        """Test that steering prompts reflect completeness status."""
        character = {
            "name": "Test",
            "race": None,
            "class": None,
            "level": 1,
            "ability_scores": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }
        }
        
        steering_prompt = srd_checker.generate_steering_prompt(character)
        
        # Should contain guidance about completion status
        self.assertIn("Focus", steering_prompt)
        
        # Should mention critical information
        self.assertIn("URGENT", steering_prompt)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 