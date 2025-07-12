#!/usr/bin/env python3
"""
Player-Friendly Dice Rolling System for SoloHeart

This module provides a dice rolling system designed for players with zero RPG knowledge.
Instead of requiring players to know dice notation (d20, d8, etc.), the game prompts
them with natural language and automatically applies modifiers from their character sheet.
"""

import random
import re
import logging
from typing import Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class DiceRoller:
    """Player-friendly dice rolling system with automatic modifier application."""
    
    def __init__(self):
        self.dice_names = {
            4: "4-sided die",
            6: "6-sided die", 
            8: "8-sided die",
            10: "10-sided die",
            12: "12-sided die",
            20: "20-sided die",
            100: "100-sided die"
        }
    
    def roll_dice(self, sides: int, count: int = 1, modifier: int = 0) -> Dict:
        """
        Roll dice and return results in a player-friendly format.
        
        Args:
            sides: Number of sides on the die (4, 6, 8, 10, 12, 20, 100)
            count: Number of dice to roll (default 1)
            modifier: Modifier to add to the total (default 0)
            
        Returns:
            Dict with roll results in player-friendly format
        """
        if sides not in self.dice_names:
            return {
                "success": False,
                "error": f"Invalid die size: {sides}. Valid sizes are: {list(self.dice_names.keys())}"
            }
        
        try:
            # Roll the dice
            rolls = [random.randint(1, sides) for _ in range(count)]
            total = sum(rolls) + modifier
            
            # Create player-friendly description
            if count == 1:
                die_name = self.dice_names[sides]
                description = f"Roll a {die_name}"
            else:
                die_name = self.dice_names[sides]
                description = f"Roll {count} {die_name}s"
            
            if modifier > 0:
                description += f" and add {modifier}"
            elif modifier < 0:
                description += f" and subtract {abs(modifier)}"
            
            return {
                "success": True,
                "description": description,
                "dice_sides": sides,
                "dice_count": count,
                "modifier": modifier,
                "rolls": rolls,
                "total": total,
                "player_friendly": {
                    "prompt": description,
                    "result": f"You rolled {sum(rolls)}",
                    "modifier_text": f" + {modifier}" if modifier > 0 else f" - {abs(modifier)}" if modifier < 0 else "",
                    "total_text": f" = {total} total"
                }
            }
            
        except Exception as e:
            logger.error(f"Error rolling dice: {e}")
            return {
                "success": False,
                "error": f"Error rolling dice: {str(e)}"
            }
    
    def roll_attack(self, character_data: Dict) -> Dict:
        """
        Roll an attack with automatic modifier calculation.
        
        Args:
            character_data: Character data including ability scores and proficiencies
            
        Returns:
            Attack roll result
        """
        # Determine attack bonus based on character data
        attack_bonus = self._calculate_attack_bonus(character_data)
        
        result = self.roll_dice(20, 1, attack_bonus)
        if result["success"]:
            result["roll_type"] = "attack"
            result["attack_bonus"] = attack_bonus
            
        return result
    
    def roll_ability_check(self, ability: str, character_data: Dict) -> Dict:
        """
        Roll an ability check with automatic modifier calculation.
        
        Args:
            ability: Ability name (strength, dexterity, etc.)
            character_data: Character data including ability scores
            
        Returns:
            Ability check result
        """
        ability_modifier = self._calculate_ability_modifier(ability, character_data)
        
        result = self.roll_dice(20, 1, ability_modifier)
        if result["success"]:
            result["roll_type"] = "ability_check"
            result["ability"] = ability
            result["ability_modifier"] = ability_modifier
            
        return result
    
    def roll_saving_throw(self, ability: str, character_data: Dict) -> Dict:
        """
        Roll a saving throw with automatic modifier calculation.
        
        Args:
            ability: Ability name (strength, dexterity, etc.)
            character_data: Character data including ability scores and proficiencies
            
        Returns:
            Saving throw result
        """
        save_modifier = self._calculate_save_modifier(ability, character_data)
        
        result = self.roll_dice(20, 1, save_modifier)
        if result["success"]:
            result["roll_type"] = "saving_throw"
            result["ability"] = ability
            result["save_modifier"] = save_modifier
            
        return result
    
    def roll_damage(self, damage_dice: str, character_data: Dict) -> Dict:
        """
        Roll damage dice with automatic modifier calculation.
        
        Args:
            damage_dice: Damage dice string (e.g., "1d6", "2d8+3")
            character_data: Character data for damage modifiers
            
        Returns:
            Damage roll result
        """
        # Parse damage dice string
        parsed = self._parse_damage_dice(damage_dice)
        if not parsed["success"]:
            return parsed
        
        count, sides, modifier = parsed["count"], parsed["sides"], parsed["modifier"]
        
        # Add strength modifier for melee weapons
        if character_data.get("class") in ["Fighter", "Barbarian", "Paladin"]:
            strength_mod = self._calculate_ability_modifier("strength", character_data)
            modifier += strength_mod
        
        result = self.roll_dice(sides, count, modifier)
        if result["success"]:
            result["roll_type"] = "damage"
            result["damage_dice"] = damage_dice
            
        return result
    
    def _calculate_attack_bonus(self, character_data: Dict) -> int:
        """Calculate attack bonus from character data."""
        # Base attack bonus from level and class
        level = character_data.get("level", 1)
        char_class = character_data.get("class", "")
        
        # Simple attack bonus calculation
        if char_class in ["Fighter", "Paladin", "Ranger"]:
            base_bonus = level
        elif char_class in ["Rogue", "Monk"]:
            base_bonus = level - 1
        else:  # Spellcasters
            base_bonus = level - 2
        
        # Add ability modifier (use strength for melee, dexterity for ranged)
        ability_mod = self._calculate_ability_modifier("strength", character_data)
        
        return base_bonus + ability_mod
    
    def _calculate_ability_modifier(self, ability: str, character_data: Dict) -> int:
        """Calculate ability modifier from character data."""
        ability_scores = character_data.get("ability_scores", {})
        ability_map = {
            "strength": "str",
            "dexterity": "dex", 
            "constitution": "con",
            "intelligence": "int",
            "wisdom": "wis",
            "charisma": "cha"
        }
        ability_key = (ability or '')
        logger.debug(f">>> DEBUG: calling .lower() on ability in _calculate_ability_modifier, value={ability!r}, type={type(ability)}")
        ability_key = ability_key.lower()
        score_key = ability_map.get(ability_key)
        if not score_key or score_key not in ability_scores:
            return 0
        score = ability_scores[score_key]
        return (score - 10) // 2
    
    def _calculate_save_modifier(self, ability: str, character_data: Dict) -> int:
        """Calculate saving throw modifier from character data."""
        ability_mod = self._calculate_ability_modifier(ability, character_data)
        
        # Add proficiency bonus if proficient
        level = character_data.get("level", 1)
        proficiency_bonus = (level - 1) // 4 + 2
        
        # Check if proficient in this save (simplified)
        char_class = character_data.get("class", "")
        if char_class in ["Fighter", "Paladin"] and ability in ["strength", "constitution"]:
            return ability_mod + proficiency_bonus
        elif char_class in ["Rogue", "Monk"] and ability in ["dexterity", "intelligence"]:
            return ability_mod + proficiency_bonus
        else:
            return ability_mod
    
    def _parse_damage_dice(self, damage_dice: str) -> Dict:
        """Parse damage dice string (e.g., '1d6', '2d8+3')."""
        pattern = r'(\d+)d(\d+)([+-]\d+)?'
        logger.debug(f">>> DEBUG: calling .lower() on damage_dice in _parse_damage_dice, value={damage_dice!r}, type={type(damage_dice)}")
        match = re.match(pattern, damage_dice.lower())
        
        if not match:
            return {
                "success": False,
                "error": f"Invalid damage dice format: {damage_dice}. Use format like '1d6' or '2d8+3'"
            }
        
        count = int(match.group(1))
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        return {
            "success": True,
            "count": count,
            "sides": sides,
            "modifier": modifier
        }

# Global dice roller instance
dice_roller = DiceRoller() 