#!/usr/bin/env python3
"""
LLM-Powered Vibe Code Character Creator for SoloHeart
Handles natural language character creation through conversation with the AI.
Adapted from July 6 implementation (commit 8af2e2de) for current SoloHeart architecture.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
try:
    from .character_manager import CharacterManager
except ImportError:
    from character_manager import CharacterManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VibeCodeCharacterCreator:
    """Handles LLM-powered character creation through natural conversation."""
    
    def __init__(self):
        self.conversation_history = []
        self.current_character_data = {}
        self.is_complete = False
        self.character_manager = CharacterManager()
        
        # Initialize Gemma3 LLM service
        try:
            from ..gemma3_llm_service import chat_completion
            self.chat_completion = chat_completion
            logger.info("Gemma3 LLM service initialized successfully")
        except ImportError:
            # Fallback to direct import if relative import fails
            try:
                from gemma3_llm_service import chat_completion
                self.chat_completion = chat_completion
                logger.info("Gemma3 LLM service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemma3 LLM service: {e}")
                raise
        
        # Load SRD data for validation
        self.srd_races = self._load_srd_races()
        self.srd_classes = self._load_srd_classes()
        self.srd_backgrounds = self._load_srd_backgrounds()
        
        # Character creation prompts with SRD compliance
        self.initial_prompt = """You are a helpful D&D 5e character creation assistant. You must ONLY use content from the System Reference Document 5.2 (SRD).

AVAILABLE SRD RACES: Human, Elf (High Elf, Wood Elf), Dwarf (Hill Dwarf, Mountain Dwarf), Halfling (Lightfoot Halfling, Stout Halfling), Dragonborn, Gnome (Forest Gnome, Rock Gnome), Half-Elf, Half-Orc, Tiefling

AVAILABLE SRD CLASSES: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard

AVAILABLE SRD BACKGROUNDS: Acolyte, Criminal, Folk Hero, Guild Artisan, Hermit, Noble, Outlander, Sage, Soldier, Urchin

Your goal is to create a complete, SRD-compliant D&D 5e character through natural conversation. Ask one question at a time and build the character step by step.

IMPORTANT: If the player suggests any race, class, background, or other content not listed above, politely explain that you can only use SRD content and suggest an equivalent SRD option.

Start by asking about the character's basic concept, then move through:
1. Race and class (SRD only)
2. Background (SRD only)
3. Ability scores and stats
4. Equipment and proficiencies (SRD only)
5. Final details and confirmation

