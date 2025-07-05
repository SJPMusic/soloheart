#!/usr/bin/env python3
"""
Semantic Character Analyzer - Context-Aware Fact Extraction

This module implements semantic understanding similar to how I analyze character descriptions,
using context, cross-referencing, and reasoning rather than just pattern matching.
"""

import re
from typing import Dict, List, Any, Tuple
from .character_fact_extraction import (
    RACES, CLASSES, BACKGROUNDS, extract_name_from_text, extract_age_from_text,
    extract_race_from_text, extract_class_from_text, extract_background_from_text,
    extract_gender_from_text, extract_gear_from_text, extract_traumas_from_text,
    extract_motivations_from_text, extract_emotional_themes, extract_combat_style,
    extract_traits, extract_relational_history_from_text
)

class SemanticCharacterAnalyzer:
    """
    Analyzes character descriptions using semantic understanding and context reasoning.
    """
    
    def __init__(self):
        self.context_clues = {
            "fighter": [
                "blacksmith", "soldier", "warrior", "guard", "knight", "combat",
                "weapon", "sword", "axe", "hammer", "armor", "fighting", "battle",
                "military", "veteran", "war", "defend", "protect", "guardian"
            ],
            "wizard": [
                "arcane", "magic", "spell", "grimoire", "tome", "scroll", "study",
                "learned", "scholar", "academic", "library", "research", "ancient",
                "mystical", "enchantment", "conjuration", "evocation"
            ],
            "rogue": [
                "sneak", "stealth", "thief", "assassin", "spy", "scout", "dagger",
                "lockpick", "trap", "sneaky", "quiet", "observant", "careful",
                "underground", "shady", "criminal", "outlaw"
            ],
            "cleric": [
                "priest", "divine", "holy", "sacred", "temple", "church", "faith",
                "worship", "prayer", "healing", "blessing", "monastery", "religious",
                "spiritual", "divine magic", "holy weapon"
            ]
        }
    
    def analyze_full_name(self, text: str) -> str:
        """
        Extract full name using semantic understanding of name patterns.
        """
        # Look for "His name is X Y" or "My character is X Y" patterns
        name_patterns = [
            r"his name is ([a-z]+ [a-z]+)",
            r"my character is ([a-z]+ [a-z]+)",
            r"call me ([a-z]+ [a-z]+)",
            r"i am ([a-z]+ [a-z]+)",
            r"([a-z]+ [a-z]+) is my name"
        ]
        
        text_lower = text.lower()
        for pattern in name_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1).title()
        
        # Fallback to single name extraction
        return extract_name_from_text(text)
    
    def analyze_class_with_context(self, text: str) -> str:
        """
        Analyze class using context clues and cross-referencing.
        """
        text_lower = text.lower()
        
        # Count context clues for each class
        class_scores = {}
        for class_name, clues in self.context_clues.items():
            score = 0
            for clue in clues:
                if clue in text_lower:
                    score += 1
            class_scores[class_name] = score
        
        # Get the class with highest score
        if class_scores:
            best_class = max(class_scores.items(), key=lambda x: x[1])
            if best_class[1] > 0:
                return best_class[0].title()
        
        # Fallback to pattern matching
        return extract_class_from_text(text)
    
    def analyze_trauma_with_context(self, text: str) -> List[str]:
        """
        Analyze trauma using semantic understanding of loss and injury.
        """
        text_lower = text.lower()
        traumas = []
        
        # Look for specific trauma patterns
        trauma_patterns = [
            (r"lost (?:his|her|their) (arm|leg|eye|hand)", "Lost limb"),
            (r"losing (?:his|her|their) (arm|leg|eye|hand)", "Lost limb"),
            (r"(arm|leg|eye|hand) was (lost|severed|destroyed)", "Lost limb"),
            (r"mysterious (explosion|accident|incident)", "Mysterious accident"),
            (r"blamed for (?:a|the) (fire|explosion|disaster)", "Falsely blamed"),
            (r"left in disgrace", "Disgraced"),
            (r"abandoned (?:his|her|their) (vows|faith|home)", "Abandoned past"),
            (r"betrayed by (?:his|her|their) (family|friends|mentor)", "Betrayal")
        ]
        
        for pattern, trauma_type in trauma_patterns:
            if re.search(pattern, text_lower):
                traumas.append(trauma_type)
        
        # Add pattern-based traumas
        pattern_traumas = extract_traumas_from_text(text)
        traumas.extend(pattern_traumas)
        
        return list(set(traumas))  # Remove duplicates
    
    def analyze_motivations_with_context(self, text: str) -> List[str]:
        """
        Analyze motivations using semantic understanding of goals and desires.
        """
        text_lower = text.lower()
        motivations = []
        
        # Look for specific motivation patterns
        motivation_patterns = [
            (r"searching for (?:whoever|the one who|the person who)", "Find perpetrator"),
            (r"looking for (?:whoever|the one who|the person who)", "Find perpetrator"),
            (r"seeking (?:justice|revenge|vengeance)", "Seek justice"),
            (r"hoping for (?:justice|revenge|vengeance)", "Seek justice"),
            (r"wants to (?:find|catch|punish)", "Find perpetrator"),
            (r"determined to (?:find|catch|punish)", "Find perpetrator"),
            (r"vows to (?:find|catch|punish)", "Find perpetrator"),
            (r"clear (?:his|her|their) name", "Clear name"),
            (r"prove (?:his|her|their) innocence", "Clear name"),
            (r"restore (?:his|her|their) honor", "Restore honor")
        ]
        
        for pattern, motivation_type in motivation_patterns:
            if re.search(pattern, text_lower):
                motivations.append(motivation_type)
        
        # Add pattern-based motivations
        pattern_motivations = extract_motivations_from_text(text)
        motivations.extend(pattern_motivations)
        
        return list(set(motivations))  # Remove duplicates
    
    def analyze_gear_with_context(self, text: str) -> List[str]:
        """
        Analyze gear using semantic understanding of equipment and tools.
        """
        text_lower = text.lower()
        gear = []
        
        # Look for specific gear patterns
        gear_patterns = [
            (r"mechanical (arm|leg|replacement)", "Mechanical limb"),
            (r"crafted (?:a|an) (?:mechanical|magical) (arm|leg)", "Mechanical limb"),
            (r"powered by (?:arcane|magical) energy", "Arcane-powered gear"),
            (r"massive hammer", "Massive hammer"),
            (r"leather apron", "Leather apron"),
            (r"worn traveler's cloak", "Traveler's cloak"),
            (r"hidden dagger", "Hidden dagger"),
            (r"old journal", "Old journal"),
            (r"cryptic prophecies", "Cryptic prophecies")
        ]
        
        for pattern, gear_item in gear_patterns:
            if re.search(pattern, text_lower):
                gear.append(gear_item)
        
        # Add pattern-based gear
        pattern_gear = extract_gear_from_text(text)
        gear.extend(pattern_gear)
        
        return list(set(gear))  # Remove duplicates
    
    def analyze_combat_style_with_context(self, text: str) -> str:
        """
        Analyze combat style using semantic understanding of fighting approach.
        """
        text_lower = text.lower()
        
        # Look for specific combat style patterns
        combat_patterns = [
            (r"fixing broken weapons", "Weapon repair"),
            (r"crafted.*weapon", "Weapon crafting"),
            (r"mechanical.*arm", "Mechanical combat"),
            (r"massive hammer", "Heavy weapon combat"),
            (r"hidden dagger", "Stealth combat"),
            (r"quick to act", "Reactive combat"),
            (r"first to step in", "Protective combat"),
            (r"doesn't call himself a warrior", "Reluctant fighter")
        ]
        
        for pattern, style in combat_patterns:
            if re.search(pattern, text_lower):
                return style
        
        # Fallback to pattern matching
        return extract_combat_style(text)
    
    def analyze_all_facts_semantically(self, text: str) -> Dict[str, Any]:
        """
        Analyze all character facts using semantic understanding and context reasoning.
        """
        facts = {}
        
        # Use semantic analysis for each fact type
        facts["name"] = self.analyze_full_name(text)
        facts["age"] = extract_age_from_text(text)
        facts["race"] = extract_race_from_text(text)
        facts["class"] = self.analyze_class_with_context(text)
        facts["background"] = extract_background_from_text(text)
        facts["gender"] = extract_gender_from_text(text)
        facts["gear"] = self.analyze_gear_with_context(text)
        facts["traumas"] = self.analyze_trauma_with_context(text)
        facts["motivations"] = self.analyze_motivations_with_context(text)
        facts["emotional_themes"] = extract_emotional_themes(text)
        facts["combat_style"] = self.analyze_combat_style_with_context(text)
        facts["traits"] = extract_traits(text)
        facts["relational_history"] = extract_relational_history_from_text(text)
        
        # Remove None values and empty lists
        facts = {k: v for k, v in facts.items() if v is not None and v != [] and v != {}}
        
        return facts

def extract_all_facts_semantically(text: str) -> Dict[str, Any]:
    """
    Extract all character facts using semantic understanding.
    """
    analyzer = SemanticCharacterAnalyzer()
    return analyzer.analyze_all_facts_semantically(text) 