from dotenv import load_dotenv
load_dotenv()
"""
The Narrative Engine D&D Demo - Unified Interface
A demonstration application showcasing TNE's symbolic processing capabilities through interactive character creation and narrative development workflows.
"""

import os
import json
import logging
import uuid
import datetime
import re
import random
import glob
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from llm_interface.provider_factory import get_llm_provider
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
from utils.guided_character_completion import GuidedCharacterCompletion, CompletionPhase, StatAssignmentMode
from utils.srd_requirements import SRDRequirements, FieldPriority
from utils.ability_score_system import AbilityScoreSystem, AbilityScoreMethod
from utils.racial_modifiers import racial_modifiers
from srd_compliance_checker import srd_checker
# Enable TNE integration for symbolic processing and memory management
from narrative_engine_integration import TNEDemoEngine
from routing import tne_connector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Gemma 3 LLM service - no fallbacks, must be available

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
    
    # Check LLM provider connection
    try:
        provider = get_llm_provider()
        logger.info(f"✅ LLM provider initialized: {provider.provider_name.title()}")
    except Exception as e:
        logger.error(f"❌ LLM provider connection failed: {e}")
        logger.error("💡 Please check your LLM provider configuration in .env")
        logger.error("💡 For Google Gemma 3: Ensure the API server is running at http://localhost:1234/v1")
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

