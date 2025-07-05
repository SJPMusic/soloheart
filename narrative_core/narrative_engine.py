#!/usr/bin/env python3
"""
The Narrative Engine - Memory-Driven Narrative Continuity System
==============================================================

A persistent, memory-driven narrative system designed to remember, contextualize, 
and interpret narrative continuity across any domain (games, therapy, education, simulation).

This is NOT a game engine or storytelling bot. It is a memory system designed to power 
meaningful, emergent narrative experience driven by consequence, emotion, and continuity.

Core Design Principles:
- Memory-driven continuity with layered decay
- Causal inference connecting events by consequence, not chronology
- Emergent storytelling through evolving state and remembered choices
- Domain-agnostic architecture supporting any narrative interface
- Emotional and thematic memory scoring for relevance ranking
- Persistent character development and relationship tracking
"""

import json
import hashlib
import logging
import math
import uuid
from typing import Dict, List, Any, Optional, Deque, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import os
import pickle

logger = logging.getLogger(__name__)

# --- Core Enums ---

class MemoryLayer(Enum):
    """Layered memory system with different decay characteristics."""
    SHORT_TERM = "short_term"    # Immediate context (last N exchanges) - fast decay
    MID_TERM = "mid_term"        # Session-level (goals, arcs, unresolved threads) - medium decay
    LONG_TERM = "long_term"      # Campaign/world-level (lore, history, relationships) - slow decay

class MemoryType(Enum):
    """Types of narrative memory with different processing characteristics."""
    EVENT = "event"                           # Discrete narrative events
    DECISION = "decision"                     # Character choices and consequences
    EMOTION = "emotion"                       # Emotional states and reactions
    RELATIONSHIP = "relationship"             # Character relationship changes
    THEME = "theme"                           # Narrative theme reinforcement
    WORLD_STATE = "world_state"              # Environmental/setting changes
    CALLBACK = "callback"                     # References to past events
    FORESHADOW = "foreshadow"                # Future implications
    CHARACTER_DEVELOPMENT = "character_development"  # Character growth
    CAUSAL_LINK = "causal_link"              # Cause-effect relationships
    SYMBOLIC = "symbolic"                    # Symbolic meaning and metaphor
    CONFLICT = "conflict"                    # Tensions and oppositions

class EmotionalContext(Enum):
    """Emotional context for memory scoring and relevance."""
    JOY = "joy"
    FEAR = "fear"
    ANGER = "anger"
    SADNESS = "sadness"
    SURPRISE = "surprised"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    DISGUST = "disgust"
    LOVE = "love"
    HOPE = "hope"
    DESPAIR = "despair"
    CURIOSITY = "curiosity"
    GUILT = "guilt"
    SHAME = "shame"
    PRIDE = "pride"
    ENVY = "envy"
    GRATITUDE = "gratitude"
    CONTEMPT = "contempt"
    AMBIVALENCE = "ambivalence"

class NarrativeTheme(Enum):
    """Core narrative themes that inform memory scoring and surfacing."""
    HOPE = "hope"
    LOSS = "loss"
    REDEMPTION = "redemption"
    BETRAYAL = "betrayal"
    TRANSFORMATION = "transformation"
    POWER = "power"
    SACRIFICE = "sacrifice"
    JUSTICE = "justice"
    REVENGE = "revenge"
    FORGIVENESS = "forgiveness"
    IDENTITY = "identity"
    BELONGING = "belonging"
    ISOLATION = "isolation"
    GROWTH = "growth"
    DECAY = "decay"
    REBIRTH = "rebirth"
    CORRUPTION = "corruption"
    PURITY = "purity"
    CHAOS = "chaos"
    ORDER = "order"

# --- Core Data Structures ---

