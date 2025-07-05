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
    Extract race from text with stricter validation and confidence scoring.
    Only return a race if the match is high-confidence (strong pattern or context).
    """
    if not text:
        return None
    text_lower = text.lower()
    logger.debug(f"🔍 Extracting race from text: '{text[:100]}...'")
    races_sorted = sorted(RACES, key=len, reverse=True)
    # High-confidence patterns
    for race in races_sorted:
        race_lower = race.lower()
        # Strong context: 'a/an/the/my [race]', 'is a [race]', etc.
        patterns = [
            rf'\b(?:a|an|the|my|is a|is an|was a|was an)\s+{re.escape(race_lower)}\b',
            rf'\b{re.escape(race_lower)}\b [a-z]+',  # '[race] [class]'
            rf'\b[a-z]+ {re.escape(race_lower)}\b',  # '[class] [race]'
        ]
        for pat in patterns:
            if re.search(pat, text_lower):
                logger.debug(f"✅ High-confidence race detected: {race}")
                return race
    # Fallback: word boundary only if not part of another word
    for race in races_sorted:
        race_lower = race.lower()
        if re.search(rf'\b{re.escape(race_lower)}\b', text_lower):
            logger.debug(f"✅ Race detected: {race}")
            return race
    
    # If no race found but we have a class, default to Human for common cases
    class_found = extract_class_from_text(text)
    if class_found and any(word in text_lower for word in ['he', 'she', 'his', 'her', 'him', 'he\'s', 'she\'s']):
        logger.debug(f"✅ Defaulting to Human (class found: {class_found})")
        return "Human"
    
    logger.debug(f"⚠️ No race detected in text: '{text[:100]}...'")
    return None

def extract_class_from_text(text: str) -> Optional[str]:
    """
    Extract class from text with stricter validation and confidence scoring.
    Only return a class if the match is high-confidence (strong pattern or context).
    """
    if not text:
        return None
    text_lower = text.lower()
    logger.debug(f"🔍 Extracting class from text: '{text[:100]}...'")
    classes_sorted = sorted(CLASSES, key=len, reverse=True)
    for char_class in classes_sorted:
        class_lower = char_class.lower()
        patterns = [
            rf'\b(?:a|an|the|my|is a|is an|was a|was an)\s+{re.escape(class_lower)}\b',
            rf'\b{re.escape(class_lower)}\b [a-z]+',
            rf'\b[a-z]+ {re.escape(class_lower)}\b',
        ]
        for pat in patterns:
            if re.search(pat, text_lower):
                logger.debug(f"✅ High-confidence class detected: {char_class}")
                return char_class
    for char_class in classes_sorted:
        class_lower = char_class.lower()
        if re.search(rf'\b{re.escape(class_lower)}\b', text_lower):
            logger.debug(f"✅ Class detected: {char_class}")
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
    Extract character name from text using stricter patterns and context.
    Avoid pronouns, verbs, and common words. Only return if high-confidence.
    """
    if not text:
        return None
    text_lower = text.lower()
    logger.debug(f"🔍 Extracting name from text: '{text[:100]}...'")
    # Name extraction patterns (high-confidence)
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
            # Filter out pronouns, verbs, and common words
            if name.lower() in [
                "her", "his", "their", "wields", "fights", "is", "was", "has", "had",
                "she", "he", "they", "it", "you", "i", "we", "me", "him", "them", "us"
            ]:
                continue
            logger.debug(f"✅ High-confidence name detected: {name}")
            return name
    # Do not use fallback single-word extraction (prone to false positives)
    logger.debug(f"⚠️ No high-confidence name detected in text: '{text[:100]}...'")
    return None

