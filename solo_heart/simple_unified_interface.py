#!/usr/bin/env python3
"""
Simple Unified SoloHeart Narrative Interface
A single Flask server that provides the complete immersive SoloHeart experience.
"""

import os
import json
import logging
import uuid
import datetime
import re
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from ollama_llm_service import chat_completion
from utils.character_fact_extraction import (
    extract_race_from_text,
    extract_class_from_text,
    extract_background_from_text,
    extract_name_from_text,
    extract_emotional_themes,
    extract_combat_style,
    extract_traits,
    extract_motivations
)
# Temporarily disable Narrative Engine integration for basic functionality
# from narrative_engine_integration import SoloHeartNarrativeEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ollama LLM service - no fallbacks, must be available

def check_system_requirements():
    """Check that all system requirements are met."""
    logger.info("🔍 Checking system requirements...")
    
    # Check if port 5001 is available
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 5001))
        sock.close()
        logger.info("✅ Port 5001 is available")
    except OSError:
        # Only clear port if we're not in Flask debug mode (which restarts)
        if not os.environ.get('FLASK_ENV') == 'development':
            logger.error("❌ Port 5001 is already in use")
            logger.info("💡 Stopping conflicting processes...")
            os.system("lsof -ti:5001 | xargs kill -9 2>/dev/null")
            logger.info("✅ Port 5001 cleared")
        else:
            logger.info("⚠️ Port 5001 in use (likely Flask restart) - continuing...")
    
    # Check Ollama connection
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            if 'llama3:latest' in model_names:
                logger.info("✅ Ollama is running with llama3 model")
            else:
                logger.warning("⚠️ Ollama is running but llama3 model not found")
                logger.info("💡 Run: ollama pull llama3")
        else:
            raise Exception(f"Ollama health check failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Ollama connection failed: {e}")
        logger.error("💡 Please start Ollama with: brew services start ollama")
        logger.error("💡 Or install with: brew install ollama")
        raise Exception("System requirements not met")
    
    logger.info("✅ All system requirements met")

# Run system checks at startup (only on initial start, not Flask restarts)
if not os.environ.get('WERKZEUG_RUN_MAIN'):
    try:
        check_system_requirements()
    except Exception as e:
        logger.error(f"❌ System check failed: {e}")
        logger.error("Please fix the issues above before starting the game")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'unified-narrative-key')

