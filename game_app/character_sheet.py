#!/usr/bin/env python3
"""
Character Sheet Class for SoloHeart
Comprehensive SRD 5.2-compliant character data structure.
"""

import json
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class Alignment(Enum):
    """D&D 5E alignments."""
    LAWFUL_GOOD = "Lawful Good"
    NEUTRAL_GOOD = "Neutral Good"
    CHAOTIC_GOOD = "Chaotic Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    TRUE_NEUTRAL = "True Neutral"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_EVIL = "Chaotic Evil"

@dataclass
class CharacterSheet:
    """
    Comprehensive D&D 5E character sheet with SRD 5.2 compliance.
    
    This class represents a complete character profile with all required fields
    for D&D 5E gameplay, ensuring SRD compliance and future vibe code compatibility.
    """
    
    # ===== IDENTITY SECTION =====
    character_name: str = ""
    player_name: str = ""
    race: str = ""  # SRD only - see SRD Appendix B
    class_name: str = ""  # SRD only - see SRD Appendix B
    level: int = 1
    background: str = ""  # SRD only - see SRD Appendix B
    alignment: str = "True Neutral"
    experience_points: int = 0
    inspiration: bool = False
    
    # ===== ABILITY SCORES SECTION =====
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    proficiency_bonus: int = 2
    
    # ===== MODIFIERS SECTION =====
    strength_mod: int = 0
    dexterity_mod: int = 0
    constitution_mod: int = 0
    intelligence_mod: int = 0
    wisdom_mod: int = 0
    charisma_mod: int = 0
    
    # ===== SAVING THROWS SECTION =====
    saving_throws: Dict[str, Dict[str, Union[bool, int]]] = field(default_factory=lambda: {
        "strength": {"is_proficient": False, "modifier": 0},
        "dexterity": {"is_proficient": False, "modifier": 0},
        "constitution": {"is_proficient": False, "modifier": 0},
        "intelligence": {"is_proficient": False, "modifier": 0},
        "wisdom": {"is_proficient": False, "modifier": 0},
        "charisma": {"is_proficient": False, "modifier": 0}
    })
    
    # ===== SKILLS SECTION (All SRD) =====
    skills: Dict[str, Dict[str, Union[str, bool, int]]] = field(default_factory=lambda: {
        # Strength skills
        "athletics": {"ability": "strength", "is_proficient": False, "modifier": 0},
        # Dexterity skills
        "acrobatics": {"ability": "dexterity", "is_proficient": False, "modifier": 0},
        "sleight_of_hand": {"ability": "dexterity", "is_proficient": False, "modifier": 0},
        "stealth": {"ability": "dexterity", "is_proficient": False, "modifier": 0},
        # Intelligence skills
        "arcana": {"ability": "intelligence", "is_proficient": False, "modifier": 0},
        "history": {"ability": "intelligence", "is_proficient": False, "modifier": 0},
        "investigation": {"ability": "intelligence", "is_proficient": False, "modifier": 0},
        "nature": {"ability": "intelligence", "is_proficient": False, "modifier": 0},
        "religion": {"ability": "intelligence", "is_proficient": False, "modifier": 0},
        # Wisdom skills
        "animal_handling": {"ability": "wisdom", "is_proficient": False, "modifier": 0},
        "insight": {"ability": "wisdom", "is_proficient": False, "modifier": 0},
        "medicine": {"ability": "wisdom", "is_proficient": False, "modifier": 0},
        "perception": {"ability": "wisdom", "is_proficient": False, "modifier": 0},
        "survival": {"ability": "wisdom", "is_proficient": False, "modifier": 0},
        # Charisma skills
        "deception": {"ability": "charisma", "is_proficient": False, "modifier": 0},
        "intimidation": {"ability": "charisma", "is_proficient": False, "modifier": 0},
        "performance": {"ability": "charisma", "is_proficient": False, "modifier": 0},
        "persuasion": {"ability": "charisma", "is_proficient": False, "modifier": 0}
    })
    
    # ===== COMBAT STATS SECTION =====
    armor_class: int = 10
    initiative: int = 0
    speed: int = 30
    hit_points_max: int = 10
    hit_points_current: int = 10
    temporary_hit_points: int = 0
    hit_dice_total: str = "1d8"
    hit_dice_remaining: str = "1d8"
    death_saves: Dict[str, int] = field(default_factory=lambda: {"successes": 0, "failures": 0})
    passive_perception: int = 10
    
    # ===== ATTACKS AND SPELLCASTING SECTION =====
    attacks: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    spellcasting: Dict[str, Any] = field(default_factory=lambda: {
        "spellcasting_ability": "",
        "spell_save_dc": 0,
        "spell_attack_bonus": 0,
        "cantrips": [],
        "known_spells_by_level": {},
        "prepared_spells": [],
        "slots_total_by_level": {},
        "slots_used_by_level": {}
    })
    
    # ===== EQUIPMENT & CURRENCY SECTION =====
    equipment: List[str] = field(default_factory=list)
    currency: Dict[str, int] = field(default_factory=lambda: {
        "cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0
    })
    
    # ===== PROFICIENCIES AND FEATS SECTION =====
    armor_proficiencies: List[str] = field(default_factory=list)
    weapon_proficiencies: List[str] = field(default_factory=list)
    tool_proficiencies: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    feats: List[str] = field(default_factory=list)  # SRD-only validation required
    
    # ===== PERSONALITY & STORY SECTION =====
    personality_traits: str = ""
    ideals: str = ""
    bonds: str = ""
    flaws: str = ""
    features_and_traits: List[str] = field(default_factory=list)  # From race, class, background
    backstory: str = ""
    character_appearance: str = ""
    allies_and_organizations: List[str] = field(default_factory=list)
    faction_symbol: Optional[str] = None
    
    # ===== PHYSICAL DESCRIPTION SECTION =====
    age: str = ""
    height: str = ""
    weight: str = ""
    eyes: str = ""
    hair: str = ""
    skin: str = ""
    
    # ===== METADATA SECTION =====
    created_date: str = ""
    last_modified: str = ""
    creation_method: str = ""
    campaign_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize derived values and validate SRD compliance."""
        # Set creation metadata
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()
        
        # Calculate ability modifiers
        self._calculate_ability_modifiers()
        
        # Calculate proficiency bonus
        self._calculate_proficiency_bonus()
        
        # Update derived stats
        self._update_derived_stats()
        
        # Validate SRD compliance
        self._validate_srd_compliance()
    
    def _calculate_ability_modifiers(self):
        """Calculate ability modifiers using SRD 5E formula."""
        self.strength_mod = (self.strength - 10) // 2
        self.dexterity_mod = (self.dexterity - 10) // 2
        self.constitution_mod = (self.constitution - 10) // 2
        self.intelligence_mod = (self.intelligence - 10) // 2
        self.wisdom_mod = (self.wisdom - 10) // 2
        self.charisma_mod = (self.charisma - 10) // 2
    
    def _calculate_proficiency_bonus(self):
        """Calculate proficiency bonus based on level."""
        self.proficiency_bonus = ((self.level - 1) // 4) + 2
    
    def _update_derived_stats(self):
        """Update all derived statistics."""
        # Update saving throw modifiers
        self.saving_throws["strength"]["modifier"] = self.strength_mod
        self.saving_throws["dexterity"]["modifier"] = self.dexterity_mod
        self.saving_throws["constitution"]["modifier"] = self.constitution_mod
        self.saving_throws["intelligence"]["modifier"] = self.intelligence_mod
        self.saving_throws["wisdom"]["modifier"] = self.wisdom_mod
        self.saving_throws["charisma"]["modifier"] = self.charisma_mod
        
        # Update skill modifiers
        for skill_name, skill_data in self.skills.items():
            ability = skill_data["ability"]
            if ability == "strength":
                skill_data["modifier"] = self.strength_mod
            elif ability == "dexterity":
                skill_data["modifier"] = self.dexterity_mod
            elif ability == "constitution":
                skill_data["modifier"] = self.constitution_mod
            elif ability == "intelligence":
                skill_data["modifier"] = self.intelligence_mod
            elif ability == "wisdom":
                skill_data["modifier"] = self.wisdom_mod
            elif ability == "charisma":
                skill_data["modifier"] = self.charisma_mod
        
        # Update passive perception
        perception_modifier = self.skills["perception"]["modifier"]
        perception_proficiency = self.skills["perception"]["is_proficient"]
        self.passive_perception = 10 + perception_modifier
        if perception_proficiency:
            self.passive_perception += self.proficiency_bonus
    
    def _validate_srd_compliance(self):
        """Validate that all SRD-restricted fields contain valid values."""
        try:
            # Load SRD data for validation
            srd_data = self._load_srd_data()
            
            # Validate race
            if self.race and self.race not in srd_data.get('races', {}).get('races', {}):
                logger.warning(f"Invalid race: {self.race}")
            
            # Validate class
            if self.class_name and self.class_name not in srd_data.get('classes', {}).get('classes', {}):
                logger.warning(f"Invalid class: {self.class_name}")
            
            # Validate background
            if self.background and self.background not in srd_data.get('backgrounds', {}).get('backgrounds', {}):
                logger.warning(f"Invalid background: {self.background}")
            
            # Validate feats
            valid_feats = srd_data.get('feats', {}).get('feats', {}).keys()
            for feat in self.feats:
                if feat not in valid_feats:
                    logger.warning(f"Invalid feat: {feat}")
                    
        except Exception as e:
            logger.error(f"Error validating SRD compliance: {e}")
    
    def _load_srd_data(self) -> Dict[str, Any]:
        """Load SRD data for validation."""
        try:
            srd_data = {}
            srd_files = ['races.json', 'classes.json', 'backgrounds.json', 'feats.json']
            
            for filename in srd_files:
                try:
                    with open(f'srd_data/{filename}', 'r') as f:
                        srd_data[filename.replace('.json', '')] = json.load(f)
                except FileNotFoundError:
                    logger.warning(f"SRD file {filename} not found")
                    
            return srd_data
        except Exception as e:
            logger.error(f"Error loading SRD data: {e}")
            return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character sheet to dictionary format."""
        return {
            "metadata": {
                "version": "1.0.0",
                "created_date": self.created_date,
                "last_modified": self.last_modified,
                "creation_method": self.creation_method,
                "campaign_id": self.campaign_id
            },
            "basic_info": {
                "name": self.character_name,
                "player_name": self.player_name,
                "race": self.race,
                "class": self.class_name,
                "level": self.level,
                "background": self.background,
                "alignment": self.alignment,
                "experience_points": self.experience_points,
                "inspiration": self.inspiration,
                "proficiency_bonus": self.proficiency_bonus
            },
            "ability_scores": {
                "strength": self.strength,
                "dexterity": self.dexterity,
                "constitution": self.constitution,
                "intelligence": self.intelligence,
                "wisdom": self.wisdom,
                "charisma": self.charisma
            },
            "ability_modifiers": {
                "strength": self.strength_mod,
                "dexterity": self.dexterity_mod,
                "constitution": self.constitution_mod,
                "intelligence": self.intelligence_mod,
                "wisdom": self.wisdom_mod,
                "charisma": self.charisma_mod
            },
            "saving_throws": self.saving_throws,
            "skills": self.skills,
            "combat_stats": {
                "armor_class": self.armor_class,
                "initiative": self.initiative,
                "speed": self.speed,
                "hit_points_max": self.hit_points_max,
                "hit_points_current": self.hit_points_current,
                "temporary_hit_points": self.temporary_hit_points,
                "hit_dice_total": self.hit_dice_total,
                "hit_dice_remaining": self.hit_dice_remaining,
                "death_saves": self.death_saves,
                "passive_perception": self.passive_perception
            },
            "attacks": self.attacks,
            "spellcasting": self.spellcasting,
            "equipment": self.equipment,
            "currency": self.currency,
            "proficiencies": {
                "armor": self.armor_proficiencies,
                "weapons": self.weapon_proficiencies,
                "tools": self.tool_proficiencies,
                "languages": self.languages
            },
            "feats": self.feats,
            "personality": {
                "traits": self.personality_traits,
                "ideals": self.ideals,
                "bonds": self.bonds,
                "flaws": self.flaws
            },
            "features_and_traits": self.features_and_traits,
            "backstory": self.backstory,
            "appearance": {
                "description": self.character_appearance,
                "age": self.age,
                "height": self.height,
                "weight": self.weight,
                "eyes": self.eyes,
                "hair": self.hair,
                "skin": self.skin
            },
            "allies_and_organizations": self.allies_and_organizations,
            "faction_symbol": self.faction_symbol
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterSheet':
        """Create character sheet from dictionary data."""
        # TODO: Support mapping from vibe code - ensure all fields are writable
        # by future vibe code output without assuming interactive creation
        basic_info = data.get("basic_info", {})
        ability_scores = data.get("ability_scores", {})
        ability_modifiers = data.get("ability_modifiers", {})
        combat_stats = data.get("combat_stats", {})
        personality = data.get("personality", {})
        appearance = data.get("appearance", {})
        proficiencies = data.get("proficiencies", {})
        
        return cls(
            # Identity
            character_name=basic_info.get("name", ""),
            player_name=basic_info.get("player_name", ""),
            race=basic_info.get("race", ""),
            class_name=basic_info.get("class", ""),
            level=basic_info.get("level", 1),
            background=basic_info.get("background", ""),
            alignment=basic_info.get("alignment", "True Neutral"),
            experience_points=basic_info.get("experience_points", 0),
            inspiration=basic_info.get("inspiration", False),
            
            # Ability scores
            strength=ability_scores.get("strength", 10),
            dexterity=ability_scores.get("dexterity", 10),
            constitution=ability_scores.get("constitution", 10),
            intelligence=ability_scores.get("intelligence", 10),
            wisdom=ability_scores.get("wisdom", 10),
            charisma=ability_scores.get("charisma", 10),
            proficiency_bonus=basic_info.get("proficiency_bonus", 2),
            
            # Modifiers
            strength_mod=ability_modifiers.get("strength", 0),
            dexterity_mod=ability_modifiers.get("dexterity", 0),
            constitution_mod=ability_modifiers.get("constitution", 0),
            intelligence_mod=ability_modifiers.get("intelligence", 0),
            wisdom_mod=ability_modifiers.get("wisdom", 0),
            charisma_mod=ability_modifiers.get("charisma", 0),
            
            # Combat stats
            armor_class=combat_stats.get("armor_class", 10),
            initiative=combat_stats.get("initiative", 0),
            speed=combat_stats.get("speed", 30),
            hit_points_max=combat_stats.get("hit_points_max", 10),
            hit_points_current=combat_stats.get("hit_points_current", 10),
            temporary_hit_points=combat_stats.get("temporary_hit_points", 0),
            hit_dice_total=combat_stats.get("hit_dice_total", "1d8"),
            hit_dice_remaining=combat_stats.get("hit_dice_remaining", "1d8"),
            death_saves=combat_stats.get("death_saves", {"successes": 0, "failures": 0}),
            passive_perception=combat_stats.get("passive_perception", 10),
            
            # Other fields
            attacks=data.get("attacks", []),
            spellcasting=data.get("spellcasting", {}),
            equipment=data.get("equipment", []),
            currency=data.get("currency", {}),
            armor_proficiencies=proficiencies.get("armor", []),
            weapon_proficiencies=proficiencies.get("weapons", []),
            tool_proficiencies=proficiencies.get("tools", []),
            languages=proficiencies.get("languages", []),
            feats=data.get("feats", []),
            personality_traits=personality.get("traits", ""),
            ideals=personality.get("ideals", ""),
            bonds=personality.get("bonds", ""),
            flaws=personality.get("flaws", ""),
            features_and_traits=data.get("features_and_traits", []),
            backstory=data.get("backstory", ""),
            character_appearance=appearance.get("description", ""),
            allies_and_organizations=data.get("allies_and_organizations", []),
            faction_symbol=data.get("faction_symbol"),
            age=appearance.get("age", ""),
            height=appearance.get("height", ""),
            weight=appearance.get("weight", ""),
            eyes=appearance.get("eyes", ""),
            hair=appearance.get("hair", ""),
            skin=appearance.get("skin", ""),
            
            # Metadata
            created_date=data.get("metadata", {}).get("created_date", ""),
            creation_method=data.get("metadata", {}).get("creation_method", ""),
            campaign_id=data.get("metadata", {}).get("campaign_id")
        )
    
    def update_field(self, field_name: str, value: Any) -> bool:
        """Update a specific field and recalculate derived values."""
        if hasattr(self, field_name):
            setattr(self, field_name, value)
            self.last_modified = datetime.now().isoformat()
            
            # Recalculate derived values
            self._calculate_ability_modifiers()
            self._calculate_proficiency_bonus()
            self._update_derived_stats()
            
            return True
        return False
    
    def get_field_value(self, field_name: str) -> Any:
        """Get the value of a specific field."""
        return getattr(self, field_name, None)
    
    def validate_field(self, field_name: str, value: Any) -> tuple[bool, str]:
        """Validate a field value against SRD requirements."""
        try:
            srd_data = self._load_srd_data()
            
            if field_name == "race":
                valid_races = srd_data.get('races', {}).get('races', {}).keys()
                if value in valid_races:
                    return True, "Valid SRD race"
                else:
                    return False, f"Invalid race. Must be one of: {', '.join(valid_races)}"
            
            elif field_name == "class_name":
                valid_classes = srd_data.get('classes', {}).get('classes', {}).keys()
                if value in valid_classes:
                    return True, "Valid SRD class"
                else:
                    return False, f"Invalid class. Must be one of: {', '.join(valid_classes)}"
            
            elif field_name == "background":
                valid_backgrounds = srd_data.get('backgrounds', {}).get('backgrounds', {}).keys()
                if value in valid_backgrounds:
                    return True, "Valid SRD background"
                else:
                    return False, f"Invalid background. Must be one of: {', '.join(valid_backgrounds)}"
            
            elif field_name == "feats":
                if isinstance(value, list):
                    valid_feats = srd_data.get('feats', {}).get('feats', {}).keys()
                    invalid_feats = [feat for feat in value if feat not in valid_feats]
                    if not invalid_feats:
                        return True, "All feats are valid SRD feats"
                    else:
                        return False, f"Invalid feats: {', '.join(invalid_feats)}"
                else:
                    return False, "Feats must be a list"
            
            elif field_name == "alignment":
                valid_alignments = [align.value for align in Alignment]
                if value in valid_alignments:
                    return True, "Valid alignment"
                else:
                    return False, f"Invalid alignment. Must be one of: {', '.join(valid_alignments)}"
            
            elif field_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                if isinstance(value, int) and 1 <= value <= 20:
                    return True, "Valid ability score"
                else:
                    return False, "Ability score must be an integer between 1 and 20"
            
            elif field_name == "level":
                if isinstance(value, int) and 1 <= value <= 20:
                    return True, "Valid level"
                else:
                    return False, "Level must be an integer between 1 and 20"
            
            # For non-SRD restricted fields, accept any value
            return True, "Field validated"
            
        except Exception as e:
            logger.error(f"Error validating field {field_name}: {e}")
            return False, f"Validation error: {str(e)}" 