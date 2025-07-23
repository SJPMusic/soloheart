#!/usr/bin/env python3
"""
Test Vibe Code Character Creation SRD Compliance
Validates that the Vibe Code system only uses SRD 5.2 content and generates complete character sheets.
"""

import sys
import os
import json
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add the game_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'game_app'))

from character_creator.vibe_code_creator import VibeCodeCharacterCreator

class TestVibeCodeSRDCompliance:
    """Test suite for Vibe Code character creation SRD compliance."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock the LLM service to avoid actual API calls
        with patch('character_creator.vibe_code_creator.chat_completion', create=True) as mock_chat:
            self.mock_chat = mock_chat
            self.vibe_creator = VibeCodeCharacterCreator()
    
    def test_srd_races_loaded(self):
        """Test that SRD races are properly loaded."""
        assert self.vibe_creator.srd_races is not None
        assert len(self.vibe_creator.srd_races) > 0
        
        # Check for specific SRD races
        expected_races = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling']
        for race in expected_races:
            assert race in self.vibe_creator.srd_races, f"SRD race '{race}' not found"
    
    def test_srd_classes_loaded(self):
        """Test that SRD classes are properly loaded."""
        assert self.vibe_creator.srd_classes is not None
        assert len(self.vibe_creator.srd_classes) > 0
        
        # Check for specific SRD classes
        expected_classes = ['Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard']
        for class_name in expected_classes:
            assert class_name in self.vibe_creator.srd_classes, f"SRD class '{class_name}' not found"
    
    def test_srd_backgrounds_loaded(self):
        """Test that SRD backgrounds are properly loaded."""
        assert self.vibe_creator.srd_backgrounds is not None
        assert len(self.vibe_creator.srd_backgrounds) > 0
        
        # Check for specific SRD backgrounds
        expected_backgrounds = ['Acolyte', 'Criminal', 'Folk Hero', 'Guild Artisan', 'Hermit', 'Noble', 'Outlander', 'Sage', 'Soldier', 'Urchin']
        for background in expected_backgrounds:
            assert background in self.vibe_creator.srd_backgrounds, f"SRD background '{background}' not found"
    
    def test_srd_validation_races(self):
        """Test SRD validation for races."""
        # Valid SRD races
        assert self.vibe_creator._validate_srd_content('race', 'Human') == True
        assert self.vibe_creator._validate_srd_content('race', 'Elf') == True
        assert self.vibe_creator._validate_srd_content('race', 'Dwarf') == True
        
        # Invalid non-SRD races
        assert self.vibe_creator._validate_srd_content('race', 'Aasimar') == False
        assert self.vibe_creator._validate_srd_content('race', 'Goblin') == False
        assert self.vibe_creator._validate_srd_content('race', 'Tabaxi') == False
    
    def test_srd_validation_classes(self):
        """Test SRD validation for classes."""
        # Valid SRD classes
        assert self.vibe_creator._validate_srd_content('class', 'Fighter') == True
        assert self.vibe_creator._validate_srd_content('class', 'Wizard') == True
        assert self.vibe_creator._validate_srd_content('class', 'Cleric') == True
        
        # Invalid non-SRD classes
        assert self.vibe_creator._validate_srd_content('class', 'Artificer') == False
        assert self.vibe_creator._validate_srd_content('class', 'Blood Hunter') == False
    
    def test_srd_validation_backgrounds(self):
        """Test SRD validation for backgrounds."""
        # Valid SRD backgrounds
        assert self.vibe_creator._validate_srd_content('background', 'Soldier') == True
        assert self.vibe_creator._validate_srd_content('background', 'Acolyte') == True
        assert self.vibe_creator._validate_srd_content('background', 'Criminal') == True
        
        # Invalid non-SRD backgrounds
        assert self.vibe_creator._validate_srd_content('background', 'Anthropologist') == False
        assert self.vibe_creator._validate_srd_content('background', 'Archaeologist') == False
    
    def test_extract_character_info_srd_compliance(self):
        """Test that character info extraction enforces SRD compliance."""
        # Mock LLM response with non-SRD content
        self.mock_chat.return_value = '{"race": "Aasimar", "class": "Artificer", "background": "Anthropologist"}'
        
        result = self.vibe_creator._extract_character_info("I want to be an Aasimar Artificer with Anthropologist background")
        
        # Should replace non-SRD content with SRD equivalents
        assert result.get('race') == 'Human'  # Default SRD race
        assert result.get('class') == 'Fighter'  # Default SRD class
        assert result.get('background') == 'Soldier'  # Default SRD background
    
    def test_extract_character_info_srd_valid(self):
        """Test that valid SRD content is preserved."""
        # Mock LLM response with valid SRD content
        self.mock_chat.return_value = '{"race": "Elf", "class": "Wizard", "background": "Sage"}'
        
        result = self.vibe_creator._extract_character_info("I want to be an Elf Wizard with Sage background")
        
        # Should preserve valid SRD content
        assert result.get('race') == 'Elf'
        assert result.get('class') == 'Wizard'
        assert result.get('background') == 'Sage'
    
    def test_character_completion_requirements(self):
        """Test that character completion requires all necessary fields."""
        # Test incomplete character
        self.vibe_creator.current_character_data = {
            'name': 'Test',
            'race': 'Human',
            'class': 'Fighter'
            # Missing level and background
        }
        assert self.vibe_creator._is_character_complete() == False
        
        # Test complete character
        self.vibe_creator.current_character_data = {
            'name': 'Test',
            'race': 'Human',
            'class': 'Fighter',
            'level': 1,
            'background': 'Soldier'
        }
        assert self.vibe_creator._is_character_complete() == True
    
    def test_character_finalization_srd_compliance(self):
        """Test that character finalization enforces SRD compliance."""
        # Set up character with some non-SRD content
        self.vibe_creator.current_character_data = {
            'name': 'Test',
            'race': 'Aasimar',  # Non-SRD
            'class': 'Artificer',  # Non-SRD
            'background': 'Anthropologist',  # Non-SRD
            'level': 1
        }
        
        # Mock character manager
        with patch.object(self.vibe_creator, 'character_manager') as mock_manager:
            mock_manager.create_character.return_value = {
                'basic_info': {'name': 'Test'},
                'ability_scores': {},
                'saving_throws': {},
                'skills': {},
                'combat_stats': {},
                'proficiencies': {},
                'equipment': {},
                'personality': {},
                'features': {},
                'spellcasting': {},
                'background_info': {}
            }
            
            result = self.vibe_creator._finalize_character()
            
            # Should replace non-SRD content
            assert self.vibe_creator.current_character_data['race'] == 'Human'
            assert self.vibe_creator.current_character_data['class'] == 'Fighter'
            assert self.vibe_creator.current_character_data['background'] == 'Soldier'
    
    def test_character_finalization_complete_fields(self):
        """Test that character finalization includes all required fields."""
        self.vibe_creator.current_character_data = {
            'name': 'Test',
            'race': 'Human',
            'class': 'Fighter',
            'background': 'Soldier',
            'level': 1
        }
        
        # Mock character manager to return complete character
        with patch.object(self.vibe_creator, 'character_manager') as mock_manager:
            mock_manager.create_character.return_value = {
                'basic_info': {'name': 'Test', 'race': 'Human', 'class': 'Fighter', 'level': 1},
                'ability_scores': {'strength': 10, 'dexterity': 10, 'constitution': 10, 'intelligence': 10, 'wisdom': 10, 'charisma': 10},
                'saving_throws': {'strength': False, 'dexterity': False, 'constitution': True, 'intelligence': False, 'wisdom': False, 'charisma': False},
                'skills': {'athletics': False, 'acrobatics': False, 'stealth': False},
                'combat_stats': {'hit_points': 12, 'armor_class': 16, 'initiative': 0, 'speed': 30},
                'proficiencies': {'armor': ['light', 'medium', 'heavy', 'shields'], 'weapons': ['simple', 'martial']},
                'equipment': {'weapons': [], 'armor': [], 'gear': []},
                'personality': {'traits': [], 'ideals': [], 'bonds': [], 'flaws': []},
                'features': [],
                'spellcasting': {'ability': None, 'spells': []},
                'background_info': {'feature': 'Military Rank'}
            }
            
            result = self.vibe_creator._finalize_character()
            
            assert result['success'] == True
            assert result['is_complete'] == True
            
            # Verify all required sections are present
            character = result['character_data']
            required_sections = ['basic_info', 'ability_scores', 'saving_throws', 'skills', 
                               'combat_stats', 'proficiencies', 'equipment', 'personality', 
                               'features', 'spellcasting', 'background_info']
            
            for section in required_sections:
                assert section in character, f"Missing required section: {section}"
    
    def test_srd_alternative_suggestions(self):
        """Test that SRD alternatives are suggested for invalid content."""
        assert self.vibe_creator._suggest_srd_alternative('race', 'Aasimar') == 'Human'
        assert self.vibe_creator._suggest_srd_alternative('class', 'Artificer') == 'Fighter'
        assert self.vibe_creator._suggest_srd_alternative('background', 'Anthropologist') == 'Soldier'
    
    def test_prompt_srd_compliance(self):
        """Test that prompts include SRD compliance instructions."""
        assert "SRD" in self.vibe_creator.initial_prompt
        assert "SRD" in self.vibe_creator.followup_prompt
        assert "Human, Elf, Dwarf" in self.vibe_creator.initial_prompt
        assert "Barbarian, Bard, Cleric" in self.vibe_creator.initial_prompt
        assert "Acolyte, Criminal, Folk Hero" in self.vibe_creator.initial_prompt

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 