#!/usr/bin/env python3
"""
Enhanced Step-by-Step Character Creator for SoloHeart

Provides a comprehensive guided character creation experience using the full CharacterSheet class.
Includes all SRD 5.2 fields: ability scores, saving throws, skills, combat stats, equipment, feats, etc.
"""

import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import json

# Import the comprehensive CharacterSheet
try:
    from ..character_sheet import CharacterSheet, Alignment
    from ..ability_score_system import AbilityScoreSystem, AbilityScoreMethod
except ImportError:
    from character_sheet import CharacterSheet, Alignment
    from ability_score_system import AbilityScoreSystem, AbilityScoreMethod

logger = logging.getLogger(__name__)

class EnhancedStepByStepCreator:
    """
    Enhanced step-by-step character creation with comprehensive field coverage.
    
    Features:
    - Full CharacterSheet integration
    - Comprehensive ability score assignment
    - Saving throws and skills
    - Equipment and gear selection
    - Feat selection
    - Spellcasting details
    - SRD 5.2 compliance
    """
    
    def __init__(self, llm_service=None, on_complete_callback: Optional[Callable] = None):
        """
        Initialize the enhanced step-by-step character creator.
        
        Args:
            llm_service: LLM service for parsing natural language responses
            on_complete_callback: Callback function when character creation is complete
        """
        # Define comprehensive field groups
        self.field_groups = {
            "identity": [
                "character_name", "player_name", "race", "class_name", "level", 
                "background", "alignment", "age", "experience_points"
            ],
            "ability_scores": [
                "ability_score_method", "strength", "dexterity", "constitution", 
                "intelligence", "wisdom", "charisma"
            ],
            "combat_stats": [
                "hit_points", "armor_class", "initiative", "speed", "proficiency_bonus"
            ],
            "saving_throws": [
                "strength_save", "dexterity_save", "constitution_save", 
                "intelligence_save", "wisdom_save", "charisma_save"
            ],
            "skills": [
                "acrobatics", "animal_handling", "arcana", "athletics", "deception",
                "history", "insight", "intimidation", "investigation", "medicine",
                "nature", "perception", "performance", "persuasion", "religion",
                "sleight_of_hand", "stealth", "survival"
            ],
            "combat": [
                "attacks", "spellcasting_ability", "spell_slots", "spells_known"
            ],
            "equipment": [
                "equipment", "weapons", "armor", "currency", "treasure"
            ],
            "proficiencies": [
                "proficiencies", "languages", "feats", "class_features"
            ],
            "personality": [
                "personality_traits", "ideals", "bonds", "flaws", "backstory"
            ],
            "physical": [
                "height", "weight", "eyes", "hair", "skin", "distinguishing_features"
            ]
        }
        
        # Flatten all fields for sequential processing
        self.all_fields = []
        for group_name, fields in self.field_groups.items():
            self.all_fields.extend(fields)
        
        # For compatibility with main_app.py
        self.fields = self.all_fields
        
        # Initialize state
        self.state = {field: None for field in self.all_fields}
        self.state['ready_confirmed'] = False  # Track readiness state
        self.current_field_index = 0
        self.is_active = False
        self.current_group = None  # Will be set when we start
        
        # Services and callbacks
        self.llm_service = llm_service
        self.on_complete_callback = on_complete_callback
        
        # Initialize systems
        self.ability_system = AbilityScoreSystem()
        self.character_sheet = None
        
        # Field-specific prompts
        self.field_prompts = self._initialize_field_prompts()
        
        logger.info("EnhancedStepByStepCreator initialized")
    
    def _initialize_field_prompts(self) -> Dict[str, str]:
        """Initialize comprehensive field prompts."""
        return {
            # Identity fields
            "character_name": "What is your character's name?",
            "player_name": "What is your name (the player)?",
            "race": "What race is your character? (Human, Elf, Dwarf, etc.)",
            "class_name": "What class is your character? (Fighter, Wizard, etc.)",
            "level": "What level is your character? (default: 1)",
            "background": "What background does your character have?",
            "alignment": "What is your character's alignment?",
            "age": "How old is your character?",
            "experience_points": "How many experience points does your character have? (default: 0)",
            
            # Ability scores
            "ability_score_method": "How would you like to assign ability scores?\n1) Standard Array (15, 14, 13, 12, 10, 8)\n2) Point Buy (27 points)\n3) Optimal Assignment (AI assigns best for your class)",
            "strength": "What is your character's Strength score?",
            "dexterity": "What is your character's Dexterity score?",
            "constitution": "What is your character's Constitution score?",
            "intelligence": "What is your character's Intelligence score?",
            "wisdom": "What is your character's Wisdom score?",
            "charisma": "What is your character's Charisma score?",
            
            # Combat stats
            "hit_points": "What are your character's hit points?",
            "armor_class": "What is your character's armor class?",
            "initiative": "What is your character's initiative modifier?",
            "speed": "What is your character's movement speed?",
            "proficiency_bonus": "What is your character's proficiency bonus?",
            
            # Saving throws (will be auto-calculated, but can be overridden)
            "strength_save": "What is your character's Strength saving throw modifier?",
            "dexterity_save": "What is your character's Dexterity saving throw modifier?",
            "constitution_save": "What is your character's Constitution saving throw modifier?",
            "intelligence_save": "What is your character's Intelligence saving throw modifier?",
            "wisdom_save": "What is your character's Wisdom saving throw modifier?",
            "charisma_save": "What is your character's Charisma saving throw modifier?",
            
            # Skills (will be auto-calculated, but can be overridden)
            "acrobatics": "What is your character's Acrobatics skill modifier?",
            "animal_handling": "What is your character's Animal Handling skill modifier?",
            "arcana": "What is your character's Arcana skill modifier?",
            "athletics": "What is your character's Athletics skill modifier?",
            "deception": "What is your character's Deception skill modifier?",
            "history": "What is your character's History skill modifier?",
            "insight": "What is your character's Insight skill modifier?",
            "intimidation": "What is your character's Intimidation skill modifier?",
            "investigation": "What is your character's Investigation skill modifier?",
            "medicine": "What is your character's Medicine skill modifier?",
            "nature": "What is your character's Nature skill modifier?",
            "perception": "What is your character's Perception skill modifier?",
            "performance": "What is your character's Performance skill modifier?",
            "persuasion": "What is your character's Persuasion skill modifier?",
            "religion": "What is your character's Religion skill modifier?",
            "sleight_of_hand": "What is your character's Sleight of Hand skill modifier?",
            "stealth": "What is your character's Stealth skill modifier?",
            "survival": "What is your character's Survival skill modifier?",
            
            # Combat
            "attacks": "What weapons does your character use?",
            "spellcasting_ability": "What is your character's spellcasting ability? (Intelligence, Wisdom, or Charisma)",
            "spell_slots": "What spell slots does your character have?",
            "spells_known": "What spells does your character know?",
            
            # Equipment
            "equipment": "What equipment does your character carry?",
            "weapons": "What weapons does your character have?",
            "armor": "What armor does your character wear?",
            "currency": "How much money does your character have?",
            "treasure": "What treasure does your character possess?",
            
            # Proficiencies
            "proficiencies": "What proficiencies does your character have?",
            "languages": "What languages does your character speak?",
            "feats": "What feats does your character have?",
            "class_features": "What class features does your character have?",
            
            # Personality
            "personality_traits": "What are your character's personality traits?",
            "ideals": "What are your character's ideals?",
            "bonds": "What are your character's bonds?",
            "flaws": "What are your character's flaws?",
            "backstory": "What is your character's backstory?",
            
            # Physical description
            "height": "How tall is your character?",
            "weight": "How much does your character weigh?",
            "eyes": "What color are your character's eyes?",
            "hair": "What color/style is your character's hair?",
            "skin": "What color is your character's skin?",
            "distinguishing_features": "What distinguishing features does your character have?"
        }
    
    def start(self) -> str:
        """Start the enhanced character creation process."""
        self.is_active = True
        self.current_field_index = 0
        self.state = {field: None for field in self.all_fields}
        self.state['ready_confirmed'] = False  # Track readiness state
        
        logger.info("Starting enhanced step-by-step character creation")
        
        # Welcome message and readiness check
        welcome_message = """🎭 **Welcome to D&D 5E Character Creation!**

I'll guide you through creating your character step-by-step, covering all the essential elements:

• **Basic Information** (name, race, class, background)
• **Ability Scores** (strength, dexterity, constitution, etc.)
• **Combat Statistics** (hit points, armor class, initiative)
• **Skills & Proficiencies** (athletics, perception, languages, etc.)
• **Equipment & Gear** (weapons, armor, adventuring gear)
• **Personality & Background** (traits, ideals, bonds, flaws)

This process will ensure your character is fully SRD 5.2 compliant and ready for adventure!

Are you ready to begin creating your character? (Type 'yes' to start or 'no' to cancel)"""
        
        return welcome_message
    
    def process_response(self, user_input: str) -> str:
        """Process user response and advance to next field."""
        if not self.is_active:
            return "Character creation is not active. Use 'start' to begin."
        
        # Handle commands
        command_response = self._handle_commands(user_input)
        if command_response:
            return command_response
        
        # Check if we're in the initial readiness phase
        if not self.state.get('ready_confirmed'):
            user_input_lower = user_input.lower().strip()
            if user_input_lower in ['yes', 'y']:
                self.state['ready_confirmed'] = True
                # Now we can start asking for the first field
                return self._ask_next_field()
            elif user_input_lower in ['no', 'n', 'cancel', 'quit']:
                self.is_active = False
                return "Character creation cancelled."
            else:
                return "Are you ready to begin creating your character? (Type 'yes' to start or 'no' to cancel)"
        
        # Get current field
        if self.current_field_index >= len(self.all_fields):
            return self._complete_creation()
        
        current_field = self.all_fields[self.current_field_index]
        
        # Parse the response
        parsed_value = self._parse_response(current_field, user_input)
        
        if parsed_value is not None:
            self.state[current_field] = parsed_value
            logger.info(f"Set {current_field} to: {parsed_value}")
            
            # Move to next field
            self.current_field_index += 1
            
            # Check if we're done
            if self.current_field_index >= len(self.all_fields):
                return self._complete_creation()
            else:
                return self._ask_next_field()
        else:
            return f"I couldn't understand that response for {current_field}. Please try again or type 'help' for assistance."
    
    def _handle_commands(self, user_input: str) -> Optional[str]:
        """Handle user commands."""
        user_input_lower = user_input.lower().strip()
        
        if user_input_lower in ['help', '?']:
            return self._get_help()
        elif user_input_lower in ['summary', 'status']:
            return self._get_summary()
        elif user_input_lower.startswith('edit '):
            field_name = user_input_lower[5:].strip()
            return self._edit_field(field_name)
        elif user_input_lower in ['skip', 'default']:
            return self._skip_current_field()
        elif user_input_lower in ['back', 'previous']:
            return self._go_back()
        
        return None
    
    def _ask_next_field(self) -> str:
        """Ask about the next field."""
        if self.current_field_index >= len(self.all_fields):
            return self._complete_creation()
        
        current_field = self.all_fields[self.current_field_index]
        prompt = self.field_prompts.get(current_field, f"What is your character's {current_field}?")
        
        # Add group header if we're starting a new group
        current_group = self._get_field_group(current_field)
        if current_group != self.current_group:
            self.current_group = current_group
            group_header = f"\n📋 **{current_group.title()}**\n"
            prompt = group_header + prompt
        
        return prompt
    
    def _get_field_group(self, field: str) -> str:
        """Get the group name for a field."""
        for group_name, fields in self.field_groups.items():
            if field in fields:
                return group_name
        return "other"
    
    def _parse_response(self, field: str, user_input: str) -> Optional[Any]:
        """Parse user response for a specific field."""
        user_input = user_input.strip()
        
        # Handle special cases
        if field == "ability_score_method":
            return self._parse_ability_score_method(user_input)
        elif field in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            return self._parse_ability_score(field, user_input)
        elif field == "level":
            return self._parse_level(user_input)
        elif field == "alignment":
            return self._parse_alignment(user_input)
        elif field == "age":
            return self._parse_age(user_input)
        elif field == "experience_points":
            return self._parse_experience_points(user_input)
        elif field in ["hit_points", "armor_class", "initiative", "speed", "proficiency_bonus"]:
            return self._parse_numeric(field, user_input)
        elif field.endswith("_save") or field in self.field_groups["skills"]:
            return self._parse_modifier(field, user_input)
        else:
            # For most fields, just return the input as-is
            return user_input if user_input else None
    
    def _parse_ability_score_method(self, user_input: str) -> Optional[str]:
        """Parse ability score method selection."""
        user_input_lower = user_input.lower().strip()
        
        if user_input_lower in ['1', 'standard', 'standard array']:
            return 'standard_array'
        elif user_input_lower in ['2', 'point buy', 'pointbuy']:
            return 'point_buy'
        elif user_input_lower in ['3', 'optimal', 'optimal assignment']:
            return 'optimal_assignment'
        
        return None
    
    def _parse_ability_score(self, field: str, user_input: str) -> Optional[int]:
        """Parse ability score value."""
        try:
            score = int(user_input.strip())
            if 1 <= score <= 20:
                return score
        except ValueError:
            pass
        return None
    
    def _parse_level(self, user_input: str) -> Optional[int]:
        """Parse character level."""
        try:
            level = int(user_input.strip())
            if 1 <= level <= 20:
                return level
        except ValueError:
            pass
        return 1  # Default to level 1
    
    def _parse_alignment(self, user_input: str) -> Optional[str]:
        """Parse alignment."""
        user_input_lower = user_input.lower().strip()
        
        alignments = {
            'lawful good': 'Lawful Good',
            'neutral good': 'Neutral Good', 
            'chaotic good': 'Chaotic Good',
            'lawful neutral': 'Lawful Neutral',
            'neutral': 'True Neutral',
            'chaotic neutral': 'Chaotic Neutral',
            'lawful evil': 'Lawful Evil',
            'neutral evil': 'Neutral Evil',
            'chaotic evil': 'Chaotic Evil'
        }
        
        return alignments.get(user_input_lower)
    
    def _parse_age(self, user_input: str) -> Optional[int]:
        """Parse character age."""
        try:
            age = int(user_input.strip())
            if age > 0:
                return age
        except ValueError:
            pass
        return None
    
    def _parse_experience_points(self, user_input: str) -> Optional[int]:
        """Parse experience points."""
        try:
            xp = int(user_input.strip())
            if xp >= 0:
                return xp
        except ValueError:
            pass
        return 0  # Default to 0 XP
    
    def _parse_numeric(self, field: str, user_input: str) -> Optional[int]:
        """Parse numeric field."""
        try:
            value = int(user_input.strip())
            return value
        except ValueError:
            pass
        return None
    
    def _parse_modifier(self, field: str, user_input: str) -> Optional[int]:
        """Parse modifier field (saving throws, skills)."""
        try:
            modifier = int(user_input.strip())
            return modifier
        except ValueError:
            pass
        return None
    
    def _skip_current_field(self) -> str:
        """Skip the current field and move to the next."""
        if self.current_field_index >= len(self.all_fields):
            return self._complete_creation()
        
        current_field = self.all_fields[self.current_field_index]
        self.state[current_field] = None  # Set to None to indicate skipped
        
        self.current_field_index += 1
        return self._ask_next_field()
    
    def _go_back(self) -> str:
        """Go back to the previous field."""
        if self.current_field_index > 0:
            self.current_field_index -= 1
            return self._ask_next_field()
        else:
            return "You're at the beginning. There's no previous field to go back to."
    
    def _get_help(self) -> str:
        """Get help information."""
        return """
**Available Commands:**
- `help` or `?` - Show this help
- `summary` or `status` - Show current progress
- `edit <field>` - Edit a specific field
- `skip` or `default` - Skip current field
- `back` or `previous` - Go back to previous field

**Character Creation Progress:**
You're creating a comprehensive D&D 5E character with all fields including:
- Identity (name, race, class, etc.)
- Ability scores and modifiers
- Combat statistics
- Saving throws and skills
- Equipment and gear
- Proficiencies and feats
- Personality and backstory
- Physical description

Type your response to continue, or use a command above.
"""
    
    def _get_summary(self) -> str:
        """Get current progress summary."""
        completed_fields = [field for field, value in self.state.items() if value is not None]
        total_fields = len(self.all_fields)
        
        summary = f"""
**Character Creation Progress: {len(completed_fields)}/{total_fields} fields completed**

**Completed Fields:**
"""
        
        for group_name, fields in self.field_groups.items():
            group_completed = [field for field in fields if self.state.get(field) is not None]
            if group_completed:
                summary += f"\n**{group_name.title()}:**\n"
                for field in group_completed:
                    value = self.state[field]
                    summary += f"  • {field}: {value}\n"
        
        summary += f"\n**Current Field:** {self.all_fields[self.current_field_index] if self.current_field_index < len(self.all_fields) else 'Complete'}"
        
        return summary
    
    def _edit_field(self, field_name: str) -> str:
        """Edit a specific field."""
        if field_name in self.all_fields:
            # Find the field index
            try:
                field_index = self.all_fields.index(field_name)
                self.current_field_index = field_index
                return f"Editing {field_name}. Current value: {self.state[field_name]}\n{self._ask_next_field()}"
            except ValueError:
                return f"Field '{field_name}' not found."
        else:
            return f"Field '{field_name}' not found. Available fields: {', '.join(self.all_fields)}"
    
    def _complete_creation(self) -> str:
        """Complete the character creation process."""
        self.is_active = False
        
        # Create the CharacterSheet
        character_sheet = self._create_character_sheet()
        
        # Call completion callback
        if self.on_complete_callback:
            try:
                self.on_complete_callback(character_sheet)
            except Exception as e:
                logger.error(f"Error in completion callback: {e}")
        
        logger.info("Enhanced character creation completed")
        
        return f"""
🎉 **Character Creation Complete!**

Your comprehensive D&D 5E character is ready:

**Name:** {character_sheet.character_name}
**Race:** {character_sheet.race}
**Class:** {character_sheet.class_name}
**Level:** {character_sheet.level}
**Background:** {character_sheet.background}

**Ability Scores:**
• Strength: {character_sheet.strength} ({character_sheet.strength_mod:+d})
• Dexterity: {character_sheet.dexterity} ({character_sheet.dexterity_mod:+d})
• Constitution: {character_sheet.constitution} ({character_sheet.constitution_mod:+d})
• Intelligence: {character_sheet.intelligence} ({character_sheet.intelligence_mod:+d})
• Wisdom: {character_sheet.wisdom} ({character_sheet.wisdom_mod:+d})
• Charisma: {character_sheet.charisma} ({character_sheet.charisma_mod:+d})

**Combat Stats:**
• Hit Points: {character_sheet.hit_points_max}
• Armor Class: {character_sheet.armor_class}
• Initiative: {character_sheet.initiative:+d}
• Speed: {character_sheet.speed} ft.

**Equipment:** {', '.join(character_sheet.equipment) if character_sheet.equipment else 'None'}
**Feats:** {', '.join(character_sheet.feats) if character_sheet.feats else 'None'}

Your character is ready for adventure! 🗡️✨
"""
    
    def _create_character_sheet(self) -> CharacterSheet:
        """Create a complete CharacterSheet from the collected data."""
        # Handle ability scores
        ability_scores = self._calculate_ability_scores()
        
        # Create the character sheet with safe defaults for None values
        character_sheet = CharacterSheet(
            character_name=self.state.get('character_name') or 'Unknown',
            player_name=self.state.get('player_name') or 'Unknown',
            race=self.state.get('race') or 'Human',
            class_name=self.state.get('class_name') or 'Fighter',
            level=int(self.state.get('level') or 1),
            background=self.state.get('background') or 'Soldier',
            alignment=self.state.get('alignment') or 'True Neutral',
            experience_points=int(self.state.get('experience_points') or 0),
            
            # Ability scores (use individual fields, not dict)
            strength=ability_scores.get('strength', 10),
            dexterity=ability_scores.get('dexterity', 10),
            constitution=ability_scores.get('constitution', 10),
            intelligence=ability_scores.get('intelligence', 10),
            wisdom=ability_scores.get('wisdom', 10),
            charisma=ability_scores.get('charisma', 10),
            proficiency_bonus=int(self.state.get('proficiency_bonus') or 2),
            
            # Combat stats
            armor_class=int(self.state.get('armor_class') or 10),
            initiative=int(self.state.get('initiative') or 0),
            speed=int(self.state.get('speed') or 30),
            hit_points_max=int(self.state.get('hit_points') or 10),
            hit_points_current=int(self.state.get('hit_points') or 10),
            
            # Equipment and gear
            equipment=self.state.get('equipment', '').split(', ') if self.state.get('equipment') else [],
            
            # Proficiencies
            languages=self.state.get('languages', '').split(', ') if self.state.get('languages') else [],
            feats=self.state.get('feats', '').split(', ') if self.state.get('feats') else [],
            
            # Personality
            personality_traits=self.state.get('personality_traits', ''),
            ideals=self.state.get('ideals', ''),
            bonds=self.state.get('bonds', ''),
            flaws=self.state.get('flaws', ''),
            backstory=self.state.get('backstory', ''),
            
            # Physical description
            age=self.state.get('age', ''),
            height=self.state.get('height', ''),
            weight=self.state.get('weight', ''),
            eyes=self.state.get('eyes', ''),
            hair=self.state.get('hair', ''),
            skin=self.state.get('skin', ''),
            
            # Metadata
            created_date=datetime.now().isoformat(),
            creation_method='enhanced_step_by_step'
        )
        
        self.character_sheet = character_sheet
        return character_sheet
    
    def _calculate_ability_scores(self) -> Dict[str, int]:
        """Calculate ability scores based on method and class."""
        method = self.state.get('ability_score_method', 'optimal_assignment')
        character_class = self.state.get('class_name', 'Fighter')
        race = self.state.get('race', 'Human')
        
        # If user provided specific scores, use those
        if all(self.state.get(ability) is not None for ability in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']):
            return {
                'strength': self.state['strength'],
                'dexterity': self.state['dexterity'],
                'constitution': self.state['constitution'],
                'intelligence': self.state['intelligence'],
                'wisdom': self.state['wisdom'],
                'charisma': self.state['charisma']
            }
        
        # Otherwise, use the ability score system
        if method == 'standard_array':
            method_enum = AbilityScoreMethod.STANDARD_ARRAY
        elif method == 'point_buy':
            method_enum = AbilityScoreMethod.POINT_BUY
        else:
            method_enum = AbilityScoreMethod.OPTIMAL_ASSIGNMENT
        
        return self.ability_system.assign_ability_scores(method_enum, character_class, race)
    
    def get_current_progress(self) -> Dict:
        """Get current progress information."""
        return {
            'is_active': self.is_active,
            'current_field_index': self.current_field_index,
            'total_fields': len(self.all_fields),
            'completed_fields': len([f for f, v in self.state.items() if v is not None]),
            'current_field': self.all_fields[self.current_field_index] if self.current_field_index < len(self.all_fields) else None,
            'state': self.state
        }
    
    def reset(self) -> str:
        """Reset the character creation process."""
        self.is_active = False
        self.current_field_index = 0
        self.state = {field: None for field in self.all_fields}
        return "Character creation reset. Use 'start' to begin again."
    
    def restore_state(self, state: dict, current_field_index: int, is_active: bool):
        """Restore state from saved data."""
        self.state = state
        self.current_field_index = current_field_index
        self.is_active = is_active
        logger.info(f"Restored enhanced step-by-step state: field_index={current_field_index}, active={is_active}") 