def extract_emotional_themes(text: str) -> List[str]:
    """
    Extract emotional and motivational themes from multi-sentence input.
    Returns a list of detected themes/keywords (e.g., betrayal, revenge, guilt, hope, sadism).
    """
    if not text:
        return []
    text_lower = text.lower()
    themes = set()
    # Theme keywords and synonyms
    theme_map = {
        "betrayal": ["betray", "betrayed", "treachery", "traitor"],
        "revenge": ["revenge", "vengeance", "avenge", "retribution"],
        "guilt": ["guilt", "guilty", "regret", "shame"],
        "hope": ["hope", "optimism", "dream", "aspire", "future"],
        "fear": ["fear", "afraid", "scared", "coward", "hide", "hiding"],
        "anger": ["anger", "angry", "rage", "furious", "wrath"],
        "sadism": ["smiles when she kills", "smiles when he kills", "enjoys killing", "enjoys pain", "cruel", "sadist", "takes pleasure in"],
        "loss": ["lost", "loss", "died", "killed", "destroyed", "death", "grief"],
        "justice": ["justice", "righteous", "punish", "punishment"],
        "redemption": ["redemption", "redeem", "atonement", "forgiveness"],
        "ambition": ["ambition", "ambitious", "power", "rise", "conquer"],
        "love": ["love", "loved", "loving", "affection", "cares for"],
        "loneliness": ["alone", "lonely", "solitude", "isolated"]
    }
    for theme, keywords in theme_map.items():
        for kw in keywords:
            if kw in text_lower:
                themes.add(theme)
    return list(themes)

def extract_combat_style(text: str) -> Optional[str]:
    """
    Extract combat style or fighting approach from text.
    Looks for weapon usage, fighting techniques, or combat preferences.
    """
    if not text:
        return None
    text_lower = text.lower()
    logger.debug(f"🔍 Extracting combat style from text: '{text[:100]}...'")
    
    # Combat style patterns
    combat_patterns = [
        r"wields? ([^,\.]+)",  # "wields twin axes", "wields a sword"
        r"uses? ([^,\.]+)",   # "uses a longbow", "uses daggers"
        r"fights? with ([^,\.]+)",  # "fights with nothing more than a giant axe"
        r"armed with ([^,\.]+)",  # "armed with twin daggers"
        r"prefers? ([^,\.]+)",  # "prefers ranged combat"
        r"specializes? in ([^,\.]+)",  # "specializes in dual wielding"
        r"masters? of ([^,\.]+)",  # "master of the bow"
        r"expert in ([^,\.]+)",  # "expert in hand-to-hand combat"
    ]
    
    for pattern in combat_patterns:
        match = re.search(pattern, text_lower)
        if match:
            style = match.group(1).strip()
            # Filter out common words that aren't combat-related
            if style and len(style) > 2 and style not in ["the", "and", "or", "but", "for", "with", "by", "from"]:
                logger.debug(f"✅ Combat style detected: {style}")
                return style.title()
    
    logger.debug(f"⚠️ No combat style detected in text: '{text[:100]}...'")
    return None

def extract_traits(text: str) -> List[str]:
    """
    Extract character traits or signature behaviors from text.
    Returns a list of detected traits.
    """
    if not text:
        return []
    text_lower = text.lower()
    logger.debug(f"🔍 Extracting traits from text: '{text[:100]}...'")
    
    traits = []
    
    # Trait patterns
    trait_patterns = [
        r"always ([^,\.]+)",  # "always angry", "always cautious"
        r"never ([^,\.]+)",   # "never trusts", "never gives up"
        r"constantly ([^,\.]+)",  # "constantly vigilant"
        r"tends to ([^,\.]+)",  # "tends to overthink"
        r"known for ([^,\.]+)",  # "known for his temper"
        r"famous for ([^,\.]+)",  # "famous for her patience"
        r"renowned for ([^,\.]+)",  # "renowned for his courage"
        r"hides? in ([^,\.]+)",  # "hides in the shadows"
        r"lurks? in ([^,\.]+)",  # "lurks in dark corners"
        r"smiles? when ([^,\.]+)",  # "smiles when she kills"
        r"laughs? when ([^,\.]+)",  # "laughs when others cry"
    ]
    
    for pattern in trait_patterns:
        match = re.search(pattern, text_lower)
        if match:
            trait = match.group(1).strip()
            if trait and len(trait) > 2:
                traits.append(trait.title())
    
    # Also look for standalone trait words
    trait_keywords = [
        "angry", "cautious", "brave", "cowardly", "mysterious", "outgoing",
        "quiet", "loud", "patient", "impatient", "kind", "cruel", "gentle",
        "rough", "smooth", "wise", "foolish", "clever", "stupid", "strong",
        "weak", "fast", "slow", "loyal", "treacherous", "honest", "deceitful"
    ]
    
    for keyword in trait_keywords:
        if re.search(rf'\b{keyword}\b', text_lower):
            traits.append(keyword.title())
    
    # Remove duplicates while preserving order
    unique_traits = []
    for trait in traits:
        if trait not in unique_traits:
            unique_traits.append(trait)
    
    if unique_traits:
        logger.debug(f"✅ Traits detected: {unique_traits}")
    else:
        logger.debug(f"⚠️ No traits detected in text: '{text[:100]}...'")
    
    return unique_traits

