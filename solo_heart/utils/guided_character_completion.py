#!/usr/bin/env python3
"""
Guided Character Completion System for SoloHeart

This module provides a guided character completion system that helps players
fill in missing character details through natural conversation and targeted questions.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from utils.ability_score_system import AbilityScoreSystem, AbilityScoreMethod

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
    ROLL_4D6_DROP_LOWEST = "roll_4d6_drop_lowest"

class GuidedCharacterCompletion:
    """Guided character completion system that helps players fill in missing details."""
    
    def __init__(self):
        self.guided_questions_asked = 0
        self.max_guided_questions = 3  # Keep it minimal
        self.stat_assignment_mode = StatAssignmentMode.AUTO
        self.ability_score_system = AbilityScoreSystem()
        
        # Track what we've already asked about
        self.asked_about = set()
    
    def should_transition_to_guided(self, user_input: str, extracted_facts: Dict[str, Any], 
                                  character_data: Dict[str, Any]) -> bool:
        """
        Determine if we should transition to guided questions.
        Only do this if the user seems stuck or confused.
        """
        # Don't transition if user is actively providing information
        if len(extracted_facts) > 0:
            return False
        
        # Don't transition if we've already asked too many questions
        if self.guided_questions_asked >= self.max_guided_questions:
            return False
        
        # Only transition if user seems confused or asks for help
        confusion_indicators = [
            "help", "confused", "don't know", "what do you mean", "how do i",
            "what should i", "i'm not sure", "what next", "??", "?"
        ]
        
        user_input_lower = user_input
        logger.debug(f">>> DEBUG: calling .lower() on user_input in should_transition_to_guided, value={user_input!r}, type={type(user_input)}")
        user_input_lower = user_input_lower.lower()
        return any(indicator in user_input_lower for indicator in confusion_indicators)
    
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
        """Get missing fields in priority order. Only ask for essential information."""
        missing = []
        
        # Only ask for the most essential fields - name and race
        if not character_data.get('name') or character_data['name'] in [None, "Unknown", ""]:
            missing.append('name')
        
        if not character_data.get('race') or character_data['race'] in [None, "Unknown", ""]:
            missing.append('race')
        
        # Only ask for class if we have name and race, and only if it's completely missing
        has_basic_info = (character_data.get('name') and character_data.get('race'))
        if (not character_data.get('class') or character_data['class'] in [None, "Unknown", ""]) and has_basic_info:
            missing.append('class')
        
        # Only ask for age if we have the basic info and it's completely missing
        if has_basic_info and (not character_data.get('age') or character_data['age'] in [None, "Unknown", 0]):
            missing.append('age')
        
        # Don't ask for other fields - let the user provide them naturally through conversation
        # The system can work with just name, race, class, and age
        
        return missing
    
    def _format_question(self, field: str, character_data: Dict[str, Any]) -> str:
        """Format a user-friendly question for the given field."""
        char_name = character_data.get('name', 'your character')
        if not char_name or char_name == "Unknown":
            char_name = "your character"
        
        # More natural, conversational questions that encourage storytelling
        questions = {
            'name': f"What is your character's name?",
            'race': f"I'm curious about {char_name}'s heritage. What kind of being are they?",
            'class': f"What does {char_name} do when trouble comes? How do they handle themselves?",
            'background': f"What was {char_name}'s life like before all this? What did they do?",
            'alignment': f"How does {char_name} see the world? What guides their choices?",
            'age': f"How old is {char_name}?",
            'gender': f"What gender is {char_name}?",
            'personality_traits': f"What kind of person is {char_name}? How would others describe them?",
            'motivations': f"What keeps {char_name} going? What matters most to them?"
        }
        
        return questions.get(field, f"Tell me more about {char_name}.")
    
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
                "I'll make sure they follow the official DnD SRD 5.2 rules.")
    
    def assign_stats_automatically(self, character_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Automatically assign ability scores based on character story and class.
        Uses the new ability score system.
        """
        return self.ability_score_system.assign_auto_based_on_story(character_data)
    
    def assign_standard_array(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically assign the standard array to ability scores.
        Uses SRD 5.2 standard array.
        """
        scores = self.ability_score_system.assign_standard_array(character_data)
        modifiers = self.ability_score_system.calculate_modifiers(scores)
        
        return {
            'scores': scores,
            'modifiers': modifiers,
            'method': AbilityScoreMethod.STANDARD_ARRAY
        }
    
    def assign_point_buy(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assign ability scores using point buy system.
        Uses SRD 5.2 point buy rules.
        """
        scores = self.ability_score_system.assign_point_buy(character_data)
        modifiers = self.ability_score_system.calculate_modifiers(scores)
        
        return {
            'scores': scores,
            'modifiers': modifiers,
            'method': AbilityScoreMethod.POINT_BUY
        }
    
    def assign_rolled_scores(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assign ability scores using 4d6 drop lowest method.
        Uses SRD 5.2 rolling method.
        """
        scores = self.ability_score_system.assign_rolled_scores(character_data)
        modifiers = self.ability_score_system.calculate_modifiers(scores)
        
        return {
            'scores': scores,
            'modifiers': modifiers,
            'method': AbilityScoreMethod.ROLL_4D6_DROP_LOWEST
        }
    
    def validate_manual_stats(self, stats: Dict[str, int]) -> Tuple[bool, str]:
        """
        Validate manually entered ability scores against SRD 5.2 rules.
        Returns (is_valid, error_message).
        """
        return self.ability_score_system.validate_scores(stats, AbilityScoreMethod.MANUAL)
    
    def get_ability_score_summary(self, scores: Dict[str, int]) -> str:
        """
        Get a formatted summary of ability scores with modifiers.
        
        Args:
            scores: Ability scores
            
        Returns:
            Formatted summary string
        """
        modifiers = self.ability_score_system.calculate_modifiers(scores)
        
        summary = "**Ability Scores:**\n"
        for ability in self.ability_score_system.abilities:
            ability_str = (ability or '')
            logger.debug(f">>> DEBUG: calling .title() on ability in get_ability_score_summary, value={ability_str!r}, type={type(ability_str)}")
            ability_display = ability_str.title() if ability_str else 'Unknown'
            score = scores[ability]
            modifier = modifiers[ability]
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            description = self.ability_score_system.get_score_description(score)
            
            summary += f"• **{ability_display}**: {score} ({modifier_str}) - {description}\n"
        
        return summary
    
    def get_class_recommendations(self, char_class: str) -> str:
        """
        Get ability score recommendations for a class.
        
        Args:
            char_class: Character class
            
        Returns:
            Formatted recommendations string
        """
        # Defensive patch for .title() and .lower()
        char_class_str = (char_class or '')
        logger.debug(f">>> DEBUG: calling .title() on char_class in get_class_recommendations, value={char_class_str!r}, type={type(char_class_str)}")
        recommendations = self.ability_score_system.get_class_recommendations(char_class_str)
        
        # Safely format class name
        class_display = 'Unknown'
        if char_class_str:
            class_display = char_class_str.title()
        
        summary = f"**Ability Score Recommendations for {class_display}:**\n"
        for ability, recommendation in recommendations.items():
            ability_title = (ability or '')
            logger.debug(f">>> DEBUG: calling .title() on ability in get_class_recommendations, value={ability_title!r}, type={type(ability_title)}")
            ability_display = ability_title.title() if ability_title else 'Unknown'
            summary += f"• **{ability_display}**: {recommendation}\n"
        return summary
    
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
        
        # Add ability scores if available
        ability_scores = character_data.get('ability_scores', {})
        if ability_scores:
            summary += "\n" + self.get_ability_score_summary(ability_scores)
        
        summary += "\nReady to start your adventure?"
        return summary 