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
    from vector_memory.vector_memory_module import VectorMemoryModule
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
        
        # Initialize vector memory for semantic search
        self.vector_memory = VectorMemoryModule(
            index_path=f"vector_memory/{campaign_id}",
            dimension=384
        )
        
        self.session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🔧 Initialized TNE Demo Engine for campaign: {campaign_id}")
        logger.info(f"🧠 Vector memory initialized for semantic search")
    
    def record_character_creation(self, character_data: Dict[str, Any]) -> str:
        """
        Record character creation in the Narrative Engine.
        Returns campaign context for LLM providers.
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
        
        # Add to TNE memory
        memory_id = self.engine.add_memory(
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
        
        # Also add to vector memory for semantic search
        character_summary = f"Character {character_data.get('name', 'Unknown')} created: {character_data.get('race', 'Unknown')} {character_data.get('class', 'Unknown')} with {character_data.get('background', 'Unknown')} background"
        vector_memory_id = self.vector_memory.add_memory(
            content=character_summary,
            memory_type="character_creation",
            layer="long_term",
            user_id='player',
            session_id=self.session_id,
            emotional_weight=0.4,
            thematic_tags=['character_creation', 'development']
        )
        
        logger.info(f"✅ Recorded character creation: {character_data.get('name', 'Unknown')}")
        logger.info(f"🧠 Added to vector memory: {vector_memory_id}")
        return char_id
    
    def record_player_action(self, user_input: str, context: Dict[str, Any]) -> str:
        """
        Record a player action in the Narrative Engine.
        Returns campaign context for LLM providers.
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
        Get structured campaign context for LLM providers.
        """
        return self.engine.get_context_for_llm(
            user_id=user_id, 
            session_id=self.session_id,
            include_characters=True,
            include_world_state=True
        )
    
    def get_memory_context_for_llm(self, user_id: str = None, max_memories: int = 15) -> str:
        """
        Get memory context for LLM providers, including vector memory search results.
        Returns structured context for LLM providers.
        """
        try:
            # Get TNE memories
            tne_memories = self.engine.get_recent_memories(
                user_id=user_id, 
                limit=max_memories // 2  # Reserve half for vector memories
            )
            
            # Get vector memories through semantic search
            vector_memories = []
            if hasattr(self, 'vector_memory') and self.vector_memory:
                # Search for relevant memories based on recent context
                if tne_memories:
                    # Use the most recent memory as search query
                    latest_memory = tne_memories[0]
                    search_query = latest_memory.get('content', {}).get('summary', '')
                    if search_query:
                        vector_results = self.vector_memory.search_memories(
                            query=search_query,
                            top_k=max_memories // 2,
                            user_id=user_id
                        )
                        vector_memories = [
                            {
                                'id': item.id,
                                'content': item.content,
                                'similarity': score,
                                'memory_type': item.memory_type,
                                'thematic_tags': item.thematic_tags,
                                'created_at': item.created_at.isoformat()
                            }
                            for item, score in vector_results
                        ]
                        logger.info(f"🧠 Retrieved {len(vector_memories)} vector memories with similarity search")
            
            # Combine and format memories
            all_memories = []
            
            # Add TNE memories
            for memory in tne_memories:
                all_memories.append({
                    'source': 'tne',
                    'id': memory.get('id', 'unknown'),
                    'content': memory.get('content', {}).get('summary', ''),
                    'memory_type': memory.get('memory_type', 'unknown'),
                    'emotional_weight': memory.get('emotional_weight', 0.5),
                    'thematic_tags': memory.get('thematic_tags', []),
                    'created_at': memory.get('created_at', 'unknown')
                })
            
            # Add vector memories
            for memory in vector_memories:
                all_memories.append({
                    'source': 'vector',
                    'id': memory['id'],
                    'content': memory['content'],
                    'memory_type': memory['memory_type'],
                    'similarity': memory['similarity'],
                    'thematic_tags': memory['thematic_tags'],
                    'created_at': memory['created_at']
                })
            
            # Sort by relevance (TNE memories first, then by similarity/recency)
            all_memories.sort(key=lambda x: (
                x['source'] != 'tne',  # TNE memories first
                -x.get('similarity', 0) if x['source'] == 'vector' else -x.get('emotional_weight', 0)
            ))
            
            # Format for LLM context
            context_parts = []
            
            if all_memories:
                context_parts.append("=== RELEVANT MEMORIES ===")
                
                for i, memory in enumerate(all_memories[:max_memories]):
                    source_marker = "🧠" if memory['source'] == 'vector' else "💭"
                    context_parts.append(
                        f"{source_marker} Memory {i+1}: {memory['content']}"
                    )
                    
                    if memory.get('thematic_tags'):
                        tags_str = ', '.join(memory['thematic_tags'])
                        context_parts.append(f"   Tags: {tags_str}")
                    
                    if memory['source'] == 'vector' and memory.get('similarity'):
                        context_parts.append(f"   Similarity: {memory['similarity']:.3f}")
                
                context_parts.append("")
            
            # Add character context
            characters = self.engine.get_characters()
            if characters:
                context_parts.append("=== CHARACTERS ===")
                for char in characters:
                    char_name = char.get('name', 'Unknown')
                    char_desc = char.get('description', 'A character')
                    context_parts.append(f"👤 {char_name}: {char_desc}")
                context_parts.append("")
            
            # Add world state
            world_state = self.engine.get_world_state()
            if world_state:
                context_parts.append("=== WORLD STATE ===")
                for key, value in world_state.items():
                    context_parts.append(f"🌍 {key}: {value}")
                context_parts.append("")
            
            context = "\n".join(context_parts)
            
            # Log memory retrieval stats
            tne_count = len([m for m in all_memories if m['source'] == 'tne'])
            vector_count = len([m for m in all_memories if m['source'] == 'vector'])
            logger.info(f"📊 Memory context: {tne_count} TNE + {vector_count} vector memories")
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Failed to get memory context: {e}")
            return "=== NO MEMORY CONTEXT AVAILABLE ==="
    
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
    
    def detect_narrative_ending(self, goals, transformation, resolution, world_state):
        try:
            completed_goals = sum(1 for goal in goals if goal.get('confidence', 0) > 0.8)
            total_goals = len(goals) if goals else 1
            goal_completion_rate = completed_goals / total_goals if total_goals > 0 else 0
            transformation_confidence = transformation.get('confidence_score', 0) if transformation else 0
            resolution_progress = resolution.get('progress', 0) if resolution else 0
            resolution_state = resolution.get('resolution_state', 'early') if resolution else 'early'
            story_flags = world_state.get('story_flags', {})
            completed_flags = sum(1 for flag, value in story_flags.items() if value is True)
            total_flags = len(story_flags) if story_flags else 1
            flag_completion_rate = completed_flags / total_flags if total_flags > 0 else 0
            completion_score = (goal_completion_rate + transformation_confidence + resolution_progress + flag_completion_rate) / 4
            ending_triggered = completion_score > 0.75 and resolution_state in ['climax', 'denouement']
            if not ending_triggered:
                return {
                    'ending_triggered': False,
                    'ending_type': None,
                    'justification': f"Story completion at {completion_score:.1%}, not ready for ending",
                    'confidence': completion_score
                }
            ending_type = self._determine_ending_type(goals, transformation, world_state)
            return {
                'ending_triggered': True,
                'ending_type': ending_type,
                'justification': f"Story completion at {completion_score:.1%}, {ending_type} ending triggered",
                'confidence': completion_score
            }
        except Exception as e:
            logger.error(f"Error detecting narrative ending: {e}")
            return {
                'ending_triggered': False,
                'ending_type': None,
                'justification': 'Error in ending detection',
                'confidence': 0.0
            }

    def _determine_ending_type(self, goals, transformation, world_state):
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

    def generate_narrative_epilogue(self, memory_log, goals_achieved, character_stats, transformation_path, world_state_flags, ending_type):
        try:
            character_name = character_stats.get('name', 'The Hero')
            character_level = character_stats.get('level', 1)
            transformation_type = transformation_path.get('transformation_type', 'Unknown')
            epilogue_text = self._generate_ending_specific_epilogue(ending_type, character_name, transformation_type, goals_achieved, world_state_flags)
            epilogue_theme = self._determine_epilogue_theme(ending_type, transformation_type)
            epilogue_quotes = self._generate_epilogue_quotes(ending_type, transformation_type)
            return {
                'epilogue_text': epilogue_text,
                'epilogue_theme': epilogue_theme,
                'epilogue_quotes': epilogue_quotes
            }
        except Exception as e:
            logger.error(f"Error generating narrative epilogue: {e}")
            return {
                'epilogue_text': 'An epilogue could not be generated.',
                'epilogue_theme': 'Unknown',
                'epilogue_quotes': ['Every journey changes the traveler.']
            }

    def _generate_ending_specific_epilogue(self, ending_type, character_name, transformation_type, goals_achieved, world_state_flags):
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

    def _determine_epilogue_theme(self, ending_type, transformation_type):
        themes = {
            'triumph': 'Victory and Legacy',
            'tragedy': 'Loss and Remembrance',
            'rebirth': 'Transformation and Renewal',
            'sacrifice': 'Selflessness and Honor',
            'redemption': 'Forgiveness and Growth',
            'bittersweet': 'Balance and Wisdom'
        }
        return themes.get(ending_type, 'Journey and Change')

    def _generate_epilogue_quotes(self, ending_type, transformation_type):
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
    
    def extract_symbolic_tags(self, narrative_text: str, memory_context: Dict[str, Any], character_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract symbolic tags from narrative text using TNE analysis.
        """
        try:
            # Analyze narrative text for symbolic patterns
            symbolic_tags = []
            
            # Extract emotional context
            emotional_context = self._analyze_emotional_context(narrative_text)
            
            # Extract narrative themes
            narrative_themes = self._extract_narrative_themes(narrative_text)
            
            # Extract thematic tags
            thematic_tags = self._extract_thematic_tags(narrative_text)
            
            # Archetype detection
            archetypes = self._detect_archetypes(narrative_text)
            
            # Metaphor detection
            metaphors = self._detect_metaphors(narrative_text)
            
            # Combine all symbolic elements
            for archetype in archetypes:
                symbolic_tags.append({
                    'type': 'archetype',
                    'symbol': archetype,
                    'confidence': 0.8,
                    'color': '#fbbf24',
                    'tooltip': f'Archetypal pattern: {archetype}'
                })
            
            for theme in narrative_themes:
                symbolic_tags.append({
                    'type': 'theme',
                    'symbol': theme.value.title(),
                    'confidence': 0.7,
                    'color': '#3b82f6',
                    'tooltip': f'Narrative theme: {theme.value}'
                })
            
            for metaphor in metaphors:
                symbolic_tags.append({
                    'type': 'metaphor',
                    'symbol': metaphor,
                    'confidence': 0.6,
                    'color': '#10b981',
                    'tooltip': f'Metaphorical meaning: {metaphor}'
                })
            
            return symbolic_tags
            
        except Exception as e:
            logger.error(f"Error extracting symbolic tags: {e}")
            return []
    
    def infer_narrative_goals(self, session_history: List[Dict], memory_context: Dict[str, Any], current_turn: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Infer narrative goals from session history and memory context.
        """
        try:
            goals = []
            
            # Analyze session history for goal patterns
            all_text = ' '.join([msg.get('content', '') for msg in session_history]).lower()
            
            # Goal type detection with TNE context
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
            
            # Detect goals based on keywords and TNE context
            for goal_type, pattern in goal_patterns.items():
                if any(keyword in all_text for keyword in pattern['keywords']):
                    # Calculate confidence based on frequency and TNE context
                    keyword_count = sum(1 for keyword in pattern['keywords'] if keyword in all_text)
                    base_confidence = pattern['confidence']
                    
                    # Boost confidence based on memory context
                    memory_boost = 0.1 if memory_context else 0.0
                    confidence = min(0.95, base_confidence + (keyword_count * 0.05) + memory_boost)
                    
                    # Generate narrative justification
                    justification = self._generate_goal_justification(goal_type, all_text)
                    
                    goals.append({
                        'type': goal_type,
                        'confidence': confidence,
                        'color': pattern['color'],
                        'justification': justification,
                        'progress': min(0.8, confidence * 0.8)
                    })
            
            # Sort by confidence and return top 3
            goals.sort(key=lambda x: x['confidence'], reverse=True)
            return goals[:3]
            
        except Exception as e:
            logger.error(f"Error inferring narrative goals: {e}")
            return []
    
    def infer_character_transformation(self, narrative_history: list, symbolic_tags: list, character_stats: dict) -> dict:
        """
        Infer character transformation from narrative history and symbolic tags.
        """
        try:
            all_text = ' '.join([msg.get('content', '') for msg in narrative_history]).lower()
            transformation_patterns = {
                'Innocent → Orphan → Seeker → Warrior → Magician': {
                    'keywords': ['innocent', 'naive', 'orphan', 'lost', 'seeker', 'quest', 'warrior', 'battle', 'magician', 'power'],
                    'confidence': 0.8,
                    'archetypal_shift': "Hero's Journey",
                    'description': "Classic hero's journey from innocence to mastery"
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
            detected_transformations = []
            for pattern_name, pattern_data in transformation_patterns.items():
                keyword_matches = sum(1 for keyword in pattern_data['keywords'] if keyword in all_text)
                if keyword_matches >= 2:
                    confidence = min(0.95, pattern_data['confidence'] + (keyword_matches * 0.05))
                    detected_transformations.append({
                        'transformation_type': pattern_name,
                        'archetypal_shift': pattern_data['archetypal_shift'],
                        'confidence_score': confidence,
                        'description': pattern_data['description'],
                        'evidence_snippets': self._extract_evidence_snippets(all_text, pattern_data['keywords'])
                    })
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
        except Exception as e:
            logger.error(f"Error inferring character transformation: {e}")
            return {
                'transformation_type': 'Unknown',
                'archetypal_shift': 'Error in analysis',
                'confidence_score': 0.0,
                'description': 'Error analyzing transformation',
                'evidence_snippets': []
            }

    def _extract_evidence_snippets(self, text: str, keywords: list) -> list:
        snippets = []
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 10:
                    snippets.append(clean_sentence[:100] + "..." if len(clean_sentence) > 100 else clean_sentence)
        return snippets[:3]

    def monitor_narrative_resolution(self, goals: list, world_state: dict, memory_context: dict, transformations: list) -> dict:
        try:
            completed_goals = sum(1 for goal in goals if goal.get('confidence', 0) > 0.8)
            total_goals = len(goals) if goals else 1
            story_flags = world_state.get('story_flags', {})
            completed_flags = sum(1 for flag, value in story_flags.items() if value is True)
            total_flags = len(story_flags) if story_flags else 1
            transformation_progress = 0
            if transformations:
                transformation_progress = transformations[0].get('confidence_score', 0)
            goal_progress = completed_goals / total_goals if total_goals > 0 else 0
            flag_progress = completed_flags / total_flags if total_flags > 0 else 0
            overall_progress = (goal_progress + flag_progress + transformation_progress) / 3
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
        except Exception as e:
            logger.error(f"Error monitoring narrative resolution: {e}")
            return {
                'resolution_state': 'unknown',
                'progress': 0.0,
                'goal_progress': 0.0,
                'flag_progress': 0.0,
                'transformation_progress': 0.0,
                'justification': 'Error in resolution monitoring',
                'recommendation': 'Unable to provide recommendation'
            }
    
    def _detect_archetypes(self, text: str) -> List[str]:
        """Detect archetypal patterns in text."""
        text_lower = text.lower()
        archetypes = []
        
        archetype_patterns = {
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
        
        for archetype, keywords in archetype_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                archetypes.append(archetype)
        
        return archetypes
    
    def _detect_metaphors(self, text: str) -> List[str]:
        """Detect metaphorical patterns in text."""
        text_lower = text.lower()
        metaphors = []
        
        metaphor_patterns = {
            'Light vs Dark': ['light', 'dark', 'shadow', 'illumination', 'obscurity'],
            'Journey': ['journey', 'path', 'road', 'travel', 'quest'],
            'Battle': ['battle', 'war', 'fight', 'conflict', 'struggle'],
            'Growth': ['growth', 'bloom', 'flourish', 'develop', 'mature'],
            'Decay': ['decay', 'rot', 'wither', 'fade', 'decline'],
            'Water': ['water', 'flow', 'river', 'ocean', 'tide'],
            'Fire': ['fire', 'flame', 'burn', 'heat', 'passion'],
            'Earth': ['earth', 'ground', 'soil', 'foundation', 'stability']
        }
        
        for metaphor, keywords in metaphor_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                metaphors.append(metaphor)
        
        return metaphors
    
    def _generate_goal_justification(self, goal_type: str, context_text: str) -> str:
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
    
    def _extract_stat_triggers(self, character_stats: Dict[str, Any]) -> List[str]:
        """Extract stat-based triggers from character stats."""
        triggers = []
        
        # HP-based triggers
        current_hp = character_stats.get('hit_points', 10)
        if current_hp <= 3:
            triggers.append("critical_health")
        elif current_hp <= 5:
            triggers.append("low_health")
        elif current_hp <= 10:
            triggers.append("wounded")
        
        # Ability score triggers
        ability_scores = character_stats.get('ability_scores', {})
        
        for ability, score in ability_scores.items():
            if score >= 18:
                triggers.append(f"exceptional_{ability}")
            elif score >= 16:
                triggers.append(f"high_{ability}")
            elif score <= 6:
                triggers.append(f"low_{ability}")
        
        # Level-based triggers
        level = character_stats.get('level', 1)
        if level >= 5:
            triggers.append("experienced_warrior")
        elif level >= 3:
            triggers.append("seasoned_adventurer")
        
        return triggers 