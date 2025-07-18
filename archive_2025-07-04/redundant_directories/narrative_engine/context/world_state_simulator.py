"""
WorldStateSimulator - The Narrative Engine
=========================================

Enhanced world state tracking and simulation for Phase 3.
References: The Narrative Engine.docx, Narrative_Engine_Comparative_Report.docx

- Tracks location state, timeline, NPC relationships
- Manages event flags and branching consequences
- Campaign save/load with persistent state
- Supports narrative continuity and player agency
- Aligned with design manifesto: memory is sacred, story is cognitive
"""

from typing import Dict, Any, List, Optional, Set
import threading
import json
import os
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class LocationState:
    """Represents the state of a location in the world"""
    location_id: str
    name: str
    description: str
    current_occupants: List[str] = field(default_factory=list)  # Character/NPC IDs
    environmental_state: Dict[str, Any] = field(default_factory=dict)  # Weather, lighting, etc.
    discovered_by: Set[str] = field(default_factory=set)  # Characters who have discovered this location
    last_visited: Optional[str] = None
    visit_count: int = 0

@dataclass
class NPCRelationship:
    """Represents a relationship between two NPCs or NPC and player"""
    npc_id: str
    target_id: str  # Can be another NPC or player character
    relationship_type: str  # "friend", "enemy", "lover", "mentor", etc.
    strength: float  # -1.0 to 1.0 (negative = hostile, positive = friendly)
    trust_level: float  # 0.0 to 1.0
    shared_memories: List[str] = field(default_factory=list)  # Memory IDs they share
    last_interaction: Optional[str] = None

@dataclass
class EventFlag:
    """Represents a story event flag that can trigger consequences"""
    flag_id: str
    name: str
    description: str
    is_triggered: bool = False
    trigger_conditions: List[str] = field(default_factory=list)  # Conditions that must be met
    consequences: List[str] = field(default_factory=list)  # IDs of consequence events
    triggered_by: Optional[str] = None
    triggered_at: Optional[str] = None

@dataclass
class TimelineEvent:
    """Represents a significant event in the campaign timeline"""
    event_id: str
    name: str
    description: str
    timestamp: str
    event_type: str  # "quest", "combat", "social", "exploration", etc.
    location_id: Optional[str] = None
    involved_characters: List[str] = field(default_factory=list)
    consequences: List[str] = field(default_factory=list)  # IDs of consequence events
    is_resolved: bool = False

