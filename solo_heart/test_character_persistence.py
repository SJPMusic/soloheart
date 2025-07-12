#!/usr/bin/env python3
"""
Character Data Persistence Test Suite

Tests that character data persists across multiple API calls and sessions.
This is a critical test to ensure the character creator doesn't lose data.
"""

import unittest
import json
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_unified_interface import TNECharacterGenerator

class TestCharacterDataPersistence(unittest.TestCase):
    """Test suite for character data persistence across sessions."""
    
    def setUp(self):
        """Set up test environment."""
        self.character_generator = TNECharacterGenerator()
        
    def test_initial_session_creates_data(self):
        """Test that initial session properly creates character data."""
        # Simulate first character creation session
        description = "I am Cain Millerson, a 18-year-old human from a farm."
        
        result = self.character_generator.start_character_creation(description, "test_campaign")
        
        # Verify session started successfully
        self.assertTrue(result['success'])
        
        # Verify character data was extracted and stored
        character_data = self.character_generator.get_character_data()
        self.assertIsNotNone(character_data.get('name'))
        self.assertEqual(character_data.get('name'), 'Cain Millerson')
        self.assertEqual(character_data.get('age'), 18)
        self.assertEqual(character_data.get('race'), 'Human')
        
    def test_second_session_preserves_data(self):
        """Test that second session preserves existing character data."""
        # First session - create character
        description1 = "I am Cain Millerson, a 18-year-old human from a farm."
        result1 = self.character_generator.start_character_creation(description1, "test_campaign")
        
        # Get initial character data
        initial_data = self.character_generator.get_character_data()
        initial_name = initial_data.get('name')
        initial_age = initial_data.get('age')
        initial_race = initial_data.get('race')
        
        # Verify we have data
        self.assertIsNotNone(initial_name)
        self.assertIsNotNone(initial_age)
        self.assertIsNotNone(initial_race)
        
        # Second session - should preserve existing data
        description2 = "I want to be a fighter class."
        result2 = self.character_generator.start_character_creation(description2, "test_campaign")
        
        # Verify session continued successfully
        self.assertTrue(result2['success'])
        
        # Verify character data was preserved
        preserved_data = self.character_generator.get_character_data()
        self.assertEqual(preserved_data.get('name'), initial_name)
        self.assertEqual(preserved_data.get('age'), initial_age)
        self.assertEqual(preserved_data.get('race'), initial_race)
        
        # Verify new data was added
        self.assertEqual(preserved_data.get('class'), 'Fighter')
        
    def test_continue_conversation_preserves_data(self):
        """Test that continue_conversation preserves all character data."""
        # Start character creation
        description = "I am Cain Millerson, a 18-year-old human from a farm."
        result = self.character_generator.start_character_creation(description, "test_campaign")
        
        # Get initial data
        initial_data = self.character_generator.get_character_data()
        initial_name = initial_data.get('name')
        initial_age = initial_data.get('age')
        
        # Continue conversation
        user_input = "I want to be a fighter with high strength."
        result = self.character_generator.continue_conversation(user_input)
        
        # Verify conversation continued successfully
        self.assertTrue(result['success'])
        
        # Verify all previous data was preserved
        preserved_data = self.character_generator.get_character_data()
        self.assertEqual(preserved_data.get('name'), initial_name)
        self.assertEqual(preserved_data.get('age'), initial_age)
        
        # Verify new data was added
        self.assertEqual(preserved_data.get('class'), 'Fighter')
        
    def test_new_session_resets_data(self):
        """Test that truly new session (no existing data) resets character data."""
        # Create a fresh character generator
        fresh_generator = TNECharacterGenerator()
        
        # Verify initial state is empty
        initial_data = fresh_generator.get_character_data()
        self.assertIsNone(initial_data.get('name'))
        self.assertIsNone(initial_data.get('race'))
        
        # Start new session
        description = "I am a new character, Elara the Elf."
        result = fresh_generator.start_character_creation(description, "new_campaign")
        
        # Verify session started successfully
        self.assertTrue(result['success'])
        
        # Verify new data was created
        new_data = fresh_generator.get_character_data()
        self.assertIsNotNone(new_data.get('name'))
        self.assertEqual(new_data.get('name'), 'Elara')
        self.assertEqual(new_data.get('race'), 'Elf')
        
    def test_session_detection_logic(self):
        """Test the session detection logic that determines when to reset data."""
        # Test with no existing data (should reset)
        empty_generator = TNECharacterGenerator()
        empty_data = empty_generator.get_character_data()
        
        # Simulate the session detection logic
        has_name = empty_data.get('name') is not None
        has_race = empty_data.get('race') is not None
        
        self.assertFalse(has_name)
        self.assertFalse(has_race)
        
        # Test with existing data (should not reset)
        populated_generator = TNECharacterGenerator()
        populated_generator.character_data['name'] = 'Test Character'
        populated_generator.character_data['race'] = 'Human'
        
        populated_data = populated_generator.get_character_data()
        has_name = populated_data.get('name') is not None
        has_race = populated_data.get('race') is not None
        
        self.assertTrue(has_name)
        self.assertTrue(has_race)
        
    def test_complex_multi_turn_scenario(self):
        """Test a complex multi-turn character creation scenario."""
        # Turn 1: Basic character info
        description1 = "I am Cain Millerson, a 18-year-old human from a farm."
        result1 = self.character_generator.start_character_creation(description1, "complex_test")
        self.assertTrue(result1['success'])
        
        data1 = self.character_generator.get_character_data()
        self.assertEqual(data1.get('name'), 'Cain Millerson')
        self.assertEqual(data1.get('age'), 18)
        self.assertEqual(data1.get('race'), 'Human')
        
        # Turn 2: Add class and background
        input2 = "I want to be a fighter with a soldier background."
        result2 = self.character_generator.continue_conversation(input2)
        self.assertTrue(result2['success'])
        
        data2 = self.character_generator.get_character_data()
        # Verify previous data preserved
        self.assertEqual(data2.get('name'), 'Cain Millerson')
        self.assertEqual(data2.get('age'), 18)
        self.assertEqual(data2.get('race'), 'Human')
        # Verify new data added
        self.assertEqual(data2.get('class'), 'Fighter')
        self.assertEqual(data2.get('background'), 'Soldier')
        
        # Turn 3: Add personality traits
        input3 = "I am brave but sometimes reckless in battle."
        result3 = self.character_generator.continue_conversation(input3)
        self.assertTrue(result3['success'])
        
        data3 = self.character_generator.get_character_data()
        # Verify all previous data preserved
        self.assertEqual(data3.get('name'), 'Cain Millerson')
        self.assertEqual(data3.get('age'), 18)
        self.assertEqual(data3.get('race'), 'Human')
        self.assertEqual(data3.get('class'), 'Fighter')
        self.assertEqual(data3.get('background'), 'Soldier')
        # Verify new personality data added
        self.assertIn('brave', str(data3.get('personality_traits', [])).lower())
        
    def test_data_integrity_across_sessions(self):
        """Test that data integrity is maintained across multiple sessions."""
        # Session 1: Create character
        description1 = "I am Cain Millerson, a 18-year-old human fighter."
        result1 = self.character_generator.start_character_creation(description1, "integrity_test")
        self.assertTrue(result1['success'])
        
        # Session 2: Add more details
        description2 = "I have high strength and constitution from farm work."
        result2 = self.character_generator.start_character_creation(description2, "integrity_test")
        self.assertTrue(result2['success'])
        
        # Session 3: Add equipment
        description3 = "I carry a longsword and wear chain mail armor."
        result3 = self.character_generator.start_character_creation(description3, "integrity_test")
        self.assertTrue(result3['success'])
        
        # Verify all data from all sessions is preserved
        final_data = self.character_generator.get_character_data()
        
        # Session 1 data
        self.assertEqual(final_data.get('name'), 'Cain Millerson')
        self.assertEqual(final_data.get('age'), 18)
        self.assertEqual(final_data.get('race'), 'Human')
        self.assertEqual(final_data.get('class'), 'Fighter')
        
        # Session 2 data (ability scores)
        self.assertIsNotNone(final_data.get('ability_scores'))
        
        # Session 3 data (equipment)
        self.assertIsNotNone(final_data.get('gear'))
        self.assertIn('longsword', str(final_data.get('gear', [])).lower())
        
    def test_regression_protection(self):
        """Test that the regression protection logic works correctly."""
        # Test the specific condition that prevents data reset
        generator = TNECharacterGenerator()
        
        # Simulate existing character data
        generator.character_data['name'] = 'Existing Character'
        generator.character_data['race'] = 'Human'
        
        # This should NOT reset the data
        description = "I want to add more details to my character."
        result = generator.start_character_creation(description, "regression_test")
        
        # Verify data was preserved
        preserved_data = generator.get_character_data()
        self.assertEqual(preserved_data.get('name'), 'Existing Character')
        self.assertEqual(preserved_data.get('race'), 'Human')
        
        # Verify the session detection logged the continuation
        # (This would require checking logs, but we can verify the behavior)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 