def extract_motivations(text: str) -> List[str]:
    """
    Extract character motivations and driving forces from text.
    Returns a list of detected motivations.
    """
    if not text:
        return []
    text_lower = text.lower()
    logger.debug(f"🔍 Extracting motivations from text: '{text[:100]}...'")
    
    motivations = []
    
    # Motivation patterns
    motivation_patterns = [
        r"seeks? ([^,\.]+)",  # "seeks revenge", "seeks redemption"
        r"wants? to ([^,\.]+)",  # "wants to prove herself", "wants to find peace"
        r"desires? ([^,\.]+)",  # "desires power", "desires knowledge"
        r"longs? for ([^,\.]+)",  # "longs for home", "longs for adventure"
        r"hopes? to ([^,\.]+)",  # "hopes to find", "hopes to become"
        r"dreams? of ([^,\.]+)",  # "dreams of glory", "dreams of peace"
        r"yearns? for ([^,\.]+)",  # "yearns for freedom"
        r"craves? ([^,\.]+)",  # "craves power", "craves attention"
        r"driven by ([^,\.]+)",  # "driven by revenge", "driven by guilt"
        r"motivated by ([^,\.]+)",  # "motivated by loss", "motivated by love"
        r"because ([^,\.]+)",  # "because his family was killed"
        r"after ([^,\.]+)",  # "after the betrayal", "after losing everything"
        r"since ([^,\.]+)",  # "since the war", "since childhood"
    ]
    
    for pattern in motivation_patterns:
        match = re.search(pattern, text_lower)
        if match:
            motivation = match.group(1).strip()
            if motivation and len(motivation) > 2:
                motivations.append(motivation.title())
    
    # Also use the existing emotional themes extraction
    emotional_themes = extract_emotional_themes(text)
    motivations.extend(emotional_themes)
    
    # Remove duplicates while preserving order
    unique_motivations = []
    for motivation in motivations:
        if motivation not in unique_motivations:
            unique_motivations.append(motivation)
    
    if unique_motivations:
        logger.debug(f"✅ Motivations detected: {unique_motivations}")
    else:
        logger.debug(f"⚠️ No motivations detected in text: '{text[:100]}...'")
    
    return unique_motivations

def extract_alignment_from_text(text: str) -> Optional[str]:
    """
    Extract alignment from text.
    Handles responses like "good", "neutral", "chaotic", "lawful", etc.
    """
    if not text:
        return None
    text_lower = text.lower().strip()
    logger.debug(f"🔍 Extracting alignment from text: '{text[:100]}...'")
    
    # Alignment mapping
    alignment_map = {
        "good": "Good",
        "neutral": "Neutral", 
        "evil": "Evil",
        "lawful": "Lawful",
        "chaotic": "Chaotic",
        "lawful good": "Lawful Good",
        "neutral good": "Neutral Good",
        "chaotic good": "Chaotic Good",
        "lawful neutral": "Lawful Neutral",
        "true neutral": "True Neutral",
        "chaotic neutral": "Chaotic Neutral",
        "lawful evil": "Lawful Evil",
        "neutral evil": "Neutral Evil",
        "chaotic evil": "Chaotic Evil"
    }
    
    # Check for exact matches
    for alignment_key, alignment_value in alignment_map.items():
        if text_lower == alignment_key:
            logger.debug(f"✅ Alignment detected: {alignment_value}")
            return alignment_value
    
    # Check for partial matches
    for alignment_key, alignment_value in alignment_map.items():
        if alignment_key in text_lower:
            logger.debug(f"✅ Alignment detected (partial): {alignment_value}")
            return alignment_value
    
    logger.debug(f"⚠️ No alignment detected in text: '{text[:100]}...'")
    return None 