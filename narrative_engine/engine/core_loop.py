"""
Core engine loop for The Narrative Engine.
Following Cursor's AgentManager pattern but adapted for storytelling.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Import shared types and modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import ConversationTurn, EngineConfig, MemoryType
from memory.memory_manager import MemoryManager
from llm_interface import LLMProvider

class NarrativeEngineCore:
    """Core orchestration engine for narrative continuity."""
    
    def __init__(self, 
                 llm_provider: LLMProvider,
                 config: EngineConfig = None,
                 memory_file: str = "narrative_memory.json"):
        self.llm_provider = llm_provider
        self.config = config or EngineConfig()
        self.memory_manager = MemoryManager(memory_file)
        self.conversation_history: List[ConversationTurn] = []
        self.current_context = ""
        
        logger.info("Narrative Engine Core initialized")
    
    def process_input(self, user_input: str) -> str:
        """Process user input and generate a narrative response."""
        logger.info(f"Processing input: {user_input[:50]}...")
        
        # Step 1: Extract facts from user input
        extracted_facts = self.memory_manager.extract_facts_from_input(user_input)
        logger.info(f"Extracted {len(extracted_facts)} facts from input")
        
        # Step 2: Search for relevant memories
        relevant_memories = self.memory_manager.search_memories(
            user_input, 
            limit=self.config.memory_retrieval_limit
        )
        logger.info(f"Found {len(relevant_memories)} relevant memories")
        
        # Step 3: Build context from memories
        memory_context = self.memory_manager.format_memories_for_context(relevant_memories)
        
        # Step 4: Generate response using LLM
        response = self.llm_provider.generate_narrative_response(
            user_input=user_input,
            context=self.current_context,
            memory_context=memory_context
        )
        
        # Step 5: Record the conversation turn
        turn = ConversationTurn(
            user_input=user_input,
            system_response=response,
            timestamp=datetime.now(),
            memory_accessed=[m.id for m in relevant_memories]
        )
        self.conversation_history.append(turn)
        
        # Step 6: Update current context
        self._update_context(user_input, response, relevant_memories)
        
        logger.info(f"Generated response: {response[:100]}...")
        return response
    
    def _update_context(self, user_input: str, response: str, memories: List):
        """Update the current narrative context."""
        # Simple context update for MVP
        # In production, this would use more sophisticated context management
        context_parts = []
        
        # Add recent conversation
        if self.conversation_history:
            recent_turns = self.conversation_history[-3:]  # Last 3 turns
            for turn in recent_turns:
                context_parts.append(f"User: {turn.user_input}")
                context_parts.append(f"System: {turn.system_response}")
        
        # Add relevant memories
        if memories:
            context_parts.append("Relevant Context:")
            for memory in memories:
                context_parts.append(f"- {memory.content}")
        
        self.current_context = "\n".join(context_parts)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation and memory state."""
        return {
            "total_turns": len(self.conversation_history),
            "total_memories": len(self.memory_manager.memories),
            "memory_types": {
                memory_type.value: len(self.memory_manager.get_memories_by_type(memory_type))
                for memory_type in MemoryType
            },
            "recent_memories": [
                {
                    "content": m.content,
                    "type": m.memory_type.value,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in self.memory_manager.get_recent_memories(5)
            ],
            "llm_available": self.llm_provider.is_available
        }
    
    def add_memory_manually(self, 
                           content: str, 
                           memory_type: MemoryType,
                           tags: List[str] = None) -> str:
        """Manually add a memory entry."""
        return self.memory_manager.add_memory(
            content=content,
            memory_type=memory_type,
            tags=tags or []
        )
    
    def search_memories(self, query: str, limit: int = 5) -> List:
        """Search memories and return formatted results."""
        memories = self.memory_manager.search_memories(query, limit=limit)
        return [
            {
                "id": m.id,
                "content": m.content,
                "type": m.memory_type.value,
                "tags": m.tags,
                "timestamp": m.timestamp.isoformat()
            }
            for m in memories
        ]
    
    def clear_memories(self):
        """Clear all memories (for testing)."""
        self.memory_manager.memories = []
        self.memory_manager.save_memories()
        logger.info("All memories cleared")
    
    def save_state(self):
        """Save the current state."""
        self.memory_manager.save_memories()
        logger.info("Engine state saved") 