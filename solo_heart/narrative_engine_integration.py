#!/usr/bin/env python3
"""
SoloHeart Narrative Engine Integration
Bridges SoloHeart with The Narrative Engine for enhanced narrative continuity and memory.
"""

import os
import sys
import json
import logging
import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add the narrative engine to the path
narrative_engine_path = Path(__file__).parent.parent / "narrative_engine"
sys.path.insert(0, str(narrative_engine_path))

try:
    from core.narrative_engine import NarrativeEngine
    from memory.memory_manager import MemoryManager
    from llm_interface.ollama_provider import OllamaProvider
    from shared.types import MemoryEntry, MemoryType
    from context.contextual_drift_guard import ContextualDriftGuard
    from journaling.player_journal import PlayerJournal
except ImportError as e:
    logging.error(f"Failed to import Narrative Engine components: {e}")
    logging.error("Make sure the narrative_engine directory is properly set up")
    raise

logger = logging.getLogger(__name__)

class SoloHeartNarrativeEngine:
    """
    Integration layer between SoloHeart and The Narrative Engine.
    Provides SoloHeart-specific narrative functionality while leveraging
    the modular, domain-agnostic Narrative Engine core.
    """
    
    def __init__(self, campaign_id: str = None):
        self.campaign_id = campaign_id
        self.engine = None
        self.memory_manager = None
        self.llm_provider = None
        self.context_guard = None
        self.player_journal = None
        self.initialized = False
        
        # SoloHeart-specific configuration
        self.soloheart_config = {
            "domain": "soloheart",
            "narrative_style": "immersive_adventure",
            "memory_retention_days": 30,
            "context_window_size": 10,
            "temperature": 0.8,
            "max_tokens": 400
        }
        
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the Narrative Engine with SoloHeart-specific configuration."""
        try:
            # Initialize LLM provider (Ollama)
            self.llm_provider = OllamaProvider(
                model_name="llama3",
                base_url="http://localhost:11434",
                system_prompt=self._get_soloheart_system_prompt()
            )
            
            # Initialize memory manager
            memory_dir = Path("narrative_engine/memory_data")
            memory_dir.mkdir(exist_ok=True)
            
            self.memory_manager = MemoryManager(
                memory_file=str(memory_dir / f"soloheart_{self.campaign_id or 'default'}.json"),
                max_entries=1000,
                retention_days=self.soloheart_config["memory_retention_days"]
            )
            
            # Initialize contextual drift guard
            self.context_guard = ContextualDriftGuard(
                window_size=self.soloheart_config["context_window_size"]
            )
            
            # Initialize player journal
            journal_dir = Path("narrative_engine/journal_data")
            journal_dir.mkdir(exist_ok=True)
            
            self.player_journal = PlayerJournal(
                journal_file=str(journal_dir / f"soloheart_{self.campaign_id or 'default'}.jsonl")
            )
            
            # Initialize the core engine
            self.engine = NarrativeEngine(
                llm_provider=self.llm_provider,
                memory_manager=self.memory_manager,
                context_guard=self.context_guard,
                player_journal=self.player_journal
            )
            
            self.initialized = True
            logger.info("✅ SoloHeart Narrative Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize SoloHeart Narrative Engine: {e}")
            self.initialized = False
            raise
    
    def _get_soloheart_system_prompt(self) -> str:
        """Get SoloHeart-specific system prompt for the LLM."""
        return """You are a SoloHeart Guide, an AI companion for immersive solo narrative adventures. Your role is to:

1. **Create Immersive Experiences**: Craft vivid, atmospheric scenes that draw players into rich narrative worlds
2. **Maintain Narrative Continuity**: Remember and reference past events, character development, and story threads
3. **Adapt to Player Choices**: Respond dynamically to player decisions and actions, creating meaningful consequences
4. **Foster Character Development**: Help players explore their character's growth, relationships, and personal journey
5. **Balance Challenge and Support**: Provide appropriate challenges while ensuring players feel supported and engaged

**SoloHeart Style Guidelines:**
- Write in third person, present tense for scene descriptions
- Use rich sensory details (sight, sound, smell, touch, taste)
- Create atmospheric tension and emotional resonance
- Balance action with introspection and character moments
- Maintain consistent tone and pacing appropriate to the story
- Ask clarifying questions when player intentions are unclear
- Provide meaningful choices that impact the narrative direction

