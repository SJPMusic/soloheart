#!/usr/bin/env python3
"""
Character Manager for Solo DnD 5E
Handles character creation, validation, and operations using SRD-compliant schema.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import jsonschema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CharacterManager:
    """Manages character creation and operations using SRD-compliant schema."""
    
    def __init__(self):
        self.schema = self._load_schema()
        self.srd_data = self._load_srd_data()
    
    def _load_schema(self) -> Dict:
        """Load the character schema."""
        try:
            with open('character_schema.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading character schema: {e}")
            return {}
    
    def _load_srd_data(self) -> Dict:
        """Load SRD data for validation and defaults."""
        try:
            srd_files = ['classes.json', 'races.json', 'backgrounds.json', 'equipment.json']
            srd_data = {}
            
            for filename in srd_files:
                filepath = os.path.join('srd_data', filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        srd_data[filename.replace('.json', '')] = json.load(f)
            
            return srd_data
        except Exception as e:
            logger.error(f"Error loading SRD data: {e}")
            return {}
    
    def create_character(self, basic_info: Dict, creation_method: str = "manual") -> Dict:
        """Create a new character with the provided basic info."""
        try:
            # Create base character structure
            character = {
                "metadata": {
                    "version": "1.0.0",
                    "created_date": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat(),
                    "creation_method": creation_method
                },
                "basic_info": {
                    "name": basic_info.get("name", "Adventurer"),
                    "race": basic_info.get("race", "Human"),
                    "class": basic_info.get("class", "Fighter"),
                    "background": basic_info.get("background", "Soldier"),
                    "alignment": basic_info.get("alignment", "True Neutral"),
                    "level": basic_info.get("level", 1),
                    "experience_points": basic_info.get("experience_points", 0),
                    "proficiency_bonus": self._calculate_proficiency_bonus(basic_info.get("level", 1))
                },
                "ability_scores": {
                    "strength": basic_info.get("stats", {}).get("strength", 10),
                    "dexterity": basic_info.get("stats", {}).get("dexterity", 10),
                    "constitution": basic_info.get("stats", {}).get("constitution", 10),
                    "intelligence": basic_info.get("stats", {}).get("intelligence", 10),
                    "wisdom": basic_info.get("stats", {}).get("wisdom", 10),
                    "charisma": basic_info.get("stats", {}).get("charisma", 10)
                }
            }
            
            # Add computed sections
            character.update(self._create_saving_throws(character))
            character.update(self._create_skills(character))
            character.update(self._create_combat_stats(character))
            character.update(self._create_proficiencies(character))
            character.update(self._create_equipment(character))
            character.update(self._create_personality(character))
            character.update(self._create_features(character))
            character.update(self._create_spellcasting(character))
            character.update(self._create_background_info(character))
            
            # Validate the character
            if self.validate_character(character):
                return character
            else:
                raise ValueError("Character validation failed")
                
        except Exception as e:
            logger.error(f"Error creating character: {e}")
            raise
    
    def _calculate_proficiency_bonus(self, level: int) -> int:
        """Calculate proficiency bonus based on level."""
        return ((level - 1) // 4) + 2
    
    def _calculate_ability_modifier(self, score: int) -> int:
        """Calculate ability modifier from ability score."""
        return (score - 10) // 2
    
    def _create_saving_throws(self, character: Dict) -> Dict:
        """Create saving throws section."""
        ability_scores = character["ability_scores"]
        class_name = character["basic_info"]["class"]
        
        # Get class saving throw proficiencies
        class_data = self.srd_data.get("classes", {}).get(class_name, {})
        saving_throw_proficiencies = class_data.get("saving_throw_proficiencies", [])
        
        saving_throws = {}
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            proficient = ability in saving_throw_proficiencies
            modifier = self._calculate_ability_modifier(ability_scores[ability])
            if proficient:
                modifier += character["basic_info"]["proficiency_bonus"]
            
            saving_throws[ability] = {
                "proficient": proficient,
                "modifier": modifier
            }
        
        return {"saving_throws": saving_throws}
    
    def _create_skills(self, character: Dict) -> Dict:
        """Create skills section."""
        ability_scores = character["ability_scores"]
        class_name = character["basic_info"]["class"]
        background = character["basic_info"]["background"]
        
        # Get class and background skill proficiencies
        class_data = self.srd_data.get("classes", {}).get(class_name, {})
        background_data = self.srd_data.get("backgrounds", {}).get(background, {})
        
        class_skills = class_data.get("skill_proficiencies", [])
        background_skills = background_data.get("skill_proficiencies", [])
        
        # Define all skills with their associated abilities
        all_skills = {
            "acrobatics": "dexterity",
            "animal_handling": "wisdom",
            "arcana": "intelligence",
            "athletics": "strength",
            "deception": "charisma",
            "history": "intelligence",
            "insight": "wisdom",
            "intimidation": "charisma",
            "investigation": "intelligence",
            "medicine": "wisdom",
            "nature": "intelligence",
            "perception": "wisdom",
            "performance": "charisma",
            "persuasion": "charisma",
            "religion": "intelligence",
            "sleight_of_hand": "dexterity",
            "stealth": "dexterity",
            "survival": "wisdom"
        }
        
        skills = {}
        for skill_name, ability in all_skills.items():
            proficient = skill_name in class_skills or skill_name in background_skills
            modifier = self._calculate_ability_modifier(ability_scores[ability])
            if proficient:
                modifier += character["basic_info"]["proficiency_bonus"]
            
            skills[skill_name] = {
                "proficient": proficient,
                "expertise": False,  # Will be set by class features
                "modifier": modifier,
                "ability": ability
            }
        
        return {"skills": skills}
    
    def _create_combat_stats(self, character: Dict) -> Dict:
        """Create combat stats section."""
        ability_scores = character["ability_scores"]
        class_name = character["basic_info"]["class"]
        level = character["basic_info"]["level"]
        
        # Calculate initiative
        initiative = self._calculate_ability_modifier(ability_scores["dexterity"])
        
        # Calculate hit points (simplified - would need class hit die info)
        constitution_modifier = self._calculate_ability_modifier(ability_scores["constitution"])
        base_hp = 8 + constitution_modifier  # Default to d8
        max_hp = base_hp + (level - 1) * (4 + constitution_modifier)  # Average roll
        
        # Determine hit dice based on class
        hit_dice_map = {
            "Barbarian": "1d12",
            "Fighter": "1d10",
            "Paladin": "1d10",
            "Ranger": "1d10",
            "Cleric": "1d8",
            "Druid": "1d8",
            "Monk": "1d8",
            "Rogue": "1d8",
            "Bard": "1d8",
            "Warlock": "1d8",
            "Sorcerer": "1d6",
            "Wizard": "1d6"
        }
        
        hit_die_type = hit_dice_map.get(class_name, "1d8")
        
        combat_stats = {
            "armor_class": 10 + self._calculate_ability_modifier(ability_scores["dexterity"]),
            "initiative": initiative,
            "speed": 30,  # Base speed, will be modified by race
            "hit_points": {
                "maximum": max_hp,
                "current": max_hp,
                "temporary": 0
            },
            "hit_dice": [
                {
                    "type": hit_die_type,
                    "total": level,
                    "used": 0
                }
            ]
        }
        
        return {"combat_stats": combat_stats}
    
    def _create_proficiencies(self, character: Dict) -> Dict:
        """Create proficiencies section."""
        class_name = character["basic_info"]["class"]
        background = character["basic_info"]["background"]
        
        class_data = self.srd_data.get("classes", {}).get(class_name, {})
        background_data = self.srd_data.get("backgrounds", {}).get(background, {})
        
        proficiencies = {
            "armor": class_data.get("armor_proficiencies", []),
            "weapons": class_data.get("weapon_proficiencies", []),
            "tools": background_data.get("tool_proficiencies", []),
            "languages": ["Common"] + background_data.get("language_proficiencies", [])
        }
        
        return {"proficiencies": proficiencies}
    
    def _create_equipment(self, character: Dict) -> Dict:
        """Create equipment section."""
        class_name = character["basic_info"]["class"]
        background = character["basic_info"]["background"]
        
        class_data = self.srd_data.get("classes", {}).get(class_name, {})
        background_data = self.srd_data.get("backgrounds", {}).get(background, {})
        
        equipment = {
            "weapons": [],
            "armor": [],
            "items": [],
            "currency": {
                "copper": 0,
                "silver": 0,
                "electrum": 0,
                "gold": 0,
                "platinum": 0
            }
        }
        
        # Add starting equipment from class and background
        if "starting_equipment" in class_data:
            equipment["items"].extend(class_data["starting_equipment"])
        
        if "starting_equipment" in background_data:
            equipment["items"].extend(background_data["starting_equipment"])
        
        return {"equipment": equipment}
    
    def _create_personality(self, character: Dict) -> Dict:
        """Create personality section."""
        background = character["basic_info"]["background"]
        background_data = self.srd_data.get("backgrounds", {}).get(background, {})
        
        personality = {
            "traits": background_data.get("personality_traits", []),
            "ideals": background_data.get("ideals", []),
            "bonds": background_data.get("bonds", []),
            "flaws": background_data.get("flaws", [])
        }
        
        return {"personality": personality}
    
    def _create_features(self, character: Dict) -> Dict:
        """Create features section."""
        class_name = character["basic_info"]["class"]
        race = character["basic_info"]["race"]
        
        features = []
        
        # Add class features
        class_data = self.srd_data.get("classes", {}).get(class_name, {})
        if "features" in class_data:
            for feature in class_data["features"]:
                features.append({
                    "name": feature["name"],
                    "source": "class",
                    "description": feature["description"],
                    "level_acquired": feature.get("level", 1)
                })
        
        # Add race features
        race_data = self.srd_data.get("races", {}).get(race, {})
        if "features" in race_data:
            for feature in race_data["features"]:
                features.append({
                    "name": feature["name"],
                    "source": "race",
                    "description": feature["description"],
                    "level_acquired": 1
                })
        
        return {"features": features}
    
    def _create_spellcasting(self, character: Dict) -> Dict:
        """Create spellcasting section."""
        class_name = character["basic_info"]["class"]
        ability_scores = character["ability_scores"]
        
        # Determine spellcasting ability
        spellcasting_ability_map = {
            "Bard": "charisma",
            "Cleric": "wisdom",
            "Druid": "wisdom",
            "Paladin": "charisma",
            "Ranger": "wisdom",
            "Sorcerer": "charisma",
            "Warlock": "charisma",
            "Wizard": "intelligence"
        }
        
        spellcasting_ability = spellcasting_ability_map.get(class_name)
        
        if not spellcasting_ability:
            # Non-spellcasting class
            return {
                "spellcasting": {
                    "ability": None,
                    "spell_save_dc": 0,
                    "spell_attack_bonus": 0,
                    "spell_slots": {},
                    "spells": []
                }
            }
        
        # Calculate spellcasting stats
        ability_modifier = self._calculate_ability_modifier(ability_scores[spellcasting_ability])
        proficiency_bonus = character["basic_info"]["proficiency_bonus"]
        
        spellcasting = {
            "ability": spellcasting_ability,
            "spell_save_dc": 8 + proficiency_bonus + ability_modifier,
            "spell_attack_bonus": proficiency_bonus + ability_modifier,
            "spell_slots": {},
            "spells": []
        }
        
        return {"spellcasting": spellcasting}
    
    def _create_background_info(self, character: Dict) -> Dict:
        """Create background info section."""
        background_info = {
            "backstory": "",
            "appearance": "",
            "notes": ""
        }
        
        return {"background_info": background_info}
    
    def validate_character(self, character: Dict) -> bool:
        """Validate character against the schema."""
        try:
            jsonschema.validate(instance=character, schema=self.schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Character validation error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating character: {e}")
            return False
    
    def save_character(self, character: Dict, campaign_id: str) -> bool:
        """Save character to file."""
        try:
            # Update last modified timestamp
            character["metadata"]["last_modified"] = datetime.now().isoformat()
            
            # Ensure directory exists
            os.makedirs('character_saves', exist_ok=True)
            
            # Save character
            filename = f"character_saves/{campaign_id}_character.json"
            with open(filename, 'w') as f:
                json.dump(character, f, indent=2)
            
            logger.info(f"Character saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving character: {e}")
            return False
    
    def load_character(self, campaign_id: str) -> Optional[Dict]:
        """Load character from file."""
        try:
            filename = f"character_saves/{campaign_id}_character.json"
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    character = json.load(f)
                
                # Validate loaded character
                if self.validate_character(character):
                    logger.info(f"Character loaded from {filename}")
                    return character
                else:
                    logger.error(f"Invalid character data in {filename}")
                    return None
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error loading character: {e}")
            return None
    
    def update_character(self, character: Dict, updates: Dict) -> Dict:
        """Update character with new data."""
        try:
            # Deep merge updates into character
            def deep_merge(base, updates):
                for key, value in updates.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value
                return base
            
            updated_character = deep_merge(character.copy(), updates)
            updated_character["metadata"]["last_modified"] = datetime.now().isoformat()
            
            # Validate updated character
            if self.validate_character(updated_character):
                return updated_character
            else:
                raise ValueError("Updated character validation failed")
                
        except Exception as e:
            logger.error(f"Error updating character: {e}")
            raise
    
    def get_character_summary(self, character: Dict) -> Dict:
        """Get a summary of character information."""
        basic_info = character["basic_info"]
        ability_scores = character["ability_scores"]
        
        return {
            "name": basic_info["name"],
            "race": basic_info["race"],
            "class": basic_info["class"],
            "level": basic_info["level"],
            "background": basic_info["background"],
            "alignment": basic_info["alignment"],
            "hit_points": character["combat_stats"]["hit_points"]["current"],
            "max_hit_points": character["combat_stats"]["hit_points"]["maximum"],
            "armor_class": character["combat_stats"]["armor_class"],
            "ability_scores": ability_scores,
            "proficiency_bonus": basic_info["proficiency_bonus"]
        } 