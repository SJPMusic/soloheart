#!/usr/bin/env python3
"""
Vibe Code Character Creation Handler
====================================

Handles the AI-driven character creation flow with proper conversation state management.
Prevents input loops and repeated misinterpretation of user replies.
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class CreationStage(Enum):
    """Stages of the character creation process."""
    INITIAL = "initial"
    RACE_SELECTION = "race_selection"
    CLASS_SELECTION = "class_selection"
    BACKGROUND_SELECTION = "background_selection"
    ABILITY_SCORES = "ability_scores"
    PERSONALITY = "personality"
    EQUIPMENT = "equipment"
    REVIEW = "review"
    COMPLETE = "complete"

class InputIntent(Enum):
    """Classification of user input intent."""
    VIBE_PROMPT = "vibe_prompt"  # Initial full-text character concept
    FIELD_ANSWER = "field_answer"  # Answer to a structured question
    CORRECTION = "correction"  # Refinement of an earlier choice
    CLARIFICATION = "clarification"  # Asking for more information
    CONFIRMATION = "confirmation"  # Confirming a choice

@dataclass
class ConversationState:
    """Tracks the state of a character creation conversation."""
    session_id: str
    creation_stage: CreationStage
    character_description: str
    campaign_name: str
    current_question: str
    conversation_history: List[Dict[str, Any]]
    character_data: Dict[str, Any]
    last_response: str
    response_count: int
    created_date: datetime
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.character_data is None:
            self.character_data = {}
        if self.created_date is None:
            self.created_date = datetime.now()

class VibeCodeHandler:
    """
    Handles vibe code character creation with proper state management.
    """
    
    def __init__(self):
        self.logger = logger
        self.active_conversations: Dict[str, ConversationState] = {}
        
        # Define the creation flow
        self.creation_flow = [
            (CreationStage.RACE_SELECTION, "What race would you like to play?"),
            (CreationStage.CLASS_SELECTION, "What class would you like to play?"),
            (CreationStage.BACKGROUND_SELECTION, "What background does your character have?"),
            (CreationStage.ABILITY_SCORES, "How would you like to assign ability scores?"),
            (CreationStage.PERSONALITY, "Tell me about your character's personality."),
            (CreationStage.EQUIPMENT, "What equipment would you like to start with?"),
            (CreationStage.REVIEW, "Let me show you your character for review.")
        ]
    
    def classify_input_intent(self, user_input: str, conversation_state: ConversationState) -> InputIntent:
        """
        Classify the intent of user input to prevent misinterpretation.
        
        Args:
            user_input: The user's input text
            conversation_state: Current conversation state
            
        Returns:
            InputIntent classification
        """
        user_input_lower = user_input.lower().strip()
        
        # Check if this is an initial vibe prompt (longer, descriptive text)
        if (conversation_state.creation_stage == CreationStage.INITIAL and 
            len(user_input) > 20 and 
            any(word in user_input_lower for word in ['character', 'want', 'like', 'play', 'adventure', 'story'])):
            return InputIntent.VIBE_PROMPT
        
        # Check if this is a correction (mentions previous choices)
        if any(word in user_input_lower for word in ['change', 'different', 'instead', 'actually', 'correction']):
            return InputIntent.CORRECTION
        
        # Check if this is a confirmation
        if user_input_lower in ['yes', 'no', 'okay', 'sure', 'confirm', 'continue']:
            return InputIntent.CONFIRMATION
        
        # Check if this is a clarification request
        if any(word in user_input_lower for word in ['what', 'how', 'why', 'explain', 'clarify', 'question']):
            return InputIntent.CLARIFICATION
        
        # Default to field answer (short, specific response)
        return InputIntent.FIELD_ANSWER
    
    def detect_duplicate_response(self, user_input: str, conversation_state: ConversationState) -> bool:
        """
        Detect if this response is a duplicate of the last system response.
        
        Args:
            user_input: The user's input text
            conversation_state: Current conversation state
            
        Returns:
            True if this appears to be a duplicate response
        """
        if not conversation_state.conversation_history:
            return False
        
        # Check if user input matches the last system response
        last_system_response = conversation_state.last_response.lower()
        user_input_lower = user_input.lower()
        
        # Check for exact matches or very similar content
        if user_input_lower == last_system_response:
            return True
        
        # Check if user is echoing back the question
        if any(phrase in user_input_lower for phrase in ['what race', 'what class', 'what background']):
            return True
        
        return False
    
    def start_creation(self, session_id: str, description: str, campaign_name: str = "") -> Dict[str, Any]:
        """
        Start a new vibe code character creation session.
        
        Args:
            session_id: Unique session identifier
            description: Initial character description
            campaign_name: Optional campaign name
            
        Returns:
            Response data for the client
        """
        try:
            self.logger.info(f"Starting vibe code creation for session {session_id}")
            
            # Create conversation state
            conversation_state = ConversationState(
                session_id=session_id,
                creation_stage=CreationStage.INITIAL,
                character_description=description,
                campaign_name=campaign_name,
                current_question="",
                conversation_history=[],
                character_data={},
                last_response="",
                response_count=0
            )
            
            # Store the conversation state
            self.active_conversations[session_id] = conversation_state
            
            # Generate initial response
            response = self._generate_initial_response(description)
            conversation_state.last_response = response
            conversation_state.response_count += 1
            
            # Move to first stage
            conversation_state.creation_stage = CreationStage.RACE_SELECTION
            conversation_state.current_question = self.creation_flow[0][1]
            
            # Add to conversation history
            conversation_state.conversation_history.append({
                'role': 'system',
                'content': response,
                'timestamp': datetime.now().isoformat(),
                'stage': conversation_state.creation_stage.value
            })
            
            return {
                'success': True,
                'message': response,
                'is_complete': False,
                'session_id': session_id,
                'current_stage': conversation_state.creation_stage.value,
                'current_question': conversation_state.current_question
            }
            
        except Exception as e:
            self.logger.error(f"Error starting vibe code creation: {e}")
            return {
                'success': False,
                'message': 'Error starting character creation',
                'error': str(e)
            }
    
    def continue_creation(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        Continue the vibe code character creation conversation.
        
        Args:
            session_id: Session identifier
            user_input: User's input text
            
        Returns:
            Response data for the client
        """
        try:
            if session_id not in self.active_conversations:
                return {
                    'success': False,
                    'message': 'Session not found. Please start a new character creation.',
                    'error': 'session_not_found'
                }
            
            conversation_state = self.active_conversations[session_id]
            
            # Classify input intent
            input_intent = self.classify_input_intent(user_input, conversation_state)
            
            # Check for duplicate responses
            if self.detect_duplicate_response(user_input, conversation_state):
                self.logger.warning(f"Duplicate response detected for session {session_id}")
                return {
                    'success': True,
                    'message': "I see you've repeated my question. Let me clarify: " + conversation_state.current_question,
                    'is_complete': False,
                    'session_id': session_id,
                    'current_stage': conversation_state.creation_stage.value,
                    'current_question': conversation_state.current_question,
                    'input_intent': input_intent.value
                }
            
            # Add user input to conversation history
            conversation_state.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat(),
                'intent': input_intent.value
            })
            
            # Process input based on intent and stage
            response = self._process_input(user_input, input_intent, conversation_state)
            
            # Update conversation state
            conversation_state.last_response = response
            conversation_state.response_count += 1
            
            # Add system response to history
            conversation_state.conversation_history.append({
                'role': 'system',
                'content': response,
                'timestamp': datetime.now().isoformat(),
                'stage': conversation_state.creation_stage.value
            })
            
            return {
                'success': True,
                'message': response,
                'is_complete': conversation_state.creation_stage == CreationStage.COMPLETE,
                'session_id': session_id,
                'current_stage': conversation_state.creation_stage.value,
                'current_question': conversation_state.current_question,
                'input_intent': input_intent.value,
                'character_data': conversation_state.character_data if conversation_state.creation_stage == CreationStage.COMPLETE else None
            }
            
        except Exception as e:
            self.logger.error(f"Error continuing vibe code creation: {e}")
            return {
                'success': False,
                'message': 'Error continuing character creation',
                'error': str(e)
            }
    
    def _generate_initial_response(self, description: str) -> str:
        """Generate the initial response to a character description."""
        return f"I understand you want to create a character described as: '{description}'. Let me ask you some questions to flesh out the details. What race would you like to play?"
    
    def _process_input(self, user_input: str, input_intent: InputIntent, conversation_state: ConversationState) -> str:
        """
        Process user input based on intent and current stage.
        
        Args:
            user_input: User's input text
            input_intent: Classified intent of the input
            conversation_state: Current conversation state
            
        Returns:
            System response
        """
        current_stage = conversation_state.creation_stage
        
        # Handle corrections
        if input_intent == InputIntent.CORRECTION:
            return self._handle_correction(user_input, conversation_state)
        
        # Handle clarifications
        if input_intent == InputIntent.CLARIFICATION:
            return self._handle_clarification(user_input, conversation_state)
        
        # Handle confirmations
        if input_intent == InputIntent.CONFIRMATION:
            return self._handle_confirmation(user_input, conversation_state)
        
        # Handle field answers based on current stage
        if current_stage == CreationStage.RACE_SELECTION:
            return self._handle_race_selection(user_input, conversation_state)
        elif current_stage == CreationStage.CLASS_SELECTION:
            return self._handle_class_selection(user_input, conversation_state)
        elif current_stage == CreationStage.BACKGROUND_SELECTION:
            return self._handle_background_selection(user_input, conversation_state)
        elif current_stage == CreationStage.ABILITY_SCORES:
            return self._handle_ability_scores(user_input, conversation_state)
        elif current_stage == CreationStage.PERSONALITY:
            return self._handle_personality(user_input, conversation_state)
        elif current_stage == CreationStage.EQUIPMENT:
            return self._handle_equipment(user_input, conversation_state)
        elif current_stage == CreationStage.REVIEW:
            return self._handle_review(user_input, conversation_state)
        
        # Fallback
        return "I'm not sure how to process that input. Could you please clarify?"
    
    def _handle_race_selection(self, user_input: str, conversation_state: ConversationState) -> str:
        """Handle race selection input."""
        # Extract race from input (simplified - would use LLM in full implementation)
        race = user_input.strip().title()
        
        # Validate race
        valid_races = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling']
        if race not in valid_races:
            return f"I don't recognize '{race}' as a valid race. Please choose from: {', '.join(valid_races)}"
        
        # Store race
        conversation_state.character_data['race'] = race
        
        # Move to next stage
        conversation_state.creation_stage = CreationStage.CLASS_SELECTION
        conversation_state.current_question = self.creation_flow[1][1]
        
        return f"Great choice! A {race} character. {conversation_state.current_question}"
    
    def _handle_class_selection(self, user_input: str, conversation_state: ConversationState) -> str:
        """Handle class selection input."""
        class_name = user_input.strip().title()
        
        valid_classes = ['Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard']
        if class_name not in valid_classes:
            return f"I don't recognize '{class_name}' as a valid class. Please choose from: {', '.join(valid_classes)}"
        
        conversation_state.character_data['class'] = class_name
        conversation_state.creation_stage = CreationStage.BACKGROUND_SELECTION
        conversation_state.current_question = self.creation_flow[2][1]
        
        return f"Excellent! A {conversation_state.character_data['race']} {class_name}. {conversation_state.current_question}"
    
    def _handle_background_selection(self, user_input: str, conversation_state: ConversationState) -> str:
        """Handle background selection input."""
        background = user_input.strip().title()
        
        valid_backgrounds = ['Acolyte', 'Criminal', 'Folk Hero', 'Haunted One', 'Noble', 'Sage', 'Soldier', 'Urchin']
        if background not in valid_backgrounds:
            return f"I don't recognize '{background}' as a valid background. Please choose from: {', '.join(valid_backgrounds)}"
        
        conversation_state.character_data['background'] = background
        conversation_state.creation_stage = CreationStage.ABILITY_SCORES
        conversation_state.current_question = self.creation_flow[3][1]
        
        return f"Perfect! A {background} background. {conversation_state.current_question}"
    
    def _handle_ability_scores(self, user_input: str, conversation_state: ConversationState) -> str:
        """Handle ability scores input."""
        # For now, use standard array
        conversation_state.character_data['ability_scores'] = {
            'strength': 15,
            'dexterity': 14,
            'constitution': 13,
            'intelligence': 12,
            'wisdom': 10,
            'charisma': 8
        }
        
        conversation_state.creation_stage = CreationStage.PERSONALITY
        conversation_state.current_question = self.creation_flow[4][1]
        
        return f"I've assigned standard ability scores. {conversation_state.current_question}"
    
    def _handle_personality(self, user_input: str, conversation_state: ConversationState) -> str:
        """Handle personality input."""
        conversation_state.character_data['personality'] = user_input
        conversation_state.creation_stage = CreationStage.EQUIPMENT
        conversation_state.current_question = self.creation_flow[5][1]
        
        return f"Great personality! {conversation_state.current_question}"
    
    def _handle_equipment(self, user_input: str, conversation_state: ConversationState) -> str:
        """Handle equipment input."""
        conversation_state.character_data['equipment'] = user_input
        conversation_state.creation_stage = CreationStage.REVIEW
        conversation_state.current_question = self.creation_flow[6][1]
        
        return f"Equipment noted! {conversation_state.current_question}"
    
    def _handle_review(self, user_input: str, conversation_state: ConversationState) -> str:
        """Handle review stage."""
        conversation_state.creation_stage = CreationStage.COMPLETE
        
        # Generate character summary
        char_data = conversation_state.character_data
        summary = f"""
Character Summary:
- Name: {char_data.get('name', 'Unnamed')}
- Race: {char_data.get('race', 'Unknown')}
- Class: {char_data.get('class', 'Unknown')}
- Background: {char_data.get('background', 'Unknown')}
- Personality: {char_data.get('personality', 'Not specified')}
- Equipment: {char_data.get('equipment', 'Not specified')}
        """.strip()
        
        return f"Perfect! Here's your character:\n\n{summary}\n\nYour character is ready to begin their adventure!"
    
    def _handle_correction(self, user_input: str, conversation_state: ConversationState) -> str:
        """Handle correction input."""
        return "I understand you want to make a correction. What would you like to change?"
    
    def _handle_clarification(self, user_input: str, conversation_state: ConversationState) -> str:
        """Handle clarification input."""
        return f"Let me clarify: {conversation_state.current_question}"
    
    def _handle_confirmation(self, user_input: str, conversation_state: ConversationState) -> str:
        """Handle confirmation input."""
        return f"Confirmed! {conversation_state.current_question}"
    
    def get_conversation_state(self, session_id: str) -> Optional[ConversationState]:
        """Get the current conversation state for a session."""
        return self.active_conversations.get(session_id)
    
    def cleanup_session(self, session_id: str) -> bool:
        """Clean up a completed or abandoned session."""
        try:
            if session_id in self.active_conversations:
                del self.active_conversations[session_id]
                self.logger.info(f"Cleaned up session {session_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error cleaning up session {session_id}: {e}")
            return False

# Global instance
vibe_code_handler = VibeCodeHandler() 