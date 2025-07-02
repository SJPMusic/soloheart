"""
Narrative Bridge Module for DnD Game

This module acts as the DnD-specific adapter for The Narrative Engine.
It provides a simplified interface tailored to the DnD game context while
isolating domain-specific logic from engine internals.

The bridge allows easy future replacement or upgrade of the Narrative Engine
without requiring changes to the DnD game code.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import json
import datetime

# Import from the modularized narrative_engine
try:
    from narrative_engine.memory.vector_memory_module import VectorMemoryModule
    from narrative_engine.context.world_state_simulator import WorldStateSimulator
    from narrative_engine.context.contextual_drift_guard import ContextualDriftGuard
    from narrative_engine.core.session_logger import SessionLogger
    from narrative_engine.core.character_manager import CharacterManager
    
    # Import new systems
    from narrative_engine.journaling.player_journal import PlayerJournal, JournalEntryType
    from narrative_engine.memory.emotional_memory import EmotionalMemoryEnhancer, EmotionType
    from narrative_engine.narrative_structure.character_arcs import CharacterArcManager, ArcType, ArcStatus
    from narrative_engine.narrative_structure.plot_threads import PlotThreadManager, ThreadType, ThreadStatus
    from narrative_engine.core.campaign_orchestrator import (
        DynamicCampaignOrchestrator,
        OrchestrationEvent,
        OrchestrationEventType,
        OrchestrationPriority,
        CampaignState
    )
except ImportError as e:
    logging.error(f"Failed to import narrative_engine modules: {e}")
    raise

from lore_manager import LoreManager, LoreType, LoreEntry

logger = logging.getLogger(__name__)

@dataclass
class DnDGameState:
    """DnD-specific game state wrapper"""
    campaign_id: str
    current_location: str
    party_members: List[Dict[str, Any]]
    active_quests: List[Dict[str, Any]]
    world_state: Dict[str, Any]
    session_data: Dict[str, Any]

@dataclass
class DnDMemoryEntry:
    """DnD-specific memory entry"""
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
class DnDNPCResponse:
    """DnD-specific NPC response"""
    text: str
    npc_name: str
    emotional_tone: str
    quest_hints: Optional[List[str]] = None
    combat_ready: bool = False
    relationship_change: Optional[float] = None

class NarrativeBridge:
    """
    Bridge between DnD game and The Narrative Engine
    
    This class provides a DnD-specific interface to the narrative engine,
    handling domain-specific logic while maintaining clean separation
    from the engine internals.
    """
    
    def __init__(self, campaign_id: str = "Default Campaign"):
        """
        Initialize the Narrative Bridge with campaign ID.
        
        Args:
            campaign_id: Unique identifier for the campaign
        """
        self.campaign_id = campaign_id
        
        # Initialize core components
        self.memory_system = VectorMemoryModule(campaign_id=campaign_id)
        self.world_simulator = WorldStateSimulator()
        # Note: SessionLogger requires LayeredMemorySystem, but we're using VectorMemoryModule
        # For now, we'll create a minimal session logger without memory integration
        self.session_logger = None  # Will be initialized when needed
        self.character_manager = CharacterManager()
        
        # Initialize advanced systems
        self.player_journal = PlayerJournal()
        self.emotional_memory = EmotionalMemoryEnhancer()
        self.character_arcs = CharacterArcManager()
        self.plot_threads = PlotThreadManager()
        
        # Initialize campaign orchestrator
        self.campaign_orchestrator = DynamicCampaignOrchestrator(
            storage_path=f"orchestrator_{campaign_id}.jsonl"
        )
        
        # Initialize lore manager
        self.lore_manager = LoreManager(campaign_id)
        
        # Initialize AI DM engine and contextual drift guard
        try:
            from narrative_engine.core.ai_dm_engine import AIDMEngine
            from narrative_engine.context.contextual_drift_guard import ContextualDriftGuard
            
            self.ai_dm_engine = AIDMEngine()
            self.drift_guard = ContextualDriftGuard()
            logger.info("AI DM Engine and Contextual Drift Guard initialized successfully")
        except ImportError as e:
            logger.warning(f"AI DM Engine not available: {e}. Using fallback narration.")
            self.ai_dm_engine = None
            self.drift_guard = None
        except Exception as e:
            logger.warning(f"Error initializing AI DM Engine: {e}. Using fallback narration.")
            self.ai_dm_engine = None
            self.drift_guard = None
        
        logger.info(f"Narrative Bridge initialized for campaign: {campaign_id}")
    
    def store_dnd_memory(
        self,
        content: str,
        memory_type: str = "event",
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        emotional_context: Optional[List[str]] = None,
        primary_emotion: Optional[EmotionType] = None,
        emotional_intensity: float = 0.5,
        character_id: str = "player"
    ) -> bool:
        """
        Store a DnD memory with optional emotional tagging and character association.
        """
        try:
            if primary_emotion is None:
                primary_emotion = self._detect_emotion_from_content(content)
            memory_metadata = metadata or {}
            memory_metadata.update({
                "memory_type": memory_type,
                "tags": tags or [],
                "emotional_context": emotional_context or [],
                "primary_emotion": primary_emotion.value if hasattr(primary_emotion, 'value') else str(primary_emotion),
                "emotional_intensity": emotional_intensity,
                "campaign_id": self.campaign_id,
                "character_id": character_id,
                "timestamp": datetime.datetime.now().isoformat()
            })
            success = self.memory_system.store_memory(
                text=content,
                metadata=memory_metadata
            )
            if primary_emotion and success and self.emotional_memory:
                try:
                    memories = self.memory_system.retrieve_similar(content, top_n=1, filters={"character_id": character_id})
                    if memories:
                        self.emotional_memory.add_emotional_context(
                            memories[0],
                            primary_emotion=primary_emotion,
                            intensity=emotional_intensity
                        )
                except Exception as e:
                    logger.warning(f"Could not enhance memory with emotional context: {e}")
            logger.info(f"Stored DnD memory with emotion {primary_emotion} for {character_id}: {content[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error storing DnD memory: {e}")
            return False

    def store_character_creation(self, character_data: dict, campaign_id: str) -> bool:
        """
        Store complete character creation data in the vector memory system.
        
        Args:
            character_data: Complete character data dictionary
            campaign_id: Campaign ID for the character
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a comprehensive character description
            character_name = character_data.get('name', 'Unknown')
            character_race = character_data.get('race', 'Unknown')
            character_class = character_data.get('class', 'Unknown')
            character_level = character_data.get('level', 1)
            character_background = character_data.get('background', 'Unknown')
            
            # Build a detailed character description
            character_description = f"""
            Character: {character_name}
            Race: {character_race}
            Class: {character_class} (Level {character_level})
            Background: {character_background}
            
            Ability Scores:
            - Strength: {character_data.get('ability_scores', {}).get('strength', 10)}
            - Dexterity: {character_data.get('ability_scores', {}).get('dexterity', 10)}
            - Constitution: {character_data.get('ability_scores', {}).get('constitution', 10)}
            - Intelligence: {character_data.get('ability_scores', {}).get('intelligence', 10)}
            - Wisdom: {character_data.get('ability_scores', {}).get('wisdom', 10)}
            - Charisma: {character_data.get('ability_scores', {}).get('charisma', 10)}
            
            Combat Stats:
            - Hit Points: {character_data.get('hit_points', 10)}
            - Armor Class: {character_data.get('armor_class', 10)}
            
            Proficiencies:
            - Saving Throws: {', '.join(character_data.get('saving_throws', []))}
            - Skills: {', '.join(character_data.get('skills', []))}
            - Feats: {', '.join(character_data.get('feats', []))}
            
            Equipment:
            - Weapons: {', '.join(character_data.get('weapons', []))}
            - Gear: {', '.join(character_data.get('gear', []))}
            - Spells: {', '.join(character_data.get('spells', []))}
            
            Personality: {character_data.get('personality', 'Not specified')}
            Background Story: {character_data.get('background_freeform', 'Not specified')}
            """
            
            # Store the character creation with high importance
            success = self.store_dnd_memory(
                content=character_description,
                memory_type="character_creation",
                metadata=character_data,
                tags=["character_creation", "character_sheet", character_name, character_race, character_class],
                emotional_context=["excitement", "anticipation"],
                primary_emotion=EmotionType.JOY,
                emotional_intensity=0.9,
                character_id=character_name
            )
            
            if success:
                logger.info(f"Successfully stored character creation data for {character_name} in campaign {campaign_id}")
                
                # Also create a journal entry for the character creation
                self.add_journal_entry(
                    character_id=character_name,
                    entry_type=JournalEntryType.CHARACTER_CREATION,
                    title=f"Character Creation: {character_name}",
                    content=f"Created {character_name}, a {character_race} {character_class} with {character_background} background.",
                    tags=["character_creation", character_name, character_race, character_class],
                    emotional_context=["excitement", "anticipation"],
                    metadata=character_data
                )
                
                return True
            else:
                logger.error(f"Failed to store character creation data for {character_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing character creation: {e}")
            return False
    
    def _detect_emotion_from_content(self, content: str) -> EmotionType:
        """
        Detect emotion from content using simple keyword analysis.
        
        Args:
            content: Memory content to analyze
            
        Returns:
            Detected emotion type
        """
        content_lower = content.lower()
        
        # Fear-related keywords
        if any(word in content_lower for word in ["fear", "afraid", "terrified", "scared", "panic", "dread"]):
            return EmotionType.FEAR
        
        # Anger-related keywords
        if any(word in content_lower for word in ["angry", "rage", "fury", "wrath", "hostile", "attack"]):
            return EmotionType.ANGER
        
        # Joy-related keywords
        if any(word in content_lower for word in ["joy", "happy", "excited", "elated", "triumph", "victory"]):
            return EmotionType.JOY
        
        # Sadness-related keywords
        if any(word in content_lower for word in ["sad", "grief", "mourn", "despair", "loss", "defeat"]):
            return EmotionType.SADNESS
        
        # Surprise-related keywords
        if any(word in content_lower for word in ["surprised", "shocked", "amazed", "astonished", "unexpected"]):
            return EmotionType.SURPRISE
        
        # Disgust-related keywords
        if any(word in content_lower for word in ["disgust", "revolted", "sickened", "repulsed", "horror"]):
            return EmotionType.DISGUST
        
        # Trust-related keywords
        if any(word in content_lower for word in ["trust", "faith", "loyal", "alliance", "friend"]):
            return EmotionType.TRUST
        
        # Anticipation-related keywords
        if any(word in content_lower for word in ["anticipate", "expect", "prepare", "ready", "await"]):
            return EmotionType.ANTICIPATION
        
        # Default to determination for action-oriented content
        if any(word in content_lower for word in ["action", "move", "enter", "inspect", "prepare", "question"]):
            return EmotionType.DETERMINATION
        
        # Default to curiosity for exploration
        if any(word in content_lower for word in ["explore", "discover", "find", "search", "investigate"]):
            return EmotionType.CURIOSITY
        
        # Default to wonder for mysterious content
        if any(word in content_lower for word in ["mystery", "strange", "ancient", "crypt", "artifacts"]):
            return EmotionType.WONDER
        
        # Default emotion
        return EmotionType.DETERMINATION
    
    def get_npc_response(self, npc_name: str, context: str, 
                        player_emotion: Optional[Dict[str, float]] = None) -> DnDNPCResponse:
        """
        Generate an NPC response using the narrative engine
        
        Args:
            npc_name: Name of the NPC
            context: Current situation context
            player_emotion: Player's emotional state
            
        Returns:
            DnDNPCResponse: NPC response with DnD-specific context
        """
        try:
            # Get or create NPC character
            npc = self.character_manager.get_character(npc_name)
            if not npc:
                npc = Character(
                    name=npc_name,
                    personality="Adaptive DnD NPC",
                    current_emotion="neutral"
                )
                self.character_manager.add_character(npc)
            
            # Generate response using NPC behavior engine
            response = self.npc_behavior_engine.generate_response(
                npc=npc,
                context=context,
                emotional_context=player_emotion or {}
            )
            
            # Analyze response for DnD-specific elements
            quest_hints = self._extract_quest_hints(response)
            combat_ready = self._detect_combat_readiness(response)
            emotional_tone = self._analyze_emotional_tone(response)
            
            return DnDNPCResponse(
                text=response,
                npc_name=npc_name,
                emotional_tone=emotional_tone,
                quest_hints=quest_hints,
                combat_ready=combat_ready
            )
            
        except Exception as e:
            logger.error(f"Failed to generate NPC response: {e}")
            return DnDNPCResponse(
                text="The NPC seems distracted and doesn't respond clearly.",
                npc_name=npc_name,
                emotional_tone="neutral"
            )
    
    def generate_dm_narration(
        self,
        situation: str,
        player_actions: List[str],
        world_context: Optional[Dict[str, Any]] = None,
        emotional_context: Optional[List[str]] = None
    ) -> str:
        """
        Generate DM narration for a situation.
        
        Args:
            situation: Current situation description
            player_actions: List of player actions
            world_context: World context information
            emotional_context: Emotional context for the situation
            
        Returns:
            Generated narration
        """
        try:
            # Check if AI DM engine is available
            if self.ai_dm_engine is None:
                # Enhanced fallback narration
                return self._generate_fallback_narration(situation, player_actions, emotional_context)
            
            # Prepare context
            context = world_context or {}
            context["situation"] = situation
            context["player_actions"] = player_actions
            context["emotional_context"] = emotional_context or []
            
            # Generate narration using AI DM engine
            narration = self.ai_dm_engine.process_action(
                player_action=situation,
                character_info=world_context.get("character_info"),
                campaign_context=world_context.get("campaign_context", "")
            )
            
            # Validate narration for contextual coherence if drift guard is available
            if self.drift_guard:
                validated_narration = self.drift_guard.validate_narration(narration, context)
            else:
                validated_narration = narration
            
            logger.info(f"Generated DM narration: {validated_narration[:50]}...")
            return validated_narration
            
        except Exception as e:
            logger.error(f"Error generating DM narration: {e}")
            return self._generate_fallback_narration(situation, player_actions, emotional_context)
    
    def _generate_fallback_narration(
        self,
        situation: str,
        player_actions: List[str],
        emotional_context: Optional[List[str]] = None
    ) -> str:
        """
        Generate enhanced fallback narration when AI DM engine is not available.
        
        Args:
            situation: Current situation description
            player_actions: List of player actions
            emotional_context: Emotional context for the situation
            
        Returns:
            Fallback narration
        """
        # Enhanced fallback narration based on action type
        action_lower = situation.lower()
        
        if "crypt" in action_lower or "dungeon" in action_lower:
            return f"The ancient stone walls of the crypt echo with your footsteps as you {situation.lower()}. The air is thick with the weight of centuries, and shadows dance eerily in the torchlight."
        
        elif "inspect" in action_lower or "examine" in action_lower:
            return f"You carefully {situation.lower()}, your trained eyes searching for any hidden details or clues that might reveal the secrets of this place."
        
        elif "hide" in action_lower or "shadows" in action_lower:
            return f"With practiced stealth, you {situation.lower()}. Your rogue training serves you well as you blend into the darkness, becoming one with the shadows."
        
        elif "combat" in action_lower or "prepare" in action_lower:
            return f"Your muscles tense as you {situation.lower()}. Years of training and countless battles have taught you to be ready for anything that might emerge from the darkness."
        
        elif "question" in action_lower or "figure" in action_lower:
            return f"You {situation.lower()}, your voice steady despite the tension. Your noble upbringing and diplomatic training guide your words as you seek to understand this mysterious encounter."
        
        else:
            # Generic enhanced fallback
            emotions = emotional_context or ["determination"]
            emotion_text = ", ".join(emotions)
            return f"With {emotion_text} in your heart, you {situation.lower()}. The world around you responds to your actions, revealing new possibilities and challenges."
    
    def recall_related_memories(
        self,
        query: str,
        max_results: int = 5,
        memory_type: Optional[str] = None,
        emotional_filter: Optional[EmotionType] = None,
        min_emotional_intensity: float = 0.0,
        character_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recall memories related to a query with optional emotional filtering and character filter.
        """
        try:
            filters = {}
            if memory_type:
                filters["memory_type"] = memory_type
            if character_id:
                filters["character_id"] = character_id
            memories = self.memory_system.retrieve_similar(
                query=query,
                top_n=max_results,
                filters=filters
            )
            if emotional_filter:
                from narrative_engine.memory.emotional_memory import EmotionalMemoryFilter
                emotional_filter_obj = EmotionalMemoryFilter()
                memories = emotional_filter_obj.filter_by_emotion(
                    memories, emotional_filter, min_emotional_intensity
                )
            dnd_memories = []
            for memory in memories:
                metadata = memory.get("metadata", {})
                primary_emotion = metadata.get("primary_emotion", "Neutral")
                emotional_intensity = metadata.get("emotional_intensity", 0.5)
                dnd_memory = {
                    "content": memory.get("text", str(memory)),
                    "memory_type": memory.get("memory_type", "event"),
                    "relevance_score": memory.get("importance", 0.5),
                    "location": metadata.get("location"),
                    "quest_related": metadata.get("quest_related"),
                    "combat_related": metadata.get("combat_related", False),
                    "emotional_context": metadata.get("emotional_context", []),
                    "emotion": primary_emotion,
                    "emotional_intensity": emotional_intensity,
                    "tags": metadata.get("tags", []),
                    "timestamp": metadata.get("timestamp"),
                    "character_id": metadata.get("character_id", "player")
                }
                dnd_memories.append(dnd_memory)
            logger.info(f"Recalled {len(dnd_memories)} related memories for {character_id or 'all characters'}")
            return dnd_memories
        except Exception as e:
            logger.error(f"Error recalling memories: {e}")
            return []
    
    def recall_emotional_memories(
        self,
        emotion_type: Optional[EmotionType] = None,
        min_intensity: float = 0.0,
        max_results: int = 10,
        character_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recall memories filtered by emotional content.
        
        Args:
            emotion_type: Specific emotion to filter by
            min_intensity: Minimum emotional intensity (0.0 to 1.0)
            max_results: Maximum number of results to return
            character_id: Optional character filter
            
        Returns:
            List of emotional memories
        """
        try:
            # Get all memories first
            all_memories = self.memory_system.retrieve_similar("", top_n=100)
            
            # Filter by character if specified
            if character_id:
                all_memories = [
                    memory for memory in all_memories 
                    if memory.get("metadata", {}).get("character_id") == character_id
                ]
            
            # Filter by emotional content
            emotional_memories = []
            for memory in all_memories:
                metadata = memory.get("metadata", {})
                memory_emotion = metadata.get("primary_emotion", "Neutral")
                memory_intensity = metadata.get("emotional_intensity", 0.0)
                
                # Check if this memory matches our emotional criteria
                if emotion_type:
                    # Convert emotion to string for comparison
                    emotion_str = emotion_type.value if hasattr(emotion_type, 'value') else str(emotion_type)
                    if memory_emotion != emotion_str:
                        continue
                
                if memory_intensity < min_intensity:
                    continue
                
                # Format the memory for return
                emotional_memory = {
                    "content": memory.get("text", str(memory)),
                    "emotion": memory_emotion,
                    "intensity": memory_intensity,
                    "memory_type": metadata.get("memory_type", "event"),
                    "timestamp": metadata.get("timestamp"),
                    "character_id": metadata.get("character_id", "player"),
                    "tags": metadata.get("tags", []),
                    "emotional_context": metadata.get("emotional_context", [])
                }
                emotional_memories.append(emotional_memory)
            
            # Sort by emotional intensity (highest first) and limit results
            emotional_memories.sort(key=lambda x: x.get("intensity", 0.0), reverse=True)
            emotional_memories = emotional_memories[:max_results]
            
            logger.info(f"Recalled {len(emotional_memories)} emotional memories")
            return emotional_memories
            
        except Exception as e:
            logger.error(f"Error recalling emotional memories: {e}")
            return []
    
    def update_world_state(
        self,
        location: str,
        changes: Dict[str, Any]
    ) -> bool:
        """
        Update the world state for a location.
        
        Args:
            location: Location to update
            changes: Changes to apply
            
        Returns:
            True if updated successfully
        """
        try:
            # FIXED: Updated update_location_state() to use update_location() with correct parameters
            self.world_simulator.update_location(
                campaign_id=self.campaign_id,
                character_id="player",  # Default character ID
                new_location=location,
                location_data=changes
            )
            
            logger.info(f"Updated world state for location: {location}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating world state: {e}")
            return False
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the campaign.
        
        Returns:
            Campaign summary dictionary
        """
        try:
            # Get basic campaign info
            campaign_info = {
                "campaign_id": self.campaign_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Get memory statistics
            try:
                memory_stats = self.memory_system.get_memory_stats()
                campaign_info["memory_count"] = memory_stats.get("total_memories", 0)
            except AttributeError:
                # VectorMemoryModule doesn't have get_memory_stats
                campaign_info["memory_count"] = len(self.memory_system.memories) if hasattr(self.memory_system, 'memories') else 0
            
            # Get session statistics
            if self.session_logger:
                try:
                    session_stats = self.session_logger.get_session_count()
                    campaign_info["session_count"] = session_stats
                except AttributeError:
                    campaign_info["session_count"] = 0
            else:
                campaign_info["session_count"] = 0
            
            # Get journal statistics
            journal_stats = self.player_journal.get_journal_stats(
                campaign_id=self.campaign_id
            )
            campaign_info["journal_entries"] = journal_stats.get("total_entries", 0)
            
            # Get character arc statistics
            arc_stats = self.character_arcs.get_arc_summary(
                campaign_id=self.campaign_id
            )
            campaign_info["character_arcs"] = arc_stats.get("total_arcs", 0)
            
            # Get plot thread statistics
            thread_stats = self.plot_threads.get_thread_summary(
                campaign_id=self.campaign_id
            )
            campaign_info["plot_threads"] = thread_stats.get("total_threads", 0)
            
            # FIXED: Updated get_all_locations() to use get_current_state() and extract locations
            campaign_info["world_locations"] = self.world_simulator.get_current_state(self.campaign_id).get("locations", {})
            
            logger.info(f"Generated campaign summary for {self.campaign_id}")
            return campaign_info
            
        except Exception as e:
            logger.error(f"Error getting campaign summary: {e}")
            return {
                "campaign_id": self.campaign_id,
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def export_campaign_data(
        self,
        export_path: str,
        include_journals: bool = True,
        include_arcs: bool = True,
        include_threads: bool = True
    ) -> bool:
        """
        Export campaign data to various formats.
        
        Args:
            export_path: Base path for exports
            include_journals: Whether to export journals
            include_arcs: Whether to export character arcs
            include_threads: Whether to export plot threads
            
        Returns:
            True if export successful
        """
        try:
            # Export journal entries
            if include_journals:
                journal_entries = self.player_journal.get_entries_by_character(
                    "player", self.campaign_id
                )
                JournalExporter.export_to_markdown(
                    journal_entries,
                    f"{export_path}_journal.md",
                    include_metadata=True,
                    group_by="entry_type"
                )
                JournalExporter.export_to_jsonl(
                    journal_entries,
                    f"{export_path}_journal.jsonl",
                    include_metadata=True
                )
            
            # Export character arcs
            if include_arcs:
                arcs = self.character_arcs.get_arcs_by_campaign(self.campaign_id)
                # Note: Arc export functionality would need to be implemented
            
            # Export plot threads
            if include_threads:
                threads = self.plot_threads.get_threads_by_campaign(self.campaign_id)
                # Note: Thread export functionality would need to be implemented
            
            logger.info(f"Exported campaign data to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting campaign data: {e}")
            return False
    
    def _extract_quest_hints(self, response: str) -> List[str]:
        """Extract quest-related hints from NPC response"""
        # Simple keyword-based extraction
        quest_keywords = ["quest", "mission", "task", "objective", "goal", "seeking", "need"]
        hints = []
        
        for keyword in quest_keywords:
            if keyword.lower() in response.lower():
                # Extract sentence containing keyword
                sentences = response.split('.')
                for sentence in sentences:
                    if keyword.lower() in sentence.lower():
                        hints.append(sentence.strip())
        
        return hints[:3]  # Limit to 3 hints
    
    def _detect_combat_readiness(self, response: str) -> bool:
        """Detect if NPC response indicates combat readiness"""
        combat_keywords = ["fight", "battle", "attack", "defend", "weapon", "ready", "threat"]
        return any(keyword.lower() in response.lower() for keyword in combat_keywords)
    
    def _analyze_emotional_tone(self, response: str) -> str:
        """Analyze emotional tone of response"""
        positive_words = ["happy", "glad", "pleased", "excited", "grateful", "friendly"]
        negative_words = ["angry", "sad", "fearful", "hostile", "suspicious", "worried"]
        
        pos_count = sum(1 for word in positive_words if word in response.lower())
        neg_count = sum(1 for word in negative_words if word in response.lower())
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
    
    def add_journal_entry(
        self,
        character_id: str,
        entry_type: JournalEntryType,
        title: str,
        content: str,
        session_id: Optional[str] = None,
        location: Optional[str] = None,
        scene: Optional[str] = None,
        tags: Optional[List[str]] = None,
        emotional_context: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Add a journal entry for a character.
        
        Args:
            character_id: ID of the character
            entry_type: Type of journal entry
            title: Entry title
            content: Entry content
            session_id: Optional session ID
            location: Optional location
            scene: Optional scene
            tags: Optional tags
            emotional_context: Optional emotional context
            metadata: Optional metadata
            
        Returns:
            Entry ID if successful, None otherwise
        """
        try:
            entry = self.player_journal.add_entry(
                character_id=character_id,
                campaign_id=self.campaign_id,
                entry_type=entry_type,
                title=title,
                content=content,
                session_id=session_id,
                location=location,
                scene=scene,
                tags=tags,
                emotional_context=emotional_context,
                metadata=metadata
            )
            
            logger.info(f"Added journal entry: {title} for character {character_id}")
            return entry.entry_id
            
        except Exception as e:
            logger.error(f"Error adding journal entry: {e}")
            return None
    
    def get_journal_entries(
        self,
        character_id: Optional[str] = None,
        session_id: Optional[str] = None,
        entry_type: Optional[JournalEntryType] = None,
        max_entries: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get journal entries with optional filtering.
        
        Args:
            character_id: Optional character filter
            session_id: Optional session filter
            entry_type: Optional entry type filter
            max_entries: Maximum number of entries to return (default: 50)
            
        Returns:
            List of journal entries in reverse chronological order (newest first)
        """
        try:
            if character_id:
                entries = self.player_journal.get_entries_by_character(
                    character_id, self.campaign_id, max_entries
                )
            elif session_id:
                entries = self.player_journal.get_entries_by_session(session_id, character_id)
            else:
                entries = self.player_journal.get_entries_by_character(
                    "player", self.campaign_id, max_entries
                )
            
            # Filter by entry type if specified
            if entry_type:
                entries = [entry for entry in entries if entry.entry_type == entry_type]
            
            # Convert to dictionary format and sort by timestamp (newest first)
            dict_entries = [entry.to_dict() for entry in entries]
            
            # Sort by timestamp in reverse chronological order (newest first)
            dict_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Limit to max_entries
            return dict_entries[:max_entries]
            
        except Exception as e:
            logger.error(f"Error getting journal entries: {e}")
            return []
    
    def create_character_arc(
        self,
        character_id: str,
        name: str,
        arc_type: ArcType,
        description: str,
        target_completion: Optional[datetime.datetime] = None,
        tags: Optional[List[str]] = None,
        emotional_themes: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a character arc.
        
        Args:
            character_id: ID of the character
            name: Arc name
            arc_type: Type of arc
            description: Arc description
            target_completion: Optional target completion date
            tags: Optional tags
            emotional_themes: Optional emotional themes
            metadata: Optional metadata
            
        Returns:
            Arc ID if successful, None otherwise
        """
        try:
            arc = self.character_arcs.create_arc(
                character_id=character_id,
                campaign_id=self.campaign_id,
                name=name,
                arc_type=arc_type,
                description=description,
                target_completion=target_completion,
                tags=tags,
                emotional_themes=emotional_themes,
                metadata=metadata
            )
            
            logger.info(f"Created character arc: {name} for character {character_id}")
            return arc.arc_id
            
        except Exception as e:
            logger.error(f"Error creating character arc: {e}")
            return None
    
    def add_arc_milestone(
        self,
        arc_id: str,
        title: str,
        description: str,
        memory_ids: Optional[List[str]] = None,
        emotional_context: Optional[str] = None,
        completion_percentage: float = 0.0
    ) -> Optional[str]:
        """
        Add a milestone to a character arc.
        
        Args:
            arc_id: ID of the arc
            title: Milestone title
            description: Milestone description
            memory_ids: Associated memory IDs
            emotional_context: Emotional context
            completion_percentage: Completion percentage
            
        Returns:
            Milestone ID if successful, None otherwise
        """
        try:
            milestone = self.character_arcs.add_milestone_to_arc(
                arc_id=arc_id,
                title=title,
                description=description,
                memory_ids=memory_ids,
                emotional_context=emotional_context,
                completion_percentage=completion_percentage
            )
            
            if milestone:
                logger.info(f"Added milestone: {title} to arc {arc_id}")
                return milestone.milestone_id
            return None
            
        except Exception as e:
            logger.error(f"Error adding arc milestone: {e}")
            return None
    
    def create_plot_thread(
        self,
        name: str,
        thread_type: ThreadType,
        description: str,
        priority: int = 1,
        assigned_characters: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a plot thread.
        
        Args:
            name: Thread name
            thread_type: Type of thread
            description: Thread description
            priority: Thread priority (1-10)
            assigned_characters: Optional assigned characters
            tags: Optional tags
            metadata: Optional metadata
            
        Returns:
            Thread ID if successful, None otherwise
        """
        try:
            thread = self.plot_threads.create_thread(
                campaign_id=self.campaign_id,
                name=name,
                thread_type=thread_type,
                description=description,
                priority=priority,
                assigned_characters=assigned_characters,
                tags=tags,
                metadata=metadata
            )
            
            logger.info(f"Created plot thread: {name}")
            return thread.thread_id
            
        except Exception as e:
            logger.error(f"Error creating plot thread: {e}")
            return None
    
    def add_thread_update(
        self,
        thread_id: str,
        title: str,
        description: str,
        memory_ids: Optional[List[str]] = None,
        status_change: Optional[ThreadStatus] = None,
        priority_change: Optional[int] = None
    ) -> Optional[str]:
        """
        Add an update to a plot thread.
        
        Args:
            thread_id: ID of the thread
            title: Update title
            description: Update description
            memory_ids: Associated memory IDs
            status_change: Optional status change
            priority_change: Optional priority change
            
        Returns:
            Update ID if successful, None otherwise
        """
        try:
            update = self.plot_threads.add_update_to_thread(
                thread_id=thread_id,
                title=title,
                description=description,
                memory_ids=memory_ids,
                status_change=status_change,
                priority_change=priority_change
            )
            
            if update:
                logger.info(f"Added update: {title} to thread {thread_id}")
                return update.update_id
            return None
            
        except Exception as e:
            logger.error(f"Error adding thread update: {e}")
            return None
    
    def get_character_arcs(
        self,
        character_id: Optional[str] = None,
        status: Optional[ArcStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Get character arcs with optional filtering.
        
        Args:
            character_id: Optional character filter
            status: Optional status filter
            
        Returns:
            List of character arcs
        """
        try:
            arcs = self.character_arcs.get_arcs_by_character(
                character_id or "player", self.campaign_id, status
            )
            
            # Convert to dictionary format
            return [arc.to_dict() for arc in arcs]
            
        except Exception as e:
            logger.error(f"Error getting character arcs: {e}")
            return []
    
    def get_plot_threads(
        self,
        status: Optional[ThreadStatus] = None,
        min_priority: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get plot threads with optional filtering.
        
        Args:
            status: Optional status filter
            min_priority: Minimum priority filter
            
        Returns:
            List of plot threads
        """
        try:
            if status:
                threads = self.plot_threads.get_threads_by_campaign(
                    self.campaign_id, status
                )
            else:
                threads = self.plot_threads.get_open_threads(
                    self.campaign_id, min_priority
                )
            
            # Convert to dictionary format
            return [thread.to_dict() for thread in threads]
            
        except Exception as e:
            logger.error(f"Error getting plot threads: {e}")
            return []

    # Campaign Orchestrator Integration Methods
    
    def analyze_campaign_state(self) -> CampaignState:
        """
        Analyze the current state of the campaign for orchestration.
        
        Returns:
            CampaignState object with current analysis
        """
        try:
            return self.campaign_orchestrator.analyze_campaign_state(self, self.campaign_id)
        except Exception as e:
            logger.error(f"Error analyzing campaign state: {e}")
            # Return minimal state
            return CampaignState(
                campaign_id=self.campaign_id,
                active_arcs=[],
                open_threads=[],
                recent_memories=[],
                emotional_context={},
                character_locations={},
                world_events=[],
                session_count=0
            )
    
    def generate_orchestration_events(self, max_events: int = 3) -> List[OrchestrationEvent]:
        """
        Generate orchestration events based on current campaign state.
        
        Args:
            max_events: Maximum number of events to generate
            
        Returns:
            List of generated orchestration events
        """
        try:
            campaign_state = self.analyze_campaign_state()
            return self.campaign_orchestrator.generate_orchestration_events(campaign_state, max_events)
        except Exception as e:
            logger.error(f"Error generating orchestration events: {e}")
            return []
    
    def get_pending_orchestration_events(
        self,
        priority: Optional[OrchestrationPriority] = None,
        event_type: Optional[OrchestrationEventType] = None
    ) -> List[OrchestrationEvent]:
        """
        Get pending orchestration events.
        
        Args:
            priority: Optional priority filter
            event_type: Optional event type filter
            
        Returns:
            List of pending events
        """
        try:
            return self.campaign_orchestrator.get_pending_events(priority, event_type)
        except Exception as e:
            logger.error(f"Error getting pending events: {e}")
            return []
    
    def execute_orchestration_event(
        self,
        event_id: str,
        execution_notes: Optional[str] = None
    ) -> bool:
        """
        Execute an orchestration event.
        
        Args:
            event_id: ID of the event to execute
            execution_notes: Optional notes about execution
            
        Returns:
            True if executed successfully
        """
        try:
            return self.campaign_orchestrator.execute_event(
                event_id,
                self,
                execution_notes
            )
        except Exception as e:
            logger.error(f"Error executing orchestration event: {e}")
            return False
    
    def get_orchestration_summary(self) -> Dict[str, Any]:
        """Get a summary of orchestration activity."""
        return self.campaign_orchestrator.get_orchestration_summary()
    
    def get_triggered_orchestration_events(self, action_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get orchestration events that were triggered by the last action.
        
        Args:
            action_context: Context about the action that was just performed
                - action: The action text
                - character: Character performing the action
                - location: Location where action occurred
                - emotional_context: Emotional context of the action
                
        Returns:
            List of triggered event data for UI display
        """
        try:
            # Enhance events with campaign context before returning
            triggered_events = self.campaign_orchestrator.get_triggered_events(action_context)
            
            # Enhance each event with additional context
            campaign_state = self.analyze_campaign_state()
            enhanced_events = []
            
            for event_data in triggered_events:
                # Find the actual event object to enhance
                event_id = event_data.get('event_id')
                if event_id in self.campaign_orchestrator.events:
                    event = self.campaign_orchestrator.events[event_id]
                    enhanced_event = self.campaign_orchestrator.enhance_event_with_context(event, campaign_state)
                    enhanced_events.append(self.campaign_orchestrator._format_event_for_ui(enhanced_event))
                else:
                    enhanced_events.append(event_data)
            
            logger.info(f"Found {len(enhanced_events)} triggered orchestration events")
            return enhanced_events
            
        except Exception as e:
            logger.error(f"Error getting triggered orchestration events: {e}")
            return []
    
    def get_orchestration_event_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent orchestration event history for timeline display.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events formatted for UI
        """
        try:
            return self.campaign_orchestrator.get_event_history(limit)
        except Exception as e:
            logger.error(f"Error getting orchestration event history: {e}")
            return []
    
    def get_active_orchestration_events(self) -> List[Dict[str, Any]]:
        """
        Get all currently active (pending) orchestration events.
        
        Returns:
            List of active events formatted for UI
        """
        try:
            pending_events = self.campaign_orchestrator.get_pending_events()
            campaign_state = self.analyze_campaign_state()
            
            enhanced_events = []
            for event in pending_events:
                enhanced_event = self.campaign_orchestrator.enhance_event_with_context(event, campaign_state)
                enhanced_events.append(self.campaign_orchestrator._format_event_for_ui(enhanced_event))
            
            return enhanced_events
        except Exception as e:
            logger.error(f"Error getting active orchestration events: {e}")
            return []
    
    def get_orchestration_insights(self) -> Dict[str, Any]:
        """Get insights about the current orchestration state."""
        try:
            campaign_state = self.analyze_campaign_state()
            active_events = self.get_active_orchestration_events()
            
            insights = {
                "campaign_momentum": self._calculate_campaign_momentum(campaign_state),
                "pressure_points": self._identify_pressure_points(campaign_state, active_events),
                "emotional_themes": self._extract_emotional_themes(campaign_state),
                "active_events_count": len(active_events),
                "pending_decisions": len([e for e in active_events if e.get("requires_player_decision", False)]),
                "campaign_complexity": self._calculate_campaign_complexity(campaign_state),
                "narrative_coherence": self._assess_narrative_coherence(),
                "character_development_opportunities": self._identify_character_development_opportunities(),
                "world_building_hooks": self._identify_world_building_hooks(),
                "quest_opportunities": self._identify_quest_opportunities(),
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting orchestration insights: {e}")
            return {
                "error": str(e),
                "campaign_momentum": "unknown",
                "pressure_points": [],
                "emotional_themes": [],
                "active_events_count": 0,
                "pending_decisions": 0,
                "campaign_complexity": "low",
                "narrative_coherence": "unknown",
                "character_development_opportunities": [],
                "world_building_hooks": [],
                "quest_opportunities": [],
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def get_campaign_progression_suggestions(self) -> List[Dict[str, Any]]:
        """Get suggestions for campaign progression based on current state."""
        try:
            campaign_state = self.analyze_campaign_state()
            active_events = self.get_active_orchestration_events()
            recent_memories = self.memory_system.retrieve_similar("", top_n=5)
            
            suggestions = []
            
            # Character development suggestions
            character_arcs = self.get_character_arcs()
            for arc in character_arcs:
                if arc.get("status") == ArcStatus.ACTIVE:
                    suggestions.append({
                        "type": "character_development",
                        "title": f"Develop {arc.get('name', 'Character Arc')}",
                        "description": f"Focus on {arc.get('description', 'character growth')}",
                        "priority": "medium",
                        "related_arc": arc.get("id")
                    })
            
            # Plot thread suggestions
            plot_threads = self.get_plot_threads()
            for thread in plot_threads:
                if thread.get("status") == ThreadStatus.ACTIVE:
                    suggestions.append({
                        "type": "plot_advancement",
                        "title": f"Advance {thread.get('name', 'Plot Thread')}",
                        "description": f"Explore {thread.get('description', 'this storyline')}",
                        "priority": "high" if thread.get("priority", 1) > 5 else "medium",
                        "related_thread": thread.get("id")
                    })
            
            # World exploration suggestions
            if recent_memories:
                suggestions.append({
                    "type": "world_exploration",
                    "title": "Explore Recent Discoveries",
                    "description": "Investigate the mysteries and locations you've encountered",
                    "priority": "medium"
                })
            
            # Emotional development suggestions
            emotional_memories = self.emotional_memory.get_emotional_memories() if self.emotional_memory else []
            if emotional_memories:
                suggestions.append({
                    "type": "emotional_development",
                    "title": "Process Emotional Experiences",
                    "description": "Reflect on recent emotional events and their impact",
                    "priority": "low"
                })
            
            # Quest suggestions based on active events
            for event in active_events:
                if event.get("event_type") == OrchestrationEventType.QUEST_OPPORTUNITY:
                    suggestions.append({
                        "type": "quest_opportunity",
                        "title": event.get("title", "New Quest Available"),
                        "description": event.get("description", "A new quest has emerged"),
                        "priority": "high",
                        "related_event": event.get("id")
                    })
            
            return suggestions[:10]  # Limit to top 10 suggestions
            
        except Exception as e:
            logger.error(f"Error getting campaign progression suggestions: {e}")
            return []
    
    def _calculate_campaign_complexity(self, campaign_state: CampaignState) -> str:
        """Calculate campaign complexity based on various factors."""
        try:
            complexity_score = 0
            
            # Factor in number of active arcs
            complexity_score += len(self.get_character_arcs(status=ArcStatus.ACTIVE)) * 2
            
            # Factor in number of active plot threads
            complexity_score += len(self.get_plot_threads(status=ThreadStatus.ACTIVE)) * 3
            
            # Factor in number of active orchestration events
            complexity_score += len(self.get_active_orchestration_events()) * 1
            
            # Factor in emotional complexity
            if self.emotional_memory:
                emotional_memories = self.emotional_memory.get_emotional_memories()
                complexity_score += len(emotional_memories) * 0.5
            
            if complexity_score < 5:
                return "low"
            elif complexity_score < 15:
                return "medium"
            else:
                return "high"
                
        except Exception as e:
            logger.error(f"Error calculating campaign complexity: {e}")
            return "unknown"
    
    def _assess_narrative_coherence(self) -> str:
        """Assess the coherence of the current narrative."""
        try:
            # This is a simplified assessment
            recent_memories = self.memory_system.retrieve_similar("", top_n=10)
            if len(recent_memories) < 3:
                return "building"
            
            # Check for thematic consistency
            themes = set()
            for memory in recent_memories:
                if "tags" in memory.get("metadata", {}):
                    themes.update(memory["metadata"]["tags"])
            
            if len(themes) <= 3:
                return "coherent"
            elif len(themes) <= 6:
                return "moderate"
            else:
                return "complex"
                
        except Exception as e:
            logger.error(f"Error assessing narrative coherence: {e}")
            return "unknown"
    
    def _identify_character_development_opportunities(self) -> List[Dict[str, Any]]:
        """Identify opportunities for character development."""
        try:
            opportunities = []
            character_arcs = self.get_character_arcs(status=ArcStatus.ACTIVE)
            
            for arc in character_arcs:
                if arc.get("completion_percentage", 0) < 50:
                    opportunities.append({
                        "arc_id": arc.get("id"),
                        "title": arc.get("name"),
                        "description": f"Continue developing {arc.get('name', 'this character arc')}",
                        "current_progress": arc.get("completion_percentage", 0)
                    })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error identifying character development opportunities: {e}")
            return []
    
    def _identify_world_building_hooks(self) -> List[Dict[str, Any]]:
        """Identify opportunities for world building."""
        try:
            hooks = []
            recent_memories = self.memory_system.retrieve_similar("", top_n=5)
            
            for memory in recent_memories:
                content = memory.get("text", "").lower()
                if any(keyword in content for keyword in ["mysterious", "ancient", "legend", "rumor", "strange"]):
                    hooks.append({
                        "memory_id": memory.get("id"),
                        "title": "Explore Mysterious Elements",
                        "description": f"Investigate: {memory.get('text', '')[:100]}...",
                        "type": "mystery"
                    })
            
            return hooks[:3]  # Limit to top 3
            
        except Exception as e:
            logger.error(f"Error identifying world building hooks: {e}")
            return []
    
    def _identify_quest_opportunities(self) -> List[Dict[str, Any]]:
        """Identify potential quest opportunities."""
        try:
            opportunities = []
            active_events = self.get_active_orchestration_events()
            
            for event in active_events:
                if event.get("event_type") in [OrchestrationEventType.QUEST_OPPORTUNITY, OrchestrationEventType.ENCOUNTER]:
                    opportunities.append({
                        "event_id": event.get("id"),
                        "title": event.get("title", "Quest Opportunity"),
                        "description": event.get("description", "A new quest has emerged"),
                        "type": event.get("event_type", "unknown")
                    })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error identifying quest opportunities: {e}")
            return []

    def get_narrative_dynamics(self, campaign_id: str) -> Dict[str, Any]:
        """Get real-time narrative dynamics data for the UI."""
        try:
            # Analyze campaign state
            campaign_state = self.campaign_orchestrator.analyze_campaign_state(self, campaign_id)
            
            # Generate orchestration events
            events = self.campaign_orchestrator.generate_orchestration_events(campaign_state, max_events=5)
            
            # Detect conflicts
            conflicts = self.campaign_orchestrator.detect_conflicts(campaign_state)
            
            # Enhance events with context
            enhanced_events = []
            for event in events:
                enhanced_event = self.campaign_orchestrator.enhance_event_with_context(event, campaign_state)
                enhanced_events.append(enhanced_event)
            
            # Get recent event history
            event_history = self.campaign_orchestrator.get_event_history(limit=5)
            
            # Calculate campaign momentum
            momentum = self._calculate_campaign_momentum(campaign_state)
            
            # Get emotional themes
            emotional_themes = self._extract_emotional_themes(campaign_state)
            
            # Get pressure points
            pressure_points = self._identify_pressure_points(campaign_state, conflicts)
            
            return {
                'campaign_id': campaign_id,
                'momentum': momentum,
                'emotional_themes': emotional_themes,
                'pressure_points': pressure_points,
                'active_events': [self.campaign_orchestrator._format_event_for_ui(event) for event in enhanced_events],
                'recent_events': event_history,
                'active_conflicts': [self._format_conflict_for_ui(conflict) for conflict in conflicts],
                'campaign_state': {
                    'active_arcs': len(campaign_state.active_arcs),
                    'open_threads': len(campaign_state.open_threads),
                    'recent_memories': len(campaign_state.recent_memories),
                    'session_count': campaign_state.session_count
                }
            }
        except Exception as e:
            logger.error(f"Error getting narrative dynamics: {e}")
            return {
                'campaign_id': campaign_id,
                'momentum': 'stable',
                'emotional_themes': [],
                'pressure_points': [],
                'active_events': [],
                'recent_events': [],
                'active_conflicts': [],
                'campaign_state': {
                    'active_arcs': 0,
                    'open_threads': 0,
                    'recent_memories': 0,
                    'session_count': 0
                }
            }
    
    def get_conflict_nodes(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get all active conflict nodes for the campaign."""
        try:
            # Analyze campaign state
            campaign_state = self.campaign_orchestrator.analyze_campaign_state(self, campaign_id)
            
            # Detect conflicts
            conflicts = self.campaign_orchestrator.detect_conflicts(campaign_state)
            
            # Get existing active conflicts
            active_conflicts = self.campaign_orchestrator.get_active_conflicts()
            
            # Combine and format
            all_conflicts = conflicts + active_conflicts
            
            return [self._format_conflict_for_ui(conflict) for conflict in all_conflicts]
        except Exception as e:
            logger.error(f"Error getting conflict nodes: {e}")
            return []
    
    def _extract_emotional_themes(self, campaign_state: CampaignState) -> List[str]:
        """Extract dominant emotional themes from campaign state."""
        try:
            emotional_themes = []
            
            # Extract from emotional context
            for emotion, intensity in campaign_state.emotional_context.items():
                if intensity > 0.5:  # Only include significant emotions
                    emotional_themes.append(emotion)
            
            # Extract from recent memories
            for memory in campaign_state.recent_memories:
                emotional_context = memory.get('metadata', {}).get('emotional_context', [])
                emotional_themes.extend(emotional_context)
            
            # Return unique themes, sorted by frequency
            theme_counts = {}
            for theme in emotional_themes:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
            
            return [theme for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
            
        except Exception as e:
            logger.error(f"Error extracting emotional themes: {e}")
            return []
    
    def _format_conflict_for_ui(self, conflict) -> Dict[str, Any]:
        """Format a conflict node for UI display."""
        try:
            return {
                'id': conflict.conflict_id,
                'type': conflict.conflict_type.value,
                'urgency': conflict.urgency.value,
                'title': conflict.title,
                'description': conflict.description,
                'characters_involved': conflict.characters_involved,
                'related_arcs': conflict.related_arcs,
                'related_threads': conflict.related_threads,
                'suggested_resolutions': conflict.suggested_resolutions,
                'impact_preview': conflict.impact_preview,
                'emotional_context': conflict.emotional_context,
                'value_contradictions': conflict.value_contradictions,
                'created_timestamp': conflict.created_timestamp.isoformat(),
                'conflict_icon': conflict.conflict_icon,
                'urgency_color': self._get_urgency_color(conflict.urgency.value),
                'type_label': self._get_conflict_type_label(conflict.conflict_type.value)
            }
        except Exception as e:
            logger.error(f"Error formatting conflict for UI: {e}")
            return {
                'id': conflict.conflict_id if hasattr(conflict, 'conflict_id') else 'unknown',
                'type': 'unknown',
                'urgency': 'medium',
                'title': 'Unknown Conflict',
                'description': 'Error formatting conflict',
                'characters_involved': [],
                'related_arcs': [],
                'related_threads': [],
                'suggested_resolutions': [],
                'impact_preview': {},
                'emotional_context': [],
                'value_contradictions': [],
                'created_timestamp': datetime.datetime.now().isoformat(),
                'conflict_icon': '❓',
                'urgency_color': 'yellow',
                'type_label': 'Unknown'
            }
    
    def _get_urgency_color(self, urgency: str) -> str:
        """Get color for urgency level."""
        colors = {
            'critical': 'red',
            'high': 'orange',
            'medium': 'yellow',
            'low': 'green'
        }
        return colors.get(urgency, 'gray')
    
    def _get_conflict_type_label(self, conflict_type: str) -> str:
        """Get human-readable label for conflict type."""
        labels = {
            'internal': 'Internal Struggle',
            'interpersonal': 'Party Conflict',
            'external': 'External Threat'
        }
        return labels.get(conflict_type, 'Unknown')
    
    def resolve_conflict(self, conflict_id: str, resolution_id: str, campaign_id: str) -> bool:
        """Resolve a conflict with a specific resolution."""
        try:
            success = self.campaign_orchestrator.resolve_conflict(conflict_id, resolution_id, self)
            if success:
                logger.info(f"Successfully resolved conflict {conflict_id}")
            return success
        except Exception as e:
            logger.error(f"Error resolving conflict: {e}")
            return False
    
    def get_conflict_summary(self, campaign_id: str) -> Dict[str, Any]:
        """Get a summary of conflict activity for the campaign."""
        try:
            return self.campaign_orchestrator.get_conflict_summary()
        except Exception as e:
            logger.error(f"Error getting conflict summary: {e}")
            return {
                'total_conflicts': 0,
                'active_conflicts': 0,
                'resolved_conflicts': 0,
                'conflict_types': {},
                'urgency_breakdown': {}
            }

    def get_conflict_timeline(self, campaign_id: str):
        from solo_heart.narrative_diagnostics import generate_conflict_timeline
        return generate_conflict_timeline(campaign_id)

    def get_arc_map(self, campaign_id: str):
        from solo_heart.narrative_diagnostics import generate_arc_map
        return generate_arc_map(campaign_id)

    def get_emotion_heatmap(self, campaign_id: str):
        from solo_heart.narrative_diagnostics import generate_emotion_heatmap
        return generate_emotion_heatmap(campaign_id)

    def get_diagnostic_report(self, campaign_id: str):
        from solo_heart.narrative_diagnostics import generate_diagnostic_report
        return generate_diagnostic_report(campaign_id)

    # Lore Management Methods
    def get_lore_panel_data(self) -> Dict[str, Any]:
        """Get all data needed for the lore panel"""
        try:
            # Get all lore entries
            all_entries = self.lore_manager.get_lore_entries()
            
            # Convert to serializable format
            entries_data = []
            for entry in all_entries:
                entries_data.append({
                    "id": entry.lore_id,
                    "title": entry.title,
                    "type": entry.lore_type.value,
                    "content": entry.content,
                    "tags": entry.tags,
                    "importance_level": entry.importance_level,
                    "is_secret": entry.is_secret,
                    "discovered_by": entry.discovered_by,
                    "discovery_context": entry.discovery_context,
                    "created_at": entry.created_at.isoformat(),
                    "updated_at": entry.updated_at.isoformat(),
                    "linked_items": entry.linked_items
                })
            
            # Get lore summary
            summary = self.lore_manager.get_lore_summary()
            
            return {
                "entries": entries_data,
                "summary": summary,
                "total_entries": len(entries_data)
            }
        except Exception as e:
            logger.error(f"Error getting lore panel data: {e}")
            return {"entries": [], "summary": {}, "total_entries": 0}
    
    def search_lore_entries(self, query: str, lore_types: List[str] = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Search lore entries"""
        try:
            # Convert string types to LoreType enums
            type_enums = None
            if lore_types:
                type_enums = [LoreType(t) for t in lore_types if t in [lt.value for lt in LoreType]]
            
            # Search lore entries
            results = self.lore_manager.search_lore(
                query=query,
                lore_types=type_enums,
                tags=tags
            )
            
            # Convert to serializable format
            entries_data = []
            for entry in results:
                entries_data.append({
                    "id": entry.lore_id,
                    "title": entry.title,
                    "type": entry.lore_type.value,
                    "content": entry.content,
                    "tags": entry.tags,
                    "importance_level": entry.importance_level,
                    "is_secret": entry.is_secret,
                    "discovered_by": entry.discovered_by,
                    "discovery_context": entry.discovery_context,
                    "created_at": entry.created_at.isoformat(),
                    "updated_at": entry.updated_at.isoformat(),
                    "linked_items": entry.linked_items
                })
            
            return entries_data
        except Exception as e:
            logger.error(f"Error searching lore entries: {e}")
            return []
    
    def get_lore_entry_by_id(self, lore_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific lore entry by ID"""
        try:
            entry = self.lore_manager.get_lore_entry_by_id(lore_id)
            if entry:
                return {
                    "id": entry.lore_id,
                    "title": entry.title,
                    "type": entry.lore_type.value,
                    "content": entry.content,
                    "tags": entry.tags,
                    "importance_level": entry.importance_level,
                    "is_secret": entry.is_secret,
                    "discovered_by": entry.discovered_by,
                    "discovery_context": entry.discovery_context,
                    "created_at": entry.created_at.isoformat(),
                    "updated_at": entry.updated_at.isoformat(),
                    "linked_items": entry.linked_items
                }
            return None
        except Exception as e:
            logger.error(f"Error getting lore entry by ID: {e}")
            return None
    
    def create_lore_entry(self, 
                         title: str,
                         lore_type: str,
                         content: str,
                         tags: List[str] = None,
                         discovered_by: str = None,
                         discovery_context: str = None,
                         importance_level: int = 1,
                         is_secret: bool = False) -> Optional[str]:
        """Create a new lore entry"""
        try:
            # Convert string type to LoreType enum
            try:
                lore_type_enum = LoreType(lore_type)
            except ValueError:
                logger.error(f"Invalid lore type: {lore_type}")
                return None
            
            entry = self.lore_manager.add_lore_entry(
                title=title,
                lore_type=lore_type_enum,
                content=content,
                tags=tags or [],
                discovered_by=discovered_by,
                discovery_context=discovery_context,
                importance_level=importance_level,
                is_secret=is_secret
            )
            
            return entry.lore_id
        except Exception as e:
            logger.error(f"Error creating lore entry: {e}")
            return None
    
    def create_lore_entry_from_event(self, 
                                   event_data: Dict[str, Any],
                                   event_type: str = "orchestration") -> Optional[str]:
        """Auto-generate lore entry from orchestration event or memory"""
        try:
            if event_type == "orchestration":
                return self._create_lore_from_orchestration_event(event_data)
            elif event_type == "memory":
                return self._create_lore_from_memory_entry(event_data)
            elif event_type == "conflict":
                return self._create_lore_from_conflict_resolution(event_data)
            else:
                logger.warning(f"Unknown event type for lore generation: {event_type}")
                return None
        except Exception as e:
            logger.error(f"Error creating lore entry from event: {e}")
            return None
    
    def _create_lore_from_orchestration_event(self, event_data: Dict[str, Any]) -> Optional[str]:
        """Create lore entry from orchestration event"""
        try:
            title = event_data.get("title", "Unknown Event")
            description = event_data.get("description", "")
            event_type = event_data.get("event_type", "event")
            
            # Determine lore type based on event type
            if "faction" in event_type.lower() or "guild" in event_type.lower():
                lore_type = LoreType.FACTION
            elif "location" in event_type.lower() or "place" in event_type.lower():
                lore_type = LoreType.LOCATION
            elif "character" in event_type.lower() or "npc" in event_type.lower():
                lore_type = LoreType.CHARACTER
            elif "item" in event_type.lower() or "artifact" in event_type.lower():
                lore_type = LoreType.ITEM
            else:
                lore_type = LoreType.EVENT
            
            # Generate content
            content = f"{title}\n\n{description}"
            
            # Extract tags from event data
            tags = [event_type, "orchestration"]
            if "tags" in event_data:
                tags.extend(event_data["tags"])
            
            # Determine importance based on event priority
            importance = 1
            if event_data.get("priority") == "high":
                importance = 3
            elif event_data.get("priority") == "critical":
                importance = 5
            
            return self.create_lore_entry(
                title=title,
                lore_type=lore_type.value,
                content=content,
                tags=tags,
                discovered_by=event_data.get("triggered_by", "Unknown"),
                discovery_context=f"Orchestration event: {event_data.get('id', 'unknown')}",
                importance_level=importance
            )
        except Exception as e:
            logger.error(f"Error creating lore from orchestration event: {e}")
            return None
    
    def _create_lore_from_memory_entry(self, memory_data: Dict[str, Any]) -> Optional[str]:
        """Create lore entry from memory entry"""
        try:
            # Use the lore manager's auto-generation
            lore_entry = self.lore_manager.auto_generate_from_memory(memory_data)
            return lore_entry.lore_id if lore_entry else None
        except Exception as e:
            logger.error(f"Error creating lore from memory entry: {e}")
            return None
    
    def _create_lore_from_conflict_resolution(self, conflict_data: Dict[str, Any]) -> Optional[str]:
        """Create lore entry from conflict resolution"""
        try:
            title = f"Resolution: {conflict_data.get('title', 'Unknown Conflict')}"
            description = conflict_data.get("resolution_description", "")
            conflict_type = conflict_data.get("conflict_type", "interpersonal")
            
            # Determine lore type based on conflict type
            if conflict_type == "external":
                lore_type = LoreType.EVENT
            elif conflict_type == "internal":
                lore_type = LoreType.CHARACTER
            else:
                lore_type = LoreType.PLOT
            
            # Generate content
            content = f"{title}\n\n{description}"
            
            # Extract tags
            tags = [conflict_type, "conflict", "resolution"]
            
            return self.create_lore_entry(
                title=title,
                lore_type=lore_type.value,
                content=content,
                tags=tags,
                discovered_by=conflict_data.get("resolved_by", "Unknown"),
                discovery_context=f"Conflict resolution: {conflict_data.get('id', 'unknown')}",
                importance_level=3
            )
        except Exception as e:
            logger.error(f"Error creating lore from conflict resolution: {e}")
            return None
    
    def link_lore_to_item(self, lore_id: str, item_type: str, item_id: str) -> bool:
        """Link a lore entry to another item (character, location, etc.)"""
        try:
            entry = self.lore_manager.get_lore_entry_by_id(lore_id)
            if entry:
                entry.add_link(item_type, item_id)
                self.lore_manager.save_lore()
                return True
            return False
        except Exception as e:
            logger.error(f"Error linking lore to item: {e}")
            return False
    
    def get_lore_by_type(self, lore_type: str) -> List[Dict[str, Any]]:
        """Get all lore entries of a specific type"""
        try:
            lore_type_enum = LoreType(lore_type)
            entries = self.lore_manager.get_lore_by_type(lore_type_enum)
            
            entries_data = []
            for entry in entries:
                entries_data.append({
                    "id": entry.lore_id,
                    "title": entry.title,
                    "type": entry.lore_type.value,
                    "content": entry.content,
                    "tags": entry.tags,
                    "importance_level": entry.importance_level,
                    "is_secret": entry.is_secret,
                    "discovered_by": entry.discovered_by,
                    "discovery_context": entry.discovery_context,
                    "created_at": entry.created_at.isoformat(),
                    "updated_at": entry.updated_at.isoformat(),
                    "linked_items": entry.linked_items
                })
            
            return entries_data
        except Exception as e:
            logger.error(f"Error getting lore by type: {e}")
            return []
    
    def get_lore_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all lore entries with a specific tag"""
        try:
            entries = self.lore_manager.get_lore_by_tag(tag)
            
            entries_data = []
            for entry in entries:
                entries_data.append({
                    "id": entry.lore_id,
                    "title": entry.title,
                    "type": entry.lore_type.value,
                    "content": entry.content,
                    "tags": entry.tags,
                    "importance_level": entry.importance_level,
                    "is_secret": entry.is_secret,
                    "discovered_by": entry.discovered_by,
                    "discovery_context": entry.discovery_context,
                    "created_at": entry.created_at.isoformat(),
                    "updated_at": entry.updated_at.isoformat(),
                    "linked_items": entry.linked_items
                })
            
            return entries_data
        except Exception as e:
            logger.error(f"Error getting lore by tag: {e}")
            return []

    def initialize_campaign(self, character_data: Dict[str, Any], campaign_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Initialize a new campaign with the given character.
        
        Args:
            character_data: Character data dictionary
            campaign_name: Optional campaign name
            
        Returns:
            Campaign data dictionary or None if failed
        """
        try:
            if not campaign_name:
                campaign_name = f"Adventure of {character_data.get('name', 'the Hero')}"
            
            # Generate unique campaign ID
            import uuid
            campaign_id = f"campaign-{uuid.uuid4().hex[:8]}"
            
            # Store initial character data
            character_file = f"character_saves/{campaign_id}_character.json"
            with open(character_file, 'w') as f:
                json.dump(character_data, f, indent=2)
            
            # Create campaign data
            campaign_data = {
                "campaign_id": campaign_id,
                "name": campaign_name,
                "created_date": datetime.datetime.now().isoformat(),
                "active_character": character_data,
                "session_count": 0,
                "current_location": "Starting Area",
                "world_state": {}
            }
            
            # Save campaign data
            campaign_file = f"campaign_saves/{campaign_id}.json"
            with open(campaign_file, 'w') as f:
                json.dump(campaign_data, f, indent=2)
            
            # Initialize narrative bridge for this campaign
            self.campaign_id = campaign_id
            
            # Store complete character creation data in memory
            self.store_character_creation(character_data, campaign_id)
            
            # Store initial memory
            self.store_dnd_memory(
                f"You begin your adventure as {character_data.get('name', 'a hero')}, a {character_data.get('race', 'adventurer')} {character_data.get('class', 'hero')}.",
                memory_type="campaign_start",
                character_id=character_data.get('name', 'player')
            )
            
            # Create initial character arc
            self.create_character_arc(
                character_id=character_data.get('name', 'player'),
                name="The Hero's Journey",
                arc_type=ArcType.PERSONAL_GROWTH,
                description=f"The journey of {character_data.get('name', 'the hero')} as they discover their destiny.",
                emotional_themes=["courage", "growth", "discovery"]
            )
            
            # Create initial plot thread
            self.create_plot_thread(
                name="The Mysterious Artifacts",
                thread_type=ThreadType.MAIN_QUEST,
                description="Ancient artifacts have appeared in the world, drawing the attention of many.",
                priority=1,
                assigned_characters=[character_data.get('name', 'player')]
            )
            
            logger.info(f"Initialized campaign: {campaign_id}")
            return campaign_data
            
        except Exception as e:
            logger.error(f"Error initializing campaign: {e}")
            return None

    def generate_setting_introduction(self, character_data: Dict[str, Any], campaign_name: str) -> str:
        """
        Generate LLM-created setting introduction as per design guide.
        
        Args:
            character_data: Character data dictionary
            campaign_name: Campaign name
            
        Returns:
            Generated setting introduction text
        """
        try:
            # Use Ollama to generate a unique setting introduction
            from ollama_llm_service import chat_completion
            
            prompt = f"""
            You are a master storyteller creating an immersive opening scene for a DnD 5e solo adventure.
            
            Character: {character_data.get('name', 'the Hero')} - a {character_data.get('race', 'adventurer')} {character_data.get('class', 'hero')}
            Campaign: {campaign_name}
            
            Create a vivid, atmospheric opening scene that introduces the character to their adventure. 
            This should be 2-3 paragraphs that set the mood, establish the immediate environment, 
            and hint at the adventure to come. Make it feel like the opening of an epic fantasy novel.
            
            Focus on:
            - Sensory details (sights, sounds, smells)
            - Atmospheric mood
            - Immediate surroundings
            - A sense of mystery or adventure
            - The character's current situation
            
            Write in third person, present tense, as if narrating the scene to the player.
            """
            
            introduction = chat_completion([
                {"role": "system", "content": "You are a master DnD storyteller creating immersive opening scenes."},
                {"role": "user", "content": prompt}
            ], temperature=0.8, max_tokens=300)
            
            introduction = introduction.strip()
            
            # Store this as a memory
            self.store_dnd_memory(
                introduction,
                memory_type="setting_introduction",
                character_id=character_data.get('name', 'player')
            )
            
            return introduction
            
        except Exception as e:
            logger.error(f"Error generating setting introduction: {e}")
            # Fallback introduction
            return f"You find yourself in a mysterious land, ready to begin your adventure as {character_data.get('name', 'a hero')}..."

    def load_campaign(self, campaign_id: str) -> bool:
        """
        Load an existing campaign.
        
        Args:
            campaign_id: Campaign ID to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import os
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if not os.path.exists(campaign_file):
                logger.error(f"Campaign file not found: {campaign_file}")
                return False
            
            with open(campaign_file, 'r') as f:
                campaign_data = json.load(f)
            
            # Update the bridge's campaign ID
            self.campaign_id = campaign_id
            
            # Reinitialize components with the new campaign ID
            self.memory_system = VectorMemoryModule(campaign_id=campaign_id)
            self.campaign_orchestrator = DynamicCampaignOrchestrator(
                storage_path=f"orchestrator_{campaign_id}.jsonl"
            )
            self.lore_manager = LoreManager(campaign_id)
            
            logger.info(f"Loaded campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading campaign: {e}")
            return False

    def process_player_input(self, player_input: str, campaign_id: str) -> str:
        """
        Process player input and return DM response.
        
        Args:
            player_input: Player's action/input
            campaign_id: Campaign ID
            
        Returns:
            DM response text
        """
        try:
            # Store player action as memory
            self.store_dnd_memory(
                player_input,
                memory_type="player_action",
                character_id="player"
            )
            
            # Recall relevant memories
            relevant_memories = self.recall_related_memories(
                player_input,
                max_results=5,
                character_id="player"
            )
            
            # Generate DM response using AI
            if self.ai_dm_engine:
                context = {
                    "player_action": player_input,
                    "relevant_memories": relevant_memories,
                    "campaign_id": campaign_id,
                    "character_name": "the player"
                }
                
                response = self.ai_dm_engine.generate_response(context)
            else:
                # Fallback response
                response = self._generate_fallback_narration(
                    situation="player action",
                    player_actions=[player_input]
                )
            
            # Store DM response as memory
            self.store_dnd_memory(
                response,
                memory_type="dm_response",
                character_id="dm"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing player input: {e}")
            return "I'm sorry, but I'm having trouble processing that right now. Please try again."

    def save_campaign(self, campaign_id: str) -> bool:
        """
        Save current campaign state.
        
        Args:
            campaign_id: Campaign ID to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import os
            # Update campaign data
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if os.path.exists(campaign_file):
                with open(campaign_file, 'r') as f:
                    campaign_data = json.load(f)
                
                campaign_data["last_modified"] = datetime.datetime.now().isoformat()
                campaign_data["session_count"] = campaign_data.get("session_count", 0) + 1
                
                with open(campaign_file, 'w') as f:
                    json.dump(campaign_data, f, indent=2)
            
            logger.info(f"Saved campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving campaign: {e}")
            return False

    def get_campaign_data(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get campaign data.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign data dictionary or None if not found
        """
        try:
            import os
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if not os.path.exists(campaign_file):
                return None
            
            with open(campaign_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error getting campaign data: {e}")
            return None

# Convenience functions for common DnD operations
def create_dnd_bridge(campaign_id: str, api_key: Optional[str] = None) -> NarrativeBridge:
    """Create a new narrative bridge for DnD gameplay"""
    return NarrativeBridge(campaign_id, api_key)

def store_combat_memory(bridge: NarrativeBridge, combat_description: str, 
                       location: str, participants: List[str]) -> bool:
    """Store a combat-related memory"""
    memory = DnDMemoryEntry(
        content=combat_description,
        memory_type="episodic",
        location=location,
        combat_related=True,
        tags=["combat"] + participants
    )
    return bridge.store_dnd_memory(memory)

def store_quest_memory(bridge: NarrativeBridge, quest_description: str,
                      quest_name: str, location: str) -> bool:
    """Store a quest-related memory"""
    memory = DnDMemoryEntry(
        content=quest_description,
        memory_type="semantic",
        location=location,
        quest_related=quest_name,
        tags=["quest", quest_name]
    )
    return bridge.store_dnd_memory(memory) 

    def initialize_campaign(self, character_data: Dict[str, Any], campaign_name: str = None) -> Optional[Dict[str, Any]]:
        """Initialize a new campaign with the given character."""
        try:
            if not campaign_name:
                campaign_name = f"Adventure of {character_data.get('name', 'the Hero')}"
            
            import uuid
            campaign_id = f"campaign-{uuid.uuid4().hex[:8]}"
            
            character_file = f"character_saves/{campaign_id}_character.json"
            with open(character_file, 'w') as f:
                json.dump(character_data, f, indent=2)
            
            campaign_data = {
                "campaign_id": campaign_id,
                "name": campaign_name,
                "created_date": datetime.datetime.now().isoformat(),
                "active_character": character_data,
                "session_count": 0,
                "current_location": "Starting Area",
                "world_state": {}
            }
            
            campaign_file = f"campaign_saves/{campaign_id}.json"
            with open(campaign_file, 'w') as f:
                json.dump(campaign_data, f, indent=2)
            
            self.campaign_id = campaign_id
            
            self.store_dnd_memory(
                f"You begin your adventure as {character_data.get('name', 'a hero')}, a {character_data.get('race', 'adventurer')} {character_data.get('class', 'hero')}.",
                memory_type="campaign_start",
                character_id=character_data.get('name', 'player')
            )
            
            self.create_character_arc(
                character_id=character_data.get('name', 'player'),
                name="The Hero's Journey",
                arc_type=ArcType.PERSONAL_GROWTH,
                description=f"The journey of {character_data.get('name', 'the hero')} as they discover their destiny.",
                emotional_themes=["courage", "growth", "discovery"]
            )
            
            self.create_plot_thread(
                name="The Mysterious Artifacts",
                thread_type=ThreadType.MAIN_QUEST,
                description="Ancient artifacts have appeared in the world, drawing the attention of many.",
                priority=1,
                assigned_characters=[character_data.get('name', 'player')]
            )
            
            logger.info(f"Initialized campaign: {campaign_id}")
            return campaign_data
            
        except Exception as e:
            logger.error(f"Error initializing campaign: {e}")
            return None

    def generate_setting_introduction(self, character_data: Dict[str, Any], campaign_name: str) -> str:
        """Generate LLM-created setting introduction as per design guide."""
        try:
            from ollama_llm_service import chat_completion
            
            prompt = f"""
            You are a master storyteller creating an immersive opening scene for a DnD 5e solo adventure.
            
            Character: {character_data.get('name', 'the Hero')} - a {character_data.get('race', 'adventurer')} {character_data.get('class', 'hero')}
            Campaign: {campaign_name}
            
            Create a vivid, atmospheric opening scene that introduces the character to their adventure. 
            This should be 2-3 paragraphs that set the mood, establish the immediate environment, 
            and hint at the adventure to come. Make it feel like the opening of an epic fantasy novel.
            
            Focus on:
            - Sensory details (sights, sounds, smells)
            - Atmospheric mood
            - Immediate surroundings
            - A sense of mystery or adventure
            - The character's current situation
            
            Write in third person, present tense, as if narrating the scene to the player.
            """
            
            introduction = chat_completion([
                {"role": "system", "content": "You are a master DnD storyteller creating immersive opening scenes."},
                {"role": "user", "content": prompt}
            ], temperature=0.8, max_tokens=300)
            
            introduction = introduction.strip()
            
            self.store_dnd_memory(
                introduction,
                memory_type="setting_introduction",
                character_id=character_data.get('name', 'player')
            )
            
            return introduction
            
        except Exception as e:
            logger.error(f"Error generating setting introduction: {e}")
            return f"You find yourself in a mysterious land, ready to begin your adventure as {character_data.get('name', 'a hero')}..."

    def load_campaign(self, campaign_id: str) -> bool:
        """Load an existing campaign."""
        try:
            import os
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if not os.path.exists(campaign_file):
                logger.error(f"Campaign file not found: {campaign_file}")
                return False
            
            with open(campaign_file, 'r') as f:
                campaign_data = json.load(f)
            
            self.campaign_id = campaign_id
            
            self.memory_system = VectorMemoryModule(campaign_id=campaign_id)
            self.campaign_orchestrator = DynamicCampaignOrchestrator(
                storage_path=f"orchestrator_{campaign_id}.jsonl"
            )
            self.lore_manager = LoreManager(campaign_id)
            
            logger.info(f"Loaded campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading campaign: {e}")
            return False

    def process_player_input(self, player_input: str, campaign_id: str) -> str:
        """Process player input and return DM response."""
        try:
            self.store_dnd_memory(
                player_input,
                memory_type="player_action",
                character_id="player"
            )
            
            relevant_memories = self.recall_related_memories(
                player_input,
                max_results=5,
                character_id="player"
            )
            
            if self.ai_dm_engine:
                context = {
                    "player_action": player_input,
                    "relevant_memories": relevant_memories,
                    "campaign_id": campaign_id,
                    "character_name": "the player"
                }
                
                response = self.ai_dm_engine.generate_response(context)
            else:
                response = self._generate_fallback_narration(
                    situation="player action",
                    player_actions=[player_input]
                )
            
            self.store_dnd_memory(
                response,
                memory_type="dm_response",
                character_id="dm"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing player input: {e}")
            return "I'm sorry, but I'm having trouble processing that right now. Please try again."

    def save_campaign(self, campaign_id: str) -> bool:
        """Save current campaign state."""
        try:
            import os
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if os.path.exists(campaign_file):
                with open(campaign_file, 'r') as f:
                    campaign_data = json.load(f)
                
                campaign_data["last_modified"] = datetime.datetime.now().isoformat()
                campaign_data["session_count"] = campaign_data.get("session_count", 0) + 1
                
                with open(campaign_file, 'w') as f:
                    json.dump(campaign_data, f, indent=2)
            
            logger.info(f"Saved campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving campaign: {e}")
            return False

    def get_campaign_data(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign data."""
        try:
            import os
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if not os.path.exists(campaign_file):
                return None
            
            with open(campaign_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error getting campaign data: {e}")
            return None