class WorldStateSimulator:
    """
    Enhanced world state tracking and simulation.
    
    Phase 3 Goals:
    - Location state management with environmental tracking
    - Timeline and event flag system for branching consequences
    - NPC relationship network with memory sharing
    - Campaign save/load with persistent state
    - Narrative continuity preservation
    """
    
    def __init__(self, save_directory: str = "campaign_saves"):
        self._state = {}
        self._lock = threading.Lock()
        self.save_directory = save_directory
        
        # Ensure save directory exists
        os.makedirs(save_directory, exist_ok=True)
        
        logger.info("WorldStateSimulator initialized with persistent save support")

    def update_location(self, campaign_id: str, character_id: str, new_location: str, 
                       location_data: Optional[Dict[str, Any]] = None):
        """
        Update a character's location with enhanced state tracking.
        
        Args:
            campaign_id: Campaign identifier
            character_id: Character/NPC identifier
            new_location: Location ID
            location_data: Optional location metadata (name, description, etc.)
        """
        with self._lock:
            campaign_state = self._state.setdefault(campaign_id, {})
            
            # Update character location
            locations = campaign_state.setdefault('locations', {})
            old_location = locations.get(character_id)
            locations[character_id] = new_location
            
            # Update location state if data provided
            if location_data:
                location_states = campaign_state.setdefault('location_states', {})
                if new_location not in location_states:
                    location_states[new_location] = LocationState(
                        location_id=new_location,
                        name=location_data.get('name', new_location),
                        description=location_data.get('description', ''),
                        current_occupants=[],
                        environmental_state=location_data.get('environmental_state', {}),
                        discovered_by=set(),
                        last_visited=datetime.now(timezone.utc).isoformat(),
                        visit_count=0
                    )
                
                # Update location state
                loc_state = location_states[new_location]
                if character_id not in loc_state.current_occupants:
                    loc_state.current_occupants.append(character_id)
                loc_state.discovered_by.add(character_id)
                loc_state.visit_count += 1
                loc_state.last_visited = datetime.now(timezone.utc).isoformat()
                
                # Remove from old location if exists
                if old_location and old_location in location_states:
                    old_loc_state = location_states[old_location]
                    if character_id in old_loc_state.current_occupants:
                        old_loc_state.current_occupants.remove(character_id)
            
            logger.info(f"Updated {character_id} location to {new_location} in campaign {campaign_id}")

    def update_npc_status(self, campaign_id: str, npc_id: str, status_dict: Dict[str, Any]):
        """Update an NPC's status with enhanced tracking."""
        with self._lock:
            campaign_state = self._state.setdefault(campaign_id, {})
            npc_statuses = campaign_state.setdefault('npc_status', {})
            
            # Preserve existing status and update
            current_status = npc_statuses.get(npc_id, {})
            current_status.update(status_dict)
            current_status['last_updated'] = datetime.now(timezone.utc).isoformat()
            npc_statuses[npc_id] = current_status
            
            logger.info(f"Updated NPC {npc_id} status in campaign {campaign_id}")

    def record_faction_change(self, campaign_id: str, faction_id: str, delta: int, 
                            reason: Optional[str] = None):
        """Record a change in faction reputation with reason tracking."""
        with self._lock:
            campaign_state = self._state.setdefault(campaign_id, {})
            factions = campaign_state.setdefault('factions', {})
            
            if faction_id not in factions:
                factions[faction_id] = {
                    'reputation': 0,
                    'history': []
                }
            
            old_reputation = factions[faction_id]['reputation']
            factions[faction_id]['reputation'] += delta
            factions[faction_id]['history'].append({
                'change': delta,
                'new_reputation': factions[faction_id]['reputation'],
                'reason': reason,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"Faction {faction_id} reputation changed by {delta} in campaign {campaign_id}")

    def add_npc_relationship(self, campaign_id: str, npc_id: str, target_id: str, 
                           relationship_type: str, strength: float, trust_level: float):
        """Add or update an NPC relationship."""
        with self._lock:
            campaign_state = self._state.setdefault(campaign_id, {})
            relationships = campaign_state.setdefault('npc_relationships', {})
            
            relationship_key = f"{npc_id}_{target_id}"
            relationships[relationship_key] = NPCRelationship(
                npc_id=npc_id,
                target_id=target_id,
                relationship_type=relationship_type,
                strength=strength,
                trust_level=trust_level,
                shared_memories=[],
                last_interaction=datetime.now(timezone.utc).isoformat()
            )
            
            logger.info(f"Added relationship between {npc_id} and {target_id} in campaign {campaign_id}")

    def add_event_flag(self, campaign_id: str, flag_id: str, name: str, description: str,
                      trigger_conditions: List[str] = None, consequences: List[str] = None):
        """Add an event flag for story progression tracking."""
        with self._lock:
            campaign_state = self._state.setdefault(campaign_id, {})
            event_flags = campaign_state.setdefault('event_flags', {})
            
            event_flags[flag_id] = EventFlag(
                flag_id=flag_id,
                name=name,
                description=description,
                trigger_conditions=trigger_conditions or [],
                consequences=consequences or []
            )
            
            logger.info(f"Added event flag {flag_id} in campaign {campaign_id}")

    def trigger_event_flag(self, campaign_id: str, flag_id: str, triggered_by: str):
        """Trigger an event flag and record the consequence."""
        with self._lock:
            campaign_state = self._state.get(campaign_id, {})
            event_flags = campaign_state.get('event_flags', {})
            
            if flag_id in event_flags:
                flag = event_flags[flag_id]
                flag.is_triggered = True
                flag.triggered_by = triggered_by
                flag.triggered_at = datetime.now(timezone.utc).isoformat()
                
                # Add to timeline
                timeline = campaign_state.setdefault('timeline', {})
                event_id = f"flag_trigger_{flag_id}_{datetime.now(timezone.utc).timestamp()}"
                timeline[event_id] = TimelineEvent(
                    event_id=event_id,
                    name=f"Flag Triggered: {flag.name}",
                    description=f"Event flag '{flag.name}' was triggered by {triggered_by}",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    event_type="flag_trigger",
                    consequences=flag.consequences
                )
                
                logger.info(f"Triggered event flag {flag_id} in campaign {campaign_id}")

    def add_timeline_event(self, campaign_id: str, event_id: str, name: str, description: str,
                          location_id: Optional[str] = None, involved_characters: List[str] = None,
                          event_type: str = "general"):
        """Add a significant event to the campaign timeline."""
        with self._lock:
            campaign_state = self._state.setdefault(campaign_id, {})
            timeline = campaign_state.setdefault('timeline', {})
            
            timeline[event_id] = TimelineEvent(
                event_id=event_id,
                name=name,
                description=description,
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type=event_type,
                location_id=location_id,
                involved_characters=involved_characters or [],
                consequences=[]
            )
            
            logger.info(f"Added timeline event {event_id} in campaign {campaign_id}")

    def get_current_state(self, campaign_id: str) -> Dict[str, Any]:
        """Return the current world state for a campaign as a JSON-compatible dict."""
        with self._lock:
            campaign_state = self._state.get(campaign_id, {}).copy()
            
            # Convert dataclasses to dicts for JSON compatibility
            if 'location_states' in campaign_state:
                campaign_state['location_states'] = {
                    k: asdict(v) for k, v in campaign_state['location_states'].items()
                }
                # Convert sets to lists for JSON serialization
                for loc_state in campaign_state['location_states'].values():
                    loc_state['discovered_by'] = list(loc_state['discovered_by'])
            
            if 'npc_relationships' in campaign_state:
                campaign_state['npc_relationships'] = {
                    k: asdict(v) for k, v in campaign_state['npc_relationships'].items()
                }
            
            if 'event_flags' in campaign_state:
                campaign_state['event_flags'] = {
                    k: asdict(v) for k, v in campaign_state['event_flags'].items()
                }
            
            if 'timeline' in campaign_state:
                campaign_state['timeline'] = {
                    k: asdict(v) for k, v in campaign_state['timeline'].items()
                }
            
            return campaign_state

    def save_campaign_state(self, campaign_id: str) -> bool:
        """Save campaign state to persistent storage."""
        try:
            state_data = self.get_current_state(campaign_id)
            state_data['save_timestamp'] = datetime.now(timezone.utc).isoformat()
            state_data['campaign_id'] = campaign_id
            
            filename = os.path.join(self.save_directory, f"{campaign_id}_world_state.json")
            with open(filename, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            logger.info(f"Saved campaign state for {campaign_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save campaign state for {campaign_id}: {e}")
            return False

    def load_campaign_state(self, campaign_id: str) -> bool:
        """Load campaign state from persistent storage."""
        try:
            filename = os.path.join(self.save_directory, f"{campaign_id}_world_state.json")
            if not os.path.exists(filename):
                logger.warning(f"No saved state found for campaign {campaign_id}")
                return False
            
            with open(filename, 'r') as f:
                state_data = json.load(f)
            
            with self._lock:
                # Convert back to proper data structures
                if 'location_states' in state_data:
                    for loc_id, loc_data in state_data['location_states'].items():
                        loc_data['discovered_by'] = set(loc_data['discovered_by'])
                        state_data['location_states'][loc_id] = LocationState(**loc_data)
                
                if 'npc_relationships' in state_data:
                    for rel_key, rel_data in state_data['npc_relationships'].items():
                        state_data['npc_relationships'][rel_key] = NPCRelationship(**rel_data)
                
                if 'event_flags' in state_data:
                    for flag_id, flag_data in state_data['event_flags'].items():
                        state_data['event_flags'][flag_id] = EventFlag(**flag_data)
                
                if 'timeline' in state_data:
                    for event_id, event_data in state_data['timeline'].items():
                        state_data['timeline'][event_id] = TimelineEvent(**event_data)
                
                self._state[campaign_id] = state_data
            
            logger.info(f"Loaded campaign state for {campaign_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to load campaign state for {campaign_id}: {e}")
            return False

    def get_location_state(self, campaign_id: str, location_id: str) -> Optional[LocationState]:
        """Get the current state of a specific location."""
        with self._lock:
            campaign_state = self._state.get(campaign_id, {})
            location_states = campaign_state.get('location_states', {})
            return location_states.get(location_id)

    def get_npc_relationships(self, campaign_id: str, npc_id: str) -> List[NPCRelationship]:
        """Get all relationships for a specific NPC."""
        with self._lock:
            campaign_state = self._state.get(campaign_id, {})
            relationships = campaign_state.get('npc_relationships', {})
            
            npc_relationships = []
            for rel_key, relationship in relationships.items():
                if relationship.npc_id == npc_id or relationship.target_id == npc_id:
                    npc_relationships.append(relationship)
            
            return npc_relationships

    def get_active_event_flags(self, campaign_id: str) -> List[EventFlag]:
        """Get all active (non-triggered) event flags."""
        with self._lock:
            campaign_state = self._state.get(campaign_id, {})
            event_flags = campaign_state.get('event_flags', {})
            
            return [flag for flag in event_flags.values() if not flag.is_triggered]

    def get_recent_timeline_events(self, campaign_id: str, limit: int = 10) -> List[TimelineEvent]:
        """Get recent timeline events for a campaign."""
        with self._lock:
            campaign_state = self._state.get(campaign_id, {})
            timeline_events = campaign_state.get('timeline_events', [])
            
            # Sort by timestamp and return recent events
            sorted_events = sorted(timeline_events, key=lambda x: x.timestamp, reverse=True)
            return sorted_events[:limit]

    def export_state(self) -> Dict[str, Any]:
        """Export the entire world state for save/load functionality."""
        with self._lock:
            return {
                'state': self._state,
                'save_directory': self.save_directory
            }

    def import_state(self, data: Dict[str, Any]):
        """Import world state from save/load data."""
        with self._lock:
            self._state = data.get('state', {})
            self.save_directory = data.get('save_directory', 'campaign_saves')
            
            # Ensure save directory exists
            os.makedirs(self.save_directory, exist_ok=True)
            
            logger.info("World state imported successfully")

# Global instance for easy access
world_state_simulator = WorldStateSimulator() 