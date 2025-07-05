#!/usr/bin/env python3
"""
Guided Character Completion System

This module handles the transition from open-ended creative input to structured
character sheet completion, providing a smooth experience for players who may
not be familiar with D&D 5E mechanics.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class CompletionPhase(Enum):
    """Phases of character completion."""
    CREATIVE_INPUT = "creative_input"
    GUIDED_QUESTIONS = "guided_questions"
    STAT_ASSIGNMENT = "stat_assignment"
    FINALIZATION = "finalization"

class StatAssignmentMode(Enum):
    """Modes for ability score assignment."""
    AUTO = "auto"
    MANUAL = "manual"
    STANDARD_ARRAY = "standard_array"
    POINT_BUY = "point_buy"

class GuidedCharacterCompletion:
    """
    Manages the transition from creative character input to guided character sheet completion.
    """
    
    def __init__(self):
        self.phase = CompletionPhase.CREATIVE_INPUT
        self.creative_phase_complete = False
        self.stat_assignment_mode = StatAssignmentMode.AUTO
        self.consecutive_low_confidence = 0
        self.guided_questions_asked = 0
        self.max_guided_questions = 10
        
        # SRD 5.1 compliant options
        self.races = ["Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome", "Half-Elf", "Half-Orc", "Tiefling"]
        self.classes = ["Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"]
        self.backgrounds = ["Acolyte", "Criminal", "Folk Hero", "Noble", "Sage", "Soldier"]
        
        # Standard array for automatic assignment
        self.standard_array = [15, 14, 13, 12, 10, 8]
        
    def should_transition_to_guided(self, user_input: str, extracted_facts: Dict[str, Any], 
                                  character_data: Dict[str, Any]) -> bool:
        """
        Determine if we should transition from creative input to guided questions.
        Much less aggressive - only transition if we have very few facts or explicit completion request.
        """
        # Check for explicit completion phrases
        completion_phrases = [
            "i'm done", "that's all", "that's my character", "that's everything",
            "i'm finished", "that's it", "complete", "finish", "ready to start",
            "let's begin", "start the game", "what else do i need", "help me finish",
            "fill in the rest", "complete my character"
        ]
        
        if any(phrase in user_input.lower() for phrase in completion_phrases):
            logger.info("🎯 Transition triggered: explicit completion request")
            return True
        
        # Count how many core facts we have - check both extracted_facts and character_data
        core_facts = ["name", "race", "class", "background", "age", "gender"]
        context_facts = ["personality_traits", "traits", "motivations", "emotional_themes", "gear", "combat_style"]
        
        # Check extracted_facts first, then character_data
        core_count = 0
        context_count = 0
        
        for fact in core_facts:
            if (fact in extracted_facts and extracted_facts[fact]) or \
               (fact in character_data and character_data[fact] and character_data[fact] not in [None, "Unknown", ""]):
                core_count += 1
        
        for fact in context_facts:
            if (fact in extracted_facts and extracted_facts[fact]) or \
               (fact in character_data and character_data[fact] and character_data[fact] not in [None, "Unknown", "", []]):
                context_count += 1
        
        # Only transition if we have very few facts (less than 2 core facts)
        if core_count < 2:
            logger.info(f"🎯 Transition triggered: only {core_count} core facts extracted")
            return True
        
        # If we have good facts, don't transition - let the user continue naturally
        logger.info(f"✅ Continuing natural input: {core_count} core facts, {context_count} context facts")
        return False
    
    def get_transition_message(self) -> str:
        """Get the message to show when transitioning to guided questions."""
        return ("Thanks for sharing your character! Now I'll help you fill in the rest of their character sheet step by step. "
                "You can always take over if you'd like to assign things manually.")
    
    def get_next_guided_question(self, character_data: Dict[str, Any]) -> Optional[str]:
        """
        Get the next guided question based on what's missing from the character sheet.
        Returns None if no more questions are needed.
        """
        if self.guided_questions_asked >= self.max_guided_questions:
            return None
        
        # Priority order for questions
        missing_fields = self._get_missing_fields(character_data)
        
        if not missing_fields:
            return None
        
        # Get the highest priority missing field
        next_field = missing_fields[0]
        self.guided_questions_asked += 1
        
        return self._format_question(next_field, character_data)
    
    def _get_missing_fields(self, character_data: Dict[str, Any]) -> List[str]:
        """Get missing fields in priority order."""
        missing = []
        
        # High priority fields
        if not character_data.get('race') or character_data['race'] in [None, "Unknown", ""]:
            missing.append('race')
        if not character_data.get('class') or character_data['class'] in [None, "Unknown", ""]:
            missing.append('class')
        if not character_data.get('background') or character_data['background'] in [None, "Unknown", ""]:
            missing.append('background')
        
        # Medium priority fields
        if not character_data.get('alignment') or character_data['alignment'] in [None, "Unknown", ""]:
            missing.append('alignment')
        if not character_data.get('age') or character_data['age'] in [None, "Unknown", 0]:
            missing.append('age')
        if not character_data.get('gender') or character_data['gender'] in [None, "Unknown", ""]:
            missing.append('gender')
        
        # Lower priority fields - check both personality_traits and traits
        if (not character_data.get('personality_traits') or character_data['personality_traits'] == []) and \
           (not character_data.get('traits') or character_data['traits'] == []):
            missing.append('personality_traits')
        if not character_data.get('motivations') or character_data['motivations'] == []:
            missing.append('motivations')
        
        return missing
    
    def _format_question(self, field: str, character_data: Dict[str, Any]) -> str:
        """Format a user-friendly question for the given field."""
        char_name = character_data.get('name', 'your character')
        if not char_name or char_name == "Unknown":
            char_name = "your character"
        
        questions = {
            'race': f"What kind of being is {char_name}? Are they human, elf, dwarf, or something else?",
            'class': f"What kind of person is {char_name}—do they sneak around, cast spells, or fight up close?",
            'background': f"What was {char_name}'s life like before becoming an adventurer? Were they a soldier, scholar, criminal, or something else?",
            'alignment': f"How does {char_name} typically behave? Are they generally good, neutral, or do they follow their own rules?",
            'age': f"How old is {char_name}?",
            'gender': f"What gender is {char_name}?",
            'personality_traits': f"What are some personality traits that describe {char_name}?",
            'motivations': f"What drives {char_name}? What do they want most?"
        }
        
        return questions.get(field, f"Tell me about {char_name}'s {field}.")
    
    def should_start_stat_assignment(self, character_data: Dict[str, Any]) -> bool:
        """Determine if we should start ability score assignment."""
        # Check if we have the basic character info needed for stat assignment
        required_fields = ['race', 'class']
        has_required = all(character_data.get(field) and character_data[field] not in [None, "Unknown", ""] 
                          for field in required_fields)
        
        # Check if stats haven't been assigned yet
        ability_scores = character_data.get('ability_scores', {})
        stats_assigned = all(score > 0 for score in ability_scores.values()) if ability_scores else False
        
        return has_required and not stats_assigned
    
    def get_stat_assignment_prompt(self) -> str:
        """Get the prompt for ability score assignment."""
        return ("Want me to assign ability scores based on what you told me about your character's story and personality? "
                "I'll make sure they follow the official rules.")
    
    def assign_stats_automatically(self, character_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Automatically assign ability scores based on character story and class.
        Uses SRD 5.1 standard array.
        """
        char_class = character_data.get('class', '').lower()
        personality_traits = character_data.get('personality_traits', [])
        motivations = character_data.get('motivations', [])
        
        # Determine primary and secondary abilities based on class
        if char_class in ['fighter', 'barbarian', 'paladin']:
            primary = 'strength'
            secondary = 'constitution'
        elif char_class in ['rogue', 'ranger', 'monk']:
            primary = 'dexterity'
            secondary = 'constitution'
        elif char_class in ['wizard', 'sorcerer']:
            primary = 'intelligence' if char_class == 'wizard' else 'charisma'
            secondary = 'constitution'
        elif char_class in ['cleric', 'druid']:
            primary = 'wisdom'
            secondary = 'constitution'
        elif char_class in ['bard', 'warlock']:
            primary = 'charisma'
            secondary = 'constitution'
        else:
            # Default to balanced scores
            primary = 'strength'
            secondary = 'dexterity'
        
        # Assign scores using standard array
        scores = {
            'strength': 10,
            'dexterity': 10,
            'constitution': 10,
            'intelligence': 10,
            'wisdom': 10,
            'charisma': 10
        }
        
        # Assign highest scores to primary abilities
        scores[primary] = 15
        scores[secondary] = 14
        
        # Distribute remaining scores based on character traits
        remaining_scores = [13, 12, 10, 8]
        
        # Analyze personality for additional stat hints
        if any('wise' in trait.lower() or 'knowledge' in trait.lower() for trait in personality_traits):
            scores['intelligence'] = remaining_scores.pop(0)
        if any('charismatic' in trait.lower() or 'leader' in trait.lower() for trait in personality_traits):
            scores['charisma'] = remaining_scores.pop(0)
        if any('agile' in trait.lower() or 'quick' in trait.lower() for trait in personality_traits):
            scores['dexterity'] = remaining_scores.pop(0)
        
        # Fill remaining scores
        for ability in ['strength', 'dexterity', 'intelligence', 'wisdom', 'charisma']:
            if scores[ability] == 10 and remaining_scores:
                scores[ability] = remaining_scores.pop(0)
        
        # Ensure constitution gets a decent score if not already assigned
        if scores['constitution'] == 10 and remaining_scores:
            scores['constitution'] = remaining_scores.pop(0)
        
        logger.info(f"🎲 Auto-assigned stats: {scores}")
        return scores
    
    def validate_manual_stats(self, stats: Dict[str, int]) -> Tuple[bool, str]:
        """
        Validate manually entered ability scores against SRD 5.1 rules.
        Returns (is_valid, error_message).
        """
        # Check that all scores are present
        required_abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        for ability in required_abilities:
            if ability not in stats:
                return False, f"Missing {ability} score"
            if not isinstance(stats[ability], int):
                return False, f"{ability} must be a number"
            if stats[ability] < 3 or stats[ability] > 18:
                return False, f"{ability} must be between 3 and 18"
        
        # Check if scores match standard array (simplified validation)
        score_values = list(stats.values())
        score_values.sort(reverse=True)
        
        if score_values == [15, 14, 13, 12, 10, 8]:
            return True, "Valid standard array"
        
        # For now, accept any valid scores (could add point-buy validation later)
        return True, "Valid ability scores"
    
    def get_confusion_response(self) -> str:
        """Get a response when the player seems confused."""
        return ("No worries—if stats or rules feel too complicated, I'll handle them for you. "
                "Just tell me anything else you want to add about your character, and I'll take care of the rest.")
    
    def get_completion_summary(self, character_data: Dict[str, Any]) -> str:
        """Get a summary of the completed character."""
        name = character_data.get('name', 'Your character')
        race = character_data.get('race', 'Unknown')
        char_class = character_data.get('class', 'Unknown')
        background = character_data.get('background', 'Unknown')
        
        summary = f"Perfect! Here's {name}:\n\n"
        summary += f"**{name}** - {race} {char_class} ({background})\n\n"
        
        # Add key details
        if character_data.get('age'):
            summary += f"Age: {character_data['age']}\n"
        if character_data.get('alignment'):
            summary += f"Alignment: {character_data['alignment']}\n"
        if character_data.get('personality_traits'):
            summary += f"Personality: {', '.join(character_data['personality_traits'])}\n"
        if character_data.get('motivations'):
            summary += f"Motivations: {', '.join(character_data['motivations'])}\n"
        
        summary += "\nReady to start your adventure?"
        return summary 