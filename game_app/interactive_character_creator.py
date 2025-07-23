#!/usr/bin/env python3
"""
Interactive Character Creator for SoloHeart
Provides guided character creation with SRD 5.2 compliance and vibe code compatibility.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from .character_sheet import CharacterSheet, Alignment

logger = logging.getLogger(__name__)

class InteractiveCharacterCreator:
    """
    Interactive character creation system with SRD 5.2 compliance.
    
    Provides guided creation with options exploration, confirmation, and fallbacks.
    Fully compatible with future vibe code integration.
    """
    
    def __init__(self):
        self.character_sheet = CharacterSheet()
        self.srd_data = self._load_srd_data()
        self.current_step = 0
        self.completed_steps = set()
        self.creation_steps = [
            "identity",
            "ability_scores", 
            "class_features",
            "background",
            "equipment",
            "personality",
            "appearance",
            "finalize"
        ]
        
    def _load_srd_data(self) -> Dict[str, Any]:
        """Load SRD data for validation and options."""
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
    
    def get_current_step_info(self) -> Dict[str, Any]:
        """Get information about the current creation step."""
        if self.current_step >= len(self.creation_steps):
            return {"status": "complete", "message": "Character creation is complete!"}
            
        step = self.creation_steps[self.current_step]
        
        step_info = {
            "step": step,
            "step_number": self.current_step + 1,
            "total_steps": len(self.creation_steps),
            "status": "in_progress"
        }
        
        if step == "identity":
            step_info.update({
                "title": "Character Identity",
                "description": "Let's start with the basics of your character.",
                "fields": [
                    {"name": "character_name", "type": "text", "label": "Character Name", "required": True},
                    {"name": "player_name", "type": "text", "label": "Player Name", "required": False},
                    {"name": "race", "type": "select", "label": "Race", "required": True, "options": self._get_race_options()},
                    {"name": "class_name", "type": "select", "label": "Class", "required": True, "options": self._get_class_options()},
                    {"name": "level", "type": "number", "label": "Level", "required": True, "default": 1, "min": 1, "max": 20},
                    {"name": "alignment", "type": "select", "label": "Alignment", "required": True, "options": self._get_alignment_options()}
                ]
            })
        elif step == "ability_scores":
            step_info.update({
                "title": "Ability Scores",
                "description": "Choose how to assign your character's ability scores.",
                "fields": [
                    {"name": "method", "type": "select", "label": "Assignment Method", "required": True, "options": [
                        {"value": "standard_array", "label": "Standard Array (15, 14, 13, 12, 10, 8)"},
                        {"value": "point_buy", "label": "Point Buy (27 points, customize freely)"},
                        {"value": "optimal", "label": "Optimal Assignment (AI assigns best for your class)"}
                    ]}
                ]
            })
        elif step == "class_features":
            step_info.update({
                "title": "Class Features",
                "description": "Configure your character's class-specific features.",
                "fields": self._get_class_feature_fields()
            })
        elif step == "background":
            step_info.update({
                "title": "Background",
                "description": "Choose your character's background and story.",
                "fields": [
                    {"name": "background", "type": "select", "label": "Background", "required": True, "options": self._get_background_options()},
                    {"name": "personality_traits", "type": "text", "label": "Personality Traits", "required": False},
                    {"name": "ideals", "type": "text", "label": "Ideals", "required": False},
                    {"name": "bonds", "type": "text", "label": "Bonds", "required": False},
                    {"name": "flaws", "type": "text", "label": "Flaws", "required": False}
                ]
            })
        elif step == "equipment":
            step_info.update({
                "title": "Equipment & Proficiencies",
                "description": "Choose your character's equipment and proficiencies.",
                "fields": self._get_equipment_fields()
            })
        elif step == "personality":
            step_info.update({
                "title": "Personality & Story",
                "description": "Develop your character's personality and backstory.",
                "fields": [
                    {"name": "backstory", "type": "textarea", "label": "Backstory", "required": False},
                    {"name": "character_appearance", "type": "textarea", "label": "Physical Description", "required": False},
                    {"name": "allies_and_organizations", "type": "text", "label": "Allies & Organizations", "required": False}
                ]
            })
        elif step == "appearance":
            step_info.update({
                "title": "Physical Details",
                "description": "Add specific physical details about your character.",
                "fields": [
                    {"name": "age", "type": "text", "label": "Age", "required": False},
                    {"name": "height", "type": "text", "label": "Height", "required": False},
                    {"name": "weight", "type": "text", "label": "Weight", "required": False},
                    {"name": "eyes", "type": "text", "label": "Eye Color", "required": False},
                    {"name": "hair", "type": "text", "label": "Hair", "required": False},
                    {"name": "skin", "type": "text", "label": "Skin", "required": False}
                ]
            })
        elif step == "finalize":
            step_info.update({
                "title": "Finalize Character",
                "description": "Review and finalize your character.",
                "fields": []
            })
            
        return step_info
    
    def _get_race_options(self) -> List[Dict[str, str]]:
        """Get SRD race options with descriptions."""
        races = self.srd_data.get('races', {}).get('races', {})
        options = []
        
        for race_name, race_data in races.items():
            options.append({
                "value": race_name,
                "label": race_name,
                "description": race_data.get('description', ''),
                "ability_bonuses": race_data.get('ability_score_increases', {}),
                "features": [f["name"] for f in race_data.get('features', [])]
            })
            
        return options
    
    def _get_class_options(self) -> List[Dict[str, str]]:
        """Get SRD class options with descriptions."""
        classes = self.srd_data.get('classes', {}).get('classes', {})
        options = []
        
        for class_name, class_data in classes.items():
            options.append({
                "value": class_name,
                "label": class_name,
                "description": f"Hit Dice: {class_data.get('hit_dice', '1d8')}, Base HP: {class_data.get('base_hp', 8)}",
                "hit_dice": class_data.get('hit_dice', '1d8'),
                "base_hp": class_data.get('base_hp', 8),
                "spellcasting": class_data.get('spellcasting', False)
            })
            
        return options
    
    def _get_alignment_options(self) -> List[Dict[str, str]]:
        """Get alignment options."""
        return [
            {"value": "Lawful Good", "label": "Lawful Good"},
            {"value": "Neutral Good", "label": "Neutral Good"},
            {"value": "Chaotic Good", "label": "Chaotic Good"},
            {"value": "Lawful Neutral", "label": "Lawful Neutral"},
            {"value": "True Neutral", "label": "True Neutral"},
            {"value": "Chaotic Neutral", "label": "Chaotic Neutral"},
            {"value": "Lawful Evil", "label": "Lawful Evil"},
            {"value": "Neutral Evil", "label": "Neutral Evil"},
            {"value": "Chaotic Evil", "label": "Chaotic Evil"}
        ]
    
    def _get_background_options(self) -> List[Dict[str, str]]:
        """Get SRD background options with descriptions."""
        backgrounds = self.srd_data.get('backgrounds', {}).get('backgrounds', {})
        options = []
        
        for bg_name, bg_data in backgrounds.items():
            options.append({
                "value": bg_name,
                "label": bg_name,
                "description": bg_data.get('description', ''),
                "skill_proficiencies": bg_data.get('skill_proficiencies', []),
                "feature": bg_data.get('feature', {}).get('name', '')
            })
            
        return options
    
    def _get_class_feature_fields(self) -> List[Dict[str, Any]]:
        """Get class-specific feature fields based on selected class."""
        class_name = self.character_sheet.class_name
        if not class_name:
            return []
            
        fields = []
        
        # Get class data from SRD
        class_data = self.srd_data.get('classes', {}).get('classes', {}).get(class_name, {})
        
        # Add class-specific fields
        if class_name.lower() in ['wizard', 'sorcerer', 'warlock', 'bard', 'cleric', 'druid']:
            fields.append({
                "name": "spellcasting_ability",
                "type": "select",
                "label": "Spellcasting Ability",
                "required": True,
                "options": [
                    {"value": "intelligence", "label": "Intelligence (Wizard)"},
                    {"value": "wisdom", "label": "Wisdom (Cleric, Druid)"},
                    {"value": "charisma", "label": "Charisma (Sorcerer, Warlock, Bard)"}
                ]
            })
        
        # Add proficiency fields
        proficiencies = class_data.get('proficiencies', {})
        
        if 'armor' in proficiencies:
            fields.append({
                "name": "armor_proficiencies",
                "type": "multiselect",
                "label": "Armor Proficiencies",
                "required": False,
                "options": [{"value": armor, "label": armor.title()} for armor in proficiencies['armor']],
                "default": proficiencies['armor']
            })
        
        if 'weapons' in proficiencies:
            fields.append({
                "name": "weapon_proficiencies",
                "type": "multiselect",
                "label": "Weapon Proficiencies",
                "required": False,
                "options": [{"value": weapon, "label": weapon.title()} for weapon in proficiencies['weapons']],
                "default": proficiencies['weapons']
            })
        
        # Add saving throw proficiencies
        if 'saving_throws' in proficiencies:
            fields.append({
                "name": "saving_throw_proficiencies",
                "type": "multiselect",
                "label": "Saving Throw Proficiencies",
                "required": False,
                "options": [{"value": save, "label": save} for save in proficiencies['saving_throws']],
                "default": proficiencies['saving_throws']
            })
        
        # Add class features
        features = class_data.get('features', [])
        if features:
            fields.append({
                "name": "class_features",
                "type": "info",
                "label": "Class Features",
                "required": False,
                "description": "\n".join([f"• {f['name']} (Level {f['level']}): {f['description']}" for f in features])
            })
            
        return fields
    
    def _get_equipment_fields(self) -> List[Dict[str, Any]]:
        """Get equipment and proficiency fields."""
        class_name = self.character_sheet.class_name
        class_data = self.srd_data.get('classes', {}).get('classes', {}).get(class_name, {})
        
        fields = [
            {"name": "starting_equipment", "type": "select", "label": "Starting Equipment", "required": True, "options": [
                {"value": "class_package", "label": "Class Equipment Package (Recommended)"},
                {"value": "custom", "label": "Custom Equipment (using starting gold)"}
            ]},
            {"name": "starting_gold", "type": "number", "label": "Starting Gold (if custom)", "required": False, "min": 0, "max": 1000, "default": 100}
        ]
        
        # Add class-specific equipment options
        if class_name:
            fields.append({
                "name": "class_equipment_info",
                "type": "info",
                "label": f"{class_name} Equipment",
                "required": False,
                "description": f"Hit Dice: {class_data.get('hit_dice', '1d8')}\nBase HP: {class_data.get('base_hp', 8)}"
            })
        
        # Add background equipment
        background = self.character_sheet.background
        if background:
            bg_data = self.srd_data.get('backgrounds', {}).get('backgrounds', {}).get(background, {})
            equipment = bg_data.get('equipment', [])
            if equipment:
                fields.append({
                    "name": "background_equipment",
                    "type": "info",
                    "label": f"{background} Background Equipment",
                    "required": False,
                    "description": "\n".join([f"• {item}" for item in equipment])
                })
        
        return fields
    
    def process_step_input(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input for the current step and validate it."""
        current_step = self.creation_steps[self.current_step]
        validation_results = {}
        
        for field_name, value in field_data.items():
            is_valid, message = self._validate_field(current_step, field_name, value)
            validation_results[field_name] = {
                "valid": is_valid,
                "message": message,
                "value": value
            }
            
            if is_valid:
                # Update character sheet
                self._update_character_field(field_name, value)
        
        # Check if all required fields are valid
        step_info = self.get_current_step_info()
        required_fields = [f["name"] for f in step_info.get("fields", []) if f.get("required", False)]
        all_required_valid = all(
            validation_results.get(field, {}).get("valid", False) 
            for field in required_fields
        )
        
        return {
            "step": current_step,
            "validation_results": validation_results,
            "all_required_valid": all_required_valid,
            "can_proceed": all_required_valid
        }
    
    def _validate_field(self, step: str, field_name: str, value: Any) -> tuple[bool, str]:
        """Validate a field value against SRD requirements."""
        if step == "identity":
            if field_name == "race":
                return self._validate_srd_option("races", "races", value)
            elif field_name == "class_name":
                return self._validate_srd_option("classes", "classes", value)
            elif field_name == "level":
                return self._validate_number_range(value, 1, 20)
            elif field_name == "alignment":
                return self._validate_alignment(value)
        elif step == "background":
            if field_name == "background":
                return self._validate_srd_option("backgrounds", "backgrounds", value)
        elif step == "ability_scores":
            if field_name == "method":
                return self._validate_ability_method(value)
                
        return True, "Valid"
    
    def _validate_srd_option(self, data_key: str, sub_key: str, value: str) -> tuple[bool, str]:
        """Validate that a value is a valid SRD option."""
        data = self.srd_data.get(data_key, {}).get(sub_key, {})
        if value in data:
            return True, "Valid SRD option"
        else:
            return False, f"Invalid {data_key[:-1]}. Must be one of: {', '.join(data.keys())}"
    
    def _validate_number_range(self, value: Any, min_val: int, max_val: int) -> tuple[bool, str]:
        """Validate a number is within range."""
        try:
            num_val = int(value)
            if min_val <= num_val <= max_val:
                return True, "Valid"
            else:
                return False, f"Must be between {min_val} and {max_val}"
        except (ValueError, TypeError):
            return False, "Must be a valid number"
    
    def _validate_alignment(self, value: str) -> tuple[bool, str]:
        """Validate alignment value."""
        valid_alignments = [a.value for a in Alignment]
        if value in valid_alignments:
            return True, "Valid alignment"
        else:
            return False, f"Invalid alignment. Must be one of: {', '.join(valid_alignments)}"
    
    def _validate_ability_method(self, value: str) -> tuple[bool, str]:
        """Validate ability score assignment method."""
        valid_methods = ["standard_array", "point_buy", "optimal"]
        if value in valid_methods:
            return True, "Valid method"
        else:
            return False, f"Invalid method. Must be one of: {', '.join(valid_methods)}"
    
    def _update_character_field(self, field_name: str, value: Any):
        """Update a field in the character sheet."""
        if hasattr(self.character_sheet, field_name):
            setattr(self.character_sheet, field_name, value)
            logger.info(f"Updated {field_name} to {value}")
    
    def advance_step(self) -> bool:
        """Advance to the next creation step."""
        if self.current_step < len(self.creation_steps) - 1:
            self.completed_steps.add(self.creation_steps[self.current_step])
            self.current_step += 1
            return True
        return False
    
    def go_back_step(self) -> bool:
        """Go back to the previous creation step."""
        if self.current_step > 0:
            self.current_step -= 1
            return True
        return False
    
    def get_help_for_field(self, field_name: str) -> Dict[str, Any]:
        """Get help information for a specific field."""
        help_info = {
            "field": field_name,
            "description": "",
            "examples": [],
            "tips": []
        }
        
        if field_name == "race":
            help_info.update({
                "description": "Your character's race determines their ancestry and provides racial traits.",
                "examples": ["Human", "Elf", "Dwarf", "Halfling"],
                "tips": [
                    "Consider the racial ability score bonuses when choosing your class",
                    "Each race has unique features that can complement your playstyle",
                    "Some races have subraces with additional options"
                ]
            })
        elif field_name == "class_name":
            help_info.update({
                "description": "Your character's class defines their primary abilities and role in the party.",
                "examples": ["Fighter", "Wizard", "Cleric", "Rogue"],
                "tips": [
                    "Choose a class that matches your desired playstyle",
                    "Consider the party composition when selecting your class",
                    "Each class has different hit dice and armor proficiencies"
                ]
            })
        elif field_name == "ability_scores":
            help_info.update({
                "description": "Ability scores represent your character's basic attributes.",
                "examples": ["Standard Array: 15, 14, 13, 12, 10, 8", "Point Buy: 27 points to distribute"],
                "tips": [
                    "Standard Array is balanced and beginner-friendly",
                    "Point Buy allows for customization but requires careful planning",
                    "Optimal assignment automatically assigns the best scores for your class"
                ]
            })
            
        return help_info
    
    def get_suggestion_for_field(self, field_name: str, context: str = "") -> str:
        """Get a suggestion for a field based on context."""
        if field_name == "class_name" and context == "beginner":
            return "For beginners, I recommend the Fighter class. It's straightforward to play, has good survivability, and doesn't require managing complex spell systems."
        elif field_name == "race" and context == "beginner":
            return "For beginners, I recommend the Human race. They get +1 to all ability scores, making them versatile and forgiving for any class choice."
        elif field_name == "background" and context == "beginner":
            return "For beginners, I recommend the Soldier background. It's straightforward and provides useful skill proficiencies for combat-focused characters."
        else:
            return "Choose what feels right for your character concept. Don't worry too much about optimization - the most important thing is that you enjoy playing your character!"
    
    def handle_user_question(self, field_name: str, question: str) -> str:
        """Handle user questions about field options."""
        question_lower = question.lower()
        
        if field_name == "race":
            if "difference" in question_lower or "compare" in question_lower:
                return self._compare_race_options(question)
            elif "beginner" in question_lower or "easy" in question_lower:
                return "For beginners, I recommend Human or Half-Elf. Humans get +1 to all ability scores, making them versatile. Half-Elves get +2 Charisma and +1 to two other abilities, plus darkvision and other useful features."
            elif "strong" in question_lower or "combat" in question_lower:
                return "For combat-focused characters, consider Half-Orc (+2 Strength, +1 Constitution) or Mountain Dwarf (+2 Strength, +2 Constitution). Both provide excellent physical attributes for martial classes."
            else:
                return self._get_race_summary()
        
        elif field_name == "class_name":
            if "difference" in question_lower or "compare" in question_lower:
                return self._compare_class_options(question)
            elif "beginner" in question_lower or "easy" in question_lower:
                return "For beginners, I recommend Fighter or Cleric. Fighters are straightforward with good survivability. Clerics are versatile with healing and combat abilities."
            elif "magic" in question_lower or "spells" in question_lower:
                return "For spellcasting, consider Wizard (Intelligence-based, most spells), Sorcerer (Charisma-based, flexible casting), or Cleric (Wisdom-based, divine magic)."
            else:
                return self._get_class_summary()
        
        elif field_name == "background":
            if "difference" in question_lower or "compare" in question_lower:
                return self._compare_background_options(question)
            elif "beginner" in question_lower:
                return "For beginners, I recommend Soldier or Folk Hero. Soldier provides combat-related skills, while Folk Hero gives you a connection to common people."
            else:
                return self._get_background_summary()
        
        return f"I can help you with questions about {field_name}. What specifically would you like to know?"
    
    def get_fallback_option(self, field_name: str) -> str:
        """Get a fallback option when user says 'I don't know'."""
        import random
        
        if field_name == "race":
            races = list(self.srd_data.get('races', {}).get('races', {}).keys())
            return random.choice(races)
        
        elif field_name == "class_name":
            classes = list(self.srd_data.get('classes', {}).get('classes', {}).keys())
            return random.choice(classes)
        
        elif field_name == "background":
            backgrounds = list(self.srd_data.get('backgrounds', {}).get('backgrounds', {}).keys())
            return random.choice(backgrounds)
        
        elif field_name == "alignment":
            alignments = ["True Neutral", "Neutral Good", "Chaotic Good"]
            return random.choice(alignments)
        
        elif field_name == "ability_scores":
            return "optimal"  # Default to optimal assignment
        
        return "Unknown field"
    
    def confirm_value(self, field_name: str, value: str) -> str:
        """Generate a confirmation prompt for a value."""
        if field_name == "race":
            race_data = self.srd_data.get('races', {}).get('races', {}).get(value, {})
            description = race_data.get('description', '')
            return f"Confirm {value} as your race?\n\n{description}\n\nType 'yes' to confirm or 'no' to choose again."
        
        elif field_name == "class_name":
            class_data = self.srd_data.get('classes', {}).get('classes', {}).get(value, {})
            hit_dice = class_data.get('hit_dice', '1d8')
            base_hp = class_data.get('base_hp', 8)
            return f"Confirm {value} as your class?\n\nHit Dice: {hit_dice}\nBase HP: {base_hp}\n\nType 'yes' to confirm or 'no' to choose again."
        
        elif field_name == "background":
            bg_data = self.srd_data.get('backgrounds', {}).get('backgrounds', {}).get(value, {})
            description = bg_data.get('description', '')
            return f"Confirm {value} as your background?\n\n{description}\n\nType 'yes' to confirm or 'no' to choose again."
        
        else:
            return f"Confirm '{value}' for {field_name}? Type 'yes' to confirm or 'no' to choose again."
    
    def _compare_race_options(self, question: str) -> str:
        """Compare race options based on the question."""
        if "elf" in question.lower() and "human" in question.lower():
            return "Elves get +2 Dexterity, darkvision, and long lifespans. Humans get +1 to all ability scores, making them more versatile. Elves are great for dexterity-based classes, while Humans work well with any class."
        elif "dwarf" in question.lower():
            return "Dwarves get +2 Constitution and resistance to poison. Hill Dwarves get +1 Wisdom, Mountain Dwarves get +2 Strength. Great for tough, durable characters."
        elif "halfling" in question.lower():
            return "Halflings get +2 Dexterity, are small-sized, and have the Lucky trait (reroll 1s on d20 rolls). Great for dexterity-based classes like Rogues."
        else:
            return self._get_race_summary()
    
    def _compare_class_options(self, question: str) -> str:
        """Compare class options based on the question."""
        if "fighter" in question.lower() and "barbarian" in question.lower():
            return "Fighters are versatile warriors with multiple attacks and fighting styles. Barbarians are fierce warriors who can enter a rage for extra damage and damage resistance. Fighters are more tactical, Barbarians are more aggressive."
        elif "wizard" in question.lower() and "sorcerer" in question.lower():
            return "Wizards learn spells from scrolls and spellbooks, have the largest spell selection, and use Intelligence. Sorcerers have innate magic, use Charisma, and can modify spells with metamagic. Wizards are more versatile, Sorcerers are more flexible with their spells."
        else:
            return self._get_class_summary()
    
    def _compare_background_options(self, question: str) -> str:
        """Compare background options based on the question."""
        if "soldier" in question.lower() and "criminal" in question.lower():
            return "Soldier provides combat-related skills and a military background. Criminal provides stealth and deception skills for a more rogue-like character. Choose based on your character's past."
        else:
            return self._get_background_summary()
    
    def _get_race_summary(self) -> str:
        """Get a summary of all race options."""
        races = self.srd_data.get('races', {}).get('races', {})
        summary = "Available races:\n"
        for race_name, race_data in races.items():
            bonuses = race_data.get('ability_score_increases', {})
            bonus_text = ", ".join([f"+{bonus} {ability.title()}" for ability, bonus in bonuses.items()])
            summary += f"- {race_name}: {bonus_text}\n"
        return summary
    
    def _get_class_summary(self) -> str:
        """Get a summary of all class options."""
        classes = self.srd_data.get('classes', {}).get('classes', {})
        summary = "Available classes:\n"
        for class_name, class_data in classes.items():
            hit_dice = class_data.get('hit_dice', '1d8')
            summary += f"- {class_name}: {hit_dice} hit dice\n"
        return summary
    
    def _get_background_summary(self) -> str:
        """Get a summary of all background options."""
        backgrounds = self.srd_data.get('backgrounds', {}).get('backgrounds', {})
        summary = "Available backgrounds:\n"
        for bg_name, bg_data in backgrounds.items():
            skills = bg_data.get('skill_proficiencies', [])
            skill_text = ", ".join(skills) if skills else "None"
            summary += f"- {bg_name}: {skill_text} skills\n"
        return summary
    
    def finalize_character(self) -> CharacterSheet:
        """Finalize the character creation process."""
        # TODO: Support mapping from vibe code
        # Apply any final calculations and validations
        self.character_sheet._update_derived_stats()
        self.character_sheet._validate_srd_compliance()
        
        return self.character_sheet
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Get a summary of the current character state."""
        return {
            "basic_info": {
                "name": self.character_sheet.character_name,
                "race": self.character_sheet.race,
                "class": self.character_sheet.class_name,
                "level": self.character_sheet.level,
                "background": self.character_sheet.background,
                "alignment": self.character_sheet.alignment
            },
            "ability_scores": {
                "strength": self.character_sheet.strength,
                "dexterity": self.character_sheet.dexterity,
                "constitution": self.character_sheet.constitution,
                "intelligence": self.character_sheet.intelligence,
                "wisdom": self.character_sheet.wisdom,
                "charisma": self.character_sheet.charisma
            },
            "ability_modifiers": {
                "strength": self.character_sheet.strength_mod,
                "dexterity": self.character_sheet.dexterity_mod,
                "constitution": self.character_sheet.constitution_mod,
                "intelligence": self.character_sheet.intelligence_mod,
                "wisdom": self.character_sheet.wisdom_mod,
                "charisma": self.character_sheet.charisma_mod
            },
            "progress": {
                "current_step": self.current_step,
                "total_steps": len(self.creation_steps),
                "completed_steps": list(self.completed_steps)
            }
        }
    
    def process_interactive_input(self, user_input: str) -> Dict[str, Any]:
        """Process interactive user input with support for questions, suggestions, and fallbacks."""
        user_input_lower = user_input.lower().strip()
        
        # Handle special commands
        if user_input_lower in ['help', '?']:
            return {
                "type": "help",
                "message": "You can:\n- Ask questions about options (e.g., 'What's the difference between Fighter and Barbarian?')\n- Ask for suggestions (e.g., 'What's good for a beginner?')\n- Say 'I don't know' for a random choice\n- Type 'yes' to confirm or 'no' to choose again\n- Provide a direct answer"
            }
        
        elif user_input_lower in ['i don\'t know', 'i dont know', 'dunno', 'random']:
            current_step = self.creation_steps[self.current_step]
            fallback = self.get_fallback_option(current_step)
            return {
                "type": "fallback",
                "field": current_step,
                "value": fallback,
                "message": f"I'll choose '{fallback}' for you. Type 'yes' to confirm or 'no' to choose something else."
            }
        
        elif user_input_lower in ['yes', 'confirm', 'ok', 'sure']:
            return {
                "type": "confirmation",
                "message": "Confirmed! Moving to the next step."
            }
        
        elif user_input_lower in ['no', 'nope', 'choose again']:
            return {
                "type": "rejection",
                "message": "No problem! Let's choose again."
            }
        
        # Handle questions
        elif any(word in user_input_lower for word in ['what', 'how', 'why', 'difference', 'compare', 'beginner', 'suggestion']):
            current_step = self.creation_steps[self.current_step]
            response = self.handle_user_question(current_step, user_input)
            return {
                "type": "question_response",
                "message": response
            }
        
        # Handle direct input
        else:
            current_step = self.creation_steps[self.current_step]
            is_valid, message = self._validate_field(current_step, current_step, user_input)
            
            if is_valid:
                return {
                    "type": "confirmation_request",
                    "field": current_step,
                    "value": user_input,
                    "message": self.confirm_value(current_step, user_input)
                }
            else:
                return {
                    "type": "validation_error",
                    "message": f"Invalid input: {message}\n\nPlease try again or ask for help."
                }
    
    def get_current_prompt(self) -> str:
        """Get the current prompt for the user."""
        current_step = self.creation_steps[self.current_step]
        step_info = self.get_current_step_info()
        
        prompt = f"\n🎭 {step_info['title']}\n"
        prompt += f"{step_info['description']}\n\n"
        
        if current_step == "identity":
            prompt += "What would you like to do?\n"
            prompt += "• Type a race name (e.g., 'Human', 'Elf')\n"
            prompt += "• Ask a question (e.g., 'What's the difference between Human and Elf?')\n"
            prompt += "• Ask for a suggestion (e.g., 'What's good for a beginner?')\n"
            prompt += "• Say 'I don't know' for a random choice\n"
            prompt += "• Type 'help' for more options\n\n"
            prompt += "Your choice: "
        
        elif current_step == "ability_scores":
            prompt += "How would you like to assign your ability scores?\n"
            prompt += "1) Standard Array (15, 14, 13, 12, 10, 8) - Balanced and beginner-friendly\n"
            prompt += "2) Point Buy (27 points) - Customize freely\n"
            prompt += "3) Optimal Assignment - AI assigns best scores for your class\n\n"
            prompt += "Type '1', '2', or '3', or ask for help: "
        
        elif current_step == "background":
            prompt += "What background does your character have?\n"
            prompt += "• Type a background name (e.g., 'Soldier', 'Acolyte')\n"
            prompt += "• Ask about backgrounds (e.g., 'What backgrounds are good for beginners?')\n"
            prompt += "• Say 'I don't know' for a random choice\n\n"
            prompt += "Your choice: "
        
        else:
            prompt += "Please provide your input or ask for help: "
        
        return prompt 