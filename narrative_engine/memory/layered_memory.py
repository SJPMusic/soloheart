"""
Layered Memory System - The Narrative Engine
============================================

Implements the memory framework from Chapter 3: Memory as Narrative Context
- Layered memory (short/mid/long-term)
- Memory decay and priority weighting
- Personalization through memory
- Nonlinear memory models
- Emotional context and thematic tagging
"""

import json
import hashlib
from typing import Dict, List, Any, Optional, Deque
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# --- Memory Layer and Types ---

class MemoryLayer(Enum):
    SHORT_TERM = "short_term"    # Immediate context (last N exchanges)
    MID_TERM = "mid_term"        # Session-level (goals, arcs, unresolved threads)
    LONG_TERM = "long_term"      # Campaign/world-level (lore, history, relationships)

class MemoryType(Enum):
    EVENT = "event"
    DECISION = "decision"
    EMOTION = "emotion"
    RELATIONSHIP = "relationship"
    THEME = "theme"
    WORLD_STATE = "world_state"
    CALLBACK = "callback"
    FORESHADOW = "foreshadow"
    CHARACTER_DEVELOPMENT = "character_development"
    PLOT_POINT = "plot_point"

class EmotionalContext(Enum):
    JOY = "joy"
    FEAR = "fear"
    ANGER = "anger"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    DISGUST = "disgust"
    LOVE = "love"
    HOPE = "hope"
    DESPAIR = "despair"
    CURIOSITY = "curiosity"

@dataclass
class MemoryNode:
    """
    Represents a single memory in the narrative engine.
    Supports decay, reinforcement, emotional context, and associations.
    """
    id: str
    content: Dict[str, Any]
    memory_type: MemoryType
    layer: MemoryLayer
    timestamp: datetime
    emotional_weight: float  # 0.0 to 1.0
    emotional_context: List[EmotionalContext]
    thematic_tags: List[str]
    user_id: str
    session_id: str
    decay_rate: float
    reinforcement_count: int
    last_accessed: datetime
    associations: List[str]  # Related memory IDs
    triggers: List[str]      # Keywords for recall
    causal_links: List[str]  # Causal memory IDs
    personalization: Dict[str, Any]
    narrative_context: Dict[str, Any]  # Domain-specific context

    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
        if self.emotional_context is None:
            self.emotional_context = []
        if self.thematic_tags is None:
            self.thematic_tags = []
        if self.associations is None:
            self.associations = []
        if self.triggers is None:
            self.triggers = []
        if self.causal_links is None:
            self.causal_links = []
        if self.personalization is None:
            self.personalization = {}
        if self.narrative_context is None:
            self.narrative_context = {}

    def _generate_id(self) -> str:
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.md5((content_str + self.layer.value + self.memory_type.value + self.timestamp.isoformat()).encode()).hexdigest()[:16]

    def get_significance(self, now: Optional[datetime] = None) -> float:
        """
        Returns a significance score based on emotional weight, decay, and reinforcement.
        Implements the forgetting as function concept from Chapter 3.
        """
        now = now or datetime.utcnow()
        age_hours = (now - self.timestamp).total_seconds() / 3600
        decay = max(0.1, 1.0 - (age_hours * self.decay_rate))
        reinforcement = min(0.5, self.reinforcement_count * 0.1)
        recency = max(0.0, 0.3 * (1.0 - ((now - self.last_accessed).total_seconds() / 86400)))
        layer_mult = {MemoryLayer.SHORT_TERM: 0.5, MemoryLayer.MID_TERM: 1.0, MemoryLayer.LONG_TERM: 1.5}[self.layer]
        return (self.emotional_weight * decay + reinforcement + recency) * layer_mult

    def reinforce(self):
        """Reinforce this memory, reducing decay rate and updating access time."""
        self.reinforcement_count += 1
        self.decay_rate = max(0.01, self.decay_rate * 0.9)
        self.last_accessed = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'layer': self.layer.value,
            'timestamp': self.timestamp.isoformat(),
            'emotional_weight': self.emotional_weight,
            'emotional_context': [e.value for e in self.emotional_context],
            'thematic_tags': self.thematic_tags,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'decay_rate': self.decay_rate,
            'reinforcement_count': self.reinforcement_count,
            'last_accessed': self.last_accessed.isoformat(),
            'associations': self.associations,
            'triggers': self.triggers,
            'causal_links': self.causal_links,
            'personalization': self.personalization,
            'narrative_context': self.narrative_context,
            'significance': self.get_significance()
        }