**Memory Integration:**
- Reference past events, character relationships, and story developments
- Build upon established lore and world-building elements
- Maintain consistency with previously established facts and events
- Use memory to create deeper, more meaningful narrative connections

Remember: You're not just telling a story - you're creating an immersive, personal journey that adapts and grows with the player's choices and character development."""

    def initialize_campaign(self, character_data: Dict[str, Any], campaign_name: str = None) -> Dict[str, Any]:
        """Initialize a new SoloHeart campaign with character data."""
        if not self.initialized:
            raise RuntimeError("Narrative Engine not initialized")
        
        try:
            # Create campaign metadata
            campaign_id = self.campaign_id or str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
            campaign_name = campaign_name or f"SoloHeart Campaign {campaign_id}"
            
            # Store character information in memory
            character_memory = MemoryEntry(
                memory_type=MemoryType.CHARACTER,
                content=f"Character: {character_data.get('name', 'Adventurer')} - {character_data.get('race', 'Human')} {character_data.get('class', 'Fighter')}",
                metadata={
                    "character_data": character_data,
                    "campaign_name": campaign_name,
                    "campaign_id": campaign_id
                },
                timestamp=datetime.datetime.now().isoformat()
            )
            
            self.memory_manager.add_memory(character_memory)
            
            # Generate immersive opening scene
            opening_scene = self._generate_opening_scene(character_data, campaign_name)
            
            # Store opening scene in memory
            scene_memory = MemoryEntry(
                memory_type=MemoryType.SCENE,
                content=f"Opening Scene: {opening_scene}",
                metadata={
                    "scene_type": "opening",
                    "campaign_id": campaign_id
                },
                timestamp=datetime.datetime.now().isoformat()
            )
            
            self.memory_manager.add_memory(scene_memory)
            
            # Create campaign data structure
            campaign_data = {
                "id": campaign_id,
                "name": campaign_name,
                "created_date": datetime.datetime.now().isoformat(),
                "last_modified": datetime.datetime.now().isoformat(),
                "active_character": character_data,
                "opening_scene": opening_scene,
                "session_count": 1,
                "narrative_engine_initialized": True
            }
            
            logger.info(f"✅ Initialized SoloHeart campaign: {campaign_id}")
            return campaign_data
            
        except Exception as e:
            logger.error(f"❌ Error initializing campaign: {e}")
            raise
    
    def _generate_opening_scene(self, character_data: Dict[str, Any], campaign_name: str) -> str:
        """Generate an immersive opening scene using the Narrative Engine."""
        try:
            character_name = character_data.get('name', 'Adventurer')
            character_race = character_data.get('race', 'Human')
            character_class = character_data.get('class', 'Fighter')
            
            prompt = f"""
            Create an immersive opening scene for a SoloHeart adventure featuring:
            
            Character: {character_name} - a {character_race} {character_class}
            Campaign: {campaign_name}
            
            The scene should:
            - Establish a vivid, atmospheric setting
            - Introduce the character's current situation
            - Create a sense of mystery, adventure, or personal journey
            - Use rich sensory details and emotional resonance
            - Set up potential story threads and character development opportunities
            
            Write in third person, present tense, as if narrating the scene to the player.
            Keep it to 2-3 paragraphs maximum.
            """
            
            response = self.engine.process_input(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating opening scene: {e}")
            return f"You find yourself in a mysterious land, ready to begin your adventure as {character_data.get('name', 'a hero')}..."
    
    def process_player_input(self, player_input: str, campaign_context: Dict[str, Any] = None) -> str:
        """Process player input and return an immersive SoloHeart response."""
        if not self.initialized:
            raise RuntimeError("Narrative Engine not initialized")
        
        try:
            # Store player input in memory
            input_memory = MemoryEntry(
                memory_type=MemoryType.ACTION,
                content=f"Player Action: {player_input}",
                metadata={
                    "input_type": "player_action",
                    "campaign_id": self.campaign_id
                },
                timestamp=datetime.datetime.now().isoformat()
            )
            
            self.memory_manager.add_memory(input_memory)
            
            # Build context-aware prompt
            context_prompt = self._build_context_prompt(player_input, campaign_context)
            
            # Process through the Narrative Engine
            response = self.engine.process_input(context_prompt)
            
            # Store response in memory
            response_memory = MemoryEntry(
                memory_type=MemoryType.RESPONSE,
                content=f"Guide Response: {response}",
                metadata={
                    "response_type": "guide_response",
                    "campaign_id": self.campaign_id
                },
                timestamp=datetime.datetime.now().isoformat()
            )
            
            self.memory_manager.add_memory(response_memory)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error processing player input: {e}")
            return "I'm sorry, but I'm having trouble processing that right now. Please try again."
    
    def _build_context_prompt(self, player_input: str, campaign_context: Dict[str, Any] = None) -> str:
        """Build a context-aware prompt for the Narrative Engine."""
        try:
            # Get relevant memories for context
            recent_memories = self.memory_manager.get_recent_memories(limit=5)
            character_memories = self.memory_manager.get_memories_by_type(MemoryType.CHARACTER, limit=3)
            
            context_parts = []
            
            # Add character context
            if character_memories:
                context_parts.append("Character Context:")
                for memory in character_memories:
                    context_parts.append(f"- {memory.content}")
            
            # Add recent story context
            if recent_memories:
                context_parts.append("\nRecent Story Context:")
                for memory in recent_memories:
                    if memory.memory_type in [MemoryType.SCENE, MemoryType.ACTION, MemoryType.RESPONSE]:
                        context_parts.append(f"- {memory.content}")
            
            # Add campaign context if provided
            if campaign_context:
                context_parts.append(f"\nCampaign Context: {campaign_context.get('name', 'Unknown Campaign')}")
            
            context_text = "\n".join(context_parts) if context_parts else "No specific context available."
            
            prompt = f"""
            Context:
            {context_text}
            
            Player Input: "{player_input}"
            
            As a SoloHeart Guide, respond to the player's input by:
            1. Describing what happens next in vivid, atmospheric detail
            2. Maintaining narrative continuity with past events
            3. Creating meaningful consequences for the player's actions
            4. Advancing the story in an engaging way
            5. Asking for clarification if the player's intentions are unclear
            
            Write in third person, present tense. Keep your response to 2-3 paragraphs maximum.
            Focus on immediate consequences and what the player experiences.
            """
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error building context prompt: {e}")
            return f'Respond to the player input: "{player_input}" as a SoloHeart Guide.'
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """Get a summary of the current campaign state."""
        if not self.initialized:
            return {"error": "Narrative Engine not initialized"}
        
        try:
            # Get character information
            character_memories = self.memory_manager.get_memories_by_type(MemoryType.CHARACTER, limit=1)
            character_info = character_memories[0].metadata.get('character_data', {}) if character_memories else {}
            
            # Get recent story events
            recent_events = self.memory_manager.get_recent_memories(limit=10)
            story_events = [memory.content for memory in recent_events if memory.memory_type in [MemoryType.SCENE, MemoryType.ACTION, MemoryType.RESPONSE]]
            
            # Get campaign statistics
            total_memories = len(self.memory_manager.get_all_memories())
            character_memories_count = len(self.memory_manager.get_memories_by_type(MemoryType.CHARACTER))
            scene_memories_count = len(self.memory_manager.get_memories_by_type(MemoryType.SCENE))
            
            return {
                "campaign_id": self.campaign_id,
                "character": character_info,
                "recent_events": story_events[-5:],  # Last 5 events
                "statistics": {
                    "total_memories": total_memories,
                    "character_memories": character_memories_count,
                    "scene_memories": scene_memories_count
                },
                "last_updated": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign summary: {e}")
            return {"error": str(e)}
    
    def save_campaign_state(self) -> bool:
        """Save the current campaign state."""
        if not self.initialized:
            return False
        
        try:
            # Memory manager auto-saves, but we can add campaign-specific saves here
            logger.info(f"✅ Campaign state saved for campaign: {self.campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving campaign state: {e}")
            return False
    
    def load_campaign_state(self, campaign_id: str) -> bool:
        """Load a campaign state."""
        try:
            # Update campaign ID
            self.campaign_id = campaign_id
            
            # Reinitialize with the new campaign ID
            self._initialize_engine()
            
            logger.info(f"✅ Loaded campaign state for: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading campaign state: {e}")
            return False 