@dataclass
class MemoryNode:
    """
    Represents a single memory in the narrative engine with sophisticated
    decay, reinforcement, and causal linking capabilities.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Dict[str, Any] = field(default_factory=dict)
    memory_type: MemoryType = MemoryType.EVENT
    layer: MemoryLayer = MemoryLayer.MID_TERM
    timestamp: datetime = field(default_factory=datetime.utcnow)
    emotional_weight: float = 0.5  # 0.0 to 1.0
    emotional_context: List[EmotionalContext] = field(default_factory=list)
    thematic_tags: List[str] = field(default_factory=list)
    narrative_themes: List[NarrativeTheme] = field(default_factory=list)
    user_id: str = ""
    session_id: str = ""
    decay_rate: float = 0.1
    reinforcement_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    associations: List[str] = field(default_factory=list)  # Related memory IDs
    triggers: List[str] = field(default_factory=list)      # Keywords for recall
    causal_links: List[str] = field(default_factory=list)  # Causal memory IDs
    causal_effects: List[str] = field(default_factory=list)  # Effects this memory causes
    personalization: Dict[str, Any] = field(default_factory=dict)
    narrative_context: Dict[str, Any] = field(default_factory=dict)
    domain_context: Dict[str, Any] = field(default_factory=dict)  # Domain-specific context
    significance_score: float = 0.0
    last_significance_calculation: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
        if self.last_significance_calculation is None:
            self.last_significance_calculation = self.timestamp

    def calculate_significance(self, now: Optional[datetime] = None) -> float:
        """
        Calculate current significance score based on emotional weight, decay, 
        reinforcement, and thematic importance.
        """
        now = now or datetime.utcnow()
        
        # Base emotional weight
        base_score = self.emotional_weight
        
        # Time-based decay (different rates per layer)
        age_hours = (now - self.timestamp).total_seconds() / 3600
        layer_decay_rates = {
            MemoryLayer.SHORT_TERM: 0.2,   # Fast decay
            MemoryLayer.MID_TERM: 0.05,    # Medium decay
            MemoryLayer.LONG_TERM: 0.01    # Slow decay
        }
        decay_rate = layer_decay_rates.get(self.layer, 0.05)
        decay = max(0.1, 1.0 - (age_hours * decay_rate))
        
        # Reinforcement bonus
        reinforcement = min(0.3, self.reinforcement_count * 0.05)
        
        # Recency bonus (recent access)
        recency_hours = (now - self.last_accessed).total_seconds() / 3600
        recency = max(0.0, 0.2 * (1.0 - (recency_hours / 24)))
        
        # Thematic importance bonus
        thematic_bonus = min(0.2, len(self.narrative_themes) * 0.05)
        
        # Causal importance bonus
        causal_bonus = min(0.15, len(self.causal_links) * 0.02 + len(self.causal_effects) * 0.03)
        
        # Layer multiplier
        layer_multipliers = {
            MemoryLayer.SHORT_TERM: 0.8,
            MemoryLayer.MID_TERM: 1.0,
            MemoryLayer.LONG_TERM: 1.3
        }
        layer_mult = layer_multipliers.get(self.layer, 1.0)
        
        # Calculate final significance
        significance = (base_score * decay + reinforcement + recency + thematic_bonus + causal_bonus) * layer_mult
        self.significance_score = max(0.0, min(1.0, significance))
        self.last_significance_calculation = now
        
        return self.significance_score

    def reinforce(self, reinforcement_strength: float = 1.0):
        """Reinforce this memory, reducing decay rate and updating access time."""
        self.reinforcement_count += int(reinforcement_strength)
        self.decay_rate = max(0.01, self.decay_rate * (0.95 ** reinforcement_strength))
        self.last_accessed = datetime.utcnow()
        self.calculate_significance()

    def add_causal_link(self, cause_memory_id: str):
        """Add a causal link to another memory."""
        if cause_memory_id not in self.causal_links:
            self.causal_links.append(cause_memory_id)

    def add_causal_effect(self, effect_memory_id: str):
        """Add this memory as a cause of another memory."""
        if effect_memory_id not in self.causal_effects:
            self.causal_effects.append(effect_memory_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'layer': self.layer.value,
            'timestamp': self.timestamp.isoformat(),
            'emotional_weight': self.emotional_weight,
            'emotional_context': [e.value for e in self.emotional_context],
            'thematic_tags': self.thematic_tags,
            'narrative_themes': [t.value for t in self.narrative_themes],
            'user_id': self.user_id,
            'session_id': self.session_id,
            'decay_rate': self.decay_rate,
            'reinforcement_count': self.reinforcement_count,
            'last_accessed': self.last_accessed.isoformat(),
            'associations': self.associations,
            'triggers': self.triggers,
            'causal_links': self.causal_links,
            'causal_effects': self.causal_effects,
            'personalization': self.personalization,
            'narrative_context': self.narrative_context,
            'domain_context': self.domain_context,
            'significance_score': self.significance_score,
            'last_significance_calculation': self.last_significance_calculation.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryNode':
        """Create from dictionary for deserialization."""
        # Convert string values back to enums
        data['memory_type'] = MemoryType(data['memory_type'])
        data['layer'] = MemoryLayer(data['layer'])
        data['emotional_context'] = [EmotionalContext(e) for e in data['emotional_context']]
        data['narrative_themes'] = [NarrativeTheme(t) for t in data.get('narrative_themes', [])]
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        data['last_significance_calculation'] = datetime.fromisoformat(data['last_significance_calculation'])
        
        return cls(**data)

@dataclass
class Character:
    """
    Represents a character with persistent development tracking,
    relationship management, and goal evolution.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    traits: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    relationships: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # character_id -> relationship_data
    development_arc: List[Dict[str, Any]] = field(default_factory=list)
    current_state: Dict[str, Any] = field(default_factory=dict)
    background: Dict[str, Any] = field(default_factory=dict)
    personality_matrix: Dict[str, float] = field(default_factory=dict)  # trait -> strength (0.0 to 1.0)
    emotional_state: Dict[str, float] = field(default_factory=dict)  # emotion -> intensity
    memory_ids: List[str] = field(default_factory=list)  # Associated memory IDs
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def add_development_moment(self, moment: Dict[str, Any]):
        """Add a character development moment to the arc."""
        moment['timestamp'] = datetime.utcnow().isoformat()
        self.development_arc.append(moment)
        self.last_updated = datetime.utcnow()

    def update_trait(self, trait: str, strength: float):
        """Update a personality trait strength."""
        self.personality_matrix[trait] = max(0.0, min(1.0, strength))
        self.last_updated = datetime.utcnow()

    def update_emotional_state(self, emotion: str, intensity: float):
        """Update emotional state intensity."""
        self.emotional_state[emotion] = max(0.0, min(1.0, intensity))
        self.last_updated = datetime.utcnow()

    def add_relationship(self, other_character_id: str, relationship_type: str, strength: float = 0.5):
        """Add or update a relationship with another character."""
        self.relationships[other_character_id] = {
            'type': relationship_type,
            'strength': max(0.0, min(1.0, strength)),
            'last_updated': datetime.utcnow().isoformat()
        }
        self.last_updated = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'traits': self.traits,
            'goals': self.goals,
            'conflicts': self.conflicts,
            'relationships': self.relationships,
            'development_arc': self.development_arc,
            'current_state': self.current_state,
            'background': self.background,
            'personality_matrix': self.personality_matrix,
            'emotional_state': self.emotional_state,
            'memory_ids': self.memory_ids,
            'last_updated': self.last_updated.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Create from dictionary for deserialization."""
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

@dataclass
class WorldState:
    """
    Represents the dynamic world state with factions, regions, and NPCs
    that behave independently with stored goals and evolving beliefs.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    factions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    regions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    npcs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    world_events: List[Dict[str, Any]] = field(default_factory=list)
    environmental_state: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def add_faction(self, faction_id: str, faction_data: Dict[str, Any]):
        """Add or update a faction with goals and beliefs."""
        faction_data['last_updated'] = datetime.utcnow().isoformat()
        self.factions[faction_id] = faction_data
        self.last_updated = datetime.utcnow()

    def add_npc(self, npc_id: str, npc_data: Dict[str, Any]):
        """Add or update an NPC with goals and beliefs."""
        npc_data['last_updated'] = datetime.utcnow().isoformat()
        self.npcs[npc_id] = npc_data
        self.last_updated = datetime.utcnow()

    def add_world_event(self, event_data: Dict[str, Any]):
        """Add a world event that may affect multiple entities."""
        event_data['timestamp'] = datetime.utcnow().isoformat()
        self.world_events.append(event_data)
        self.last_updated = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'factions': self.factions,
            'regions': self.regions,
            'npcs': self.npcs,
            'world_events': self.world_events,
            'environmental_state': self.environmental_state,
            'last_updated': self.last_updated.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldState':
        """Create from dictionary for deserialization."""
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