class TNECharacterGenerator:
    """TNE demo character generator for symbolic processing visualization and memory flow display."""
    
    def __init__(self, playtest_mode: bool = None):
        self.conversation_history = []
        self.character_data = {
            # Core Identity (CRITICAL)
            "name": None,
            "race": None,
            "class": None,
            "level": 1,
            
            # Ability Scores (CRITICAL) - Now using proper structure
            "ability_scores": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            },
            "ability_modifiers": {
                "strength": 0,
                "dexterity": 0,
                "constitution": 0,
                "intelligence": 0,
                "wisdom": 0,
                "charisma": 0
            },
            
            # Combat Stats (CRITICAL)
            "hit_points": 10,
            "armor_class": 10,
            "initiative": 0,
            "speed": 30,
            
            # Background & Identity (HIGH)
            "background": None,
            "alignment": None,
            "age": None,
            "gender": None,
            
            # Proficiencies (HIGH)
            "proficiencies": [],
            "languages": [],
            
            # Equipment (HIGH)
            "equipment": [],
            "weapons": [],
            "armor": None,
            
            # Personality & Story (MEDIUM)
            "personality_traits": [],
            "ideals": [],
            "bonds": [],
            "flaws": [],
            "motivations": [],
            "backstory": "",
            
            # Combat & Abilities (MEDIUM)
            "combat_style": None,
            "spells": [],
            "features": [],
            
            # Flavor & Details (LOW)
            "appearance": None,
            "emotional_themes": [],
            "traumas": [],
            "relational_history": {},
            "traits": [],
            
            # Legacy fields for backward compatibility
            "saving_throws": [],
            "skills": [],
            "feats": [],
            "gear": [],
            "combat_experience": None,
            "background_freeform": "",
            "created_date": None,
            "_symbolic_data": {}  # Store archetypal tags and symbolic meaning
        }
        
        # Symbolic processing now delegated to TNE
        self.is_complete = False
        self.character_finalized = False
        self.in_review_mode = False
        self.narrative_bridge = None  # Will be set in start_character_creation
        self.fact_history = []
        
        # Initialize guided completion system
        self.guided_completion = GuidedCharacterCompletion()
        
        # Initialize SRD requirements system
        self.srd_requirements = SRDRequirements()
        
        # Initialize ability score system
        self.ability_score_system = AbilityScoreSystem()
        
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
            
            # Create a concise prompt for the LLM
            prompt = f"""Extract DnD 5E character facts from: "{text}"

Return JSON with: name, race, class, background, age, gender, alignment, personality_traits, motivations, emotional_themes, combat_style, traits, traumas, relational_history, gear, backstory.

Rules: Only extract explicit facts. Use null for missing info. Use arrays for lists. Use objects for relationships.

{current_facts_str}

JSON:"""

            # Call LLM using the correct format with shorter timeout
            from llm_interface.provider_factory import chat_completion
            messages = [{"role": "user", "content": prompt}]
            
            # Set shorter timeout for faster responses
            import os
            original_timeout = os.environ.get('LLM_TIMEOUT_SECONDS', '180')
            os.environ['LLM_TIMEOUT_SECONDS'] = '30'  # 30 second timeout
            
            try:
                response = chat_completion(messages)
            finally:
                # Restore original timeout
                os.environ['LLM_TIMEOUT_SECONDS'] = original_timeout
            
            if not response or not response.strip():
                logger.error("❌ LLM returned empty response")
                return {}
            
            # Parse the JSON response
            import re
            
            # Try to extract JSON from the response (in case LLM adds extra text)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response
            
            # Minimal JSON cleanup - only remove newlines and comments
            json_str = json_str.replace('\n', ' ').replace('\r', ' ')
            json_str = re.sub(r'//.*?(?=\n|$)', '', json_str)  # Remove comments
            
            try:
                facts = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"❌ LLM extraction failed: {e}")
                logger.error(f"LLM response was: {response}")
                logger.error(f"Cleaned JSON was: {json_str}")
                return {}
            
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
            return {}
    
    def _extract_and_commit_facts_immediately(self, text: str) -> Dict[str, Any]:
        """
        Extract facts from text using LLM as primary method, with pattern-matching fallback.
        Returns dict of newly committed facts and any ambiguous ones requiring confirmation.
        """
        logger.info(f"🔍 Extracting facts from: '{text[:100]}...'")
        
        newly_committed = {}
        ambiguous_facts = {}
        
        # Try LLM extraction first (with timeout)
        try:
            llm_facts = self._extract_facts_with_llm(text)
        except Exception as e:
            logger.warning(f"⚠️ LLM extraction failed, skipping to pattern matching: {e}")
            llm_facts = {}
        
        # Post-process: Only commit age if explicitly present in text
        if llm_facts and 'age' in llm_facts:
            logger.debug(f">>> DEBUG: calling .lower() on text in age_pattern (line 336), value={text!r}, type={type(text)}")
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
        logger.debug(f">>> DEBUG: calling .lower() on text in age_match (line 399), value={text!r}, type={type(text)}")
        age_match = re.search(r'(\d+)\s*(?:year|yr)s?\s*old', text.lower())
        if age_match:
            extracted_facts['age'] = int(age_match.group(1))
            
        # Extract gender using simple patterns
        logger.debug(f">>> DEBUG: calling .lower() on text in gender detection (line 404), value={text!r}, type={type(text)}")
        if re.search(r'\b(he|his|him)\b', text.lower()):
            extracted_facts['gender'] = 'Male'
        else:
            logger.debug(f">>> DEBUG: calling .lower() on text in gender detection (line 406), value={text!r}, type={type(text)}")
            if re.search(r'\b(she|her|hers)\b', text.lower()):
                extracted_facts['gender'] = 'Female'
            else:
                logger.debug(f">>> DEBUG: calling .lower() on text in gender detection (line 408), value={text!r}, type={type(text)}")
                if re.search(r'\b(they|their|them)\b', text.lower()):
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
            logger.debug(f">>> DEBUG: calling .lower() on themes+motivations in theme_text (line 504), value={themes+motivations!r}, type={type(themes+motivations)}")
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
        """
        Get symbolic summary from TNE for the given character.
        # Replaced local symbolic logic with TNE integration
        """
        character_id = self.character_data.get('id') or self.character_data.get('name', 'unknown')
        symbolic_state = tne_connector.get_symbolic_summary(character_id)
        # Format output for UI
        symbolic_parts = []
        chaos_order = symbolic_state.get("chaos_order_state", "Unknown")
        symbolic_parts.append(f"Chaos/Order State: {chaos_order}")
        if symbolic_state.get("narrative_decay", 0) > 0:
            symbolic_parts.append(f"Narrative Decay: {symbolic_state['narrative_decay']:.2f}")
        tags = symbolic_state.get("archetypal_tags", [])
        if tags:
            symbolic_parts.append(f"Archetypal Themes: {', '.join(tags)})")
        if symbolic_state.get("symbolic_coherence", 1.0) < 1.0:
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
        """
        Start player-led character creation with immediate fact extraction.
        
        CRITICAL REGRESSION WARNING:
        - Do not reset character data unless this is a truly new session
        - This fix prevents data loss during character creation
        - See test_character_persistence.py for validation tests
        - Session detection logic: if not (name or race), then reset; otherwise preserve
        """
        try:
            campaign_context = None  # Always define campaign_context for all branches
            logger.info(f"🎲 Starting player-led character creation with description: {description[:100]}...")
            logger.info(f"📝 Campaign name: {campaign_name}")
            
            # Only reset character creation state if this is a new session
            if not self.character_data.get('name') and not self.character_data.get('race'):
                # This is a new session - reset everything
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
            else:
                # This is continuing an existing session - preserve character data
                logger.info("🔄 Continuing existing character creation session")
            
            # Extract facts from initial description
            extraction_result = self._extract_and_commit_facts_immediately(description)
            
            # Initialize TNE Demo Engine
            self.narrative_bridge = TNEDemoEngine(campaign_id=campaign_name or "default")
            
            # Initialize campaign_context to None first
            campaign_context = None

            # Get campaign context for Ollama (must be defined before use)
            try:
                campaign_context = self.narrative_bridge.get_memory_context_for_ollama(
                    user_id='player'
                )
            except Exception as e:
                logger.warning(f"⚠️ Could not get campaign context: {e}")
                campaign_context = None

            # Record character creation in Narrative Engine
            try:
                self.narrative_bridge.record_character_creation(self.character_data)
            except Exception as e:
                logger.error(f"❌ Error recording character creation: {e}")
                # Continue anyway - don't fail the entire process
            
            # Generate natural response using Ollama with context
            if extraction_result["committed"]:
                # Use Ollama to generate a natural response about what was captured
                response = self._generate_natural_response_with_context(
                    description, 
                    extraction_result, 
                    "Character creation started", 
                    campaign_context
                )
            else:
                # Simple acknowledgment for empty input
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
            
            # Extract facts from user input first
            extraction_result = self._extract_and_commit_facts_immediately(user_input)
            
            # Record player action in Narrative Engine with extracted facts
            if hasattr(self, 'narrative_bridge') and self.narrative_bridge:
                try:
                    # Record player action in Narrative Engine
                    self.narrative_bridge.record_player_action(
                        user_input, 
                        {
                            "character_name": self.character_data.get('name'),
                            "location": "character_creation",
                            "emotional_impact": extraction_result.get("committed", {}),
                            "consequences": [],
                            "unresolved": True
                        }
                    )
                    
                    # Record character facts if any were extracted
                    if extraction_result.get("committed"):
                        self.narrative_bridge.record_character_facts(
                            extraction_result["committed"], 
                            self.character_data.get('name', 'Unknown')
                        )
                    
                    # Get campaign context for Ollama
                    campaign_context = self.narrative_bridge.get_memory_context_for_ollama(
                        user_id='player'
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Narrative Engine error: {e}")
                    campaign_context = None
            else:
                campaign_context = None
            
            # Check if character sheet is incomplete using SRD 5.2 compliance checker
            completeness_result = srd_checker.check_character_completeness(self.character_data)
            srd_compliance_result = srd_checker.validate_srd_compliance(self.character_data)
            
            if not completeness_result['is_complete']:
                # Use intelligent priority engine to determine what to ask for next
                priority_fields = srd_checker.get_next_priority_fields(self.character_data, max_fields=2)
                steering_prompt = srd_checker.generate_steering_prompt(self.character_data)
                
                logger.info(f"📋 Character sheet incomplete: {completeness_result['completion_percentage']:.1f}% complete")
                logger.info(f"🎯 Priority fields: {[f.field for f in priority_fields]}")
                logger.info(f"🎯 Steering prompt: {steering_prompt}")
                
                # Use steering prompt to guide the AI response
                response = self._generate_natural_response_with_context(user_input, extraction_result, steering_prompt, campaign_context)
                logger.info(f"💬 Priority-guided response: {response}")
            else:
                # Character sheet is complete, continue with natural conversation
                response = self._generate_llm_response(user_input, extraction_result, self.character_data, campaign_context)
                logger.info(f"💬 Natural LLM response: {response}")
            
            # Log SRD compliance status
            if not srd_compliance_result['is_srd_compliant']:
                logger.warning(f"⚠️ SRD compliance issues: {srd_compliance_result['compliance_issues']}")
            else:
                logger.info("✅ Character is SRD 5.2 compliant")
            
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

    def _generate_llm_response(self, user_input: str, extraction_result: Dict[str, Any], character_data: Dict[str, Any], campaign_context: Dict[str, Any] = None) -> str:
        """
        Generate a natural response using LLM with Narrative Engine context.
        This creates a more human-like conversation flow informed by campaign memory.
        """
        try:
            # Build context for LLM
            character_summary = self._get_character_summary()
            extracted_facts = extraction_result.get("committed", {}) if isinstance(extraction_result, dict) else {}
            
            # Add enhanced Narrative Engine context if available
            context_info = ""
            if campaign_context:
                context_info = f"\n{campaign_context}"
            
            # Create a natural conversation prompt with memory context
            prompt = f"""You are a helpful D&D character creation assistant with access to campaign memory and context. The player is creating their character and has just told you something new.

Current character information:
{character_summary}

Player's latest input: "{user_input}"

If facts were extracted from their input, here they are:
{extracted_facts}
{context_info}

Respond naturally as a helpful assistant. Acknowledge what you learned about their character, ask thoughtful questions, or encourage them to tell you more. Be conversational and engaging, not robotic. Keep your response under 2-3 sentences.

Response:"""

            # Get response from LLM
            provider = get_llm_provider()
            response = provider.chat_completion(prompt)
            
            if response and response.strip():
                return response.strip()
            else:
                return "I'm listening. Tell me more about your character."
                
        except Exception as e:
            logger.error(f"❌ Error generating LLM response: {e}")
            return "I'm listening. Tell me more about your character."

    def _generate_natural_response_with_context(self, user_input: str, extraction_result: Dict[str, Any], additional_context: str, campaign_context: Dict[str, Any] = None) -> str:
        """
        Generate a natural conversational response using LLM with additional context about what's missing.
        """
        try:
            # Build context about what we learned
            committed_facts = extraction_result.get("committed", {}) if isinstance(extraction_result, dict) else {}
            character_summary = self._get_character_summary()
            
            # Track what information we already have to avoid repetitive questions
            existing_info = []
            if self.character_data.get('name'):
                existing_info.append("name")
            if self.character_data.get('age'):
                existing_info.append("age")
            if self.character_data.get('gender'):
                existing_info.append("gender")
            if self.character_data.get('race'):
                existing_info.append("race")
            if self.character_data.get('class'):
                existing_info.append("class")
            if self.character_data.get('background'):
                existing_info.append("background")
            if self.character_data.get('personality_traits'):
                existing_info.append("personality")
            if self.character_data.get('combat_style'):
                existing_info.append("combat style")
            if self.character_data.get('backstory'):
                existing_info.append("backstory")
            
            if committed_facts:
                fact_summary = []
                for fact_type, value in committed_facts.items():
                    if value:
                        fact_summary.append(f"{fact_type}: {value}")
                
                context = f"I learned: {', '.join(fact_summary)}. "
            else:
                context = ""
            
            # Add campaign context if available
            context_info = ""
            if campaign_context:
                context_info = f"\n{campaign_context}"
            
            # Create a conversational prompt with completion guidance
            prompt = f"""You are a helpful game master helping a player create their D&D character. 
The player just said: "{user_input}"

Current character information:
{character_summary}

Information already provided: {', '.join(existing_info) if existing_info else 'none'}

{context}{additional_context}{context_info}

Respond naturally and conversationally. The player is creating their character and you should help them develop their story. 

IMPORTANT: Don't ask about information they've already told you. If they've already described their appearance, don't ask about it again. If they've already mentioned their background, don't ask about it again. Focus on what's missing or help them develop what they've already shared.

If there's missing information, guide them conversationally to share more about their character. Don't be pushy or scripted - make it feel like natural conversation. Be encouraging and help them develop their character's story.

Keep your response under 2-3 sentences and focus on one aspect at a time.

STEERING GUIDANCE: {additional_context}"""
            
            # Get response from LLM
            provider = get_llm_provider()
            response = provider.chat_completion(prompt)
            
            if response and response.strip():
                logger.info(f"💬 Guided natural response: {response}")
                return response.strip()
            else:
                return "Tell me more about your character."
            
        except Exception as e:
            logger.error(f"❌ Error generating guided natural response: {e}")
            return "Tell me more about your character."

class TNEDemoBridge:
    """Narrative bridge for TNE Demo with memory tracking."""
    
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
            
            # Load campaign data and restore conversation history
            with open(campaign_file, 'r') as f:
                campaign_data = json.load(f)
            
            # Restore conversation history if it exists
            if "conversation_history" in campaign_data:
                self.conversation_history[campaign_id] = campaign_data["conversation_history"]
            else:
                self.conversation_history[campaign_id] = []
            
            self.current_campaign_id = campaign_id
            logger.info(f"✅ Loaded campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading campaign: {e}")
            return False
    
    def generate_campaign_recap(self, campaign_id: str) -> str:
        """Generate a recap of the campaign's current state."""
        try:
            campaign_data = self.get_campaign_data(campaign_id)
            if not campaign_data:
                return "Welcome back! Your adventure awaits."
            
            character = campaign_data.get('active_character', {})
            name = character.get('name', 'Adventurer')
            race = character.get('race', 'Human')
            char_class = character.get('class', 'Fighter')
            
            # Get conversation history
            history = self.conversation_history.get(campaign_id, [])
            
            if len(history) <= 2:
                # Very new campaign
                return f"Welcome back, {name}! You are a {race} {char_class} just beginning your adventure. What would you like to do?"
            
            # Generate recap from recent history
            recent_messages = history[-6:]  # Last 6 messages (3 exchanges)
            
            # Build context for recap generation
            context_messages = [
                {
                    "role": "system",
                    "content": f"""You are a TNE Demo Guide providing a brief campaign recap. 

The player is {name}, a {race} {char_class}.

Your task is to provide a concise, engaging recap of the recent adventure events based on the conversation history. Focus on:
1. The most recent significant events or discoveries
2. Current situation or location
3. Any important NPCs, items, or objectives mentioned
4. What the player was last doing

Keep it brief (2-3 sentences) and engaging. Don't make up details that aren't in the history."""
                }
            ]
            
            # Add recent conversation history
            for msg in recent_messages:
                context_messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add instruction for recap
            context_messages.append({
                "role": "user", 
                "content": "Please provide a brief recap of where we left off in this adventure."
            })
            
            # Generate recap using LLM
            try:
                recap = provider.chat_completion(context_messages, temperature=0.7, max_tokens=150)
                logger.info(f"✅ Generated recap for campaign {campaign_id}: {recap[:100]}...")
                return recap.strip()
            except Exception as llm_error:
                logger.error(f"❌ LLM error generating recap: {llm_error}")
                # Fallback to simple recap
                return f"Welcome back, {name}! You are a {race} {char_class} continuing your adventure. What would you like to do?"
            
        except Exception as e:
            logger.error(f"❌ Error generating campaign recap: {e}")
            return f"Welcome back, {name}! Your adventure continues..."
    
    def process_player_input(self, player_input: str, campaign_id: str) -> str:
        """Process player input and return TNE Demo Guide response with enhanced prompt system."""
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
            
            # Build enhanced prompt with structured sections
            prompt_sections = self._build_enhanced_prompt(player_input, campaign_id, campaign_context)
            
            # Create context messages with structured prompt
            context_messages = [
                {"role": "system", "content": prompt_sections['system']},
                {"role": "user", "content": prompt_sections['context']},
                {"role": "user", "content": prompt_sections['memory']},
                {"role": "user", "content": prompt_sections['stats']},
                {"role": "user", "content": prompt_sections['input']}
            ]
            
            # Add recent conversation history (last 3-5 turns)
            recent_history = self.conversation_history[campaign_id][-6:]  # Last 6 exchanges (3 turns)
            for msg in recent_history:
                if msg["role"] in ["user", "assistant"]:
                    context_messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Use the LLM service
            provider = get_llm_provider()
            response = provider.chat_completion(context_messages, temperature=0.8, max_tokens=400)
            
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
    
    def _build_enhanced_prompt(self, player_input: str, campaign_id: str, campaign_context: Dict[str, Any]) -> Dict[str, str]:
        """Build structured prompt with context, memory, stats, symbolism, goals, and input sections."""
        
        character = campaign_context.get('active_character', {})
        name = character.get('name', 'Adventurer')
        race = character.get('race', 'Human')
        char_class = character.get('class', 'Fighter')
        level = character.get('level', 1)
        
        # System prompt
        system_prompt = f"""You are a TNE Demo Guide, an AI companion for immersive narrative demonstrations.

The player is {name}, a {race} {char_class} (Level {level}).

Your role is to:
1. Respond to player actions and choices
2. Reference ONLY the actual conversation history and memory context provided
3. Don't make up events that aren't in the history
4. Ask clarifying questions when needed
5. NEVER invent NPCs, locations, or events that haven't been discussed

IMPORTANT: Only reference events that have actually been discussed in the conversation history. If the player asks about something that hasn't been established, say you don't know about that yet.

Write in third person, present tense. Be descriptive and engaging. Keep responses concise but vivid."""
        
        # Context section
        context_section = f"""[Context]
Campaign: {campaign_context.get('name', 'Adventure')}
Character: {name} ({race} {char_class}, Level {level})
Current Session: {len(self.conversation_history.get(campaign_id, []))} interactions"""
        
        # Memory section (retrieved from memory API)
        memory_section = self._get_memory_context_for_prompt(campaign_id)
        
        # Stats section
        stats_section = f"""[Stats]
Character Stats:
- HP: {character.get('hit_points', 10)}/{character.get('hit_points', 10)}
- AC: {character.get('armor_class', 10)}
- Level: {level}
- Experience: {character.get('experience', 0)}"""
        
        # Stat Triggers section (new)
        stat_triggers_section = self._get_stat_triggers_for_prompt(campaign_id, character)
        
        # Symbolism section (retrieved from symbolic analysis)
        symbolism_section = self._get_symbolic_context_for_prompt(campaign_id, player_input)
        
        # Goals section (retrieved from goal inference)
        goals_section = self._get_goals_context_for_prompt(campaign_id, player_input)
        
        # World State section (retrieved from world state)
        world_state_section = self._get_world_state_for_prompt(campaign_id)
        
        # Transformation section (retrieved from transformation analysis)
        transformation_section = self._get_transformation_context_for_prompt(campaign_id, player_input)
        
        # Resolution section (retrieved from resolution monitoring)
        resolution_section = self._get_resolution_context_for_prompt(campaign_id, player_input)
        
        # Input section
        input_section = f"""[Input]
Player Action: {player_input}"""
        
        return {
            'system': system_prompt,
            'context': context_section,
            'memory': memory_section,
            'stats': stats_section,
            'stat_triggers': stat_triggers_section,
            'world_state': world_state_section,
            'symbolism': symbolism_section,
            'goals': goals_section,
            'transformation': transformation_section,
            'resolution': resolution_section,
            'input': input_section
        }
    
    def _get_memory_context_for_prompt(self, campaign_id: str) -> str:
        """Retrieve memory context for prompt generation."""
        try:
            # Initialize TNE Demo Engine for memory retrieval
            from narrative_engine_integration import TNEDemoEngine
            tne_engine = TNEDemoEngine(campaign_id=campaign_id)
            
            # Get memory context
            memory_context = tne_engine.get_memory_context_for_ollama(
                user_id='player',
                max_memories=5  # Limit to 5 most recent memories
            )
            
            if memory_context and memory_context.strip():
                return f"""[Memory]
Recent memories and experiences:
{memory_context}"""
            else:
                return f"""[Memory]
No recent memories available."""
                
        except ImportError:
            return f"""[Memory]
Memory system not available."""
        except Exception as e:
            logger.warning(f"Error retrieving memory context: {e}")
            return f"""[Memory]
Memory retrieval error."""
    
    def _get_symbolic_context_for_prompt(self, campaign_id: str, player_input: str) -> str:
        """Retrieve symbolic context for prompt generation."""
        try:
            # Get recent narrative text from conversation history
            recent_history = self.conversation_history.get(campaign_id, [])
            narrative_text = ""
            
            # Combine recent messages for symbolic analysis
            for msg in recent_history[-3:]:  # Last 3 messages
                if msg.get('role') == 'assistant':
                    narrative_text += msg.get('content', '') + " "
            
            if not narrative_text.strip():
                return f"""[Symbolism]
No recent narrative content for symbolic analysis."""
            
            # Extract symbolic tags
            try:
                from narrative_engine_integration import TNEDemoEngine
                tne_engine = TNEDemoEngine(campaign_id=campaign_id)
                
                symbolic_tags = tne_engine.extract_symbolic_tags(
                    narrative_text=narrative_text,
                    memory_context={},
                    character_stats={}
                )
                
                if symbolic_tags:
                    tag_summary = []
                    for tag in symbolic_tags[:5]:  # Limit to 5 most relevant tags
                        tag_summary.append(f"- {tag.get('type', 'symbol')}: {tag.get('symbol', 'Unknown')}")
                    
                    return f"""[Symbolism]
Active symbolic elements:
{chr(10).join(tag_summary)}"""
                else:
                    return f"""[Symbolism]
No significant symbolic elements detected."""
                    
            except ImportError:
                # Use fallback symbolic extraction
                fallback_tags = extract_fallback_symbolic_tags(narrative_text)
                if fallback_tags:
                    tag_summary = []
                    for tag in fallback_tags[:5]:
                        tag_summary.append(f"- {tag.get('type', 'symbol')}: {tag.get('symbol', 'Unknown')}")
                    
                    return f"""[Symbolism]
Active symbolic elements:
{chr(10).join(tag_summary)}"""
                else:
                    return f"""[Symbolism]
No significant symbolic elements detected."""
                    
        except Exception as e:
            logger.warning(f"Error retrieving symbolic context: {e}")
            return f"""[Symbolism]
Symbolic analysis error."""
    
    def _get_goals_context_for_prompt(self, campaign_id: str, player_input: str) -> str:
        """Retrieve goals context for prompt generation."""
        try:
            # Get session history for goal inference
            session_history = self.conversation_history.get(campaign_id, [])
            
            if not session_history:
                return f"""[Goals]
No session history available for goal inference."""
            
            # Infer goals
            try:
                from narrative_engine_integration import TNEDemoEngine
                tne_engine = TNEDemoEngine(campaign_id=campaign_id)
                
                inferred_goals = tne_engine.infer_narrative_goals(
                    session_history=session_history,
                    memory_context={},
                    current_turn={'input': player_input}
                )
                
                if inferred_goals:
                    goal_summary = []
                    for goal in inferred_goals[:3]:  # Top 3 goals
                        confidence = goal.get('confidence', 0)
                        goal_summary.append(f"- {goal.get('type', 'Goal')} ({confidence:.1%}): {goal.get('justification', 'No justification')}")
                    
                    return f"""[Goals]
Active narrative goals:
{chr(10).join(goal_summary)}"""
                else:
                    return f"""[Goals]
No clear narrative goals detected."""
                    
            except ImportError:
                # Use fallback goal inference
                fallback_goals = infer_fallback_goals(session_history, {}, {'input': player_input})
                if fallback_goals:
                    goal_summary = []
                    for goal in fallback_goals:
                        confidence = goal.get('confidence', 0)
                        goal_summary.append(f"- {goal.get('type', 'Goal')} ({confidence:.1%}): {goal.get('justification', 'No justification')}")
                    
                    return f"""[Goals]
Active narrative goals:
{chr(10).join(goal_summary)}"""
                else:
                    return f"""[Goals]
No clear narrative goals detected."""
                    
        except Exception as e:
            logger.warning(f"Error retrieving goals context: {e}")
            return f"""[Goals]
Goal inference error."""
    
    def _get_stat_triggers_for_prompt(self, campaign_id: str, character: Dict[str, Any]) -> str:
        """Get stat-based branching triggers for prompt generation."""
        try:
            triggers = []
            
            # HP-based triggers
            current_hp = character.get('hit_points', 10)
            max_hp = character.get('hit_points', 10)  # Assuming current HP is max for now
            
            if current_hp <= 3:
                triggers.append("CRITICAL: You feel your vision blur and your limbs grow heavy. Death approaches...")
            elif current_hp <= 5:
                triggers.append("DANGER: Your wounds are severe. You need healing soon.")
            elif current_hp <= max_hp * 0.25:
                triggers.append("WARNING: You're badly injured and should seek rest.")
            
            # Ability score triggers
            ability_scores = character.get('ability_scores', {})
            
            # High Intelligence
            if ability_scores.get('intelligence', 10) >= 18:
                triggers.append("INTELLIGENCE: You recognize arcane symbols and patterns others might miss.")
            elif ability_scores.get('intelligence', 10) >= 16:
                triggers.append("INTELLIGENCE: Your sharp mind helps you notice important details.")
            
            # High Charisma
            if ability_scores.get('charisma', 10) >= 18:
                triggers.append("CHARISMA: Your natural charm makes others want to help you.")
            elif ability_scores.get('charisma', 10) >= 16:
                triggers.append("CHARISMA: People are drawn to your personality.")
            
            # High Strength
            if ability_scores.get('strength', 10) >= 18:
                triggers.append("STRENGTH: Your impressive physique intimidates others.")
            elif ability_scores.get('strength', 10) >= 16:
                triggers.append("STRENGTH: Your physical presence commands attention.")
            
            # High Dexterity
            if ability_scores.get('dexterity', 10) >= 18:
                triggers.append("DEXTERITY: Your reflexes are lightning-fast.")
            elif ability_scores.get('dexterity', 10) >= 16:
                triggers.append("DEXTERITY: You move with exceptional grace.")
            
            # High Wisdom
            if ability_scores.get('wisdom', 10) >= 18:
                triggers.append("WISDOM: Your intuition is almost supernatural.")
            elif ability_scores.get('wisdom', 10) >= 16:
                triggers.append("WISDOM: You have keen insight into situations.")
            
            # High Constitution
            if ability_scores.get('constitution', 10) >= 18:
                triggers.append("CONSTITUTION: Your endurance is legendary.")
            elif ability_scores.get('constitution', 10) >= 16:
                triggers.append("CONSTITUTION: You're remarkably resilient.")
            
            # Level-based triggers
            level = character.get('level', 1)
            if level >= 5:
                triggers.append("EXPERIENCED: Your combat experience shows in your movements.")
            elif level >= 3:
                triggers.append("SEASONED: You've seen enough to know what you're doing.")
            
            # Recent stat changes (tracked in campaign data)
            campaign_data = self.get_campaign_data(campaign_id)
            if campaign_data:
                recent_changes = campaign_data.get('recent_stat_changes', [])
                for change in recent_changes[-3:]:  # Last 3 changes
                    if change.get('type') == 'hp_loss':
                        triggers.append(f"RECENT: You're still recovering from recent injuries.")
                    elif change.get('type') == 'xp_gain':
                        triggers.append(f"RECENT: You feel stronger from recent experience.")
                    elif change.get('type') == 'ability_increase':
                        triggers.append(f"RECENT: Your {change.get('ability', 'abilities')} have improved.")
            
            if triggers:
                return f"""[StatTriggers]
Active stat-based narrative elements:
{chr(10).join(f"- {trigger}" for trigger in triggers)}"""
            else:
                return f"""[StatTriggers]
No significant stat-based triggers active."""
                
        except Exception as e:
            logger.warning(f"Error retrieving stat triggers: {e}")
            return f"""[StatTriggers]
Stat trigger analysis error."""
    
    def _get_world_state_for_prompt(self, campaign_id: str) -> str:
        """Get world state for prompt generation."""
        try:
            # Load world state from file
            world_state = self._load_world_state(campaign_id)
            
            if world_state:
                # Format world state for prompt
                world_elements = []
                
                # Current location
                if world_state.get('current_location'):
                    world_elements.append(f"Location: {world_state['current_location']}")
                
                # Important items
                items = world_state.get('items', [])
                if items:
                    world_elements.append(f"Items: {', '.join(items)}")
                
                # NPC flags
                npc_flags = world_state.get('npc_flags', {})
                if npc_flags:
                    npc_list = [f"{npc}: {status}" for npc, status in npc_flags.items()]
                    world_elements.append(f"NPCs: {', '.join(npc_list)}")
                
                # Story flags
                story_flags = world_state.get('story_flags', {})
                if story_flags:
                    flag_list = [f"{flag}: {value}" for flag, value in story_flags.items()]
                    world_elements.append(f"Story: {', '.join(flag_list)}")
                
                if world_elements:
                    return f"""[WorldState]
Current world state:
{chr(10).join(f"- {element}" for element in world_elements)}"""
                else:
                    return f"""[WorldState]
World state: Initial exploration phase."""
            else:
                return f"""[WorldState]
World state: New adventure beginning."""
                
        except Exception as e:
            logger.warning(f"Error retrieving world state: {e}")
            return f"""[WorldState]
World state: Unknown (error loading)."""
    
    def _load_world_state(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Load world state from file."""
        try:
            world_state_file = f"campaigns/{campaign_id}/world_state.json"
            if os.path.exists(world_state_file):
                with open(world_state_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.warning(f"Error loading world state: {e}")
            return None
    
    def _save_world_state(self, campaign_id: str, world_state: Dict[str, Any]) -> bool:
        """Save world state to file."""
        try:
            # Ensure campaigns directory exists
            os.makedirs(f"campaigns/{campaign_id}", exist_ok=True)
            
            world_state_file = f"campaigns/{campaign_id}/world_state.json"
            with open(world_state_file, 'w') as f:
                json.dump(world_state, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving world state: {e}")
            return False
    
    def _get_transformation_context_for_prompt(self, campaign_id: str, player_input: str) -> str:
        """Get transformation context for prompt generation."""
        try:
            # Get narrative history from conversation
            narrative_history = self.conversation_history.get(campaign_id, [])
            
            # Get symbolic tags from recent analysis
            recent_symbolic_tags = []
            try:
                from narrative_engine_integration import TNEDemoEngine
                tne_engine = TNEDemoEngine(campaign_id=campaign_id)
                
                # Get recent narrative text for symbolic analysis
                recent_text = ""
                for msg in narrative_history[-5:]:  # Last 5 messages
                    if msg.get('role') == 'assistant':
                        recent_text += msg.get('content', '') + " "
                
                if recent_text.strip():
                    symbolic_tags = tne_engine.extract_symbolic_tags(
                        narrative_text=recent_text,
                        memory_context={},
                        character_stats={}
                    )
                    recent_symbolic_tags = symbolic_tags
            except ImportError:
                # Use fallback symbolic extraction
                recent_text = ""
                for msg in narrative_history[-5:]:
                    if msg.get('role') == 'assistant':
                        recent_text += msg.get('content', '') + " "
                
                if recent_text.strip():
                    recent_symbolic_tags = extract_fallback_symbolic_tags(recent_text)
            
            # Get character stats
            character_stats = {}
            campaign_data = self.get_campaign_data(campaign_id)
            if campaign_data and campaign_data.get('active_character'):
                character_stats = campaign_data['active_character']
            
            # Infer transformation
            try:
                from narrative_engine_integration import TNEDemoEngine
                tne_engine = TNEDemoEngine(campaign_id=campaign_id)
                
                transformation = tne_engine.infer_character_transformation(
                    narrative_history=narrative_history,
                    symbolic_tags=recent_symbolic_tags,
                    character_stats=character_stats
                )
                
                if transformation and transformation.get('transformation_type') != 'Unknown':
                    evidence_text = ""
                    if transformation.get('evidence_snippets'):
                        evidence_text = "\n".join([f"- {snippet}" for snippet in transformation['evidence_snippets'][:2]])
                    
                    return f"""[Transformation]
Current character arc: {transformation.get('transformation_type', 'Unknown')}
Archetypal shift: {transformation.get('archetypal_shift', 'No clear pattern')}
Confidence: {transformation.get('confidence_score', 0):.1%}
Evidence: {evidence_text}"""
                else:
                    return f"""[Transformation]
No clear character transformation detected yet."""
                    
            except ImportError:
                # Use fallback transformation inference
                fallback_transformation = infer_fallback_transformation(narrative_history, recent_symbolic_tags, character_stats)
                
                if fallback_transformation and fallback_transformation.get('transformation_type') != 'Unknown':
                    evidence_text = ""
                    if fallback_transformation.get('evidence_snippets'):
                        evidence_text = "\n".join([f"- {snippet}" for snippet in fallback_transformation['evidence_snippets'][:2]])
                    
                    return f"""[Transformation]
Current character arc: {fallback_transformation.get('transformation_type', 'Unknown')}
Archetypal shift: {fallback_transformation.get('archetypal_shift', 'No clear pattern')}
Confidence: {fallback_transformation.get('confidence_score', 0):.1%}
Evidence: {evidence_text}"""
                else:
                    return f"""[Transformation]
No clear character transformation detected yet."""
                    
        except Exception as e:
            logger.warning(f"Error retrieving transformation context: {e}")
            return f"""[Transformation]
Transformation analysis error."""
    
    def _get_resolution_context_for_prompt(self, campaign_id: str, player_input: str) -> str:
        """Get resolution context for prompt generation."""
        try:
            # Get current goals
            goals = []
            try:
                from narrative_engine_integration import TNEDemoEngine
                tne_engine = TNEDemoEngine(campaign_id=campaign_id)
                
                # Get session history for goal inference
                session_history = self.conversation_history.get(campaign_id, [])
                
                if session_history:
                    inferred_goals = tne_engine.infer_narrative_goals(
                        session_history=session_history,
                        memory_context={},
                        current_turn={'input': player_input}
                    )
                    goals = inferred_goals
            except ImportError:
                # Use fallback goal inference
                session_history = self.conversation_history.get(campaign_id, [])
                if session_history:
                    goals = infer_fallback_goals(session_history, {}, {'input': player_input})
            
            # Get world state
            world_state = self._load_world_state(campaign_id) or {}
            
            # Get memory context
            memory_context = {}
            try:
                from narrative_engine_integration import TNEDemoEngine
                tne_engine = TNEDemoEngine(campaign_id=campaign_id)
                memory_context = tne_engine.get_memory_context_for_ollama(
                    user_id='player',
                    max_memories=5
                )
            except ImportError:
                memory_context = "Memory system not available"
            
            # Get transformations
            transformations = []
            try:
                from narrative_engine_integration import TNEDemoEngine
                tne_engine = TNEDemoEngine(campaign_id=campaign_id)
                
                narrative_history = self.conversation_history.get(campaign_id, [])
                recent_symbolic_tags = []
                
                # Get recent symbolic tags
                recent_text = ""
                for msg in narrative_history[-5:]:
                    if msg.get('role') == 'assistant':
                        recent_text += msg.get('content', '') + " "
                
                if recent_text.strip():
                    symbolic_tags = tne_engine.extract_symbolic_tags(
                        narrative_text=recent_text,
                        memory_context={},
                        character_stats={}
                    )
                    recent_symbolic_tags = symbolic_tags
                
                # Get character stats
                character_stats = {}
                campaign_data = self.get_campaign_data(campaign_id)
                if campaign_data and campaign_data.get('active_character'):
                    character_stats = campaign_data['active_character']
                
                transformation = tne_engine.infer_character_transformation(
                    narrative_history=narrative_history,
                    symbolic_tags=recent_symbolic_tags,
                    character_stats=character_stats
                )
                
                if transformation:
                    transformations = [transformation]
            except ImportError:
                # Use fallback transformation
                narrative_history = self.conversation_history.get(campaign_id, [])
                recent_symbolic_tags = []
                
                recent_text = ""
                for msg in narrative_history[-5:]:
                    if msg.get('role') == 'assistant':
                        recent_text += msg.get('content', '') + " "
                
                if recent_text.strip():
                    recent_symbolic_tags = extract_fallback_symbolic_tags(recent_text)
                
                character_stats = {}
                campaign_data = self.get_campaign_data(campaign_id)
                if campaign_data and campaign_data.get('active_character'):
                    character_stats = campaign_data['active_character']
                
                fallback_transformation = infer_fallback_transformation(narrative_history, recent_symbolic_tags, character_stats)
                if fallback_transformation:
                    transformations = [fallback_transformation]
            
            # Monitor resolution
            try:
                from narrative_engine_integration import TNEDemoEngine
                tne_engine = TNEDemoEngine(campaign_id=campaign_id)
                
                resolution = tne_engine.monitor_narrative_resolution(
                    goals=goals,
                    world_state=world_state,
                    memory_context=memory_context,
                    transformations=transformations
                )
                
                if resolution:
                    return f"""[Resolution]
Story stage: {resolution.get('resolution_state', 'unknown')}
Progress: {resolution.get('progress', 0):.1%}
Justification: {resolution.get('justification', 'No justification available')}
Recommendation: {resolution.get('recommendation', 'No recommendation available')}"""
                else:
                    return f"""[Resolution]
Story stage: early
Progress: 0.0%
Justification: Story is in early development
Recommendation: Establish stakes and introduce conflicts"""
                    
            except ImportError:
                # Use fallback resolution monitoring
                fallback_resolution = monitor_fallback_resolution(goals, world_state, memory_context, transformations)
                
                return f"""[Resolution]
Story stage: {fallback_resolution.get('resolution_state', 'unknown')}
Progress: {fallback_resolution.get('progress', 0):.1%}
Justification: {fallback_resolution.get('justification', 'No justification available')}
Recommendation: {fallback_resolution.get('recommendation', 'No recommendation available')}"""
                    
        except Exception as e:
            logger.warning(f"Error retrieving resolution context: {e}")
            return f"""[Resolution]
Resolution monitoring error."""
    
    def save_campaign(self, campaign_id: str) -> bool:
        """Save current campaign state."""
        try:
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if os.path.exists(campaign_file):
                with open(campaign_file, 'r') as f:
                    campaign_data = json.load(f)
                
                campaign_data["last_modified"] = datetime.datetime.now().isoformat()
                campaign_data["session_count"] = campaign_data.get("session_count", 0) + 1
                
                # Save conversation history
                if campaign_id in self.conversation_history:
                    campaign_data["conversation_history"] = self.conversation_history[campaign_id]
                
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

class TNEDemoGame:
    """Simple unified game manager."""
    
    def __init__(self):
        self.character_generator = TNECharacterGenerator()
        self.narrative_bridge = TNEDemoBridge()
    
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
game = TNEDemoGame()

@app.route('/')
def start_screen():
    """Start screen - the landing page with session management."""
    return render_template('start.html')

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
            return jsonify({'success': True, 'redirect': f'/game?campaign_id={campaign_id}'})
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
    try:
        # Get current character data
        character_data = game.character_generator.get_character_data()
        
        # Get ability scores
        ability_scores = character_data.get('ability_scores', {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        })
        
        # Get racial information
        race = character_data.get('race', 'Unknown')
        subrace = character_data.get('subrace')
        
        # Get racial summary if available
        racial_summary = ""
        try:
            # from utils.racial_modifiers import racial_modifiers  # Removed duplicate import
            if race and race != 'Unknown':
                racial_summary = racial_modifiers.format_racial_summary(race, subrace)
        except ImportError:
            racial_summary = f"Race: {race}" + (f" ({subrace})" if subrace else "")
        
        # Create simple HTML response
        html_response = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Character Sheet Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .character-info {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .ability-scores {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
        .ability-score {{ background: white; padding: 10px; border-radius: 3px; border: 1px solid #ddd; }}
        .score {{ font-weight: bold; color: #2c5aa0; }}
        .modifier {{ color: #666; }}
        .racial-info {{ background: #e8f4f8; padding: 15px; border-radius: 5px; }}
        .racial-summary {{ white-space: pre-line; }}
    </style>
</head>
<body>
    <h1>Character Sheet Test</h1>
    
    <div class="character-info">
        <h2>Character Information</h2>
        <p><strong>Name:</strong> {character_data.get('name', 'Unknown')}</p>
        <p><strong>Race:</strong> {race}</p>
        <p><strong>Subrace:</strong> {subrace or 'None'}</p>
        <p><strong>Class:</strong> {character_data.get('class', 'Unknown')}</p>
        <p><strong>Level:</strong> {character_data.get('level', 1)}</p>
    </div>
    
    <div class="ability-scores">
        <h2>Ability Scores</h2>
"""
        
        for ability, score in ability_scores.items():
            modifier = (score - 10) // 2
            modifier_text = f"+{modifier}" if modifier >= 0 else f"{modifier}"
            html_response += f"""
        <div class="ability-score">
            <div class="score">{ability.title()}: {score}</div>
            <div class="modifier">Modifier: {modifier_text}</div>
        </div>
"""
        
        html_response += f"""
    </div>
    
    <div class="racial-info">
        <h2>Racial Information</h2>
        <div class="racial-summary">{racial_summary}</div>
    </div>
</body>
</html>
"""
        
        return html_response
    except Exception as e:
        logger.error(f"Error in test character sheet: {e}")
        return f"Error: {e}"

@app.route('/character-sheet-test')
def character_sheet_test():
    """Alternative test page for character sheet updates."""
    try:
        return "Character Sheet Test - Alternative Working!"
    except Exception as e:
        logger.error(f"Error in character sheet test: {e}")
        return f"Error: {e}"

@app.route('/ability-scores-test')
def ability_scores_test():
    """Test page for ability scores display."""
    try:
        # Get current character data
        character_data = game.character_generator.get_character_data()
        
        # Get ability scores
        ability_scores = character_data.get('ability_scores', {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        })
        
        # Create simple text response
        response = f"""
Ability Scores Test

Character: {character_data.get('name', 'Unknown')}
Race: {character_data.get('race', 'Unknown')}
Class: {character_data.get('class', 'Unknown')}
Level: {character_data.get('level', 1)}

Ability Scores:
"""
        
        for ability, score in ability_scores.items():
            modifier = (score - 10) // 2
            modifier_text = f"+{modifier}" if modifier >= 0 else f"{modifier}"
            response += f"{ability.title()}: {score} (Modifier: {modifier_text})\n"
        
        return response
    except Exception as e:
        logger.error(f"Error in ability scores test: {e}")
        return f"Error: {e}"

@app.route('/simple-test')
def simple_test():
    """Simple test endpoint."""
    return "Simple test endpoint working!"

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
        temp_bridge = TNEDemoBridge()
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
    
    character_id = game.character_generator.character_data.get('id') or game.character_generator.character_data.get('name', 'unknown')
    symbolic_state = tne_connector.get_symbolic_summary(character_id)
    
    # Check for TNE errors and handle gracefully
    if symbolic_state.get('error'):
        return jsonify({
            'success': True,
            'symbolic_data': {
                'error': 'Symbolic analysis unavailable',
                'message': 'TNE symbolic processing is currently unavailable'
            }
        })
    
    # Return TNE-compliant symbolic data
    return jsonify({
        'success': True, 
        'symbolic_data': {
            'chaos_order_tension': symbolic_state.get('chaos_order_tension', 0.5),
            'chaos_order_state': symbolic_state.get('chaos_order_state', 'Unknown'),
            'narrative_decay': symbolic_state.get('narrative_decay', 0.0),
            'symbolic_coherence': symbolic_state.get('symbolic_coherence', 1.0),
            'narrative_response': symbolic_state.get('narrative_response', ''),
            'archetypal_tags': symbolic_state.get('archetypal_tags', []),
            'archetypal_data': game.character_generator.character_data.get('_symbolic_data', {})
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
    """Main game interface - enhanced gameplay with narrative display."""
    campaign_id = session.get('campaign_id')
    return render_template('gameplay.html', identity_scope_id=campaign_id)

@app.route('/game/new')
def new_game():
    """Start a new game with optional campaign ID."""
    campaign_id = request.args.get('campaign')
    if campaign_id:
        session['campaign_id'] = campaign_id
    return render_template('character_creation.html')

@app.route('/game/resume/<session_id>')
def resume_game(session_id):
    """Resume a specific game session."""
    try:
        # Load the session
        success = game.narrative_bridge.load_campaign(session_id)
        if success:
            session['campaign_id'] = session_id
            return render_template('gameplay.html')
        else:
            return jsonify({'success': False, 'message': 'Failed to load session'})
    except Exception as e:
        logger.error(f"Error resuming game: {e}")
        return jsonify({'success': False, 'message': 'Error resuming game'})

@app.route('/game/demo')
def demo_game():
    """Start a demo game with temporary session."""
    try:
        # Create a demo session with guest prefix
        demo_session_id = f"guest_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session['campaign_id'] = demo_session_id
        session['demo_mode'] = True
        
        # Initialize demo campaign
        character_data = {
            'name': 'Demo Character',
            'race': 'Human',
            'class': 'Fighter',
            'level': 1,
            'ability_scores': {
                'strength': 15, 'dexterity': 14, 'constitution': 13,
                'intelligence': 12, 'wisdom': 10, 'charisma': 8
            }
        }
        
        game.narrative_bridge.initialize_campaign(character_data, demo_session_id)
        
        return render_template('gameplay.html')
    except Exception as e:
        logger.error(f"Error starting demo: {e}")
        return jsonify({'success': False, 'message': 'Error starting demo'})

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

@app.route('/api/game/recap')
def get_campaign_recap():
    """Get a recap of the current campaign state."""
    try:
        # Try to get campaign_id from query parameter first (more reliable)
        campaign_id = request.args.get('campaign_id')
        
        # If not in query parameter, try session
        if not campaign_id:
            campaign_id = session.get('campaign_id')
        
        logger.info(f"🔍 Campaign recap requested for campaign_id: {campaign_id}")
        
        if not campaign_id:
            logger.warning("❌ No campaign_id in query parameter or session")
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        # Load the campaign if not already loaded
        if not game.narrative_bridge.load_campaign(campaign_id):
            logger.error(f"❌ Failed to load campaign {campaign_id}")
            return jsonify({'success': False, 'message': 'Failed to load campaign'})
        
        recap = game.narrative_bridge.generate_campaign_recap(campaign_id)
        logger.info(f"✅ Generated recap: {recap[:100]}...")
        
        return jsonify({
            'success': True,
            'recap': recap
        })
    
    except Exception as e:
        logger.error(f"Error getting campaign recap: {e}")
        return jsonify({'success': False, 'message': 'Error generating recap'})

@app.route('/api/memory/context')
def get_memory_context():
    """Get structured memory context for the current campaign."""
    try:
        campaign_id = session.get('campaign_id')
        if not campaign_id:
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        # Get campaign data
        campaign_data = game.narrative_bridge.get_campaign_data(campaign_id)
        if not campaign_data:
            return jsonify({'success': False, 'message': 'Campaign not found'})
        
        # Initialize TNE Demo Engine for memory retrieval
        try:
            from narrative_engine_integration import TNEDemoEngine
            tne_engine = TNEDemoEngine(campaign_id=campaign_id)
            
            # Get memory context
            memory_context = tne_engine.get_memory_context_for_ollama(
                user_id='player',
                max_memories=10
            )
            
            # Get memory stats
            memory_stats = tne_engine.get_memory_stats()
            
            # Structure the response
            structured_memory = {
                'recent_memories': memory_context,
                'memory_stats': memory_stats,
                'emotional_tags': [],
                'thematic_tags': [],
                'importance_levels': []
            }
            
            # Extract tags from recent memories (simplified for now)
            if memory_context:
                # Parse memory context for tags
                memory_lines = memory_context.split('\n')
                for line in memory_lines:
                    if 'emotional' in line.lower():
                        structured_memory['emotional_tags'].append(line.strip())
                    elif 'thematic' in line.lower():
                        structured_memory['thematic_tags'].append(line.strip())
            
            return jsonify({
                'success': True,
                'memory_context': structured_memory
            })
            
        except ImportError:
            # Fallback if TNE integration is not available
            logger.warning("TNE integration not available, using fallback memory")
            return jsonify({
                'success': True,
                'memory_context': {
                    'recent_memories': "Memory system not available",
                    'memory_stats': {'total_memories': 0, 'recent_memories': 0},
                    'emotional_tags': [],
                    'thematic_tags': [],
                    'importance_levels': []
                }
            })
    
    except Exception as e:
        logger.error(f"Error getting memory context: {e}")
        return jsonify({'success': False, 'message': 'Error retrieving memory context'})

@app.route('/api/symbolic/tags', methods=['POST'])
def extract_symbolic_tags():
    """Extract symbolic tags from narrative text using the Narrative Engine."""
    try:
        data = request.get_json()
        narrative_text = data.get('narrative_text', '')
        memory_context = data.get('memory_context', {})
        character_stats = data.get('character_stats', {})
        
        if not narrative_text:
            return jsonify({'success': False, 'message': 'Narrative text is required'})
        
        # Initialize TNE Demo Engine for symbolic processing
        try:
            from narrative_engine_integration import TNEDemoEngine
            campaign_id = session.get('campaign_id', 'default')
            tne_engine = TNEDemoEngine(campaign_id=campaign_id)
            
            # Extract symbolic tags using TNE
            symbolic_tags = tne_engine.extract_symbolic_tags(
                narrative_text=narrative_text,
                memory_context=memory_context,
                character_stats=character_stats
            )
            
            return jsonify({
                'success': True,
                'symbolic_tags': symbolic_tags
            })
            
        except ImportError:
            # Fallback symbolic tag extraction
            logger.warning("TNE integration not available, using fallback symbolic extraction")
            fallback_tags = extract_fallback_symbolic_tags(narrative_text)
            return jsonify({
                'success': True,
                'symbolic_tags': fallback_tags
            })
    
    except Exception as e:
        logger.error(f"Error extracting symbolic tags: {e}")
        return jsonify({'success': False, 'message': 'Error extracting symbolic tags'})

def extract_fallback_symbolic_tags(narrative_text: str) -> List[Dict[str, Any]]:
    """Fallback symbolic tag extraction when TNE is not available."""
    text_lower = narrative_text.lower()
    tags = []
    
    # Archetype detection
    archetypes = {
        'Hero': ['hero', 'protagonist', 'champion', 'warrior', 'savior'],
        'Mentor': ['mentor', 'guide', 'teacher', 'wise', 'elder'],
        'Shadow': ['shadow', 'dark', 'evil', 'villain', 'antagonist'],
        'Trickster': ['trickster', 'fool', 'jester', 'deceiver', 'chaos'],
        'Rebirth': ['rebirth', 'renewal', 'transformation', 'change', 'evolution'],
        'Labyrinth': ['labyrinth', 'maze', 'confusion', 'lost', 'journey'],
        'Monster': ['monster', 'beast', 'creature', 'threat', 'danger'],
        'Threshold': ['threshold', 'door', 'gate', 'passage', 'boundary'],
        'Sacred': ['sacred', 'holy', 'divine', 'spiritual', 'magical'],
        'Profane': ['profane', 'corrupt', 'tainted', 'fallen', 'sinful']
    }
    
    for archetype, keywords in archetypes.items():
        if any(keyword in text_lower for keyword in keywords):
            tags.append({
                'type': 'archetype',
                'symbol': archetype,
                'confidence': 0.8,
                'color': '#fbbf24',
                'tooltip': f'Archetypal pattern: {archetype}'
            })
    
    # Theme detection
    themes = {
        'Redemption': ['redemption', 'forgiveness', 'atonement', 'salvation'],
        'Betrayal': ['betrayal', 'treachery', 'deception', 'traitor'],
        'Sacrifice': ['sacrifice', 'giving up', 'losing', 'surrendering'],
        'Transformation': ['transformation', 'change', 'evolution', 'growth'],
        'Power': ['power', 'strength', 'authority', 'control'],
        'Justice': ['justice', 'fairness', 'right', 'wrong', 'punishment'],
        'Love': ['love', 'affection', 'passion', 'romance'],
        'Death': ['death', 'dying', 'mortal', 'end', 'final'],
        'Rebirth': ['rebirth', 'renewal', 'awakening', 'resurrection'],
        'Chaos': ['chaos', 'disorder', 'confusion', 'anarchy']
    }
    
    for theme, keywords in themes.items():
        if any(keyword in text_lower for keyword in keywords):
            tags.append({
                'type': 'theme',
                'symbol': theme,
                'confidence': 0.7,
                'color': '#3b82f6',
                'tooltip': f'Narrative theme: {theme}'
            })
    
    # Metaphor detection
    metaphors = {
        'Light vs Dark': ['light', 'dark', 'shadow', 'illumination', 'obscurity'],
        'Journey': ['journey', 'path', 'road', 'travel', 'quest'],
        'Battle': ['battle', 'war', 'fight', 'conflict', 'struggle'],
        'Growth': ['growth', 'bloom', 'flourish', 'develop', 'mature'],
        'Decay': ['decay', 'rot', 'wither', 'fade', 'decline'],
        'Water': ['water', 'flow', 'river', 'ocean', 'tide'],
        'Fire': ['fire', 'flame', 'burn', 'heat', 'passion'],
        'Earth': ['earth', 'ground', 'soil', 'foundation', 'stability']
    }
    
    for metaphor, keywords in metaphors.items():
        if any(keyword in text_lower for keyword in keywords):
            tags.append({
                'type': 'metaphor',
                'symbol': metaphor,
                'confidence': 0.6,
                'color': '#10b981',
                'tooltip': f'Metaphorical meaning: {metaphor}'
            })
    
    # Contradiction detection
    contradictions = []
    contradiction_pairs = [
        ('light', 'dark'), ('good', 'evil'), ('life', 'death'),
        ('hope', 'despair'), ('love', 'hate'), ('order', 'chaos'),
        ('strength', 'weakness'), ('truth', 'lies'), ('freedom', 'control')
    ]
    
    for pair in contradiction_pairs:
        if pair[0] in text_lower and pair[1] in text_lower:
            contradictions.append(f"{pair[0].title()} vs {pair[1].title()}")
    
    for contradiction in contradictions:
        tags.append({
            'type': 'contradiction',
            'symbol': contradiction,
            'confidence': 0.9,
            'color': '#ef4444',
            'tooltip': f'Contradictory elements: {contradiction}'
        })
    
    return tags

@app.route('/api/goal/infer', methods=['POST'])
def infer_narrative_goals():
    """Infer narrative goals from session history and memory context."""
    try:
        data = request.get_json()
        session_history = data.get('session_history', [])
        memory_context = data.get('memory_context', {})
        current_turn = data.get('current_turn', {})
        
        # Initialize TNE Demo Engine for goal inference
        try:
            from narrative_engine_integration import TNEDemoEngine
            campaign_id = session.get('campaign_id', 'default')
            tne_engine = TNEDemoEngine(campaign_id=campaign_id)
            
            # Infer goals using TNE
            inferred_goals = tne_engine.infer_narrative_goals(
                session_history=session_history,
                memory_context=memory_context,
                current_turn=current_turn
            )
            
            return jsonify({
                'success': True,
                'inferred_goals': inferred_goals
            })
            
        except ImportError:
            # Fallback goal inference
            logger.warning("TNE integration not available, using fallback goal inference")
            fallback_goals = infer_fallback_goals(session_history, memory_context, current_turn)
            return jsonify({
                'success': True,
                'inferred_goals': fallback_goals
            })
    
    except Exception as e:
        logger.error(f"Error inferring narrative goals: {e}")
        return jsonify({'success': False, 'message': 'Error inferring narrative goals'})

def infer_fallback_goals(session_history: List[Dict], memory_context: Dict, current_turn: Dict) -> List[Dict[str, Any]]:
    """Fallback goal inference when TNE is not available."""
    goals = []
    
    # Analyze session history for goal patterns
    all_text = ' '.join([msg.get('content', '') for msg in session_history]).lower()
    
    # Goal type detection
    goal_patterns = {
        'Escape': {
            'keywords': ['escape', 'flee', 'run', 'get away', 'leave', 'exit'],
            'confidence': 0.8,
            'color': '#ef4444'
        },
        'Discover': {
            'keywords': ['find', 'discover', 'explore', 'search', 'investigate', 'learn'],
            'confidence': 0.7,
            'color': '#3b82f6'
        },
        'Change': {
            'keywords': ['change', 'transform', 'become', 'evolve', 'grow', 'develop'],
            'confidence': 0.6,
            'color': '#10b981'
        },
        'Protect': {
            'keywords': ['protect', 'defend', 'guard', 'save', 'shield', 'shelter'],
            'confidence': 0.8,
            'color': '#f59e0b'
        },
        'Destroy': {
            'keywords': ['destroy', 'kill', 'eliminate', 'remove', 'end', 'stop'],
            'confidence': 0.9,
            'color': '#dc2626'
        },
        'Connect': {
            'keywords': ['connect', 'meet', 'join', 'unite', 'bond', 'relationship'],
            'confidence': 0.6,
            'color': '#8b5cf6'
        },
        'Survive': {
            'keywords': ['survive', 'live', 'stay alive', 'endure', 'persist'],
            'confidence': 0.7,
            'color': '#059669'
        },
        'Achieve': {
            'keywords': ['achieve', 'accomplish', 'succeed', 'win', 'complete', 'finish'],
            'confidence': 0.6,
            'color': '#fbbf24'
        }
    }
    
    # Detect goals based on keywords
    for goal_type, pattern in goal_patterns.items():
        if any(keyword in all_text for keyword in pattern['keywords']):
            # Calculate confidence based on frequency
            keyword_count = sum(1 for keyword in pattern['keywords'] if keyword in all_text)
            confidence = min(0.95, pattern['confidence'] + (keyword_count * 0.05))
            
            # Generate narrative justification
            justification = generate_goal_justification(goal_type, all_text)
            
            goals.append({
                'type': goal_type,
                'confidence': confidence,
                'color': pattern['color'],
                'justification': justification,
                'progress': min(0.8, confidence * 0.8)  # Progress bar value
            })
    
    # Sort by confidence and return top 3
    goals.sort(key=lambda x: x['confidence'], reverse=True)
    return goals[:3]

def generate_goal_justification(goal_type: str, context_text: str) -> str:
    """Generate a brief narrative justification for a goal."""
    justifications = {
        'Escape': "The character seeks to escape from a threatening or confining situation.",
        'Discover': "The character is driven by curiosity and the desire to uncover hidden knowledge.",
        'Change': "The character is undergoing or seeking personal transformation and growth.",
        'Protect': "The character feels responsible for protecting others or important things.",
        'Destroy': "The character is motivated to eliminate a threat or obstacle.",
        'Connect': "The character seeks meaningful relationships or connections with others.",
        'Survive': "The character is focused on basic survival in a dangerous environment.",
        'Achieve': "The character is pursuing a specific accomplishment or success."
    }
    
    return justifications.get(goal_type, f"The character is pursuing a {goal_type.lower()} goal.")

@app.route('/api/transformation/infer', methods=['POST'])
def infer_character_transformation():
    """Infer character transformation from narrative history and symbolic tags."""
    try:
        data = request.get_json()
        narrative_history = data.get('narrative_history', [])
        symbolic_tags = data.get('symbolic_tags', [])
        character_stats = data.get('character_stats', {})
        
        # Initialize TNE Demo Engine for transformation analysis
        try:
            from narrative_engine_integration import TNEDemoEngine
            campaign_id = session.get('campaign_id', 'default')
            tne_engine = TNEDemoEngine(campaign_id=campaign_id)
            
            # Infer transformation using TNE
            transformation = tne_engine.infer_character_transformation(
                narrative_history=narrative_history,
                symbolic_tags=symbolic_tags,
                character_stats=character_stats
            )
            
            return jsonify({
                'success': True,
                'transformation': transformation
            })
            
        except ImportError:
            # Fallback transformation inference
            logger.warning("TNE integration not available, using fallback transformation inference")
            fallback_transformation = infer_fallback_transformation(narrative_history, symbolic_tags, character_stats)
            return jsonify({
                'success': True,
                'transformation': fallback_transformation
            })
    
    except Exception as e:
        logger.error(f"Error inferring character transformation: {e}")
        return jsonify({'success': False, 'message': 'Error inferring transformation'})

def infer_fallback_transformation(narrative_history: List[Dict], symbolic_tags: List[Dict], character_stats: Dict) -> Dict[str, Any]:
    """Fallback transformation inference when TNE is not available."""
    
    # Analyze narrative history for transformation patterns
    all_text = ' '.join([msg.get('content', '') for msg in narrative_history]).lower()
    
    # Transformation archetype patterns
    transformation_patterns = {
        'Innocent → Orphan → Seeker → Warrior → Magician': {
            'keywords': ['innocent', 'naive', 'orphan', 'lost', 'seeker', 'quest', 'warrior', 'battle', 'magician', 'power'],
            'confidence': 0.8,
            'archetypal_shift': 'Hero\'s Journey',
            'description': 'Classic hero\'s journey from innocence to mastery'
        },
        'Victim → Survivor → Redeemer': {
            'keywords': ['victim', 'suffering', 'survivor', 'endure', 'redeem', 'save', 'heal'],
            'confidence': 0.7,
            'archetypal_shift': 'Redemption Arc',
            'description': 'Transformation from victimhood to redemption'
        },
        'Monster → Protector': {
            'keywords': ['monster', 'evil', 'dark', 'protect', 'guard', 'save', 'shield'],
            'confidence': 0.6,
            'archetypal_shift': 'Beauty and the Beast',
            'description': 'Transformation from monstrous to protective'
        },
        'Fool → Sage': {
            'keywords': ['fool', 'naive', 'ignorant', 'sage', 'wise', 'knowledge', 'learn'],
            'confidence': 0.7,
            'archetypal_shift': 'Wisdom Journey',
            'description': 'Transformation from ignorance to wisdom'
        },
        'Outcast → Leader': {
            'keywords': ['outcast', 'alone', 'rejected', 'leader', 'guide', 'inspire', 'unite'],
            'confidence': 0.6,
            'archetypal_shift': 'Leadership Arc',
            'description': 'Transformation from isolation to leadership'
        }
    }
    
    # Detect transformation patterns
    detected_transformations = []
    for pattern_name, pattern_data in transformation_patterns.items():
        keyword_matches = sum(1 for keyword in pattern_data['keywords'] if keyword in all_text)
        if keyword_matches >= 2:  # Need at least 2 keyword matches
            confidence = min(0.95, pattern_data['confidence'] + (keyword_matches * 0.05))
            detected_transformations.append({
                'transformation_type': pattern_name,
                'archetypal_shift': pattern_data['archetypal_shift'],
                'confidence_score': confidence,
                'description': pattern_data['description'],
                'evidence_snippets': extract_evidence_snippets(all_text, pattern_data['keywords'])
            })
    
    # Sort by confidence and return the most likely transformation
    if detected_transformations:
        detected_transformations.sort(key=lambda x: x['confidence_score'], reverse=True)
        return detected_transformations[0]
    else:
        return {
            'transformation_type': 'Unknown',
            'archetypal_shift': 'No clear pattern',
            'confidence_score': 0.0,
            'description': 'No clear transformation detected',
            'evidence_snippets': []
        }

def extract_evidence_snippets(text: str, keywords: List[str]) -> List[str]:
    """Extract evidence snippets from text based on keywords."""
    snippets = []
    sentences = text.split('.')
    
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in keywords):
            # Clean up the sentence
            clean_sentence = sentence.strip()
            if len(clean_sentence) > 10:  # Only include substantial snippets
                snippets.append(clean_sentence[:100] + "..." if len(clean_sentence) > 100 else clean_sentence)
    
    return snippets[:3]  # Limit to 3 most relevant snippets

@app.route('/api/resolution/monitor', methods=['POST'])
def monitor_narrative_resolution():
    """Monitor narrative resolution and detect proximity to climax."""
    try:
        data = request.get_json()
        goals = data.get('goals', [])
        world_state = data.get('world_state', {})
        memory_context = data.get('memory_context', {})
        transformations = data.get('transformations', [])
        
        # Initialize TNE Demo Engine for resolution monitoring
        try:
            from narrative_engine_integration import TNEDemoEngine
            campaign_id = session.get('campaign_id', 'default')
            tne_engine = TNEDemoEngine(campaign_id=campaign_id)
            
            # Monitor resolution using TNE
            resolution = tne_engine.monitor_narrative_resolution(
                goals=goals,
                world_state=world_state,
                memory_context=memory_context,
                transformations=transformations
            )
            
            return jsonify({
                'success': True,
                'resolution': resolution
            })
            
        except ImportError:
            # Fallback resolution monitoring
            logger.warning("TNE integration not available, using fallback resolution monitoring")
            fallback_resolution = monitor_fallback_resolution(goals, world_state, memory_context, transformations)
            return jsonify({
                'success': True,
                'resolution': fallback_resolution
            })
    
    except Exception as e:
        logger.error(f"Error monitoring narrative resolution: {e}")
        return jsonify({'success': False, 'message': 'Error monitoring resolution'})

def monitor_fallback_resolution(goals: List[Dict], world_state: Dict, memory_context: Dict, transformations: List[Dict]) -> Dict[str, Any]:
    """Fallback resolution monitoring when TNE is not available."""
    
    # Analyze goals for completion status
    completed_goals = sum(1 for goal in goals if goal.get('confidence', 0) > 0.8)
    total_goals = len(goals) if goals else 1
    
    # Analyze world state for story progression
    story_flags = world_state.get('story_flags', {})
    completed_flags = sum(1 for flag, value in story_flags.items() if value is True)
    total_flags = len(story_flags) if story_flags else 1
    
    # Analyze transformations for character development
    transformation_progress = 0
    if transformations:
        transformation_progress = transformations[0].get('confidence_score', 0)
    
    # Calculate overall resolution progress
    goal_progress = completed_goals / total_goals if total_goals > 0 else 0
    flag_progress = completed_flags / total_flags if total_flags > 0 else 0
    overall_progress = (goal_progress + flag_progress + transformation_progress) / 3
    
    # Determine resolution state
    if overall_progress < 0.25:
        resolution_state = 'early'
        recommendation = 'Establish stakes and introduce conflicts'
    elif overall_progress < 0.5:
        resolution_state = 'mid'
        recommendation = 'Develop character relationships and deepen conflicts'
    elif overall_progress < 0.75:
        resolution_state = 'climax'
        recommendation = 'Raise stakes and introduce moral costs'
    else:
        resolution_state = 'denouement'
        recommendation = 'Resolve conflicts and show character growth'
    
    return {
        'resolution_state': resolution_state,
        'progress': overall_progress,
        'goal_progress': goal_progress,
        'flag_progress': flag_progress,
        'transformation_progress': transformation_progress,
        'justification': f"Story is {resolution_state} stage with {overall_progress:.1%} completion",
        'recommendation': recommendation
    }

@app.route('/api/world/state', methods=['GET'])
def get_world_state():
    """Get current world state for the active campaign."""
    try:
        campaign_id = session.get('campaign_id')
        if not campaign_id:
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        # Get world state from TNE Demo Bridge
        world_state = game.narrative_bridge._load_world_state(campaign_id)
        
        if world_state:
            return jsonify({
                'success': True,
                'world_state': world_state
            })
        else:
            # Return default world state
            default_state = {
                'current_location': 'Unknown',
                'items': [],
                'npc_flags': {},
                'story_flags': {},
                'discovered_locations': [],
                'met_characters': [],
                'acquired_items': []
            }
            return jsonify({
                'success': True,
                'world_state': default_state
            })
    
    except Exception as e:
        logger.error(f"Error getting world state: {e}")
        return jsonify({'success': False, 'message': 'Error retrieving world state'})

@app.route('/api/world/update', methods=['POST'])
def update_world_state():
    """Update world state with new information."""
    try:
        campaign_id = session.get('campaign_id')
        if not campaign_id:
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        data = request.get_json()
        updates = data.get('updates', {})
        
        if not updates:
            return jsonify({'success': False, 'message': 'No updates provided'})
        
        # Load current world state
        current_state = game.narrative_bridge._load_world_state(campaign_id) or {
            'current_location': 'Unknown',
            'items': [],
            'npc_flags': {},
            'story_flags': {},
            'discovered_locations': [],
            'met_characters': [],
            'acquired_items': []
        }
        
        # Apply updates
        for key, value in updates.items():
            if key == 'current_location':
                current_state['current_location'] = value
                if value not in current_state['discovered_locations']:
                    current_state['discovered_locations'].append(value)
            elif key == 'add_item':
                if value not in current_state['items']:
                    current_state['items'].append(value)
                if value not in current_state['acquired_items']:
                    current_state['acquired_items'].append(value)
            elif key == 'remove_item':
                if value in current_state['items']:
                    current_state['items'].remove(value)
            elif key == 'npc_flag':
                npc_name = value.get('npc')
                npc_status = value.get('status')
                if npc_name and npc_status:
                    current_state['npc_flags'][npc_name] = npc_status
                    if npc_name not in current_state['met_characters']:
                        current_state['met_characters'].append(npc_name)
            elif key == 'story_flag':
                flag_name = value.get('flag')
                flag_value = value.get('value')
                if flag_name and flag_value is not None:
                    current_state['story_flags'][flag_name] = flag_value
            else:
                # Direct key-value update
                current_state[key] = value
        
        # Save updated world state
        success = game.narrative_bridge._save_world_state(campaign_id, current_state)
        
        if success:
            return jsonify({
                'success': True,
                'world_state': current_state,
                'message': 'World state updated successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to save world state'})
    
    except Exception as e:
        logger.error(f"Error updating world state: {e}")
        return jsonify({'success': False, 'message': 'Error updating world state'})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for TNE Demo monitoring."""
    try:
        # Check LLM provider status
        llm_healthy = False
        llm_provider = "unknown"
        try:
            from llm_interface.provider_factory import get_llm_provider
            provider = get_llm_provider()
            llm_healthy = provider is not None
            llm_provider = provider.provider_name if provider else "unknown"
        except Exception as e:
            logger.error(f"LLM provider health check failed: {e}")
        
        # Check TNB connection (if configured)
        tnb_healthy = False
        try:
            import os
            tnb_endpoint = os.environ.get('TNB_ENDPOINT')
            if tnb_endpoint:
                import requests
                response = requests.get(f"{tnb_endpoint}/api/health", timeout=5)
                tnb_healthy = response.status_code == 200
        except:
            pass
        
        # Check TNE connection (if configured)
        tne_healthy = False
        try:
            import os
            tne_endpoint = os.environ.get('TNE_ENDPOINT')
            if tne_endpoint:
                import requests
                response = requests.get(f"{tne_endpoint}/api/health", timeout=5)
                tne_healthy = response.status_code == 200
        except:
            pass
        
        # Check if demo instance is available
        demo_healthy = hasattr(game, 'character_generator') and game.character_generator is not None
        
        # Determine overall status
        if llm_healthy and demo_healthy:
            status = 'healthy'
        elif llm_healthy or demo_healthy:
            status = 'degraded'
        else:
            status = 'unhealthy'
        
        return jsonify({
            'status': status,
            'timestamp': datetime.datetime.now().isoformat(),
            'llm_provider': llm_provider,
            'llm_healthy': llm_healthy,
            'tnb_healthy': tnb_healthy,
            'tne_healthy': tne_healthy,
            'demo_healthy': demo_healthy,
            'memory_visualization': os.environ.get('MEMORY_VISUALIZATION', 'false').lower() == 'true',
            'goal_tracking': os.environ.get('GOAL_TRACKING', 'false').lower() == 'true',
            'symbolic_display': os.environ.get('SYMBOLIC_DISPLAY', 'false').lower() == 'true',
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
    """Handle ability score assignment using SRD 5.2 methods."""
    try:
        data = request.get_json()
        assignment_type = data.get('type', 'auto')  # 'auto', 'standard_array', 'point_buy', 'roll', 'manual'
        
        if assignment_type == 'auto':
            # Auto-assign stats based on character story
            scores = game.character_generator.ability_score_system.assign_auto_based_on_story(
                game.character_generator.character_data
            )
            modifiers = game.character_generator.ability_score_system.calculate_modifiers(scores)
            
            game.character_generator.character_data['ability_scores'] = scores
            game.character_generator.character_data['ability_modifiers'] = modifiers
            game.character_generator.guided_completion.stat_assignment_mode = StatAssignmentMode.AUTO
            
            response = f"Perfect! I've assigned your ability scores based on your character's story:\n\n"
            response += game.character_generator.guided_completion.get_ability_score_summary(scores)
            response += "\n\nYour character is ready! Would you like to start your adventure?"
            
        elif assignment_type == 'standard_array':
            # Use SRD 5.2 standard array
            result = game.character_generator.guided_completion.assign_standard_array(
                game.character_generator.character_data
            )
            
            game.character_generator.character_data['ability_scores'] = result['scores']
            game.character_generator.character_data['ability_modifiers'] = result['modifiers']
            game.character_generator.guided_completion.stat_assignment_mode = StatAssignmentMode.STANDARD_ARRAY
            
            response = f"Great! I've assigned the SRD 5.2 standard array:\n\n"
            response += game.character_generator.guided_completion.get_ability_score_summary(result['scores'])
            response += "\n\nYour character is ready! Would you like to start your adventure?"
            
        elif assignment_type == 'point_buy':
            # Use SRD 5.2 point buy system
            result = game.character_generator.guided_completion.assign_point_buy(
                game.character_generator.character_data
            )
            
            game.character_generator.character_data['ability_scores'] = result['scores']
            game.character_generator.character_data['ability_modifiers'] = result['modifiers']
            game.character_generator.guided_completion.stat_assignment_mode = StatAssignmentMode.POINT_BUY
            
            response = f"Excellent! I've assigned scores using the SRD 5.2 point buy system:\n\n"
            response += game.character_generator.guided_completion.get_ability_score_summary(result['scores'])
            response += "\n\nYour character is ready! Would you like to start your adventure?"
            
        elif assignment_type == 'roll':
            # Use 4d6 drop lowest method
            result = game.character_generator.guided_completion.assign_rolled_scores(
                game.character_generator.character_data
            )
            
            game.character_generator.character_data['ability_scores'] = result['scores']
            game.character_generator.character_data['ability_modifiers'] = result['modifiers']
            game.character_generator.guided_completion.stat_assignment_mode = StatAssignmentMode.ROLL_4D6_DROP_LOWEST
            
            response = f"Fantastic! I've rolled your ability scores using 4d6 drop lowest:\n\n"
            response += game.character_generator.guided_completion.get_ability_score_summary(result['scores'])
            response += "\n\nYour character is ready! Would you like to start your adventure?"
            
        elif assignment_type == 'manual':
            # Manual assignment - validate the provided scores
            manual_scores = data.get('scores', {})
            is_valid, error_message = game.character_generator.guided_completion.validate_manual_stats(manual_scores)
            
            if is_valid:
                modifiers = game.character_generator.ability_score_system.calculate_modifiers(manual_scores)
                
                game.character_generator.character_data['ability_scores'] = manual_scores
                game.character_generator.character_data['ability_modifiers'] = modifiers
                game.character_generator.guided_completion.stat_assignment_mode = StatAssignmentMode.MANUAL
                
                response = f"Perfect! Your manually assigned ability scores are valid:\n\n"
                response += game.character_generator.guided_completion.get_ability_score_summary(manual_scores)
                response += "\n\nYour character is ready! Would you like to start your adventure?"
            else:
                response = f"❌ Invalid ability scores: {error_message}\n\nPlease check your scores and try again."
        
        else:
            response = "❌ Invalid assignment type. Please choose 'auto', 'standard_array', 'point_buy', 'roll', or 'manual'."
        
        return jsonify({
            "success": True,
            "response": response,
            "character_data": game.character_generator.get_character_data()
        })
        
    except Exception as e:
        logger.error(f"❌ Error assigning ability scores: {e}")
        return jsonify({
            "success": False,
            "error": f"Error assigning ability scores: {str(e)}"
        })



@app.route('/api/character/create/ability-scores/validate', methods=['POST'])
def validate_ability_scores():
    """Validate manually entered ability scores."""
    try:
        data = request.get_json()
        scores = data.get('scores', {})
        method = data.get('method', 'manual')
        
        # Convert method string to enum
        method_enum = AbilityScoreMethod.MANUAL
        if method == 'standard_array':
            method_enum = AbilityScoreMethod.STANDARD_ARRAY
        elif method == 'point_buy':
            method_enum = AbilityScoreMethod.POINT_BUY
        elif method == 'roll_4d6_drop_lowest':
            method_enum = AbilityScoreMethod.ROLL_4D6_DROP_LOWEST
        
        is_valid, message = game.character_generator.ability_score_system.validate_scores(scores, method_enum)
        
        if is_valid:
            modifiers = game.character_generator.ability_score_system.calculate_modifiers(scores)
            summary = game.character_generator.guided_completion.get_ability_score_summary(scores)
            
            return jsonify({
                "success": True,
                "valid": True,
                "message": message,
                "modifiers": modifiers,
                "summary": summary
            })
        else:
            return jsonify({
                "success": True,
                "valid": False,
                "message": message
            })
        
    except Exception as e:
        logger.error(f"❌ Error validating ability scores: {e}")
        return jsonify({
            "success": False,
            "error": f"Error validating ability scores: {str(e)}"
        })

@app.route('/api/character/create/ability-scores/current', methods=['GET'])
def get_current_ability_scores():
    """Get current ability scores and modifiers."""
    try:
        scores = game.character_generator.character_data.get('ability_scores', {})
        modifiers = game.character_generator.character_data.get('ability_modifiers', {})
        
        if scores:
            summary = game.character_generator.guided_completion.get_ability_score_summary(scores)
            
            return jsonify({
                "success": True,
                "scores": scores,
                "modifiers": modifiers,
                "summary": summary
            })
        else:
            return jsonify({
                "success": True,
                "scores": None,
                "modifiers": None,
                "summary": "No ability scores assigned yet."
            })
        
    except Exception as e:
        logger.error(f"❌ Error getting current ability scores: {e}")
        return jsonify({
            "success": False,
            "error": f"Error getting current ability scores: {str(e)}"
        })

@app.route('/api/character/create/ability-scores/assign', methods=['POST'])
def assign_ability_scores():
    """Assign ability scores using the specified method."""
    try:
        data = request.get_json()
        method = data.get('method', 'auto')
        
        if method == 'auto':
            # Auto-assign based on character story
            scores = game.character_generator.ability_score_system.assign_auto_based_on_story(
                game.character_generator.character_data
            )
            modifiers = game.character_generator.ability_score_system.calculate_modifiers(scores)
            
            game.character_generator.character_data['ability_scores'] = scores
            game.character_generator.character_data['ability_modifiers'] = modifiers
            
            response = f"Perfect! I've assigned your ability scores based on your character's story:\n\n"
            response += game.character_generator.guided_completion.get_ability_score_summary(scores)
            response += "\n\nYour character is ready! Would you like to start your adventure?"
            
        elif method == 'standard_array':
            # Use SRD 5.2 standard array
            scores = game.character_generator.ability_score_system.assign_standard_array(
                game.character_generator.character_data
            )
            modifiers = game.character_generator.ability_score_system.calculate_modifiers(scores)
            
            game.character_generator.character_data['ability_scores'] = scores
            game.character_generator.character_data['ability_modifiers'] = modifiers
            
            response = f"Great! I've assigned the SRD 5.2 standard array:\n\n"
            response += game.character_generator.guided_completion.get_ability_score_summary(scores)
            response += "\n\nYour character is ready! Would you like to start your adventure?"
            
        elif method == 'point_buy':
            # Use SRD 5.2 point buy system
            scores = game.character_generator.ability_score_system.assign_point_buy(
                game.character_generator.character_data
            )
            modifiers = game.character_generator.ability_score_system.calculate_modifiers(scores)
            
            game.character_generator.character_data['ability_scores'] = scores
            game.character_generator.character_data['ability_modifiers'] = modifiers
            
            response = f"Excellent! I've assigned scores using the SRD 5.2 point buy system:\n\n"
            response += game.character_generator.guided_completion.get_ability_score_summary(scores)
            response += "\n\nYour character is ready! Would you like to start your adventure?"
            
        elif method == 'roll':
            # Use 4d6 drop lowest method
            scores = game.character_generator.ability_score_system.assign_rolled_scores(
                game.character_generator.character_data
            )
            modifiers = game.character_generator.ability_score_system.calculate_modifiers(scores)
            
            game.character_generator.character_data['ability_scores'] = scores
            game.character_generator.character_data['ability_modifiers'] = modifiers
            
            response = f"Fantastic! I've rolled your ability scores using 4d6 drop lowest:\n\n"
            response += game.character_generator.guided_completion.get_ability_score_summary(scores)
            response += "\n\nYour character is ready! Would you like to start your adventure?"
            
        elif method == 'manual':
            # Manual assignment - validate the provided scores
            manual_scores = data.get('scores', {})
            is_valid, error_message = game.character_generator.ability_score_system.validate_scores(
                manual_scores, AbilityScoreMethod.MANUAL
            )
            
            if is_valid:
                modifiers = game.character_generator.ability_score_system.calculate_modifiers(manual_scores)
                
                game.character_generator.character_data['ability_scores'] = manual_scores
                game.character_generator.character_data['ability_modifiers'] = modifiers
                
                response = f"Perfect! Your manually assigned ability scores are valid:\n\n"
                response += game.character_generator.guided_completion.get_ability_score_summary(manual_scores)
                response += "\n\nYour character is ready! Would you like to start your adventure?"
            else:
                response = f"❌ Invalid ability scores: {error_message}\n\nPlease check your scores and try again."
        
        else:
            response = "❌ Invalid assignment type. Please choose 'auto', 'standard_array', 'point_buy', 'roll', or 'manual'."
        
        return jsonify({
            "success": True,
            "response": response,
            "character_data": game.character_generator.get_character_data()
        })
        
    except Exception as e:
        logger.error(f"❌ Error assigning ability scores: {e}")
        return jsonify({
            "success": False,
            "error": f"Error assigning ability scores: {str(e)}"
        })

@app.route('/api/character/create/ability-scores/methods', methods=['GET'])
def get_ability_score_methods():
    """Get available ability score assignment methods."""
    try:
        # Safely get character class, defaulting to 'fighter' if not set
        char_class = game.character_generator.character_data.get('class')
        char_class = (char_class or '')
        
        methods = {
            "auto": {
                "name": "Automatic (Story-Based)",
                "description": "I'll assign scores based on your character's story and personality",
                "recommended": True
            },
            "standard_array": {
                "name": "Standard Array",
                "description": "Use the SRD 5.2 standard array: 15, 14, 13, 12, 10, 8",
                "recommended": False
            },
            "point_buy": {
                "name": "Point Buy",
                "description": "Use the SRD 5.2 point buy system (27 points)",
                "recommended": False
            },
            "roll": {
                "name": "Roll 4d6 Drop Lowest",
                "description": "Roll 4d6 for each ability, drop the lowest die",
                "recommended": False
            },
            "manual": {
                "name": "Manual Entry",
                "description": "Enter your own ability scores",
                "recommended": False
            }
        }
        
        # Add class recommendations
        recommendations = game.character_generator.ability_score_system.get_class_recommendations(char_class)
        
        # Safely format current class
        current_class = 'Unknown'
        if char_class:
            current_class = char_class.title()
        
        return jsonify({
            "success": True,
            "methods": methods,
            "class_recommendations": recommendations,
            "current_class": current_class
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting ability score methods: {e}")
        return jsonify({
            "success": False,
            "error": f"Error getting ability score methods: {str(e)}"
        })

@app.route('/api/character/create/races', methods=['GET'])
def get_available_races():
    """Get available races with their descriptions and bonuses."""
    try:
        races = racial_modifiers.get_available_races()
        
        return jsonify({
            "success": True,
            "races": races
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting available races: {e}")
        return jsonify({
            "success": False,
            "error": f"Error getting available races: {str(e)}"
        })

@app.route('/api/character/create/races/<race_name>', methods=['GET'])
def get_race_info(race_name):
    """Get detailed information about a specific race."""
    try:
        # from utils.racial_modifiers import racial_modifiers  # Removed duplicate import
        race_info = racial_modifiers.get_race_info(race_name)
        if not race_info:
            return jsonify({
                "success": False,
                "error": f"Race '{race_name}' not found"
            })
        
        # Get recommended races for current class
        char_class = game.character_generator.character_data.get('class', '')
        recommended_races = racial_modifiers.get_recommended_races_for_class(char_class)
        
        return jsonify({
            "success": True,
            "race": race_info,
            "recommended_for_class": race_name.lower() in recommended_races,
            "current_class": char_class
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting race info: {e}")
        return jsonify({
            "success": False,
            "error": f"Error getting race info: {str(e)}"
        })

@app.route('/api/character/create/races/<race_name>/subraces', methods=['GET'])
def get_subraces(race_name):
    """Get available subraces for a specific race."""
    try:
        # from utils.racial_modifiers import racial_modifiers  # Removed duplicate import
        race_info = racial_modifiers.get_race_info(race_name)
        if not race_info:
            return jsonify({
                "success": False,
                "error": f"Race '{race_name}' not found"
            })
        
        subraces = []
        for subrace in race_info['subraces']:
            subrace_info = racial_modifiers.get_subrace_info(subrace.lower())
            if subrace_info:
                subraces.append({
                    'name': subrace,
                    'ability_bonuses': {k: v for k, v in subrace_info.items() if k != 'traits'},
                    'traits': subrace_info.get('traits', [])
                })
        
        return jsonify({
            "success": True,
            "race": race_name,
            "subraces": subraces
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting subraces: {e}")
        return jsonify({
            "success": False,
            "error": f"Error getting subraces: {str(e)}"
        })

@app.route('/api/character/create/ability-scores/assign-with-race', methods=['POST'])
def assign_ability_scores_with_race():
    """Assign ability scores using the specified method and apply racial modifiers."""
    try:
        data = request.get_json()
        method = data.get('method', 'auto')
        race = data.get('race', 'human')
        subrace = data.get('subrace')
        # from utils.racial_modifiers import racial_modifiers  # Removed duplicate import
        if not racial_modifiers.validate_race_subrace_combination(race, subrace):
            return jsonify({
                "success": False,
                "error": f"Invalid race/subrace combination: {race}/{subrace}"
            })
        
        # Assign base scores
        if method == 'auto':
            base_scores = game.character_generator.ability_score_system.assign_auto_based_on_story(
                game.character_generator.character_data
            )
        elif method == 'standard_array':
            base_scores = game.character_generator.ability_score_system.assign_standard_array(
                game.character_generator.character_data
            )
        elif method == 'point_buy':
            base_scores = game.character_generator.ability_score_system.assign_point_buy(
                game.character_generator.character_data
            )
        elif method == 'roll':
            base_scores = game.character_generator.ability_score_system.assign_rolled_scores(
                game.character_generator.character_data
            )
        elif method == 'manual':
            base_scores = data.get('scores', {})
            is_valid, error_message = game.character_generator.ability_score_system.validate_scores(
                base_scores, AbilityScoreMethod.MANUAL
            )
            if not is_valid:
                return jsonify({
                    "success": False,
                    "error": f"Invalid manual scores: {error_message}"
                })
        else:
            return jsonify({
                "success": False,
                "error": "Invalid assignment method"
            })
        
        # Apply racial modifiers
        final_scores = game.character_generator.ability_score_system.apply_racial_modifiers(
            base_scores, race, subrace
        )
        
        # Calculate modifiers
        modifiers = game.character_generator.ability_score_system.calculate_modifiers(final_scores)
        
        # Store in character data
        game.character_generator.character_data['ability_scores'] = final_scores
        game.character_generator.character_data['ability_modifiers'] = modifiers
        game.character_generator.character_data['race'] = race
        if subrace:
            game.character_generator.character_data['subrace'] = subrace
        
        # Get racial summary
        racial_summary = game.character_generator.ability_score_system.get_racial_summary(race, subrace)
        
        # Format response
        response = f"Perfect! I've assigned your ability scores using {method.replace('_', ' ').title()} and applied {race.title()}"
        if subrace:
            response += f" ({subrace.title()})"
        response += " racial modifiers:\n\n"
        
        response += game.character_generator.guided_completion.get_ability_score_summary(final_scores)
        response += f"\n\n{racial_summary}\n\nYour character is ready! Would you like to start your adventure?"
        
        return jsonify({
            "success": True,
            "response": response,
            "character_data": game.character_generator.get_character_data(),
            "base_scores": base_scores,
            "racial_bonuses": {
                ability: final_scores[ability] - base_scores[ability]
                for ability in final_scores
                if final_scores[ability] != base_scores[ability]
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error assigning ability scores with race: {e}")
        return jsonify({
            "success": False,
            "error": f"Error assigning ability scores with race: {str(e)}"
        })

@app.route('/api/character/create/races/recommendations', methods=['GET'])
def get_race_recommendations():
    """Get race recommendations based on current character class."""
    try:
        # from utils.racial_modifiers import racial_modifiers  # Removed duplicate import
        char_class = game.character_generator.character_data.get('class', '')
        recommended_races = racial_modifiers.get_recommended_races_for_class(char_class)
        
        # Get detailed info for recommended races
        race_details = {}
        for race in recommended_races:
            race_info = racial_modifiers.get_race_info(race)
            if race_info:
                race_details[race] = {
                    'name': race_info['name'],
                    'description': race_info['description'],
                    'ability_bonuses': race_info['ability_bonuses']
                }
        
        return jsonify({
            "success": True,
            "current_class": char_class,
            "recommended_races": recommended_races,
            "race_details": race_details
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting race recommendations: {e}")
        return jsonify({
            "success": False,
            "error": f"Error getting race recommendations: {str(e)}"
        })

@app.route('/api/narrative/ending', methods=['POST'])
def detect_narrative_ending():
    """Detect if narrative has reached a cinematic ending point."""
    try:
        data = request.get_json()
        goals = data.get('goals', [])
        transformation = data.get('transformation', {})
        resolution = data.get('resolution', {})
        world_state = data.get('world_state', {})
        
        # Initialize TNE Demo Engine for ending detection
        try:
            from narrative_engine_integration import TNEDemoEngine
            campaign_id = session.get('campaign_id', 'default')
            tne_engine = TNEDemoEngine(campaign_id=campaign_id)
            
            # Detect ending using TNE
            ending = tne_engine.detect_narrative_ending(
                goals=goals,
                transformation=transformation,
                resolution=resolution,
                world_state=world_state
            )
            
            return jsonify({
                'success': True,
                'ending': ending
            })
            
        except ImportError:
            # Fallback ending detection
            logger.warning("TNE integration not available, using fallback ending detection")
            fallback_ending = detect_fallback_ending(goals, transformation, resolution, world_state)
            return jsonify({
                'success': True,
                'ending': fallback_ending
            })
    
    except Exception as e:
        logger.error(f"Error detecting narrative ending: {e}")
        return jsonify({'success': False, 'message': 'Error detecting ending'})

def detect_fallback_ending(goals, transformation, resolution, world_state):
    # Analyze goals for completion
    completed_goals = sum(1 for goal in goals if goal.get('confidence', 0) > 0.8)
    total_goals = len(goals) if goals else 1
    goal_completion_rate = completed_goals / total_goals if total_goals > 0 else 0
    # Analyze transformation progress
    transformation_confidence = transformation.get('confidence_score', 0) if transformation else 0
    # Analyze resolution state
    resolution_progress = resolution.get('progress', 0) if resolution else 0
    resolution_state = resolution.get('resolution_state', 'early') if resolution else 'early'
    # Analyze world state for story completion
    story_flags = world_state.get('story_flags', {})
    completed_flags = sum(1 for flag, value in story_flags.items() if value is True)
    total_flags = len(story_flags) if story_flags else 1
    flag_completion_rate = completed_flags / total_flags if total_flags > 0 else 0
    # Calculate overall completion score
    completion_score = (goal_completion_rate + transformation_confidence + resolution_progress + flag_completion_rate) / 4
    # Determine if ending should be triggered
    ending_triggered = completion_score > 0.75 and resolution_state in ['climax', 'denouement']
    if not ending_triggered:
        return {
            'ending_triggered': False,
            'ending_type': None,
            'justification': f"Story completion at {completion_score:.1%}, not ready for ending",
            'confidence': completion_score
        }
    # Determine ending type based on narrative elements
    ending_type = determine_ending_type(goals, transformation, world_state)
    return {
        'ending_triggered': True,
        'ending_type': ending_type,
        'justification': f"Story completion at {completion_score:.1%}, {ending_type} ending triggered",
        'confidence': completion_score
    }

def determine_ending_type(goals, transformation, world_state):
    goal_types = [goal.get('type', '').lower() for goal in goals]
    transformation_type = transformation.get('transformation_type', '').lower() if transformation else ''
    story_flags = world_state.get('story_flags', {})
    if 'sacrifice' in goal_types or 'sacrifice' in transformation_type:
        return 'sacrifice'
    elif 'redemption' in goal_types or 'redemption' in transformation_type:
        return 'redemption'
    elif 'rebirth' in goal_types or 'rebirth' in transformation_type:
        return 'rebirth'
    elif any(flag for flag, value in story_flags.items() if 'tragic' in flag.lower() or 'loss' in flag.lower()):
        return 'tragedy'
    elif any(flag for flag, value in story_flags.items() if 'victory' in flag.lower() or 'triumph' in flag.lower()):
        return 'triumph'
    else:
        return 'bittersweet'

@app.route('/api/narrative/epilogue', methods=['POST'])
def generate_narrative_epilogue():
    """Generate epilogue based on completed narrative."""
    try:
        data = request.get_json()
        memory_log = data.get('memory_log', [])
        goals_achieved = data.get('goals_achieved', [])
        character_stats = data.get('character_stats', {})
        transformation_path = data.get('transformation_path', {})
        world_state_flags = data.get('world_state_flags', {})
        ending_type = data.get('ending_type', 'bittersweet')
        # Initialize TNE Demo Engine for epilogue generation
        try:
            from narrative_engine_integration import TNEDemoEngine
            campaign_id = session.get('campaign_id', 'default')
            tne_engine = TNEDemoEngine(campaign_id=campaign_id)
            epilogue = tne_engine.generate_narrative_epilogue(
                memory_log=memory_log,
                goals_achieved=goals_achieved,
                character_stats=character_stats,
                transformation_path=transformation_path,
                world_state_flags=world_state_flags,
                ending_type=ending_type
            )
            return jsonify({
                'success': True,
                'epilogue': epilogue
            })
        except ImportError:
            logger.warning("TNE integration not available, using fallback epilogue generation")
            fallback_epilogue = generate_fallback_epilogue(memory_log, goals_achieved, character_stats, transformation_path, world_state_flags, ending_type)
            return jsonify({
                'success': True,
                'epilogue': fallback_epilogue
            })
    except Exception as e:
        logger.error(f"Error generating narrative epilogue: {e}")
        return jsonify({'success': False, 'message': 'Error generating epilogue'})

def generate_fallback_epilogue(memory_log, goals_achieved, character_stats, transformation_path, world_state_flags, ending_type):
    character_name = character_stats.get('name', 'The Hero')
    character_level = character_stats.get('level', 1)
    transformation_type = transformation_path.get('transformation_type', 'Unknown')
    epilogue_text = generate_ending_specific_epilogue(ending_type, character_name, transformation_type, goals_achieved, world_state_flags)
    epilogue_theme = determine_epilogue_theme(ending_type, transformation_type)
    epilogue_quotes = generate_epilogue_quotes(ending_type, transformation_type)
    return {
        'epilogue_text': epilogue_text,
        'epilogue_theme': epilogue_theme,
        'epilogue_quotes': epilogue_quotes
    }

def generate_ending_specific_epilogue(ending_type, character_name, transformation_type, goals_achieved, world_state_flags):
    if ending_type == 'triumph':
        return f"And so {character_name}'s journey reached its triumphant conclusion. Through trials and tribulations, they had emerged victorious, their transformation from {transformation_type.split(' → ')[0] if ' → ' in transformation_type else 'innocence'} to {transformation_type.split(' → ')[-1] if ' → ' in transformation_type else 'mastery'} complete. The world would remember their deeds, and their legend would inspire generations to come."
    elif ending_type == 'tragedy':
        return f"In the end, {character_name}'s path led to tragedy. Despite their transformation from {transformation_type.split(' → ')[0] if ' → ' in transformation_type else 'hope'} to {transformation_type.split(' → ')[-1] if ' → ' in transformation_type else 'despair'}, the cost was too great. Their story serves as a cautionary tale, a reminder that not all journeys end in victory."
    elif ending_type == 'rebirth':
        return f"Through the crucible of their adventures, {character_name} experienced a profound rebirth. Their transformation from {transformation_type.split(' → ')[0] if ' → ' in transformation_type else 'old self'} to {transformation_type.split(' → ')[-1] if ' → ' in transformation_type else 'new self'} was not just physical, but spiritual. They emerged from their trials fundamentally changed, ready to face whatever the future held."
    elif ending_type == 'sacrifice':
        return f"{character_name} chose the path of sacrifice, giving up everything for the greater good. Their transformation from {transformation_type.split(' → ')[0] if ' → ' in transformation_type else 'selfishness'} to {transformation_type.split(' → ')[-1] if ' → ' in transformation_type else 'selflessness'} was complete. Though they may be gone, their sacrifice ensures that others may live and prosper."
    elif ending_type == 'redemption':
        return f"{character_name} found redemption through their journey. Their transformation from {transformation_type.split(' → ')[0] if ' → ' in transformation_type else 'darkness'} to {transformation_type.split(' → ')[-1] if ' → ' in transformation_type else 'light'} was hard-won, but ultimately successful. They proved that even the most fallen can rise again, given the chance and the will to change."
    else:
        return f"{character_name}'s journey ended in bittersweet fashion. Their transformation from {transformation_type.split(' → ')[0] if ' → ' in transformation_type else 'innocence'} to {transformation_type.split(' → ')[-1] if ' → ' in transformation_type else 'experience'} brought both victory and loss. They achieved their goals, but at a cost that would forever change them. Such is the nature of true adventure."

def determine_epilogue_theme(ending_type, transformation_type):
    themes = {
        'triumph': 'Victory and Legacy',
        'tragedy': 'Loss and Remembrance',
        'rebirth': 'Transformation and Renewal',
        'sacrifice': 'Selflessness and Honor',
        'redemption': 'Forgiveness and Growth',
        'bittersweet': 'Balance and Wisdom'
    }
    return themes.get(ending_type, 'Journey and Change')

def generate_epilogue_quotes(ending_type, transformation_type):
    quotes = {
        'triumph': [
            "The greatest glory in living lies not in never falling, but in rising every time we fall.",
            "Heroes are made by the paths they choose, not the powers they are graced with."
        ],
        'tragedy': [
            "Sometimes the greatest tragedies are those that teach us the most profound lessons.",
            "In loss, we find the strength we never knew we had."
        ],
        'rebirth': [
            "Every ending is a new beginning.",
            "The only way to make sense out of change is to plunge into it, move with it, and join the dance."
        ],
        'sacrifice': [
            "The true measure of a hero is not how they live, but how they die.",
            "Greater love has no one than this: to lay down one's life for one's friends."
        ],
        'redemption': [
            "It is never too late to be what you might have been.",
            "The past is not a prison, but a foundation for the future."
        ],
        'bittersweet': [
            "Life is not about waiting for the storm to pass, but learning to dance in the rain.",
            "The beauty of life lies not in its perfection, but in its imperfection."
        ]
    }
    return quotes.get(ending_type, ["Every journey changes the traveler."])

@app.route('/api/archive/finalize', methods=['POST'])
def finalize_campaign_archive():
    """Save final state when ending is triggered."""
    try:
        data = request.get_json()
        campaign_id = session.get('campaign_id', 'default')
        character_data = data.get('character_data', {})
        world_state = data.get('world_state', {})
        goals = data.get('goals', [])
        transformation = data.get('transformation', {})
        ending_summary = data.get('ending_summary', {})
        
        # Create archive directory structure
        archive_dir = os.path.join('campaigns', campaign_id, 'archive')
        os.makedirs(archive_dir, exist_ok=True)
        
        # Generate timestamp for archive file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_filename = f"{timestamp}_final_state.json"
        archive_path = os.path.join(archive_dir, archive_filename)
        
        # Prepare final state data
        final_state = {
            'campaign_id': campaign_id,
            'timestamp': datetime.now().isoformat(),
            'character_data': character_data,
            'world_state': world_state,
            'goals': goals,
            'transformation': transformation,
            'ending_summary': ending_summary,
            'archive_version': '1.0'
        }
        
        # Save to archive file
        with open(archive_path, 'w') as f:
            json.dump(final_state, f, indent=2)
        
        # Log ending to endings.json
        endings_file = os.path.join('campaigns', campaign_id, 'endings.json')
        endings_data = []
        
        if os.path.exists(endings_file):
            try:
                with open(endings_file, 'r') as f:
                    endings_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                endings_data = []
        
        # Add new ending record
        ending_record = {
            'timestamp': datetime.now().isoformat(),
            'ending_type': ending_summary.get('ending_type', 'unknown'),
            'justification': ending_summary.get('justification', ''),
            'goal_states': [goal.get('state', 'unknown') for goal in goals],
            'transformation_arc': transformation.get('transformation_type', 'unknown'),
            'archive_file': archive_filename,
            'character_name': character_data.get('name', 'Unknown')
        }
        
        endings_data.append(ending_record)
        
        # Save endings log
        with open(endings_file, 'w') as f:
            json.dump(endings_data, f, indent=2)
        
        logger.info(f"✅ Campaign finalized and archived: {archive_filename}")
        
        return jsonify({
            'success': True,
            'archive_file': archive_filename,
            'message': 'Campaign finalized and archived successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Error finalizing campaign archive: {e}")
        return jsonify({
            'success': False,
            'error': f'Error finalizing archive: {str(e)}'
        })

@app.route('/api/archive/list', methods=['GET'])
def list_archives():
    """List all available archives."""
    try:
        campaign_id = session.get('campaign_id', 'default')
        archive_dir = os.path.join('campaigns', campaign_id, 'archive')
        
        archives = []
        
        if os.path.exists(archive_dir):
            for filename in os.listdir(archive_dir):
                if filename.endswith('_final_state.json'):
                    file_path = os.path.join(archive_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            archive_data = json.load(f)
                        
                        # Extract summary information
                        archive_summary = {
                            'filename': filename,
                            'timestamp': archive_data.get('timestamp', ''),
                            'character_name': archive_data.get('character_data', {}).get('name', 'Unknown'),
                            'ending_type': archive_data.get('ending_summary', {}).get('ending_type', 'unknown'),
                            'campaign_id': archive_data.get('campaign_id', campaign_id)
                        }
                        archives.append(archive_summary)
                        
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Error reading archive file {filename}: {e}")
                        continue
        
        # Sort by timestamp (newest first)
        archives.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'archives': archives
        })
        
    except Exception as e:
        logger.error(f"❌ Error listing archives: {e}")
        return jsonify({
            'success': False,
            'error': f'Error listing archives: {str(e)}'
        })

@app.route('/api/archive/load', methods=['GET'])
def load_archive():
    """Load a specific archive file."""
    try:
        filename = request.args.get('file')
        if not filename:
            return jsonify({
                'success': False,
                'error': 'Filename parameter required'
            })
        
        campaign_id = session.get('campaign_id', 'default')
        archive_path = os.path.join('campaigns', campaign_id, 'archive', filename)
        
        if not os.path.exists(archive_path):
            return jsonify({
                'success': False,
                'error': 'Archive file not found'
            })
        
        with open(archive_path, 'r') as f:
            archive_data = json.load(f)
        
        return jsonify({
            'success': True,
            'archive_data': archive_data
        })
        
    except Exception as e:
        logger.error(f"❌ Error loading archive: {e}")
        return jsonify({
            'success': False,
            'error': f'Error loading archive: {str(e)}'
        })

@app.route('/api/archive/delete', methods=['POST'])
def delete_archive():
    """Delete a specific archive file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'Filename parameter required'
            })
        
        campaign_id = session.get('campaign_id', 'default')
        archive_path = os.path.join('campaigns', campaign_id, 'archive', filename)
        
        if not os.path.exists(archive_path):
            return jsonify({
                'success': False,
                'error': 'Archive file not found'
            })
        
        os.remove(archive_path)
        logger.info(f"✅ Deleted archive: {filename}")
        
        return jsonify({
            'success': True,
            'message': 'Archive deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Error deleting archive: {e}")
        return jsonify({
            'success': False,
            'error': f'Error deleting archive: {str(e)}'
        })

@app.route('/api/campaign/newgameplus', methods=['POST'])
def create_new_game_plus():
    """Create a new game+ with legacy elements."""
    try:
        data = request.get_json()
        legacy_options = data.get('legacy_options', {})
        carry_memories = legacy_options.get('memories', False)
        carry_stat_bonuses = legacy_options.get('stat_bonuses', False)
        carry_items = legacy_options.get('items', False)
        
        # Get current campaign data
        campaign_id = session.get('campaign_id', 'default')
        current_character = session.get('character_data', {})
        current_world_state = session.get('world_state', {})
        
        # Create new campaign ID
        new_campaign_id = f"{campaign_id}_ngp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create new character with legacy tags
        new_character = current_character.copy()
        new_character['from_campaign_id'] = campaign_id
        new_character['legacy_tags'] = []
        
        # Apply legacy options
        if carry_memories:
            new_character['legacy_tags'].append('memories')
            # Add memory fragments to character background
            memory_fragments = [
                "Fragments of past adventures echo in their mind",
                "Ancient wisdom from previous journeys guides their path",
                "The weight of past choices shapes their destiny"
            ]
            new_character['background'] = f"{new_character.get('background', '')} {random.choice(memory_fragments)}"
        
        if carry_stat_bonuses:
            new_character['legacy_tags'].append('stat_bonuses')
            # Add small stat bonuses
            for ability in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
                if ability in new_character.get('ability_scores', {}):
                    new_character['ability_scores'][ability] += 1
        
        if carry_items:
            new_character['legacy_tags'].append('items')
            # Add legacy items
            legacy_items = [
                "A mysterious artifact from a previous life",
                "A weapon that remembers its wielder",
                "A talisman of forgotten power"
            ]
            current_items = new_character.get('equipment', [])
            current_items.extend(legacy_items)
            new_character['equipment'] = current_items
        
        # Create new campaign directory
        new_campaign_dir = os.path.join('campaigns', new_campaign_id)
        os.makedirs(new_campaign_dir, exist_ok=True)
        
        # Save new character
        character_file = os.path.join(new_campaign_dir, 'character.json')
        with open(character_file, 'w') as f:
            json.dump(new_character, f, indent=2)
        
        # Create new world state with legacy elements
        new_world_state = {
            'location': 'A realm touched by echoes of past adventures',
            'items': [],
            'npc_flags': {},
            'story_flags': {
                'legacy_campaign': True,
                'echoes_of_past': True
            }
        }
        
        if carry_items:
            new_world_state['items'].append('Ancient relics scattered throughout the land')
        
        # Save new world state
        world_state_file = os.path.join(new_campaign_dir, 'world_state.json')
        with open(world_state_file, 'w') as f:
            json.dump(new_world_state, f, indent=2)
        
        # Update session with new campaign
        session['campaign_id'] = new_campaign_id
        session['character_data'] = new_character
        session['world_state'] = new_world_state
        
        logger.info(f"✅ Created New Game+: {new_campaign_id}")
        
        return jsonify({
            'success': True,
            'new_campaign_id': new_campaign_id,
            'character_data': new_character,
            'world_state': new_world_state,
            'legacy_options': legacy_options
        })
        
    except Exception as e:
        logger.error(f"❌ Error creating New Game+: {e}")
        return jsonify({
            'success': False,
            'error': f'Error creating New Game+: {str(e)}'
        })

@app.route('/api/archive/endings', methods=['GET'])
def get_ending_history():
    """Get ending history for current campaign."""
    try:
        campaign_id = session.get('campaign_id', 'default')
        endings_file = os.path.join('campaigns', campaign_id, 'endings.json')
        
        endings_data = []
        if os.path.exists(endings_file):
            try:
                with open(endings_file, 'r') as f:
                    endings_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                endings_data = []
        
        return jsonify({
            'success': True,
            'endings': endings_data
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting ending history: {e}")
        return jsonify({
            'success': False,
            'error': f'Error getting ending history: {str(e)}'
        })

@app.route('/archives')
def archives_page():
    """Archive browser page."""
    return render_template('archives.html')

@app.route('/archives/<campaign_id>')
def campaign_archives(campaign_id):
    """Campaign-specific archives page."""
    return render_template('campaign_archives.html', campaign_id=campaign_id)

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all available gameplay/character creation sessions."""
    try:
        session_dir = os.path.join('logs', 'character_creation_sessions')
        sessions = []
        for file in glob.glob(os.path.join(session_dir, '*.jsonl')):
            try:
                with open(file, 'r') as f:
                    lines = f.readlines()
                    if not lines:
                        continue
                    # Use first line for metadata
                    first_event = json.loads(lines[0])
                    session_id = os.path.splitext(os.path.basename(file))[0]
                    name = first_event.get('character_data', {}).get('name') or first_event.get('description', 'Unnamed Session')
                    created = first_event.get('timestamp') or first_event.get('created', '')
                    last_updated = first_event.get('last_updated', created)
                    campaign = first_event.get('campaign_name', 'Unknown')
                    sessions.append({
                        'session_id': session_id,
                        'name': name,
                        'created': created,
                        'last_updated': last_updated,
                        'campaign': campaign,
                        'filename': os.path.basename(file)
                    })
            except Exception as e:
                logger.warning(f"Error reading session file {file}: {e}")
                continue
        # Sort by last_updated or created
        sessions.sort(key=lambda x: x.get('last_updated', x.get('created', '')), reverse=True)
        return jsonify({'success': True, 'sessions': sessions})
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sessions/load', methods=['GET', 'POST'])
def load_session():
    """Load a specific session log file."""
    try:
        # Support both GET (query param) and POST (JSON body)
        if request.method == 'GET':
            session_id = request.args.get('session_id')
        else:
            data = request.get_json()
            session_id = data.get('session_id')
            
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id required'})
            
        session_file = os.path.join('logs', 'character_creation_sessions', f'{session_id}.jsonl')
        if not os.path.exists(session_file):
            return jsonify({'success': False, 'error': 'Session file not found'})
            
        with open(session_file, 'r') as f:
            lines = f.readlines()
            events = [json.loads(line) for line in lines]
            
        return jsonify({'success': True, 'events': events})
    except Exception as e:
        logger.error(f"Error loading session: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sessions/delete', methods=['POST'])
def delete_session():
    """Delete a specific session log file."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id required'})
        session_file = os.path.join('logs', 'character_creation_sessions', f'{session_id}.jsonl')
        if not os.path.exists(session_file):
            return jsonify({'success': False, 'error': 'Session file not found'})
        os.remove(session_file)
        logger.info(f"Deleted session: {session_id}")
        return jsonify({'success': True, 'message': 'Session deleted'})
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sessions/rename', methods=['POST'])
def rename_session():
    """Rename a session (update the name in the first event)."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        new_name = data.get('new_name')
        if not session_id or not new_name:
            return jsonify({'success': False, 'error': 'session_id and new_name required'})
        session_file = os.path.join('logs', 'character_creation_sessions', f'{session_id}.jsonl')
        if not os.path.exists(session_file):
            return jsonify({'success': False, 'error': 'Session file not found'})
        with open(session_file, 'r') as f:
            lines = f.readlines()
        if not lines:
            return jsonify({'success': False, 'error': 'Session file is empty'})
        first_event = json.loads(lines[0])
        if 'character_data' in first_event:
            first_event['character_data']['name'] = new_name
        else:
            first_event['description'] = new_name
        lines[0] = json.dumps(first_event) + '\n'
        with open(session_file, 'w') as f:
            f.writelines(lines)
        logger.info(f"Renamed session {session_id} to {new_name}")
        return jsonify({'success': True, 'message': 'Session renamed'})
    except Exception as e:
        logger.error(f"Error renaming session: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/confrontations')
def get_confrontation_logs():
    """Get confrontation logs for the current campaign."""
    try:
        campaign_id = session.get('campaign_id')
        if not campaign_id:
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        # Proxy to The Narrative Engine API
        import requests
        try:
            # Assuming TNE API is running on port 8000
            response = requests.get(f'http://localhost:8000/campaign/{campaign_id}/confrontations')
            if response.status_code == 200:
                data = response.json()
                return jsonify({
                    'success': True,
                    'confrontations': data.get('confrontations', []),
                    'total_count': data.get('total_count', 0)
                })
            else:
                logger.warning(f"TNE API returned status {response.status_code}")
                return jsonify({
                    'success': True,
                    'confrontations': [],
                    'total_count': 0
                })
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not connect to TNE API: {e}")
            return jsonify({
                'success': True,
                'confrontations': [],
                'total_count': 0
            })
        
    except Exception as e:
        logger.error(f"Error getting confrontation logs: {e}")
        return jsonify({'success': False, 'message': 'Error retrieving confrontation logs'})

if __name__ == '__main__':
    print("🎲 Starting The Narrative Engine D&D Demo...")
    print("Access the demo at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5001, debug=False)
