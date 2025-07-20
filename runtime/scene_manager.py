"""
Scene Manager for SoloHeart Runtime

Manages scene recording and narrative progression using NarrativeEngineProxy
for all TNE communication.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from runtime.narrative_engine_proxy import NarrativeEngineProxy

logger = logging.getLogger(__name__)


class SceneManager:
    """
    Manages scene recording and narrative progression for SoloHeart.
    
    Uses NarrativeEngineProxy for all TNE communication to maintain
    clean separation between SoloHeart and TNE implementation.
    """
    
    def __init__(self, campaign_id: str, base_url: str = "http://localhost:5002"):
        """
        Initialize the Scene Manager.
        
        Args:
            campaign_id: The campaign ID for scene tracking
            base_url: The TNE API base URL
        """
        self.campaign_id = campaign_id
        self.proxy = NarrativeEngineProxy(campaign_id, base_url)
        self.scene_history = []
        
        logger.info(f"Scene Manager initialized for campaign {campaign_id}")
    
    def record_scene(
        self, 
        scene_text: str, 
        metadata: Optional[Dict[str, Any]] = None,
        location: Optional[str] = None,
        participants: Optional[List[str]] = None,
        scene_type: str = "narrative"
    ) -> bool:
        """
        Record a narrative scene using NarrativeEngineProxy.
        
        Args:
            scene_text: The narrative description of the scene
            metadata: Optional metadata about the scene
            location: Optional location where the scene takes place
            participants: Optional list of participants in the scene
            scene_type: Type of scene (narrative, combat, dialogue, etc.)
            
        Returns:
            True if scene was recorded successfully, False otherwise
        """
        try:
            # Prepare scene metadata
            scene_metadata = {
                "scene_type": scene_type,
                "timestamp": datetime.now().isoformat(),
                "campaign_id": self.campaign_id
            }
            
            if metadata:
                scene_metadata.update(metadata)
            if location:
                scene_metadata["location"] = location
            if participants:
                scene_metadata["participants"] = participants
            
            # Record scene via proxy
            result = self.proxy.record_scene(scene_text, scene_metadata)
            
            if result.get('status') == 'success':
                # Store locally for quick access
                local_scene = {
                    "text": scene_text,
                    "metadata": scene_metadata,
                    "recorded_at": datetime.now().isoformat()
                }
                self.scene_history.append(local_scene)
                
                logger.info(f"Scene recorded successfully: {scene_text[:50]}...")
                return True
            else:
                logger.error(f"Failed to record scene: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error recording scene: {e}")
            return False
    
    def record_combat_scene(
        self,
        combat_description: str,
        participants: List[str],
        location: str,
        outcome: str,
        damage_dealt: Optional[int] = None,
        experience_gained: Optional[int] = None
    ) -> bool:
        """
        Record a combat scene with specific combat metadata.
        
        Args:
            combat_description: Description of the combat
            participants: List of participants (player, enemies, allies)
            location: Where the combat took place
            outcome: Result of the combat (victory, defeat, retreat, etc.)
            damage_dealt: Optional damage dealt by player
            experience_gained: Optional experience gained
            
        Returns:
            True if combat scene was recorded successfully
        """
        metadata = {
            "scene_type": "combat",
            "participants": participants,
            "location": location,
            "outcome": outcome
        }
        
        if damage_dealt is not None:
            metadata["damage_dealt"] = damage_dealt
        if experience_gained is not None:
            metadata["experience_gained"] = experience_gained
        
        return self.record_scene(combat_description, metadata)
    
    def record_dialogue_scene(
        self,
        dialogue_text: str,
        speaker: str,
        listener: str,
        location: str,
        emotional_tone: Optional[str] = None,
        relationship_impact: Optional[float] = None
    ) -> bool:
        """
        Record a dialogue scene with conversation metadata.
        
        Args:
            dialogue_text: The dialogue content
            speaker: Who is speaking
            listener: Who is being spoken to
            location: Where the dialogue takes place
            emotional_tone: Optional emotional tone of the dialogue
            relationship_impact: Optional impact on relationship (-1 to 1)
            
        Returns:
            True if dialogue scene was recorded successfully
        """
        metadata = {
            "scene_type": "dialogue",
            "speaker": speaker,
            "listener": listener,
            "location": location
        }
        
        if emotional_tone:
            metadata["emotional_tone"] = emotional_tone
        if relationship_impact is not None:
            metadata["relationship_impact"] = relationship_impact
        
        return self.record_scene(dialogue_text, metadata)
    
    def get_scene_stats(self) -> Dict[str, Any]:
        """
        Get statistics about recorded scenes.
        
        Returns:
            Dictionary containing scene statistics
        """
        try:
            # Get stats from TNE via proxy
            result = self.proxy.get_scene_stats()
            
            if result.get('status') == 'success':
                return result
            else:
                logger.warning(f"Failed to get scene stats from TNE: {result.get('error')}")
                # Return local stats as fallback
                return self._get_local_scene_stats()
                
        except Exception as e:
            logger.error(f"Error getting scene stats: {e}")
            return self._get_local_scene_stats()
    
    def _get_local_scene_stats(self) -> Dict[str, Any]:
        """Get scene statistics from local scene history."""
        if not self.scene_history:
            return {
                "total_scenes": 0,
                "scene_types": {},
                "avg_scene_length": 0,
                "last_scene_time": None
            }
        
        scene_types = {}
        total_length = 0
        
        for scene in self.scene_history:
            scene_type = scene.get("metadata", {}).get("scene_type", "unknown")
            scene_types[scene_type] = scene_types.get(scene_type, 0) + 1
            total_length += len(scene.get("text", ""))
        
        return {
            "total_scenes": len(self.scene_history),
            "scene_types": scene_types,
            "avg_scene_length": total_length / len(self.scene_history) if self.scene_history else 0,
            "last_scene_time": self.scene_history[-1]["recorded_at"] if self.scene_history else None
        }
    
    def get_recent_scenes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent scenes from local history.
        
        Args:
            limit: Maximum number of scenes to return
            
        Returns:
            List of recent scene data
        """
        return self.scene_history[-limit:] if self.scene_history else []
    
    def is_tne_online(self) -> bool:
        """
        Check if TNE is available for scene recording.
        
        Returns:
            True if TNE is online and available
        """
        return self.proxy.is_online() 