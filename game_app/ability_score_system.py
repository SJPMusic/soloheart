#!/usr/bin/env python3
"""
D&D 5E Ability Score Assignment System for SoloHeart
Implements Standard Array, Point Buy, and Optimal Assignment methods.
"""

import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class AbilityScoreMethod(Enum):
    """Ability score assignment methods."""
    STANDARD_ARRAY = "standard_array"
    POINT_BUY = "point_buy"
    OPTIMAL_ASSIGNMENT = "optimal_assignment"

class AbilityScoreSystem:
    """Handles D&D 5E ability score assignment using SRD-compliant methods."""
    
    def __init__(self):
        # Standard Array values (SRD 5E)
        self.standard_array = [15, 14, 13, 12, 10, 8]
        
        # Point Buy costs (SRD 5E)
        self.point_buy_costs = {
            8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9
        }
        
        # Point Buy limits
        self.point_buy_min = 8
        self.point_buy_max = 15
        self.point_buy_total = 27
        
        # Ability score names
        self.abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        
        # Class primary abilities (SRD 5E)
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
        
        # Class secondary abilities
        self.class_secondary_abilities = {
            'barbarian': ['dexterity'],
            'fighter': ['dexterity'],
            'paladin': ['constitution'],
            'ranger': ['constitution'],
            'rogue': ['constitution'],
            'monk': ['constitution'],
            'cleric': ['constitution'],
            'druid': ['constitution'],
            'wizard': ['dexterity'],
            'sorcerer': ['constitution'],
            'warlock': ['constitution'],
            'bard': ['constitution']
        }
    
    def assign_ability_scores(self, method: AbilityScoreMethod, 
                            character_class: str = None,
                            race: str = None) -> Dict[str, int]:
        """
        Assign ability scores using the specified method.
        
        Args:
            method: Assignment method to use
            character_class: Character class for optimal assignment
            race: Character race for racial bonuses
            
        Returns:
            Dictionary of ability scores
        """
        if method == AbilityScoreMethod.STANDARD_ARRAY:
            return self._assign_standard_array(character_class, race)
        elif method == AbilityScoreMethod.POINT_BUY:
            return self._assign_point_buy(character_class, race)
        elif method == AbilityScoreMethod.OPTIMAL_ASSIGNMENT:
            return self._assign_optimal(character_class, race)
        else:
            raise ValueError(f"Unknown ability score method: {method}")
    
    def _assign_standard_array(self, character_class: str = None, race: str = None) -> Dict[str, int]:
        """Assign using SRD 5E standard array."""
        scores = self.standard_array.copy()
        
        if character_class:
            # Assign highest scores to primary abilities
            primary_abilities = self.class_primary_abilities.get(character_class.lower(), [])
            scores.sort(reverse=True)
            
            assigned = {}
            for i, ability in enumerate(self.abilities):
                if ability in primary_abilities and scores:
                    assigned[ability] = scores.pop(0)
                else:
                    assigned[ability] = scores.pop(0) if scores else 10
            
            return assigned
        else:
            # Random assignment
            import random
            random.shuffle(scores)
            return dict(zip(self.abilities, scores))
    
    def _assign_point_buy(self, character_class: str = None, race: str = None) -> Dict[str, int]:
        """Assign using SRD 5E point buy system."""
        # Start with all 8s
        scores = {ability: 8 for ability in self.abilities}
        points_remaining = 27
        
        if character_class:
            # Prioritize primary abilities
            primary_abilities = self.class_primary_abilities.get(character_class.lower(), [])
            secondary_abilities = self.class_secondary_abilities.get(character_class.lower(), [])
            
            # Assign points to primary abilities first (15, 14)
            for ability in primary_abilities:
                if points_remaining >= 9:  # Cost for 15
                    scores[ability] = 15
                    points_remaining -= 9
                elif points_remaining >= 7:  # Cost for 14
                    scores[ability] = 14
                    points_remaining -= 7
                elif points_remaining >= 5:  # Cost for 13
                    scores[ability] = 13
                    points_remaining -= 5
            
            # Assign points to secondary abilities (13, 12)
            for ability in secondary_abilities:
                if points_remaining >= 5:  # Cost for 13
                    scores[ability] = 13
                    points_remaining -= 5
                elif points_remaining >= 4:  # Cost for 12
                    scores[ability] = 12
                    points_remaining -= 4
        
        # Distribute remaining points to other abilities
        for ability in self.abilities:
            if scores[ability] == 8 and points_remaining > 0:
                if points_remaining >= 2:  # Cost for 10
                    scores[ability] = 10
                    points_remaining -= 2
                elif points_remaining >= 1:  # Cost for 9
                    scores[ability] = 9
                    points_remaining -= 1
        
        return scores
    
    def _assign_optimal(self, character_class: str = None, race: str = None) -> Dict[str, int]:
        """Assign optimal ability scores using Point Buy for the given class."""
        if not character_class:
            # Fallback to point buy if no class specified
            return self._assign_point_buy(character_class, race)
        
        # Use point buy with optimal class-based distribution
        return self._assign_point_buy(character_class, race)
    
    def calculate_modifier(self, score: int) -> int:
        """Calculate ability modifier using SRD 5E formula."""
        return (score - 10) // 2
    
    def get_point_buy_cost(self, score: int) -> int:
        """Get the point buy cost for a given ability score."""
        return self.point_buy_costs.get(score, 0)
    
    def validate_point_buy(self, scores: Dict[str, int]) -> Tuple[bool, str]:
        """Validate if ability scores are valid for point buy."""
        total_cost = 0
        for ability, score in scores.items():
            if score < self.point_buy_min or score > self.point_buy_max:
                return False, f"Score {score} for {ability} is outside valid range (8-15)"
            total_cost += self.get_point_buy_cost(score)
        
        if total_cost > self.point_buy_total:
            return False, f"Total cost {total_cost} exceeds available points {self.point_buy_total}"
        
        return True, f"Valid point buy: {total_cost}/{self.point_buy_total} points used"
    
    def get_optimal_scores_for_class(self, character_class: str) -> Dict[str, int]:
        """Get the optimal ability score distribution for a given class."""
        primary_abilities = self.class_primary_abilities.get(character_class.lower(), [])
        secondary_abilities = self.class_secondary_abilities.get(character_class.lower(), [])
        
        # Optimal distribution: 15, 14, 13, 12, 10, 8
        optimal_scores = [15, 14, 13, 12, 10, 8]
        
        assigned = {}
        score_index = 0
        
        # Assign to primary abilities first
        for ability in primary_abilities:
            if score_index < len(optimal_scores):
                assigned[ability] = optimal_scores[score_index]
                score_index += 1
        
        # Assign to secondary abilities
        for ability in secondary_abilities:
            if score_index < len(optimal_scores):
                assigned[ability] = optimal_scores[score_index]
                score_index += 1
        
        # Assign remaining scores to other abilities
        for ability in self.abilities:
            if ability not in assigned and score_index < len(optimal_scores):
                assigned[ability] = optimal_scores[score_index]
                score_index += 1
        
        return assigned
    
    def apply_racial_bonuses(self, scores: Dict[str, int], race: str) -> Dict[str, int]:
        """Apply racial ability score bonuses."""
        # SRD 5E racial bonuses
        racial_bonuses = {
            'human': {'strength': 1, 'dexterity': 1, 'constitution': 1, 'intelligence': 1, 'wisdom': 1, 'charisma': 1},
            'elf': {'dexterity': 2},
            'dwarf': {'constitution': 2},
            'halfling': {'dexterity': 2},
            'dragonborn': {'strength': 2, 'charisma': 1},
            'gnome': {'intelligence': 2},
            'half-elf': {'charisma': 2, 'strength': 1, 'constitution': 1},
            'half-orc': {'strength': 2, 'constitution': 1},
            'tiefling': {'intelligence': 1, 'charisma': 2}
        }
        
        bonuses = racial_bonuses.get(race.lower(), {})
        for ability, bonus in bonuses.items():
            if ability in scores:
                scores[ability] += bonus
        
        return scores
    
    def get_ability_score_summary(self, scores: Dict[str, int]) -> Dict[str, Dict[str, int]]:
        """Get a summary of ability scores with modifiers."""
        summary = {}
        for ability, score in scores.items():
            summary[ability] = {
                'score': score,
                'modifier': self.calculate_modifier(score)
            }
        return summary 