class SimpleCharacterGenerator:
    """Simple character generator for step-by-step guided character creation with immediate fact commitment."""
    
    def __init__(self, playtest_mode: bool = None):
        self.conversation_history = []
        self.character_data = {
            "name": "Adventurer",
            "race": "Unknown",
            "class": "Unknown",
            "level": 1,
            "background": "Unknown",
            "alignment": "Neutral",
            "personality": "A brave adventurer",
            "age": None,
            "ability_scores": {
                "strength": 10, "dexterity": 10, "constitution": 10,
                "intelligence": 10, "wisdom": 10, "charisma": 10
            },
            "hit_points": 10,
            "armor_class": 10,
            "saving_throws": [],
            "skills": [],
            "feats": [],
            "weapons": [],
            "gear": [],
            "spells": [],
            "background_freeform": "",
            "created_date": None
        }
        self.is_complete = False
        self.character_finalized = False
        self.in_review_mode = False
        self.confirmed_facts = set()
        self.narrative_bridge = None
        self.fact_history = []
        
        # Enhanced fact tracking
        self.fact_types = {
            "name": {"required": True, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "race": {"required": True, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "class": {"required": True, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "background": {"required": True, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "personality": {"required": True, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "age": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "alignment": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None}
        }
        
        # Session tracking
        self.session_id = str(uuid.uuid4())
        self.session_start_time = datetime.datetime.now()
        self.validation_pending = False
        self.pending_facts = {}
        
        # Draft saving
        self.draft_saved = False
        self.draft_id = None
        
        if playtest_mode is None:
            playtest_mode = os.environ.get('PLAYTEST_LOG', '0') == '1'
        self.playtest_mode = playtest_mode
        
        # Ensure logs directory exists
        os.makedirs("logs/character_creation_sessions", exist_ok=True)
    
    def _log(self, method, *args, **kwargs):
        # Logging disabled - removed playtest logger
        pass
    
    def _get_current_step(self) -> str:
        """Get the current step in character creation."""
        if self.current_step_index < len(self.creation_steps):
            return self.creation_steps[self.current_step_index]
        return "complete"
    
    def _get_next_step_prompt(self) -> str:
        """Generate the appropriate prompt for the current step."""
        current_step = self._get_current_step()
        
        if current_step == "race":
            return "What race would you like to be? Your options include: Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, and Tiefling. Each race has unique abilities and traits."
        
        elif current_step == "class":
            race = self.character_data.get("race", "Unknown")
            return f"Great! You're a {race}. What class would you like to be? Your options include: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, and Wizard. Each class has different abilities and playstyles."
        
        elif current_step == "name":
            race = self.character_data.get("race", "Unknown")
            char_class = self.character_data.get("class", "Unknown")
            return f"Perfect! You're a {race} {char_class}. What's your character's name?"
        
        elif current_step == "background":
            name = self.character_data.get("name", "Adventurer")
            race = self.character_data.get("race", "Unknown")
            char_class = self.character_data.get("class", "Unknown")
            return f"Excellent! {name} the {race} {char_class}. What background does your character have? Your options include: Acolyte, Criminal, Folk Hero, Noble, Sage, Soldier, or you can describe a custom background."
        
        elif current_step == "personality":
            name = self.character_data.get("name", "Adventurer")
            return f"Great! Now tell me about {name}'s personality. What are they like? Are they brave, cautious, friendly, mysterious, or something else? Describe their character and temperament."
        
        elif current_step == "ability_scores":
            name = self.character_data.get("name", "Adventurer")
            char_class = self.character_data.get("class", "Unknown")
            return f"Perfect! Now let's assign {name}'s ability scores. As a {char_class}, you'll want to focus on certain abilities. I can suggest scores based on your class, or you can choose your own method. Would you like me to suggest optimal scores for a {char_class}, or do you have a preference for how to assign them?"
        
        else:
            return "Character creation is complete! Let's review your character."
    
    def _extract_and_stage_all_facts(self, text: str) -> None:
        """Extract all possible facts from text input and stage them for user confirmation."""
        logger.info(f"🔍 Extracting all possible facts from: '{text}'")
        self.pending_facts = {}
        ambiguous = []
        contradictions = []
        
        # Use all extractors
        extractors = {
            'name': extract_name_from_text,
            'race': extract_race_from_text,
            'class': extract_class_from_text,
            'background': extract_background_from_text,
        }
        
        # Extract facts using utility functions
        for fact_type, extractor in extractors.items():
            try:
                result = extractor(text)
                if result:
                    self.pending_facts[fact_type] = result
                    logger.info(f"✅ Extracted {fact_type}: {result}")
            except Exception as e:
                logger.warning(f"⚠️ Error extracting {fact_type}: {e}")
        
        # Extract personality from the full text if no specific personality was found
        if 'personality' not in self.pending_facts:
            # Use the full text as personality if it contains emotional content
            emotional_themes = extract_emotional_themes(text)
            if emotional_themes or any(word in text.lower() for word in ['angry', 'sad', 'happy', 'fear', 'love', 'hate', 'trust', 'betray']):
                self.pending_facts['personality'] = text.strip()
                logger.info(f"✅ Extracted personality from full text")
        
        # Extract combat style
        combat_style = extract_combat_style(text)
        if combat_style:
            self.pending_facts['combat_style'] = combat_style
            logger.info(f"✅ Extracted combat style: {combat_style}")
        
        # Extract traits
        traits = extract_traits(text)
        if traits:
            self.pending_facts['traits'] = traits
            logger.info(f"✅ Extracted traits: {traits}")
        
        # Extract motivations (but don't stage for confirmation - store directly)
        motivations = extract_motivations(text)
        if motivations:
            self.character_data['motivations'] = motivations
            logger.info(f"✅ Extracted motivations: {motivations}")
        
        # Check for contradictions with existing character data
        for fact_type, new_value in self.pending_facts.items():
            old_value = self.character_data.get(fact_type)
            if old_value and old_value != new_value:
                if old_value != 'Unknown' and old_value != 'Adventurer':
                    contradictions.append(f"{fact_type}: {old_value} vs {new_value}")
        
        # Log the extraction results
        if self.pending_facts:
            logger.info(f"📋 Staged facts: {self.pending_facts}")
        if contradictions:
            logger.warning(f"⚠️ Contradictions detected: {contradictions}")
        if not self.pending_facts:
            logger.info("ℹ️ No new facts extracted")
        
        return self.pending_facts, contradictions

    def _build_confirmation_prompt(self, facts: dict, contradictions: list) -> str:
        """Build a user-friendly confirmation prompt for all staged facts."""
        if not facts:
            return "I couldn't extract any new details from that. Could you rephrase or provide more information?"
        
        lines = ["Here's what I gathered:"]
        lines.append("")
        
        # Define the order to display facts
        fact_order = ['name', 'race', 'class', 'background', 'personality', 'combat_style', 'traits']
        
        for fact_type in fact_order:
            if fact_type in facts:
                value = facts[fact_type]
                if fact_type == 'traits' and isinstance(value, list):
                    # Handle traits as a list
                    traits_str = ', '.join(value)
                    lines.append(f"    • Traits: {traits_str}")
                else:
                    # Handle other facts as strings
                    lines.append(f"    • {fact_type.title()}: {value}")
        
        lines.append("")
        lines.append("Does that look right? You can say 'yes,' or tell me what to change.")
        
        return "\n".join(lines)

    def _extract_and_commit_facts_from_text(self, text: str) -> None:
        """Extract and stage facts from text input for validation, including corrections and removals."""
        logger.info(f"🔍 Extracting and staging facts from: '{text}'")
        self.pending_facts = {}
        
        # Check for corrections first (e.g., "Actually, he's 20, not 18")
        corrections = self._detect_corrections(text)
        if corrections:
            for fact_type, new_value in corrections.items():
                self.pending_facts[fact_type] = {
                    'value': new_value,
                    'source_text': text,
                    'is_correction': True,
                    'old_value': self.character_data.get(fact_type)
                }
            logger.info(f"✅ Detected corrections: {corrections}")
            return
        
        # Check for fact removals (e.g., "Remove the backstory", "Take out the part about...")
        removals = self._detect_removals(text)
        if removals:
            for fact_type in removals:
                self.pending_facts[fact_type] = {
                    'value': None,
                    'source_text': text,
                    'is_removal': True,
                    'old_value': self.character_data.get(fact_type)
                }
            logger.info(f"✅ Detected removals: {removals}")
            return
        
        # Check for fact expansions (e.g., "Add that he has a younger sister")
        expansions = self._detect_expansions(text)
        if expansions:
            for fact_type, expansion_text in expansions.items():
                current_value = self.character_data.get(fact_type, "")
                if current_value:
                    new_value = f"{current_value}. {expansion_text}"
                else:
                    new_value = expansion_text
                self.pending_facts[fact_type] = {
                    'value': new_value,
                    'source_text': text,
                    'is_expansion': True,
                    'old_value': current_value
                }
            logger.info(f"✅ Detected expansions: {expansions}")
            return
        
        # Regular fact extraction (existing logic)
        for fact_type in self.fact_types:
            if not self.fact_types[fact_type]['extracted']:
                extractor = globals().get(f"extract_{fact_type}_from_text", None)
                if extractor:
                    value = extractor(text)
                    if value:
                        self.pending_facts[fact_type] = {
                            'value': value,
                            'source_text': text
                        }
        
        # If nothing extracted, fallback to personality guess
        if not self.pending_facts and len(text.strip().split()) > 1:
            if not self.fact_types['personality']['extracted']:
                self.pending_facts['personality'] = {'value': text.strip(), 'source_text': text}
        
        # Log all staged facts
        for k, v in self.pending_facts.items():
            self._log_fact_extraction(k, v['value'], v['source_text'])

    def _detect_corrections(self, text: str) -> Dict[str, str]:
        """Detect correction patterns in text."""
        corrections = {}
        text_lower = text.lower()
        
        # Pattern: "Actually, he's 20, not 18" or "Make her a sorcerer instead"
        correction_patterns = [
            (r"actually[,:]?\s+(?:he'?s|she'?s|they'?re|it'?s|he\s+is|she\s+is|they\s+are)\s+(\d+)(?:,\s*not\s+(\d+))?", "age"),
            (r"actually[,:]?\s+(?:he'?s|she'?s|they'?re|he\s+is|she\s+is|they\s+are)\s+(human|elf|dwarf|halfling|dragonborn|gnome|half-elf|half-orc|tiefling)", "race"),
            (r"make\s+(?:him|her|them)\s+(human|elf|dwarf|halfling|dragonborn|gnome|half-elf|half-orc|tiefling)", "race"),
            (r"actually[,:]?\s+(?:he'?s|she'?s|they'?re|he\s+is|she\s+is|they\s+are)\s+(barbarian|bard|cleric|druid|fighter|monk|paladin|ranger|rogue|sorcerer|warlock|wizard)", "class"),
            (r"make\s+(?:him|her|them)\s+(barbarian|bard|cleric|druid|fighter|monk|paladin|ranger|rogue|sorcerer|warlock|wizard)", "class"),
            (r"actually[,:]?\s+(?:his|her|their)\s+name\s+is\s+([a-z]+)", "name"),
            (r"call\s+(?:him|her|them)\s+([a-z]+)", "name"),
            (r"actually[,:]?\s+(?:he'?s|she'?s|they'?re|he\s+is|she\s+is|they\s+are)\s+(acolyte|criminal|folk hero|noble|sage|soldier)", "background"),
            (r"make\s+(?:his|her|their)\s+background\s+(acolyte|criminal|folk hero|noble|sage|soldier)", "background")
        ]
        
        for pattern, fact_type in correction_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if fact_type == "age":
                    corrections["age"] = match.group(1)
                else:
                    corrections[fact_type] = match.group(1).title()
        
        return corrections

    def _detect_removals(self, text: str) -> List[str]:
        """Detect removal patterns in text."""
        removals = []
        text_lower = text.lower()
        
        removal_patterns = [
            (r"remove\s+(?:the\s+)?(backstory|personality|age|name|race|class|background)", r"\1"),
            (r"take\s+out\s+(?:the\s+)?(backstory|personality|age|name|race|class|background)", r"\1"),
            (r"delete\s+(?:the\s+)?(backstory|personality|age|name|race|class|background)", r"\1"),
            (r"forget\s+(?:about\s+)?(?:the\s+)?(backstory|personality|age|name|race|class|background)", r"\1"),
            (r"don'?t\s+include\s+(?:the\s+)?(backstory|personality|age|name|race|class|background)", r"\1")
        ]
        
        for pattern, fact_type in removal_patterns:
            if re.search(pattern, text_lower):
                removals.append(fact_type)
        
        return removals

    def _detect_expansions(self, text: str) -> Dict[str, str]:
        """Detect expansion patterns in text."""
        expansions = {}
        text_lower = text.lower()
        
        expansion_patterns = [
            (r"add\s+that\s+(?:he|she|they)\s+(.+?)(?:\.|$)", "personality"),
            (r"include\s+that\s+(?:he|she|they)\s+(.+?)(?:\.|$)", "personality"),
            (r"also\s+(?:he|she|they)\s+(.+?)(?:\.|$)", "personality"),
            (r"additionally[,:]?\s+(.+?)(?:\.|$)", "personality")
        ]
        
        for pattern, fact_type in expansion_patterns:
            match = re.search(pattern, text_lower)
            if match:
                expansions[fact_type] = match.group(1).strip()
        
        return expansions

    def _handle_contradictory_info(self, fact_type: str, new_value: str, old_value: str) -> str:
        """Handle contradictory information by asking for clarification."""
        clarification_prompts = {
            "age": f"You mentioned {old_value} before, but now you've said {new_value}. Which age would you like to keep?",
            "race": f"You mentioned {old_value} before, but now you've said {new_value}. Which race would you like to keep?",
            "class": f"You mentioned {old_value} before, but now you've said {new_value}. Which class would you like to keep?",
            "name": f"You mentioned {old_value} before, but now you've said {new_value}. Which name would you like to keep?",
            "background": f"You mentioned {old_value} before, but now you've said {new_value}. Which background would you like to keep?",
            "personality": f"You mentioned '{old_value}' before, but now you've said '{new_value}'. Which personality description would you like to keep?"
        }
        
        return clarification_prompts.get(fact_type, f"You mentioned {old_value} before, but now you've said {new_value}. Which would you like to keep?")

    def confirm_pending_facts(self, corrections=None):
        """Commit pending facts after user confirmation/correction with enhanced logging."""
        if corrections:
            for k, v in corrections.items():
                if v is None:
                    # Remove fact
                    old_value = self.character_data.get(k)
                    self._log_fact_removal(k, old_value)
                    if k in self.character_data:
                        del self.character_data[k]
                    continue
                else:
                    # Update fact
                    old_value = self.character_data.get(k)
                    if old_value and old_value != v:
                        # Log the correction
                        self._log_fact_correction(k, old_value, v)
                    self.character_data[k] = v
                    self._log_fact_addition(k, v)
        else:
            # Commit all pending facts
            for fact_type, value in self.pending_facts.items():
                old_value = self.character_data.get(fact_type)
                if old_value and old_value != value:
                    # Log the correction
                    self._log_fact_correction(fact_type, old_value, value)
                self.character_data[fact_type] = value
                self._log_fact_addition(fact_type, value)
        
        # Clear pending facts
        self.pending_facts = {}
        
        # Ensure motivations are preserved (they're stored directly, not staged)
        if 'motivations' not in self.character_data:
            self.character_data['motivations'] = []
        
        logger.info(f"✅ Facts committed to character_data: {self.character_data}")
        
        # Log the confirmation
        self._log('fact_confirmation', {'facts': self.character_data})
        
        return True

    def _log_fact_correction(self, fact_type: str, old_value: str, new_value: str):
        """Log a fact correction with timestamp."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            'event': 'fact_correction',
            'fact_type': fact_type,
            'old_value': old_value,
            'new_value': new_value,
            'timestamp': timestamp
        }
        self._write_log_entry(log_entry)
        logger.info(f"📝 [CORRECTION] {fact_type}: {old_value} → {new_value} @ {timestamp}")

    def _log_fact_removal(self, fact_type: str, old_value: str):
        """Log a fact removal with timestamp."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            'event': 'fact_removal',
            'fact_type': fact_type,
            'old_value': old_value,
            'timestamp': timestamp
        }
        self._write_log_entry(log_entry)
        logger.info(f"🗑️ [REMOVAL] {fact_type}: {old_value} @ {timestamp}")

    def _log_fact_addition(self, fact_type: str, value: str):
        """Log a fact addition with timestamp."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            'event': 'fact_addition',
            'fact_type': fact_type,
            'value': value,
            'timestamp': timestamp
        }
        self._write_log_entry(log_entry)
        logger.info(f"➕ [ADDITION] {fact_type}: {value} @ {timestamp}")

    def _write_log_entry(self, log_entry: Dict[str, Any]):
        """Write a log entry to the session log file."""
        try:
            log_file = f"logs/character_creation_sessions/{self.session_id}.jsonl"
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing log entry: {e}")

    def get_fact_summary(self):
        """Return a summary of all committed facts."""
        summary = []
        
        # Check for committed facts in character_data
        if self.character_data.get('name') and self.character_data['name'] != 'Adventurer':
            summary.append(f"**Name**: {self.character_data['name']}")
        
        if self.character_data.get('race') and self.character_data['race'] != 'Unknown':
            summary.append(f"**Race**: {self.character_data['race']}")
        
        if self.character_data.get('class') and self.character_data['class'] != 'Unknown':
            summary.append(f"**Class**: {self.character_data['class']}")
        
        if self.character_data.get('background') and self.character_data['background'] != 'Unknown':
            summary.append(f"**Background**: {self.character_data['background']}")
        
        if self.character_data.get('personality') and self.character_data['personality'] != 'A brave adventurer':
            summary.append(f"**Personality**: {self.character_data['personality']}")
        
        if self.character_data.get('combat_style'):
            summary.append(f"**Combat Style**: {self.character_data['combat_style']}")
        
        if self.character_data.get('traits'):
            traits_str = ', '.join(self.character_data['traits'])
            summary.append(f"**Traits**: {traits_str}")
        
        if self.character_data.get('motivations'):
            motivations_str = ', '.join(self.character_data['motivations'])
            summary.append(f"**Motivations**: {motivations_str}")
        
        if not summary:
            summary.append("No facts have been confirmed yet.")
        
        return summary

    def save_draft(self):
        try:
            self.draft_saved = True
            self.draft_id = self.session_id
            self._log_session_event('draft_saved', {'character_data': self.character_data})
            # Calculate % complete
            total = len([k for k in self.fact_types if self.fact_types[k]['required']])
            filled = len([k for k in self.fact_types if self.fact_types[k]['required'] and self.fact_types[k]['extracted']])
            percent_complete = int((filled / total) * 100) if total else 0
            metadata = {
                'character_name': self.character_data.get('name', 'Adventurer'),
                'status': 'draft',
                'percent_complete': percent_complete,
                'session_id': self.session_id,
                'session_start_time': str(self.session_start_time),
                'session_end_time': str(datetime.datetime.now()),
                'fact_types': self.fact_types,
                'character_data': self.character_data
            }
            draft_path = f"logs/character_creation_sessions/{self.session_id}.jsonl"
            with open(draft_path, 'w') as f:
                f.write('# ' + json.dumps(metadata) + '\n')
            return True
        except Exception as e:
            logger.error(f"Error saving draft: {e}")
            return False

    def finalize_character(self):
        try:
            if not self.is_character_complete():
                return {
                    "success": False,
                    "message": "Character is not complete. Please fill in all required fields."
                }
            if not self.in_review_mode:
                return {
                    "success": False,
                    "message": "Character must be in review mode before finalization."
                }
            self.character_finalized = True
            self.in_review_mode = False
            # Memory storage disabled - removed vector memory system
            pass
            logger.info(f"Character finalized: {self.character_data['name']}")
            return {
                "success": True,
                "message": f"Character {self.character_data['name']} is now finalized and ready for adventure!",
                "character_data": self.character_data
            }
        except Exception as e:
            logger.error(f"Error finalizing character: {e}")
            return {
                "success": False,
                "message": "Error finalizing character."
            }
    
    def _extract_multiple_facts(self, user_input: str) -> Dict[str, str]:
        """Extract multiple facts from user input, prioritizing unconfirmed facts."""
        logger.info(f"🔍 Extracting multiple facts from: '{user_input}'")
        
        extracted_facts = {}
        user_input_lower = user_input.lower()
        
        # Get the order of steps we need to fill
        steps_needed = self._get_unknown_facts_list()
        logger.info(f"Steps still needed: {steps_needed}")
        
        # Extract race if needed
        if "Race" in steps_needed:
            extracted_race = extract_race_from_text(user_input)
            if extracted_race:
                extracted_facts["race"] = extracted_race
                logger.info(f"✅ Race detected: {extracted_race}")
        
        # Extract class if needed
        if "Class" in steps_needed:
            extracted_class = extract_class_from_text(user_input)
            if extracted_class:
                extracted_facts["class"] = extracted_class
                logger.info(f"✅ Class detected: {extracted_class}")
        
        # Extract name if needed
        if "Name" in steps_needed:
            extracted_name = extract_name_from_text(user_input)
            if extracted_name:
                extracted_facts["name"] = extracted_name
                logger.info(f"✅ Name detected: {extracted_name}")
        
        # Extract background if needed
        if "Background" in steps_needed:
            extracted_background = extract_background_from_text(user_input)
            if extracted_background:
                extracted_facts["background"] = extracted_background
                logger.info(f"✅ Background detected: {extracted_background}")
            else:
                # For custom backgrounds, check if the input looks like a background description
                # and we haven't extracted other facts that would make this a name/race/class
                if not extracted_facts and len(user_input.strip().split()) > 2:
                    extracted_facts["background"] = user_input.strip()
                    logger.info(f"✅ Custom background detected: {user_input.strip()}")
        
        # Extract personality if needed
        if "Personality" in steps_needed:
            # Only extract personality if we haven't extracted other facts
            # and the input looks like a personality description
            if not extracted_facts and len(user_input.strip().split()) > 1:
                extracted_facts["personality"] = user_input.strip()
                logger.info(f"✅ Personality detected: {user_input.strip()}")
        
        logger.info(f"📋 Total facts extracted: {extracted_facts}")
        return extracted_facts
    
    def _extract_single_fact(self, user_input: str, step: str) -> Optional[str]:
        """Extract a single fact from user input for the current step."""
        user_input_lower = user_input.lower()
        logger.info(f"🔍 Extracting {step} from: '{user_input}'")
        
        if step == "race":
            # Use the centralized race extraction utility
            extracted_race = extract_race_from_text(user_input)
            if extracted_race:
                logger.info(f"✅ Race detected: {extracted_race}")
                return extracted_race
            else:
                logger.warning(f"⚠️ No race detected in: '{user_input}'")
                return None
        
        elif step == "class":
            # Use the centralized class extraction utility
            extracted_class = extract_class_from_text(user_input)
            if extracted_class:
                logger.info(f"✅ Class detected: {extracted_class}")
                return extracted_class
            else:
                logger.warning(f"⚠️ No class detected in: '{user_input}'")
                return None
        
        elif step == "name":
            # Use the centralized name extraction utility
            extracted_name = extract_name_from_text(user_input)
            if extracted_name:
                logger.info(f"✅ Name detected: {extracted_name}")
                return extracted_name
            else:
                logger.warning(f"⚠️ No name detected in: '{user_input}'")
                return None
        
        elif step == "background":
            # Use the centralized background extraction utility
            extracted_background = extract_background_from_text(user_input)
            if extracted_background:
                logger.info(f"✅ Background detected: {extracted_background}")
                return extracted_background
            else:
                # For custom backgrounds, return the input as-is
                logger.info(f"✅ Custom background detected: {user_input.strip()}")
                return user_input.strip()
        
        elif step == "personality":
            # For personality, return the input as-is
            return user_input.strip()
        
        return None
    
    def _commit_step_fact(self, step: str, value: str) -> None:
        """Commit a fact for the current step and advance to the next step."""
        try:
            old_value = self.character_data.get(step)
            self.fact_history.append((step, old_value))
            logger.info(f"💾 Committing {step} = {value} (old value: {old_value})")
            
            if step == "name":
                self.character_data["name"] = value
            elif step == "race":
                self.character_data["race"] = value
                logger.info(f"🎯 RACE COMMITTED: {value}")
            elif step == "class":
                self.character_data["class"] = value
                self.character_data["saving_throws"] = self._get_class_saving_throws(value)
                self.character_data["skills"] = self._get_class_skills(value)
                weapons, gear, spells = self._generate_equipment(value)
                self.character_data["weapons"] = weapons
                self.character_data["gear"] = gear
                self.character_data["spells"] = spells
                self.character_data["ability_scores"] = self._generate_ability_scores(value)
            elif step == "background":
                self.character_data["background"] = value
            elif step == "personality":
                self.character_data["personality"] = value
            
            self.confirmed_facts.add(step)
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            logger.info(f"✅ [STEP COMMIT] {step} = {value} (replaced: {old_value}) @ {timestamp}")
            
            # Store in memory for persistence
            self._store_character_fact_in_memory(step, value, "player")
            
            # Advance to next step
            self.current_step_index += 1
            
        except Exception as e:
            logger.error(f"Error committing step fact {step}: {e}")
    
    def _generate_ability_score_suggestions(self, char_class: str) -> Dict[str, int]:
        """Generate suggested ability scores based on class."""
        suggestions = {
            "strength": 10, "dexterity": 10, "constitution": 12,
            "intelligence": 10, "wisdom": 10, "charisma": 10
        }
        
        # Class-specific suggestions
        if char_class == "Fighter":
            suggestions.update({"strength": 16, "constitution": 14, "dexterity": 12})
        elif char_class == "Wizard":
            suggestions.update({"intelligence": 16, "constitution": 12, "dexterity": 12})
        elif char_class == "Paladin":
            suggestions.update({"strength": 16, "charisma": 14, "constitution": 12})
        elif char_class == "Rogue":
            suggestions.update({"dexterity": 16, "intelligence": 12, "constitution": 12})
        elif char_class == "Cleric":
            suggestions.update({"wisdom": 16, "constitution": 12, "strength": 12})
        elif char_class == "Bard":
            suggestions.update({"charisma": 16, "dexterity": 14, "constitution": 12})
        elif char_class == "Monk":
            suggestions.update({"dexterity": 16, "wisdom": 14, "constitution": 12})
        elif char_class == "Ranger":
            suggestions.update({"dexterity": 16, "wisdom": 14, "constitution": 12})
        elif char_class == "Sorcerer":
            suggestions.update({"charisma": 16, "constitution": 12, "dexterity": 12})
        elif char_class == "Warlock":
            suggestions.update({"charisma": 16, "constitution": 12, "dexterity": 12})
        elif char_class == "Barbarian":
            suggestions.update({"strength": 16, "constitution": 14, "dexterity": 12})
        elif char_class == "Druid":
            suggestions.update({"wisdom": 16, "constitution": 12, "dexterity": 12})
        
        return suggestions
    
    def _get_step_confirmation(self, step: str, value: str) -> str:
        """Generate a confirmation message for the committed fact."""
        if step == "race":
            return f"Excellent! You are a {value}."
        elif step == "class":
            race = self.character_data.get("race", "Unknown")
            return f"Perfect! You are a {race} {value}."
        elif step == "name":
            race = self.character_data.get("race", "Unknown")
            char_class = self.character_data.get("class", "Unknown")
            return f"Great! {value} the {race} {char_class}."
        elif step == "background":
            name = self.character_data.get("name", "Adventurer")
            return f"Wonderful! {name} has a {value} background."
        elif step == "personality":
            name = self.character_data.get("name", "Adventurer")
            return f"Perfect! {name} is {value}."
        else:
            return f"Great! {step} set to {value}."
    
    def _get_clarification_prompt(self, step: str, user_input: str) -> str:
        """Generate a clarification prompt when fact extraction fails."""
        if step == "race":
            return f"I didn't quite catch that. Could you please tell me what race you'd like to be? Your options are: Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, and Tiefling."
        elif step == "class":
            race = self.character_data.get("race", "Unknown")
            return f"I didn't quite catch that. Could you please tell me what class you'd like to be? As a {race}, you can choose from: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, and Wizard."
        elif step == "name":
            return f"I didn't quite catch your character's name. Could you please tell me what your character is called?"
        elif step == "background":
            return f"I didn't quite catch that. Could you please tell me what background your character has? You can choose from: Acolyte, Criminal, Folk Hero, Noble, Sage, Soldier, or describe a custom background."
        elif step == "personality":
            return f"I didn't quite catch that. Could you please tell me about your character's personality? What are they like?"
        else:
            return f"I didn't quite understand. Could you please clarify?"
    
    def _handle_ability_score_assignment(self, user_input: str) -> Dict[str, Any]:
        """Handle the ability score assignment step."""
        user_input_lower = user_input.lower()
        char_class = self.character_data.get("class", "Unknown")
        
        # Check if user wants suggestions
        if any(word in user_input_lower for word in ["suggest", "optimal", "recommend", "auto", "automatic"]):
            suggestions = self._generate_ability_score_suggestions(char_class)
            self.character_data["ability_scores"] = suggestions
            self.confirmed_facts.add("ability_scores")
            self.current_step_index += 1
            
            response = f"Perfect! I've assigned optimal ability scores for a {char_class}:\n\n"
            for ability, score in suggestions.items():
                response += f"• {ability.title()}: {score}\n"
            response += f"\n{self.get_character_summary()}\n\n🎯 **Character Creation Complete!**\n\nHere is your complete character sheet. Would you like to begin the campaign or make any changes?"
            
            self.conversation_history.append({"role": "assistant", "content": response})
            self.in_review_mode = True
            self.is_complete = True
            
            return {
                "success": True,
                "message": response,
                "is_complete": True,
                "in_review_mode": True
            }
        
        # Check if user wants to assign manually
        elif any(word in user_input_lower for word in ["manual", "myself", "choose", "pick", "assign"]):
            response = f"Great! You can assign your ability scores manually. You have 27 points to spend on your six abilities (Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma). Each ability starts at 8, and costs increase as scores get higher. Would you like me to explain the point-buy system, or do you have specific scores in mind?"
            
            self.conversation_history.append({"role": "assistant", "content": response})
            return {
                "success": True,
                "message": response,
                "is_complete": False,
                "current_step": "ability_scores"
            }
        
        # Try to extract ability scores from input
        else:
            # For now, just use suggestions if we can't parse manual scores
            suggestions = self._generate_ability_score_suggestions(char_class)
            self.character_data["ability_scores"] = suggestions
            self.confirmed_facts.add("ability_scores")
            self.current_step_index += 1
            
            response = f"I've assigned ability scores for your {char_class}:\n\n"
            for ability, score in suggestions.items():
                response += f"• {ability.title()}: {score}\n"
            response += f"\n{self.get_character_summary()}\n\n🎯 **Character Creation Complete!**\n\nHere is your complete character sheet. Would you like to begin the campaign or make any changes?"
            
            self.conversation_history.append({"role": "assistant", "content": response})
            self.in_review_mode = True
            self.is_complete = True
            
            return {
                "success": True,
                "message": response,
                "is_complete": True,
                "in_review_mode": True
            }
    
    def _log(self, method, *args, **kwargs):
        # Logging disabled - removed playtest logger
        pass
    
    def _mock_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate deterministic mock responses for offline testing."""
        try:
            # Get the last user message and system message
            last_user_message = ""
            system_message = ""
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                elif msg["role"] == "user":
                    last_user_message = msg["content"].lower()
            
            # Extract current character state from system message
            current_race = "Unknown"
            current_class = "Unknown"
            current_name = "Adventurer"
            current_background = "Unknown"
            
            if "CONFIRMED CHARACTER FACTS:" in system_message:
                if "Race: Human" in system_message:
                    current_race = "Human"
                elif "Race: Elf" in system_message:
                    current_race = "Elf"
                elif "Race: Dwarf" in system_message:
                    current_race = "Dwarf"
                elif "Race: Dragonborn" in system_message:
                    current_race = "Dragonborn"
                
                if "Class: Fighter" in system_message:
                    current_class = "Fighter"
                elif "Class: Wizard" in system_message:
                    current_class = "Wizard"
                elif "Class: Paladin" in system_message:
                    current_class = "Paladin"
                elif "Class: Monk" in system_message:
                    current_class = "Monk"
                
                if "Name: " in system_message:
                    name_match = system_message.split("Name: ")[1].split("\n")[0]
                    if name_match != "Not specified":
                        current_name = name_match
                
                if "Background: " in system_message:
                    bg_match = system_message.split("Background: ")[1].split("\n")[0]
                    if bg_match != "Not specified":
                        current_background = bg_match
            
            # Handle specific edit requests for testing
            if "change my class to wizard" in last_user_message:
                return "Class changed to Wizard. What else would you like to modify?"
            elif "make me chaotic neutral" in last_user_message:
                return "Alignment changed to Chaotic Neutral. What else would you like to modify?"
            elif "change my name to alice" in last_user_message:
                return "Name changed to Alice. What else would you like to modify?"
            elif "change my background to noble" in last_user_message:
                return "Background changed to Noble. What else would you like to modify?"
            elif "change my class to barbarian" in last_user_message:
                return "Character is already finalized and cannot be edited."
            
            # Handle compound statements (multiple facts in one input)
            if "human paladin" in last_user_message:
                return "Excellent! You are a Human Paladin. What's your name?"
            elif "human fighter" in last_user_message:
                return "Perfect! You are a Human Fighter. What's your name?"
            elif "human wizard" in last_user_message:
                return "Great choice! You are a Human Wizard. What's your name?"
            elif "elf wizard" in last_user_message:
                return "A wise choice! You are an Elf Wizard. What's your name?"
            elif "dwarf fighter" in last_user_message:
                return "Excellent! You are a Dwarf Fighter. What's your name?"
            elif "human monk" in last_user_message:
                return "Great choice! You are a Human Monk. What's your name?"
            
            # Generate context-aware responses
            if "what do you know" in last_user_message or "character so far" in last_user_message:
                response_parts = []
                if current_race != "Unknown":
                    response_parts.append(f"a {current_race}")
                if current_class != "Unknown":
                    response_parts.append(f"{current_class}")
                if current_name != "Adventurer":
                    response_parts.append(f"named {current_name}")
                if current_background != "Unknown":
                    response_parts.append(f"with a {current_background} background")
                
                if response_parts:
                    return f"Based on our conversation, you are {' '.join(response_parts)}. What would you like to tell me next?"
                else:
                    return "We're just getting started! What race would you like to be?"
            
            elif "dragonborn" in last_user_message:
                return "Excellent choice! You are a Dragonborn. What class would you like to be?"
            elif "elf" in last_user_message:
                return "A wise choice! You are an Elf. What class would you like to be?"
            elif "human" in last_user_message:
                return "A classic choice! You are a Human. What class would you like to be?"
            elif "fighter" in last_user_message:
                if current_race != "Unknown":
                    return f"Perfect! You are a {current_race} Fighter. What's your name?"
                else:
                    return "Perfect! You are a Fighter. What race would you like to be?"
            elif "wizard" in last_user_message:
                if current_race != "Unknown":
                    return f"Excellent! You are a {current_race} Wizard. What's your name?"
                else:
                    return "Excellent! You are a Wizard. What race would you like to be?"
            elif "monk" in last_user_message:
                if current_race != "Unknown":
                    return f"Excellent choice! You are a {current_race} Monk. What's your name?"
                else:
                    return "Excellent choice! You are a Monk. What race would you like to be?"
            elif "paladin" in last_user_message:
                if current_race != "Unknown":
                    return f"Great choice! You are a {current_race} Paladin. What's your name?"
                else:
                    return "Great choice! You are a Paladin. What race would you like to be?"
            elif "name" in last_user_message or "called" in last_user_message:
                if current_race != "Unknown" and current_class != "Unknown":
                    return f"Great name! As a {current_race} {current_class}, what background would you like?"
                else:
                    return "Great name! What background would you like for your character?"
            elif "criminal background" in last_user_message:
                return "Perfect background choice! Character creation complete! Here's your character summary."
            elif "complete" in last_user_message or "done" in last_user_message:
                return "Character creation complete! Your character has been created successfully."
            elif "actually" in last_user_message:
                # Handle stability-first logic - remind about review phase
                if any(word in last_user_message for word in ["human", "elf", "dwarf", "fighter", "wizard", "monk", "name", "background"]):
                    return "I understand you want to make a change! We'll have a chance to make changes after the character is complete. For now, let's finish gathering all the information we need."
                else:
                    return "I understand you want to make a change. What would you like to modify?"
            else:
                return "I'd be happy to help you create a character! What race would you like to be?"
                
        except Exception as e:
            logger.error(f"Error in mock LLM response: {e}")
            return "I'm here to help you create your character. What would you like to know?"
    
    def _real_llm_call(self, messages: List[Dict[str, str]]) -> str:
        """Make a real LLM call to Ollama."""
        try:
            import time
            
            # Add a small delay to avoid overwhelming the local model
            time.sleep(0.5)
            
            logger.info("🤖 Making LLM call to Ollama...")
            
            response_content = chat_completion(messages, temperature=0.7, max_tokens=500)
            logger.info(f"✅ LLM response received: {response_content[:100]}...")
            return response_content.strip()
                
        except Exception as e:
            logger.error(f"❌ LLM call failed: {e}")
            if "Cannot connect to Ollama" in str(e):
                raise Exception("❌ Ollama not running. Please start it with: 'ollama serve' or 'brew services start ollama'")
            elif "timeout" in str(e).lower():
                raise Exception("❌ LLM request timed out. The model may be too slow or overloaded.")
            else:
                raise Exception(f"Ollama LLM service error: {e}")
    
    def start_character_creation(self, description: str, campaign_name: str = "") -> Dict[str, Any]:
        """Start conversational character creation using Ollama."""
        try:
            logger.info(f"🎲 Starting conversational character creation with description: {description[:100]}...")
            logger.info(f"📝 Campaign name: {campaign_name}")
            
            # Reset to beginning
            self.current_step_index = 0
            self.confirmed_facts.clear()
            self.conversation_history = []
            self.in_review_mode = False
            self.is_complete = False
            
            logger.info("🔄 Reset character creation state")
            
            # Extract what we can from the initial description
            self._extract_and_stage_all_facts(description)
            
            # If we have pending facts, present them for confirmation first
            if self.pending_facts:
                confirmation_message = self._build_confirmation_prompt(self.pending_facts, [])
                self.conversation_history = [
                    {"role": "user", "content": description},
                    {"role": "assistant", "content": confirmation_message}
                ]
                return {
                    "success": True,
                    "message": confirmation_message,
                    "is_complete": False,
                    "current_step": "fact_confirmation",
                    "pending_facts": self.pending_facts
                }
            
            # Create system prompt for conversational character creation
            system_prompt = """You are a SoloHeart character creation assistant. Your role is to have a natural conversation with the player to help them create their character.

IMPORTANT GUIDELINES:
1. Have a natural, conversational tone - don't use rigid prompts
2. Extract character details from what the player tells you
3. Suggest appropriate D&D classes/races based on their descriptions
4. Ask follow-up questions to gather missing information
5. Be enthusiastic and engaging
6. Don't ask for information the player has already provided
7. When you have enough information, offer to complete the character

CHARACTER DETAILS TO GATHER:
- Name
- Race (Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling)
- Class (Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard)
- Background (Acolyte, Criminal, Folk Hero, Noble, Sage, Soldier, or custom)
- Personality traits
- Any backstory elements

Start by acknowledging their description and asking any clarifying questions needed."""
            
            # Add the player's initial description
            self.conversation_history = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": description}
            ]
            
            # Get Ollama's response
            logger.info("🤖 Getting Ollama's initial response...")
            ai_response = self._real_llm_call(self.conversation_history)
            
            # Store the AI response
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            logger.info("💾 Stored initial conversation")
            self._log('log_state', self.character_data)
            
            result = {
                "success": True,
                "message": ai_response,
                "is_complete": False,
                "current_step": "conversation"
            }
            
            logger.info(f"✅ Conversational character creation started successfully")
            return result
            
        except Exception as e:
            self._log('log_error', str(e))
            logger.error(f"❌ Error starting character creation: {e}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Error starting character creation: {str(e)}"
            }
    
    def _build_emotional_and_arc_scaffolding(self, personality: str, backstory: str) -> str:
        """Build emotional and narrative arc scaffolding based on character details."""
        try:
            # Get character name for personalization
            char_name = self.character_data.get('name', 'your character')
            if char_name == 'Adventurer':
                char_name = 'your character'
            
            # Get detected motivations
            motivations = self.character_data.get('motivations', [])
            motivation_text = ""
            if motivations:
                if len(motivations) == 1:
                    motivation_text = motivations[0].lower()
                elif len(motivations) == 2:
                    motivation_text = f"{motivations[0].lower()} and {motivations[1].lower()}"
                else:
                    motivation_text = f"{', '.join(motivations[:-1]).lower()}, and {motivations[-1].lower()}"
            
            # Build personalized prompt
            if motivation_text:
                prompt = f"It sounds like {char_name} carries a lot of {motivation_text}. "
            else:
                prompt = f"It sounds like {char_name} has been through some intense experiences. "
            
            prompt += "Do you imagine their story heading toward redemption, vengeance, transformation, or something else? Or would you rather discover it during play? (This is totally optional!)"
            
            logger.info(f"🎭 Generated emotional arc scaffolding for {char_name}")
            return prompt
            
        except Exception as e:
            logger.error(f"❌ Error building emotional scaffolding: {e}")
            return "What direction do you see your character's story taking? Redemption, vengeance, transformation, or something else? Or would you rather discover it during play?"

    def continue_conversation(self, user_input: str) -> Dict[str, Any]:
        """Continue conversational character creation using Ollama, with emotional and arc scaffolding."""
        try:
            self._log('log_user_input', user_input)
            self.conversation_history.append({"role": "user", "content": user_input})
            logger.info(f"Current character data: {self.character_data}")

            # Handle 'what do we have so far' or similar
            if any(phrase in user_input.lower() for phrase in ["what do we have so far", "what have we got", "current status", "show me what we have", "show me the character"]):
                fact_summary = self.get_fact_summary()
                response = f"Here's what we have so far:\n{fact_summary}\nWhat would you like to add or change?"
                self.conversation_history.append({"role": "assistant", "content": response})
                return {
                    "success": True,
                    "message": response,
                    "is_complete": False,
                    "current_step": "status_check"
                }

            # If we are waiting for confirmation, check for confirmation phrases
            confirmation_phrases = [
                "yes", "that's right", "correct", "looks good", "that looks right", "you got it", "sounds right"
            ]
            if self.pending_facts:
                if user_input.strip().lower() in confirmation_phrases:
                    self.confirm_pending_facts()
                    logger.info(f"✅ Facts confirmed and committed: {self.character_data}")
                    # Only trigger arc scaffolding if personality, background, and either class or race are confirmed
                    core_keys = [k for k in ["personality", "background"] if self.character_data.get(k) and self.character_data[k] not in ["Unknown", "A brave adventurer", None, ""]]
                    class_or_race = any(self.character_data.get(k) and self.character_data[k] not in ["Unknown", None, ""] for k in ["class", "race"])
                    if len(core_keys) == 2 and class_or_race and not hasattr(self, 'arc_scaffolding_asked'):
                        self.arc_scaffolding_asked = True
                        scaffolding = self._build_emotional_and_arc_scaffolding(
                            self.character_data.get('personality', ''),
                            self.character_data.get('background', '')
                        )
                        self.conversation_history.append({"role": "assistant", "content": scaffolding})
                        return {
                            "success": True,
                            "message": scaffolding,
                            "is_complete": False,
                            "current_step": "arc_scaffolding"
                        }
                    response = "Great! I've saved those details. What else would you like to tell me about your character?"
                    self.conversation_history.append({"role": "assistant", "content": response})
                    return {
                        "success": True,
                        "message": response,
                        "is_complete": False,
                        "current_step": "conversation"
                    }
                else:
                    # Treat as new info/correction, re-extract facts
                    self._extract_and_stage_all_facts(user_input)
                    confirmation_message = self._build_confirmation_prompt(self.pending_facts, [])
                    self.conversation_history.append({"role": "assistant", "content": confirmation_message})
                    return {
                        "success": True,
                        "message": confirmation_message,
                        "is_complete": False,
                        "current_step": "fact_confirmation",
                        "pending_facts": self.pending_facts
                    }

            # Otherwise, extract facts from the user input
            self._extract_and_stage_all_facts(user_input)
            if self.pending_facts:
                confirmation_message = self._build_confirmation_prompt(self.pending_facts, [])
                self.conversation_history.append({"role": "assistant", "content": confirmation_message})
                return {
                    "success": True,
                    "message": confirmation_message,
                    "is_complete": False,
                    "current_step": "fact_confirmation",
                    "pending_facts": self.pending_facts
                }

            # If not enough facts, do not allow completion or fallback
            if not self._enough_facts_for_progress():
                response = "I need a bit more information before we can continue. Please tell me more about your character—maybe their name, race, class, background, or personality."
                self.conversation_history.append({"role": "assistant", "content": response})
                return {
                    "success": True,
                    "message": response,
                    "is_complete": False,
                    "current_step": "awaiting_more_info"
                }

            # If enough facts, continue with emotional scaffolding if not already done
            core_keys = [k for k in ["personality", "background"] if self.character_data.get(k) and self.character_data[k] not in ["Unknown", "A brave adventurer", None, ""]]
            class_or_race = any(self.character_data.get(k) and self.character_data[k] not in ["Unknown", None, ""] for k in ["class", "race"])
            if len(core_keys) == 2 and class_or_race and not hasattr(self, 'arc_scaffolding_asked'):
                self.arc_scaffolding_asked = True
                scaffolding = self._build_emotional_and_arc_scaffolding(
                    self.character_data.get('personality', ''),
                    self.character_data.get('background', '')
                )
                self.conversation_history.append({"role": "assistant", "content": scaffolding})
                return {
                    "success": True,
                    "message": scaffolding,
                    "is_complete": False,
                    "current_step": "arc_scaffolding"
                }

            # Otherwise, continue normal conversation
            response = "What else would you like to tell me about your character?"
            self.conversation_history.append({"role": "assistant", "content": response})
            return {
                "success": True,
                "message": response,
                "is_complete": False,
                "current_step": "conversation"
            }
        except Exception as e:
            self._log('log_error', str(e))
            logger.error(f"Error continuing conversation: {e}")
            return {
                "success": False,
                "message": "Error processing your input. Please try again."
            }

    def _extract_character_data(self) -> Optional[Dict[str, Any]]:
        """Extract character data from conversation history."""
        try:
            # Use LLM to extract comprehensive character data
            conversation_text = " ".join([msg["content"] for msg in self.conversation_history])
            
            extraction_prompt = f"""
            Based on this SoloHeart character creation conversation, extract a complete character sheet in JSON format.
            
            Conversation:
            {conversation_text}
            
            IMPORTANT: Carefully analyze the entire conversation to find all character details that were mentioned. Look for:
            - Name: Any name mentioned by the player
            - Race: Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling
            - Class: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard
            - Background: Acolyte, Criminal, Folk Hero, Noble, Sage, Soldier, or custom
            - Personality traits and appearance details
            - Backstory elements
            
            Generate a complete character with the following structure:
            {{
                "name": "Character Name",
                "race": "Race",
                "class": "Class", 
                "level": 1,
                "background": "Background",
                "personality": "Personality description",
                "ability_scores": {{
                    "strength": 10,
                    "dexterity": 10,
                    "constitution": 10,
                    "intelligence": 10,
                    "wisdom": 10,
                    "charisma": 10
                }},
                "hit_points": 10,
                "armor_class": 10,
                "saving_throws": ["STR", "CON"],
                "skills": ["Athletics", "Perception"],
                "feats": [],
                "weapons": ["Longsword"],
                "gear": ["Explorer's Pack"],
                "spells": [],
                "background_freeform": "Character backstory and motivations"
            }}
            
            Use reasonable defaults for any missing information. Return only valid JSON.
            """
            
            logger.info("🤖 Making LLM call to extract character data...")
            try:
                import requests
                from requests.exceptions import Timeout
                
                # Use requests with timeout for the LLM call
                response_text = chat_completion([
                    {"role": "system", "content": "You are a SoloHeart character sheet generator. Carefully analyze the conversation and extract all character details mentioned. Return only valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ], temperature=0.1, max_tokens=800)
                logger.info("✅ LLM response received for character data extraction")
            except Timeout:
                logger.error("❌ LLM request timed out after 30 seconds")
                # Return a default character if LLM times out
                return {
                    "name": "Adventurer",
                    "race": "Human",
                    "class": "Fighter",
                    "level": 1,
                    "background": "Adventurer",
                    "personality": "A brave adventurer",
                    "ability_scores": {
                        "strength": 10, "dexterity": 10, "constitution": 10,
                        "intelligence": 10, "wisdom": 10, "charisma": 10
                    },
                    "hit_points": 10,
                    "armor_class": 10,
                    "saving_throws": [],
                    "skills": [],
                    "feats": [],
                    "weapons": [],
                    "gear": [],
                    "spells": [],
                    "background_freeform": "A brave adventurer ready for adventure"
                }
            except Exception as e:
                logger.error(f"❌ LLM call failed for character data extraction: {e}")
                # Return a default character if LLM fails
                return {
                    "name": "Adventurer",
                    "race": "Human",
                    "class": "Fighter",
                    "level": 1,
                    "background": "Adventurer",
                    "personality": "A brave adventurer",
                    "ability_scores": {
                        "strength": 10, "dexterity": 10, "constitution": 10,
                        "intelligence": 10, "wisdom": 10, "charisma": 10
                    },
                    "hit_points": 10,
                    "armor_class": 10,
                    "saving_throws": [],
                    "skills": [],
                    "feats": [],
                    "weapons": [],
                    "gear": [],
                    "spells": [],
                    "background_freeform": "A brave adventurer ready for adventure"
                }
            
            # Parse the JSON response
            import json
            import re
            
            response_text = response_text.strip()
            
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                character_data = json.loads(json_match.group())
                
                # Ensure all required fields are present
                character_data.setdefault("name", "Adventurer")
                character_data.setdefault("race", "Human")
                character_data.setdefault("class", "Fighter")
                character_data.setdefault("level", 1)
                character_data.setdefault("background", "Adventurer")
                character_data.setdefault("personality", f"A {character_data['race']} {character_data['class']}")
                character_data.setdefault("ability_scores", {
                    "strength": 10, "dexterity": 10, "constitution": 10,
                    "intelligence": 10, "wisdom": 10, "charisma": 10
                })
                character_data.setdefault("hit_points", 10)
                character_data.setdefault("armor_class", 10)
                character_data.setdefault("saving_throws", [])
                character_data.setdefault("skills", [])
                character_data.setdefault("feats", [])
                character_data.setdefault("weapons", [])
                character_data.setdefault("gear", [])
                character_data.setdefault("spells", [])
                character_data.setdefault("background_freeform", "")
                character_data["created_date"] = datetime.datetime.now().isoformat()
                
                return character_data
            else:
                # Fallback to simple extraction
                return self._simple_extract_character_data(conversation_text)
            
        except Exception as e:
            logger.error(f"Error extracting character data: {e}")
            # Fallback to simple extraction
            conversation_text = " ".join([msg["content"] for msg in self.conversation_history])
            return self._simple_extract_character_data(conversation_text)
    
    def _detect_and_commit_facts(self, user_input: str, ai_response: str) -> None:
        """Detect new character facts from the conversation and commit them immediately."""
        try:
            import re
            combined_text = f"{user_input} {ai_response}".lower()
            logger.info(f"Analyzing text for facts: '{combined_text[:100]}...'")
            logger.info(f"Current confirmed facts: {self.confirmed_facts}")
            # Patterns for revisions/edits
            revision_patterns = [
                r"actually[,:]? (i'?m|i am|let's go with|let's make it|i'll go with|i'll take|i've decided|maybe|scratch that)[^.,;:]*? (human|elf|dwarf|halfling|dragonborn|gnome|half-elf|half-orc|tiefling|barbarian|bard|cleric|druid|fighter|monk|paladin|ranger|rogue|sorcerer|warlock|wizard|acolyte|criminal|folk hero|noble|sage|soldier)"
            ]
            # Detect race/class/background revisions
            for pattern in revision_patterns:
                match = re.search(pattern, combined_text)
                if match:
                    value = match.group(2).title()
                    # Determine fact type
                    if value in ["Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome", "Half-Elf", "Half-Orc", "Tiefling"]:
                        self._commit_fact("race", value, "player", allow_overwrite=True)
                        logger.info(f"[REVISION] Overwrote race with: {value}")
                    elif value in ["Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"]:
                        self._commit_fact("class", value, "player", allow_overwrite=True)
                        logger.info(f"[REVISION] Overwrote class with: {value}")
                    elif value in ["Acolyte", "Criminal", "Folk Hero", "Noble", "Sage", "Soldier"]:
                        self._commit_fact("background", value, "player", allow_overwrite=True)
                        logger.info(f"[REVISION] Overwrote background with: {value}")
            # Flexible confirmation patterns
            def match_patterns(fact_type, values, extra_patterns=None):
                found_any = False
                for value in values:
                    if value.lower() in combined_text:
                        patterns = [
                            f"you are a {value.lower()}", f"your character is a {value.lower()}", f"you're a {value.lower()}",
                            f"i am a {value.lower()}", f"i'm a {value.lower()}", f"let's make you a {value.lower()}",
                            f"i want to be a {value.lower()}", f"i want a {value.lower()}", f"make me a {value.lower()}",
                            f"i choose {value.lower()}", f"i pick {value.lower()}", f"i'll be a {value.lower()}",
                            f"i've decided i'll be a {value.lower()}", f"let's go with {value.lower()}",
                            f"maybe a {value.lower()} suits me best", f"i'll take the {value.lower()} background",
                            # Additional patterns for compound statements
                            f"a {value.lower()}", f"the {value.lower()}", f"my {value.lower()}"
                        ]
                        if extra_patterns:
                            patterns.extend(extra_patterns)
                        if any(p in combined_text for p in patterns):
                            self._commit_fact(fact_type, value.title(), "player")
                            found_any = True
                return found_any
            # Race - use centralized extraction utility
            extracted_race = extract_race_from_text(combined_text)
            if extracted_race:
                self._commit_fact("race", extracted_race, "player")
                logger.info(f"✅ Race fact committed: {extracted_race}")
            # Class - use centralized extraction utility
            extracted_class = extract_class_from_text(combined_text)
            if extracted_class:
                self._commit_fact("class", extracted_class, "player")
                logger.info(f"✅ Class fact committed: {extracted_class}")
            # Background - use centralized extraction utility
            extracted_background = extract_background_from_text(combined_text)
            if extracted_background:
                self._commit_fact("background", extracted_background, "player")
                logger.info(f"✅ Background fact committed: {extracted_background}")
            # Name
            name_patterns = [
                r"my name is ([a-z]+)", r"i'm called ([a-z]+)", r"call me ([a-z]+)",
                r"my character is named ([a-z]+)", r"name me ([a-z]+)",
                r"^i am ([a-z]+)$", r"^i'm ([a-z]+)$",  # Only match standalone "I am X" or "I'm X"
                r"my name's ([a-z]+)", r"i go by ([a-z]+)",
                r"my character is ([a-z]+)"  # NEW: match 'my character is John'
            ]
            if "name" not in self.confirmed_facts or any(re.search(p, combined_text) for p in name_patterns):
                for pattern in name_patterns:
                    match = re.search(pattern, combined_text)
                    if match:
                        name = match.group(1).title()
                        self._commit_fact("name", name, "player", allow_overwrite=True)
                        break
            # Personality
            personality_keywords = ["brave", "loyal", "cunning", "wise", "charismatic", "strong", "kind", "fierce", "gentle", "bold"]
            if "personality" not in self.confirmed_facts or any(word in combined_text for word in personality_keywords):
                personality_patterns = [
                    r"(?:i am|i'm|my personality is|i am) ([^.]+)",
                    r"(?:i am|i'm) ([^.]+)",
                    r"(?:my character is|i am) ([^.]+)"
                ]
                for pattern in personality_patterns:
                    personality_match = re.search(pattern, combined_text)
                    if personality_match:
                        personality = personality_match.group(1).strip()
                        self._commit_fact("personality", personality, "player", allow_overwrite=True)
                        break
        except Exception as e:
            logger.error(f"Error detecting and committing facts: {e}")
    
    def _commit_fact(self, fact_type: str, value: str, source: str = "player", allow_overwrite: bool = False) -> None:
        """Commit a character fact to memory and update the character sheet with timestamp and source tracking."""
        try:
            old_value = self.character_data.get(fact_type)
            is_overwrite = old_value is not None and old_value != value
            # Enforce immutability during creation (unless in review mode or explicitly allowed)
            if not self.in_review_mode and not allow_overwrite and fact_type in self.confirmed_facts:
                logger.info(f"[IMMUTABLE] Fact {fact_type} already confirmed during creation phase")
                return
            self.fact_history.append((fact_type, old_value))
            if fact_type == "name":
                self.character_data["name"] = value
            elif fact_type == "race":
                self.character_data["race"] = value
            elif fact_type == "class":
                self.character_data["class"] = value
                self.character_data["saving_throws"] = self._get_class_saving_throws(value)
                self.character_data["skills"] = self._get_class_skills(value)
                weapons, gear, spells = self._generate_equipment(value)
                self.character_data["weapons"] = weapons
                self.character_data["gear"] = gear
                self.character_data["spells"] = spells
                self.character_data["ability_scores"] = self._generate_ability_scores(value)
            elif fact_type == "background":
                self.character_data["background"] = value
            elif fact_type == "personality":
                self.character_data["personality"] = value
            self.confirmed_facts.add(fact_type)
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            if self.narrative_bridge:
                self._store_character_fact_in_memory(fact_type, value, source)
            logger.info(f"[CHAR FACT COMMIT] {fact_type}  {value} (source: {source}, replaced: {old_value if is_overwrite else None}) @ {timestamp}")
            self._log('log_fact', fact_type, value, source, replaced=old_value if old_value != value else None)
        except Exception as e:
            logger.error(f"Error committing fact {fact_type}: {e}")
    
    def undo_last_fact(self) -> Optional[tuple]:
        """Undo the last committed character fact and return the undone fact."""
        try:
            if not self.fact_history:
                logger.info("No facts to undo")
                return None
            
            fact_type, old_value = self.fact_history.pop()
            
            # Restore the old value
            if old_value is None:
                if fact_type in self.character_data:
                    del self.character_data[fact_type]
                if fact_type in self.confirmed_facts:
                    self.confirmed_facts.remove(fact_type)
            else:
                self.character_data[fact_type] = old_value
                # Keep the fact as confirmed since it was previously confirmed
            
            # Log the reversal
            logger.info(f"Undid character fact: {fact_type} = {old_value}")
            
            # Memory storage disabled - removed vector memory system
            pass
            
            return (fact_type, old_value)
            
        except Exception as e:
            logger.error(f"Error undoing last fact: {e}")
            return None
    
    def _store_character_fact_in_memory(self, fact_type: str, value: str, source: str = "player") -> None:
        """Store a character fact in the vector memory system with timestamp and source tracking."""
        try:
            character_name = self.character_data.get("name", "Adventurer")
            
            # Create a memory entry for this fact
            fact_description = f"Character fact confirmed: {character_name} is a {value}"
            if fact_type == "race":
                fact_description = f"Character fact confirmed: {character_name} is a {value}"
            elif fact_type == "class":
                fact_description = f"Character fact confirmed: {character_name} is a {value}"
            elif fact_type == "background":
                fact_description = f"Character fact confirmed: {character_name} has a {value} background"
            elif fact_type == "personality":
                fact_description = f"Character fact confirmed: {character_name} is {value}"
            
            # Memory storage disabled - removed vector memory system
            pass
            
        except Exception as e:
            logger.error(f"Error storing character fact in memory: {e}")
    
    def _get_current_character_state(self, bullet_points: bool = False) -> str:
        """Get a summary of what character information has been collected so far."""
        try:
            confirmed_facts = []
            unconfirmed_facts = []
            
            # Check for committed facts in character_data
            if self.character_data.get('name') and self.character_data['name'] != 'Adventurer':
                confirmed_facts.append(f"Name: {self.character_data['name']}")
            else:
                unconfirmed_facts.append("Name")
            
            if self.character_data.get('race') and self.character_data['race'] != 'Unknown':
                confirmed_facts.append(f"Race: {self.character_data['race']}")
            else:
                unconfirmed_facts.append("Race")
            
            if self.character_data.get('class') and self.character_data['class'] != 'Unknown':
                confirmed_facts.append(f"Class: {self.character_data['class']}")
            else:
                unconfirmed_facts.append("Class")
            
            if self.character_data.get('background') and self.character_data['background'] != 'Unknown':
                confirmed_facts.append(f"Background: {self.character_data['background']}")
            else:
                unconfirmed_facts.append("Background")
            
            if self.character_data.get('personality') and self.character_data['personality'] != 'A brave adventurer':
                confirmed_facts.append(f"Personality: {self.character_data['personality']}")
            else:
                unconfirmed_facts.append("Personality")
            
            if bullet_points:
                return '\n'.join(f"- {fact}" for fact in confirmed_facts) if confirmed_facts else "- None yet"
            
            state_summary = f"""
CONFIRMED CHARACTER FACTS:
{chr(10).join(f"- {fact}" for fact in confirmed_facts) if confirmed_facts else "- None yet"}

STILL NEEDED:
{chr(10).join(f"- {fact}" for fact in unconfirmed_facts) if unconfirmed_facts else "- All facts confirmed!"}

Level: {self.character_data.get('level', 1)}
"""
            return state_summary
        except Exception as e:
            logger.error(f"Error getting current character state: {e}")
            return "Unable to determine current character state"

    def _get_unknown_facts_list(self):
        """Return a list of unconfirmed fact types in order."""
        order = ["name", "race", "class", "background", "personality"]
        unknown_facts = []
        
        for fact in order:
            if fact == "name" and (not self.character_data.get('name') or self.character_data['name'] == 'Adventurer'):
                unknown_facts.append("Name")
            elif fact == "race" and (not self.character_data.get('race') or self.character_data['race'] == 'Unknown'):
                unknown_facts.append("Race")
            elif fact == "class" and (not self.character_data.get('class') or self.character_data['class'] == 'Unknown'):
                unknown_facts.append("Class")
            elif fact == "background" and (not self.character_data.get('background') or self.character_data['background'] == 'Unknown'):
                unknown_facts.append("Background")
            elif fact == "personality" and (not self.character_data.get('personality') or self.character_data['personality'] == 'A brave adventurer'):
                unknown_facts.append("Personality")
        
        return unknown_facts
    
    def is_character_complete(self) -> bool:
        """Check if all required character fields are filled."""
        required_fields = {
            "name": lambda x: x != "Adventurer" and x != "Unknown",
            "race": lambda x: x != "Unknown",
            "class": lambda x: x != "Unknown", 
            "background": lambda x: x != "Unknown",
            "personality": lambda x: x != "A brave adventurer" and x != "Unknown",
            "ability_scores": lambda x: isinstance(x, dict) and all(isinstance(v, int) for v in x.values())
        }
        
        for field, validator in required_fields.items():
            if not validator(self.character_data.get(field, "Unknown")):
                return False
        return True
    
    def get_character_summary(self) -> str:
        """Generate a formatted character summary for review."""
        char = self.character_data
        summary = f"""
🎭 **Character Summary**

**Name:** {char['name']}
**Race:** {char['race']}
**Class:** {char['class']} (Level {char['level']})
**Background:** {char['background']}
**Alignment:** {char['alignment']}

**Ability Scores:**
- Strength: {char['ability_scores']['strength']}
- Dexterity: {char['ability_scores']['dexterity']}
- Constitution: {char['ability_scores']['constitution']}
- Intelligence: {char['ability_scores']['intelligence']}
- Wisdom: {char['ability_scores']['wisdom']}
- Charisma: {char['ability_scores']['charisma']}

**Combat Stats:**
- Hit Points: {char['hit_points']}
- Armor Class: {char['armor_class']}

**Skills:** {', '.join(char['skills']) if char['skills'] else 'None'}
**Saving Throws:** {', '.join(char['saving_throws']) if char['saving_throws'] else 'None'}

**Equipment:**
- Weapons: {', '.join(char['weapons']) if char['weapons'] else 'None'}
- Gear: {', '.join(char['gear']) if char['gear'] else 'None'}
- Spells: {', '.join(char['spells']) if char['spells'] else 'None'}

**Personality:** {char['personality']}
"""
        return summary.strip()
    
    def apply_character_edit(self, message: str) -> Dict[str, Any]:
        """Apply edits to character during review mode."""
        import re
        # Check finalized first
        if self.character_finalized:
            return {
                "success": False,
                "message": "Character is already finalized and cannot be edited."
            }
        if not self.in_review_mode:
            return {
                "success": False,
                "message": "Character edits are only allowed during the review phase."
            }
        try:
            message_lower = message.lower()
            changes_made = []
            # Sort alignment patterns by length descending for specificity
            alignment_patterns = dict(sorted({
                "lawful good": "Lawful Good", "lg": "Lawful Good",
                "lawful neutral": "Lawful Neutral", "ln": "Lawful Neutral", 
                "lawful evil": "Lawful Evil", "le": "Lawful Evil",
                "neutral good": "Neutral Good", "ng": "Neutral Good",
                "neutral": "Neutral", "n": "Neutral",
                "neutral evil": "Neutral Evil", "ne": "Neutral Evil",
                "chaotic good": "Chaotic Good", "cg": "Chaotic Good",
                "chaotic neutral": "Chaotic Neutral", "cn": "Chaotic Neutral",
                "chaotic evil": "Chaotic Evil", "ce": "Chaotic Evil"
            }.items(), key=lambda x: -len(x[0])))
            for pattern, alignment in alignment_patterns.items():
                if pattern in message_lower:
                    old_alignment = self.character_data["alignment"]
                    self.character_data["alignment"] = alignment
                    changes_made.append(f"Alignment: {old_alignment} → {alignment}")
                    break
            
            # Parse class changes
            class_patterns = {
                "barbarian", "bard", "cleric", "druid", "fighter", "monk", 
                "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard"
            }
            
            for class_name in class_patterns:
                if f"change my class to {class_name}" in message_lower or f"make me a {class_name}" in message_lower:
                    old_class = self.character_data["class"]
                    self.character_data["class"] = class_name.title()
                    # Update class-specific data
                    self.character_data["saving_throws"] = self._get_class_saving_throws(class_name.title())
                    self.character_data["skills"] = self._get_class_skills(class_name.title())
                    weapons, gear, spells = self._generate_equipment(class_name.title())
                    self.character_data["weapons"] = weapons
                    self.character_data["gear"] = gear
                    self.character_data["spells"] = spells
                    self.character_data["ability_scores"] = self._generate_ability_scores(class_name.title())
                    changes_made.append(f"Class: {old_class} → {class_name.title()}")
                    break
            
            # Parse name changes
            name_match = re.search(r"change my name to ([a-z]+)", message_lower)
            if name_match:
                old_name = self.character_data["name"]
                new_name = name_match.group(1).title()
                self.character_data["name"] = new_name
                changes_made.append(f"Name: {old_name} → {new_name}")
            
            # Parse background changes
            background_patterns = ["acolyte", "criminal", "folk hero", "noble", "sage", "soldier"]
            for bg in background_patterns:
                if f"change my background to {bg}" in message_lower or f"make my background {bg}" in message_lower:
                    old_bg = self.character_data["background"]
                    self.character_data["background"] = bg.title()
                    changes_made.append(f"Background: {old_bg} → {bg.title()}")
                    break
            
            if changes_made:
                # Update vector memory for changed facts
                for change in changes_made:
                    fact_type = change.split(":")[0].lower()
                    new_value = change.split("→")[1].strip()
                    if self.narrative_bridge:
                        self._store_character_fact_in_memory(fact_type, new_value, "edit")
                
                logger.info(f"Applied character edits: {changes_made}")
                return {
                    "success": True,
                    "message": f"Changes applied: {', '.join(changes_made)}",
                    "summary": self.get_character_summary()
                }
            else:
                return {
                    "success": False,
                    "message": "I didn't understand what you wanted to change. Try phrases like 'change my class to wizard' or 'make me chaotic neutral'."
                }
                
        except Exception as e:
            logger.error(f"Error applying character edit: {e}")
            return {
                "success": False,
                "message": "Error applying changes. Please try again."
            }
    
    def finalize_character(self) -> Dict[str, Any]:
        try:
            if not self.is_character_complete():
                return {
                    "success": False,
                    "message": "Character is not complete. Please fill in all required fields."
                }
            if not self.in_review_mode:
                return {
                    "success": False,
                    "message": "Character must be in review mode before finalization."
                }
            self.character_finalized = True
            self.in_review_mode = False
            # Memory storage disabled - removed vector memory system
            pass
            logger.info(f"Character finalized: {self.character_data['name']}")
            return {
                "success": True,
                "message": f"Character {self.character_data['name']} is now finalized and ready for adventure!",
                "character_data": self.character_data
            }
        except Exception as e:
            logger.error(f"Error finalizing character: {e}")
            return {
                "success": False,
                "message": "Error finalizing character."
            }

    def _simple_extract_character_data(self, conversation_text: str) -> Dict[str, Any]:
        """Simple fallback character data extraction."""
        import re
        
        # Name - look for "name is" or "called" patterns
        name_match = re.search(r'(?:name is|called|named)\s+([A-Z][a-z]+)', conversation_text, re.IGNORECASE)
        name = name_match.group(1) if name_match else "Adventurer"
        
        # Race - use centralized extraction utility
        race = extract_race_from_text(conversation_text) or "Human"
        
        # Class - use centralized extraction utility
        character_class = extract_class_from_text(conversation_text) or "Fighter"
        
        # Generate reasonable ability scores based on class
        ability_scores = self._generate_ability_scores(character_class)
        
        # Generate equipment based on class
        weapons, gear, spells = self._generate_equipment(character_class)
        
        return {
            "name": name,
            "race": race,
            "class": character_class,
            "level": 1,
            "background": "Adventurer",
            "personality": f"A {race} {character_class} named {name}",
            "ability_scores": ability_scores,
            "hit_points": ability_scores["constitution"] + 5,  # Base HP
            "armor_class": 10,
            "saving_throws": self._get_class_saving_throws(character_class),
            "skills": self._get_class_skills(character_class),
            "feats": [],
            "weapons": weapons,
            "gear": gear,
            "spells": spells,
            "background_freeform": f"{name} is a {race} {character_class} seeking adventure and glory.",
            "created_date": datetime.datetime.now().isoformat()
        }
    
    def _generate_ability_scores(self, character_class: str) -> Dict[str, int]:
        """Generate reasonable ability scores for a character class."""
        # Base scores with class-appropriate bonuses
        base_scores = {
            "strength": 10, "dexterity": 10, "constitution": 10,
            "intelligence": 10, "wisdom": 10, "charisma": 10
        }
        
        # Class-specific adjustments
        if character_class in ["Barbarian", "Fighter", "Paladin"]:
            base_scores["strength"] = 14
            base_scores["constitution"] = 12
        elif character_class in ["Rogue", "Ranger", "Monk"]:
            base_scores["dexterity"] = 14
            base_scores["constitution"] = 12
        elif character_class in ["Wizard", "Sorcerer"]:
            base_scores["intelligence"] = 14 if character_class == "Wizard" else 12
            base_scores["charisma"] = 14 if character_class == "Sorcerer" else 12
            base_scores["constitution"] = 12
        elif character_class in ["Cleric", "Druid"]:
            base_scores["wisdom"] = 14
            base_scores["constitution"] = 12
        elif character_class == "Bard":
            base_scores["charisma"] = 14
            base_scores["dexterity"] = 12
        elif character_class == "Warlock":
            base_scores["charisma"] = 14
            base_scores["constitution"] = 12
        
        return base_scores
    
    def _generate_equipment(self, character_class: str) -> tuple:
        """Generate starting equipment for a character class."""
        weapons = []
        gear = ["Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "50 feet of rope"]
        spells = []
        
        if character_class == "Fighter":
            weapons = ["Longsword", "Shield"]
            gear.extend(["Chain mail", "Crossbow, light", "20 bolts"])
        elif character_class == "Wizard":
            weapons = ["Quarterstaff"]
            gear.extend(["Spellbook", "Arcane focus", "Scholar's pack"])
            spells = ["Fire Bolt", "Mage Hand", "Prestidigitation"]
        elif character_class == "Cleric":
            weapons = ["Mace", "Shield"]
            gear.extend(["Chain mail", "Holy symbol"])
            spells = ["Sacred Flame", "Spare the Dying", "Cure Wounds"]
        elif character_class == "Rogue":
            weapons = ["Shortsword", "Shortbow"]
            gear.extend(["Leather armor", "Thieves' tools", "Burglar's pack"])
        elif character_class == "Ranger":
            weapons = ["Longbow", "Shortsword"]
            gear.extend(["Leather armor", "Explorer's pack"])
        elif character_class == "Barbarian":
            weapons = ["Greataxe", "Javelin"]
            gear.extend(["Explorer's pack", "4 javelins"])
        elif character_class == "Bard":
            weapons = ["Rapier", "Lute"]
            gear.extend(["Leather armor", "Diplomat's pack"])
            spells = ["Vicious Mockery", "Prestidigitation", "Cure Wounds"]
        elif character_class == "Druid":
            weapons = ["Quarterstaff"]
            gear.extend(["Leather armor", "Druidic focus", "Explorer's pack"])
            spells = ["Produce Flame", "Guidance", "Cure Wounds"]
        elif character_class == "Monk":
            weapons = ["Shortsword"]
            gear.extend(["Explorer's pack", "10 darts"])
        elif character_class == "Paladin":
            weapons = ["Longsword", "Shield"]
            gear.extend(["Chain mail", "Holy symbol", "Priest's pack"])
        elif character_class == "Sorcerer":
            weapons = ["Quarterstaff"]
            gear.extend(["Arcane focus", "Explorer's pack"])
            spells = ["Fire Bolt", "Mage Hand", "Burning Hands"]
        elif character_class == "Warlock":
            weapons = ["Quarterstaff"]
            gear.extend(["Arcane focus", "Scholar's pack"])
            spells = ["Eldritch Blast", "Prestidigitation", "Hex"]
        
        return weapons, gear, spells
    
    def _get_class_saving_throws(self, character_class: str) -> List[str]:
        """Get saving throw proficiencies for a character class."""
        saving_throws = {
            "Barbarian": ["STR", "CON"],
            "Bard": ["DEX", "CHA"],
            "Cleric": ["WIS", "CHA"],
            "Druid": ["INT", "WIS"],
            "Fighter": ["STR", "CON"],
            "Monk": ["STR", "DEX"],
            "Paladin": ["WIS", "CHA"],
            "Ranger": ["STR", "DEX"],
            "Rogue": ["DEX", "INT"],
            "Sorcerer": ["CON", "CHA"],
            "Warlock": ["WIS", "CHA"],
            "Wizard": ["INT", "WIS"]
        }
        return saving_throws.get(character_class, ["STR", "CON"])
    
    def _get_class_skills(self, character_class: str) -> List[str]:
        """Get skill proficiencies for a character class."""
        skills = {
            "Barbarian": ["Athletics", "Survival"],
            "Bard": ["Acrobatics", "Performance"],
            "Cleric": ["Insight", "Religion"],
            "Druid": ["Animal Handling", "Nature"],
            "Fighter": ["Athletics", "Intimidation"],
            "Monk": ["Acrobatics", "Athletics"],
            "Paladin": ["Athletics", "Intimidation"],
            "Ranger": ["Animal Handling", "Survival"],
            "Rogue": ["Acrobatics", "Stealth"],
            "Sorcerer": ["Arcana", "Deception"],
            "Warlock": ["Arcana", "Deception"],
            "Wizard": ["Arcana", "History"]
        }
        return skills.get(character_class, ["Athletics", "Perception"])
    
    def get_character_data(self) -> Dict[str, Any]:
        """Get the completed character data with actual committed facts."""
        # Ensure created_date is set
        if not self.character_data.get("created_date"):
            self.character_data["created_date"] = datetime.datetime.now().isoformat()
        
        # Generate ability scores if we have a class but no scores
        if self.character_data.get('class') and not self.character_data.get('ability_scores'):
            char_class = self.character_data['class']
            self.character_data['ability_scores'] = self._generate_ability_scores(char_class)
            self.character_data['hit_points'] = 10  # Default HP
        
        # Ensure all new fields are present
        if 'combat_style' not in self.character_data:
            self.character_data['combat_style'] = None
        if 'traits' not in self.character_data:
            self.character_data['traits'] = []
        if 'motivations' not in self.character_data:
            self.character_data['motivations'] = []
        
        # Return a copy to prevent external modification
        return self.character_data.copy()

    def _enough_facts_for_progress(self):
        # Require at least 3 core facts to allow progress
        char = self.character_data
        core_keys = [k for k in ["personality", "background", "class", "race", "motivation"] if char.get(k) and char[k] not in ["Unknown", "A brave adventurer", None, ""]]
        return len(core_keys) >= 3

    def save_character(self, campaign_id: str):
        """Save character data to file."""
        try:
            os.makedirs("character_saves", exist_ok=True)
            character_file = f"character_saves/{campaign_id}_character.json"
            with open(character_file, 'w') as f:
                json.dump(self.character_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving character: {e}")

    def _log_session_event(self, event_type: str, data: Dict[str, Any]):
        """Log a session event with timestamp."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            'event': event_type,
            'data': data,
            'timestamp': timestamp,
            'session_id': self.session_id
        }
        self._write_log_entry(log_entry)
        logger.info(f"📋 [SESSION] {event_type}: {data} @ {timestamp}")

    def _present_fact_validation(self):
        """Present the current pending facts for user validation with change type indication."""
        if not self.pending_facts:
            return "No new facts extracted."
        
        summary_parts = []
        for k, v in self.pending_facts.items():
            if v.get('is_removal'):
                summary_parts.append(f"**Remove {k.title()}**: {v.get('old_value', 'current value')}")
            elif v.get('is_correction'):
                summary_parts.append(f"**Correct {k.title()}**: {v.get('old_value', 'current value')} → {v['value']}")
            elif v.get('is_expansion'):
                summary_parts.append(f"**Expand {k.title()}**: {v['value']}")
            else:
                summary_parts.append(f"**Add {k.title()}**: {v['value']}")
        
        summary_text = '\n'.join(summary_parts)
        return f"Here's what I've got so far:\n{summary_text}\n\nIs this correct? You can correct, remove, or expand on any fact."

    def _check_for_contradictions(self, new_facts: Dict[str, Any]) -> List[str]:
        """Check for contradictions between new facts and existing character data."""
        contradictions = []
        for fact_type, fact_data in new_facts.items():
            if fact_data.get('is_correction') or fact_data.get('is_expansion'):
                old_value = self.character_data.get(fact_type)
                new_value = fact_data['value']
                if old_value and old_value != new_value and not fact_data.get('is_expansion'):
                    contradictions.append(fact_type)
        return contradictions

    def _handle_contradictory_info(self, fact_type: str, new_value: str, old_value: str) -> str:
        """Handle contradictory information by asking for clarification."""
        clarification_prompts = {
            "age": f"You mentioned {old_value} before, but now you've said {new_value}. Which age would you like to keep?",
            "race": f"You mentioned {old_value} before, but now you've said {new_value}. Which race would you like to keep?",
            "class": f"You mentioned {old_value} before, but now you've said {new_value}. Which class would you like to keep?",
            "name": f"You mentioned {old_value} before, but now you've said {new_value}. Which name would you like to keep?",
            "background": f"You mentioned {old_value} before, but now you've said {new_value}. Which background would you like to keep?",
            "personality": f"You mentioned '{old_value}' before, but now you've said '{new_value}'. Which personality description would you like to keep?"
        }
        
        return clarification_prompts.get(fact_type, f"You mentioned {old_value} before, but now you've said {new_value}. Which would you like to keep?")

    def save_draft_with_metadata(self):
        self.draft_saved = True
        self.draft_id = self.session_id
        self._log_session_event('draft_saved', {'character_data': self.character_data})
        # Calculate % complete
        total = len([k for k in self.fact_types if self.fact_types[k]['required']])
        filled = len([k for k in self.fact_types if self.fact_types[k]['required'] and self.fact_types[k]['extracted']])
        percent_complete = int((filled / total) * 100) if total else 0
        metadata = {
            'character_name': self.character_data.get('name', 'Adventurer'),
            'status': 'draft',
            'percent_complete': percent_complete,
            'session_id': self.session_id,
            'session_start_time': str(self.session_start_time),
            'session_end_time': str(datetime.datetime.now()),
            'fact_types': self.fact_types,
            'character_data': self.character_data
        }
        draft_path = f"logs/character_creation_sessions/{self.session_id}.jsonl"
        with open(draft_path, 'w') as f:
            f.write('# ' + json.dumps(metadata) + '\n')
        return True

    def _update_fact_types(self, fact_type, value, source_text):
        """Update fact_types tracking with new fact."""
        self.fact_types[fact_type]['extracted'] = True
        self.fact_types[fact_type]['value'] = value
        self.fact_types[fact_type]['source_text'] = source_text
        self.fact_types[fact_type]['timestamp'] = datetime.datetime.now().isoformat()
        self._log_fact_extraction(fact_type, value, source_text)

    def _log_fact_extraction(self, fact_type: str, value: str, source_text: str):
        """Log a fact extraction with timestamp."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            'event': 'fact_extraction',
            'fact_type': fact_type,
            'value': value,
            'source_text': source_text,
            'timestamp': timestamp
        }
        self._write_log_entry(log_entry)
        logger.info(f"🔍 [EXTRACTION] {fact_type}: {value} from '{source_text[:50]}...' @ {timestamp}")

class SimpleNarrativeBridge:
    """Simple narrative bridge for SoloHeart (without complex Narrative Engine)."""
    
    def __init__(self):
        self.ensure_directories()
        self.current_campaign_id = None
    
    def ensure_directories(self):
        """Ensure necessary directories exist."""
        os.makedirs("campaign_saves", exist_ok=True)
        os.makedirs("character_saves", exist_ok=True)
    
    def initialize_campaign(self, character_data: Dict[str, Any], campaign_name: str = None) -> Optional[Dict[str, Any]]:
        """Initialize a new campaign with character data."""
        try:
            campaign_id = str(uuid.uuid4())[:8]
            campaign_name = campaign_name or f"Campaign {campaign_id}"
            
            # Create simple campaign data
            campaign_data = {
                "id": campaign_id,
                "name": campaign_name,
                "created_date": datetime.datetime.now().isoformat(),
                "last_modified": datetime.datetime.now().isoformat(),
                "active_character": character_data,
                "opening_scene": self._generate_simple_opening_scene(character_data),
                "session_count": 1,
                "narrative_engine_initialized": False
            }
            
            # Save campaign data to file
            campaign_file = f"campaign_saves/{campaign_id}.json"
            with open(campaign_file, 'w') as f:
                json.dump(campaign_data, f, indent=2)
            
            # Save character
            character_file = f"character_saves/{campaign_id}_character.json"
            with open(character_file, 'w') as f:
                json.dump(character_data, f, indent=2)
            
            self.current_campaign_id = campaign_id
            logger.info(f"✅ Initialized simple campaign: {campaign_id}")
            return campaign_data
            
        except Exception as e:
            logger.error(f"❌ Error initializing campaign: {e}")
            return None
    
    def _generate_simple_opening_scene(self, character_data: Dict[str, Any]) -> str:
        """Generate a simple opening scene."""
        name = character_data.get('name', 'Adventurer')
        race = character_data.get('race', 'Human')
        char_class = character_data.get('class', 'Fighter')
        
        return f"You are {name}, a {race} {char_class}. Your adventure begins in a bustling tavern where rumors of ancient treasures and dark threats whisper through the air. What would you like to do?"
    

    
    def load_campaign(self, campaign_id: str) -> bool:
        """Load an existing campaign."""
        try:
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if not os.path.exists(campaign_file):
                logger.error(f"❌ Campaign file not found: {campaign_file}")
                return False
            
            self.current_campaign_id = campaign_id
            logger.info(f"✅ Loaded simple campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading campaign: {e}")
            return False
    
    def process_player_input(self, player_input: str, campaign_id: str) -> str:
        """Process player input and return SoloHeart Guide response."""
        try:
            # Get campaign context
            campaign_context = self.get_campaign_data(campaign_id)
            if not campaign_context:
                return "I'm sorry, but I can't find your campaign data. Please try starting a new campaign."
            
            # Create a simple prompt for the LLM
            character = campaign_context.get('active_character', {})
            name = character.get('name', 'Adventurer')
            race = character.get('race', 'Human')
            char_class = character.get('class', 'Fighter')
            
            system_prompt = f"""You are a SoloHeart Guide, an AI companion for immersive solo narrative adventures. 

The player is {name}, a {race} {char_class}. 

Your role is to:
1. Create immersive, atmospheric scenes
2. Respond to player actions and choices
3. Maintain narrative continuity
4. Provide meaningful consequences for player decisions
5. Ask clarifying questions when needed

Write in third person, present tense. Be descriptive and engaging. Keep responses concise but vivid."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": player_input}
            ]
            
            # Use the LLM service
            response = chat_completion(messages, temperature=0.8, max_tokens=300)
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ Error processing player input: {e}")
            return "I'm sorry, but I'm having trouble processing that right now. Please try again."
    
    def save_campaign(self, campaign_id: str) -> bool:
        """Save current campaign state."""
        try:
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if os.path.exists(campaign_file):
                with open(campaign_file, 'r') as f:
                    campaign_data = json.load(f)
                
                campaign_data["last_modified"] = datetime.datetime.now().isoformat()
                campaign_data["session_count"] = campaign_data.get("session_count", 0) + 1
                
                with open(campaign_file, 'w') as f:
                    json.dump(campaign_data, f, indent=2)
            
            logger.info(f"✅ Saved simple campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving campaign: {e}")
            return False
    
    def get_campaign_data(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign data."""
        try:
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if not os.path.exists(campaign_file):
                return None
            
            with open(campaign_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error getting campaign data: {e}")
            return None

class SimpleUnifiedGame:
    """Simple unified game manager."""
    
    def __init__(self):
        self.character_generator = SimpleCharacterGenerator()
        self.narrative_bridge = SimpleNarrativeBridge()
    
    def get_saved_campaigns(self):
        """Get list of all saved campaigns."""
        campaigns = []
        try:
            if os.path.exists('campaign_saves'):
                for filename in os.listdir('campaign_saves'):
                    if filename.endswith('.json'):
                        campaign_id = filename.replace('.json', '')
                        filepath = os.path.join('campaign_saves', filename)
                        
                        try:
                            with open(filepath, 'r') as f:
                                campaign_data = json.load(f)
                            
                            campaigns.append({
                                'id': campaign_id,
                                'name': campaign_data.get('name', f'Campaign {campaign_id}'),
                                'created_date': campaign_data.get('created_date', 'Unknown'),
                                'last_modified': datetime.datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                                'character_name': campaign_data.get('active_character', {}).get('name', 'Unknown')
                            })
                        except Exception as e:
                            logger.error(f"Error reading campaign {campaign_id}: {e}")
                            campaigns.append({
                                'id': campaign_id,
                                'name': f'Campaign {campaign_id} (Corrupted)',
                                'created_date': 'Unknown',
                                'last_modified': 'Unknown',
                                'character_name': 'Unknown'
                            })
        except Exception as e:
            logger.error(f"Error listing campaigns: {e}")
        
        return sorted(campaigns, key=lambda x: x['last_modified'], reverse=True)
    
    def delete_campaign(self, campaign_id):
        """Delete a campaign and all its associated files."""
        try:
            # Delete main campaign file
            campaign_file = os.path.join('campaign_saves', f'{campaign_id}.json')
            if os.path.exists(campaign_file):
                os.remove(campaign_file)
            
            # Delete associated files
            associated_files = [
                f'{campaign_id}_character.json'
            ]
            
            for filename in associated_files:
                filepath = os.path.join('character_saves', filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            return True
        except Exception as e:
            logger.error(f"Error deleting campaign {campaign_id}: {e}")
            return False

# Initialize game manager
game = SimpleUnifiedGame()

@app.route('/')
def start_screen():
    """Start screen - the only gamified portion of the UI."""
    return render_template('start_screen.html')

@app.route('/api/campaigns')
def list_campaigns():
    """List all saved campaigns."""
    campaigns = game.get_saved_campaigns()
    return jsonify({'success': True, 'campaigns': campaigns})

@app.route('/api/campaigns/<campaign_id>/delete', methods=['POST'])
def delete_campaign(campaign_id):
    """Delete a campaign."""
    success = game.delete_campaign(campaign_id)
    return jsonify({'success': success})

@app.route('/api/campaigns/<campaign_id>/load', methods=['POST'])
def load_campaign(campaign_id):
    """Load a campaign and redirect to game."""
    try:
        success = game.narrative_bridge.load_campaign(campaign_id)
        if success:
            session['campaign_id'] = campaign_id
            return jsonify({'success': True, 'redirect': '/game'})
        else:
            return jsonify({'success': False, 'message': 'Failed to load campaign'})
    except Exception as e:
        logger.error(f"Error loading campaign: {e}")
        return jsonify({'success': False, 'message': 'Error loading campaign'})

@app.route('/character-creation')
def character_creation():
    """Character creation screen with two options."""
    return render_template('character_creation.html')

@app.route('/vibe-code-creation')
def vibe_code_creation():
    """Vibe code character creation interface."""
    return render_template('vibe_code_creation.html')

@app.route('/api/character/vibe-code/start', methods=['POST'])
def start_vibe_code_creation():
    """Start the vibe code character creation process with conversational approach."""
    try:
        logger.info("🚀 Starting vibe code character creation...")
        data = request.get_json()
        description = data.get('description', '')
        campaign_name = data.get('campaign_name', '')
        
        logger.info(f"📝 Raw user input: '{description}'")
        logger.info(f"🎯 Campaign: {campaign_name}")
        
        if not description:
            logger.warning("❌ No description provided")
            return jsonify({'success': False, 'message': 'Character description is required'})
        
        # Initialize narrative bridge for character creation
        logger.info("🔧 Initializing narrative bridge...")
        temp_bridge = SimpleNarrativeBridge()
        game.character_generator.narrative_bridge = temp_bridge
        
        # Start character creation session
        game.character_generator._log_session_event('session_start', {'description': description, 'campaign_name': campaign_name})
        
        # Start conversational character creation
        result = game.character_generator.start_character_creation(description, campaign_name)
        
        # Store the character generator state in session
        session['character_creation_active'] = True
        session['campaign_name'] = campaign_name
        
        logger.info("💾 Session data stored successfully")
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'is_complete': result.get('is_complete', False),
            'current_step': result.get('current_step', 'conversation')
        })
    except Exception as e:
        logger.error(f"❌ Error starting vibe code creation: {e}")
        import traceback
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'Error starting character creation: {str(e)}'})

@app.route('/api/character/vibe-code/continue', methods=['POST'])
def continue_vibe_code_creation():
    """Continue the vibe code character creation conversation."""
    try:
        logger.info("🔄 Continuing vibe code character creation...")
        data = request.get_json()
        user_input = data.get('user_input', '')
        
        logger.info(f"📝 Raw user input: '{user_input}'")
        
        if not user_input:
            logger.warning("❌ No user input provided")
            return jsonify({'success': False, 'message': 'User input is required'})
        
        # Continue conversational character creation
        result = game.character_generator.continue_conversation(user_input)
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'is_complete': result.get('is_complete', False),
            'current_step': result.get('current_step', 'conversation'),
            'in_review_mode': result.get('in_review_mode', False)
        })
    except Exception as e:
        logger.error(f"Error in continue_vibe_code_creation: {e}")
        return jsonify({'success': False, 'message': 'Error continuing character creation.'})

@app.route('/api/character/vibe-code/confirm', methods=['POST'])
def confirm_vibe_code_facts():
    """Confirm or correct pending facts."""
    try:
        data = request.get_json()
        corrections = data.get('corrections', None)  # Dict of fact_type: new_value or None
        # Commit all facts in pending_facts after confirmation
        for k, v in game.character_generator.pending_facts.items():
            if corrections and k in corrections:
                new_value = corrections[k]
                if new_value is None:
                    # Remove fact
                    old_value = game.character_generator.character_data.get(k)
                    game.character_generator._log_fact_removal(k, old_value)
                    if k in game.character_generator.character_data:
                        del game.character_generator.character_data[k]
                    if k in game.character_generator.fact_types:
                        game.character_generator.fact_types[k]['extracted'] = False
                        game.character_generator.fact_types[k]['value'] = None
                else:
                    # Update fact
                    old_value = game.character_generator.character_data.get(k)
                    if old_value and old_value != new_value:
                        game.character_generator._log_fact_correction(k, old_value, new_value)
                    v['value'] = new_value
            # Commit fact
            old_value = game.character_generator.character_data.get(k)
            new_value = v['value']
            if old_value and old_value != new_value:
                game.character_generator._log_fact_correction(k, old_value, new_value)
            else:
                game.character_generator._log_fact_addition(k, new_value)
            game.character_generator._update_fact_types(k, new_value, v['source_text'])
            game.character_generator.character_data[k] = new_value
        game.character_generator.pending_facts = {}
        game.character_generator._log_session_event('fact_confirmation', {'facts': game.character_generator.character_data})
        # After confirmation, check if more facts are needed
        missing = [k for k, v in game.character_generator.fact_types.items() if v['required'] and not v['extracted']]
        if missing:
            return jsonify({'success': True, 'message': f"Thanks! I still need: {', '.join(missing)}. Please provide more details.", 'fact_types': game.character_generator.fact_types})
        else:
            summary = game.character_generator.get_fact_summary()
            return jsonify({'success': True, 'message': summary + '\nAre you ready to start your adventure with this character?', 'fact_types': game.character_generator.fact_types})
    except Exception as e:
        logger.error(f"Error confirming facts: {e}")
        return jsonify({'success': False, 'message': 'Error confirming facts.'})

@app.route('/api/character/vibe-code/summary', methods=['GET'])
def get_character_summary():
    """Return a summary of all committed facts."""
    summary = game.character_generator.get_fact_summary()
    return jsonify({'success': True, 'summary': summary})

@app.route('/api/character/vibe-code/save-draft', methods=['POST'])
def save_character_draft():
    """Save the current character as a draft."""
    try:
        game.character_generator.save_draft()
        return jsonify({'success': True, 'message': 'Draft saved.'})
    except Exception as e:
        logger.error(f"Error saving draft: {e}")
        return jsonify({'success': False, 'message': 'Error saving draft.'})

@app.route('/api/character/vibe-code/complete', methods=['POST'])
def complete_vibe_code_creation():
    """Complete character creation and start campaign."""
    try:
        logger.info("🎯 Completing vibe code character creation...")
        
        # Get character data
        logger.info("📋 Getting character data...")
        character_data = game.character_generator.get_character_data()
        campaign_name = session.get('campaign_name', 'New Campaign')
        
        logger.info(f"📝 Campaign name: {campaign_name}")
        logger.info(f"👤 Final character: {character_data.get('race', 'Unknown')} {character_data.get('class', 'Unknown')} named {character_data.get('name', 'Unknown')}")
        
        if not character_data:
            logger.error("❌ No character data available")
            return jsonify({'success': False, 'message': 'No character data available'})
        
        # Initialize campaign
        logger.info("🚀 Initializing campaign...")
        campaign_data = game.narrative_bridge.initialize_campaign(character_data, campaign_name)
        
        if campaign_data:
            logger.info(f"✅ Campaign initialized with ID: {campaign_data.get('id', 'Unknown')}")
            
            # Store character creation data in memory (this is now called within initialize_campaign)
            # The store_character_creation method is called automatically during campaign initialization
            
            # Clear session data
            logger.info("🧹 Clearing session data...")
            session.pop('character_creation_active', None)
            session.pop('campaign_name', None)
            session['campaign_id'] = campaign_data['id']
            
            logger.info("🎉 Character creation completed successfully!")
            return jsonify({
                'success': True,
                'message': 'Character created and campaign started!',
                'redirect': '/game'
            })
        else:
            logger.error("❌ Failed to initialize campaign")
            return jsonify({'success': False, 'message': 'Failed to start campaign'})
    
    except Exception as e:
        logger.error(f"❌ Error completing vibe code creation: {e}")
        import traceback
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'Error completing character creation'})

