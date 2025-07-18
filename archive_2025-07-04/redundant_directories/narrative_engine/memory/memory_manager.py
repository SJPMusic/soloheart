"""
Memory Manager for The Narrative Engine.
Following Cursor's memory management patterns but adapted for storytelling.
"""

import json
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Import shared types
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import MemoryEntry, MemoryType

class MemoryManager:
    """Manages narrative memory with semantic search and tagging."""
    
    def __init__(self, memory_file: str = "narrative_memory.json"):
        self.memory_file = memory_file
        self.memories: List[MemoryEntry] = []
        self.load_memories()
    
    def add_memory(self, 
                   content: str, 
                   memory_type: MemoryType, 
                   tags: List[str] = None,
                   emotional_weight: float = 0.0,
                   context: Dict[str, Any] = None) -> str:
        """Add a new memory entry."""
        if tags is None:
            tags = []
        
        memory_id = str(uuid.uuid4())
        memory = MemoryEntry(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            timestamp=datetime.now(),
            tags=tags,
            emotional_weight=emotional_weight,
            context=context or {}
        )
        
        self.memories.append(memory)
        self.save_memories()
        
        logger.info(f"Added memory: {memory_type.value} - {content[:50]}...")
        return memory_id
    
    def search_memories(self, 
                       query: str, 
                       memory_types: List[MemoryType] = None,
                       limit: int = 5) -> List[MemoryEntry]:
        """Search memories by semantic similarity and tags."""
        if not self.memories:
            return []
        
        # Simple keyword-based search for MVP
        # In production, this would use embeddings for semantic search
        query_lower = query.lower()
        results = []
        
        for memory in self.memories:
            # Filter by memory type if specified
            if memory_types and memory.memory_type not in memory_types:
                continue
            
            # Check content similarity
            content_score = self._calculate_similarity(query_lower, memory.content.lower())
            
            # Check tag similarity
            tag_score = 0
            for tag in memory.tags:
                tag_score = max(tag_score, self._calculate_similarity(query_lower, tag.lower()))
            
            # Combined score
            score = max(content_score, tag_score)
            
            if score > 0.1:  # Threshold for relevance
                results.append((memory, score))
        
        # Sort by relevance score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, score in results[:limit]]
    
    def get_memories_by_type(self, memory_type: MemoryType) -> List[MemoryEntry]:
        """Get all memories of a specific type."""
        return [m for m in self.memories if m.memory_type == memory_type]
    
    def get_memories_by_tag(self, tag: str) -> List[MemoryEntry]:
        """Get all memories with a specific tag."""
        tag_lower = tag.lower()
        return [m for m in self.memories if tag_lower in [t.lower() for t in m.tags]]
    
    def get_recent_memories(self, limit: int = 10) -> List[MemoryEntry]:
        """Get the most recent memories."""
        sorted_memories = sorted(self.memories, key=lambda x: x.timestamp, reverse=True)
        return sorted_memories[:limit]
    
    def _calculate_similarity(self, query: str, text: str) -> float:
        """Calculate simple similarity score between query and text."""
        # Simple word overlap for MVP
        query_words = set(query.split())
        text_words = set(text.split())
        
        if not query_words or not text_words:
            return 0.0
        
        intersection = query_words.intersection(text_words)
        union = query_words.union(text_words)
        
        return len(intersection) / len(union)
    
    def extract_facts_from_input(self, user_input: str) -> List[MemoryEntry]:
        """Extract potential facts from user input."""
        facts = []
        
        # Simple fact extraction patterns
        fact_patterns = [
            ("met", "I met", MemoryType.CHARACTER),
            ("gave", "gave me", MemoryType.EVENT),
            ("found", "I found", MemoryType.EVENT),
            ("went to", "went to", MemoryType.EVENT),
            ("saw", "I saw", MemoryType.EVENT),
            ("talked to", "talked to", MemoryType.CHARACTER),
        ]
        
        for pattern, trigger, memory_type in fact_patterns:
            if trigger.lower() in user_input.lower():
                # Extract the relevant part of the sentence
                parts = user_input.split(trigger)
                if len(parts) > 1:
                    fact_content = f"{trigger}{parts[1]}".strip()
                    if fact_content:
                        memory_id = self.add_memory(
                            content=fact_content,
                            memory_type=memory_type,
                            tags=[pattern, "user_input"],
                            emotional_weight=0.3
                        )
                        facts.append(self.get_memory_by_id(memory_id))
        
        return facts
    
    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get a specific memory by ID."""
        for memory in self.memories:
            if memory.id == memory_id:
                return memory
        return None
    
    def format_memories_for_context(self, memories: List[MemoryEntry]) -> str:
        """Format memories for inclusion in LLM context."""
        if not memories:
            return ""
        
        formatted = []
        for memory in memories:
            formatted.append(f"- {memory.content} ({memory.memory_type.value})")
        
        return "\n".join(formatted)
    
    def save_memories(self):
        """Save memories to file."""
        try:
            data = [memory.to_dict() for memory in self.memories]
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.memories)} memories to {self.memory_file}")
        except Exception as e:
            logger.error(f"Error saving memories: {e}")
    
    def load_memories(self):
        """Load memories from file."""
        try:
            with open(self.memory_file, 'r') as f:
                data = json.load(f)
            
            self.memories = [MemoryEntry.from_dict(item) for item in data]
            logger.info(f"Loaded {len(self.memories)} memories from {self.memory_file}")
        except FileNotFoundError:
            logger.info(f"Memory file {self.memory_file} not found, starting with empty memory")
            self.memories = []
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
            self.memories = [] 