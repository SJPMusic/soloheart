#!/usr/bin/env python3
"""
Memory Extraction Pipeline Tests for Vibe Code Character Creation

Validates that character facts are correctly extracted from natural language input
and reflected in the frontend summary panel after vibe code creation input is submitted.
"""

import sys
import os
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the solo_heart directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'solo_heart'))

from character_generator import CharacterGenerator
from simple_unified_interface import SimpleCharacterGenerator


class TestMemoryExtractionPipeline:
    """Test suite for character fact extraction from natural language input."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.character_generator = CharacterGenerator()
        
        # Mock the LLM service to isolate extraction logic
        self.character_generator.llm_service = Mock()
        self.character_generator.llm_service.get_completion.return_value = {
            'success': True,
            'response': 'Mock LLM response for testing extraction pipeline'
        }
    
    def test_basic_fact_extraction_from_vibe_code(self):
        """
        Test Case: Basic Fact Extraction
        
        Simulate a user inputting the following vibe code:
        "I'm picturing a female half-elf ranger who grew up in a shattered kingdom. 
        She's quiet but deadly with a bow, and she secretly longs to heal what was lost."
        
        Ensure that after memory processing, the following fields are updated:
        - Race → "Half-Elf"
        - Class → "Ranger" 
        - Gender → "Female"
        - Personality includes "quiet" or "deadly"
        - Background includes "shattered kingdom" or Child of War if inferred from SRD
        """
        input_text = (
            "I'm picturing a female half-elf ranger who grew up in a shattered kingdom. "
            "She's quiet but deadly with a bow, and she secretly longs to heal what was lost."
        )
        
        expected = {
            "race": "Half-Elf",
            "class": "Ranger", 
            "gender": "Female",
            "personality": ["quiet", "deadly"],
            "background": "shattered kingdom",
        }
        
        # Reset character data for clean test
        self.character_generator.current_character_data = {
            'name': None,
            'race': None,
            'class': None,
            'level': 1,
            'background': None,
            'personality': None,
            'backstory': None,
            'age': None,
            'gender': None,
            'alignment': None,
            'appearance': None,
            'created_date': datetime.now().isoformat(),
            'creation_method': 'conversational'
        }
        
        # Extract character details from input
        self.character_generator._extract_character_details(input_text)
        
        # Get the result
        result = self.character_generator.get_character_data()
        
        # Assertions with detailed error messages
        assert result["race"] == expected["race"], f"Expected race '{expected['race']}', got '{result['race']}'"
        assert result["class"] == expected["class"], f"Expected class '{expected['class']}', got '{result['class']}'"
        assert result["gender"] == expected["gender"], f"Expected gender '{expected['gender']}', got '{result['gender']}'"
        
        # Check personality traits (case-insensitive)
        if result.get("personality"):
            personality_lower = result["personality"].lower()
            personality_found = any(trait in personality_lower for trait in expected["personality"])
            assert personality_found, f"Expected personality traits {expected['personality']}, got '{result.get('personality')}'"
        else:
            pytest.fail(f"Expected personality traits {expected['personality']}, but personality field is empty")
        
        # Check background (case-insensitive)
        if result.get("background"):
            background_lower = result["background"].lower()
            background_found = any(term in background_lower for term in ["shattered", "kingdom"])
            assert background_found, f"Expected background to contain 'shattered' or 'kingdom', got '{result.get('background')}'"
        else:
            pytest.fail("Expected background to contain 'shattered' or 'kingdom', but background field is empty")
    
    def test_name_extraction_patterns(self):
        """Test various name extraction patterns."""
        test_cases = [
            {
                "input": "My name is Thorne Blackwood and I am a human rogue.",
                "expected": "Thorne Blackwood"
            },
            {
                "input": "I am called Elira, an elven druid.",
                "expected": "Elira"
            },
            {
                "input": "Call me Jack the Quick.",
                "expected": "Jack The Quick"
            },
            {
                "input": "I'm a character named Aria the Swift.",
                "expected": "Aria The Swift"
            }
        ]
        
        for test_case in test_cases:
            # Reset character data
            self.character_generator.current_character_data = {
                'name': None,
                'race': None,
                'class': None,
                'level': 1,
                'background': None,
                'personality': None,
                'backstory': None,
                'age': None,
                'gender': None,
                'alignment': None,
                'appearance': None,
                'created_date': datetime.now().isoformat(),
                'creation_method': 'conversational'
            }
            
            # Extract character details
            self.character_generator._extract_character_details(test_case["input"])
            result = self.character_generator.get_character_data()
            
            assert result["name"] == test_case["expected"], \
                f"Expected name '{test_case['expected']}', got '{result['name']}' for input: '{test_case['input']}'"
    
    def test_race_extraction_patterns(self):
        """Test race extraction with various patterns."""
        test_cases = [
            {"input": "I am a human fighter.", "expected": "Human"},
            {"input": "My character is an elven wizard.", "expected": "Elf"},
            {"input": "I want to be a dwarven cleric.", "expected": "Dwarf"},
            {"input": "She is a half-elf ranger.", "expected": "Half-Elf"},
            {"input": "He's a tiefling warlock.", "expected": "Tiefling"}
        ]
        
        for test_case in test_cases:
            # Reset character data
            self.character_generator.current_character_data = {
                'name': None,
                'race': None,
                'class': None,
                'level': 1,
                'background': None,
                'personality': None,
                'backstory': None,
                'age': None,
                'gender': None,
                'alignment': None,
                'appearance': None,
                'created_date': datetime.now().isoformat(),
                'creation_method': 'conversational'
            }
            
            # Extract character details
            self.character_generator._extract_character_details(test_case["input"])
            result = self.character_generator.get_character_data()
            
            assert result["race"] == test_case["expected"], \
                f"Expected race '{test_case['expected']}', got '{result['race']}' for input: '{test_case['input']}'"
    
    def test_class_extraction_patterns(self):
        """Test class extraction with various patterns."""
        test_cases = [
            {"input": "I am a human fighter.", "expected": "Fighter"},
            {"input": "My character is an elven wizard.", "expected": "Wizard"},
            {"input": "I want to be a dwarven cleric.", "expected": "Cleric"},
            {"input": "She is a half-elf ranger.", "expected": "Ranger"},
            {"input": "He's a tiefling warlock.", "expected": "Warlock"},
            {"input": "I'm a thief by trade.", "expected": "Rogue"},
            {"input": "She's a nature priest.", "expected": "Druid"}
        ]
        
        for test_case in test_cases:
            # Reset character data
            self.character_generator.current_character_data = {
                'name': None,
                'race': None,
                'class': None,
                'level': 1,
                'background': None,
                'personality': None,
                'backstory': None,
                'age': None,
                'gender': None,
                'alignment': None,
                'appearance': None,
                'created_date': datetime.now().isoformat(),
                'creation_method': 'conversational'
            }
            
            # Extract character details
            self.character_generator._extract_character_details(test_case["input"])
            result = self.character_generator.get_character_data()
            
            assert result["class"] == test_case["expected"], \
                f"Expected class '{test_case['expected']}', got '{result['class']}' for input: '{test_case['input']}'"
    
    def test_gender_extraction_patterns(self):
        """Test gender extraction from pronouns and explicit statements."""
        test_cases = [
            {"input": "He is a male human fighter.", "expected": "Male"},
            {"input": "She is a female elven wizard.", "expected": "Female"},
            {"input": "I am a woman who grew up on the streets.", "expected": "Female"},
            {"input": "My character is a guy who loves adventure.", "expected": "Male"},
            {"input": "They are a non-binary druid.", "expected": "Non-Binary"}
        ]
        
        for test_case in test_cases:
            # Reset character data
            self.character_generator.current_character_data = {
                'name': None,
                'race': None,
                'class': None,
                'level': 1,
                'background': None,
                'personality': None,
                'backstory': None,
                'age': None,
                'gender': None,
                'alignment': None,
                'appearance': None,
                'created_date': datetime.now().isoformat(),
                'creation_method': 'conversational'
            }
            
            # Extract character details
            self.character_generator._extract_character_details(test_case["input"])
            result = self.character_generator.get_character_data()
            
            assert result["gender"] == test_case["expected"], \
                f"Expected gender '{test_case['expected']}', got '{result['gender']}' for input: '{test_case['input']}'"
    
    def test_personality_trait_accumulation(self):
        """Test that personality traits accumulate over multiple inputs."""
        inputs = [
            "I am a cautious human rogue.",
            "I am also mysterious and quiet.",
            "But I can be brave when needed."
        ]
        
        # Reset character data
        self.character_generator.current_character_data = {
            'name': None,
            'race': None,
            'class': None,
            'level': 1,
            'background': None,
            'personality': None,
            'backstory': None,
            'age': None,
            'gender': None,
            'alignment': None,
            'appearance': None,
            'created_date': datetime.now().isoformat(),
            'creation_method': 'conversational'
        }
        
        expected_traits = ["cautious", "mysterious", "quiet", "brave"]
        
        # Process each input
        for input_text in inputs:
            self.character_generator._extract_character_details(input_text)
        
        result = self.character_generator.get_character_data()
        
        # Check that personality contains all expected traits
        if result.get("personality"):
            personality_lower = result["personality"].lower()
            for trait in expected_traits:
                assert trait in personality_lower, f"Expected trait '{trait}' not found in personality: '{result['personality']}'"
        else:
            pytest.fail("Expected personality traits to be accumulated, but personality field is empty")
    
    def test_backstory_accumulation(self):
        """Test that backstory details accumulate over multiple inputs."""
        inputs = [
            "I grew up on the streets as an orphan.",
            "I learned to survive by stealing.",
            "Now I work as a thief for hire."
        ]
        
        # Reset character data
        self.character_generator.current_character_data = {
            'name': None,
            'race': None,
            'class': None,
            'level': 1,
            'background': None,
            'personality': None,
            'backstory': None,
            'age': None,
            'gender': None,
            'alignment': None,
            'appearance': None,
            'created_date': datetime.now().isoformat(),
            'creation_method': 'conversational'
        }
        
        # Process each input
        for input_text in inputs:
            self.character_generator._extract_character_details(input_text)
        
        result = self.character_generator.get_character_data()
        
        # Check that backstory contains key elements
        assert result.get("backstory"), "Expected backstory to be accumulated, but backstory field is empty"
        
        backstory_lower = result["backstory"].lower()
        expected_elements = ["streets", "orphan", "stealing", "thief"]
        
        for element in expected_elements:
            assert element in backstory_lower, f"Expected backstory element '{element}' not found in: '{result['backstory']}'"
    
    def test_age_extraction(self):
        """Test age extraction from various formats."""
        test_cases = [
            {"input": "I am 25 years old.", "expected": 25},
            {"input": "She is 30 y.o.", "expected": 30},
            {"input": "He's 35 years old and experienced.", "expected": 35}
        ]
        
        for test_case in test_cases:
            # Reset character data
            self.character_generator.current_character_data = {
                'name': None,
                'race': None,
                'class': None,
                'level': 1,
                'background': None,
                'personality': None,
                'backstory': None,
                'age': None,
                'gender': None,
                'alignment': None,
                'appearance': None,
                'created_date': datetime.now().isoformat(),
                'creation_method': 'conversational'
            }
            
            # Extract character details
            self.character_generator._extract_character_details(test_case["input"])
            result = self.character_generator.get_character_data()
            
            assert result["age"] == test_case["expected"], \
                f"Expected age {test_case['expected']}, got {result['age']} for input: '{test_case['input']}'"
    
    def test_appearance_extraction(self):
        """Test appearance trait extraction."""
        input_text = "I have dark hair and green eyes. I am tall and muscular."
        
        # Reset character data
        self.character_generator.current_character_data = {
            'name': None,
            'race': None,
            'class': None,
            'level': 1,
            'background': None,
            'personality': None,
            'backstory': None,
            'age': None,
            'gender': None,
            'alignment': None,
            'appearance': None,
            'created_date': datetime.now().isoformat(),
            'creation_method': 'conversational'
        }
        
        # Extract character details
        self.character_generator._extract_character_details(input_text)
        result = self.character_generator.get_character_data()
        
        # Check that appearance contains expected traits
        assert result.get("appearance"), "Expected appearance to be extracted, but appearance field is empty"
        
        appearance_lower = result["appearance"].lower()
        expected_traits = ["dark hair", "green eyes", "tall", "muscular"]
        
        for trait in expected_traits:
            assert trait in appearance_lower, f"Expected appearance trait '{trait}' not found in: '{result['appearance']}'"
    
    def test_complete_character_extraction(self):
        """Test complete character extraction from a detailed description."""
        input_text = (
            "My name is Thorne Blackwood. I am a 35-year-old male human rogue who grew up on the streets as an orphan. "
            "I am cautious and mysterious, with dark hair and green eyes. I learned to survive by stealing and now work as a thief for hire. "
            "I am lawful neutral in alignment."
        )
        
        # Reset character data
        self.character_generator.current_character_data = {
            'name': None,
            'race': None,
            'class': None,
            'level': 1,
            'background': None,
            'personality': None,
            'backstory': None,
            'age': None,
            'gender': None,
            'alignment': None,
            'appearance': None,
            'created_date': datetime.now().isoformat(),
            'creation_method': 'conversational'
        }
        
        # Extract character details
        self.character_generator._extract_character_details(input_text)
        result = self.character_generator.get_character_data()
        
        # Verify all expected fields
        expected_fields = {
            "name": "Thorne Blackwood",
            "race": "Human",
            "class": "Rogue",
            "age": 35,
            "gender": "Male",
            "alignment": "Lawful Neutral"
        }
        
        for field, expected_value in expected_fields.items():
            assert result[field] == expected_value, \
                f"Expected {field} '{expected_value}', got '{result[field]}'"
        
        # Check personality traits
        assert result.get("personality"), "Expected personality to be extracted"
        personality_lower = result["personality"].lower()
        assert "cautious" in personality_lower, "Expected 'cautious' in personality"
        assert "mysterious" in personality_lower, "Expected 'mysterious' in personality"
        
        # Check appearance
        assert result.get("appearance"), "Expected appearance to be extracted"
        appearance_lower = result["appearance"].lower()
        assert "dark hair" in appearance_lower, "Expected 'dark hair' in appearance"
        assert "green eyes" in appearance_lower, "Expected 'green eyes' in appearance"
        
        # Check backstory
        assert result.get("backstory"), "Expected backstory to be extracted"
        backstory_lower = result["backstory"].lower()
        assert "streets" in backstory_lower, "Expected 'streets' in backstory"
        assert "orphan" in backstory_lower, "Expected 'orphan' in backstory"
        assert "stealing" in backstory_lower, "Expected 'stealing' in backstory"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 