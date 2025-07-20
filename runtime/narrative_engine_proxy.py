"""
NarrativeEngineProxy - High-level proxy wrapper around TNEClient for SoloHeart runtime.

This module provides a clean interface for SoloHeart to interact with The Narrative Engine
without dealing with HTTP details directly.
"""

import logging
from typing import Dict, Optional, Any
from integrations.tne_client import TNEClient

logger = logging.getLogger(__name__)


class NarrativeEngineProxy:
    """
    High-level proxy wrapper around TNEClient for SoloHeart runtime integration.
    
    This class encapsulates all SoloHeart's interactions with The Narrative Engine,
    providing a clean interface that abstracts away HTTP logic and aligns with
    SoloHeart's internal runtime flow.
    """
    
    def __init__(self, campaign_id: str, base_url: str = "http://localhost:5002"):
        """
        Initialize the NarrativeEngineProxy.
        
        Args:
            campaign_id: The unique identifier for the current campaign
            base_url: The base URL for the TNE API server
        """
        self.campaign_id = campaign_id
        self.base_url = base_url
        self._client = TNEClient(base_url=base_url, campaign_id=campaign_id)
        
        logger.info(f"Initialized NarrativeEngineProxy for campaign {campaign_id} at {base_url}")
    
    def record_scene(self, scene_text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record a narrative scene in The Narrative Engine.
        
        Used by SoloHeart's scene manager to capture story progression and
        maintain narrative continuity across gameplay sessions.
        
        Args:
            scene_text: The narrative description of the scene
            metadata: Optional metadata about the scene (e.g., location, characters, etc.)
            
        Returns:
            Dict containing the response from TNE or error information
        """
        try:
            logger.info(f"Recording scene for campaign {self.campaign_id}")
            response = self._client.add_scene(scene_text, metadata or {})
            logger.debug(f"Scene recorded successfully: {response.get('status', 'unknown')}")
            return response
        except Exception as e:
            logger.error(f"Failed to record scene: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    def add_memory(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a structured memory entry to The Narrative Engine.
        
        Used by SoloHeart's memory system to store important game events,
        character interactions, and player decisions for future reference.
        
        Args:
            entry: Structured memory data (e.g., combat results, quest progress, etc.)
            
        Returns:
            Dict containing the response from TNE or error information
        """
        try:
            logger.info(f"Adding memory entry for campaign {self.campaign_id}")
            response = self._client.add_memory_entry(entry)
            logger.debug(f"Memory entry added successfully: {response.get('status', 'unknown')}")
            return response
        except Exception as e:
            logger.error(f"Failed to add memory entry: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    def get_summary(self) -> str:
        """
        Get a symbolic summary of the current narrative state.
        
        Used by SoloHeart's narrative bridge to provide context for AI responses
        and maintain story coherence during gameplay.
        
        Returns:
            String containing the narrative summary or error message
        """
        try:
            logger.info(f"Requesting narrative summary for campaign {self.campaign_id}")
            response = self._client.get_symbolic_summary()
            summary = response.get('summary', 'No summary available')
            logger.debug(f"Retrieved narrative summary: {len(summary)} characters")
            return summary
        except Exception as e:
            logger.error(f"Failed to get narrative summary: {e}")
            return f"Error retrieving summary: {e}"
    
    def get_identity_profile(self) -> Dict[str, Any]:
        """
        Get the current identity profile from The Narrative Engine.
        
        Used by SoloHeart's character system to understand the player's
        current identity, background, and character development.
        
        Returns:
            Dict containing identity information or error details
        """
        try:
            logger.info(f"Querying identity profile for campaign {self.campaign_id}")
            response = self._client.query_identity()
            logger.debug(f"Retrieved identity profile: {response.get('status', 'unknown')}")
            return response
        except Exception as e:
            logger.error(f"Failed to get identity profile: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    def search_memory(self, query: str) -> Dict[str, Any]:
        """
        Search for relevant memories based on a query.
        
        Used by SoloHeart's AI system to find relevant past events and
        character interactions when generating responses or making decisions.
        
        Args:
            query: Search query to find relevant memories
            
        Returns:
            Dict containing search results or error information
        """
        try:
            logger.info(f"Searching memory for query: '{query}' in campaign {self.campaign_id}")
            response = self._client.query_concepts(query)
            logger.debug(f"Memory search completed: {len(response.get('results', []))} results")
            return response
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return {'error': str(e), 'status': 'failed', 'results': []}
    
    def get_scene_stats(self) -> Dict[str, Any]:
        """
        Get statistics about recorded scenes.
        
        Used by SoloHeart's analytics and debugging systems to monitor
        narrative progression and identify potential issues.
        
        Returns:
            Dict containing scene statistics or error information
        """
        try:
            logger.info(f"Requesting scene stats for campaign {self.campaign_id}")
            response = self._client.get_scene_stats()
            logger.debug(f"Retrieved scene stats: {response.get('status', 'unknown')}")
            return response
        except Exception as e:
            logger.error(f"Failed to get scene stats: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    def is_online(self) -> bool:
        """
        Check if The Narrative Engine API is available.
        
        Used by SoloHeart's runtime to determine if TNE integration
        is available before attempting to use narrative features.
        
        Returns:
            True if TNE is online and healthy, False otherwise
        """
        try:
            logger.debug(f"Checking TNE health for campaign {self.campaign_id}")
            response = self._client.is_healthy()
            is_healthy = response.get('status') == 'healthy'
            logger.debug(f"TNE health check result: {is_healthy}")
            return is_healthy
        except Exception as e:
            logger.warning(f"TNE health check failed: {e}")
            return False
    
    def get_campaign_id(self) -> str:
        """
        Get the current campaign ID.
        
        Returns:
            The campaign ID this proxy is configured for
        """
        return self.campaign_id
    
    def reset_campaign(self, new_campaign_id: str) -> None:
        """
        Reset the proxy to use a different campaign ID.
        
        Args:
            new_campaign_id: The new campaign ID to use
        """
        self.campaign_id = new_campaign_id
        self._client = TNEClient(base_url=self.base_url, campaign_id=new_campaign_id)
        logger.info(f"Reset NarrativeEngineProxy to campaign {new_campaign_id}") 