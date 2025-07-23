#!/usr/bin/env python3
"""
LLM-Powered Character Generator for SoloHeart
Handles natural language character creation through conversation with the AI.
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .character_manager import CharacterManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CharacterGenerator:
    """Handles LLM-powered character creation through natural conversation."""
    
    def __init__(self):
        self.conversation_history = []
        self.current_character_data = {
            'name': None,
            'race': None,
            'class': None,
            'background': None,
            'alignment': None,
            'level': 1,
            'ability_scores': {
                'strength': 10,
                'dexterity': 10,
                'constitution': 10,
                'intelligence': 10,
                'wisdom': 10,
                'charisma': 10
            },
            'personality': None,
            'backstory': None,
            'appearance': None,
            'created_date': datetime.now().isoformat(),
            'creation_method': 'conversational'
        }
        self.is_complete = False
        self.character_manager = CharacterManager()
        
        # Initialize LLM service
        try:
            from .gemma3_llm_service import chat_completion
            self.chat_completion = chat_completion
            logger.info("Gemma3 LLM service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemma3 LLM service: {e}")
            raise
    
    def start_character_creation(self, initial_description: str, campaign_name: str = "") -> Dict:
        """Start the character creation conversation."""
        self.conversation_history = []
        self.current_character_data = {
            'name': None,
            'race': None,
            'class': None,
            'background': None,
            'alignment': None,
            'level': 1,
            'ability_scores': {
                'strength': 10,
                'dexterity': 10,
                'constitution': 10,
                'intelligence': 10,
                'wisdom': 10,
                'charisma': 10
            },
            'personality': None,
            'backstory': None,
            'appearance': None,
            'created_date': datetime.now().isoformat(),
            'creation_method': 'conversational',
            'campaign_name': campaign_name
        }
        self.is_complete = False
        
        # Add the initial description to conversation
        self.conversation_history.append({
            'role': 'user',
            'content': initial_description
        })
        
        # Extract initial character details
        self._extract_character_details(initial_description)
        
        # Get the first response from the LLM
        response = self._get_conversational_response()
        
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
        
        # Extract character details from the input
        self._extract_character_details(player_input)
        
        # Get response from LLM
        response = self._get_conversational_response()
        
        # Check if we have enough information to complete
        if self._has_sufficient_character_data():
            self.is_complete = True
            # Assign ability scores when character is complete
            self._assign_ability_scores()
            response += "\n\n🎉 **Character Creation Complete!** Your character is ready for adventure!"
        
        return {
            'success': True,
            'message': response,
            'is_complete': self.is_complete,
            'character_data': self.current_character_data
        }
    
    def _get_conversational_response(self) -> str:
        """Get a natural conversational response from the LLM."""
        try:
            system_prompt = """You are an experienced Dungeon Master helping a player create their DnD 5e character through natural conversation.

Your role is to:
1. Have a natural, engaging conversation about their character
2. Ask follow-up questions when you need more details
3. Show enthusiasm for their character concept
4. Help them flesh out their character's personality, background, and motivations
5. Keep the conversation flowing naturally - don't be formal or robotic

You're a helpful DM, not a form-filler. Have fun with it! Ask about their character's goals, fears, relationships, or any interesting details they want to explore.

