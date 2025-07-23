#!/usr/bin/env python3
"""
Step-by-Step Character Creator for SoloHeart

Provides a guided, question-by-question character creation experience.
The player is asked one field at a time, and each answer is processed via LLM
to infer structured values. The flow is stateful, interpretable, and interruptible.
"""

import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class StepByStepCharacterCreator:
    """
    Guided character creation that asks one question at a time.
    
    Features:
    - Field-by-field prompting with clear field identification
    - Natural language response parsing via LLM
    - State tracking with skip logic for filled fields
    - User control commands (summary, edit, continue)
    - Graceful resumption and interruption handling
    """
    
    def __init__(self, llm_service=None, on_complete_callback: Optional[Callable] = None):
        """
        Initialize the step-by-step character creator.
        
        Args:
            llm_service: LLM service for parsing natural language responses
            on_complete_callback: Callback function when character creation is complete
        """
        # Define fields in order of collection
        self.fields = [
            "race", "class", "gender", "age", "background", 
            "personality", "level", "alignment", "name", "ability_scores"
        ]
        
        # Initialize state
        self.state = {field: None for field in self.fields}
        self.current_field_index = 0
        self.is_active = False
        
        # Services and callbacks
        self.llm_service = llm_service
        self.on_complete_callback = on_complete_callback
        
        # Field-specific prompts and validation
        self.field_prompts = {
            "race": "Let's start with your character's *race*. What kind of ancestry do they have?",
            "class": "Next up: what *class* do they belong to? Fighter? Wizard? Something more unusual?",
            "gender": "What's your character's *gender*?",
            "age": "How old is your character?",
            "background": "What's their *background*? Where did they come from?",
            "personality": "How would you describe their *personality*?",
            "level": "What *level* are they starting at? (default is 1)",
            "alignment": "What's their *alignment*? (optional - can skip with 'skip')",
            "name": "What's your character's *name*?",
            "ability_scores": "How would you like to assign your *ability scores*? Choose from:\n1) Standard Array (15, 14, 13, 12, 10, 8)\n2) Point Buy (27 points, customize freely)\n3) Optimal Assignment (AI assigns best scores for your class)"
        }
        
        # Field-specific parsing hints
        self.field_hints = {
            "race": "Common races: Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling",
            "class": "Common classes: Fighter, Wizard, Cleric, Rogue, Ranger, Paladin, Barbarian, Bard, Druid, Monk, Sorcerer, Warlock",
            "gender": "Male, Female, Non-Binary, or any other identity",
            "age": "A number representing their age in years",
            "background": "Acolyte, Criminal, Folk Hero, Haunted One, Noble, Sage, Soldier, Urchin, or custom",
            "personality": "Traits like brave, cautious, friendly, mysterious, wise, etc.",
            "level": "A number from 1-20 (defaults to 1)",
            "alignment": "Lawful Good, Neutral Good, Chaotic Good, Lawful Neutral, Neutral, Chaotic Neutral, Lawful Evil, Neutral Evil, Chaotic Evil",
            "name": "Your character's full name",
            "ability_scores": "Type '1' for Standard Array, '2' for Point Buy, or '3' for Optimal Assignment"
        }
        
        logger.info("StepByStepCharacterCreator initialized")
    
    def start(self) -> str:
        """
        Start the step-by-step character creation process.
        
        Returns:
            str: The first prompt asking about the first field
        """
        self.is_active = True
        self.current_field_index = 0
        self.state = {field: None for field in self.fields}
        
        logger.info("Starting step-by-step character creation")
        return self._ask_next_field()
    
    def process_response(self, user_input: str) -> str:
        """
        Process a user's response and advance to the next field.
        
        Args:
            user_input: The user's response to the current field question
            
        Returns:
            str: The next prompt or completion message
        """
        if not self.is_active:
            return "Character creation is not active. Use .start() to begin."
        
        # Check for control commands first
        command_response = self._handle_commands(user_input)
        if command_response:
            return command_response
        
        # Check if we're done
        if self.current_field_index >= len(self.fields):
            return "Character creation is already complete! Use 'summary' to see your character or 'reset' to start over."
        
        # Get current field
        current_field = self.fields[self.current_field_index]
        
        # Parse the user's response for the current field
        parsed_value = self._parse_response(current_field, user_input)
        logger.info(f"Parsing '{user_input}' for field '{current_field}' -> result: {parsed_value}")
        
        if parsed_value:
            # Store the parsed value
            self.state[current_field] = parsed_value
            logger.info(f"Set {current_field} to: {parsed_value}")
            
            # Move to next field
            self.current_field_index += 1
            
            # Check if we're done
            if self.current_field_index >= len(self.fields):
                return self._complete_creation()
            else:
                return self._ask_next_field()
        else:
            # Couldn't parse the response, ask again
            return f"I didn't quite understand that. {self._ask_next_field()}"
    
    def _handle_commands(self, user_input: str) -> Optional[str]:
        """
        Handle user control commands.
        
        Args:
            user_input: The user's input
            
        Returns:
            Optional[str]: Response to command, or None if not a command
        """
        input_lower = user_input.lower().strip()
        
        # Summary command
        if input_lower in ['summary', 'status', 'show']:
            return self._get_summary()
        
        # Edit command
        if input_lower.startswith('edit '):
            field_to_edit = input_lower[5:].strip()
            return self._edit_field(field_to_edit)
        
        # Continue command
        if input_lower in ['continue', 'next', 'skip']:
            return self._continue_to_next()
        
        # Help command
        if input_lower in ['help', '?']:
            return self._get_help()
        
        # Reset command
        if input_lower in ['reset', 'start over']:
            return self.start()
        
        return None
    
    def _get_summary(self) -> str:
        """Get a summary of current progress."""
        filled_fields = []
        empty_fields = []
        
        for field in self.fields:
            if self.state[field]:
                filled_fields.append(f"• {field.title()}: {self.state[field]}")
            else:
                empty_fields.append(f"• {field.title()}")
        
        summary = "**Current Character Progress:**\n\n"
        
        if filled_fields:
            summary += "**Completed:**\n" + "\n".join(filled_fields) + "\n\n"
        
        if empty_fields:
            summary += "**Remaining:**\n" + "\n".join(empty_fields) + "\n\n"
        
        # Check if we're still in bounds
        if self.current_field_index < len(self.fields):
            summary += f"Currently asking about: **{self.fields[self.current_field_index].title()}**"
        else:
            summary += "**Character creation complete!**"
        
        return summary
    
    def _edit_field(self, field_name: str) -> str:
        """
        Edit a specific field.
        
        Args:
            field_name: The field to edit
            
        Returns:
            str: Response message
        """
        field_name = field_name.lower()
        
        if field_name not in self.fields:
            return f"Unknown field '{field_name}'. Available fields: {', '.join(self.fields)}"
        
        # Find the field index
        field_index = self.fields.index(field_name)
        
        # Clear the field and move to it
        self.state[field_name] = None
        self.current_field_index = field_index
        
        return f"Let's edit your character's {field_name}. {self._ask_next_field()}"
    
    def _continue_to_next(self) -> str:
        """Skip the current field and continue to the next."""
        current_field = self.fields[self.current_field_index]
        
        # Set a default value for the current field
        default_value = self._get_default_value(current_field)
        self.state[current_field] = default_value
        
        logger.info(f"Skipped {current_field}, set to default: {default_value}")
        
        # Move to next field
        self.current_field_index += 1
        
        if self.current_field_index >= len(self.fields):
            return self._complete_creation()
        else:
            return self._ask_next_field()
    
    def _get_default_value(self, field: str) -> str:
        """Get default value for a field when skipped."""
        defaults = {
            "level": "1",
            "alignment": "Neutral",
            "age": "25",
            "personality": "Balanced"
        }
        return defaults.get(field, "Unknown")
    
    def _get_help(self) -> str:
        """Get help information."""
        help_text = """
**Step-by-Step Character Creation Help**

**Commands:**
• `summary` - Show current progress
• `edit <field>` - Edit a specific field (e.g., `edit race`)
• `continue` - Skip current field and continue
• `help` - Show this help message
• `reset` - Start over

**Current Field:** """ + self.fields[self.current_field_index].title()

        return help_text
    
    def _ask_next_field(self) -> str:
        """
        Generate the prompt for the next field.
        
        Returns:
            str: The prompt asking about the current field
        """
        current_field = self.fields[self.current_field_index]
        prompt = self.field_prompts[current_field]
        
        # Add hint if available
        if current_field in self.field_hints:
            prompt += f"\n\n*Hint: {self.field_hints[current_field]}*"
        
        return prompt
    
    def _parse_response(self, field: str, user_input: str) -> Optional[str]:
        """
        Parse a user's natural language response into a structured value.
        
        Args:
            field: The field being parsed
            user_input: The user's response
            
        Returns:
            Optional[str]: The parsed value, or None if parsing failed
        """
        if not user_input.strip():
            return None
        
        # Special handling for gender - use keyword matching first
        if field == "gender":
            gender_result = self._parse_gender_with_keywords(user_input)
            if gender_result:
                return gender_result
            # Fallback to LLM parsing only if ambiguous
            return self.llm_infer_gender(user_input)
        
        # Try pattern matching first (more reliable)
        pattern_result = self._parse_with_patterns(field, user_input)
        if pattern_result:
            return pattern_result
        
        # Fallback to LLM service if available
        if self.llm_service:
            return self._parse_with_llm(field, user_input)
        
        # If all else fails, return the input as-is for most fields
        if field in ['personality', 'background', 'name', 'alignment']:
            return user_input.strip().title()
        
        return None
    
    def _parse_gender_with_keywords(self, user_input: str) -> Optional[str]:
        """
        Parse gender using explicit keyword logic for better accuracy.
        
        Args:
            user_input: The user's response
            
        Returns:
            Optional[str]: The parsed gender value, or None if no keywords found
        """
        input_lower = user_input.lower()
        
        # Check for female keywords first (case-insensitive)
        if "female" in input_lower or "woman" in input_lower:
            return "Female"
        
        # Check for male keywords
        if "male" in input_lower or "man" in input_lower:
            return "Male"
        
        # Check for non-binary keywords
        if "nonbinary" in input_lower or "non-binary" in input_lower:
            return "Non-Binary"
        
        return None
    
    def llm_infer_gender(self, user_input: str) -> Optional[str]:
        """
        Use LLM to infer gender from ambiguous input.
        
        Args:
            user_input: The user's response
            
        Returns:
            Optional[str]: The inferred gender value, or None if unclear
        """
        try:
            if not self.llm_service:
                return None
            
            prompt = f"""
Extract the gender from this user input. Return only one of these values:
- "Female" (for female, woman, she, her, etc.)
- "Male" (for male, man, he, his, etc.)
- "Non-Binary" (for non-binary, they, them, etc.)
- "Unknown" (if gender is unclear or not specified)

User input: "{user_input}"

Extracted gender:"""

            response = self.llm_service.get_completion(prompt)
            
            if response and response.get('success'):
                parsed_value = response['response'].strip()
                if parsed_value:
                    # Normalize the result to title case
                    normalized = parsed_value.title()
                    # Accept valid gender values
                    if normalized in ["Female", "Male", "Non-Binary", "Unknown"]:
                        return normalized
            
        except Exception as e:
            logger.error(f"LLM gender inference failed: {e}")
        
        return None
    
    def _parse_with_llm(self, field: str, user_input: str) -> Optional[str]:
        """
        Parse response using LLM service.
        
        Args:
            field: The field being parsed
            user_input: The user's response
            
        Returns:
            Optional[str]: The parsed value
        """
        try:
            # Create a prompt for the LLM
            prompt = f"""
Extract the {field} from this user input. Return only the most appropriate value, nothing else.

Field: {field}
User input: "{user_input}"
Available options: {self.field_hints.get(field, 'Any valid value')}

Extracted {field}:"""

            response = self.llm_service.get_completion(prompt)
            
            if response and response.get('success'):
                parsed_value = response['response'].strip()
                if parsed_value and parsed_value.lower() not in ['none', 'unknown', 'n/a']:
                    return parsed_value
            
        except Exception as e:
            logger.error(f"LLM parsing failed for {field}: {e}")
        
        return None
    
    def _parse_with_patterns(self, field: str, user_input: str) -> Optional[str]:
        """
        Parse response using pattern matching (fallback).
        
        Args:
            field: The field being parsed
            user_input: The user's response
            
        Returns:
            Optional[str]: The parsed value
        """
        input_lower = user_input.lower()
        
        # Race patterns
        if field == "race":
            race_patterns = {
                'human': ['human', 'humanity'],
                'elf': ['elf', 'elven', 'elvish'],
                'dwarf': ['dwarf', 'dwarven', 'dwarvish'],
                'halfling': ['halfling', 'hobbit'],
                'dragonborn': ['dragonborn', 'dragon-born'],
                'gnome': ['gnome', 'gnomish'],
                'half-elf': ['half-elf', 'half elf', 'halfelven'],
                'half-orc': ['half-orc', 'half orc'],
                'tiefling': ['tiefling'],
                'aasimar': ['aasimar', 'celestial', 'touched by light']
            }
            
            for race, patterns in race_patterns.items():
                if any(pattern in input_lower for pattern in patterns):
                    return race.title()
        
        # Class patterns
        elif field == "class":
            class_patterns = {
                'fighter': ['fighter', 'warrior', 'soldier'],
                'wizard': ['wizard', 'mage', 'spellcaster'],
                'cleric': ['cleric', 'priest', 'healer'],
                'rogue': ['rogue', 'thief', 'assassin'],
                'ranger': ['ranger', 'hunter', 'scout'],
                'paladin': ['paladin', 'holy warrior'],
                'barbarian': ['barbarian', 'berserker'],
                'bard': ['bard', 'musician', 'performer'],
                'druid': ['druid', 'nature priest'],
                'monk': ['monk', 'martial artist'],
                'sorcerer': ['sorcerer', 'innate magic'],
                'warlock': ['warlock', 'pact magic']
            }
            
            for class_name, patterns in class_patterns.items():
                if any(pattern in input_lower for pattern in patterns):
                    return class_name.title()
        
        # Gender patterns - now handled by _parse_gender_with_keywords
        elif field == "gender":
            # Gender parsing is now handled in _parse_response method
            # This fallback is kept for compatibility
            return self._parse_gender_with_keywords(user_input)
        
        # Age patterns
        elif field == "age":
            import re
            age_match = re.search(r'\b(\d+)\b', user_input)
            if age_match:
                age = int(age_match.group(1))
                if 1 <= age <= 1000:  # Reasonable age range
                    return str(age)
        
        # For other fields, return the input as-is (with some cleaning)
        else:
            # Clean up the input
            cleaned = user_input.strip()
            if cleaned and len(cleaned) > 0:
                return cleaned.title()
        
        return None
    
    def _parse_ability_scores(self, user_input: str) -> Optional[str]:
        """
        Parse ability score assignment method from user input.
        
        Args:
            user_input: The user's response
            
        Returns:
            Optional[str]: The parsed ability score method
        """
        input_lower = user_input.lower().strip()
        
        # Check for numeric input
        if input_lower in ['1', 'one', 'standard', 'array', 'standard array']:
            return 'standard_array'
        elif input_lower in ['2', 'two', 'point', 'buy', 'point buy']:
            return 'point_buy'
        elif input_lower in ['3', 'three', 'optimal', 'ai', 'best', 'optimal assignment']:
            return 'optimal_assignment'
        
        # Check for more descriptive input
        if any(word in input_lower for word in ['standard', 'array', 'preset']):
            return 'standard_array'
        elif any(word in input_lower for word in ['point', 'buy', 'custom', 'choose']):
            return 'point_buy'
        elif any(word in input_lower for word in ['optimal', 'ai', 'best', 'auto', 'automatic']):
            return 'optimal_assignment'
        
        return None
    
    def _complete_creation(self) -> str:
        """
        Complete the character creation process.
        
        Returns:
            str: Completion message
        """
        self.is_active = False
        
        # Create the final character data
        character_data = self._create_character_data()
        
        # Call the completion callback if provided
        if self.on_complete_callback:
            try:
                self.on_complete_callback(character_data)
            except Exception as e:
                logger.error(f"Error in completion callback: {e}")
        
        logger.info("Character creation completed")
        
        return f"""
🎉 **Character Creation Complete!**

Your character is ready:

**Name:** {character_data.get('name', 'Unknown')}
**Race:** {character_data.get('race', 'Unknown')}
**Class:** {character_data.get('class', 'Unknown')}
**Gender:** {character_data.get('gender', 'Unknown')}
**Age:** {character_data.get('age', 'Unknown')}
**Background:** {character_data.get('background', 'Unknown')}
**Personality:** {character_data.get('personality', 'Unknown')}
**Level:** {character_data.get('level', '1')}
**Alignment:** {character_data.get('alignment', 'Unknown')}

Your character is ready for adventure! 🗡️✨
"""
    
    def _create_character_data(self) -> Dict:
        """
        Create the final character data dictionary using CharacterManager and Ability Score System.
        
        Returns:
            Dict: The complete character data with all D&D mechanics
        """
        try:
            # Import required modules
            try:
                from character_manager import CharacterManager
                from ability_score_system import AbilityScoreSystem, AbilityScoreMethod
            except ImportError:
                from ..character_manager import CharacterManager
                from ..ability_score_system import AbilityScoreSystem, AbilityScoreMethod
            
            # Get ability score method
            ability_method = self.state.get('ability_scores', 'optimal_assignment')
            
            # Create ability score system
            ability_system = AbilityScoreSystem()
            
            # Assign ability scores based on method
            if ability_method == 'standard_array':
                method = AbilityScoreMethod.STANDARD_ARRAY
            elif ability_method == 'point_buy':
                method = AbilityScoreMethod.POINT_BUY
            else:  # optimal_assignment
                method = AbilityScoreMethod.OPTIMAL_ASSIGNMENT
            
            # Get character class and race for ability score assignment
            character_class = self.state.get('class')
            race = self.state.get('race')
            
            # Assign ability scores
            ability_scores = ability_system.assign_ability_scores(method, character_class, race)
            
            # Apply racial bonuses
            ability_scores = ability_system.apply_racial_bonuses(ability_scores, race)
            
            # Calculate modifiers
            ability_modifiers = {}
            for ability, score in ability_scores.items():
                ability_modifiers[ability] = ability_system.calculate_modifier(score)
            
            # Create basic info for character manager
            basic_info = {
                'name': self.state.get('name'),
                'race': self.state.get('race'),
                'class': self.state.get('class'),
                'level': int(self.state.get('level', 1)),
                'background': self.state.get('background'),
                'personality': self.state.get('personality'),
                'age': self.state.get('age'),
                'gender': self.state.get('gender'),
                'alignment': self.state.get('alignment'),
                'ability_scores': ability_scores,
                'ability_modifiers': ability_modifiers,
                'ability_score_method': ability_method,
                'created_date': datetime.now().isoformat(),
                'creation_method': 'step_by_step'
            }
            
            # Use character manager to create complete D&D character
            char_manager = CharacterManager()
            complete_character = char_manager.create_character(basic_info, "step_by_step")
            
            logger.info(f"Created complete character: {complete_character.get('basic_info', {}).get('name', 'Unknown')}")
            return complete_character
            
        except Exception as e:
            logger.error(f"Error creating complete character: {e}")
            # Fallback to basic character data
            return {
                'name': self.state.get('name'),
                'race': self.state.get('race'),
                'class': self.state.get('class'),
                'level': int(self.state.get('level', 1)),
                'background': self.state.get('background'),
                'personality': self.state.get('personality'),
                'age': self.state.get('age'),
                'gender': self.state.get('gender'),
                'alignment': self.state.get('alignment'),
                'created_date': datetime.now().isoformat(),
                'creation_method': 'step_by_step'
            }
    
    def get_current_progress(self) -> Dict:
        """
        Get the current progress state.
        
        Returns:
            Dict: Current state information
        """
        return {
            'is_active': self.is_active,
            'current_field': self.fields[self.current_field_index] if self.is_active else None,
            'current_field_index': self.current_field_index,
            'completed_fields': len([f for f in self.fields if self.state[f]]),
            'total_fields': len(self.fields),
            'state': self.state.copy()
        }
    
    def reset(self) -> str:
        """
        Reset the character creation process.
        
        Returns:
            str: Reset confirmation message
        """
        self.is_active = False
        self.current_field_index = 0
        self.state = {field: None for field in self.fields}
        
        logger.info("Character creation reset")
        return "Character creation has been reset. Use .start() to begin again."
    
    def restore_state(self, state: dict, current_field_index: int, is_active: bool):
        """
        Restore the creator state from session data.
        
        Args:
            state: The character state dictionary
            current_field_index: The current field index
            is_active: Whether the creation is active
        """
        self.state = state
        self.current_field_index = current_field_index
        self.is_active = is_active
        
        logger.info(f"Restored step-by-step state: field_index={current_field_index}, active={is_active}") 