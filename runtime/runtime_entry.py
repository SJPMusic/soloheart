"""
Runtime Entry Point for SoloHeart

Main entry point for SoloHeart runtime that coordinates all runtime modules
and uses NarrativeEngineProxy for all TNE communication.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from runtime.narrative_engine_proxy import NarrativeEngineProxy
from runtime.scene_manager import SceneManager
from runtime.memory_tracker import MemoryTracker
from runtime.context_manager import ContextManager
from runtime.interaction_engine import InteractionEngine

logger = logging.getLogger(__name__)


class SoloHeartRuntime:
    """
    Main runtime coordinator for SoloHeart.
    
    Coordinates all runtime modules and uses NarrativeEngineProxy for all TNE communication
    to maintain clean separation between SoloHeart and TNE implementation.
    """
    
    def __init__(self, campaign_id: str, base_url: str = "http://localhost:5002"):
        """
        Initialize the SoloHeart Runtime.
        
        Args:
            campaign_id: The campaign ID for runtime tracking
            base_url: The TNE API base URL
        """
        self.campaign_id = campaign_id
        self.base_url = base_url
        
        # Initialize NarrativeEngineProxy for all TNE communication
        self.proxy = NarrativeEngineProxy(campaign_id, base_url)
        
        # Initialize all runtime modules
        self.scene_manager = SceneManager(campaign_id, base_url)
        self.memory_tracker = MemoryTracker(campaign_id, base_url)
        self.context_manager = ContextManager(campaign_id, base_url)
        self.interaction_engine = InteractionEngine(campaign_id, base_url)
        
        # Runtime state
        self.is_initialized = False
        self.runtime_stats = {
            "start_time": datetime.now().isoformat(),
            "total_scenes": 0,
            "total_memories": 0,
            "total_interactions": 0,
            "tne_connection_status": "unknown"
        }
        
        logger.info(f"SoloHeart Runtime initialized for campaign {campaign_id}")
    
    def initialize(self) -> bool:
        """
        Initialize the runtime and check TNE availability.
        
        Returns:
            True if initialization was successful
        """
        try:
            # Check TNE availability
            tne_online = self.proxy.is_online()
            self.runtime_stats["tne_connection_status"] = "online" if tne_online else "offline"
            
            if tne_online:
                logger.info("✅ TNE is online - full functionality available")
            else:
                logger.warning("⚠️ TNE is offline - using local fallback mode")
            
            self.is_initialized = True
            logger.info("SoloHeart Runtime initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SoloHeart Runtime: {e}")
            return False
    
    def process_game_action(
        self,
        action_description: str,
        action_type: str = "general",
        location: Optional[str] = None,
        participants: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a game action through all runtime modules.
        
        Args:
            action_description: Description of the action
            action_type: Type of action (combat, dialogue, exploration, etc.)
            location: Where the action takes place
            participants: Who is involved
            context: Additional context information
            
        Returns:
            Dictionary containing processing results
        """
        try:
            if not self.is_initialized:
                return {"success": False, "error": "Runtime not initialized"}
            
            # Record the scene
            scene_success = self.scene_manager.record_scene(
                action_description,
                metadata={"action_type": action_type},
                location=location,
                participants=participants,
                scene_type=action_type
            )
            
            # Add memory of the action
            memory_success = self.memory_tracker.add_memory(
                action_description,
                memory_type="action",
                metadata={
                    "action_type": action_type,
                    "location": location,
                    "participants": participants
                }
            )
            
            # Update context with recent event
            context_success = self.context_manager.add_recent_event(
                action_description,
                event_type=action_type,
                participants=participants,
                location=location
            )
            
            # Process as interaction
            interaction_result = self.interaction_engine.process_player_input(
                action_description,
                context=context,
                input_type=action_type
            )
            
            # Update runtime stats
            if scene_success:
                self.runtime_stats["total_scenes"] += 1
            if memory_success:
                self.runtime_stats["total_memories"] += 1
            if interaction_result.get("success"):
                self.runtime_stats["total_interactions"] += 1
            
            return {
                "success": True,
                "scene_recorded": scene_success,
                "memory_added": memory_success,
                "context_updated": context_success,
                "interaction_result": interaction_result,
                "runtime_stats": self.runtime_stats.copy()
            }
            
        except Exception as e:
            logger.error(f"Error processing game action: {e}")
            return {"success": False, "error": str(e)}
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the campaign.
        
        Returns:
            Dictionary containing campaign summary
        """
        try:
            summary = {
                "campaign_id": self.campaign_id,
                "runtime_stats": self.runtime_stats.copy(),
                "tne_online": self.proxy.is_online()
            }
            
            # Get narrative summary from TNE
            narrative_summary = self.proxy.get_summary()
            if narrative_summary and not narrative_summary.startswith("Error"):
                summary["narrative_summary"] = narrative_summary
            else:
                summary["narrative_summary"] = "No narrative summary available"
            
            # Get identity profile from TNE
            identity_result = self.proxy.get_identity_profile()
            if identity_result.get('status') == 'success':
                summary["identity_profile"] = identity_result.get('identity', {})
            else:
                summary["identity_profile"] = {"status": "unavailable"}
            
            # Get scene statistics
            scene_stats = self.scene_manager.get_scene_stats()
            summary["scene_stats"] = scene_stats
            
            # Get memory summary
            memory_summary = self.memory_tracker.get_memory_summary()
            summary["memory_summary"] = memory_summary
            
            # Get interaction statistics
            interaction_stats = self.interaction_engine.get_interaction_stats()
            summary["interaction_stats"] = interaction_stats
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting campaign summary: {e}")
            return {
                "campaign_id": self.campaign_id,
                "error": str(e),
                "runtime_stats": self.runtime_stats.copy()
            }
    
    def search_campaign_data(
        self,
        query: str,
        search_type: str = "all",
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search across all campaign data.
        
        Args:
            query: Search query
            search_type: Type of search (all, scenes, memories, context, interactions)
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing search results
        """
        try:
            results = {
                "query": query,
                "search_type": search_type,
                "results": {}
            }
            
            if search_type in ["all", "scenes"]:
                scene_results = self.scene_manager.get_recent_scenes(max_results)
                results["results"]["scenes"] = scene_results
            
            if search_type in ["all", "memories"]:
                memory_results = self.memory_tracker.search_memory(query, max_results=max_results)
                results["results"]["memories"] = memory_results
            
            if search_type in ["all", "context"]:
                context_results = self.context_manager.search_context(query, max_results=max_results)
                results["results"]["context"] = context_results
            
            if search_type in ["all", "interactions"]:
                interaction_results = self.interaction_engine.get_recent_interactions(max_results)
                results["results"]["interactions"] = interaction_results
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching campaign data: {e}")
            return {
                "query": query,
                "search_type": search_type,
                "error": str(e),
                "results": {}
            }
    
    def save_campaign_state(self) -> bool:
        """
        Save the current campaign state.
        
        Returns:
            True if save was successful
        """
        try:
            # Get comprehensive campaign data
            campaign_data = self.get_campaign_summary()
            
            # Add runtime module states
            campaign_data["scene_manager_state"] = {
                "scene_history_count": len(self.scene_manager.scene_history)
            }
            
            campaign_data["memory_tracker_state"] = {
                "local_cache_count": len(self.memory_tracker.local_memory_cache)
            }
            
            campaign_data["context_manager_state"] = {
                "local_cache_keys": list(self.context_manager.local_context_cache.keys())
            }
            
            campaign_data["interaction_engine_state"] = {
                "interaction_history_count": len(self.interaction_engine.interaction_history)
            }
            
            # In a real implementation, this would save to a file or database
            logger.info(f"Campaign state saved for {self.campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving campaign state: {e}")
            return False
    
    def load_campaign_state(self, campaign_data: Dict[str, Any]) -> bool:
        """
        Load campaign state from saved data.
        
        Args:
            campaign_data: Saved campaign data
            
        Returns:
            True if load was successful
        """
        try:
            # Update runtime stats
            if "runtime_stats" in campaign_data:
                self.runtime_stats.update(campaign_data["runtime_stats"])
            
            # In a real implementation, this would restore module states
            logger.info(f"Campaign state loaded for {self.campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading campaign state: {e}")
            return False
    
    def get_runtime_health(self) -> Dict[str, Any]:
        """
        Get runtime health status.
        
        Returns:
            Dictionary containing health information
        """
        try:
            health = {
                "campaign_id": self.campaign_id,
                "is_initialized": self.is_initialized,
                "tne_online": self.proxy.is_online(),
                "runtime_stats": self.runtime_stats.copy(),
                "module_status": {
                    "scene_manager": self.scene_manager.is_tne_online(),
                    "memory_tracker": self.memory_tracker.is_tne_online(),
                    "context_manager": self.context_manager.is_tne_online(),
                    "interaction_engine": self.interaction_engine.is_tne_online()
                }
            }
            
            return health
            
        except Exception as e:
            logger.error(f"Error getting runtime health: {e}")
            return {
                "campaign_id": self.campaign_id,
                "error": str(e),
                "is_initialized": self.is_initialized
            }
    
    def shutdown(self) -> None:
        """Shutdown the runtime and clean up resources."""
        try:
            # Save final state
            self.save_campaign_state()
            
            # Clear local caches
            self.scene_manager.scene_history.clear()
            self.memory_tracker.local_memory_cache.clear()
            self.context_manager.local_context_cache.clear()
            self.interaction_engine.interaction_history.clear()
            
            logger.info("SoloHeart Runtime shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during runtime shutdown: {e}")


def create_runtime(campaign_id: str, base_url: str = "http://localhost:5002") -> SoloHeartRuntime:
    """
    Factory function to create and initialize a SoloHeart Runtime.
    
    Args:
        campaign_id: The campaign ID
        base_url: The TNE API base URL
        
    Returns:
        Initialized SoloHeartRuntime instance
    """
    runtime = SoloHeartRuntime(campaign_id, base_url)
    if runtime.initialize():
        return runtime
    else:
        raise RuntimeError(f"Failed to initialize SoloHeart Runtime for campaign {campaign_id}") 