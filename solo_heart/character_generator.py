#!/usr/bin/env python3
"""
LLM-Powered Character Generator for SoloHeart
Handles natural language character creation through conversation with the AI.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from character_manager import CharacterManager
from ollama_llm_service import chat_completion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CharacterGenerator:
    """Handles LLM-powered character creation through natural conversation."""
    
    def __init__(self):
        self.conversation_history = []
        self.current_character_data = {}
        self.is_complete = False
        self.character_manager = CharacterManager()
        
        # Initialize Ollama LLM service
        try:
            from ollama_llm_service import get_ollama_service
            self.ollama_service = get_ollama_service()
            logger.info("Ollama LLM service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama LLM service: {e}")
            raise
    
    def start_character_creation(self, initial_description: str, campaign_name: str = "") -> Dict:
        """Start the character creation conversation."""
        self.conversation_history = []
        self.current_character_data = {
            'creation_method': 'vibe_code',
            'campaign_name': campaign_name,
            'creation_started': datetime.now().isoformat(),
            'conversation_history': []
        }
        self.is_complete = False
        
        # Create the initial system prompt
        system_prompt = self._create_system_prompt()
        
        # Add the initial description to conversation
        self.conversation_history.append({
            'role': 'user',
            'content': initial_description
        })
        
        # Get the first response from the LLM
        response = self._get_llm_response(system_prompt)
        
        return {
            'success': True,
            'message': response,
            'is_complete': self.is_complete,
            'character_data': self.current_character_data
        }
    
    def continue_conversation(self, player_input: str) -> Dict:
        """Continue the character creation conversation."""
        if self.is_complete:
            return {
                'success': False,
                'message': 'Character creation is already complete.',
                'is_complete': True,
                'character_data': self.current_character_data
            }
        
        # Add player input to conversation
        self.conversation_history.append({
            'role': 'user',
            'content': player_input
        })
        
        # Get response from LLM
        system_prompt = self._create_system_prompt()
        response = self._get_llm_response(system_prompt)
        
        return {
            'success': True,
            'message': response,
            'is_complete': self.is_complete,
            'character_data': self.current_character_data
        }
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for character creation."""
        return """You are an experienced SoloHeart Guide helping a player create their SoloHeart character through natural conversation. 

Your role is to:
1. Listen to the player's description of their character concept
2. Ask clarifying questions when needed to fill in missing details
3. Interpret their vision and translate it into proper SoloHeart character mechanics
        4. Maintain a conversational, SoloHeart Guide-like tone throughout

When you have enough information to create a complete character, respond with:
"CHARACTER_COMPLETE:" followed by a JSON object containing the character data.

The JSON should include all required fields for a SoloHeart character:
{
    "basic_info": {
        "name": "Character Name",
        "race": "Race (from SRD: Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling)",
        "class": "Class (from SRD: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard)",
        "background": "Background (from SRD: Acolyte, Criminal, Folk Hero, Haunted One, Noble, Sage, Soldier, Urchin)",
        "alignment": "Alignment (from SRD alignments)",
        "level": 1
    },
    "ability_scores": {
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10
    },
    "personality": {
        "traits": ["Personality trait"],
        "ideals": ["Ideal"],
        "bonds": ["Bond"],
        "flaws": ["Flaw"]
    },
    "background_info": {
        "backstory": "Character background story",
        "appearance": "Physical description",
        "notes": "Additional notes"
    }
}

Keep the conversation natural and engaging. Ask follow-up questions when you need more details, but don't be overly formal or robotic. You're a helpful SoloHeart Guide, not a form-filler.

Important: Only use races, classes, and backgrounds from the SRD. If the player mentions something not in the SRD, suggest the closest SRD equivalent."""
    
    def _get_llm_response(self, system_prompt: str) -> str:
        """Get response from the LLM."""
        try:
            # Prepare messages for the API
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.conversation_history)
            
            # Get response from Ollama
            response_content = chat_completion(messages, temperature=0.7, max_tokens=1000)
            
            # Check if character is complete
            if "CHARACTER_COMPLETE:" in response_content:
                self._parse_complete_character(response_content)
                return response_content.replace("CHARACTER_COMPLETE:", "").strip()
            
            # Add response to conversation history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response_content
            })
            
            return response_content
            
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return f"I'm having trouble processing that right now. Error: {str(e)}"
    
    def _parse_complete_character(self, response: str) -> None:
        """Parse the complete character data from LLM response."""
        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                character_data = json.loads(json_str)
                
                # Create full character using character manager
                basic_info = character_data.get('basic_info', {})
                basic_info['stats'] = character_data.get('ability_scores', {})
                
                full_character = self.character_manager.create_character(
                    basic_info, 
                    creation_method='vibe_code'
                )
                
                # Update with personality and background info
                if 'personality' in character_data:
                    full_character['personality'] = character_data['personality']
                
                if 'background_info' in character_data:
                    full_character['background_info'] = character_data['background_info']
                
                # Validate the complete character
                if self.character_manager.validate_character(full_character):
                    self.current_character_data = full_character
                    self.is_complete = True
                    logger.info(f"Character creation completed: {full_character['basic_info']['name']}")
                else:
                    logger.error("Generated character failed validation")
                    self.is_complete = False
                
        except Exception as e:
            logger.error(f"Error parsing complete character: {e}")
            # If parsing fails, continue the conversation
            self.is_complete = False
    
    def get_character_data(self) -> Dict:
        """Get the current character data."""
        return self.current_character_data.copy()
    
    def save_character(self, campaign_id: str) -> bool:
        """Save the character data to a file."""
        if not self.is_complete:
            return False
        
        try:
            return self.character_manager.save_character(self.current_character_data, campaign_id)
        except Exception as e:
            logger.error(f"Error saving character: {e}")
            return False
    
    def load_character(self, campaign_id: str) -> bool:
        """Load character data from file."""
        try:
            character = self.character_manager.load_character(campaign_id)
            if character:
                self.current_character_data = character
                self.is_complete = True
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error loading character: {e}")
            return False 