#!/usr/bin/env python3
"""
Character Fact Extraction Utilities for SoloHeart

This module provides robust extraction functions for character facts like race, class, and background
from natural language input. The extraction logic prioritizes longer matches to avoid substring
collisions (e.g., "Half-Elf" over "Elf").
"""

import re
import logging
from typing import Optional, List

# Configure logging
logger = logging.getLogger(__name__)

# Core SRD data for character facts
RACES = [
    "Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome", "Half-Elf", "Half-Orc", "Tiefling"
]

CLASSES = [
    "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", 
    "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
]

BACKGROUNDS = [
    "Acolyte", "Criminal", "Folk Hero", "Noble", "Sage", "Soldier"
]

def extract_race_from_text(text: str) -> Optional[str]:
    """
    Extract race from text with priority for longer matches.
    
    This function implements a robust race extraction strategy that:
    1. Sorts races in descending order of length to prioritize longer matches
    2. Uses regex word boundaries (\b) to ensure full word matches
    3. Handles hyphenated races like "Half-Elf" correctly
    4. Falls back to substring matching if word boundaries fail
    5. Returns the first matching race found or None
    
    Args:
        text (str): The input text to search for race mentions
        
    Returns:
        Optional[str]: The extracted race name (properly capitalized) or None if no match
        
    Examples:
        >>> extract_race_from_text("I am a Half-Elf ranger")
        'Half-Elf'
        >>> extract_race_from_text("I'm an elf")
        'Elf'
        >>> extract_race_from_text("My character is a Dragonborn")
        'Dragonborn'
        >>> extract_race_from_text("I want to be a human")
        'Human'
    """
    if not text:
        return None
    
    text_lower = text.lower()
    logger.debug(f"🔍 Extracting race from text: '{text[:100]}...'")
    
    # Sort races by length (longest first) to prioritize longer matches
    # This prevents "elf" from matching before "half-elf"
    races_sorted = sorted(RACES, key=len, reverse=True)
    
    # First, try to find exact word matches with word boundaries
    for race in races_sorted:
        race_lower = race.lower()
        
        # Use word boundary pattern to match whole words only
        # This ensures "half-elf" doesn't match "elf" in "half-elf"
        word_pattern = r'\b' + re.escape(race_lower) + r'\b'
        
        if re.search(word_pattern, text_lower):
            logger.debug(f"✅ Race detected (word boundary): {race}")
            return race
    
    # Fallback: check for substring matches (still in length order)
    for race in races_sorted:
        race_lower = race.lower()
        
        if race_lower in text_lower:
            # Additional validation: check for common confirmation patterns
            confirmation_patterns = [
                f"a {race_lower}", f"the {race_lower}", f"my {race_lower}",
                f"i am a {race_lower}", f"i'm a {race_lower}",
                f"you are a {race_lower}", f"your character is a {race_lower}"
            ]
            
            if any(pattern in text_lower for pattern in confirmation_patterns):
                logger.debug(f"✅ Race detected (substring with confirmation): {race}")
                return race
    
    logger.debug(f"⚠️ No race detected in text: '{text[:100]}...'")
    return None

def extract_class_from_text(text: str) -> Optional[str]:
    """
    Extract class from text with priority for longer matches.
    
    Similar to race extraction, this function prioritizes longer class names
    to avoid substring collisions.
    
    Args:
        text (str): The input text to search for class mentions
        
    Returns:
        Optional[str]: The extracted class name (properly capitalized) or None if no match
    """
    if not text:
        return None
    
    text_lower = text.lower()
    logger.debug(f"🔍 Extracting class from text: '{text[:100]}...'")
    
    # Sort classes by length (longest first) to prioritize longer matches
    classes_sorted = sorted(CLASSES, key=len, reverse=True)
    
    # First, try to find exact word matches with word boundaries
    for char_class in classes_sorted:
        class_lower = char_class.lower()
        
        # Use word boundary pattern to match whole words only
        word_pattern = r'\b' + re.escape(class_lower) + r'\b'
        
        if re.search(word_pattern, text_lower):
            logger.debug(f"✅ Class detected (word boundary): {char_class}")
            return char_class
    
    # Fallback: check for substring matches (still in length order)
    for char_class in classes_sorted:
        class_lower = char_class.lower()
        
        if class_lower in text_lower:
            # Additional validation: check for common confirmation patterns
            confirmation_patterns = [
                f"a {class_lower}", f"the {class_lower}", f"my {class_lower}",
                f"i am a {class_lower}", f"i'm a {class_lower}",
                f"you are a {class_lower}", f"your character is a {class_lower}"
            ]
            
            if any(pattern in text_lower for pattern in confirmation_patterns):
                logger.debug(f"✅ Class detected (substring with confirmation): {char_class}")
                return char_class
    
    logger.debug(f"⚠️ No class detected in text: '{text[:100]}...'")
    return None

