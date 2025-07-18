"""
Shared types and utilities for The Narrative Engine.
Following Cursor's conventions for modular architecture.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Types of memory entries."""
    FACT = "fact"
    EMOTION = "emotion"
    CHARACTER = "character"
    EVENT = "event"
    RELATIONSHIP = "relationship"
    INSIGHT = "insight"
    PATTERN = "pattern"
    GOAL = "goal"
    DECISION = "decision"
    CHANGE = "change"

@dataclass
class MemoryEntry:
    """A single memory entry with metadata."""
    id: str
    content: str
    memory_type: MemoryType
    timestamp: datetime
    tags: List[str]
    emotional_weight: float = 0.0
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['memory_type'] = self.memory_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['memory_type'] = MemoryType(data['memory_type'])
        return cls(**data)

@dataclass
class ConversationTurn:
    """A single turn in the conversation."""
    user_input: str
    system_response: str
    timestamp: datetime
    memory_accessed: List[str] = None
    
    def __post_init__(self):
        if self.memory_accessed is None:
            self.memory_accessed = []

@dataclass
class EngineConfig:
    """Configuration for the narrative engine."""
    model_name: str = "llama3"
    temperature: float = 0.7
    max_tokens: int = 500
    memory_retrieval_limit: int = 5
    enable_emotional_memory: bool = True
    enable_semantic_search: bool = True 