If they seem to have a complete character concept, you can ask if they're ready to finalize their character, but don't force it - let the conversation flow naturally."""

            # Prepare messages for the API
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.conversation_history)
            
            # Get response from LLM
            response_content = self.chat_completion(messages, temperature=0.8, max_tokens=800)
            
            # Add response to conversation history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response_content
            })
            
            return response_content
            
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return "I'm having trouble processing that right now. Let's continue with your character creation!"
    
    def _extract_character_details(self, text: str) -> None:
        """Extract character details from text using pattern matching and LLM analysis."""
        text_lower = text.lower()
        
        # Extract name - improved patterns (order matters - more specific first)
        if not self.current_character_data['name']:
            name_patterns = [
                r'\b(?:my name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'\b(?:called|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'\b(?:name|named)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'\b(?:i am|i\'m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s+(?:is my name|here))',
                r'\b(?:character|hero|adventurer)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s+(?:the|is a|was a|am a))'
            ]
            for pattern in name_patterns:
                name_match = re.search(pattern, text, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1).strip()
                    # Clean up the name by removing common words at the end
                    name_parts = name.split()
                    # Remove common words from the end of the name
                    while name_parts and name_parts[-1].lower() in ['the', 'and', 'or', 'but', 'with', 'from', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'is', 'am', 'was', 'a', 'an']:
                        name_parts.pop()
                    
                    if name_parts and len(name_parts) <= 3:
                        # Keep the cleaned name
                        self.current_character_data['name'] = ' '.join(name_parts).title()
                        logger.info(f"Extracted name: {self.current_character_data['name']}")
                        break
        
        # Extract race - improved with more variations (order matters - more specific first)
        if not self.current_character_data['race']:
            race_patterns = [
                ('half-elf', ['half-elf', 'half elf', 'halfelven']),
                ('half-orc', ['half-orc', 'half orc', 'half-orcish']),
                ('dragonborn', ['dragonborn', 'dragon-born']),
                ('tiefling', ['tiefling', 'tiefling']),
                ('halfling', ['halfling', 'hobbit']),
                ('gnome', ['gnome', 'gnomish']),
                ('elf', ['elf', 'elven', 'elvish', 'eladrin']),
                ('dwarf', ['dwarf', 'dwarven', 'dwarvish']),
                ('human', ['human', 'humanity'])
            ]
            for race, patterns in race_patterns:
                if any(pattern in text_lower for pattern in patterns):
                    self.current_character_data['race'] = race.title()
                    logger.info(f"Extracted race: {self.current_character_data['race']}")
                    break
        
        # Extract class - improved with more variations (order matters - more specific first)
        if not self.current_character_data['class']:
            class_patterns = [
                ('druid', ['druid', 'druidic', 'nature priest']),
                ('barbarian', ['barbarian', 'barbaric', 'berserker']),
                ('bard', ['bard', 'musician', 'performer', 'entertainer']),
                ('cleric', ['cleric', 'priest', 'healer', 'divine']),
                ('fighter', ['fighter', 'warrior', 'soldier', 'knight']),
                ('monk', ['monk', 'martial artist', 'unarmed']),
                ('paladin', ['paladin', 'holy warrior', 'divine knight']),
                ('ranger', ['ranger', 'hunter', 'scout', 'wilderness']),
                ('rogue', ['rogue', 'thief', 'assassin', 'scoundrel']),
                ('sorcerer', ['sorcerer', 'sorcerous', 'innate magic']),
                ('warlock', ['warlock', 'pact magic', 'patron']),
                ('wizard', ['wizard', 'mage', 'spellcaster', 'arcane'])
            ]
            for class_name, patterns in class_patterns:
                if any(pattern in text_lower for pattern in patterns):
                    self.current_character_data['class'] = class_name.title()
                    logger.info(f"Extracted class: {self.current_character_data['class']}")
                    break
        
        # Extract background - improved with more variations and custom backgrounds
        if not self.current_character_data['background']:
            # First try to match SRD backgrounds
            background_patterns = {
                'acolyte': ['acolyte', 'temple', 'religious', 'faithful'],
                'criminal': ['criminal', 'thief', 'outlaw', 'bandit'],
                'folk hero': ['folk hero', 'hero', 'savior', 'protector'],
                'haunted one': ['haunted', 'cursed', 'tormented', 'dark past'],
                'noble': ['noble', 'aristocrat', 'royalty', 'lord', 'lady'],
                'sage': ['sage', 'scholar', 'researcher', 'learned'],
                'soldier': ['soldier', 'military', 'veteran', 'warrior'],
                'urchin': ['urchin', 'street kid', 'orphan', 'homeless']
            }
            
            # Try to match SRD backgrounds first
            for background, patterns in background_patterns.items():
                if any(pattern in text_lower for pattern in patterns):
                    self.current_character_data['background'] = background.title()
                    logger.info(f"Extracted background: {self.current_character_data['background']}")
                    break
            
            # If no SRD background found, try to extract custom background
            if not self.current_character_data['background']:
                # Look for background-related phrases
                background_indicators = [
                    'grew up in', 'born in', 'raised in', 'from', 'hailing from',
                    'survivor of', 'child of', 'product of', 'victim of'
                ]
                
                for indicator in background_indicators:
                    if indicator in text_lower:
                        # Extract the phrase after the indicator
                        start_idx = text_lower.find(indicator) + len(indicator)
                        end_idx = text.find('.', start_idx)
                        if end_idx == -1:
                            end_idx = len(text)
                        
                        background_phrase = text[start_idx:end_idx].strip()
                        if background_phrase:
                            self.current_character_data['background'] = background_phrase.title()
                            logger.info(f"Extracted custom background: {self.current_character_data['background']}")
                            break
        
        # Extract age
        if not self.current_character_data.get('age'):
            # Try different age patterns
            age_patterns = [
                r'(\d+)-year-old',
                r'(\d+)\s+years?\s+old',
                r'(\d+)\s*y\.?o\.?',
                r'(\d+)\s+year\s+old'
            ]
            for pattern in age_patterns:
                age_match = re.search(pattern, text, re.IGNORECASE)
                if age_match:
                    self.current_character_data['age'] = int(age_match.group(1))
                    logger.info(f"Extracted age: {self.current_character_data['age']}")
                    break
        
        # Extract gender (order matters - more specific first)
        if not self.current_character_data.get('gender'):
            gender_patterns = [
                ('non-binary', ['non-binary', 'nonbinary', 'they', 'them', 'their']),
                ('female', ['female', 'woman', 'girl', 'she', 'her', 'hers']),
                ('male', ['male', 'man', 'guy', 'he', 'his', 'him'])
            ]
            for gender, patterns in gender_patterns:
                if any(pattern in text_lower for pattern in patterns):
                    self.current_character_data['gender'] = gender.title()
                    logger.info(f"Extracted gender: {self.current_character_data['gender']}")
                    break
        
        # Extract alignment (order matters - more specific first)
        if not self.current_character_data.get('alignment'):
            alignment_patterns = [
                ('lawful good', ['lawful good', 'orderly', 'just']),
                ('neutral good', ['neutral good', 'good', 'kind', 'benevolent']),
                ('chaotic good', ['chaotic good', 'free-spirited', 'rebellious']),
                ('lawful neutral', ['lawful neutral', 'order', 'tradition']),
                ('chaotic neutral', ['chaotic neutral', 'chaos', 'freedom']),
                ('lawful evil', ['lawful evil', 'tyrannical', 'oppressive']),
                ('neutral evil', ['neutral evil', 'evil', 'malicious']),
                ('chaotic evil', ['chaotic evil', 'destructive', 'anarchic']),
                ('neutral', ['neutral', 'balanced', 'middle ground']),
                ('lawful', ['lawful']),
                ('chaotic', ['chaotic'])
            ]
            for alignment, patterns in alignment_patterns:
                if any(pattern in text_lower for pattern in patterns):
                    self.current_character_data['alignment'] = alignment.title()
                    logger.info(f"Extracted alignment: {self.current_character_data['alignment']}")
                    break
        
        # Extract personality traits - improved with more comprehensive patterns
        personality_keywords = {
            'brave': ['brave', 'courageous', 'fearless', 'bold'],
            'cautious': ['cautious', 'careful', 'wary', 'prudent'],
            'friendly': ['friendly', 'amiable', 'sociable', 'outgoing'],
            'quiet': ['quiet', 'silent', 'reserved'],
            'deadly': ['deadly', 'lethal', 'dangerous', 'lethal'],
            'mysterious': ['mysterious', 'enigmatic', 'secretive'],
            'wise': ['wise', 'intelligent', 'smart', 'clever'],
            'foolish': ['foolish', 'silly', 'naive', 'innocent'],
            'kind': ['kind', 'gentle', 'compassionate', 'caring'],
            'cruel': ['cruel', 'harsh', 'mean', 'ruthless'],
            'honest': ['honest', 'truthful', 'sincere', 'genuine'],
            'deceptive': ['deceptive', 'dishonest', 'lying', 'manipulative'],
            'loyal': ['loyal', 'faithful', 'devoted', 'dedicated'],
            'treacherous': ['treacherous', 'betraying', 'untrustworthy'],
            'optimistic': ['optimistic', 'hopeful', 'positive', 'cheerful'],
            'pessimistic': ['pessimistic', 'cynical', 'negative', 'gloomy'],
            'curious': ['curious', 'inquisitive', 'exploring', 'adventurous'],
            'reserved': ['reserved', 'shy', 'introverted', 'private']
        }
        
        personality_traits = []
        for trait, patterns in personality_keywords.items():
            if any(pattern in text_lower for pattern in patterns):
                personality_traits.append(trait)
        
        if personality_traits:
            current_personality = self.current_character_data.get('personality', '')
            if current_personality:
                new_traits = [trait for trait in personality_traits if trait not in current_personality.lower()]
            else:
                new_traits = personality_traits
            if new_traits:
                if current_personality:
                    self.current_character_data['personality'] = current_personality + ', ' + ', '.join(new_traits)
                else:
                    self.current_character_data['personality'] = ', '.join(new_traits)
                logger.info(f"Updated personality: {self.current_character_data['personality']}")
        
        # Extract backstory elements - improved to accumulate more details
        backstory_indicators = [
            'survived', 'grew up', 'trained', 'learned', 'discovered', 'lost', 'found', 
            'escaped', 'fought', 'protected', 'saved', 'rescued', 'helped', 'served',
            'worked', 'lived', 'traveled', 'explored', 'studied', 'practiced',
            'experienced', 'witnessed', 'participated', 'joined', 'left', 'abandoned',
            'returned', 'arrived', 'departed', 'met', 'befriended', 'betrayed',
            'married', 'divorced', 'died', 'born', 'raised', 'educated', 'thief'
        ]
        
        if any(indicator in text_lower for indicator in backstory_indicators):
            current_backstory = self.current_character_data.get('backstory', '')
            if current_backstory and text not in current_backstory:
                # Add new information to existing backstory
                self.current_character_data['backstory'] = current_backstory + " " + text
            elif not current_backstory:
                # Start new backstory
                self.current_character_data['backstory'] = text
            logger.info("Updated backstory with new details")
        
        # Extract appearance hints
        appearance_keywords = ['tall', 'short', 'thin', 'fat', 'muscular', 'slender', 'broad', 'narrow', 'beautiful', 'ugly', 'handsome', 'pretty', 'scarred', 'tattooed', 'bald', 'long hair', 'short hair', 'blonde', 'brunette', 'redhead', 'gray hair', 'white hair', 'black hair', 'dark hair', 'blue eyes', 'green eyes', 'brown eyes', 'gray eyes']
        appearance_traits = []
        for trait in appearance_keywords:
            if trait in text_lower:
                appearance_traits.append(trait)
        
        if appearance_traits and not self.current_character_data.get('appearance'):
            self.current_character_data['appearance'] = ', '.join(appearance_traits)
            logger.info(f"Extracted appearance: {self.current_character_data['appearance']}")
    
    def _has_sufficient_character_data(self) -> bool:
        """Check if we have enough character data to consider creation complete."""
        required_fields = ['name', 'race', 'class']
        optional_fields = ['background', 'personality', 'backstory']
        
        # Must have all required fields
        if not all(self.current_character_data.get(field) for field in required_fields):
            return False
        
        # Should have at least some optional fields
        optional_count = sum(1 for field in optional_fields if self.current_character_data.get(field))
        return optional_count >= 1
    
    def _assign_ability_scores(self) -> None:
        """Assign ability scores using the optimal method for the character's class."""
        try:
            from ability_score_system import AbilityScoreSystem, AbilityScoreMethod
            
            # Create ability score system
            ability_system = AbilityScoreSystem()
            
            # Get character class and race
            character_class = self.current_character_data.get('class')
            race = self.current_character_data.get('race')
            
            # Assign optimal ability scores for the class
            ability_scores = ability_system.assign_ability_scores(
                AbilityScoreMethod.OPTIMAL_ASSIGNMENT, 
                character_class, 
                race
            )
            
            # Apply racial bonuses
            ability_scores = ability_system.apply_racial_bonuses(ability_scores, race)
            
            # Calculate modifiers
            ability_modifiers = {}
            for ability, score in ability_scores.items():
                ability_modifiers[ability] = ability_system.calculate_modifier(score)
            
            # Update character data
            self.current_character_data['ability_scores'] = ability_scores
            self.current_character_data['ability_modifiers'] = ability_modifiers
            self.current_character_data['ability_score_method'] = 'optimal_assignment'
            
            logger.info(f"Assigned ability scores for {character_class}: {ability_scores}")
            
        except Exception as e:
            logger.error(f"Error assigning ability scores: {e}")
            # Keep default scores if assignment fails
    
    def get_character_data(self) -> Dict:
        """Get the current character data."""
        return self.current_character_data.copy()
    
    def save_character(self, campaign_id: str) -> bool:
        """Save the character to a file."""
        try:
            character_data = self.get_character_data()
            character_data['campaign_id'] = campaign_id
            
            # Save using character manager
            return self.character_manager.save_character(character_data)
        except Exception as e:
            logger.error(f"Error saving character: {e}")
            return False
    
    def load_character(self, campaign_id: str) -> bool:
        """Load a character from file."""
        try:
            character_data = self.character_manager.load_character(campaign_id)
            if character_data:
                self.current_character_data = character_data
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading character: {e}")
            return False 