def extract_background_from_text(text: str) -> Optional[str]:
    """
    Extract background from text with priority for longer matches.
    
    Args:
        text (str): The input text to search for background mentions
        
    Returns:
        Optional[str]: The extracted background name (properly capitalized) or None if no match
    """
    if not text:
        return None
    
    text_lower = text.lower()
    logger.debug(f"🔍 Extracting background from text: '{text[:100]}...'")
    
    # Sort backgrounds by length (longest first) to prioritize longer matches
    backgrounds_sorted = sorted(BACKGROUNDS, key=len, reverse=True)
    
    # First, try to find exact word matches with word boundaries
    for background in backgrounds_sorted:
        bg_lower = background.lower()
        
        # Use word boundary pattern to match whole words only
        word_pattern = r'\b' + re.escape(bg_lower) + r'\b'
        
        if re.search(word_pattern, text_lower):
            logger.debug(f"✅ Background detected (word boundary): {background}")
            return background
    
    # Fallback: check for substring matches (still in length order)
    for background in backgrounds_sorted:
        bg_lower = background.lower()
        
        if bg_lower in text_lower:
            # Additional validation: check for common confirmation patterns
            confirmation_patterns = [
                f"a {bg_lower}", f"the {bg_lower}", f"my {bg_lower}",
                f"i am a {bg_lower}", f"i'm a {bg_lower}",
                f"you are a {bg_lower}", f"your character is a {bg_lower}",
                f"{bg_lower} background"
            ]
            
            if any(pattern in text_lower for pattern in confirmation_patterns):
                logger.debug(f"✅ Background detected (substring with confirmation): {background}")
                return background
    
    logger.debug(f"⚠️ No background detected in text: '{text[:100]}...'")
    return None

def extract_name_from_text(text: str) -> Optional[str]:
    """
    Extract character name from text using various patterns.
    
    Args:
        text (str): The input text to search for name mentions
        
    Returns:
        Optional[str]: The extracted name (properly capitalized) or None if no match
    """
    if not text:
        return None
    
    text_lower = text.lower()
    logger.debug(f"🔍 Extracting name from text: '{text[:100]}...'")
    
    # Name extraction patterns
    name_patterns = [
        r"my name is ([a-z]+)", r"i'm called ([a-z]+)", r"call me ([a-z]+)",
        r"my character is named ([a-z]+)", r"name me ([a-z]+)",
        r"^i am ([a-z]+)$", r"^i'm ([a-z]+)$",
        r"my name's ([a-z]+)", r"i go by ([a-z]+)",
        r"my character is ([a-z]+)", r"([a-z]+) is my name",
        r"name is ([a-z]+)", r"called ([a-z]+)", r"named ([a-z]+)",
        r"my character's name is ([a-z]+)", r"character name is ([a-z]+)",
        r"i want to be ([a-z]+)", r"i want to play ([a-z]+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text_lower)
        if match:
            name = match.group(1).title()
            logger.debug(f"✅ Name detected: {name}")
            return name
    
    # If no pattern matches, try to extract a single word that could be a name
    words = text_lower.split()
    for word in words:
        if len(word) > 2 and word.isalpha() and word not in [
            "the", "and", "but", "for", "with", "from", "that", "this", "they", "them", "their",
            "have", "will", "would", "could", "should", "want", "like", "make", "create",
            "character", "name", "race", "class", "background", "personality", "ability",
            "scores", "stats", "strength", "dexterity", "constitution", "intelligence",
            "wisdom", "charisma"
        ]:
            name = word.title()
            logger.debug(f"✅ Name detected (single word): {name}")
            return name
    
    logger.debug(f"⚠️ No name detected in text: '{text[:100]}...'")
    return None 