@app.route('/api/character/vibe-code/undo', methods=['POST'])
def undo_last_character_fact():
    """Undo the last committed character fact."""
    try:
        # Get character generator from session
        if not hasattr(game, 'character_generator'):
            return jsonify({"success": False, "message": "No active character creation session"}), 400
        
        generator = game.character_generator
        undone_fact = generator.undo_last_fact()
        
        if undone_fact is None:
            return jsonify({
                "success": False, 
                "message": "No facts to undo"
            }), 400
        
        fact_type, old_value = undone_fact
        
        return jsonify({
            "success": True,
            "message": f"Undid {fact_type}: {old_value}",
            "undone_fact": {
                "type": fact_type,
                "old_value": old_value
            },
            "current_character_data": generator.get_character_data()
        })
        
    except Exception as e:
        logger.error(f"Error undoing last fact: {e}")
        return jsonify({"success": False, "message": "Error undoing last fact"}), 500

@app.route('/api/character/vibe-code/edit', methods=['POST'])
def edit_character():
    """Apply edits to character during review mode."""
    try:
        data = request.get_json()
        edit_message = data.get('edit_message', '')
        
        if not edit_message:
            return jsonify({'success': False, 'message': 'Edit message is required'})
        
        # Get character generator from session
        if not hasattr(game, 'character_generator'):
            return jsonify({"success": False, "message": "No active character creation session"}), 400
        
        generator = game.character_generator
        
        # Apply the edit
        result = generator.apply_character_edit(edit_message)
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'summary': result.get('summary', ''),
            'character_data': generator.get_character_data()
        })
        
    except Exception as e:
        logger.error(f"Error editing character: {e}")
        return jsonify({'success': False, 'message': 'Error editing character'})

