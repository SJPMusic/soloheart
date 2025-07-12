#!/usr/bin/env python3
"""
The Narrative Engine D&D Demo - TNE Integration

This module integrates The Narrative Engine (TNE) for symbolic processing visualization
and memory flow display. It provides structured, relevant context for maintaining
narrative coherence and continuity through symbolic analysis and memory management.

The integration follows TNE's symbolic processing principles:
- Archetype detection and pattern recognition
- Symbolic reasoning and insight generation
- Memory-driven continuity with layered decay
- Domain-agnostic architecture with clean modular boundaries
"""

import json
import logging
import os
import sys
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the narrative_core to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'narrative_core'))

try:
    from narrative_engine import (
        NarrativeEngine, MemoryType, MemoryLayer, EmotionalContext, 
        NarrativeTheme, Character, WorldState
    )
    logger = logging.getLogger(__name__)
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import Narrative Engine components: {e}")
    logger.error("Make sure the narrative_core directory is properly set up")
    raise

class TNEDemoEngine:
    """
    TNE Demo integration for symbolic processing visualization and memory flow display.
    Provides campaign context, character tracking, and memory surfacing for LLM providers.
    
    This integration treats TNE as a symbolic processing system that feeds structured,
    meaningful data to LLM providers, while maintaining clean modular boundaries.
    """
    
    def __init__(self, campaign_id: str = "default"):
        self.campaign_id = campaign_id
        self.engine = NarrativeEngine(campaign_id=campaign_id, data_dir="narrative_data")
        self.session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🔧 Initialized TNE Demo Engine for campaign: {campaign_id}")
    
    def record_character_creation(self, character_data: Dict[str, Any]) -> str:
        """
        Record character creation in the Narrative Engine.
        Returns campaign context for Ollama.
        """
        # --- Universal Character Fields (domain-agnostic) ---
        UNIVERSAL_FIELDS = {
            'id', 'name', 'description', 'traits', 'goals', 'conflicts', 'relationships',
            'development_arc', 'personality_matrix', 'emotional_state', 'memory_ids', 'last_updated'
        }
        
        # --- Domain-Agnostic Character Data ---
        narrative_char_data = {}
        
        # Generate ID for the character
        narrative_char_data['id'] = str(uuid.uuid4())
        
        # Only include universal fields at the top level
        for field in UNIVERSAL_FIELDS:
            if field in character_data:
                narrative_char_data[field] = character_data[field]
        
        # Set universal character properties
        narrative_char_data['name'] = character_data.get('name', 'Unknown')
        narrative_char_data['description'] = character_data.get('description', 'A character')
        narrative_char_data['traits'] = character_data.get('traits', [])
        narrative_char_data['goals'] = character_data.get('motivations', [])
        narrative_char_data['conflicts'] = character_data.get('traumas', [])
        
        # --- Domain-Specific Data Encapsulation ---
        # ALL game-specific fields go in current_state
        current_state = dict(character_data.get('current_state', {}))
        
        # Move all domain-specific fields to current_state
        domain_specific_fields = [
            'race', 'class', 'background', 'alignment', 'age', 'gender',
            'level', 'hit_points', 'armor_class', 'initiative', 'experience',
            'combat_style', 'gear', 'spells', 'abilities', 'skills',
            'personality_traits', 'motivations', 'emotional_themes', 'traumas',
            'relational_history', 'backstory', 'inspiration_points', 'saving_throws'
        ]
        
        for field in domain_specific_fields:
            if field in character_data:
                current_state[field] = character_data[field]
        
        # Also move any other fields not in UNIVERSAL_FIELDS
        for k, v in character_data.items():
            if k not in UNIVERSAL_FIELDS and k not in domain_specific_fields:
                current_state[k] = v
        
        narrative_char_data['current_state'] = current_state
        
        # Set universal metadata
        narrative_char_data['session_id'] = self.session_id
        
        # Remove user_id from character data since Character class doesn't accept it
        if 'user_id' in narrative_char_data:
            del narrative_char_data['user_id']
        
        # Add character to engine with properly filtered data
        char_id = self.engine.add_character(narrative_char_data)
        # Record character creation as memory with emotional and thematic context
        emotional_context = self._analyze_emotional_context_from_character(character_data)
        narrative_themes = self._extract_narrative_themes_from_character(character_data)
        self.engine.add_memory(
            content={
                'action': 'character_creation_started',
                'character_name': character_data.get('name', 'Unknown'),
                'character_data': character_data,
                'summary': f"Character creation started for {character_data.get('name', 'Unknown')}"
            },
            memory_type=MemoryType.CHARACTER_DEVELOPMENT,
            layer=MemoryLayer.MID_TERM,
            user_id='player',
            session_id=self.session_id,
            emotional_weight=0.4,
            emotional_context=emotional_context,
            narrative_themes=narrative_themes,
            thematic_tags=['character_creation', 'development'],
            triggers=['character', 'creation', character_data.get('name', '').lower()]
        )
        logger.info(f"✅ Recorded character creation: {character_data.get('name', 'Unknown')}")
        return char_id
    
    def record_player_action(self, user_input: str, context: Dict[str, Any]) -> str:
        """
        Record a player action in the Narrative Engine.
        Returns campaign context for Ollama.
        """
        # Determine emotional context from input
        emotional_context = self._analyze_emotional_context(user_input)
        narrative_themes = self._extract_narrative_themes(user_input)
        thematic_tags = self._extract_thematic_tags(user_input)
        
        # Record the action
        memory_id = self.engine.add_memory(
            content={
                'action': 'player_input',
                'user_input': user_input,
                'context': context,
                'summary': f"Player action: {user_input[:100]}..."
            },
            memory_type=MemoryType.EVENT,
            layer=MemoryLayer.SHORT_TERM,
            user_id=context.get('user_id', 'player'),
            session_id=self.session_id,
            emotional_weight=0.3,
            emotional_context=emotional_context,
            narrative_themes=narrative_themes,
            thematic_tags=thematic_tags,
            triggers=self._extract_triggers(user_input)
        )
        
        logger.debug(f"📝 Recorded player action: {user_input[:50]}...")
        return memory_id
    
    def record_character_facts(self, facts: Dict[str, Any], character_name: str) -> str:
        """
        Record character facts in the Narrative Engine.
        """
        # Use the same domain-agnostic filtering as in record_character_creation
        UNIVERSAL_FIELDS = {
            'id', 'name', 'description', 'traits', 'goals', 'conflicts', 'relationships',
            'development_arc', 'personality_matrix', 'emotional_state', 'memory_ids', 'last_updated'
        }
        
        char_data = {'name': character_name}
        
        # Only include universal fields at the top level
        for field in UNIVERSAL_FIELDS:
            if field in facts:
                char_data[field] = facts[field]
        
        # Move all domain-specific fields to current_state
        domain_specific_fields = [
            'race', 'class', 'background', 'alignment', 'age', 'gender',
            'level', 'hit_points', 'armor_class', 'initiative', 'experience',
            'combat_style', 'gear', 'spells', 'abilities', 'skills',
            'personality_traits', 'motivations', 'emotional_themes', 'traumas',
            'relational_history', 'backstory', 'inspiration_points', 'saving_throws'
        ]
        
        current_state = dict(char_data.get('current_state', {}))
        
        for field in domain_specific_fields:
            if field in facts:
                current_state[field] = facts[field]
        
        # Also move any other fields not in UNIVERSAL_FIELDS
        for k, v in facts.items():
            if k not in UNIVERSAL_FIELDS and k not in domain_specific_fields:
                current_state[k] = v
        
        char_data['current_state'] = current_state
        char_data['session_id'] = self.session_id
        
        # Remove user_id from character data since Character class doesn't accept it
        if 'user_id' in char_data:
            del char_data['user_id']
        
        char_id = self.engine.add_character(char_data)
        # Record fact discovery with emotional and thematic context
        emotional_context = self._analyze_emotional_context_from_facts(facts)
        narrative_themes = self._extract_narrative_themes_from_facts(facts)
        memory_id = self.engine.add_memory(
            content={
                'action': 'character_facts_discovered',
                'character_name': character_name,
                'facts': facts,
                'summary': f"Discovered facts about {character_name}: {list(facts.keys())}"
            },
            memory_type=MemoryType.CHARACTER_DEVELOPMENT,
            layer=MemoryLayer.MID_TERM,
            user_id='player',
            session_id=self.session_id,
            emotional_weight=0.4,
            emotional_context=emotional_context,
            narrative_themes=narrative_themes,
            thematic_tags=['character_development', 'fact_discovery'],
            triggers=[character_name.lower(), 'character', 'facts']
        )
        logger.info(f"✅ Recorded character facts for {character_name}: {list(facts.keys())}")
        return memory_id
    
    def record_character_development(self, character_name: str, development_data: Dict[str, Any]) -> str:
        """
        Record character development moments in the Narrative Engine.
        """
        emotional_context = self._analyze_emotional_context_from_development(development_data)
        narrative_themes = self._extract_narrative_themes_from_development(development_data)
        
        memory_id = self.engine.add_memory(
            content={
                'action': 'character_development',
                'character_name': character_name,
                'development_data': development_data,
                'summary': f"Character development for {character_name}: {development_data.get('type', 'unknown')}"
            },
            memory_type=MemoryType.CHARACTER_DEVELOPMENT,
            layer=MemoryLayer.MID_TERM,
            user_id='player',
            session_id=self.session_id,
            emotional_weight=0.5,
            emotional_context=emotional_context,
            narrative_themes=narrative_themes,
            thematic_tags=['character_development', 'growth'],
            triggers=[character_name.lower(), 'development', 'character']
        )
        
        logger.info(f"📈 Recorded character development for {character_name}")
        return memory_id
    
    def record_world_event(self, event_data: Dict[str, Any]) -> str:
        """
        Record world events in the Narrative Engine.
        """
        emotional_context = self._analyze_emotional_context_from_event(event_data)
        narrative_themes = self._extract_narrative_themes_from_event(event_data)
        
        memory_id = self.engine.add_memory(
            content={
                'action': 'world_event',
                'event_data': event_data,
                'summary': f"World event: {event_data.get('description', 'unknown event')}"
            },
            memory_type=MemoryType.WORLD_STATE,
            layer=MemoryLayer.LONG_TERM,
            user_id='player',
            session_id=self.session_id,
            emotional_weight=0.4,
            emotional_context=emotional_context,
            narrative_themes=narrative_themes,
            thematic_tags=['world_event', 'campaign'],
            triggers=self._extract_triggers_from_event(event_data)
        )
        
        # Update world state
        self.engine.update_world_state({'world_events': [event_data]})
        
        logger.info(f"🌍 Recorded world event: {event_data.get('description', 'unknown')}")
        return memory_id
    
    def get_campaign_context(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get structured campaign context for Ollama.
        """
        return self.engine.get_context_for_llm(
            user_id=user_id, 
            session_id=self.session_id,
            include_characters=True,
            include_world_state=True
        )
    
    def get_memory_context_for_ollama(self, user_id: str = None, max_memories: int = 15) -> str:
        """
        Get memory context formatted specifically for Ollama consumption.
        """
        context = self.engine.get_context_for_llm(
            user_id=user_id, 
            session_id=self.session_id,
            max_memories=max_memories
        )
        
        # Format for Ollama consumption
        formatted_context = f"""
=== NARRATIVE CONTEXT ===
Campaign: {self.campaign_id}
Session: {self.session_id}

MEMORIES (ranked by narrative relevance):
"""
        
        for memory in context['memories'][:10]:  # Top 10 most relevant
            formatted_context += f"- {memory['type'].title()}: {memory['content'].get('summary', str(memory['content']))}\n"
            if memory['emotional_context']:
                formatted_context += f"  Emotional: {', '.join(memory['emotional_context'])}\n"
            if memory['narrative_themes']:
                formatted_context += f"  Themes: {', '.join(memory['narrative_themes'])}\n"
        
        if context['characters']:
            formatted_context += "\nCHARACTERS:\n"
            for char_id, char_data in context['characters'].items():
                formatted_context += f"- {char_data['name']}: {char_data.get('current_state', {})}\n"
                if char_data.get('goals'):
                    formatted_context += f"  Goals: {', '.join(char_data['goals'])}\n"
                if char_data.get('conflicts'):
                    formatted_context += f"  Conflicts: {', '.join(char_data['conflicts'])}\n"
        
        if context['world_state']:
            formatted_context += "\nWORLD STATE:\n"
            world = context['world_state']
            if world.get('factions'):
                formatted_context += f"Active Factions: {len(world['factions'])}\n"
            if world.get('npcs'):
                formatted_context += f"NPCs: {len(world['npcs'])}\n"
            if world.get('world_events'):
                formatted_context += f"Recent Events: {len(world['world_events'])}\n"
        
        if context['thematic_summary']:
            formatted_context += f"\nTHEMATIC ELEMENTS:\n"
            for theme, count in context['thematic_summary'].items():
                formatted_context += f"- {theme}: {count} occurrences\n"
        
        formatted_context += "\n=== END CONTEXT ===\n"
        
        return formatted_context.strip()
    
    def update_campaign_state(self, updates: Dict[str, Any]):
        """
        Update campaign state in the Narrative Engine.
        """
        self.engine.update_world_state(updates)
        logger.debug(f"🔄 Updated campaign state: {list(updates.keys())}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory system statistics.
        """
        return self.engine.get_stats()
    
    def save_narrative_data(self):
        """
        Save all narrative data to disk.
        """
        self.engine.save_data()
        logger.info(f"💾 Saved narrative data for campaign: {self.campaign_id}")
    
    def _analyze_emotional_context(self, text: str) -> List[EmotionalContext]:
        """
        Analyze emotional context from text input.
        """
        text_lower = text.lower()
        emotions = []
        
        # Enhanced keyword-based emotional analysis
        emotion_keywords = {
            EmotionalContext.JOY: ['happy', 'joy', 'excited', 'pleased', 'delighted', 'cheerful', 'elated'],
            EmotionalContext.FEAR: ['afraid', 'scared', 'fear', 'terrified', 'anxious', 'worried', 'panicked'],
            EmotionalContext.ANGER: ['angry', 'mad', 'furious', 'rage', 'hate', 'irritated', 'enraged'],
            EmotionalContext.SADNESS: ['sad', 'depressed', 'melancholy', 'grief', 'sorrow', 'mourning'],
            EmotionalContext.SURPRISE: ['surprised', 'shocked', 'amazed', 'astonished', 'stunned'],
            EmotionalContext.TRUST: ['trust', 'faith', 'confidence', 'rely', 'believe', 'depend'],
            EmotionalContext.ANTICIPATION: ['hope', 'expect', 'anticipate', 'look forward', 'await'],
            EmotionalContext.LOVE: ['love', 'affection', 'care', 'adore', 'cherish', 'devotion'],
            EmotionalContext.HOPE: ['hope', 'optimistic', 'dream', 'aspire', 'wish', 'desire'],
            EmotionalContext.DESPAIR: ['despair', 'hopeless', 'desperate', 'defeated', 'crushed'],
            EmotionalContext.CURIOSITY: ['curious', 'wonder', 'question', 'investigate', 'explore'],
            EmotionalContext.GUILT: ['guilt', 'guilty', 'remorse', 'regret', 'shame'],
            EmotionalContext.PRIDE: ['proud', 'pride', 'accomplished', 'achievement', 'success'],
            EmotionalContext.GRATITUDE: ['grateful', 'thankful', 'appreciate', 'blessed'],
            EmotionalContext.CONTEMPT: ['contempt', 'disdain', 'scorn', 'disgust', 'revulsion']
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                emotions.append(emotion)
        
        return emotions if emotions else [EmotionalContext.CURIOSITY]
    
    def _extract_narrative_themes(self, text: str) -> List[NarrativeTheme]:
        """
        Extract narrative themes from text input.
        """
        text_lower = text.lower()
        themes = []
        
        # Theme keyword mapping
        theme_keywords = {
            NarrativeTheme.HOPE: ['hope', 'dream', 'aspire', 'future', 'possibility'],
            NarrativeTheme.LOSS: ['lost', 'loss', 'gone', 'missing', 'absence'],
            NarrativeTheme.REDEMPTION: ['redemption', 'redeem', 'atonement', 'forgiveness'],
            NarrativeTheme.BETRAYAL: ['betray', 'betrayal', 'treachery', 'traitor'],
            NarrativeTheme.TRANSFORMATION: ['change', 'transform', 'evolve', 'grow'],
            NarrativeTheme.POWER: ['power', 'strength', 'might', 'authority', 'control'],
            NarrativeTheme.SACRIFICE: ['sacrifice', 'give up', 'lose', 'surrender'],
            NarrativeTheme.JUSTICE: ['justice', 'fair', 'right', 'wrong', 'punish'],
            NarrativeTheme.REVENGE: ['revenge', 'vengeance', 'retribution', 'avenge'],
            NarrativeTheme.FORGIVENESS: ['forgive', 'forgiveness', 'pardon', 'mercy'],
            NarrativeTheme.IDENTITY: ['identity', 'self', 'who am i', 'true self'],
            NarrativeTheme.BELONGING: ['belong', 'home', 'family', 'community'],
            NarrativeTheme.ISOLATION: ['alone', 'isolated', 'separated', 'lonely'],
            NarrativeTheme.GROWTH: ['grow', 'develop', 'learn', 'improve'],
            NarrativeTheme.CORRUPTION: ['corrupt', 'corruption', 'decay', 'rot'],
            NarrativeTheme.PURITY: ['pure', 'innocent', 'clean', 'untainted']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _extract_thematic_tags(self, text: str) -> List[str]:
        """
        Extract thematic tags from text input.
        """
        text_lower = text.lower()
        themes = []
        
        # Common thematic keywords
        theme_keywords = [
            'character', 'development', 'story', 'narrative', 'quest', 'adventure',
            'battle', 'combat', 'magic', 'treasure', 'friendship', 'betrayal',
            'love', 'death', 'birth', 'growth', 'change', 'transformation',
            'power', 'weakness', 'strength', 'courage', 'fear', 'hope', 'despair',
            'family', 'home', 'journey', 'destiny', 'fate', 'choice', 'consequence'
        ]
        
        for keyword in theme_keywords:
            if keyword in text_lower:
                themes.append(keyword)
        
        return themes
    
    def _extract_triggers(self, text: str) -> List[str]:
        """
        Extract trigger keywords for memory recall.
        """
        text_lower = text.lower()
        triggers = []
        
        # Extract potential names, places, and key concepts
        words = text_lower.split()
        for word in words:
            if len(word) > 3 and word.isalpha():
                triggers.append(word)
        
        # Add common trigger words
        common_triggers = ['character', 'story', 'quest', 'battle', 'magic', 'treasure']
        for trigger in common_triggers:
            if trigger in text_lower:
                triggers.append(trigger)
        
        return list(set(triggers))  # Remove duplicates
    
    def _analyze_emotional_context_from_character(self, character_data: Dict[str, Any]) -> List[EmotionalContext]:
        """
        Analyze emotional context from character data.
        """
        # Convert character data to text for analysis
        char_text = json.dumps(character_data).lower()
        return self._analyze_emotional_context(char_text)
    
    def _extract_narrative_themes_from_character(self, character_data: Dict[str, Any]) -> List[NarrativeTheme]:
        """
        Extract narrative themes from character data.
        """
        char_text = json.dumps(character_data).lower()
        return self._extract_narrative_themes(char_text)
    
    def _analyze_emotional_context_from_facts(self, facts: Dict[str, Any]) -> List[EmotionalContext]:
        """
        Analyze emotional context from character facts.
        """
        facts_text = json.dumps(facts).lower()
        return self._analyze_emotional_context(facts_text)
    
    def _extract_narrative_themes_from_facts(self, facts: Dict[str, Any]) -> List[NarrativeTheme]:
        """
        Extract narrative themes from character facts.
        """
        facts_text = json.dumps(facts).lower()
        return self._extract_narrative_themes(facts_text)
    
    def _analyze_emotional_context_from_development(self, development_data: Dict[str, Any]) -> List[EmotionalContext]:
        """
        Analyze emotional context from character development data.
        """
        dev_text = json.dumps(development_data).lower()
        return self._analyze_emotional_context(dev_text)
    
    def _extract_narrative_themes_from_development(self, development_data: Dict[str, Any]) -> List[NarrativeTheme]:
        """
        Extract narrative themes from character development data.
        """
        dev_text = json.dumps(development_data).lower()
        return self._extract_narrative_themes(dev_text)
    
    def _analyze_emotional_context_from_event(self, event_data: Dict[str, Any]) -> List[EmotionalContext]:
        """
        Analyze emotional context from world event data.
        """
        event_text = json.dumps(event_data).lower()
        return self._analyze_emotional_context(event_text)
    
    def _extract_narrative_themes_from_event(self, event_data: Dict[str, Any]) -> List[NarrativeTheme]:
        """
        Extract narrative themes from world event data.
        """
        event_text = json.dumps(event_data).lower()
        return self._extract_narrative_themes(event_text)
    
    def _extract_triggers_from_event(self, event_data: Dict[str, Any]) -> List[str]:
        """
        Extract trigger keywords from world event data.
        """
        event_text = json.dumps(event_data).lower()
        return self._extract_triggers(event_text)
    
    def set_inspiration_points(self, character_name: str, points: int) -> None:
        """
        Set inspiration points for a character (stored in current_state).
        """
        char = self.engine.get_character_by_name(character_name)
        if not char:
            logger.warning(f"Character '{character_name}' not found.")
            return
        current_state = dict(getattr(char, 'current_state', {}) or {})
        current_state['inspiration_points'] = points
        self.engine.update_character_state(character_name, current_state)
        logger.info(f"Set inspiration points for {character_name}: {points}")

    def get_inspiration_points(self, character_name: str) -> int:
        """
        Get inspiration points for a character (from current_state).
        """
        char = self.engine.get_character_by_name(character_name)
        if not char:
            logger.warning(f"Character '{character_name}' not found.")
            return 0
        current_state = getattr(char, 'current_state', {}) or {}
        return current_state.get('inspiration_points', 0)

    def set_saving_throws(self, character_name: str, saving_throws: dict) -> None:
        """
        Set saving throws for a character (stored in current_state).
        saving_throws should be a dict, e.g. {'dexterity': 2, 'wisdom': 1}
        """
        char = self.engine.get_character_by_name(character_name)
        if not char:
            logger.warning(f"Character '{character_name}' not found.")
            return
        current_state = dict(getattr(char, 'current_state', {}) or {})
        current_state['saving_throws'] = saving_throws
        self.engine.update_character_state(character_name, current_state)
        logger.info(f"Set saving throws for {character_name}: {saving_throws}")

    def get_saving_throws(self, character_name: str) -> dict:
        """
        Get saving throws for a character (from current_state).
        """
        char = self.engine.get_character_by_name(character_name)
        if not char:
            logger.warning(f"Character '{character_name}' not found.")
            return {}
        current_state = getattr(char, 'current_state', {}) or {}
        return current_state.get('saving_throws', {}) 