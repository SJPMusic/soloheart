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
    extract_combat_style,
    extract_traits,
    extract_motivations,
    extract_emotional_themes,
    extract_alignment_from_text
)
from utils.symbolic_meaning_framework import SymbolicMeaningFramework
from utils.guided_character_completion import GuidedCharacterCompletion, CompletionPhase, StatAssignmentMode
# Temporarily disable Narrative Engine integration due to missing modules
# from narrative_engine_integration import SoloHeartNarrativeEngine

# Enable Narrative Engine integration for persistent memory and context tracking
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
    """Enhanced character generator for player-led, natural language character creation with immediate fact commitment."""
    
    def __init__(self, playtest_mode: bool = None):
        self.conversation_history = []
        self.character_data = {
            "name": None,
            "race": None,
            "class": None,
            "level": 1,
            "background": None,
            "alignment": None,
            "personality_traits": [],
            "age": None,
            "gender": None,
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
            "created_date": None,
            "motivations": [],
            "emotional_themes": [],
            "combat_style": None,
            "combat_experience": None,
            "traits": [],
            "traumas": [],
            "relational_history": {},
            "backstory": "",
            "_symbolic_data": {}  # Store archetypal tags and symbolic meaning
        }
        
        # Initialize symbolic meaning framework
        self.symbolic_framework = SymbolicMeaningFramework()
        self.is_complete = False
        self.character_finalized = False
        self.in_review_mode = False
        self.narrative_bridge = None
        self.fact_history = []
        
        # Initialize guided completion system
        self.guided_completion = GuidedCharacterCompletion()
        
        # Enhanced fact tracking for DnD 5E compliance
        self.fact_types = {
            "name": {"required": True, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "race": {"required": True, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "class": {"required": True, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "background": {"required": True, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "personality_traits": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "age": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "gender": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "alignment": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "motivations": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "emotional_themes": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "combat_style": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "combat_experience": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "traits": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "traumas": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "relational_history": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "gear": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None},
            "backstory": {"required": False, "extracted": False, "value": None, "source_text": None, "timestamp": None}
        }
        
        # Session tracking
        self.session_id = str(uuid.uuid4())
        self.session_start_time = datetime.datetime.now()
        self.arc_scaffolding_triggered = False
        
        # Ensure logs directory exists
        os.makedirs("logs/character_creation_sessions", exist_ok=True)
        
        if playtest_mode is None:
            playtest_mode = os.environ.get('PLAYTEST_LOG', '0') == '1'
        self.playtest_mode = playtest_mode
    
    def _log(self, method, *args, **kwargs):
        # Logging disabled - removed playtest logger
        pass
    
    def _extract_facts_with_llm(self, text: str) -> Dict[str, Any]:
        """
        Extract character facts using Ollama LLM with structured JSON output.
        This replaces the pattern-matching approach with semantic understanding.
        """
        try:
            # Get current character data to show what's already committed
            current_facts = self.get_character_data()
            current_facts_str = ""
            if current_facts:
                # Filter out empty/null values for cleaner display
                display_facts = {k: v for k, v in current_facts.items() if v and v != [] and v != {}}
                if display_facts:
                    current_facts_str = f"\n\nCURRENTLY COMMITTED FACTS (DO NOT CHANGE THESE):\n{json.dumps(display_facts, indent=2)}"
            
            # Create a comprehensive prompt for the LLM
            prompt = f"""Extract all DnD 5E character facts from the following player description. 
Return a JSON object with these exact fields: name, race, class, background, age, gender, alignment, 
personality_traits, motivations, emotional_themes, combat_style, traits, traumas, relational_history, gear, backstory.

CRITICAL RULES:
- ONLY extract facts that are EXPLICITLY mentioned in the text
- If a field is not mentioned or is ambiguous, set its value to null
- DO NOT make assumptions or inferences about missing information
- DO NOT change facts that are already committed (see below)
- For age: only set if explicitly mentioned (e.g., "25 years old", "I am 30")
- For gender: only set if explicitly mentioned or clear from pronouns
- For lists like personality_traits, motivations, etc., return as arrays
- For relational_history, return as an object with relationship keys
- For gear, return as an array of items
- Use proper DnD 5E terminology for races, classes, and backgrounds
- Be conservative - it's better to return null than to guess

Player description:
{text}{current_facts_str}

Return only valid JSON:"""

            # Call Ollama LLM using the correct format
            messages = [{"role": "user", "content": prompt}]
            response = chat_completion(messages)
            
            # Parse the JSON response
            import json
            import re
            
            # Try to extract JSON from the response (in case LLM adds extra text)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response
            
            facts = json.loads(json_str)
            
            # Clean up the extracted facts and respect already committed facts
            cleaned_facts = {}
            for key, value in facts.items():
                if value is not None and value != "" and value != [] and value != {}:
                    # Don't override already committed facts
                    if key in current_facts and current_facts[key] and current_facts[key] != [] and current_facts[key] != {}:
                        logger.debug(f"🤖 Skipping {key} - already committed as: {current_facts[key]}")
                        continue
                    cleaned_facts[key] = value
            
            logger.info(f"🤖 LLM extracted facts: {cleaned_facts}")
            return cleaned_facts
            
        except Exception as e:
            logger.error(f"❌ LLM extraction failed: {e}")
            logger.error(f"LLM response was: {response if 'response' in locals() else 'No response'}")
            return {}
    
    def _extract_and_commit_facts_immediately(self, text: str) -> Dict[str, Any]:
        """
        Extract facts from text using LLM as primary method, with pattern-matching fallback.
        Returns dict of newly committed facts and any ambiguous ones requiring confirmation.
        """
        logger.info(f"🔍 Extracting facts from: '{text[:100]}...'")
        
        newly_committed = {}
        ambiguous_facts = {}
        
        # Try LLM extraction first
        llm_facts = self._extract_facts_with_llm(text)
        
        # Post-process: Only commit age if explicitly present in text
        if llm_facts and 'age' in llm_facts:
            age_pattern = re.search(r'(\d+)\s*(?:year|yr)s?\s*old', text.lower())
            if not age_pattern:
                llm_facts['age'] = None
        
        if llm_facts:
            # LLM extraction succeeded - commit all facts
            for fact_type, value in llm_facts.items():
                if value is not None and value != "" and value != [] and value != {}:
                    self._commit_fact_immediately(fact_type, value, text)
                    newly_committed[fact_type] = value
                    logger.info(f"🤖 LLM committed {fact_type}: {value}")
            
            logger.info(f"✅ LLM committed facts: {newly_committed}")
            return {
                "committed": newly_committed,
                "ambiguous": ambiguous_facts
            }
        
        # Fallback to pattern-matching if LLM failed
        logger.info("🔄 LLM extraction failed, falling back to pattern-matching...")
        
        # Extract facts using individual extraction functions
        extracted_facts = {}
        
        # Extract basic facts
        name = extract_name_from_text(text)
        if name:
            extracted_facts['name'] = name
            
        race = extract_race_from_text(text)
        if race:
            extracted_facts['race'] = race
            
        char_class = extract_class_from_text(text)
        if char_class:
            extracted_facts['class'] = char_class
            
        background = extract_background_from_text(text)
        if background:
            extracted_facts['background'] = background
            
        # Extract alignment
        alignment = extract_alignment_from_text(text)
        if alignment:
            extracted_facts['alignment'] = alignment
            
        combat_style = extract_combat_style(text)
        if combat_style:
            extracted_facts['combat_style'] = combat_style
            
        traits = extract_traits(text)
        if traits:
            extracted_facts['traits'] = traits
            
        motivations = extract_motivations(text)
        if motivations:
            extracted_facts['motivations'] = motivations
            
        emotional_themes = extract_emotional_themes(text)
        if emotional_themes:
            extracted_facts['emotional_themes'] = emotional_themes
        
        # Extract age using simple pattern
        age_match = re.search(r'(\d+)\s*(?:year|yr)s?\s*old', text.lower())
        if age_match:
            extracted_facts['age'] = int(age_match.group(1))
            
        # Extract gender using simple patterns
        if re.search(r'\b(he|his|him)\b', text.lower()):
            extracted_facts['gender'] = 'Male'
        elif re.search(r'\b(she|her|hers)\b', text.lower()):
            extracted_facts['gender'] = 'Female'
        elif re.search(r'\b(they|their|them)\b', text.lower()):
            extracted_facts['gender'] = 'Non-binary'
        
        # Process each extracted fact
        for fact_type, value in extracted_facts.items():
            if value is None or value == [] or value == {}:
                continue
            
            # Commit all extracted facts immediately (simplified approach)
            self._commit_fact_immediately(fact_type, value, text)
            newly_committed[fact_type] = value
            logger.debug(f"✅ Pattern-matching committed: {fact_type} = {value}")
        
        logger.info(f"✅ Pattern-matching committed facts: {newly_committed}")
        
        return {
            "committed": newly_committed,
            "ambiguous": ambiguous_facts
        }
    
    def _commit_fact_immediately(self, fact_type: str, value: Any, source_text: str) -> None:
        """Commit a fact immediately to character_data without staging."""
        timestamp = datetime.datetime.now()
        
        # Update character_data based on fact type
        if fact_type in ["motivations", "emotional_themes", "traits", "personality_traits", "traumas", "gear"] and isinstance(value, list):
            # Append to existing list-type facts
            existing = self.character_data.get(fact_type, [])
            for item in value:
                if item not in existing:
                    existing.append(item)
            self.character_data[fact_type] = existing
        elif fact_type == "relational_history" and isinstance(value, dict):
            # Merge relational history
            existing = self.character_data.get("relational_history", {})
            existing.update(value)
            self.character_data["relational_history"] = existing
        else:
            # Direct assignment for other types
            self.character_data[fact_type] = value
        
        # Update fact tracking
        if fact_type in self.fact_types:
            self.fact_types[fact_type]["extracted"] = True
            self.fact_types[fact_type]["value"] = value
            self.fact_types[fact_type]["source_text"] = source_text
            self.fact_types[fact_type]["timestamp"] = timestamp
        
        # Log the fact commitment
        self._log_fact_commitment(fact_type, value, source_text, timestamp)
        
        logger.info(f"✅ Committed {fact_type}: {value}")
    
    def _log_fact_commitment(self, fact_type: str, value: Any, source_text: str, timestamp: datetime.datetime) -> None:
        """Log a fact commitment with timestamp."""
        log_entry = {
            'event': 'fact_commitment',
            'fact_type': fact_type,
            'value': value,
            'source_text': source_text,
            'timestamp': timestamp.isoformat(),
            'session_id': self.session_id
        }

        # Write to log file
        log_file = f"logs/character_creation_sessions/{self.session_id}.jsonl"
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write log entry: {e}")
    
    def _should_trigger_emotional_scaffolding(self) -> bool:
        """Check if emotional scaffolding should be triggered."""
        if self.arc_scaffolding_triggered:
            return False

        # Check if we have at least 3 core attributes
        core_attributes = ["background", "class", "race", "personality_traits", "motivations"]
        confirmed_attributes = sum(1 for attr in core_attributes 
                                 if self.character_data.get(attr) and 
                                 self.character_data[attr] not in [None, "Unknown", "", [], {}])
        
        return confirmed_attributes >= 3
    
    def _build_emotional_scaffolding_prompt(self) -> str:
        """Build a gentle emotional scaffolding prompt."""
        char_name = self.character_data.get('name', 'your character')
        if char_name == 'Adventurer' or not char_name:
            char_name = 'your character'
        
        # Get detected themes
        themes = self.character_data.get('emotional_themes', [])
        motivations = self.character_data.get('motivations', [])
        
        if themes or motivations:
            theme_text = ", ".join(themes + motivations).lower()
            prompt = f"It sounds like {char_name} carries themes of {theme_text}. "
        else:
            prompt = f"It sounds like {char_name} has been through some intense experiences. "
        
        prompt += "Do you imagine their story heading toward redemption, vengeance, transformation, or something else? Or would you rather discover it during play? (This is totally optional!)"
        
        return prompt
    
    def _get_character_summary(self) -> str:
        """Get a clean, plain-text summary of confirmed facts with symbolic meaning."""
        summary_parts = []
        
        # Basic info
        if self.character_data.get('name'):
            summary_parts.append(f"Name: {self.character_data['name']}")
        
        if self.character_data.get('age'):
            summary_parts.append(f"Age: {self.character_data['age']}")
        
        if self.character_data.get('gender'):
            summary_parts.append(f"Gender: {self.character_data['gender']}")
        
        if self.character_data.get('race') and self.character_data['race'] != 'Unknown':
            summary_parts.append(f"Race: {self.character_data['race']}")
        
        if self.character_data.get('class') and self.character_data['class'] != 'Unknown':
            summary_parts.append(f"Class: {self.character_data['class']}")
        
        if self.character_data.get('background') and self.character_data['background'] != 'Unknown':
            summary_parts.append(f"Background: {self.character_data['background']}")
        
        if self.character_data.get('combat_experience'):
            summary_parts.append(f"Combat Experience: {self.character_data['combat_experience']}")
        
        if self.character_data.get('personality_traits'):
            summary_parts.append(f"Personality: {', '.join(self.character_data['personality_traits'])}")
        
        if self.character_data.get('combat_style'):
            summary_parts.append(f"Combat Style: {self.character_data['combat_style']}")
        
        if self.character_data.get('traits'):
            summary_parts.append(f"Traits: {', '.join(self.character_data['traits'])}")
        
        if self.character_data.get('motivations'):
            summary_parts.append(f"Motivations: {', '.join(self.character_data['motivations'])}")
        
        if self.character_data.get('emotional_themes'):
            summary_parts.append(f"Themes: {', '.join(self.character_data['emotional_themes'])}")
        
        if self.character_data.get('traumas'):
            summary_parts.append(f"Traumas: {', '.join(self.character_data['traumas'])}")
        
        if self.character_data.get('gear'):
            summary_parts.append(f"Gear: {', '.join(self.character_data['gear'])}")
        
        if self.character_data.get('relational_history'):
            rel_text = []
            for rel_type, rel_desc in self.character_data['relational_history'].items():
                rel_text.append(f"{rel_type.title()}: {rel_desc}")
            summary_parts.append(f"Relationships: {', '.join(rel_text)}")
        
        if self.character_data.get('backstory'):
            summary_parts.append(f"Backstory: {self.character_data['backstory']}")
        
        # Add symbolic meaning summary
        if self.character_data.get('_symbolic_data'):
            symbolic_summary = self._get_symbolic_summary()
            if symbolic_summary:
                summary_parts.append(f"\n🔮 Symbolic Meaning:\n{symbolic_summary}")
        
        if not summary_parts:
            return "No character details have been established yet."
        
        return "\n".join(summary_parts)
    
    def _get_symbolic_summary(self) -> str:
        """Get a summary of symbolic meaning and archetypal themes."""
        if not self.character_data.get('_symbolic_data'):
            return ""
        
        symbolic_parts = []
        
        # Get overall symbolic state
        symbolic_state = self.symbolic_framework.get_symbolic_summary()
        
        # Chaos/Order tension
        chaos_order = symbolic_state["chaos_order_state"]
        symbolic_parts.append(f"Chaos/Order State: {chaos_order}")
        
        # Narrative decay
        if symbolic_state["narrative_decay"] > 0:
            symbolic_parts.append(f"Narrative Decay: {symbolic_state['narrative_decay']:.2f}")
        
        # Archetypal tags
        all_tags = []
        for fact_type, data in self.character_data["_symbolic_data"].items():
            if "archetypal_tags" in data:
                all_tags.extend(data["archetypal_tags"])
        
        if all_tags:
            unique_tags = list(set(all_tags))
            symbolic_parts.append(f"Archetypal Themes: {', '.join(unique_tags)}")
        
        # Symbolic coherence
        if symbolic_state["symbolic_coherence"] < 1.0:
            symbolic_parts.append(f"Symbolic Coherence: {symbolic_state['symbolic_coherence']:.2f}")
        
        return "\n".join(symbolic_parts)
    
    def _get_missing_dnd_fields(self) -> List[str]:
        """Get list of missing required DnD 5E character fields."""
        missing = []
        
        # Core required fields
        if not self.character_data.get('name'):
            missing.append("name")
        if not self.character_data.get('race') or self.character_data['race'] == 'Unknown':
            missing.append("race")
        if not self.character_data.get('class') or self.character_data['class'] == 'Unknown':
            missing.append("class")
        if not self.character_data.get('background') or self.character_data['background'] == 'Unknown':
            missing.append("background")
        
        # Optional but important fields
        if not self.character_data.get('personality_traits') or not self.character_data['personality_traits']:
            missing.append("personality_traits")
        if not self.character_data.get('alignment'):
            missing.append("alignment")
        
        return missing
    
    def start_character_creation(self, description: str, campaign_name: str = "") -> Dict[str, Any]:
        """Start player-led character creation with immediate fact extraction."""
        try:
            logger.info(f"🎲 Starting player-led character creation with description: {description[:100]}...")
            logger.info(f"📝 Campaign name: {campaign_name}")
            
            # Reset character creation state
            preserved_data = {k: v for k, v in self.character_data.items() 
                             if k in ['level', 'ability_scores', 'hit_points', 'armor_class', 
                                     'saving_throws', 'skills', 'feats', 'weapons', 'gear', 'spells']}
            
            self.character_data = {
                **preserved_data,
                "name": None, "race": None, "class": None, "background": None, "alignment": None,
                "personality_traits": [], "age": None, "gender": None, "background_freeform": "", 
                "created_date": None, "motivations": [], "emotional_themes": [], "combat_style": None,
                "combat_experience": None, "traits": [], "traumas": [], "relational_history": {}, 
                "backstory": "", "_symbolic_data": {}
            }
            
            # Reset fact tracking
            for fact_type in self.fact_types:
                self.fact_types[fact_type]["extracted"] = False
                self.fact_types[fact_type]["value"] = None
                self.fact_types[fact_type]["source_text"] = None
                self.fact_types[fact_type]["timestamp"] = None
            
            self.conversation_history = []
            self.in_review_mode = False
            self.is_complete = False
            self.arc_scaffolding_triggered = False
            
            logger.info("🔄 Reset character creation state")
            
            # Extract facts from initial description
            extraction_result = self._extract_and_commit_facts_immediately(description)
            
            # Check if we should transition to guided completion
            if self.guided_completion.should_transition_to_guided(description, extraction_result["committed"], self.character_data):
                self.guided_completion.creative_phase_complete = True
                response = self.guided_completion.get_transition_message()
                
                # Get the first guided question
                next_question = self.guided_completion.get_next_guided_question(self.character_data)
                if next_question:
                    response += f"\n\n{next_question}"
            else:
                # Build response based on what was extracted
                if extraction_result["committed"]:
                    response = "I've captured what you've told me about your character. "
                    if extraction_result["ambiguous"]:
                        response += "I noticed some details that might need clarification. "
                        for fact_type, value in extraction_result["ambiguous"].items():
                            response += f"Did you mean {value} for {fact_type}? "
                    response += "What else would you like to tell me about them?"
                else:
                    response = "I'm listening. Tell me about your character."
            
            # Store conversation
            self.conversation_history = [
                {"role": "user", "content": description},
                {"role": "assistant", "content": response}
            ]
            
            # Log session start
            self._log_session_event('session_start', {'description': description, 'campaign_name': campaign_name})
            
            return {
                "success": True,
                "message": response,
                "is_complete": False,
                "current_step": "conversation",
                "committed_facts": extraction_result["committed"],
                "ambiguous_facts": extraction_result["ambiguous"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting character creation: {e}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Error starting character creation: {str(e)}"
            }

    def continue_conversation(self, user_input: str) -> Dict[str, Any]:
        """Continue player-led character creation with immediate fact extraction."""
        try:
            logger.info(f"📝 Processing user input: '{user_input[:100]}...'")
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Handle status requests
            if any(phrase in user_input.lower() for phrase in [
                "what do we have so far", "what have we got", "current status", 
                "show me what we have", "show me the character", "what's my character",
                "character summary", "what do you know about my character"
            ]):
                summary = self._get_character_summary()
                response = f"Here's what we have so far:\n\n{summary}\n\nWhat would you like to add or change?"
                self.conversation_history.append({"role": "assistant", "content": response})
                return {
                    "success": True,
                    "message": response,
                    "is_complete": False,
                    "current_step": "status_check"
                }

            # Handle completion requests
            if any(phrase in user_input.lower() for phrase in [
                "that's it", "that's everything", "i'm done", "complete", "finish",
                "ready to start", "let's begin", "start the game"
            ]):
                # Check if we need to start stat assignment
                if self.guided_completion.should_start_stat_assignment(self.character_data):
                    response = self.guided_completion.get_stat_assignment_prompt()
                    self.conversation_history.append({"role": "assistant", "content": response})
                    return {
                        "success": True,
                        "message": response,
                        "is_complete": False,
                        "current_step": "stat_assignment"
                    }
                else:
                    # Character is complete
                    self.is_complete = True
                    summary = self.guided_completion.get_completion_summary(self.character_data)
                    response = summary
                self.conversation_history.append({"role": "assistant", "content": response})
                return {
                    "success": True,
                    "message": response,
                    "is_complete": True,
                    "current_step": "complete"
                }
            
            # Extract facts from user input
            extraction_result = self._extract_and_commit_facts_immediately(user_input)
            
            # Handle guided completion phase
            if self.guided_completion.creative_phase_complete:
                # Check if we should start stat assignment
                if self.guided_completion.should_start_stat_assignment(self.character_data):
                    response = self.guided_completion.get_stat_assignment_prompt()
                else:
                    # Get next guided question
                    next_question = self.guided_completion.get_next_guided_question(self.character_data)
                    if next_question:
                        response = f"Got it! {next_question}"
                    else:
                        # All questions answered, ready for stat assignment
                        response = self.guided_completion.get_stat_assignment_prompt()
            else:
                # Check if we should transition to guided completion
                if self.guided_completion.should_transition_to_guided(user_input, extraction_result["committed"], self.character_data):
                    logger.info("🎯 Transitioning to guided character completion")
                    return self.guided_completion.get_next_question(self.character_data)
                
                # Generate natural response using Ollama instead of scripted responses
                response = self._generate_ollama_response(user_input, extraction_result, self.character_data)
                logger.info(f"💬 Ollama response: {response}")
            
            # Check if we should trigger emotional scaffolding
            if self._should_trigger_emotional_scaffolding():
                self.arc_scaffolding_triggered = True
                scaffolding_prompt = self._build_emotional_scaffolding_prompt()
                response += f"\n\n{scaffolding_prompt}"
            
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return {
                "success": True,
                "message": response,
                "is_complete": False,
                "current_step": "conversation",
                "committed_facts": extraction_result.get("committed", {}) if isinstance(extraction_result, dict) else {},
                "ambiguous_facts": extraction_result.get("ambiguous", {}) if isinstance(extraction_result, dict) else {}
            }
            
        except Exception as e:
            logger.error(f"❌ Error continuing conversation: {e}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Error processing input: {str(e)}"
            }
    
    def _log_session_event(self, event_type: str, data: Dict[str, Any]):
        """Log a session event."""
        log_entry = {
            'event': event_type,
            'data': data,
            'timestamp': datetime.datetime.now().isoformat(),
            'session_id': self.session_id
        }
        
        log_file = f"logs/character_creation_sessions/{self.session_id}.jsonl"
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write session log: {e}")
    
    def get_character_data(self) -> Dict[str, Any]:
        """Get the complete character data."""
        return self.character_data.copy()
    
    def get_fact_summary(self) -> str:
        """Get a summary of all committed facts."""
        return self._get_character_summary()
    
    def save_draft(self):
        """Save the current character as a draft."""
        try:
            draft_data = {
                'character_data': self.character_data,
                'fact_types': self.fact_types,
                'session_id': self.session_id,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            draft_id = str(uuid.uuid4())
            draft_file = f"character_saves/draft_{draft_id}.json"
            
            os.makedirs("character_saves", exist_ok=True)
            with open(draft_file, 'w') as f:
                json.dump(draft_data, f, indent=2)
            
            self.draft_id = draft_id
            self.draft_saved = True
            
            logger.info(f"✅ Draft saved with ID: {draft_id}")
            return draft_id
            
        except Exception as e:
            logger.error(f"❌ Error saving draft: {e}")
            raise
    
    def undo_last_fact(self) -> Optional[tuple]:
        """Undo the last committed character fact."""
        if not self.fact_history:
            return None
        
        # Get the last fact from history
        last_fact = self.fact_history.pop()
        fact_type, old_value, new_value = last_fact
        
        # Restore the old value
        if old_value is None:
            # Remove the fact
            if fact_type in self.character_data:
                del self.character_data[fact_type]
        if fact_type in self.fact_types:
            self.fact_types[fact_type]["extracted"] = False
            self.fact_types[fact_type]["value"] = None
        else:
            # Restore the old value
            self.character_data[fact_type] = old_value
        if fact_type in self.fact_types:
            self.fact_types[fact_type]["value"] = old_value
        
        logger.info(f"↩️ Undid {fact_type}: {new_value} → {old_value}")
        return (fact_type, new_value, old_value)

    def _generate_ollama_response(self, user_input: str, extraction_result: Dict[str, Any], character_data: Dict[str, Any]) -> str:
        """
        Generate a natural response using Ollama instead of scripted responses.
        This creates a more human-like conversation flow.
        """
        try:
            # Build context for Ollama
            character_summary = self._get_character_summary()
            extracted_facts = extraction_result.get("committed", {}) if isinstance(extraction_result, dict) else {}
            
            # Create a natural conversation prompt
            prompt = f"""You are a helpful D&D character creation assistant. The player is creating their character and has just told you something new.

Current character information:
{character_summary}

Player's latest input: "{user_input}"

If facts were extracted from their input, here they are:
{extracted_facts}

Respond naturally as a helpful assistant. Acknowledge what you learned about their character, ask thoughtful questions, or encourage them to tell you more. Be conversational and engaging, not robotic. Keep your response under 2-3 sentences.

Response:"""

            # Get response from Ollama
            from ollama_llm_service import chat_completion
            messages = [{"role": "user", "content": prompt}]
            response = chat_completion(messages)
            
            if response and response.strip():
                return response.strip()
            else:
                return "I'm listening. Tell me more about your character."
                
        except Exception as e:
            logger.error(f"❌ Error generating Ollama response: {e}")
            return "I'm listening. Tell me more about your character."

class SimpleNarrativeBridge:
    """Narrative bridge for SoloHeart with memory tracking."""
    
    def __init__(self):
        self.ensure_directories()
        self.current_campaign_id = None
        self.conversation_history = {}  # Track conversation history per campaign
    
    def ensure_directories(self):
        """Ensure necessary directories exist."""
        os.makedirs("campaign_saves", exist_ok=True)
        os.makedirs("character_saves", exist_ok=True)
    
    def initialize_campaign(self, character_data: Dict[str, Any], campaign_name: str = None) -> Optional[Dict[str, Any]]:
        """Initialize a new campaign with character data."""
        try:
            campaign_id = str(uuid.uuid4())[:8]
            campaign_name = campaign_name or f"Campaign {campaign_id}"
            
            # Initialize conversation history for this campaign
            self.conversation_history[campaign_id] = []
            
            # Create campaign data
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
            logger.info(f"✅ Initialized campaign: {campaign_id}")
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
            logger.info(f"✅ Loaded campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading campaign: {e}")
            return False
    
    def process_player_input(self, player_input: str, campaign_id: str) -> str:
        """Process player input and return SoloHeart Guide response with memory tracking."""
        try:
            # Get campaign context
            campaign_context = self.get_campaign_data(campaign_id)
            if not campaign_context:
                return "I'm sorry, but I can't find your campaign data. Please try starting a new campaign."
            
            # Add player input to conversation history
            if campaign_id not in self.conversation_history:
                self.conversation_history[campaign_id] = []
            
            self.conversation_history[campaign_id].append({
                "role": "user",
                "content": player_input,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # Build context from conversation history
            recent_history = self.conversation_history[campaign_id][-10:]  # Last 10 exchanges
            context_messages = []
            
            character = campaign_context.get('active_character', {})
            name = character.get('name', 'Adventurer')
            race = character.get('race', 'Human')
            char_class = character.get('class', 'Fighter')
            
            # Create system prompt with character info
            system_prompt = f"""You are a SoloHeart Guide, an AI companion for immersive solo narrative adventures. 

The player is {name}, a {race} {char_class}. 

Your role is to:
1. Create immersive, atmospheric scenes
2. Respond to player actions and choices
3. Maintain narrative continuity and remember past events
4. Provide meaningful consequences for player decisions
5. Ask clarifying questions when needed

IMPORTANT: Remember what has happened before and reference past events when relevant.

Write in third person, present tense. Be descriptive and engaging. Keep responses concise but vivid."""

            context_messages.append({"role": "system", "content": system_prompt})
            
            # Add recent conversation history for context
            for msg in recent_history:
                context_messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Use the LLM service
            response = chat_completion(context_messages, temperature=0.8, max_tokens=300)
            
            # Add AI response to conversation history
            self.conversation_history[campaign_id].append({
                "role": "assistant",
                "content": response.strip(),
                "timestamp": datetime.datetime.now().isoformat()
            })
            
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
            
            logger.info(f"✅ Saved campaign: {campaign_id}")
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
    """Character creation interface."""
    return render_template('character_creation.html')

@app.route('/test-character-sheet')
def test_character_sheet():
    """Test page for character sheet updates."""
    return send_file('test_character_sheet.html')

@app.route('/api/character/create/start', methods=['POST'])
def start_character_creation_api():
    """Start the enhanced player-led character creation process."""
    try:
        logger.info("🚀 Starting enhanced character creation...")
        data = request.get_json()
        description = data.get('description', '')
        campaign_name = data.get('campaign_name', '')
        logger.info(f"📝 Raw user input: '{description}'")
        logger.info(f"🎯 Campaign: {campaign_name}")
        if not description:
            logger.warning("❌ No description provided")
            return jsonify({'success': False, 'message': 'Character description is required'})
        temp_bridge = SimpleNarrativeBridge()
        game.character_generator.narrative_bridge = temp_bridge
        result = game.character_generator.start_character_creation(description, campaign_name)
        session['character_creation_active'] = True
        session['campaign_name'] = campaign_name
        logger.info("💾 Session data stored successfully")
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'is_complete': result.get('is_complete', False),
            'current_step': result.get('current_step', 'conversation'),
            'committed_facts': result.get('committed_facts', {}),
            'ambiguous_facts': result.get('ambiguous_facts', {}),
            'character_data': game.character_generator.get_character_data()
        })
    except Exception as e:
        logger.error(f"❌ Error starting character creation: {e}")
        import traceback
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'Error starting character creation: {str(e)}'})

@app.route('/api/character/create/continue', methods=['POST'])
def continue_character_creation_api():
    """Continue the enhanced player-led character creation conversation."""
    try:
        logger.info("🔄 Continuing enhanced character creation...")
        data = request.get_json()
        user_input = data.get('user_input', '')
        logger.info(f"📝 Raw user input: '{user_input}'")
        if not user_input:
            logger.warning("❌ No user input provided")
            return jsonify({'success': False, 'message': 'User input is required'})
        result = game.character_generator.continue_conversation(user_input)
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'is_complete': result.get('is_complete', False),
            'current_step': result.get('current_step', 'conversation'),
            'committed_facts': result.get('committed_facts', {}),
            'ambiguous_facts': result.get('ambiguous_facts', {}),
            'character_data': game.character_generator.get_character_data()
        })
    except Exception as e:
        logger.error(f"Error in continue_character_creation: {e}")
        return jsonify({'success': False, 'message': 'Error continuing character creation.'})

@app.route('/api/character/create/confirm', methods=['POST'])
def confirm_vibe_code_facts():
    """Handle confirmation of ambiguous facts (legacy endpoint for compatibility)."""
    try:
        data = request.get_json()
        corrections = data.get('corrections', {})
        
        # Apply any corrections directly to character_data
        for fact_type, value in corrections.items():
            if value is None:
                # Remove fact
                if fact_type in game.character_generator.character_data:
                    del game.character_generator.character_data[fact_type]
                if fact_type in game.character_generator.fact_types:
                    game.character_generator.fact_types[fact_type]['extracted'] = False
                    game.character_generator.fact_types[fact_type]['value'] = None
                else:
                    # Update fact
                    game.character_generator.character_data[fact_type] = value
                    if fact_type in game.character_generator.fact_types:
                        game.character_generator.fact_types[fact_type]['extracted'] = True
                        game.character_generator.fact_types[fact_type]['value'] = value
        
        # Check if character is complete
        missing = game.character_generator._get_missing_dnd_fields()
        if missing:
            return jsonify({
                'success': True, 
                'message': f"Thanks! I still need: {', '.join(missing)}. What else would you like to tell me?",
                'fact_types': game.character_generator.fact_types,
                'character_data': game.character_generator.get_character_data()
            })
        else:
            summary = game.character_generator.get_fact_summary()
            return jsonify({
                'success': True, 
                'message': f"{summary}\n\nAre you ready to start your adventure with this character?",
                'fact_types': game.character_generator.fact_types,
                'character_data': game.character_generator.get_character_data()
            })
    except Exception as e:
        logger.error(f"Error confirming facts: {e}")
        return jsonify({'success': False, 'message': 'Error confirming facts.'})

@app.route('/api/character/create/summary', methods=['GET'])
def get_character_summary():
    """Return a summary of all committed facts."""
    summary = game.character_generator._get_character_summary()
    return jsonify({'success': True, 'summary': summary})

@app.route('/api/character/create/symbolic', methods=['GET'])
def get_symbolic_meaning():
    """Return symbolic meaning and archetypal data."""
    if not game.character_generator.character_data.get('_symbolic_data'):
        return jsonify({'success': True, 'symbolic_data': {}})
    
    symbolic_state = game.character_generator.symbolic_framework.get_symbolic_summary()
    return jsonify({
        'success': True, 
        'symbolic_data': {
            'chaos_order_tension': symbolic_state['chaos_order_tension'],
            'chaos_order_state': symbolic_state['chaos_order_state'],
            'narrative_decay': symbolic_state['narrative_decay'],
            'symbolic_coherence': symbolic_state['symbolic_coherence'],
            'narrative_response': symbolic_state['narrative_response'],
            'archetypal_data': game.character_generator.character_data['_symbolic_data']
        }
    })

@app.route('/api/character/create/save-draft', methods=['POST'])
def save_character_draft():
    """Save the current character as a draft."""
    try:
        game.character_generator.save_draft()
        return jsonify({'success': True, 'message': 'Draft saved.'})
    except Exception as e:
        logger.error(f"Error saving draft: {e}")
        return jsonify({'success': False, 'message': 'Error saving draft.'})

@app.route('/api/character/create/complete', methods=['POST'])
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
        
        # Initialize campaign with Narrative Engine
        logger.info("🚀 Initializing campaign with Narrative Engine...")
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
                'redirect': '/game',
                'campaign_id': campaign_data['id'],
                'opening_scene': campaign_data.get('opening_scene', '')
            })
        else:
            logger.error("❌ Failed to initialize campaign")
            return jsonify({'success': False, 'message': 'Failed to start campaign'})
    
    except Exception as e:
        logger.error(f"❌ Error completing vibe code creation: {e}")
        import traceback
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'Error completing character creation'})