class NarrativeEngine:
    """
    The core Narrative Engine - a memory-driven narrative continuity system.
    
    This engine provides:
    - Layered memory with sophisticated decay and reinforcement
    - Causal inference connecting events by consequence
    - Character development and relationship tracking
    - World state simulation with independent entities
    - Memory retrieval ranked by narrative relevance
    - Domain-agnostic architecture
    """
    
    def __init__(self, campaign_id: str = "default", data_dir: str = "narrative_data"):
        self.campaign_id = campaign_id
        self.data_dir = data_dir
        self.session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Core memory system
        self.memories: Dict[str, MemoryNode] = {}
        self.characters: Dict[str, Character] = {}
        self.world_state = WorldState()
        
        # Indexes for efficient retrieval
        self.user_memories: Dict[str, Set[str]] = defaultdict(set)
        self.session_memories: Dict[str, Set[str]] = defaultdict(set)
        self.thematic_index: Dict[str, Set[str]] = defaultdict(set)
        self.emotional_index: Dict[EmotionalContext, Set[str]] = defaultdict(set)
        self.causal_index: Dict[str, Set[str]] = defaultdict(set)
        self.trigger_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Statistics and logging
        self.stats = {
            'total_memories': 0,
            'memories_by_layer': defaultdict(int),
            'memories_by_type': defaultdict(int),
            'total_characters': 0,
            'last_forget_operation': None,
            'memory_operations': 0
        }
        
        # Load existing data
        self._load_data()
        logger.info(f"🔧 Initialized Narrative Engine for campaign: {campaign_id}")

    def add_memory(self, content: Dict[str, Any], memory_type: MemoryType, 
                   layer: MemoryLayer, user_id: str, session_id: str, 
                   emotional_weight: float = 0.5, 
                   emotional_context: List[EmotionalContext] = None,
                   thematic_tags: List[str] = None,
                   narrative_themes: List[NarrativeTheme] = None,
                   triggers: List[str] = None, 
                   personalization: Dict[str, Any] = None,
                   narrative_context: Dict[str, Any] = None,
                   domain_context: Dict[str, Any] = None) -> str:
        """
        Add a new memory to the system with sophisticated indexing and causal analysis.
        """
        # Create memory node
        memory = MemoryNode(
            content=content,
            memory_type=memory_type,
            layer=layer,
            user_id=user_id,
            session_id=session_id,
            emotional_weight=emotional_weight,
            emotional_context=emotional_context or [],
            thematic_tags=thematic_tags or [],
            narrative_themes=narrative_themes or [],
            triggers=triggers or [],
            personalization=personalization or {},
            narrative_context=narrative_context or {},
            domain_context=domain_context or {}
        )
        
        # Calculate initial significance
        memory.calculate_significance()
        
        # Store memory
        self.memories[memory.id] = memory
        
        # Update indexes
        self._update_indexes(memory)
        
        # Find causal associations
        self._find_causal_associations(memory)
        
        # Update statistics
        self.stats['total_memories'] += 1
        self.stats['memories_by_layer'][layer.value] += 1
        self.stats['memories_by_type'][memory_type.value] += 1
        self.stats['memory_operations'] += 1
        
        # Log memory creation
        logger.debug(f"📝 Created memory {memory.id[:8]}... ({memory_type.value}, {layer.value})")
        
        return memory.id

    def recall(self, query: str = None, emotional: EmotionalContext = None, 
               thematic: List[str] = None, narrative_themes: List[NarrativeTheme] = None,
               user_id: str = None, layer: MemoryLayer = None, 
               min_significance: float = 0.0, limit: int = 10) -> List[MemoryNode]:
        """
        Retrieve memories ranked by narrative relevance (recency × emotional intensity × narrative weight).
        """
        candidates = set()
        
        # Start with all memories if no specific filters
        if not any([query, emotional, thematic, narrative_themes, user_id, layer]):
            candidates = set(self.memories.keys())
        else:
            # Apply filters
            if user_id:
                candidates.update(self.user_memories.get(user_id, set()))
            if layer:
                layer_memories = {mid for mid, mem in self.memories.items() if mem.layer == layer}
                candidates = candidates.intersection(layer_memories) if candidates else layer_memories
            if emotional:
                candidates.update(self.emotional_index.get(emotional, set()))
            if thematic:
                for theme in thematic:
                    candidates.update(self.thematic_index.get(theme, set()))
            if narrative_themes:
                for theme in narrative_themes:
                    candidates.update(self.thematic_index.get(theme.value, set()))
            if query:
                # Text-based search
                query_memories = {mid for mid, mem in self.memories.items() 
                                if self._matches_query(mem, query)}
                candidates = candidates.intersection(query_memories) if candidates else query_memories
        
        # Calculate current significance for all candidates
        now = datetime.utcnow()
        scored_memories = []
        for memory_id in candidates:
            memory = self.memories[memory_id]
            significance = memory.calculate_significance(now)
            if significance >= min_significance:
                scored_memories.append((memory, significance))
        
        # Sort by significance (narrative relevance)
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        result = [memory for memory, score in scored_memories[:limit]]
        
        # Reinforce accessed memories
        for memory in result:
            memory.reinforce(0.5)  # Light reinforcement for recall
        
        logger.debug(f"🔍 Recalled {len(result)} memories from {len(candidates)} candidates")
        return result

    def get_context_for_llm(self, user_id: str = None, session_id: str = None, 
                           max_memories: int = 20, include_characters: bool = True,
                           include_world_state: bool = True) -> Dict[str, Any]:
        """
        Get structured context for LLM consumption, ranked by narrative relevance.
        """
        context = {
            'campaign_id': self.campaign_id,
            'session_id': session_id or self.session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'memories': [],
            'characters': {},
            'world_state': {},
            'thematic_summary': {},
            'emotional_context': {},
            'causal_chains': []
        }
        
        # Get relevant memories
        memories = self.recall(user_id=user_id, limit=max_memories)
        for memory in memories:
            context['memories'].append({
                'id': memory.id,
                'content': memory.content,
                'type': memory.memory_type.value,
                'layer': memory.layer.value,
                'emotional_weight': memory.emotional_weight,
                'emotional_context': [e.value for e in memory.emotional_context],
                'thematic_tags': memory.thematic_tags,
                'narrative_themes': [t.value for t in memory.narrative_themes],
                'significance': memory.significance_score,
                'timestamp': memory.timestamp.isoformat()
            })
        
        # Add character information
        if include_characters:
            for char_id, character in self.characters.items():
                context['characters'][char_id] = character.to_dict()
        
        # Add world state
        if include_world_state:
            context['world_state'] = self.world_state.to_dict()
        
        # Add thematic summary
        context['thematic_summary'] = self._get_thematic_summary()
        
        # Add emotional context
        context['emotional_context'] = self._get_emotional_context()
        
        # Add causal chains
        context['causal_chains'] = self._get_causal_chains()
        
        return context

    def add_character(self, character_data: Dict[str, Any]) -> str:
        """Add or update a character with persistent development tracking."""
        # The core engine accepts any character data structure
        # Domain-specific filtering should happen in the integration layer
        char_id = character_data.get('id', str(uuid.uuid4()))
        
        if char_id in self.characters:
            # Update existing character
            character = self.characters[char_id]
            for key, value in character_data.items():
                if hasattr(character, key):
                    setattr(character, key, value)
        else:
            # Create new character - accept data as provided by integration layer
            character = Character(**character_data)
            self.characters[char_id] = character
            self.stats['total_characters'] += 1
        
        character.last_updated = datetime.utcnow()
        logger.debug(f"👤 {'Updated' if char_id in self.characters else 'Added'} character: {character.name}")
        return char_id

    def update_world_state(self, updates: Dict[str, Any]):
        """Update world state with new information."""
        if 'factions' in updates:
            for faction_id, faction_data in updates['factions'].items():
                self.world_state.add_faction(faction_id, faction_data)
        
        if 'npcs' in updates:
            for npc_id, npc_data in updates['npcs'].items():
                self.world_state.add_npc(npc_id, npc_data)
        
        if 'world_events' in updates:
            for event_data in updates['world_events']:
                self.world_state.add_world_event(event_data)
        
        logger.debug(f"🌍 Updated world state with {len(updates)} changes")

    def forget(self, threshold: float = 0.1):
        """
        Remove memories below significance threshold, implementing memory decay.
        """
        now = datetime.utcnow()
        to_remove = []
        
        for memory_id, memory in self.memories.items():
            significance = memory.calculate_significance(now)
            if significance < threshold:
                to_remove.append(memory_id)
        
        # Remove low-significance memories
        for memory_id in to_remove:
            memory = self.memories[memory_id]
            
            # Remove from indexes
            self._remove_from_indexes(memory)
            
            # Remove from characters
            for character in self.characters.values():
                if memory_id in character.memory_ids:
                    character.memory_ids.remove(memory_id)
            
            # Remove from main storage
            del self.memories[memory_id]
        
        self.stats['last_forget_operation'] = now.isoformat()
        logger.info(f"🧹 Forgot {len(to_remove)} memories below threshold {threshold}")

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        now = datetime.utcnow()
        
        # Calculate current significance for all memories
        total_significance = 0
        layer_significance = defaultdict(float)
        type_significance = defaultdict(float)
        
        for memory in self.memories.values():
            significance = memory.calculate_significance(now)
            total_significance += significance
            layer_significance[memory.layer.value] += significance
            type_significance[memory.memory_type.value] += significance
        
        return {
            'campaign_id': self.campaign_id,
            'total_memories': len(self.memories),
            'total_characters': len(self.characters),
            'average_significance': total_significance / max(1, len(self.memories)),
            'memories_by_layer': dict(self.stats['memories_by_layer']),
            'memories_by_type': dict(self.stats['memories_by_type']),
            'significance_by_layer': dict(layer_significance),
            'significance_by_type': dict(type_significance),
            'last_forget_operation': self.stats['last_forget_operation'],
            'memory_operations': self.stats['memory_operations']
        }

    def save_data(self):
        """Save all data to disk for persistence."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Save memories
        memories_data = {mid: mem.to_dict() for mid, mem in self.memories.items()}
        with open(os.path.join(self.data_dir, f"{self.campaign_id}_memories.json"), 'w') as f:
            json.dump(memories_data, f, indent=2)
        
        # Save characters
        characters_data = {cid: char.to_dict() for cid, char in self.characters.items()}
        with open(os.path.join(self.data_dir, f"{self.campaign_id}_characters.json"), 'w') as f:
            json.dump(characters_data, f, indent=2)
        
        # Save world state
        with open(os.path.join(self.data_dir, f"{self.campaign_id}_world.json"), 'w') as f:
            json.dump(self.world_state.to_dict(), f, indent=2)
        
        # Save statistics
        with open(os.path.join(self.data_dir, f"{self.campaign_id}_stats.json"), 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        logger.info(f"💾 Saved Narrative Engine data for campaign: {self.campaign_id}")

    def _load_data(self):
        """Load existing data from disk."""
        try:
            # Load memories
            memories_file = os.path.join(self.data_dir, f"{self.campaign_id}_memories.json")
            if os.path.exists(memories_file):
                with open(memories_file, 'r') as f:
                    memories_data = json.load(f)
                for mid, mem_data in memories_data.items():
                    memory = MemoryNode.from_dict(mem_data)
                    self.memories[mid] = memory
                    self._update_indexes(memory)
            
            # Load characters
            characters_file = os.path.join(self.data_dir, f"{self.campaign_id}_characters.json")
            if os.path.exists(characters_file):
                with open(characters_file, 'r') as f:
                    characters_data = json.load(f)
                for cid, char_data in characters_data.items():
                    character = Character.from_dict(char_data)
                    self.characters[cid] = character
            
            # Load world state
            world_file = os.path.join(self.data_dir, f"{self.campaign_id}_world.json")
            if os.path.exists(world_file):
                with open(world_file, 'r') as f:
                    world_data = json.load(f)
                self.world_state = WorldState.from_dict(world_data)
            
            # Load statistics
            stats_file = os.path.join(self.data_dir, f"{self.campaign_id}_stats.json")
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    self.stats.update(json.load(f))
            
            logger.info(f"📂 Loaded existing data for campaign: {self.campaign_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load existing data: {e}")

    def _update_indexes(self, memory: MemoryNode):
        """Update all indexes for efficient memory retrieval."""
        # User index
        self.user_memories[memory.user_id].add(memory.id)
        
        # Session index
        self.session_memories[memory.session_id].add(memory.id)
        
        # Thematic index
        for tag in memory.thematic_tags:
            self.thematic_index[tag].add(memory.id)
        for theme in memory.narrative_themes:
            self.thematic_index[theme.value].add(memory.id)
        
        # Emotional index
        for emotion in memory.emotional_context:
            self.emotional_index[emotion].add(memory.id)
        
        # Causal index
        for cause_id in memory.causal_links:
            self.causal_index[cause_id].add(memory.id)
        
        # Trigger index
        for trigger in memory.triggers:
            self.trigger_index[trigger].add(memory.id)

    def _remove_from_indexes(self, memory: MemoryNode):
        """Remove memory from all indexes."""
        # User index
        self.user_memories[memory.user_id].discard(memory.id)
        
        # Session index
        self.session_memories[memory.session_id].discard(memory.id)
        
        # Thematic index
        for tag in memory.thematic_tags:
            self.thematic_index[tag].discard(memory.id)
        for theme in memory.narrative_themes:
            self.thematic_index[theme.value].discard(memory.id)
        
        # Emotional index
        for emotion in memory.emotional_context:
            self.emotional_index[emotion].discard(memory.id)
        
        # Causal index
        for cause_id in memory.causal_links:
            self.causal_index[cause_id].discard(memory.id)
        
        # Trigger index
        for trigger in memory.triggers:
            self.trigger_index[trigger].discard(memory.id)

    def _find_causal_associations(self, memory: MemoryNode):
        """Find causal associations with existing memories."""
        # Simple keyword-based causal inference
        content_text = json.dumps(memory.content).lower()
        
        for existing_memory in self.memories.values():
            if existing_memory.id == memory.id:
                continue
            
            existing_text = json.dumps(existing_memory.content).lower()
            
            # Check for causal keywords
            causal_keywords = ['because', 'since', 'after', 'before', 'caused', 'led to', 'resulted in']
            for keyword in causal_keywords:
                if keyword in content_text and any(word in existing_text for word in memory.triggers):
                    # Potential causal relationship
                    memory.add_causal_link(existing_memory.id)
                    existing_memory.add_causal_effect(memory.id)
                    break

    def _matches_query(self, memory: MemoryNode, query: str) -> bool:
        """Check if memory matches a text query."""
        query_lower = query.lower()
        content_text = json.dumps(memory.content).lower()
        
        # Check content
        if query_lower in content_text:
            return True
        
        # Check triggers
        for trigger in memory.triggers:
            if query_lower in trigger.lower():
                return True
        
        # Check thematic tags
        for tag in memory.thematic_tags:
            if query_lower in tag.lower():
                return True
        
        return False

    def _get_thematic_summary(self) -> Dict[str, Any]:
        """Get summary of current thematic elements."""
        themes = defaultdict(int)
        for memory in self.memories.values():
            for theme in memory.narrative_themes:
                themes[theme.value] += 1
        
        return dict(themes)

    def _get_emotional_context(self) -> Dict[str, float]:
        """Get current emotional context summary."""
        emotions = defaultdict(float)
        for memory in self.memories.values():
            for emotion in memory.emotional_context:
                emotions[emotion.value] += memory.emotional_weight
        
        return dict(emotions)

    def _get_causal_chains(self) -> List[Dict[str, Any]]:
        """Get current causal chains for context."""
        chains = []
        processed = set()
        
        for memory in self.memories.values():
            if memory.id in processed or not memory.causal_links:
                continue
            
            chain = {
                'root_memory': memory.id,
                'chain': [memory.id] + memory.causal_links[:3]  # Limit chain length
            }
            chains.append(chain)
            processed.update(chain['chain'])
        
        return chains

    def to_dict(self) -> Dict[str, Any]:
        """Convert engine state to dictionary for serialization."""
        return {
            'campaign_id': self.campaign_id,
            'session_id': self.session_id,
            'memories': {mid: mem.to_dict() for mid, mem in self.memories.items()},
            'characters': {cid: char.to_dict() for cid, char in self.characters.items()},
            'world_state': self.world_state.to_dict(),
            'stats': self.stats
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeEngine':
        """Create engine from dictionary for deserialization."""
        engine = cls(campaign_id=data['campaign_id'])
        engine.session_id = data['session_id']
        
        # Load memories
        for mid, mem_data in data['memories'].items():
            memory = MemoryNode.from_dict(mem_data)
            engine.memories[mid] = memory
            engine._update_indexes(memory)
        
        # Load characters
        for cid, char_data in data['characters'].items():
            character = Character.from_dict(char_data)
            engine.characters[cid] = character
        
        # Load world state
        engine.world_state = WorldState.from_dict(data['world_state'])
        
        # Load statistics
        engine.stats.update(data['stats'])
        
        return engine 