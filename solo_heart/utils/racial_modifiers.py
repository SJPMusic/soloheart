#!/usr/bin/env python3
"""
DnD SRD 5.2 Racial Modifiers for SoloHeart

This module provides racial ability score modifiers that follow the official DnD SRD 5.2 rules.
It supports standard races and allows for custom lineages or variants.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class RacialModifiers:
    """Racial ability score modifiers following SRD 5.2 rules."""
    
    def __init__(self):
        # SRD 5.2 Racial Ability Score Modifiers
        self.racial_modifiers = {
            'human': {
                'name': 'Human',
                'description': 'Versatile and adaptable',
                'ability_bonuses': {
                    'strength': 1,
                    'dexterity': 1,
                    'constitution': 1,
                    'intelligence': 1,
                    'wisdom': 1,
                    'charisma': 1
                },
                'traits': ['Extra Language'],
                'subraces': []
            },
            'elf': {
                'name': 'Elf',
                'description': 'Graceful and long-lived',
                'ability_bonuses': {
                    'dexterity': 2
                },
                'traits': ['Darkvision', 'Keen Senses', 'Fey Ancestry', 'Trance'],
                'subraces': ['High Elf', 'Wood Elf', 'Dark Elf (Drow)']
            },
            'dwarf': {
                'name': 'Dwarf',
                'description': 'Sturdy and determined',
                'ability_bonuses': {
                    'constitution': 2
                },
                'traits': ['Darkvision', 'Dwarven Resilience', 'Dwarven Combat Training', 'Stonecunning'],
                'subraces': ['Hill Dwarf', 'Mountain Dwarf']
            },
            'halfling': {
                'name': 'Halfling',
                'description': 'Small and lucky',
                'ability_bonuses': {
                    'dexterity': 2
                },
                'traits': ['Lucky', 'Brave', 'Halfling Nimbleness'],
                'subraces': ['Lightfoot', 'Stout']
            },
            'dragonborn': {
                'name': 'Dragonborn',
                'description': 'Proud and draconic',
                'ability_bonuses': {
                    'strength': 2,
                    'charisma': 1
                },
                'traits': ['Draconic Ancestry', 'Breath Weapon', 'Damage Resistance'],
                'subraces': []
            },
            'gnome': {
                'name': 'Gnome',
                'description': 'Curious and inventive',
                'ability_bonuses': {
                    'intelligence': 2
                },
                'traits': ['Darkvision', 'Gnome Cunning'],
                'subraces': ['Forest Gnome', 'Rock Gnome']
            },
            'half-elf': {
                'name': 'Half-Elf',
                'description': 'Diplomatic and versatile',
                'ability_bonuses': {
                    'charisma': 2
                },
                'traits': ['Darkvision', 'Fey Ancestry', 'Skill Versatility'],
                'subraces': []
            },
            'half-orc': {
                'name': 'Half-Orc',
                'description': 'Strong and intimidating',
                'ability_bonuses': {
                    'strength': 2,
                    'constitution': 1
                },
                'traits': ['Darkvision', 'Menacing', 'Relentless Endurance', 'Savage Attacks'],
                'subraces': []
            },
            'tiefling': {
                'name': 'Tiefling',
                'description': 'Infernal heritage',
                'ability_bonuses': {
                    'intelligence': 1,
                    'charisma': 2
                },
                'traits': ['Darkvision', 'Hellish Resistance', 'Infernal Legacy'],
                'subraces': []
            }
        }
        
        # Subrace modifiers (additional bonuses)
        self.subrace_modifiers = {
            'high elf': {
                'intelligence': 1,
                'traits': ['Elf Weapon Training', 'Cantrip']
            },
            'wood elf': {
                'wisdom': 1,
                'traits': ['Elf Weapon Training', 'Fleet of Foot', 'Mask of the Wild']
            },
            'dark elf (drow)': {
                'charisma': 1,
                'traits': ['Superior Darkvision', 'Sunlight Sensitivity', 'Drow Magic', 'Drow Weapon Training']
            },
            'hill dwarf': {
                'wisdom': 1,
                'traits': ['Dwarven Toughness']
            },
            'mountain dwarf': {
                'strength': 2,
                'traits': ['Dwarven Armor Training']
            },
            'lightfoot': {
                'charisma': 1,
                'traits': ['Naturally Stealthy']
            },
            'stout': {
                'constitution': 1,
                'traits': ['Stout Resilience']
            },
            'forest gnome': {
                'dexterity': 1,
                'traits': ['Natural Illusionist', 'Speak with Small Beasts']
            },
            'rock gnome': {
                'constitution': 1,
                'traits': ['Artificer\'s Lore', 'Tinker']
            }
        }
    
    def get_available_races(self) -> Dict[str, Dict]:
        """Get all available races with their descriptions."""
        return {
            race: {
                'name': data['name'],
                'description': data['description'],
                'ability_bonuses': data['ability_bonuses'],
                'traits': data['traits'],
                'subraces': data['subraces']
            }
            for race, data in self.racial_modifiers.items()
        }
    
    def get_race_info(self, race: str) -> Optional[Dict]:
        """Get detailed information about a specific race."""
        race = race.lower()
        if race not in self.racial_modifiers:
            return None
        
        return self.racial_modifiers[race]
    
    def get_subrace_info(self, subrace: str) -> Optional[Dict]:
        """Get detailed information about a specific subrace."""
        subrace = subrace.lower()
        if subrace not in self.subrace_modifiers:
            return None
        
        return self.subrace_modifiers[subrace]
    
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
        race = race.lower()
        modified_scores = base_scores.copy()
        
        # Apply base race modifiers
        if race in self.racial_modifiers:
            race_modifiers = self.racial_modifiers[race]['ability_bonuses']
            for ability, bonus in race_modifiers.items():
                if ability in modified_scores:
                    modified_scores[ability] += bonus
                    logger.debug(f"Applied {race} bonus: {ability} +{bonus}")
        
        # Apply subrace modifiers
        if subrace:
            subrace = subrace.lower()
            if subrace in self.subrace_modifiers:
                subrace_modifiers = self.subrace_modifiers[subrace]
                for ability, bonus in subrace_modifiers.items():
                    if ability != 'traits' and ability in modified_scores:
                        modified_scores[ability] += bonus
                        logger.debug(f"Applied {subrace} bonus: {ability} +{bonus}")
        
        logger.info(f"🎲 Applied racial modifiers: {race}" + (f" ({subrace})" if subrace else ""))
        return modified_scores
    
    def get_racial_traits(self, race: str, subrace: str = None) -> List[str]:
        """
        Get racial traits for a given race and subrace.
        
        Args:
            race: Character race
            subrace: Character subrace (optional)
            
        Returns:
            List of racial traits
        """
        race = race.lower()
        traits = []
        
        # Get base race traits
        if race in self.racial_modifiers:
            traits.extend(self.racial_modifiers[race]['traits'])
        
        # Get subrace traits
        if subrace:
            subrace = subrace.lower()
            if subrace in self.subrace_modifiers:
                subrace_data = self.subrace_modifiers[subrace]
                if 'traits' in subrace_data:
                    traits.extend(subrace_data['traits'])
        
        return traits
    
    def validate_race_subrace_combination(self, race: str, subrace: str = None) -> bool:
        """
        Validate that a race and subrace combination is valid.
        
        Args:
            race: Character race
            subrace: Character subrace (optional)
            
        Returns:
            True if valid combination, False otherwise
        """
        race = race.lower()
        
        if race not in self.racial_modifiers:
            return False
        
        if not subrace:
            return True
        
        subrace = subrace.lower()
        available_subraces = [s.lower() for s in self.racial_modifiers[race]['subraces']]
        
        return subrace in available_subraces
    
    def get_recommended_races_for_class(self, char_class: str) -> List[str]:
        """
        Get recommended races for a given class based on ability score synergies.
        
        Args:
            char_class: Character class
            
        Returns:
            List of recommended races
        """
        char_class = char_class.lower()
        
        # Class primary abilities
        class_abilities = {
            'fighter': ['strength', 'constitution'],
            'paladin': ['strength', 'charisma'],
            'barbarian': ['strength', 'constitution'],
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
        
        primary_abilities = class_abilities.get(char_class, ['strength', 'constitution'])
        
        # Find races that boost primary abilities
        recommended_races = []
        for race, data in self.racial_modifiers.items():
            race_bonuses = set(data['ability_bonuses'].keys())
            if any(ability in race_bonuses for ability in primary_abilities):
                recommended_races.append(race)
        
        return recommended_races
    
    def format_racial_summary(self, race: str, subrace: str = None) -> str:
        """
        Format a summary of racial traits and bonuses.
        
        Args:
            race: Character race
            subrace: Character subrace (optional)
            
        Returns:
            Formatted racial summary
        """
        race_info = self.get_race_info(race)
        if not race_info:
            return f"Unknown race: {race}"
        
        summary = f"**{race_info['name']}"
        if subrace:
            summary += f" ({subrace.title()})"
        summary += "**\n\n"
        
        # Ability bonuses
        bonuses = race_info['ability_bonuses']
        if subrace and subrace.lower() in self.subrace_modifiers:
            subrace_data = self.subrace_modifiers[subrace.lower()]
            for ability, bonus in subrace_data.items():
                if ability != 'traits':
                    bonuses[ability] = bonuses.get(ability, 0) + bonus
        
        if bonuses:
            summary += "**Ability Score Bonuses:**\n"
            for ability, bonus in bonuses.items():
                summary += f"• {ability.title()}: +{bonus}\n"
            summary += "\n"
        
        # Traits
        traits = self.get_racial_traits(race, subrace)
        if traits:
            summary += "**Racial Traits:**\n"
            for trait in traits:
                summary += f"• {trait}\n"
        
        return summary

# Global racial modifiers instance
racial_modifiers = RacialModifiers() 