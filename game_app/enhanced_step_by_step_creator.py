#!/usr/bin/env python3
"""
Enhanced Step-by-Step Character Creator for SoloHeart

Provides an improved interactive character creation experience with:
- Open-ended or multiple-choice prompts
- Questions about options with SRD-based summaries
- Suggestions for beginners
- Value confirmation before committing
- Fallbacks for "I don't know" responses
- Full SRD 5.2 compliance
- Vibe code compatibility
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from .character_sheet import CharacterSheet, Alignment
from .interactive_character_creator import InteractiveCharacterCreator

logger = logging.getLogger(__name__)

class EnhancedStepByStepCreator:
    """
    Enhanced step-by-step character creation with improved interactivity.
    
    Features:
    - Interactive prompts with multiple input methods
    - SRD-based option exploration
    - Confirmation before committing values
    - Fallback options for uncertain users
    - Full integration with CharacterSheet and SRD data
    """
    
    def __init__(self):
        self.interactive_creator = InteractiveCharacterCreator()
        self.current_state = "prompting"  # prompting, confirming, asking_question
        self.pending_confirmation = None
        self.current_question = None
        
    def start_creation(self) -> str:
        """Start the enhanced character creation process."""
        return self.interactive_creator.get_current_prompt()
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input and return appropriate response."""
        user_input_lower = user_input.lower().strip()
        
        # Handle state-specific processing
        if self.current_state == "confirming":
            return self._handle_confirmation(user_input)
        elif self.current_state == "asking_question":
            return self._handle_question_response(user_input)
        else:
            return self._handle_prompt_input(user_input)
    
    def _handle_prompt_input(self, user_input: str) -> Dict[str, Any]:
        """Handle input during the prompting phase."""
        result = self.interactive_creator.process_interactive_input(user_input)
        
        if result["type"] == "confirmation_request":
            self.current_state = "confirming"
            self.pending_confirmation = {
                "field": result["field"],
                "value": result["value"]
            }
            return {
                "type": "confirmation_prompt",
                "message": result["message"],
                "field": result["field"],
                "value": result["value"]
            }
        
        elif result["type"] == "fallback":
            self.current_state = "confirming"
            self.pending_confirmation = {
                "field": result["field"],
                "value": result["value"]
            }
            return {
                "type": "fallback_confirmation",
                "message": result["message"],
                "field": result["field"],
                "value": result["value"]
            }
        
        elif result["type"] == "question_response":
            return {
                "type": "information",
                "message": result["message"],
                "next_prompt": self.interactive_creator.get_current_prompt()
            }
        
        elif result["type"] == "help":
            return {
                "type": "help",
                "message": result["message"],
                "next_prompt": self.interactive_creator.get_current_prompt()
            }
        
        elif result["type"] == "validation_error":
            return {
                "type": "error",
                "message": result["message"],
                "next_prompt": self.interactive_creator.get_current_prompt()
            }
        
        else:
            return {
                "type": "unknown",
                "message": "I didn't understand that. Please try again.",
                "next_prompt": self.interactive_creator.get_current_prompt()
            }
    
    def _handle_confirmation(self, user_input: str) -> Dict[str, Any]:
        """Handle confirmation responses."""
        user_input_lower = user_input.lower().strip()
        
        if user_input_lower in ['yes', 'confirm', 'ok', 'sure', 'y']:
            # Commit the value and advance
            field = self.pending_confirmation["field"]
            value = self.pending_confirmation["value"]
            
            # Update the character sheet
            self.interactive_creator._update_character_field(field, value)
            
            # Advance to next step
            if self.interactive_creator.advance_step():
                self.current_state = "prompting"
                self.pending_confirmation = None
                
                return {
                    "type": "step_completed",
                    "message": f"Great! {field.title()} set to '{value}'. Moving to the next step.",
                    "next_prompt": self.interactive_creator.get_current_prompt(),
                    "character_summary": self.interactive_creator.get_character_summary()
                }
            else:
                # Character creation complete
                final_character = self.interactive_creator.finalize_character()
                return {
                    "type": "creation_complete",
                    "message": "🎉 Character creation complete! Your character is ready for adventure!",
                    "character": final_character.to_dict()
                }
        
        elif user_input_lower in ['no', 'nope', 'choose again', 'n']:
            self.current_state = "prompting"
            self.pending_confirmation = None
            
            return {
                "type": "rejection",
                "message": "No problem! Let's choose again.",
                "next_prompt": self.interactive_creator.get_current_prompt()
            }
        
        else:
            return {
                "type": "confirmation_clarification",
                "message": "Please type 'yes' to confirm or 'no' to choose again.",
                "field": self.pending_confirmation["field"],
                "value": self.pending_confirmation["value"]
            }
    
    def _handle_question_response(self, user_input: str) -> Dict[str, Any]:
        """Handle responses during question phase."""
        # For now, treat as regular input
        self.current_state = "prompting"
        return self._handle_prompt_input(user_input)
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current creation status."""
        return {
            "current_step": self.interactive_creator.current_step,
            "total_steps": len(self.interactive_creator.creation_steps),
            "current_state": self.current_state,
            "character_summary": self.interactive_creator.get_character_summary(),
            "pending_confirmation": self.pending_confirmation
        }
    
    def get_help_for_current_step(self) -> str:
        """Get help for the current step."""
        current_step = self.interactive_creator.creation_steps[self.interactive_creator.current_step]
        return self.interactive_creator.get_help_for_field(current_step)
    
    def get_suggestion_for_current_step(self, context: str = "") -> str:
        """Get a suggestion for the current step."""
        current_step = self.interactive_creator.creation_steps[self.interactive_creator.current_step]
        return self.interactive_creator.get_suggestion_for_field(current_step, context)
    
    def reset_creation(self) -> str:
        """Reset the character creation process."""
        self.interactive_creator = InteractiveCharacterCreator()
        self.current_state = "prompting"
        self.pending_confirmation = None
        self.current_question = None
        return self.interactive_creator.get_current_prompt()
    
    def get_character_sheet(self) -> CharacterSheet:
        """Get the current character sheet."""
        return self.interactive_creator.character_sheet
    
    def is_complete(self) -> bool:
        """Check if character creation is complete."""
        return self.interactive_creator.current_step >= len(self.interactive_creator.creation_steps) 