@app.route('/api/character/vibe-code/finalize', methods=['POST'])
def finalize_character():
    """Finalize character and start campaign."""
    try:
        # Get character generator from session
        if not hasattr(game, 'character_generator'):
            return jsonify({"success": False, "message": "No active character creation session"}), 400
        
        generator = game.character_generator
        
        # Finalize the character
        result = generator.finalize_character()
        
        if not result['success']:
            return jsonify(result)
        
        # Get campaign name from session
        campaign_name = session.get('campaign_name', 'New Campaign')
        
        # Initialize campaign with finalized character
        campaign_data = game.narrative_bridge.initialize_campaign(result['character_data'], campaign_name)
        
        if campaign_data:
            # Clear session data
            session.pop('character_creation_active', None)
            session.pop('campaign_name', None)
            session['campaign_id'] = campaign_data['id']
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'redirect': '/game'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to start campaign'})
        
    except Exception as e:
        logger.error(f"Error finalizing character: {e}")
        return jsonify({'success': False, 'message': 'Error finalizing character'})

@app.route('/api/character/create', methods=['POST'])
def create_character():
    """Create character using step-by-step form."""
    try:
        data = request.get_json()
        
        # Extract all character data from form (SRD-compliant)
        character_data = {
            'name': data.get('name', 'Adventurer'),
            'race': data.get('race', 'Human'),
            'class': data.get('class', 'Fighter'),
            'level': int(data.get('level', 1)),
            'background': data.get('background', 'Adventurer'),
            'personality': data.get('personality', 'A brave adventurer'),
            
            # Ability scores
            'ability_scores': {
                'strength': int(data.get('str', 10)),
                'dexterity': int(data.get('dex', 10)),
                'constitution': int(data.get('con', 10)),
                'intelligence': int(data.get('int', 10)),
                'wisdom': int(data.get('wis', 10)),
                'charisma': int(data.get('cha', 10))
            },
            
            # Combat stats
            'hit_points': int(data.get('hp', 10)),
            'armor_class': 10,  # Default, will be calculated based on class/equipment
            
            # Proficiencies
            'saving_throws': data.get('savingThrows', '').split(', ') if data.get('savingThrows') else [],
            'skills': data.get('skills', '').split(', ') if data.get('skills') else [],
            'feats': data.get('feats', '').split(', ') if data.get('feats') else [],
            
            # Equipment
            'weapons': data.get('weapons', '').split(', ') if data.get('weapons') else [],
            'gear': data.get('gear', '').split(', ') if data.get('gear') else [],
            'spells': data.get('spells', '').split(', ') if data.get('spells') else [],
            
            # Freeform background
            'background_freeform': data.get('backgroundFreeform', ''),
            
            'created_date': datetime.datetime.now().isoformat()
        }
        
        campaign_name = data.get('campaign_name', 'New Campaign')
        
        # Initialize campaign
        campaign_data = game.narrative_bridge.initialize_campaign(character_data, campaign_name)
        
        if campaign_data:
            # Store character creation data in memory (this is now called within initialize_campaign)
            # The store_character_creation method is called automatically during campaign initialization
            
            session['campaign_id'] = campaign_data['id']
            return jsonify({
                'success': True,
                'message': 'Character created and campaign started!',
                'redirect': '/game'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to start campaign'})
    
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        return jsonify({'success': False, 'message': 'Error creating character'})

@app.route('/game')
def game_screen():
    """Main game interface - pure conversation."""
    return render_template('game_screen.html')

@app.route('/api/game/action', methods=['POST'])
def process_game_action():
    """Process player action in the game."""
    try:
        data = request.get_json()
        player_input = data.get('input', '')
        campaign_id = session.get('campaign_id')
        
        if not player_input:
            return jsonify({'success': False, 'message': 'Player input is required'})
        
        if not campaign_id:
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        # Process player input
        guide_response = game.narrative_bridge.process_player_input(player_input, campaign_id)
        
        # Save campaign
        game.narrative_bridge.save_campaign(campaign_id)
        
        return jsonify({
            'success': True,
            'response': guide_response
        })
    
    except Exception as e:
        logger.error(f"Error processing game action: {e}")
        return jsonify({'success': False, 'message': 'Error processing action'})

@app.route('/api/game/save', methods=['POST'])
def save_game():
    """Save current game state."""
    try:
        campaign_id = session.get('campaign_id')
        if not campaign_id:
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        success = game.narrative_bridge.save_campaign(campaign_id)
        return jsonify({'success': success})
    
    except Exception as e:
        logger.error(f"Error saving game: {e}")
        return jsonify({'success': False, 'message': 'Error saving game'})

@app.route('/api/game/current')
def get_current_game():
    """Get current game state."""
    try:
        campaign_id = session.get('campaign_id')
        if not campaign_id:
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        campaign_data = game.narrative_bridge.get_campaign_data(campaign_id)
        if not campaign_data:
            return jsonify({'success': False, 'message': 'Campaign not found'})
        
        return jsonify({
            'success': True,
            'campaign': campaign_data
        })
    
    except Exception as e:
        logger.error(f"Error getting current game: {e}")
        return jsonify({'success': False, 'message': 'Error getting game state'})

@app.route('/api/character/vibe-code/load-draft', methods=['POST'])
def load_character_draft():
    """Load a saved character draft and resume the conversation flow."""
    try:
        data = request.get_json()
        draft_id = data.get('draft_id', None)
        if not draft_id:
            return jsonify({'success': False, 'message': 'Draft ID required.'})
        draft_path = f"logs/character_creation_sessions/{draft_id}.jsonl"
        if not os.path.exists(draft_path):
            return jsonify({'success': False, 'message': 'Draft not found.'})
        # Read metadata and fact state
        with open(draft_path, 'r') as f:
            lines = f.readlines()
        # First line is metadata block
        metadata = json.loads(lines[0].strip().lstrip('# '))
        # Remaining lines are fact logs (optional for future use)
        # Restore fact_types and character_data
        game.character_generator.fact_types = metadata['fact_types']
        game.character_generator.character_data = metadata['character_data']
        game.character_generator.session_id = draft_id
        game.character_generator.session_start_time = metadata.get('session_start_time')
        # Resume validation/conversation
        missing = [k for k, v in game.character_generator.fact_types.items() if v['required'] and not v['extracted']]
        if missing:
            prompt = f"Draft loaded. I still need: {', '.join(missing)}. Please provide more details."
        else:
            prompt = game.character_generator.get_fact_summary() + '\nAre you ready to start your adventure with this character?'
        return jsonify({'success': True, 'message': prompt, 'fact_types': game.character_generator.fact_types})
    except Exception as e:
        logger.error(f"Error loading draft: {e}")
        return jsonify({'success': False, 'message': 'Error loading draft.'})

if __name__ == '__main__':
    print("🎲 Starting Simple Unified SoloHeart Narrative Interface...")
    print("Access the game at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5001, debug=True)
