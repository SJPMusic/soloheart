"""
Context Manager for SoloHeart Runtime

Manages narrative context and identity information using NarrativeEngineProxy
for all TNE communication.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from runtime.narrative_engine_proxy import NarrativeEngineProxy

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages narrative context and identity information for SoloHeart.
    
    Uses NarrativeEngineProxy for all TNE communication to maintain
    clean separation between SoloHeart and TNE implementation.
    """
    
    def __init__(self, campaign_id: str, base_url: str = "http://localhost:5002"):
        """
        Initialize the Context Manager.
        
        Args:
            campaign_id: The campaign ID for context tracking
            base_url: The TNE API base URL
        """
        self.campaign_id = campaign_id
        self.proxy = NarrativeEngineProxy(campaign_id, base_url)
        self.local_context_cache = {}
        
        logger.info(f"Context Manager initialized for campaign {campaign_id}")
    
    def get_narrative_summary(self) -> str:
        """
        Get a narrative summary using NarrativeEngineProxy.
        
        Returns:
            String summary of the current narrative state
        """
        try:
            summary = self.proxy.get_summary()
            if summary and not summary.startswith("Error"):
                logger.info("Retrieved narrative summary from TNE")
                return summary
            else:
                logger.warning("Failed to get narrative summary from TNE")
                return self._get_local_narrative_summary()
                
        except Exception as e:
            logger.error(f"Error getting narrative summary: {e}")
            return self._get_local_narrative_summary()
    
    def _get_local_narrative_summary(self) -> str:
        """Generate a local narrative summary as fallback."""
        if not self.local_context_cache:
            return "No narrative context available yet."
        
        context_parts = []
        if 'character_info' in self.local_context_cache:
            context_parts.append("Character information available")
        if 'world_state' in self.local_context_cache:
            context_parts.append("World state information available")
        if 'recent_events' in self.local_context_cache:
            context_parts.append("Recent events tracked")
        
        return f"Narrative Context: {', '.join(context_parts)}"
    
    def get_identity_profile(self) -> Dict[str, Any]:
        """
        Get the current identity profile using NarrativeEngineProxy.
        
        Returns:
            Dictionary containing identity information
        """
        try:
            result = self.proxy.get_identity_profile()
            
            if result.get('status') == 'success':
                identity_data = result.get('identity', {})
                # Cache locally for quick access
                self.local_context_cache['identity_profile'] = identity_data
                logger.info("Retrieved identity profile from TNE")
                return identity_data
            else:
                logger.warning(f"Failed to get identity profile: {result.get('error')}")
                return self._get_local_identity_profile()
                
        except Exception as e:
            logger.error(f"Error getting identity profile: {e}")
            return self._get_local_identity_profile()
    
    def _get_local_identity_profile(self) -> Dict[str, Any]:
        """Get cached identity profile as fallback."""
        return self.local_context_cache.get('identity_profile', {
            'name': 'Unknown',
            'background': 'Unknown',
            'level': 1,
            'status': 'local_fallback'
        })
    
    def update_character_context(
        self,
        character_name: str,
        character_class: str,
        character_race: str,
        level: int = 1,
        background: Optional[str] = None,
        personality: Optional[str] = None
    ) -> bool:
        """
        Update character context information.
        
        Args:
            character_name: Name of the character
            character_class: Character's class
            character_race: Character's race
            level: Character's level
            background: Character's background
            personality: Character's personality traits
            
        Returns:
            True if context was updated successfully
        """
        try:
            character_info = {
                "name": character_name,
                "class": character_class,
                "race": character_race,
                "level": level,
                "background": background,
                "personality": personality,
                "updated_at": datetime.now().isoformat()
            }
            
            # Store locally for quick access
            self.local_context_cache['character_info'] = character_info
            
            # Add to TNE via memory entry
            memory_entry = {
                "text": f"Character context updated: {character_name} - {character_race} {character_class} (Level {level})",
                "metadata": {
                    "memory_type": "character_context",
                    "character_info": character_info,
                    "campaign_id": self.campaign_id,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            result = self.proxy.add_memory(memory_entry)
            
            if result.get('status') == 'success':
                logger.info(f"Character context updated: {character_name}")
                return True
            else:
                logger.warning(f"Failed to update character context in TNE: {result.get('error')}")
                return True  # Still return True since we cached locally
                
        except Exception as e:
            logger.error(f"Error updating character context: {e}")
            return False
    
    def update_world_context(
        self,
        location: str,
        world_state: Dict[str, Any],
        current_time: Optional[str] = None,
        weather: Optional[str] = None,
        atmosphere: Optional[str] = None
    ) -> bool:
        """
        Update world context information.
        
        Args:
            location: Current location
            world_state: Current state of the world
            current_time: Current in-game time
            weather: Current weather conditions
            atmosphere: Atmospheric description
            
        Returns:
            True if world context was updated successfully
        """
        try:
            world_info = {
                "location": location,
                "world_state": world_state,
                "current_time": current_time,
                "weather": weather,
                "atmosphere": atmosphere,
                "updated_at": datetime.now().isoformat()
            }
            
            # Store locally for quick access
            self.local_context_cache['world_state'] = world_info
            
            # Add to TNE via memory entry
            memory_entry = {
                "text": f"World context updated: {location} - {atmosphere or 'Standard conditions'}",
                "metadata": {
                    "memory_type": "world_context",
                    "world_info": world_info,
                    "campaign_id": self.campaign_id,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            result = self.proxy.add_memory(memory_entry)
            
            if result.get('status') == 'success':
                logger.info(f"World context updated: {location}")
                return True
            else:
                logger.warning(f"Failed to update world context in TNE: {result.get('error')}")
                return True  # Still return True since we cached locally
                
        except Exception as e:
            logger.error(f"Error updating world context: {e}")
            return False
    
    def add_recent_event(
        self,
        event_description: str,
        event_type: str = "general",
        participants: Optional[List[str]] = None,
        location: Optional[str] = None,
        outcome: Optional[str] = None
    ) -> bool:
        """
        Add a recent event to the context.
        
        Args:
            event_description: Description of the event
            event_type: Type of event (combat, dialogue, exploration, etc.)
            participants: Who was involved
            location: Where it happened
            outcome: What was the result
            
        Returns:
            True if event was added successfully
        """
        try:
            event_info = {
                "description": event_description,
                "type": event_type,
                "participants": participants or [],
                "location": location,
                "outcome": outcome,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store locally for quick access
            if 'recent_events' not in self.local_context_cache:
                self.local_context_cache['recent_events'] = []
            self.local_context_cache['recent_events'].append(event_info)
            
            # Keep only the last 10 events
            self.local_context_cache['recent_events'] = self.local_context_cache['recent_events'][-10:]
            
            # Add to TNE via memory entry
            memory_entry = {
                "text": event_description,
                "metadata": {
                    "memory_type": "recent_event",
                    "event_info": event_info,
                    "campaign_id": self.campaign_id,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            result = self.proxy.add_memory(memory_entry)
            
            if result.get('status') == 'success':
                logger.info(f"Recent event added: {event_description[:50]}...")
                return True
            else:
                logger.warning(f"Failed to add recent event to TNE: {result.get('error')}")
                return True  # Still return True since we cached locally
                
        except Exception as e:
            logger.error(f"Error adding recent event: {e}")
            return False
    
    def get_full_context(self) -> Dict[str, Any]:
        """
        Get the complete current context.
        
        Returns:
            Dictionary containing all context information
        """
        context = {
            "campaign_id": self.campaign_id,
            "narrative_summary": self.get_narrative_summary(),
            "identity_profile": self.get_identity_profile(),
            "local_cache": self.local_context_cache.copy()
        }
        
        return context
    
    def search_context(
        self,
        query: str,
        context_type: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search context information using NarrativeEngineProxy.
        
        Args:
            query: Search query
            context_type: Optional filter by context type
            max_results: Maximum number of results to return
            
        Returns:
            List of matching context items
        """
        try:
            # Search via proxy
            result = self.proxy.search_memory(query)
            
            if result.get('status') == 'success':
                matches = result.get('results', [])
                
                # Apply context type filter
                if context_type:
                    matches = [m for m in matches if m.get('metadata', {}).get('memory_type') == context_type]
                
                # Limit results
                matches = matches[:max_results]
                
                logger.info(f"Found {len(matches)} context matches for query: {query}")
                return matches
            else:
                logger.warning(f"Failed to search context: {result.get('error')}")
                return self._search_local_context(query, context_type, max_results)
                
        except Exception as e:
            logger.error(f"Error searching context: {e}")
            return self._search_local_context(query, context_type, max_results)
    
    def _search_local_context(
        self,
        query: str,
        context_type: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search local context cache as fallback."""
        query_lower = query.lower()
        matches = []
        
        for key, value in self.local_context_cache.items():
            if context_type and key != context_type:
                continue
            
            # Simple text matching
            if query_lower in str(value).lower():
                matches.append({
                    'context_type': key,
                    'content': value,
                    'relevance': 0.8  # Default relevance for local matches
                })
        
        return matches[:max_results]
    
    def clear_local_cache(self) -> None:
        """Clear the local context cache."""
        self.local_context_cache.clear()
        logger.info("Local context cache cleared")
    
    def is_tne_online(self) -> bool:
        """
        Check if TNE is available for context operations.
        
        Returns:
            True if TNE is online and available
        """
        return self.proxy.is_online() 