@app.route('/api/campaign/start', methods=['POST'])
def start_campaign():
    """Start a new campaign with the current character."""
    try:
        logger.info("🚀 Starting new campaign...")
        
        # Get character data
        character_data = game.character_generator.get_character_data()
        campaign_name = session.get('campaign_name', 'New Campaign')
        
        if not character_data:
            return jsonify({'success': False, 'message': 'No character data available'})
        
        # Initialize campaign with Narrative Engine
        campaign_data = game.narrative_bridge.initialize_campaign(character_data, campaign_name)
        
        if campaign_data:
            # Store campaign ID in session
            session['campaign_id'] = campaign_data['id']
            session.pop('character_creation_active', None)
            
            logger.info(f"✅ Campaign started: {campaign_data['id']}")
            return jsonify({
                'success': True,
                'message': 'Campaign started successfully!',
                'redirect': '/game',
                'campaign_id': campaign_data['id'],
                'opening_scene': campaign_data.get('opening_scene', '')
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to start campaign'})
    
    except Exception as e:
        logger.error(f"❌ Error starting campaign: {e}")
        return jsonify({'success': False, 'message': 'Error starting campaign'})

@app.route('/api/character/create/undo', methods=['POST'])
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

@app.route('/api/character/create/edit', methods=['POST'])
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

@app.route('/api/character/create/finalize', methods=['POST'])
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
            'personality_traits': data.get('personality_traits', ['A brave adventurer']),
            
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
        player_input = data.get('input') or data.get('action', '')  # Accept both 'input' and 'action'
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
            'dm_response': guide_response  # Changed from 'response' to 'dm_response' to match frontend
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check Ollama connection
        ollama_healthy = False
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                ollama_healthy = 'llama3' in model_names or 'llama3:latest' in model_names
        except:
            pass
        
        # Check if game instance is available
        game_healthy = hasattr(game, 'character_generator') and game.character_generator is not None
        
        status = 'healthy' if ollama_healthy and game_healthy else 'degraded'
        
        return jsonify({
            'status': status,
            'timestamp': datetime.datetime.now().isoformat(),
            'ollama_healthy': ollama_healthy,
            'game_healthy': game_healthy,
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }), 500

@app.route('/api/character/create/assign-stats', methods=['POST'])
def assign_character_stats():
    """Handle ability score assignment."""
    try:
        data = request.get_json()
        assignment_type = data.get('type', 'auto')  # 'auto' or 'manual'
        
        if assignment_type == 'auto':
            # Auto-assign stats
            stats = game.character_generator.guided_completion.assign_stats_automatically(
                game.character_generator.character_data
            )
            game.character_generator.character_data['ability_scores'] = stats
            game.character_generator.guided_completion.stat_assignment_mode = StatAssignmentMode.AUTO
            
            response = f"Perfect! I've assigned your ability scores:\n\n"
            response += f"Strength: {stats['strength']}\n"
            response += f"Dexterity: {stats['dexterity']}\n"
            response += f"Constitution: {stats['constitution']}\n"
            response += f"Intelligence: {stats['intelligence']}\n"
            response += f"Wisdom: {stats['wisdom']}\n"
            response += f"Charisma: {stats['charisma']}\n\n"
            response += "Your character is ready! Would you like to start your adventure?"
            
        elif assignment_type == 'manual':
            # Manual stat assignment
            stats = data.get('stats', {})
            is_valid, error_msg = game.character_generator.guided_completion.validate_manual_stats(stats)
            
            if is_valid:
                game.character_generator.character_data['ability_scores'] = stats
                game.character_generator.guided_completion.stat_assignment_mode = StatAssignmentMode.MANUAL
                
                response = f"Great! Your ability scores are set:\n\n"
                response += f"Strength: {stats['strength']}\n"
                response += f"Dexterity: {stats['dexterity']}\n"
                response += f"Constitution: {stats['constitution']}\n"
                response += f"Intelligence: {stats['intelligence']}\n"
                response += f"Wisdom: {stats['wisdom']}\n"
                response += f"Charisma: {stats['charisma']}\n\n"
                response += "Your character is ready! Would you like to start your adventure?"
            else:
                response = f"Those scores don't quite work: {error_msg}. Please try again with valid ability scores."
        
        else:
            response = "Please choose 'auto' or 'manual' for stat assignment."
        
        game.character_generator.conversation_history.append({"role": "assistant", "content": response})
        
        return jsonify({
            'success': True,
            'message': response,
            'is_complete': assignment_type in ['auto', 'manual'] and 'error' not in response.lower(),
            'current_step': 'complete' if 'ready' in response else 'stat_assignment'
        })
        
    except Exception as e:
        logger.error(f"Error assigning stats: {e}")
        return jsonify({'success': False, 'message': 'Error assigning ability scores.'})

@app.route('/api/character/create/load-draft', methods=['POST'])
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
    app.run(host='0.0.0.0', port=5001, debug=False)
