"""
Enhanced Memory System - Narrative Context Engine (Chapter 3)
============================================================

Implements:
- Layered memory (short/mid/long-term)
- Memory decay and priority weighting
- Personalization (user modeling)
- Nonlinear recall (emotional/contextual triggers)
- Modular, extensible API for narrative and non-narrative use
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Deque
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque

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

class EmotionalContext(Enum):
    JOY = "joy"
    FEAR = "fear"
    ANGER = "anger"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    DISGUST = "disgust"

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

    def _generate_id(self) -> str:
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.md5((content_str + self.layer.value + self.memory_type.value + self.timestamp.isoformat()).encode()).hexdigest()[:16]

    def get_significance(self, now: Optional[datetime] = None) -> float:
        """
        Returns a significance score based on emotional weight, decay, and reinforcement.
        """
        now = now or datetime.utcnow()
        age_hours = (now - self.timestamp).total_seconds() / 3600
        decay = max(0.1, 1.0 - (age_hours * self.decay_rate))
        reinforcement = min(0.5, self.reinforcement_count * 0.1)
        recency = max(0.0, 0.3 * (1.0 - ((now - self.last_accessed).total_seconds() / 86400)))
        layer_mult = {MemoryLayer.SHORT_TERM: 0.5, MemoryLayer.MID_TERM: 1.0, MemoryLayer.LONG_TERM: 1.5}[self.layer]
        return (self.emotional_weight * decay + reinforcement + recency) * layer_mult

    def reinforce(self):
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
            'significance': self.get_significance()
        }

# --- Layered Memory System ---

class LayeredMemorySystem:
    """
    Modular, narrative-context memory system for DnD and beyond.
    Supports layered storage, decay, personalization, and nonlinear recall.
    """
    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        self.short_term: Deque[MemoryNode] = deque(maxlen=50)
        self.mid_term: Dict[str, MemoryNode] = {}
        self.long_term: Dict[str, MemoryNode] = {}
        self.indexes = {
            'emotional': defaultdict(list),
            'thematic': defaultdict(list),
            'user': defaultdict(list),
            'trigger': defaultdict(list)
        }
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.forgotten: List[Dict[str, Any]] = []
        self.stats = {'created': 0, 'forgotten': 0, 'reinforced': 0}

    def add_memory(self, content: Dict[str, Any], memory_type: MemoryType, layer: MemoryLayer, user_id: str, session_id: str, emotional_weight: float = 0.5, emotional_context: List[EmotionalContext] = None, thematic_tags: List[str] = None, triggers: List[str] = None, personalization: Dict[str, Any] = None) -> str:
        """
        Add a new memory node to the appropriate layer and update indexes.
        """
        now = datetime.utcnow()
        decay_rate = self._decay_rate(layer, emotional_weight)
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
            personalization=personalization or {}
        )
        if layer == MemoryLayer.SHORT_TERM:
            self.short_term.append(node)
        elif layer == MemoryLayer.MID_TERM:
            self.mid_term[node.id] = node
        else:
            self.long_term[node.id] = node
        self._update_indexes(node)
        self._update_user_profile(user_id, node)
        self.stats['created'] += 1
        return node.id

    def _decay_rate(self, layer: MemoryLayer, emotional_weight: float) -> float:
        base = {MemoryLayer.SHORT_TERM: 0.5, MemoryLayer.MID_TERM: 0.1, MemoryLayer.LONG_TERM: 0.02}[layer]
        return base * (1.0 - (emotional_weight * 0.5))

    def _extract_triggers(self, content: Dict[str, Any]) -> List[str]:
        text = json.dumps(content).lower()
        return [w for w in text.split() if len(w) > 3 and w.isalpha()][:10]

    def _update_indexes(self, node: MemoryNode):
        for e in node.emotional_context:
            self.indexes['emotional'][e].append(node.id)
        for t in node.thematic_tags:
            self.indexes['thematic'][t].append(node.id)
        self.indexes['user'][node.user_id].append(node.id)
        for trig in node.triggers:
            self.indexes['trigger'][trig].append(node.id)

    def _update_user_profile(self, user_id: str, node: MemoryNode):
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {'preferences': {}, 'emotions': defaultdict(int), 'themes': defaultdict(int)}
        profile = self.user_profiles[user_id]
        for e in node.emotional_context:
            profile['emotions'][e.value] += 1
        for t in node.thematic_tags:
            profile['themes'][t] += 1

    def recall(self, query: str = None, emotional: EmotionalContext = None, thematic: List[str] = None, user_id: str = None, layer: MemoryLayer = None, min_significance: float = 0.0) -> List[MemoryNode]:
        """
        Recall memories by query, emotion, theme, user, or layer, sorted by significance.
        """
        memories = []
        if layer == MemoryLayer.SHORT_TERM or layer is None:
            memories.extend(list(self.short_term))
        if layer == MemoryLayer.MID_TERM or layer is None:
            memories.extend(self.mid_term.values())
        if layer == MemoryLayer.LONG_TERM or layer is None:
            memories.extend(self.long_term.values())
        result = []
        for m in memories:
            if m.get_significance() < min_significance:
                continue
            if emotional and emotional not in m.emotional_context:
                continue
            if thematic and not any(t in m.thematic_tags for t in thematic):
                continue
            if user_id and m.user_id != user_id:
                continue
            if query:
                text = json.dumps(m.content).lower()
                if query.lower() not in text and not any(trig in query.lower() for trig in m.triggers):
                    continue
            result.append(m)
        result.sort(key=lambda m: m.get_significance(), reverse=True)
        for m in result[:5]:
            m.reinforce()
            self.stats['reinforced'] += 1
        return result

    def forget(self, threshold: float = 0.1):
        """
        Forget (remove) memories below a significance threshold.
        """
        forgotten = []
        for d in [self.mid_term, self.long_term]:
            for k, m in list(d.items()):
                if m.get_significance() < threshold:
                    forgotten.append(m.to_dict())
                    del d[k]
        self.forgotten.extend(forgotten)
        self.stats['forgotten'] += len(forgotten)

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        return self.user_profiles.get(user_id, {})

    def stats_summary(self) -> Dict[str, Any]:
        return {
            **self.stats,
            'short_term': len(self.short_term),
            'mid_term': len(self.mid_term),
            'long_term': len(self.long_term),
            'forgotten': len(self.forgotten),
            'users': len(self.user_profiles)
        }

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics for web interface compatibility"""
        stats = self.stats_summary()
        
        # Calculate total memories
        total_memories = stats['short_term'] + stats['mid_term'] + stats['long_term']
        
        # Calculate memory types distribution
        memory_types = {
            'short_term': stats['short_term'],
            'mid_term': stats['mid_term'], 
            'long_term': stats['long_term']
        }
        
        # Calculate average priority (emotional weight)
        all_memories = list(self.short_term) + list(self.mid_term.values()) + list(self.long_term.values())
        if all_memories:
            average_priority = sum(m.emotional_weight for m in all_memories) / len(all_memories)
        else:
            average_priority = 0.0
        
        return {
            'total_memories': total_memories,
            'memory_types': memory_types,
            'average_priority': average_priority,
            'users': stats['users'],
            'created': stats['created'],
            'forgotten': stats['forgotten'],
            'reinforced': stats['reinforced']
        }

    def to_dict(self) -> Dict[str, Any]:
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
        sys = cls(data['campaign_id'])
        for m in data.get('short_term', []):
            sys.short_term.append(cls._node_from_dict(m))
        for k, v in data.get('mid_term', {}).items():
            sys.mid_term[k] = cls._node_from_dict(v)
        for k, v in data.get('long_term', {}).items():
            sys.long_term[k] = cls._node_from_dict(v)
        sys.user_profiles = data.get('user_profiles', {})
        sys.forgotten = data.get('forgotten', [])
        sys.stats = data.get('stats', sys.stats)
        for m in list(sys.short_term) + list(sys.mid_term.values()) + list(sys.long_term.values()):
            sys._update_indexes(m)
        return sys

    @staticmethod
    def _node_from_dict(data: Dict[str, Any]) -> MemoryNode:
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
            personalization=data['personalization']
        ) 