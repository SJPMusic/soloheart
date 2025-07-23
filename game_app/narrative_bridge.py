"""
Narrative Bridge Module for Solo Game

This module acts as the Solo Game-specific adapter for The Narrative Engine.
It provides a simplified interface tailored to the Solo Game context while
isolating game-specific logic from engine internals.

The bridge allows easy future replacement or upgrade of the Narrative Engine
without requiring changes to the Solo Game code.

PHASE 1 UPDATE: Now uses TNEClient for all TNE communication via HTTP API.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import json
import datetime
import os

# Import TNEClient instead of direct TNE modules
try:
    from integrations.tne_client import TNEClient
    logger = logging.getLogger(__name__)
    logger.info("✅ TNEClient imported successfully")
except ImportError as e:
    logging.error(f"Failed to import TNEClient: {e}")
    raise

from .lore_manager import LoreManager, LoreType, LoreEntry

logger = logging.getLogger(__name__)

@dataclass
class SoloGameState:
    """Solo Game-specific game state wrapper"""
    campaign_id: str
    current_location: str
    party_members: List[Dict[str, Any]]
    active_missions: List[Dict[str, Any]]
    world_state: Dict[str, Any]
    session_data: Dict[str, Any]

@dataclass
class SoloGameMemoryEntry:
    """Solo Game-specific memory entry"""
    content: str
    memory_type: str
    metadata: Dict[str, Any]
    tags: List[str] = None
    emotional_context: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.emotional_context is None:
            self.emotional_context = []

@dataclass
class SoloGameNPCResponse:
    """Solo Game-specific NPC response"""
    text: str
    npc_name: str
    emotional_tone: str
    mission_hints: Optional[List[str]] = None
    action_ready: bool = False
    relationship_change: Optional[float] = None

class NarrativeBridge:
    """
    Bridge between Solo Game and The Narrative Engine
    
    This class provides a Solo Game-specific interface to the narrative engine,
    handling game-specific logic while maintaining clean separation
    from the engine internals.
    
    PHASE 1 UPDATE: Now uses TNEClient for all TNE communication.
    """
    
    def __init__(self, campaign_id: str = "Default Campaign"):
        """
        Initialize the Narrative Bridge with campaign ID.
        
        Args:
            campaign_id: Unique identifier for the campaign
        """
        self.campaign_id = campaign_id
        
        # Initialize TNEClient for API communication
        tne_base_url = os.getenv('TNE_API_URL', 'http://localhost:5002')
        self.tne_client = TNEClient(base_url=tne_base_url, campaign_id=campaign_id)
        
        # Test connection to TNE API
        connection_result = self.tne_client.test_connection()
        if connection_result['overall_status'] == 'disconnected':
            logger.warning(f"⚠️ TNE API server not available at {tne_base_url}")
            logger.warning("Some narrative features may be limited")
        else:
            logger.info(f"✅ Connected to TNE API server at {tne_base_url}")
        
        # Initialize lore manager (local to SoloHeart)
        self.lore_manager = LoreManager(campaign_id)
        
        logger.info(f"Narrative Bridge initialized for campaign: {campaign_id}")
    
    def store_solo_game_memory(
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
        Store a Solo Game memory using TNEClient.
        """
        try:
            # Prepare memory entry for TNE API
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
                "timestamp": datetime.datetime.now().isoformat()
                }
            }
            
            # Send to TNE via API
            result = self.tne_client.add_memory_entry(memory_entry)
            
            if "error" in result:
                logger.error(f"Failed to store memory via TNE API: {result['error']}")
                return False
            
            logger.info(f"Stored Solo Game memory for {character_id}: {content[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error storing Solo Game memory: {e}")
            return False

    def store_character_creation(self, character_data: dict, campaign_id: str) -> bool:
        """
        Store complete character creation data using TNEClient.
        
        Args:
            character_data: Complete character data dictionary
            campaign_id: Campaign ID for the character
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a comprehensive memory entry for character creation
            character_text = f"Character created: {character_data.get('name', 'Unknown')} - {character_data.get('race', 'Unknown')} {character_data.get('class', 'Unknown')}"
            
            memory_entry = {
                "text": character_text,
                "metadata": {
                    "memory_type": "character_creation",
                    "campaign_id": campaign_id,
                    "character_data": character_data,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }
            
            result = self.tne_client.add_memory_entry(memory_entry)
            
            if "error" in result:
                logger.error(f"Failed to store character creation: {result['error']}")
                return False
            
            logger.info(f"Stored character creation for {character_data.get('name', 'Unknown')}")
            return True
                
        except Exception as e:
            logger.error(f"Error storing character creation: {e}")
            return False
    
    def _detect_emotion_from_content(self, content: str) -> str:
        """
        Simple emotion detection from content.
        Returns a string emotion type instead of EmotionType enum.
        """
        content_lower = content.lower()
        
        # Simple keyword-based emotion detection
        if any(word in content_lower for word in ['fear', 'afraid', 'scared', 'terrified']):
            return 'fear'
        elif any(word in content_lower for word in ['anger', 'angry', 'furious', 'rage']):
            return 'anger'
        elif any(word in content_lower for word in ['joy', 'happy', 'excited', 'elated']):
            return 'joy'
        elif any(word in content_lower for word in ['sadness', 'sad', 'depressed', 'melancholy']):
            return 'sadness'
        elif any(word in content_lower for word in ['surprise', 'shocked', 'amazed', 'astonished']):
            return 'surprise'
        else:
            return 'neutral'
    
    def get_npc_response(self, npc_name: str, context: str, 
                        player_emotion: Optional[Dict[str, float]] = None) -> SoloGameNPCResponse:
        """
        Generate NPC response using TNE symbolic analysis.
        """
        try:
            # Query TNE for symbolic analysis of the context
            symbolic_summary = self.tne_client.get_symbolic_summary()
            
            # Add the current context as a scene
            scene_data = {
                "text": f"NPC {npc_name} interaction: {context}"
            }
            scene_result = self.tne_client.add_scene(scene_data)
            
            # Generate response based on symbolic analysis
            if "error" not in symbolic_summary:
                # Use symbolic insights to inform response generation
                identity_profile = symbolic_summary.get('result', {}).get('identity_profile', {})
                contradictions = symbolic_summary.get('result', {}).get('contradictions', [])
                
                # Simple response generation based on symbolic state
                if contradictions:
                    emotional_tone = "conflicted"
                elif identity_profile.get('confidence_score', 0) > 0.7:
                    emotional_tone = "tranquil"
                else:
                    emotional_tone = "neutral"
            else:
                emotional_tone = "neutral"
            
            # Generate response text
            response_text = f"{npc_name} responds to your interaction with a {emotional_tone} tone."
            
            return SoloGameNPCResponse(
                text=response_text,
                npc_name=npc_name,
                emotional_tone=emotional_tone,
                mission_hints=[],
                action_ready=False,
                relationship_change=0.0
            )
            
        except Exception as e:
            logger.error(f"Error generating NPC response: {e}")
            return SoloGameNPCResponse(
                text=f"{npc_name} seems distracted and gives a brief response.",
                npc_name=npc_name,
                emotional_tone="neutral",
                mission_hints=[],
                action_ready=False,
                relationship_change=0.0
            )
    
    def generate_dm_narration(
        self,
        situation: str,
        player_actions: List[str],
        world_context: Optional[Dict[str, Any]] = None,
        emotional_context: Optional[List[str]] = None
    ) -> str:
        """
        Generate DM narration using TNE symbolic analysis.
        """
        try:
            # Create a scene entry for the current situation
            scene_text = f"Situation: {situation}. Player actions: {', '.join(player_actions)}"
            if emotional_context:
                scene_text += f" Emotional context: {', '.join(emotional_context)}"
            
            scene_data = {"text": scene_text}
            scene_result = self.tne_client.add_scene(scene_data)
            
            # Query symbolic concepts for narrative guidance
            concepts_result = self.tne_client.query_concepts()
            
            # Generate narration based on symbolic analysis
            if "error" not in concepts_result:
                concepts = concepts_result.get('result', {}).get('concepts', {})
                conflicts = concepts_result.get('result', {}).get('conflicts', [])
                
                if conflicts:
                    narration = f"As you {', '.join(player_actions)}, the situation becomes more complex. {situation}"
                else:
                    narration = f"You {', '.join(player_actions)}. {situation}"
            else:
                narration = f"You {', '.join(player_actions)}. {situation}"
            
            return narration
            
        except Exception as e:
            logger.error(f"Error generating DM narration: {e}")
            return f"You {', '.join(player_actions)}. {situation}"
    
    def _generate_fallback_narration(
        self,
        situation: str,
        player_actions: List[str],
        emotional_context: Optional[List[str]] = None
    ) -> str:
        """
        Generate fallback narration when TNE is unavailable.
        """
        action_text = ', '.join(player_actions)
        narration = f"You {action_text}. {situation}"
        
        if emotional_context:
            emotion_text = ', '.join(emotional_context)
            narration += f" The emotional atmosphere is {emotion_text}."
        
        return narration
    
    def recall_related_memories(
        self,
        query: str,
        max_results: int = 5,
        memory_type: Optional[str] = None,
        emotional_filter: Optional[str] = None,
        min_emotional_intensity: float = 0.0,
        character_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recall related memories using TNE concept query.
        """
        try:
            # Query TNE for concepts related to the query
            concepts_result = self.tne_client.query_concepts(query)
            
            if "error" in concepts_result:
                logger.warning(f"Failed to query concepts: {concepts_result['error']}")
                return []
            
            # Convert concepts to memory-like format
            concepts = concepts_result.get('result', {}).get('concepts', {})
            memories = []
            
            for concept_name, concept_data in concepts.items():
                if len(memories) >= max_results:
                    break
                    
                memory = {
                    "content": f"Concept: {concept_name}",
                    "memory_type": "concept",
                    "metadata": {
                        "concept_data": concept_data,
                        "query": query,
                        "campaign_id": self.campaign_id
                    },
                    "tags": [concept_name],
                    "emotional_context": []
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"Error recalling memories: {e}")
            return []
    
    def recall_emotional_memories(
        self,
        emotion_type: Optional[str] = None,
        min_intensity: float = 0.0,
        max_results: int = 10,
        character_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recall emotional memories using TNE identity query.
        """
        try:
            # Query TNE for identity information
            identity_result = self.tne_client.query_identity()
            
            if "error" in identity_result:
                logger.warning(f"Failed to query identity: {identity_result['error']}")
                return []
            
            # Convert identity profile to memory-like format
            identity_profile = identity_result.get('result', {}).get('identity_profile', [])
            memories = []
            
            for fact in identity_profile[:max_results]:
                memory = {
                    "content": f"Identity fact: {fact}",
                    "memory_type": "identity",
                    "metadata": {
                        "emotion_type": emotion_type or "general",
                        "intensity": min_intensity,
                        "campaign_id": self.campaign_id
                    },
                    "tags": ["identity", "emotional"],
                    "emotional_context": [emotion_type] if emotion_type else []
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"Error recalling emotional memories: {e}")
            return []
    
    def update_world_state(
        self,
        location: str,
        changes: Dict[str, Any]
    ) -> bool:
        """
        Update world state using TNE scene management.
        """
        try:
            # Create a scene entry for the world state change
            scene_text = f"World state change at {location}: {json.dumps(changes)}"
            scene_data = {"text": scene_text}
            
            result = self.tne_client.add_scene(scene_data)
            
            if "error" in result:
                logger.error(f"Failed to update world state: {result['error']}")
                return False
            
            logger.info(f"Updated world state at {location}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating world state: {e}")
            return False
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """
        Get campaign summary using TNE symbolic analysis.
        """
        try:
            # Get symbolic summary from TNE
            symbolic_summary = self.tne_client.get_symbolic_summary()
            scene_stats = self.tne_client.get_scene_stats()
            
            if "error" in symbolic_summary or "error" in scene_stats:
                logger.warning("Failed to get campaign summary from TNE")
                return {
                    "campaign_id": self.campaign_id,
                    "status": "limited",
                    "message": "TNE API unavailable"
                }
            
            # Build summary from TNE data
            summary = {
                "campaign_id": self.campaign_id,
                "status": "active",
                "symbolic_profile": symbolic_summary.get('result', {}),
                "scene_statistics": scene_stats.get('result', {}),
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting campaign summary: {e}")
            return {
                "campaign_id": self.campaign_id,
                "status": "error",
                "message": str(e)
            }
    
    def export_campaign_data(
        self,
        export_path: str,
        include_journals: bool = True,
        include_arcs: bool = True,
        include_threads: bool = True
    ) -> bool:
        """
        Export campaign data using TNE API data.
        """
        try:
            # Get all available data from TNE
            symbolic_summary = self.tne_client.get_symbolic_summary()
            scene_stats = self.tne_client.get_scene_stats()
            concepts = self.tne_client.query_concepts()
            identity = self.tne_client.query_identity()
            
            # Build export data
            export_data = {
                "campaign_id": self.campaign_id,
                "export_timestamp": datetime.datetime.now().isoformat(),
                "tne_data": {
                    "symbolic_summary": symbolic_summary.get('result', {}),
                    "scene_statistics": scene_stats.get('result', {}),
                    "concepts": concepts.get('result', {}),
                    "identity": identity.get('result', {})
                },
                "lore_data": [entry.to_dict() for entry in self.lore_manager.entries.values()] if self.lore_manager else []
            }
            
            # Write to file
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Campaign data exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting campaign data: {e}")
            return False
    
    # Additional methods for backward compatibility
    def add_journal_entry(self, *args, **kwargs):
        """Placeholder for journal functionality - not implemented in TNE API yet."""
        logger.warning("Journal functionality not yet available via TNE API")
        return None
    
    def get_journal_entries(self, *args, **kwargs):
        """Placeholder for journal functionality - not implemented in TNE API yet."""
        logger.warning("Journal functionality not yet available via TNE API")
        return []
    
    def create_character_arc(self, *args, **kwargs):
        """Placeholder for character arc functionality - not implemented in TNE API yet."""
        logger.warning("Character arc functionality not yet available via TNE API")
        return None
    
    def add_arc_milestone(self, *args, **kwargs):
        """Placeholder for character arc functionality - not implemented in TNE API yet."""
        logger.warning("Character arc functionality not yet available via TNE API")
        return None
        
    def create_plot_thread(self, *args, **kwargs):
        """Placeholder for plot thread functionality - not implemented in TNE API yet."""
        logger.warning("Plot thread functionality not yet available via TNE API")
        return None
    
    def add_thread_update(self, *args, **kwargs):
        """Placeholder for plot thread functionality - not implemented in TNE API yet."""
        logger.warning("Plot thread functionality not yet available via TNE API")
        return None
    
    def get_character_arcs(self, *args, **kwargs):
        """Placeholder for character arc functionality - not implemented in TNE API yet."""
        logger.warning("Character arc functionality not yet available via TNE API")
        return []
    
    def get_plot_threads(self, *args, **kwargs):
        """Placeholder for plot thread functionality - not implemented in TNE API yet."""
        logger.warning("Plot thread functionality not yet available via TNE API")
        return []

    def analyze_campaign_state(self):
        """Placeholder for campaign state analysis - not implemented in TNE API yet."""
        logger.warning("Campaign state analysis not yet available via TNE API")
        return {}

    def generate_orchestration_events(self, *args, **kwargs):
        """Placeholder for orchestration functionality - not implemented in TNE API yet."""
        logger.warning("Orchestration functionality not yet available via TNE API")
        return []
    
    # Lore management methods (local to SoloHeart)
    def get_lore_panel_data(self, lore_type: str = None, min_importance: int = 1, discovered_only: bool = False) -> Dict[str, Any]:
        """Get lore panel data from local lore manager."""
        if self.lore_manager:
            # Get all lore entries
            all_entries = list(self.lore_manager.entries.values())
            
            # Apply filters
            if lore_type:
                from lore_manager import LoreType
                try:
                    lore_type_enum = LoreType(lore_type)
                    all_entries = [e for e in all_entries if e.lore_type == lore_type_enum]
                except ValueError:
                    # Invalid lore type, return empty results
                    all_entries = []
            
            if min_importance > 1:
                all_entries = [e for e in all_entries if e.importance_level >= min_importance]
            
            if discovered_only:
                all_entries = [e for e in all_entries if not e.is_secret]
            
            # Build summary
            total_entries = len(all_entries)
            discovered_entries = len([e for e in all_entries if not e.is_secret])
            undiscovered_entries = len([e for e in all_entries if e.is_secret])
            
            # Calculate average importance
            if all_entries:
                avg_importance = sum(e.importance_level for e in all_entries) / total_entries
            else:
                avg_importance = 0
            
            # Count by type
            type_counts = {}
            for entry in all_entries:
                lore_type = entry.lore_type.value
                type_counts[lore_type] = type_counts.get(lore_type, 0) + 1
            
            # Count by importance level
            importance_counts = {}
            for entry in all_entries:
                level = str(entry.importance_level)
                importance_counts[level] = importance_counts.get(level, 0) + 1
            
            return {
                "summary": {
                    "total_entries": total_entries,
                    "discovered_entries": discovered_entries,
                    "undiscovered_entries": undiscovered_entries,
                    "average_importance": round(avg_importance, 2)
                },
                "entries": [entry.to_dict() for entry in all_entries],
                "types": type_counts,
                "importance_levels": importance_counts
            }
        return {
            "summary": {
                "total_entries": 0,
                "discovered_entries": 0,
                "undiscovered_entries": 0,
                "average_importance": 0
            },
            "entries": [],
            "types": {},
            "importance_levels": {}
        }
    
    def search_lore_entries(self, query: str, lore_types: List[str] = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Search lore entries using local lore manager."""
        if self.lore_manager:
            # Convert string lore types to LoreType enums if provided
            lore_type_enums = None
            if lore_types:
                from lore_manager import LoreType
                lore_type_enums = [LoreType(lt) for lt in lore_types]
            
            # Search using LoreManager
            results = self.lore_manager.search_lore(query, lore_types=lore_type_enums, tags=tags)
            return [entry.to_dict() for entry in results]
        return []
    
    def create_lore_entry(self, *args, **kwargs):
        """Create lore entry using local lore manager."""
        if self.lore_manager:
            # Map parameters to match LoreManager.add_lore_entry signature
            from lore_manager import LoreType
            
            # Convert lore_type string to LoreType enum
            if 'lore_type' in kwargs:
                kwargs['lore_type'] = LoreType(kwargs['lore_type'])
            
            # Map 'importance' to 'importance_level'
            if 'importance' in kwargs:
                kwargs['importance_level'] = kwargs.pop('importance')
            
            # Map 'discovered' to 'is_secret' (inverted logic)
            if 'discovered' in kwargs:
                kwargs['is_secret'] = not kwargs.pop('discovered')
            
            entry = self.lore_manager.add_lore_entry(*args, **kwargs)
            return entry.lore_id
        return None
    
    def get_lore_by_type(self, lore_type: str) -> List[Dict[str, Any]]:
        """Get lore by type using local lore manager."""
        if self.lore_manager:
            return [entry.to_dict() for entry in self.lore_manager.get_lore_by_type(lore_type)]
        return []
    
    def get_lore_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get lore by tag using local lore manager."""
        if self.lore_manager:
            return [entry.to_dict() for entry in self.lore_manager.get_lore_by_tag(tag)]
        return []

    def get_diagnostic_report(self, campaign_id: str) -> Dict[str, Any]:
        """Get diagnostic report for the campaign."""
        try:
            # Get campaign summary from TNE
            summary = self.get_campaign_summary()
            
            # Build diagnostic report
            report = {
                "campaign_id": campaign_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "tne_status": summary.get("status", "unknown"),
                "symbolic_profile": summary.get("symbolic_profile", {}),
                "scene_statistics": summary.get("scene_statistics", {}),
                "lore_summary": {
                    "total_entries": len(self.lore_manager.entries) if self.lore_manager else 0
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error getting diagnostic report: {e}")
            return {
                "campaign_id": campaign_id,
                "status": "error",
                "message": str(e)
            }

    # Campaign management methods
    def initialize_campaign(self, character_data: Dict[str, Any], campaign_name: str = None) -> Optional[Dict[str, Any]]:
        """Initialize campaign using TNE API."""
        try:
            # Store character creation data
            success = self.store_character_creation(character_data, self.campaign_id)
            
            if not success:
                logger.error("Failed to store character creation data")
                return None
            
            # Create initial scene
            scene_text = f"Campaign initialized: {campaign_name or 'Unknown Campaign'}"
            scene_data = {"text": scene_text}
            scene_result = self.tne_client.add_scene(scene_data)
            
            if "error" in scene_result:
                logger.warning(f"Failed to create initial scene: {scene_result['error']}")
            
            return {
                "campaign_id": self.campaign_id,
                "character_data": character_data,
                "campaign_name": campaign_name,
                "status": "initialized",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error initializing campaign: {e}")
            return None

    def generate_setting_introduction(self, character_data: Dict[str, Any], campaign_name: str) -> str:
        """Generate setting introduction using TNE symbolic analysis."""
        try:
            # Query TNE for symbolic context
            symbolic_summary = self.tne_client.get_symbolic_summary()
            
            character_name = character_data.get('name', 'Player')
            character_class = character_data.get('class', 'Character')
            
            if "error" not in symbolic_summary:
                # Use symbolic insights for richer introduction
                identity_profile = symbolic_summary.get('result', {}).get('identity_profile', {})
                confidence = identity_profile.get('confidence_score', 0.5)
                
                if confidence > 0.7:
                    tone = "serene and composed"
                elif confidence > 0.4:
                    tone = "cautious but optimistic"
                else:
                    tone = "uncertain but balanced"
            else:
                tone = "balanced"
            
            introduction = f"Welcome to {campaign_name}, {character_name}. As a {character_class}, you stand {tone} at the beginning of your story."
            
            return introduction
            
        except Exception as e:
            logger.error(f"Error generating setting introduction: {e}")
            return f"Welcome to {campaign_name}. Your story begins."

    def load_campaign(self, campaign_id: str) -> bool:
        """Load campaign - mainly updates internal campaign ID."""
        try:
            self.campaign_id = campaign_id
            self.tne_client.set_campaign_id(campaign_id)
            logger.info(f"Campaign loaded: {campaign_id}")
            return True
        except Exception as e:
            logger.error(f"Error loading campaign: {e}")
            return False

    def process_player_input(self, player_input: str, campaign_id: str) -> str:
        """Process player input using TNE scene management."""
        try:
            # Add player input as a scene
            scene_data = {"text": f"Player input: {player_input}"}
            scene_result = self.tne_client.add_scene(scene_data)
            
            if "error" in scene_result:
                logger.warning(f"Failed to process player input: {scene_result['error']}")
            
            # Generate response based on symbolic analysis
            symbolic_summary = self.tne_client.get_symbolic_summary()
            
            if "error" not in symbolic_summary:
                # Use symbolic insights for response generation
                contradictions = symbolic_summary.get('result', {}).get('contradictions', [])
                
                if contradictions:
                    response = f"You consider your next move carefully. {player_input}"
                else:
                    response = f"You proceed with confidence. {player_input}"
            else:
                response = f"You act. {player_input}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing player input: {e}")
            return f"You proceed. {player_input}"

    def save_campaign(self, campaign_id: str) -> bool:
        """Save campaign data using TNE API."""
        try:
            # Get current campaign summary
            summary = self.get_campaign_summary()
            
            # Export to file
            export_path = f"campaign_saves/{campaign_id}_save.json"
            os.makedirs("campaign_saves", exist_ok=True)
            
            success = self.export_campaign_data(export_path)
            
            if success:
                logger.info(f"Campaign saved: {campaign_id}")
                return True
            else:
                logger.error(f"Failed to save campaign: {campaign_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error saving campaign: {e}")
            return False

    def get_campaign_data(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign data from TNE API."""
        try:
            # Get current campaign summary
            summary = self.get_campaign_summary()
            
            # Add campaign ID
            summary['campaign_id'] = campaign_id
            
            return summary
                
        except Exception as e:
            logger.error(f"Error getting campaign data: {e}")
            return None


def create_solo_game_bridge(campaign_id: str, api_key: Optional[str] = None) -> NarrativeBridge:
    """Create a Solo Game narrative bridge instance."""
    return NarrativeBridge(campaign_id=campaign_id)


def store_action_memory(bridge: NarrativeBridge, action_description: str, 
                       location: str, participants: List[str]) -> bool:
    """Store action memory using the bridge."""
    return bridge.store_solo_game_memory(
        content=f"Action at {location}: {action_description}",
        memory_type="action",
        metadata={"location": location, "participants": participants}
    )


def store_mission_memory(bridge: NarrativeBridge, mission_description: str,
                      mission_name: str, location: str) -> bool:
    """Store mission memory using the bridge."""
    return bridge.store_solo_game_memory(
        content=f"Mission '{mission_name}' at {location}: {mission_description}",
        memory_type="mission",
        metadata={"mission_name": mission_name, "location": location}
    )