class LayeredMemorySystem:
    """
    Modular, narrative-context memory system implementing Chapter 3 concepts.
    Supports layered storage, decay, personalization, and nonlinear recall.
    """
    
    def __init__(self, campaign_id: str = "default"):
        self.campaign_id = campaign_id
        self.short_term: Deque[MemoryNode] = deque(maxlen=50)
        self.mid_term: Dict[str, MemoryNode] = {}
        self.long_term: Dict[str, MemoryNode] = {}
        
        # Indexes for efficient recall
        self.indexes = {
            'emotional': defaultdict(list),
            'thematic': defaultdict(list),
            'user': defaultdict(list),
            'trigger': defaultdict(list),
            'character': defaultdict(list),
            'plot': defaultdict(list)
        }
        
        # User profiles for personalization
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Forgotten memories (for analysis)
        self.forgotten: List[Dict[str, Any]] = []
        
        # Statistics
        self.stats = {'created': 0, 'forgotten': 0, 'reinforced': 0, 'recalled': 0}

    def add_memory(self, content: Dict[str, Any], memory_type: MemoryType, layer: MemoryLayer, 
                   user_id: str, session_id: str, emotional_weight: float = 0.5, 
                   emotional_context: List[EmotionalContext] = None, thematic_tags: List[str] = None, 
                   triggers: List[str] = None, personalization: Dict[str, Any] = None,
                   narrative_context: Dict[str, Any] = None) -> str:
        """
        Add a new memory node to the appropriate layer and update indexes.
        Implements the memory as narrative context concept.
        """
        now = datetime.utcnow()
        decay_rate = self._calculate_decay_rate(layer, emotional_weight)
        
        node = MemoryNode(
            id=None,
            content=content,
            memory_type=memory_type,
            layer=layer,
            timestamp=now,
            emotional_weight=emotional_weight,
            emotional_context=emotional_context or [],
            thematic_tags=thematic_tags or [],
            user_id=user_id,
            session_id=session_id,
            decay_rate=decay_rate,
            reinforcement_count=0,
            last_accessed=now,
            associations=[],
            triggers=triggers or self._extract_triggers(content),
            causal_links=[],
            personalization=personalization or {},
            narrative_context=narrative_context or {}
        )
        
        # Store in appropriate layer
        if layer == MemoryLayer.SHORT_TERM:
            self.short_term.append(node)
        elif layer == MemoryLayer.MID_TERM:
            self.mid_term[node.id] = node
        else:
            self.long_term[node.id] = node
        
        # Update indexes
        self._update_indexes(node)
        
        # Update user profile
        self._update_user_profile(user_id, node)
        
        # Find associations with existing memories
        self._find_associations(node)
        
        self.stats['created'] += 1
        logger.info(f"Added memory to {layer.value}: {memory_type.value}")
        
        return node.id

    def recall(self, query: str = None, emotional: EmotionalContext = None, 
               thematic: List[str] = None, user_id: str = None, layer: MemoryLayer = None, 
               min_significance: float = 0.0, limit: int = 10) -> List[MemoryNode]:
        """
        Recall memories using nonlinear, associative methods.
        Implements the nonlinear memory models concept from Chapter 3.
        """
        candidates = []
        
        # Get all memories from specified layer(s)
        if layer:
            memories = self._get_layer_memories(layer)
        else:
            memories = list(self.short_term) + list(self.mid_term.values()) + list(self.long_term.values())
        
        # Filter by significance
        memories = [m for m in memories if m.get_significance() >= min_significance]
        
        # Apply filters
        if emotional:
            memories = [m for m in memories if emotional in m.emotional_context]
        
        if thematic:
            memories = [m for m in memories if any(tag in m.thematic_tags for tag in thematic)]
        
        if user_id:
            memories = [m for m in memories if m.user_id == user_id]
        
        # Query-based filtering
        if query:
            query_lower = query.lower()
            memories = [m for m in memories if self._matches_query(m, query_lower)]
        
        # Sort by significance and recency
        memories.sort(key=lambda m: (m.get_significance(), m.last_accessed), reverse=True)
        
        # Reinforce recalled memories
        for memory in memories[:limit]:
            memory.reinforce()
            self.stats['recalled'] += 1
        
        return memories[:limit]

    def forget(self, threshold: float = 0.1):
        """
        Implement forgetting as function from Chapter 3.
        Remove memories below significance threshold.
        """
        now = datetime.utcnow()
        
        # Check short-term memories
        to_remove = []
        for memory in self.short_term:
            if memory.get_significance(now) < threshold:
                to_remove.append(memory)
        
        for memory in to_remove:
            self.short_term.remove(memory)
            self.forgotten.append(memory.to_dict())
            self.stats['forgotten'] += 1
        
        # Check mid-term memories
        to_remove = []
        for memory_id, memory in self.mid_term.items():
            if memory.get_significance(now) < threshold:
                to_remove.append(memory_id)
        
        for memory_id in to_remove:
            memory = self.mid_term.pop(memory_id)
            self.forgotten.append(memory.to_dict())
            self.stats['forgotten'] += 1
        
        # Check long-term memories
        to_remove = []
        for memory_id, memory in self.long_term.items():
            if memory.get_significance(now) < threshold:
                to_remove.append(memory_id)
        
        for memory_id in to_remove:
            memory = self.long_term.pop(memory_id)
            self.forgotten.append(memory.to_dict())
            self.stats['forgotten'] += 1

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get personalized user profile based on their memory patterns."""
        return self.user_profiles.get(user_id, {})

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            'total_memories': len(self.short_term) + len(self.mid_term) + len(self.long_term),
            'short_term_count': len(self.short_term),
            'mid_term_count': len(self.mid_term),
            'long_term_count': len(self.long_term),
            'forgotten_count': len(self.forgotten),
            'stats': self.stats
        }

    def export_memories(self) -> Dict[str, Any]:
        """Export all memories for save/load functionality."""
        return {
            'short_term': [node.to_dict() for node in self.short_term],
            'mid_term': [node.to_dict() for node in self.mid_term.values()],
            'long_term': [node.to_dict() for node in self.long_term.values()],
            'forgotten': self.forgotten,
            'user_profiles': self.user_profiles,
            'stats': self.stats
        }

    def import_memories(self, data: Dict[str, Any]):
        """Import memories from save/load data."""
        # Clear existing memories
        self.short_term.clear()
        self.mid_term.clear()
        self.long_term.clear()
        self.forgotten.clear()
        
        # Import short-term memories
        for mem_data in data.get('short_term', []):
            node = self._node_from_dict(mem_data)
            self.short_term.append(node)
        
        # Import mid-term memories
        for mem_data in data.get('mid_term', []):
            node = self._node_from_dict(mem_data)
            self.mid_term[node.id] = node
        
        # Import long-term memories
        for mem_data in data.get('long_term', []):
            node = self._node_from_dict(mem_data)
            self.long_term[node.id] = node
        
        # Import forgotten memories
        self.forgotten = data.get('forgotten', [])
        
        # Import user profiles
        self.user_profiles = data.get('user_profiles', {})
        
        # Import stats
        self.stats = data.get('stats', self.stats)
        
        # Rebuild indexes
        self._rebuild_indexes()
    
    def _rebuild_indexes(self):
        """Rebuild all indexes after import."""
        self.indexes = {
            'emotional': defaultdict(list),
            'thematic': defaultdict(list),
            'user': defaultdict(list),
            'trigger': defaultdict(list),
            'character': defaultdict(list),
            'plot': defaultdict(list)
        }
        
        # Rebuild indexes for all memories
        for node in list(self.short_term) + list(self.mid_term.values()) + list(self.long_term.values()):
            self._update_indexes(node)

    def _calculate_decay_rate(self, layer: MemoryLayer, emotional_weight: float) -> float:
        """Calculate decay rate based on layer and emotional weight."""
        base_rates = {
            MemoryLayer.SHORT_TERM: 0.5,
            MemoryLayer.MID_TERM: 0.1,
            MemoryLayer.LONG_TERM: 0.02
        }
        base_rate = base_rates[layer]
        # Emotional weight reduces decay rate
        return base_rate * (1.0 - (emotional_weight * 0.5))

    def _extract_triggers(self, content: Dict[str, Any]) -> List[str]:
        """Extract trigger keywords from content."""
        text = json.dumps(content).lower()
        # Simple keyword extraction - could be enhanced with NLP
        words = [w for w in text.split() if len(w) > 3 and w.isalpha()]
        return list(set(words))[:10]

    def _update_indexes(self, node: MemoryNode):
        """Update all indexes for efficient recall."""
        # Emotional index
        for emotion in node.emotional_context:
            self.indexes['emotional'][emotion.value].append(node.id)
        
        # Thematic index
        for tag in node.thematic_tags:
            self.indexes['thematic'][tag].append(node.id)
        
        # User index
        self.indexes['user'][node.user_id].append(node.id)
        
        # Trigger index
        for trigger in node.triggers:
            self.indexes['trigger'][trigger].append(node.id)
        
        # Character index (if content contains character info)
        if 'character' in node.content:
            char_name = node.content['character']
            self.indexes['character'][char_name].append(node.id)
        
        # Plot index (if content contains plot info)
        if 'plot' in node.content:
            plot_id = node.content['plot']
            self.indexes['plot'][plot_id].append(node.id)

    def _update_user_profile(self, user_id: str, node: MemoryNode):
        """Update user profile based on new memory."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'emotional_preferences': defaultdict(int),
                'thematic_interests': defaultdict(int),
                'memory_patterns': [],
                'last_activity': node.timestamp
            }
        
        profile = self.user_profiles[user_id]
        
        # Update emotional preferences
        for emotion in node.emotional_context:
            profile['emotional_preferences'][emotion.value] += 1
        
        # Update thematic interests
        for tag in node.thematic_tags:
            profile['thematic_interests'][tag] += 1
        
        # Update memory patterns
        profile['memory_patterns'].append({
            'type': node.memory_type.value,
            'layer': node.layer.value,
            'emotional_weight': node.emotional_weight,
            'timestamp': node.timestamp.isoformat()
        })
        
        # Keep only recent patterns
        profile['memory_patterns'] = profile['memory_patterns'][-100:]
        profile['last_activity'] = node.timestamp

    def _find_associations(self, node: MemoryNode):
        """Find associations between new memory and existing memories."""
        # Find memories with similar themes
        for tag in node.thematic_tags:
            if tag in self.indexes['thematic']:
                for memory_id in self.indexes['thematic'][tag]:
                    if memory_id != node.id:
                        node.associations.append(memory_id)
        
        # Find memories with similar emotional context
        for emotion in node.emotional_context:
            if emotion.value in self.indexes['emotional']:
                for memory_id in self.indexes['emotional'][emotion.value]:
                    if memory_id != node.id:
                        node.associations.append(memory_id)
        
        # Remove duplicates
        node.associations = list(set(node.associations))

    def _get_layer_memories(self, layer: MemoryLayer) -> List[MemoryNode]:
        """Get all memories from a specific layer."""
        if layer == MemoryLayer.SHORT_TERM:
            return list(self.short_term)
        elif layer == MemoryLayer.MID_TERM:
            return list(self.mid_term.values())
        else:
            return list(self.long_term.values())

    def _matches_query(self, memory: MemoryNode, query: str) -> bool:
        """Check if memory matches query."""
        # Check triggers
        if any(trigger in query for trigger in memory.triggers):
            return True
        
        # Check thematic tags
        if any(tag in query for tag in memory.thematic_tags):
            return True
        
        # Check content
        content_str = json.dumps(memory.content).lower()
        if query in content_str:
            return True
        
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize memory system to dictionary."""
        return {
            'campaign_id': self.campaign_id,
            'short_term': [m.to_dict() for m in self.short_term],
            'mid_term': {k: v.to_dict() for k, v in self.mid_term.items()},
            'long_term': {k: v.to_dict() for k, v in self.long_term.items()},
            'user_profiles': self.user_profiles,
            'forgotten': self.forgotten,
            'stats': self.stats
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LayeredMemorySystem':
        """Deserialize memory system from dictionary."""
        system = cls(data['campaign_id'])
        
        # Restore short-term memories
        for mem_data in data['short_term']:
            node = cls._node_from_dict(mem_data)
            system.short_term.append(node)
        
        # Restore mid-term memories
        for mem_data in data['mid_term'].values():
            node = cls._node_from_dict(mem_data)
            system.mid_term[node.id] = node
        
        # Restore long-term memories
        for mem_data in data['long_term'].values():
            node = cls._node_from_dict(mem_data)
            system.long_term[node.id] = node
        
        # Restore other data
        system.user_profiles = data['user_profiles']
        system.forgotten = data['forgotten']
        system.stats = data['stats']
        
        # Rebuild indexes
        for memory in list(system.short_term) + list(system.mid_term.values()) + list(system.long_term.values()):
            system._update_indexes(memory)
        
        return system

    @staticmethod
    def _node_from_dict(data: Dict[str, Any]) -> MemoryNode:
        """Create MemoryNode from dictionary."""
        return MemoryNode(
            id=data['id'],
            content=data['content'],
            memory_type=MemoryType(data['memory_type']),
            layer=MemoryLayer(data['layer']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            emotional_weight=data['emotional_weight'],
            emotional_context=[EmotionalContext(e) for e in data['emotional_context']],
            thematic_tags=data['thematic_tags'],
            user_id=data['user_id'],
            session_id=data['session_id'],
            decay_rate=data['decay_rate'],
            reinforcement_count=data['reinforcement_count'],
            last_accessed=datetime.fromisoformat(data['last_accessed']),
            associations=data['associations'],
            triggers=data['triggers'],
            causal_links=data['causal_links'],
            personalization=data['personalization'],
            narrative_context=data.get('narrative_context', {})
        ) 