Be conversational and engaging. Don't overwhelm the player with too many questions at once."""

        self.followup_prompt = """Continue the character creation conversation. Ask the next logical question to complete the character. Be specific and helpful.

REMEMBER: Only use SRD content. If the player suggests non-SRD options, politely redirect them to SRD equivalents."""

    def start_character_creation(self, description: str, campaign_name: str = "") -> Dict:
        """Start the character creation process with an initial description."""
        try:
            logger.info(f"Starting Vibe Code character creation: '{description[:100]}...'")
            
            # Add initial description to conversation
            self.conversation_history.append({
                'role': 'user',
                'content': f"I want to create a character: {description}",
                'timestamp': datetime.now().isoformat()
            })
            
            # Generate AI response
            prompt = f"{self.initial_prompt}\n\nPlayer description: {description}\n\nAsk the first question to begin character creation:"
            
            try:
                ai_response = self.chat_completion(prompt)
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                ai_response = "Great! I'd love to help you create your character. Let's start with the basics - what race and class are you thinking of for this character?"
            
            # Add AI response to conversation
            self.conversation_history.append({
                'role': 'assistant',
                'content': ai_response,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'message': ai_response,
                'is_complete': False,
                'character_data': self.current_character_data
            }
            
        except Exception as e:
            logger.error(f"Error starting character creation: {e}")
            return {
                'success': False,
                'message': 'Sorry, there was an error starting character creation. Please try again.',
                'error': str(e)
            }

    def continue_conversation(self, user_input: str) -> Dict:
        """Continue the character creation conversation."""
        try:
            logger.info(f"Continuing Vibe Code conversation: '{user_input[:100]}...'")
            
            # Add user input to conversation
            self.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Extract character information from user input
            extracted_info = self._extract_character_info(user_input)
            if extracted_info:
                self._update_character_data(extracted_info)
            
            # Check if character is complete
            if self._is_character_complete():
                self.is_complete = True
                return self._finalize_character()
            
            # Generate next question
            conversation_context = self._build_conversation_context()
            prompt = f"{self.followup_prompt}\n\nConversation so far:\n{conversation_context}\n\nCurrent character data: {json.dumps(self.current_character_data, indent=2)}\n\nAsk the next question to continue character creation:"
            
            try:
                ai_response = self.chat_completion(prompt)
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                ai_response = "Thanks for that information! What would you like to tell me about next for your character?"
            
            # Add AI response to conversation
            self.conversation_history.append({
                'role': 'assistant',
                'content': ai_response,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'message': ai_response,
                'is_complete': False,
                'character_data': self.current_character_data
            }
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return {
                'success': False,
                'message': 'Sorry, there was an error continuing the conversation. Please try again.',
                'error': str(e)
            }

    def _extract_character_info(self, user_input: str) -> Dict:
        """Extract character information from user input using LLM with SRD validation."""
        try:
            prompt = f"""Extract character information from this user input. Return only a JSON object with the extracted information.

AVAILABLE SRD RACES: Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling
AVAILABLE SRD CLASSES: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard
AVAILABLE SRD BACKGROUNDS: Acolyte, Criminal, Folk Hero, Guild Artisan, Hermit, Noble, Outlander, Sage, Soldier, Urchin

User input: "{user_input}"

Current character data: {json.dumps(self.current_character_data, indent=2)}

Return a JSON object with any new character information found. Only include fields that are explicitly mentioned or strongly implied. Valid fields include:
- name, race, class, background, alignment, level
- strength, dexterity, constitution, intelligence, wisdom, charisma
- personality_traits, ideals, bonds, flaws
- equipment, weapons, armor
- languages, proficiencies
- spells (for spellcasters)

IMPORTANT: Only use SRD races, classes, and backgrounds listed above. If the user mentions non-SRD content, use the closest SRD equivalent.

Example: {{"race": "Elf", "class": "Wizard", "intelligence": 16}}

Return only the JSON object:"""

            try:
                response = self.chat_completion(prompt)
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    extracted = json.loads(json_match.group())
                    
                    # Validate SRD compliance
                    validated_extracted = self._validate_extracted_info(extracted)
                    
                    logger.info(f"Extracted character info: {validated_extracted}")
                    return validated_extracted
                else:
                    logger.warning(f"No JSON found in LLM response: {response}")
                    return {}
            except Exception as e:
                logger.error(f"Error extracting character info: {e}")
                return {}
                
        except Exception as e:
            logger.error(f"Error in character info extraction: {e}")
            return {}

    def _validate_extracted_info(self, extracted_info: Dict) -> Dict:
        """Validate extracted information against SRD data."""
        validated = {}
        
        for key, value in extracted_info.items():
            if key == 'race' and value:
                if self._validate_srd_content('race', value):
                    validated[key] = value
                else:
                    logger.warning(f"Non-SRD race '{value}' replaced with Human")
                    validated[key] = 'Human'
            elif key == 'class' and value:
                if self._validate_srd_content('class', value):
                    validated[key] = value
                else:
                    logger.warning(f"Non-SRD class '{value}' replaced with Fighter")
                    validated[key] = 'Fighter'
            elif key == 'background' and value:
                if self._validate_srd_content('background', value):
                    validated[key] = value
                else:
                    logger.warning(f"Non-SRD background '{value}' replaced with Soldier")
                    validated[key] = 'Soldier'
            else:
                validated[key] = value
        
        return validated

    def _update_character_data(self, new_info: Dict):
        """Update the current character data with new information."""
        for key, value in new_info.items():
            if value is not None and value != "":
                self.current_character_data[key] = value
                logger.info(f"Updated character data: {key} = {value}")

    def _is_character_complete(self) -> bool:
        """Check if the character has all required information."""
        required_fields = ['name', 'race', 'class', 'level', 'background']
        return all(field in self.current_character_data for field in required_fields)

    def _finalize_character(self) -> Dict:
        """Finalize the character creation process with complete SRD-compliant character."""
        try:
            # Ensure we have default values for missing fields
            defaults = {
                'level': 1,
                'background': 'Soldier',
                'alignment': 'True Neutral',
                'strength': 10,
                'dexterity': 10,
                'constitution': 10,
                'intelligence': 10,
                'wisdom': 10,
                'charisma': 10,
                'experience_points': 0,
                'hit_points': 0,  # Will be calculated by character manager
                'armor_class': 10,  # Will be calculated by character manager
                'initiative': 0,  # Will be calculated by character manager
                'speed': 30,  # Will be overridden by race if needed
                'proficiency_bonus': 2  # Will be calculated by character manager
            }
            
            for field, default_value in defaults.items():
                if field not in self.current_character_data:
                    self.current_character_data[field] = default_value
            
            # Ensure SRD compliance for all fields
            if not self._validate_srd_content('race', self.current_character_data.get('race', '')):
                self.current_character_data['race'] = 'Human'
            if not self._validate_srd_content('class', self.current_character_data.get('class', '')):
                self.current_character_data['class'] = 'Fighter'
            if not self._validate_srd_content('background', self.current_character_data.get('background', '')):
                self.current_character_data['background'] = 'Soldier'
            
            # Create the final character using the character manager
            character = self.character_manager.create_character(self.current_character_data, "vibe_code")
            
            if character:
                self.current_character_data = character
                
                # Verify all required character fields are present
                required_sections = ['basic_info', 'ability_scores', 'saving_throws', 'skills', 
                                   'combat_stats', 'proficiencies', 'equipment', 'personality', 
                                   'features', 'spellcasting', 'background_info']
                
                missing_sections = [section for section in required_sections if section not in character]
                if missing_sections:
                    logger.warning(f"Missing character sections: {missing_sections}")
                
                return {
                    'success': True,
                    'message': f"Perfect! Your character {character['basic_info']['name']} is ready for adventure!",
                    'is_complete': True,
                    'character_data': character
                }
            else:
                return {
                    'success': False,
                    'message': 'There was an error creating your character. Please try again.',
                    'is_complete': False
                }
                
        except Exception as e:
            logger.error(f"Error finalizing character: {e}")
            return {
                'success': False,
                'message': 'There was an error finalizing your character. Please try again.',
                'error': str(e)
            }

    def _build_conversation_context(self) -> str:
        """Build conversation context for LLM prompts."""
        context = ""
        for msg in self.conversation_history[-6:]:  # Last 6 messages
            role = "Player" if msg['role'] == 'user' else "Assistant"
            context += f"{role}: {msg['content']}\n"
        return context

    def save_character(self, campaign_id: str) -> bool:
        """Save the completed character."""
        try:
            if not self.is_complete or not self.current_character_data:
                return False
            
            return self.character_manager.save_character(self.current_character_data, campaign_id)
            
        except Exception as e:
            logger.error(f"Error saving character: {e}")
            return False

    def get_character_summary(self) -> Dict:
        """Get a summary of the current character."""
        if not self.current_character_data:
            return {}
        
        return self.character_manager.get_character_summary(self.current_character_data)

    def _load_srd_races(self) -> Dict:
        """Load SRD races data for validation."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, '..', '..', 'srd_data', 'races.json')
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return data.get('races', {})
            return {}
        except Exception as e:
            logger.error(f"Error loading SRD races: {e}")
            return {}

    def _load_srd_classes(self) -> Dict:
        """Load SRD classes data for validation."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, '..', '..', 'srd_data', 'classes.json')
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return data.get('classes', {})
            return {}
        except Exception as e:
            logger.error(f"Error loading SRD classes: {e}")
            return {}

    def _load_srd_backgrounds(self) -> Dict:
        """Load SRD backgrounds data for validation."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, '..', '..', 'srd_data', 'backgrounds.json')
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return data.get('backgrounds', {})
            return {}
        except Exception as e:
            logger.error(f"Error loading SRD backgrounds: {e}")
            return {}

    def _validate_srd_content(self, content_type: str, value: str) -> bool:
        """Validate that content is SRD-compliant."""
        if content_type == 'race':
            return value in self.srd_races
        elif content_type == 'class':
            return value in self.srd_classes
        elif content_type == 'background':
            return value in self.srd_backgrounds
        return True

    def _suggest_srd_alternative(self, content_type: str, invalid_value: str) -> str:
        """Suggest an SRD alternative for invalid content."""
        if content_type == 'race':
            return "Human"  # Default SRD race
        elif content_type == 'class':
            return "Fighter"  # Default SRD class
        elif content_type == 'background':
            return "Soldier"  # Default SRD background
        return "Unknown" 