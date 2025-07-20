"""
Memory Tracker for SoloHeart Runtime

Manages memory storage and retrieval using NarrativeEngineProxy for all TNE communication.
Handles episodic, symbolic, and emotional memory layers.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from runtime.narrative_engine_proxy import NarrativeEngineProxy

logger = logging.getLogger(__name__)


class MemoryTracker:
    """
    Manages memory storage and retrieval for SoloHeart.
    
    Uses NarrativeEngineProxy for all TNE communication to maintain
    clean separation between SoloHeart and TNE implementation.
    """
    
    def __init__(self, campaign_id: str, base_url: str = "http://localhost:5002"):
        """
        Initialize the Memory Tracker.
        
        Args:
            campaign_id: The campaign ID for memory tracking
            base_url: The TNE API base URL
        """
        self.campaign_id = campaign_id
        self.proxy = NarrativeEngineProxy(campaign_id, base_url)
        self.local_memory_cache = []
        
        logger.info(f"Memory Tracker initialized for campaign {campaign_id}")
    
    def add_memory(
        self,
        content: str,
        memory_type: str = "event",
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        emotional_context: Optional[List[str]] = None,
        primary_emotion: Optional[str] = None,
        emotional_intensity: float = 0.5,
        character_id: str = "player"
    ) -> bool:
        """
        Add a memory entry using NarrativeEngineProxy.
        
        Args:
            content: The memory content
            memory_type: Type of memory (event, character, location, etc.)
            metadata: Optional metadata about the memory
            tags: Optional tags for categorization
            emotional_context: Optional emotional context
            primary_emotion: Primary emotion associated with the memory
            emotional_intensity: Intensity of the emotion (0.0 to 1.0)
            character_id: ID of the character this memory belongs to
            
        Returns:
            True if memory was added successfully, False otherwise
        """
        try:
            # Prepare memory entry
            memory_entry = {
                "text": content,
                "metadata": {
                    "memory_type": memory_type,
                    "tags": tags or [],
                    "emotional_context": emotional_context or [],
                    "primary_emotion": primary_emotion,
                    "emotional_intensity": emotional_intensity,
                    "campaign_id": self.campaign_id,
                    "character_id": character_id,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            if metadata:
                memory_entry["metadata"].update(metadata)
            
            # Add memory via proxy
            result = self.proxy.add_memory(memory_entry)
            
            if result.get('status') == 'success':
                # Cache locally for quick access
                local_memory = {
                    "content": content,
                    "memory_type": memory_type,
                    "metadata": memory_entry["metadata"],
                    "added_at": datetime.now().isoformat()
                }
                self.local_memory_cache.append(local_memory)
                
                logger.info(f"Memory added successfully: {content[:50]}...")
                return True
            else:
                logger.error(f"Failed to add memory: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return False
    
    def add_episodic_memory(
        self,
        event_description: str,
        location: str,
        participants: List[str],
        outcome: str,
        emotional_impact: Optional[str] = None
    ) -> bool:
        """
        Add an episodic memory (specific event memory).
        
        Args:
            event_description: Description of the event
            location: Where the event took place
            participants: Who was involved
            outcome: What happened as a result
            emotional_impact: Optional emotional impact of the event
            
        Returns:
            True if episodic memory was added successfully
        """
        metadata = {
            "location": location,
            "participants": participants,
            "outcome": outcome
        }
        
        if emotional_impact:
            metadata["emotional_impact"] = emotional_impact
        
        return self.add_memory(
            content=event_description,
            memory_type="episodic",
            metadata=metadata
        )
    
    def add_symbolic_memory(
        self,
        concept: str,
        meaning: str,
        associations: List[str],
        importance: float = 0.5
    ) -> bool:
        """
        Add a symbolic memory (conceptual/meaning-based memory).
        
        Args:
            concept: The concept or symbol
            meaning: What it represents or means
            associations: Related concepts or ideas
            importance: Importance level (0.0 to 1.0)
            
        Returns:
            True if symbolic memory was added successfully
        """
        metadata = {
            "concept": concept,
            "meaning": meaning,
            "associations": associations,
            "importance": importance
        }
        
        return self.add_memory(
            content=f"Symbolic concept: {concept} - {meaning}",
            memory_type="symbolic",
            metadata=metadata
        )
    
    def add_emotional_memory(
        self,
        emotional_content: str,
        emotion_type: str,
        intensity: float,
        trigger: Optional[str] = None,
        duration: Optional[str] = None
    ) -> bool:
        """
        Add an emotional memory.
        
        Args:
            emotional_content: Description of the emotional experience
            emotion_type: Type of emotion (joy, fear, anger, etc.)
            intensity: Intensity of the emotion (0.0 to 1.0)
            trigger: What triggered this emotion
            duration: How long the emotion lasted
            
        Returns:
            True if emotional memory was added successfully
        """
        metadata = {
            "emotion_type": emotion_type,
            "intensity": intensity
        }
        
        if trigger:
            metadata["trigger"] = trigger
        if duration:
            metadata["duration"] = duration
        
        return self.add_memory(
            content=emotional_content,
            memory_type="emotional",
            metadata=metadata,
            primary_emotion=emotion_type,
            emotional_intensity=intensity
        )
    
    def search_memory(
        self,
        query: str,
        memory_type: Optional[str] = None,
        max_results: int = 10,
        min_relevance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for memories using NarrativeEngineProxy.
        
        Args:
            query: Search query
            memory_type: Optional filter by memory type
            max_results: Maximum number of results to return
            min_relevance: Minimum relevance score (0.0 to 1.0)
            
        Returns:
            List of matching memories
        """
        try:
            # Search via proxy
            result = self.proxy.search_memory(query)
            
            if result.get('status') == 'success':
                memories = result.get('results', [])
                
                # Apply filters
                if memory_type:
                    memories = [m for m in memories if m.get('metadata', {}).get('memory_type') == memory_type]
                
                if min_relevance > 0.0:
                    memories = [m for m in memories if m.get('relevance', 0.0) >= min_relevance]
                
                # Limit results
                memories = memories[:max_results]
                
                logger.info(f"Found {len(memories)} memories for query: {query}")
                return memories
            else:
                logger.warning(f"Failed to search memory: {result.get('error')}")
                return self._search_local_memory(query, memory_type, max_results)
                
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return self._search_local_memory(query, memory_type, max_results)
    
    def _search_local_memory(
        self,
        query: str,
        memory_type: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search local memory cache as fallback."""
        query_lower = query.lower()
        matches = []
        
        for memory in self.local_memory_cache:
            # Simple text matching
            if (query_lower in memory.get('content', '').lower() or
                query_lower in str(memory.get('metadata', {})).lower()):
                
                if memory_type and memory.get('memory_type') != memory_type:
                    continue
                
                matches.append({
                    'content': memory.get('content'),
                    'memory_type': memory.get('memory_type'),
                    'metadata': memory.get('metadata'),
                    'relevance': 0.8  # Default relevance for local matches
                })
        
        return matches[:max_results]
    
    def get_memory_summary(self) -> str:
        """
        Get a summary of all memories using NarrativeEngineProxy.
        
        Returns:
            String summary of memories
        """
        try:
            summary = self.proxy.get_summary()
            if summary and not summary.startswith("Error"):
                return summary
            else:
                logger.warning("Failed to get memory summary from TNE")
                return self._get_local_memory_summary()
                
        except Exception as e:
            logger.error(f"Error getting memory summary: {e}")
            return self._get_local_memory_summary()
    
    def _get_local_memory_summary(self) -> str:
        """Generate a local summary of memories."""
        if not self.local_memory_cache:
            return "No memories recorded yet."
        
        memory_types = {}
        for memory in self.local_memory_cache:
            memory_type = memory.get('memory_type', 'unknown')
            memory_types[memory_type] = memory_types.get(memory_type, 0) + 1
        
        summary_parts = [f"Total memories: {len(self.local_memory_cache)}"]
        for memory_type, count in memory_types.items():
            summary_parts.append(f"{memory_type}: {count}")
        
        return f"Memory Summary: {', '.join(summary_parts)}"
    
    def get_recent_memories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent memories from local cache.
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of recent memory data
        """
        return self.local_memory_cache[-limit:] if self.local_memory_cache else []
    
    def is_tne_online(self) -> bool:
        """
        Check if TNE is available for memory operations.
        
        Returns:
            True if TNE is online and available
        """
        return self.proxy.is_online() 