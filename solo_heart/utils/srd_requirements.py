#!/usr/bin/env python3
"""
SRD Requirements for D&D 5E Character Creation

This module defines all the required and optional fields for a complete D&D 5E character sheet
based on the System Reference Document (SRD). It provides validation and tracking of missing fields.
"""

import json
import logging
from typing import Dict, List, Optional, Set, Any
from enum import Enum

logger = logging.getLogger(__name__)

class FieldPriority(Enum):
    """Priority levels for character sheet fields."""
    CRITICAL = 1    # Must have to start the game
    HIGH = 2        # Important for gameplay
    MEDIUM = 3      # Nice to have
    LOW = 4         # Optional flavor

class SRDRequirements:
    """Manages SRD requirements for D&D 5E character creation."""
    
    def __init__(self):
        self.required_fields = {
            # Core Identity (CRITICAL)
            'name': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Character name',
                'validation': lambda x: isinstance(x, str) and len(x.strip()) > 0
            },
            'race': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Character race (Human, Elf, Dwarf, etc.)',
                'validation': lambda x: isinstance(x, str) and x in self._get_valid_races()
            },
            'class': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Character class (Fighter, Wizard, etc.)',
                'validation': lambda x: isinstance(x, str) and x in self._get_valid_classes()
            },
            'level': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Character level (default: 1)',
                'validation': lambda x: isinstance(x, int) and 1 <= x <= 20,
                'default': 1
            },
            
            # Ability Scores (CRITICAL)
            'strength': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Strength ability score',
                'validation': lambda x: isinstance(x, int) and 1 <= x <= 20
            },
            'dexterity': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Dexterity ability score',
                'validation': lambda x: isinstance(x, int) and 1 <= x <= 20
            },
            'constitution': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Constitution ability score',
                'validation': lambda x: isinstance(x, int) and 1 <= x <= 20
            },
            'intelligence': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Intelligence ability score',
                'validation': lambda x: isinstance(x, int) and 1 <= x <= 20
            },
            'wisdom': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Wisdom ability score',
                'validation': lambda x: isinstance(x, int) and 1 <= x <= 20
            },
            'charisma': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Charisma ability score',
                'validation': lambda x: isinstance(x, int) and 1 <= x <= 20
            },
            
            # Combat Stats (CRITICAL)
            'hit_points': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Maximum hit points',
                'validation': lambda x: isinstance(x, int) and x > 0
            },
            'armor_class': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Armor Class',
                'validation': lambda x: isinstance(x, int) and x >= 0
            },
            'initiative': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Initiative modifier',
                'validation': lambda x: isinstance(x, int)
            },
            'speed': {
                'priority': FieldPriority.CRITICAL,
                'description': 'Movement speed in feet',
                'validation': lambda x: isinstance(x, int) and x > 0
            },
            
            # Background & Identity (HIGH)
            'background': {
                'priority': FieldPriority.HIGH,
                'description': 'Character background',
                'validation': lambda x: isinstance(x, str) and x in self._get_valid_backgrounds()
            },
            'alignment': {
                'priority': FieldPriority.HIGH,
                'description': 'Character alignment',
                'validation': lambda x: isinstance(x, str) and x in self._get_valid_alignments()
            },
            'age': {
                'priority': FieldPriority.HIGH,
                'description': 'Character age',
                'validation': lambda x: isinstance(x, int) and x > 0
            },
            'gender': {
                'priority': FieldPriority.HIGH,
                'description': 'Character gender',
                'validation': lambda x: isinstance(x, str) and x in ['Male', 'Female', 'Non-binary', 'Other']
            },
            
            # Proficiencies (HIGH)
            'proficiencies': {
                'priority': FieldPriority.HIGH,
                'description': 'Skill and tool proficiencies',
                'validation': lambda x: isinstance(x, list)
            },
            'languages': {
                'priority': FieldPriority.HIGH,
                'description': 'Languages known',
                'validation': lambda x: isinstance(x, list)
            },
            
            # Equipment (HIGH)
            'equipment': {
                'priority': FieldPriority.HIGH,
                'description': 'Character equipment and gear',
                'validation': lambda x: isinstance(x, list)
            },
            'weapons': {
                'priority': FieldPriority.HIGH,
                'description': 'Weapons carried',
                'validation': lambda x: isinstance(x, list)
            },
            'armor': {
                'priority': FieldPriority.HIGH,
                'description': 'Armor worn',
                'validation': lambda x: isinstance(x, str) or x is None
            },
            
            # Personality & Story (MEDIUM)
            'personality_traits': {
                'priority': FieldPriority.MEDIUM,
                'description': 'Character personality traits',
                'validation': lambda x: isinstance(x, list)
            },
            'ideals': {
                'priority': FieldPriority.MEDIUM,
                'description': 'Character ideals',
                'validation': lambda x: isinstance(x, list)
            },
            'bonds': {
                'priority': FieldPriority.MEDIUM,
                'description': 'Character bonds',
                'validation': lambda x: isinstance(x, list)
            },
            'flaws': {
                'priority': FieldPriority.MEDIUM,
                'description': 'Character flaws',
                'validation': lambda x: isinstance(x, list)
            },
            'motivations': {
                'priority': FieldPriority.MEDIUM,
                'description': 'Character motivations',
                'validation': lambda x: isinstance(x, list)
            },
            'backstory': {
                'priority': FieldPriority.MEDIUM,
                'description': 'Character backstory',
                'validation': lambda x: isinstance(x, str) or x is None
            },
            
            # Combat & Abilities (MEDIUM)
            'combat_style': {
                'priority': FieldPriority.MEDIUM,
                'description': 'Preferred combat approach',
                'validation': lambda x: isinstance(x, str) or x is None
            },
            'spells': {
                'priority': FieldPriority.MEDIUM,
                'description': 'Spells known/prepared',
                'validation': lambda x: isinstance(x, list)
            },
            'features': {
                'priority': FieldPriority.MEDIUM,
                'description': 'Class and racial features',
                'validation': lambda x: isinstance(x, list)
            },
            
            # Flavor & Details (LOW)
            'appearance': {
                'priority': FieldPriority.LOW,
                'description': 'Physical appearance',
                'validation': lambda x: isinstance(x, str) or x is None
            },
            'emotional_themes': {
                'priority': FieldPriority.LOW,
                'description': 'Emotional themes and trauma',
                'validation': lambda x: isinstance(x, list)
            },
            'traumas': {
                'priority': FieldPriority.LOW,
                'description': 'Past traumas and experiences',
                'validation': lambda x: isinstance(x, list)
            },
            'relational_history': {
                'priority': FieldPriority.LOW,
                'description': 'Relationships and connections',
                'validation': lambda x: isinstance(x, dict)
            },
            'traits': {
                'priority': FieldPriority.LOW,
                'description': 'Additional character traits',
                'validation': lambda x: isinstance(x, list)
            }
        }
    
    def _get_valid_races(self) -> List[str]:
        """Get valid D&D 5E races from SRD."""
        return [
            "Human", "Elf", "Dwarf", "Halfling", "Dragonborn", 
            "Gnome", "Half-Elf", "Half-Orc", "Tiefling"
        ]
    
    def _get_valid_classes(self) -> List[str]:
        """Get valid D&D 5E classes from SRD."""
        return [
            "Barbarian", "Bard", "Cleric", "Druid", "Fighter", 
            "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", 
            "Warlock", "Wizard"
        ]
    
    def _get_valid_backgrounds(self) -> List[str]:
        """Get valid D&D 5E backgrounds from SRD."""
        return [
            "Acolyte", "Criminal", "Folk Hero", "Noble", "Sage", "Soldier"
        ]
    
    def _get_valid_alignments(self) -> List[str]:
        """Get valid D&D 5E alignments."""
        return [
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral", 
            "Lawful Evil", "Neutral Evil", "Chaotic Evil"
        ]
    
    def get_missing_fields(self, character_data: Dict[str, Any], priority: Optional[FieldPriority] = None) -> Dict[str, List[str]]:
        """
        Get missing fields organized by priority.
        
        Args:
            character_data: Current character data
            priority: Optional priority filter
            
        Returns:
            Dict mapping priority to list of missing field names
        """
        missing_by_priority = {}
        
        for field_name, field_info in self.required_fields.items():
            if priority and field_info['priority'] != priority:
                continue
                
            field_value = character_data.get(field_name)
            
            # Check if field is missing or invalid
            is_missing = (
                field_value is None or 
                field_value == "" or 
                field_value == [] or 
                field_value == {} or
                not field_info['validation'](field_value)
            )
            
            if is_missing:
                priority_level = field_info['priority']
                if priority_level not in missing_by_priority:
                    missing_by_priority[priority_level] = []
                missing_by_priority[priority_level].append(field_name)
        
        return missing_by_priority
    
    def get_critical_missing_fields(self, character_data: Dict[str, Any]) -> List[str]:
        """Get only critical missing fields."""
        missing = self.get_missing_fields(character_data, FieldPriority.CRITICAL)
        return missing.get(FieldPriority.CRITICAL, [])
    
    def get_high_priority_missing_fields(self, character_data: Dict[str, Any]) -> List[str]:
        """Get high priority missing fields."""
        missing = self.get_missing_fields(character_data, FieldPriority.HIGH)
        return missing.get(FieldPriority.HIGH, [])
    
    def is_character_complete(self, character_data: Dict[str, Any]) -> bool:
        """Check if character has all critical fields filled."""
        critical_missing = self.get_critical_missing_fields(character_data)
        return len(critical_missing) == 0
    
    def get_completion_percentage(self, character_data: Dict[str, Any]) -> float:
        """Get character completion percentage based on priority weights."""
        total_weight = 0
        completed_weight = 0
        
        for field_name, field_info in self.required_fields.items():
            # Weight by priority (critical = 4, high = 3, medium = 2, low = 1)
            weight = 5 - field_info['priority'].value
            
            field_value = character_data.get(field_name)
            is_complete = (
                field_value is not None and 
                field_value != "" and 
                field_value != [] and 
                field_value != {} and
                field_info['validation'](field_value)
            )
            
            total_weight += weight
            if is_complete:
                completed_weight += weight
        
        return (completed_weight / total_weight * 100) if total_weight > 0 else 0
    
    def get_field_description(self, field_name: str) -> str:
        """Get human-readable description of a field."""
        if field_name in self.required_fields:
            return self.required_fields[field_name]['description']
        return f"Unknown field: {field_name}"
    
    def get_field_priority(self, field_name: str) -> FieldPriority:
        """Get priority level of a field."""
        if field_name in self.required_fields:
            return self.required_fields[field_name]['priority']
        return FieldPriority.LOW
    
    def validate_field(self, field_name: str, value: Any) -> bool:
        """Validate a specific field value."""
        if field_name in self.required_fields:
            return self.required_fields[field_name]['validation'](value)
        return True
    
    def get_missing_fields_summary(self, character_data: Dict[str, Any]) -> str:
        """Get a human-readable summary of missing fields for Ollama."""
        missing_by_priority = self.get_missing_fields(character_data)
        
        if not missing_by_priority:
            return "Character sheet is complete!"
        
        summary_parts = []
        
        for priority in [FieldPriority.CRITICAL, FieldPriority.HIGH, FieldPriority.MEDIUM, FieldPriority.LOW]:
            if priority in missing_by_priority:
                priority_name = priority.name.replace('_', ' ').title()
                fields = missing_by_priority[priority]
                field_descriptions = [self.get_field_description(f) for f in fields]
                summary_parts.append(f"{priority_name}: {', '.join(field_descriptions)}")
        
        return "Missing fields: " + "; ".join(summary_parts) 