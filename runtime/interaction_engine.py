"""
Interaction Engine for SoloHeart Runtime

Manages player interactions and AI responses using NarrativeEngineProxy
for all TNE communication.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from runtime.narrative_engine_proxy import NarrativeEngineProxy

logger = logging.getLogger(__name__)


class InteractionEngine:
    """
    Manages player interactions and AI responses for SoloHeart.
    
    Uses NarrativeEngineProxy for all TNE communication to maintain
    clean separation between SoloHeart and TNE implementation.
    """
    
    def __init__(self, campaign_id: str, base_url: str = "http://localhost:5002"):
        """
        Initialize the Interaction Engine.
        
        Args:
            campaign_id: The campaign ID for interaction tracking
            base_url: The TNE API base URL
        """
        self.campaign_id = campaign_id
        self.proxy = NarrativeEngineProxy(campaign_id, base_url)
        self.interaction_history = []
        
        logger.info(f"Interaction Engine initialized for campaign {campaign_id}")
    
    def process_player_input(
        self,
        player_input: str,
        context: Optional[Dict[str, Any]] = None,
        input_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Process player input and generate appropriate response.
        
        Args:
            player_input: The player's input text
            context: Optional context information
            input_type: Type of input (action, dialogue, question, etc.)
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Record the interaction
            interaction_data = {
                "player_input": player_input,
                "input_type": input_type,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to interaction history
            self.interaction_history.append(interaction_data)
            
            # Search for relevant memories to inform response
            relevant_memories = self.search_relevant_memories(player_input)
            
            # Get current narrative context
            narrative_summary = self.proxy.get_summary()
            
            # Generate response based on available information
            response = self._generate_response(
                player_input, 
                relevant_memories, 
                narrative_summary, 
                context
            )
            
            # Record the response
            response_data = {
                "response": response,
                "relevant_memories": len(relevant_memories),
                "narrative_context_used": bool(narrative_summary and not narrative_summary.startswith("Error")),
                "timestamp": datetime.now().isoformat()
            }
            
            self.interaction_history[-1].update(response_data)
            
            logger.info(f"Processed player input: {player_input[:50]}...")
            
            return {
                "success": True,
                "response": response,
                "relevant_memories": relevant_memories,
                "narrative_context": narrative_summary,
                "interaction_id": len(self.interaction_history)
            }
            
        except Exception as e:
            logger.error(f"Error processing player input: {e}")
            return {
                "success": False,
                "response": "I'm having trouble processing that right now. Could you try again?",
                "error": str(e)
            }
    
    def search_relevant_memories(
        self,
        query: str,
        max_results: int = 5,
        min_relevance: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Search for memories relevant to the current interaction.
        
        Args:
            query: Search query based on player input
            max_results: Maximum number of memories to return
            min_relevance: Minimum relevance score
            
        Returns:
            List of relevant memories
        """
        try:
            # Search via proxy
            result = self.proxy.search_memory(query)
            
            if result.get('status') == 'success':
                memories = result.get('results', [])
                
                # Filter by relevance
                if min_relevance > 0.0:
                    memories = [m for m in memories if m.get('relevance', 0.0) >= min_relevance]
                
                # Limit results
                memories = memories[:max_results]
                
                logger.info(f"Found {len(memories)} relevant memories for query: {query}")
                return memories
            else:
                logger.warning(f"Failed to search memories: {result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    def _generate_response(
        self,
        player_input: str,
        relevant_memories: List[Dict[str, Any]],
        narrative_summary: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate a response based on player input and available context.
        
        Args:
            player_input: The player's input
            relevant_memories: Relevant memories from TNE
            narrative_summary: Current narrative summary
            context: Additional context information
            
        Returns:
            Generated response text
        """
        # This is a simplified response generator
        # In a real implementation, this would use an LLM or more sophisticated logic
        
        if not relevant_memories and (not narrative_summary or narrative_summary.startswith("Error")):
            # No context available, provide generic response
            return "I understand. Please continue with your adventure."
        
        # Build context-aware response
        response_parts = []
        
        if relevant_memories:
            memory_count = len(relevant_memories)
            response_parts.append(f"Based on your past experiences ({memory_count} relevant memories), ")
        
        if narrative_summary and not narrative_summary.startswith("Error"):
            response_parts.append("considering your current situation, ")
        
        # Add specific response based on input type
        input_lower = player_input.lower()
        
        if any(word in input_lower for word in ['attack', 'fight', 'combat']):
            response_parts.append("you prepare for battle. The tension rises as you ready your weapons.")
        elif any(word in input_lower for word in ['talk', 'speak', 'ask', 'question']):
            response_parts.append("you engage in conversation, seeking information or connection.")
        elif any(word in input_lower for word in ['explore', 'search', 'look', 'examine']):
            response_parts.append("you carefully examine your surroundings, looking for clues and opportunities.")
        elif any(word in input_lower for word in ['run', 'flee', 'escape']):
            response_parts.append("you decide to retreat, choosing discretion over valor.")
        else:
            response_parts.append("you proceed with your chosen course of action.")
        
        return "".join(response_parts)
    
    def record_interaction_outcome(
        self,
        interaction_id: int,
        outcome: str,
        consequences: Optional[Dict[str, Any]] = None,
        experience_gained: Optional[int] = None
    ) -> bool:
        """
        Record the outcome of an interaction.
        
        Args:
            interaction_id: ID of the interaction to update
            outcome: Description of what happened
            consequences: Optional consequences of the interaction
            experience_gained: Optional experience gained
            
        Returns:
            True if outcome was recorded successfully
        """
        try:
            if interaction_id <= 0 or interaction_id > len(self.interaction_history):
                logger.warning(f"Invalid interaction ID: {interaction_id}")
                return False
            
            # Update local interaction history
            interaction = self.interaction_history[interaction_id - 1]
            interaction.update({
                "outcome": outcome,
                "consequences": consequences or {},
                "experience_gained": experience_gained,
                "outcome_recorded_at": datetime.now().isoformat()
            })
            
            # Record outcome in TNE via memory entry
            memory_entry = {
                "text": f"Interaction outcome: {outcome}",
                "metadata": {
                    "memory_type": "interaction_outcome",
                    "interaction_id": interaction_id,
                    "outcome": outcome,
                    "consequences": consequences or {},
                    "experience_gained": experience_gained,
                    "campaign_id": self.campaign_id,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            result = self.proxy.add_memory(memory_entry)
            
            if result.get('status') == 'success':
                logger.info(f"Recorded interaction outcome: {outcome[:50]}...")
                return True
            else:
                logger.warning(f"Failed to record interaction outcome in TNE: {result.get('error')}")
                return True  # Still return True since we updated locally
                
        except Exception as e:
            logger.error(f"Error recording interaction outcome: {e}")
            return False
    
    def get_interaction_stats(self) -> Dict[str, Any]:
        """
        Get statistics about interactions.
        
        Returns:
            Dictionary containing interaction statistics
        """
        if not self.interaction_history:
            return {
                "total_interactions": 0,
                "input_types": {},
                "avg_response_time": 0,
                "last_interaction": None
            }
        
        input_types = {}
        total_response_time = 0
        response_count = 0
        
        for interaction in self.interaction_history:
            input_type = interaction.get('input_type', 'unknown')
            input_types[input_type] = input_types.get(input_type, 0) + 1
            
            # Calculate response time if available
            if 'timestamp' in interaction and 'response' in interaction:
                response_count += 1
                # Simplified time calculation (in real implementation, would use actual timestamps)
                total_response_time += 1.0  # Placeholder
        
        return {
            "total_interactions": len(self.interaction_history),
            "input_types": input_types,
            "avg_response_time": total_response_time / response_count if response_count > 0 else 0,
            "last_interaction": self.interaction_history[-1].get('timestamp') if self.interaction_history else None
        }
    
    def get_recent_interactions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent interactions.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interaction data
        """
        return self.interaction_history[-limit:] if self.interaction_history else []
    
    def clear_interaction_history(self) -> None:
        """Clear the interaction history."""
        self.interaction_history.clear()
        logger.info("Interaction history cleared")
    
    def is_tne_online(self) -> bool:
        """
        Check if TNE is available for interaction operations.
        
        Returns:
            True if TNE is online and available
        """
        return self.proxy.is_online() 