#!/usr/bin/env python3
"""
Character Export Validator Utility

A reusable utility for validating that character data exports contain
all SRD 5.2 required fields and are formatted correctly for gameplay use.

This module can be imported by other parts of the SoloHeart system to
validate character data before saving, exporting, or using in gameplay.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


def validate_character_export(character_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that a character export contains all SRD 5.2 required fields.
    
    Args:
        character_dict: The character data dictionary to validate
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # SRD 5.2 Required Fields (core gameplay fields)
    required_fields = [
        "name", "race", "class", "background", "level", "gender",
        "personality", "hit_points", "armor_class", "speed",
        "initiative_bonus", "saving_throws", "equipment", "abilities",
        "skills", "languages", "tool_proficiencies", "features"
    ]
    
    # Optional fields that can be None/empty
    optional_fields = [
        "alignment", "age", "feats", "spells", "proficiencies",
        "background_info", "appearance", "backstory", "notes"
    ]
    
    # Check for missing required fields
    for field in required_fields:
        if field not in character_dict:
            errors.append(f"Missing required field: {field}")
        elif character_dict[field] is None:
            errors.append(f"Required field '{field}' cannot be None")
        elif isinstance(character_dict[field], str) and not character_dict[field].strip():
            errors.append(f"Required field '{field}' cannot be empty string")
        elif isinstance(character_dict[field], list) and len(character_dict[field]) == 0:
            errors.append(f"Required field '{field}' cannot be empty list")
    
    # Validate field types and formats
    if not errors:
        errors.extend(_validate_field_types(character_dict))
        errors.extend(_validate_field_values(character_dict))
        errors.extend(_validate_field_consistency(character_dict))
    
    is_valid = len(errors) == 0
    
    if is_valid:
        logger.info("Character export validation passed")
    else:
        logger.warning(f"Character export validation failed: {errors}")
    
    return is_valid, errors


def _validate_field_types(character_dict: Dict[str, Any]) -> List[str]:
    """Validate that fields have the correct data types."""
    errors = []
    
    # String fields
    string_fields = ["name", "race", "class", "background", "gender", "personality"]
    for field in string_fields:
        if field in character_dict and not isinstance(character_dict[field], str):
            errors.append(f"Field '{field}' must be a string, got {type(character_dict[field])}")
    
    # Integer fields
    integer_fields = ["level", "hit_points", "armor_class", "speed", "initiative_bonus"]
    for field in integer_fields:
        if field in character_dict and not isinstance(character_dict[field], int):
            errors.append(f"Field '{field}' must be an integer, got {type(character_dict[field])}")
    
    # List fields
    list_fields = ["equipment", "skills", "languages", "tool_proficiencies", "features", "saving_throws"]
    for field in list_fields:
        if field in character_dict and not isinstance(character_dict[field], list):
            errors.append(f"Field '{field}' must be a list, got {type(character_dict[field])}")
    
    # Dictionary fields
    dict_fields = ["abilities"]
    for field in dict_fields:
        if field in character_dict and not isinstance(character_dict[field], dict):
            errors.append(f"Field '{field}' must be a dictionary, got {type(character_dict[field])}")
    
    return errors


def _validate_field_values(character_dict: Dict[str, Any]) -> List[str]:
    """Validate that fields have reasonable values."""
    errors = []
    
    # Level validation
    if "level" in character_dict:
        level = character_dict["level"]
        if not isinstance(level, int) or level < 1 or level > 20:
            errors.append(f"Level must be between 1 and 20, got {level}")
    
    # Hit points validation
    if "hit_points" in character_dict:
        hp = character_dict["hit_points"]
        if not isinstance(hp, int) or hp < 1:
            errors.append(f"Hit points must be at least 1, got {hp}")
    
    # Armor class validation
    if "armor_class" in character_dict:
        ac = character_dict["armor_class"]
        if not isinstance(ac, int) or ac < 1 or ac > 30:
            errors.append(f"Armor class must be between 1 and 30, got {ac}")
    
    # Speed validation
    if "speed" in character_dict:
        speed = character_dict["speed"]
        if not isinstance(speed, int) or speed < 0 or speed > 120:
            errors.append(f"Speed must be between 0 and 120, got {speed}")
    
    # Race validation
    valid_races = [
        "Human", "Elf", "Dwarf", "Halfling", "Dragonborn", 
        "Gnome", "Half-Elf", "Half-Orc", "Tiefling"
    ]
    if "race" in character_dict:
        race = character_dict["race"]
        if race not in valid_races:
            errors.append(f"Invalid race '{race}'. Must be one of: {', '.join(valid_races)}")
    
    # Class validation
    valid_classes = [
        "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
        "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer",
        "Warlock", "Wizard"
    ]
    if "class" in character_dict:
        char_class = character_dict["class"]
        if char_class not in valid_classes:
            errors.append(f"Invalid class '{char_class}'. Must be one of: {', '.join(valid_classes)}")
    
    # Gender validation
    valid_genders = ["Male", "Female", "Non-Binary"]
    if "gender" in character_dict:
        gender = character_dict["gender"]
        if gender not in valid_genders:
            errors.append(f"Invalid gender '{gender}'. Must be one of: {', '.join(valid_genders)}")
    
    return errors


def _validate_field_consistency(character_dict: Dict[str, Any]) -> List[str]:
    """Validate that fields are consistent with each other."""
    errors = []
    
    # Check that abilities dict has all required ability scores
    if "abilities" in character_dict:
        abilities = character_dict["abilities"]
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for ability in required_abilities:
            if ability not in abilities:
                errors.append(f"Missing ability score: {ability}")
            elif not isinstance(abilities[ability], int) or abilities[ability] < 1 or abilities[ability] > 30:
                errors.append(f"Ability score '{ability}' must be between 1 and 30, got {abilities[ability]}")
    
    # Check that saving throws list contains valid ability names
    if "saving_throws" in character_dict:
        saving_throws = character_dict["saving_throws"]
        valid_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for save in saving_throws:
            if save not in valid_abilities:
                errors.append(f"Invalid saving throw '{save}'. Must be one of: {', '.join(valid_abilities)}")
    
    # Check that skills list contains valid skill names
    if "skills" in character_dict:
        skills = character_dict["skills"]
        valid_skills = [
            "acrobatics", "animal handling", "arcana", "athletics", "deception",
            "history", "insight", "intimidation", "investigation", "medicine",
            "nature", "perception", "performance", "persuasion", "religion",
            "sleight of hand", "stealth", "survival"
        ]
        for skill in skills:
            if skill not in valid_skills:
                errors.append(f"Invalid skill '{skill}'. Must be one of: {', '.join(valid_skills)}")
    
    return errors


def get_required_fields() -> List[str]:
    """
    Get the list of required fields for SRD 5.2 character export.
    
    Returns:
        List[str]: List of required field names
    """
    return [
        "name", "race", "class", "background", "level", "gender",
        "personality", "hit_points", "armor_class", "speed",
        "initiative_bonus", "saving_throws", "equipment", "abilities",
        "skills", "languages", "tool_proficiencies", "features"
    ]


def get_optional_fields() -> List[str]:
    """
    Get the list of optional fields for character export.
    
    Returns:
        List[str]: List of optional field names
    """
    return [
        "alignment", "age", "feats", "spells", "proficiencies",
        "background_info", "appearance", "backstory", "notes"
    ]


def get_valid_races() -> List[str]:
    """
    Get the list of valid SRD 5.2 races.
    
    Returns:
        List[str]: List of valid race names
    """
    return [
        "Human", "Elf", "Dwarf", "Halfling", "Dragonborn", 
        "Gnome", "Half-Elf", "Half-Orc", "Tiefling"
    ]


def get_valid_classes() -> List[str]:
    """
    Get the list of valid SRD 5.2 classes.
    
    Returns:
        List[str]: List of valid class names
    """
    return [
        "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
        "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer",
        "Warlock", "Wizard"
    ]


def get_valid_skills() -> List[str]:
    """
    Get the list of valid D&D 5E skills.
    
    Returns:
        List[str]: List of valid skill names
    """
    return [
        "acrobatics", "animal handling", "arcana", "athletics", "deception",
        "history", "insight", "intimidation", "investigation", "medicine",
        "nature", "perception", "performance", "persuasion", "religion",
        "sleight of hand", "stealth", "survival"
    ]


def create_character_template() -> Dict[str, Any]:
    """
    Create a template character dictionary with all required fields.
    
    Returns:
        Dict[str, Any]: Template character with placeholder values
    """
    return {
        "name": "",
        "race": "",
        "class": "",
        "background": "",
        "level": 1,
        "gender": "",
        "personality": "",
        "hit_points": 10,
        "armor_class": 10,
        "speed": 30,
        "initiative_bonus": 0,
        "saving_throws": [],
        "equipment": [],
        "abilities": {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        },
        "skills": [],
        "languages": ["Common"],
        "tool_proficiencies": [],
        "features": []
    } 