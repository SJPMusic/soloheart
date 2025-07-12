#!/usr/bin/env python3
"""
DnD SRD 5.2 Ability Score System for SoloHeart

This module provides a complete ability score system that follows the official DnD SRD 5.2 rules.
It supports standard array, point buy, manual assignment, and automatic assignment based on character story.
"""

import random
import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

logger = logging.getLogger(__name__)

class AbilityScoreMethod(Enum):
    """Methods for determining ability scores."""
    STANDARD_ARRAY = "standard_array"
    POINT_BUY = "point_buy"
    MANUAL = "manual"
    AUTO = "auto"
    ROLL_4D6_DROP_LOWEST = "roll_4d6_drop_lowest"

class AbilityScoreSystem:
    """Complete ability score system following DnD SRD 5.2 rules."""
    
    def __init__(self):
        # SRD 5.2 Standard Array
        self.standard_array = [15, 14, 13, 12, 10, 8]
        
        # Point Buy costs (SRD 5.2)
        self.point_buy_costs = {
            8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9
        }
        
        # Point Buy limits
        self.point_buy_min = 8
        self.point_buy_max = 15
        self.point_buy_total = 27
        
        # Ability score names
        self.abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        self.ability_abbreviations = {
            'strength': 'STR',
            'dexterity': 'DEX', 
            'constitution': 'CON',
            'intelligence': 'INT',
            'wisdom': 'WIS',
            'charisma': 'CHA'
        }
        
        # Class primary abilities (SRD 5.2)
        self.class_primary_abilities = {
            'barbarian': ['strength', 'constitution'],
            'fighter': ['strength', 'constitution'],
            'paladin': ['strength', 'charisma'],
            'ranger': ['dexterity', 'wisdom'],
            'rogue': ['dexterity', 'intelligence'],
            'monk': ['dexterity', 'wisdom'],
            'cleric': ['wisdom', 'charisma'],
            'druid': ['wisdom', 'constitution'],
            'wizard': ['intelligence', 'constitution'],
            'sorcerer': ['charisma', 'constitution'],
            'warlock': ['charisma', 'constitution'],
            'bard': ['charisma', 'dexterity']
        }
    
    def assign_standard_array(self, character_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Assign ability scores using the SRD 5.2 standard array.
        
        Args:
            character_data: Character data including class and personality
            
        Returns:
            Dict with ability scores
        """
        char_class = (character_data.get('class') or '')
        logger.debug(f">>> DEBUG: calling .lower() on char_class in assign_standard_array, value={char_class!r}, type={type(char_class)}")
        char_class = char_class.lower()
        personality_traits = character_data.get('personality_traits', [])
        
        # Get primary abilities for the class
        primary_abilities = self.class_primary_abilities.get(char_class, ['strength', 'constitution'])
        
        # Start with all scores at 10
        scores = {ability: 10 for ability in self.abilities}
        
        # Assign highest scores to primary abilities
        scores[primary_abilities[0]] = 15  # Primary ability
        scores[primary_abilities[1]] = 14  # Secondary ability
        
        # Distribute remaining scores based on personality
        remaining_scores = [13, 12, 10, 8]
        
        # Analyze personality for additional stat hints
        if any('wise' in trait.lower() or 'knowledge' in trait.lower() for trait in personality_traits):
            logger.debug(f">>> DEBUG: calling .lower() on trait in assign_standard_array (wise/knowledge), value={trait!r}, type={type(trait)}")
            if scores['intelligence'] == 10:
                scores['intelligence'] = remaining_scores.pop(0)
        
        if any('charismatic' in trait.lower() or 'leader' in trait.lower() for trait in personality_traits):
            logger.debug(f">>> DEBUG: calling .lower() on trait in assign_standard_array (charismatic/leader), value={trait!r}, type={type(trait)}")
            if scores['charisma'] == 10:
                scores['charisma'] = remaining_scores.pop(0)
        
        if any('agile' in trait.lower() or 'quick' in trait.lower() for trait in personality_traits):
            logger.debug(f">>> DEBUG: calling .lower() on trait in assign_standard_array (agile/quick), value={trait!r}, type={type(trait)}")
            if scores['dexterity'] == 10:
                scores['dexterity'] = remaining_scores.pop(0)
        
        # Fill remaining scores
        for ability in self.abilities:
            if scores[ability] == 10 and remaining_scores:
                scores[ability] = remaining_scores.pop(0)
        
        logger.info(f"🎲 Standard array assigned: {scores}")
        return scores
    
    def assign_point_buy(self, character_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Assign ability scores using SRD 5.2 point buy system.
        
        Args:
            character_data: Character data including class and personality
            
        Returns:
            Dict with ability scores
        """
        char_class = (character_data.get('class') or '')
        logger.debug(f">>> DEBUG: calling .lower() on char_class in assign_point_buy, value={char_class!r}, type={type(char_class)}")
        char_class = char_class.lower()
        primary_abilities = self.class_primary_abilities.get(char_class, ['strength', 'constitution'])
        
        # Start with minimum scores
        scores = {ability: 8 for ability in self.abilities}
        points_used = 0
        
        # Assign primary abilities first
        scores[primary_abilities[0]] = 15  # 9 points
        scores[primary_abilities[1]] = 14  # 7 points
        points_used += 16
        
        # Distribute remaining points (27 - 16 = 11 points)
        remaining_points = 11
        
        # Assign decent scores to other abilities
        for ability in self.abilities:
            if ability not in primary_abilities and remaining_points >= 4:
                scores[ability] = 12  # 4 points
                remaining_points -= 4
            elif ability not in primary_abilities and remaining_points >= 2:
                scores[ability] = 10  # 2 points
                remaining_points -= 2
        
        logger.info(f"🎲 Point buy assigned: {scores} (points used: {27 - remaining_points})")
        return scores
    
    def roll_4d6_drop_lowest(self) -> List[int]:
        """
        Roll 4d6, drop the lowest die (SRD 5.2 method).
        
        Returns:
            List of 6 ability scores
        """
        scores = []
        for _ in range(6):
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.sort()
            scores.append(sum(rolls[1:]))  # Drop lowest
        
        logger.info(f"🎲 4d6 drop lowest rolls: {scores}")
        return scores
    
    def assign_rolled_scores(self, character_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Assign ability scores using 4d6 drop lowest method.
        
        Args:
            character_data: Character data including class
            
        Returns:
            Dict with ability scores
        """
        char_class = (character_data.get('class') or '')
        logger.debug(f">>> DEBUG: calling .lower() on char_class in assign_rolled_scores, value={char_class!r}, type={type(char_class)}")
        char_class = char_class.lower()
        primary_abilities = self.class_primary_abilities.get(char_class, ['strength', 'constitution'])
        
        # Roll the scores
        rolled_scores = self.roll_4d6_drop_lowest()
        rolled_scores.sort(reverse=True)  # Highest first
        
        # Assign scores
        scores = {}
        scores[primary_abilities[0]] = rolled_scores[0]  # Highest to primary
        scores[primary_abilities[1]] = rolled_scores[1]  # Second highest to secondary
        
        # Distribute remaining scores
        remaining_scores = rolled_scores[2:]
        for ability in self.abilities:
            if ability not in scores and remaining_scores:
                scores[ability] = remaining_scores.pop(0)
        
        logger.info(f"🎲 Rolled scores assigned: {scores}")
        return scores
    
    def assign_auto_based_on_story(self, character_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Assign ability scores automatically based on character story and personality.
        
        Args:
            character_data: Character data including story and personality
            
        Returns:
            Dict with ability scores
        """
        # Use standard array as base
        base_scores = self.assign_standard_array(character_data)
        
        # Analyze character story for additional adjustments
        story = character_data.get('backstory', '')
        personality_traits = character_data.get('personality_traits', [])
        
        # Story-based adjustments
        if 'strong' in story.lower() or 'mighty' in story.lower():
            base_scores['strength'] = min(18, base_scores['strength'] + 1)
        
        if 'quick' in story.lower() or 'agile' in story.lower():
            base_scores['dexterity'] = min(18, base_scores['dexterity'] + 1)
        
        if 'wise' in story.lower() or 'knowledge' in story.lower():
            base_scores['intelligence'] = min(18, base_scores['intelligence'] + 1)
        
        if 'charismatic' in story.lower() or 'leader' in story.lower():
            base_scores['charisma'] = min(18, base_scores['charisma'] + 1)
        
        # Personality-based adjustments
        for trait in personality_traits:
            trait_lower = trait.lower()
            if 'brave' in trait_lower or 'courageous' in trait_lower:
                base_scores['constitution'] = min(18, base_scores['constitution'] + 1)
            elif 'clever' in trait_lower or 'intelligent' in trait_lower:
                base_scores['intelligence'] = min(18, base_scores['intelligence'] + 1)
            elif 'perceptive' in trait_lower or 'wise' in trait_lower:
                base_scores['wisdom'] = min(18, base_scores['wisdom'] + 1)
        
        logger.info(f"🎲 Story-based auto-assignment: {base_scores}")
        return base_scores
    
    def calculate_modifiers(self, scores: Dict[str, int]) -> Dict[str, int]:
        """
        Calculate ability modifiers from scores.
        
        Args:
            scores: Ability scores
            
        Returns:
            Dict with ability modifiers
        """
        modifiers = {}
        for ability, score in scores.items():
            modifiers[ability] = (score - 10) // 2
        
        return modifiers
    
    def validate_scores(self, scores: Dict[str, int], method: AbilityScoreMethod) -> Tuple[bool, str]:
        """
        Validate ability scores based on the assignment method.
        
        Args:
            scores: Ability scores to validate
            method: Assignment method used
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for required abilities
        required_abilities = set(self.abilities)
        provided_abilities = set(scores.keys())
        
        if required_abilities != provided_abilities:
            missing = required_abilities - provided_abilities
            extra = provided_abilities - required_abilities
            return False, f"Missing abilities: {missing}. Extra abilities: {extra}"
        
        # Check score ranges
        for ability, score in scores.items():
            if not isinstance(score, int):
                return False, f"Score for {ability} must be an integer"
            if score < 1 or score > 20:
                return False, f"Score for {ability} must be between 1 and 20"
        
        # Method-specific validation
        if method == AbilityScoreMethod.STANDARD_ARRAY:
            return self._validate_standard_array(scores)
        elif method == AbilityScoreMethod.POINT_BUY:
            return self._validate_point_buy(scores)
        elif method == AbilityScoreMethod.ROLL_4D6_DROP_LOWEST:
            return self._validate_rolled_scores(scores)
        elif method == AbilityScoreMethod.MANUAL:
            return True, "Scores are valid"
        else:
            return True, "Scores are valid"
    
    def _validate_standard_array(self, scores: Dict[str, int]) -> Tuple[bool, str]:
        """Validate scores match standard array."""
        score_values = list(scores.values())
        score_values.sort(reverse=True)
        
        if score_values != self.standard_array:
            return False, f"Scores must match standard array: {self.standard_array}"
        
        return True, "Scores match standard array"
    
    def _validate_point_buy(self, scores: Dict[str, int]) -> Tuple[bool, str]:
        """Validate scores fit within point buy system."""
        total_cost = 0
        
        for score in scores.values():
            if score < 8 or score > 15:
                return False, f"Point buy scores must be between 8 and 15"
            
            cost = self.point_buy_costs.get(score, 0)
            total_cost += cost
        
        if total_cost > self.point_buy_total:
            return False, f"Point buy cost ({total_cost}) exceeds limit ({self.point_buy_total})"
        
        return True, f"Point buy cost: {total_cost}/{self.point_buy_total}"
    
    def _validate_rolled_scores(self, scores: Dict[str, int]) -> Tuple[bool, str]:
        """Validate scores could have been rolled."""
        for score in scores.values():
            if score < 3 or score > 18:
                return False, f"Rolled scores must be between 3 and 18"
        
        return True, "Scores are valid for rolled method"
    
    def get_score_description(self, score: int) -> str:
        """
        Get a description of an ability score.
        
        Args:
            score: Ability score
            
        Returns:
            Description of the score
        """
        if score <= 1:
            return "Abysmal"
        elif score <= 3:
            return "Very Poor"
        elif score <= 5:
            return "Poor"
        elif score <= 7:
            return "Below Average"
        elif score <= 9:
            return "Below Average"
        elif score <= 11:
            return "Average"
        elif score <= 13:
            return "Above Average"
        elif score <= 15:
            return "Good"
        elif score <= 17:
            return "Very Good"
        elif score <= 19:
            return "Exceptional"
        else:
            return "Legendary"
    
    def get_ability_description(self, ability: str) -> str:
        """
        Get a description of what an ability represents.
        
        Args:
            ability: Ability name
            
        Returns:
            Description of the ability
        """
        descriptions = {
            'strength': 'Physical power, athletic training, and the extent to which you can exert raw physical force',
            'dexterity': 'Agility, reflexes, balance, and your skill at stealth',
            'constitution': 'Health, stamina, and vital force',
            'intelligence': 'Mental acuity, accuracy of recall, and the ability to reason',
            'wisdom': 'Awareness of the world around you and the sensitivity of your senses',
            'charisma': 'Your ability to interact effectively with others'
        }
        
        return descriptions.get(ability.lower(), 'Unknown ability')
    
    def get_class_recommendations(self, char_class: str) -> Dict[str, str]:
        """
        Get ability score recommendations for a class.
        
        Args:
            char_class: Character class
            
        Returns:
            Dict with ability recommendations
        """
        char_class = char_class.lower()
        primary_abilities = self.class_primary_abilities.get(char_class, ['strength', 'constitution'])
        
        recommendations = {}
        for ability in self.abilities:
            if ability in primary_abilities:
                recommendations[ability] = "Primary - Should be your highest score"
            else:
                recommendations[ability] = "Secondary - Useful but not essential"
        
        return recommendations
    
    def apply_racial_modifiers(self, base_scores: Dict[str, int], race: str, subrace: str = None) -> Dict[str, int]:
        """
        Apply racial modifiers to base ability scores.
        
        Args:
            base_scores: Base ability scores
            race: Character race
            subrace: Character subrace (optional)
            
        Returns:
            Modified ability scores with racial bonuses applied
        """
        try:
            from .racial_modifiers import racial_modifiers
            return racial_modifiers.apply_racial_modifiers(base_scores, race, subrace)
        except ImportError:
            logger.warning("Racial modifiers module not available, returning base scores")
            return base_scores
    
    def get_racial_summary(self, race: str, subrace: str = None) -> str:
        """
        Get a formatted summary of racial traits and bonuses.
        
        Args:
            race: Character race
            subrace: Character subrace (optional)
            
        Returns:
            Formatted racial summary
        """
        try:
            from .racial_modifiers import racial_modifiers
            return racial_modifiers.format_racial_summary(race, subrace)
        except ImportError:
            return f"Race: {race}" + (f" ({subrace})" if subrace else "")

# Global ability score system instance
ability_score_system = AbilityScoreSystem() 