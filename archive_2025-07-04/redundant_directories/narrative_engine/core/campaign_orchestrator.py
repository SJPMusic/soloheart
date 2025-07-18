"""
Dynamic Campaign Orchestrator

Drives game progression based on memory, emotion, character arcs, and emerging plot threads.
Monitors active elements and dynamically suggests new quests, encounters, or developments.
"""

import json
import datetime
import logging
import random
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

from ..memory.emotional_memory import EmotionType
from ..narrative_structure.plot_threads import ThreadStatus

logger = logging.getLogger(__name__)


class OrchestrationEventType(Enum):
    """Types of orchestration events."""
    QUEST_SUGGESTION = "quest_suggestion"
    ENCOUNTER_TRIGGER = "encounter_trigger"
    CHARACTER_DEVELOPMENT = "character_development"
    PLOT_DEVELOPMENT = "plot_development"
    WORLD_EVENT = "world_event"
    EMOTIONAL_MOMENT = "emotional_moment"
    RELATIONSHIP_DEVELOPMENT = "relationship_development"
    MYSTERY_REVELATION = "mystery_revelation"
    CONFLICT_EMERGENCE = "conflict_emergence"  # New conflict type


class OrchestrationPriority(Enum):
    """Priority levels for orchestration events."""
    CRITICAL = "critical"      # Must happen soon
    HIGH = "high"             # Should happen soon
    MEDIUM = "medium"         # Can happen when convenient
    LOW = "low"              # Optional/background
    BACKGROUND = "background"  # Ambient/atmospheric


class ConflictType(Enum):
    """Types of emergent conflicts."""
    INTERNAL = "internal"           # Character's internal struggle
    INTERPERSONAL = "interpersonal" # Between characters
    EXTERNAL_THREAT = "external"    # External challenge/threat


class ConflictUrgency(Enum):
    """Urgency levels for conflicts."""
    CRITICAL = "critical"  # Immediate attention required
    HIGH = "high"         # Should be addressed soon
    MEDIUM = "medium"     # Can be addressed when convenient
    LOW = "low"          # Optional/background tension


@dataclass
class OrchestrationEvent:
    """Represents an orchestration event or suggestion."""
    event_id: str
    event_type: OrchestrationEventType
    priority: OrchestrationPriority
    title: str
    description: str
    suggested_actions: List[str]
    emotional_context: List[str]
    related_arcs: List[str] = field(default_factory=list)
    related_threads: List[str] = field(default_factory=list)
    target_characters: List[str] = field(default_factory=list)
    location_hint: Optional[str] = None
    timing_hint: Optional[str] = None
    prerequisites: List[str] = field(default_factory=list)
    consequences: List[str] = field(default_factory=list)
    created_timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    executed_timestamp: Optional[datetime.datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    # New fields for real-time feedback
    urgency_level: str = "normal"  # low, normal, high, critical
    involved_characters: List[str] = field(default_factory=list)
    memory_tie_ins: List[str] = field(default_factory=list)
    arc_impact: Dict[str, str] = field(default_factory=dict)  # arc_id -> impact_description
    thread_impact: Dict[str, str] = field(default_factory=dict)  # thread_id -> impact_description
    suggested_responses: List[Dict[str, Any]] = field(default_factory=list)  # response options with metadata
    event_icon: str = "⚔️"  # Default icon for UI display
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['priority'] = self.priority.value
        data['created_timestamp'] = self.created_timestamp.isoformat()
        if self.executed_timestamp:
            data['executed_timestamp'] = self.executed_timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrchestrationEvent':
        """Create from dictionary."""
        data['event_type'] = OrchestrationEventType(data['event_type'])
        data['priority'] = OrchestrationPriority(data['priority'])
        data['created_timestamp'] = datetime.datetime.fromisoformat(data['created_timestamp'])
        if data.get('executed_timestamp'):
            data['executed_timestamp'] = datetime.datetime.fromisoformat(data['executed_timestamp'])
        return cls(**data)


@dataclass
class CampaignState:
    """Current state of the campaign for orchestration decisions."""
    campaign_id: str
    active_arcs: List[Dict[str, Any]]
    open_threads: List[Dict[str, Any]]
    recent_memories: List[Dict[str, Any]]
    emotional_context: Dict[str, float]
    character_locations: Dict[str, str]
    world_events: List[Dict[str, Any]]
    session_count: int
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ConflictNode:
    """Represents an emergent conflict in the narrative."""
    conflict_id: str
    conflict_type: ConflictType
    urgency: ConflictUrgency
    title: str
    description: str
    characters_involved: List[str] = field(default_factory=list)
    related_arcs: List[str] = field(default_factory=list)
    related_threads: List[str] = field(default_factory=list)
    suggested_resolutions: List[Dict[str, Any]] = field(default_factory=list)
    impact_preview: Dict[str, Any] = field(default_factory=dict)
    emotional_context: List[str] = field(default_factory=list)
    value_contradictions: List[str] = field(default_factory=list)
    created_timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    resolved_timestamp: Optional[datetime.datetime] = None
    resolution_chosen: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    conflict_icon: str = "⚔️"  # Default icon for UI display
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['conflict_type'] = self.conflict_type.value
        data['urgency'] = self.urgency.value
        data['created_timestamp'] = self.created_timestamp.isoformat()
        if self.resolved_timestamp:
            data['resolved_timestamp'] = self.resolved_timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConflictNode':
        """Create from dictionary."""
        data['conflict_type'] = ConflictType(data['conflict_type'])
        data['urgency'] = ConflictUrgency(data['urgency'])
        data['created_timestamp'] = datetime.datetime.fromisoformat(data['created_timestamp'])
        if data.get('resolved_timestamp'):
            data['resolved_timestamp'] = datetime.datetime.fromisoformat(data['resolved_timestamp'])
        return cls(**data)


class DynamicCampaignOrchestrator:
    """
    Dynamic Campaign Orchestrator that drives game progression.
    
    Monitors active character arcs, unresolved plot threads, emotional context,
    and journal entries to dynamically suggest new quests, encounters, and developments.
    """
    
    def __init__(self, storage_path: str = "orchestrator_events.jsonl"):
        """
        Initialize the campaign orchestrator.
        
        Args:
            storage_path: Path to the JSONL file for persistent storage
        """
        self.storage_path = storage_path
        self.events: Dict[str, OrchestrationEvent] = {}
        self.decision_history: List[Dict[str, Any]] = []
        self.conflicts: Dict[str, ConflictNode] = {}
        self._load_events()
        
        # Orchestration weights and thresholds
        self.weights = {
            'arc_completion': 0.3,
            'thread_resolution': 0.25,
            'emotional_intensity': 0.2,
            'memory_recency': 0.15,
            'character_development': 0.1
        }
        
        # Event generation templates
        self.event_templates = self._load_event_templates()
        
        # Conflict generation templates
        self.conflict_templates = self._load_conflict_templates()
        
        logger.info("Dynamic Campaign Orchestrator initialized")
    
    def _load_events(self):
        """Load existing orchestration events from storage."""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        event = OrchestrationEvent.from_dict(data)
                        self.events[event.event_id] = event
            logger.info(f"Loaded {len(self.events)} orchestration events")
        except FileNotFoundError:
            logger.info("No existing orchestration events found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading orchestration events: {e}")
    
    def _save_event(self, event: OrchestrationEvent):
        """Save a single event to persistent storage."""
        try:
            with open(self.storage_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error saving orchestration event: {e}")
            raise
    
    def _load_event_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load event generation templates."""
        return {
            'quest_suggestion': [
                {
                    'title_template': "The {location} Mystery",
                    'description_template': "Rumors speak of strange happenings in {location}. {character} might find clues about {related_arc}.",
                    'suggested_actions': ["Investigate the rumors", "Ask locals about recent events", "Search for physical evidence"],
                    'emotional_context': ["curiosity", "determination", "caution"]
                },
                {
                    'title_template': "A Call for Help",
                    'description_template': "A desperate plea reaches {character} about {related_thread}. Time may be running out.",
                    'suggested_actions': ["Respond to the plea", "Gather information", "Prepare for the journey"],
                    'emotional_context': ["urgency", "compassion", "responsibility"]
                }
            ],
            'encounter_trigger': [
                {
                    'title_template': "Unexpected Meeting",
                    'description_template': "While traveling to {location}, {character} encounters someone connected to {related_arc}.",
                    'suggested_actions': ["Engage in conversation", "Observe their behavior", "Decide how to proceed"],
                    'emotional_context': ["surprise", "caution", "opportunity"]
                }
            ],
            'character_development': [
                {
                    'title_template': "A Moment of Reflection",
                    'description_template': "Recent events have caused {character} to reconsider their path regarding {related_arc}.",
                    'suggested_actions': ["Meditate on the situation", "Seek counsel", "Make a decision"],
                    'emotional_context': ["contemplation", "uncertainty", "growth"]
                }
            ],
            'plot_development': [
                {
                    'title_template': "New Information Emerges",
                    'description_template': "A piece of information about {related_thread} comes to light, changing everything.",
                    'suggested_actions': ["Analyze the new information", "Update allies", "Adjust plans"],
                    'emotional_context': ["revelation", "urgency", "adaptation"]
                }
            ]
        }
    
    def analyze_campaign_state(
        self,
        narrative_bridge,
        campaign_id: str
    ) -> CampaignState:
        """
        Analyze the current state of the campaign.
        
        Args:
            narrative_bridge: NarrativeBridge instance
            campaign_id: ID of the campaign
            
        Returns:
            CampaignState object with current analysis
        """
        try:
            # Get active character arcs
            from narrative_engine.narrative_structure.character_arcs import ArcStatus
            active_arcs = narrative_bridge.get_character_arcs(status=ArcStatus.ACTIVE)
            
            # Get open plot threads
            from narrative_engine.narrative_structure.plot_threads import ThreadStatus
            open_threads = narrative_bridge.get_plot_threads(status=ThreadStatus.OPEN)
            
            # Get recent memories (last 10)
            recent_memories = narrative_bridge.recall_related_memories("", max_results=10)
            
            # Analyze emotional context from recent memories
            emotional_context = self._analyze_emotional_context(recent_memories)
            
            # Get character locations (simplified)
            character_locations = {"player": "unknown"}  # Would be populated from world state
            
            # Get world events (simplified)
            world_events = []  # Would be populated from world state
            
            # Get session count
            session_count = 0  # Would be populated from session logger
            
            state = CampaignState(
                campaign_id=campaign_id,
                active_arcs=active_arcs,
                open_threads=open_threads,
                recent_memories=recent_memories,
                emotional_context=emotional_context,
                character_locations=character_locations,
                world_events=world_events,
                session_count=session_count
            )
            
            logger.info(f"Analyzed campaign state for {campaign_id}")
            return state
            
        except Exception as e:
            logger.error(f"Error analyzing campaign state: {e}")
            # Return minimal state
            return CampaignState(
                campaign_id=campaign_id,
                active_arcs=[],
                open_threads=[],
                recent_memories=[],
                emotional_context={},
                character_locations={},
                world_events=[],
                session_count=0
            )
    
    def _analyze_emotional_context(self, memories: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze emotional context from recent memories."""
        emotional_weights = {}
        
        for memory in memories:
            if 'emotional_context' in memory and memory['emotional_context']:
                for emotion in memory['emotional_context']:
                    if emotion in emotional_weights:
                        emotional_weights[emotion] += 0.1
                    else:
                        emotional_weights[emotion] = 0.1
        
        return emotional_weights
    
    def generate_orchestration_events(
        self,
        campaign_state: CampaignState,
        max_events: int = 3
    ) -> List[OrchestrationEvent]:
        """
        Generate orchestration events based on campaign state.
        
        Args:
            campaign_state: Current campaign state
            max_events: Maximum number of events to generate
            
        Returns:
            List of generated orchestration events
        """
        events = []
        
        try:
            # Analyze priorities based on campaign state
            priorities = self._calculate_priorities(campaign_state)
            
            # Generate events based on priorities
            for priority_info in priorities[:max_events]:
                event = self._generate_event_from_priority(priority_info, campaign_state)
                if event:
                    events.append(event)
                    self.events[event.event_id] = event
                    self._save_event(event)
            
            logger.info(f"Generated {len(events)} orchestration events")
            return events
            
        except Exception as e:
            logger.error(f"Error generating orchestration events: {e}")
            return []
    
    def _calculate_priorities(self, campaign_state: CampaignState) -> List[Dict[str, Any]]:
        """Calculate orchestration priorities based on campaign state."""
        priorities = []
        
        # Arc completion priorities
        for arc in campaign_state.active_arcs:
            completion = arc.get('completion_percentage', 0.0)
            if completion < 0.3:
                priorities.append({
                    'type': 'arc_completion',
                    'priority': OrchestrationPriority.HIGH,
                    'target': arc['arc_id'],
                    'weight': self.weights['arc_completion'] * (1.0 - completion),
                    'data': arc
                })
            elif completion > 0.7:
                priorities.append({
                    'type': 'arc_completion',
                    'priority': OrchestrationPriority.CRITICAL,
                    'target': arc['arc_id'],
                    'weight': self.weights['arc_completion'] * completion,
                    'data': arc
                })
        
        # Thread resolution priorities
        for thread in campaign_state.open_threads:
            priority_level = thread.get('priority', 1)
            if priority_level >= 8:
                priorities.append({
                    'type': 'thread_resolution',
                    'priority': OrchestrationPriority.CRITICAL,
                    'target': thread['thread_id'],
                    'weight': self.weights['thread_resolution'] * (priority_level / 10.0),
                    'data': thread
                })
            elif priority_level >= 5:
                priorities.append({
                    'type': 'thread_resolution',
                    'priority': OrchestrationPriority.HIGH,
                    'target': thread['thread_id'],
                    'weight': self.weights['thread_resolution'] * (priority_level / 10.0),
                    'data': thread
                })
        
        # Emotional context priorities
        for emotion, intensity in campaign_state.emotional_context.items():
            if intensity > 0.5:
                priorities.append({
                    'type': 'emotional_moment',
                    'priority': OrchestrationPriority.MEDIUM,
                    'target': emotion,
                    'weight': self.weights['emotional_intensity'] * intensity,
                    'data': {'emotion': emotion, 'intensity': intensity}
                })
        
        # Sort by weight (highest first)
        priorities.sort(key=lambda x: x['weight'], reverse=True)
        return priorities
    
    def _generate_event_from_priority(
        self,
        priority_info: Dict[str, Any],
        campaign_state: CampaignState
    ) -> Optional[OrchestrationEvent]:
        """Generate a specific event from priority information."""
        try:
            event_type = priority_info['type']
            priority = priority_info['priority']
            target = priority_info['target']
            data = priority_info['data']
            
            # Generate event ID
            event_id = f"orchestrator_{event_type}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            # Get template based on event type
            templates = self.event_templates.get(f"{event_type}_suggestion", [])
            if not templates:
                templates = self.event_templates.get('quest_suggestion', [])
            
            if not templates:
                return None
            
            template = random.choice(templates)
            
            # Fill template with campaign data
            title = self._fill_template(template['title_template'], data, campaign_state)
            description = self._fill_template(template['description_template'], data, campaign_state)
            
            event = OrchestrationEvent(
                event_id=event_id,
                event_type=self._map_priority_to_event_type(event_type),
                priority=priority,
                title=title,
                description=description,
                suggested_actions=template['suggested_actions'],
                emotional_context=template['emotional_context'],
                related_arcs=[arc['arc_id'] for arc in campaign_state.active_arcs[:2]],
                related_threads=[thread['thread_id'] for thread in campaign_state.open_threads[:2]],
                target_characters=["player"],  # Default target
                location_hint=self._suggest_location(data, campaign_state),
                timing_hint=self._suggest_timing(priority),
                prerequisites=[],
                consequences=self._suggest_consequences(event_type, data),
                metadata={'priority_weight': priority_info['weight']},
                # New fields for real-time feedback
                urgency_level="normal",  # Default urgency level
                involved_characters=["player"],  # Default involved characters
                memory_tie_ins=[],  # Default memory tie-ins
                arc_impact={},  # Default arc impact
                thread_impact={},  # Default thread impact
                suggested_responses=[],  # Default suggested responses
                event_icon="⚔️"  # Default event icon
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Error generating event from priority: {e}")
            return None
    
    def _fill_template(self, template: str, data: Dict[str, Any], campaign_state: CampaignState) -> str:
        """Fill a template string with campaign data."""
        try:
            # Simple template filling
            filled = template
            
            # Replace common placeholders
            if '{location}' in filled:
                filled = filled.replace('{location}', data.get('location', 'the area'))
            
            if '{character}' in filled:
                filled = filled.replace('{character}', 'the player')
            
            if '{related_arc}' in filled:
                arc_name = data.get('name', 'their journey')
                filled = filled.replace('{related_arc}', arc_name)
            
            if '{related_thread}' in filled:
                thread_name = data.get('name', 'the situation')
                filled = filled.replace('{related_thread}', thread_name)
            
            return filled
            
        except Exception as e:
            logger.error(f"Error filling template: {e}")
            return template
    
    def _map_priority_to_event_type(self, priority_type: str) -> OrchestrationEventType:
        """Map priority type to event type."""
        mapping = {
            'arc_completion': OrchestrationEventType.CHARACTER_DEVELOPMENT,
            'thread_resolution': OrchestrationEventType.PLOT_DEVELOPMENT,
            'emotional_moment': OrchestrationEventType.EMOTIONAL_MOMENT,
            'quest_suggestion': OrchestrationEventType.QUEST_SUGGESTION,
            'encounter_trigger': OrchestrationEventType.ENCOUNTER_TRIGGER
        }
        return mapping.get(priority_type, OrchestrationEventType.WORLD_EVENT)
    
    def _suggest_location(self, data: Dict[str, Any], campaign_state: CampaignState) -> str:
        """Suggest a location for the event."""
        # Simple location suggestion based on data
        if 'location' in data:
            return data['location']
        
        # Default locations
        locations = ["the town square", "the ancient ruins", "the forest path", "the tavern", "the marketplace"]
        return random.choice(locations)
    
    def _suggest_timing(self, priority: OrchestrationPriority) -> str:
        """Suggest timing for the event."""
        timing_suggestions = {
            OrchestrationPriority.CRITICAL: "immediately",
            OrchestrationPriority.HIGH: "soon",
            OrchestrationPriority.MEDIUM: "when convenient",
            OrchestrationPriority.LOW: "when time permits",
            OrchestrationPriority.BACKGROUND: "in the background"
        }
        return timing_suggestions.get(priority, "when convenient")
    
    def _suggest_consequences(self, event_type: str, data: Dict[str, Any]) -> List[str]:
        """Suggest possible consequences of the event."""
        consequences = []
        
        if event_type == 'arc_completion':
            consequences.extend([
                "Character growth and development",
                "New abilities or insights",
                "Changed relationships with others"
            ])
        elif event_type == 'thread_resolution':
            consequences.extend([
                "Plot advancement",
                "New mysteries revealed",
                "World state changes"
            ])
        elif event_type == 'emotional_moment':
            consequences.extend([
                "Emotional impact on character",
                "Potential relationship changes",
                "Memory formation"
            ])
        
        return consequences
    
    def get_pending_events(
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
        pending = []
        
        for event in self.events.values():
            if event.executed_timestamp is None:  # Not yet executed
                if priority and event.priority != priority:
                    continue
                if event_type and event.event_type != event_type:
                    continue
                pending.append(event)
        
        # Sort by priority (critical first) and creation time
        pending.sort(key=lambda x: (x.priority.value, x.created_timestamp), reverse=True)
        
        return pending
    
    def execute_event(
        self,
        event_id: str,
        narrative_bridge,
        execution_notes: Optional[str] = None
    ) -> bool:
        """
        Mark an event as executed and store the decision.
        
        Args:
            event_id: ID of the event to execute
            narrative_bridge: NarrativeBridge instance
            execution_notes: Optional notes about execution
            
        Returns:
            True if executed successfully
        """
        try:
            if event_id not in self.events:
                logger.warning(f"Event not found: {event_id}")
                return False
            
            event = self.events[event_id]
            event.executed_timestamp = datetime.datetime.now()
            
            # Store decision in memory
            decision_memory = {
                'content': f"Orchestrator executed: {event.title}",
                'memory_type': 'orchestration_decision',
                'metadata': {
                    'event_id': event_id,
                    'event_type': event.event_type.value,
                    'priority': event.priority.value,
                    'execution_notes': execution_notes,
                    'related_arcs': event.related_arcs,
                    'related_threads': event.related_threads
                },
                'tags': ['orchestrator', 'decision', event.event_type.value],
                'emotional_context': event.emotional_context
            }
            
            narrative_bridge.store_dnd_memory(**decision_memory)
            
            # Update decision history
            self.decision_history.append({
                'event_id': event_id,
                'execution_time': event.executed_timestamp.isoformat(),
                'notes': execution_notes
            })
            
            # Rebuild storage
            self._rebuild_storage()
            
            logger.info(f"Executed orchestration event: {event.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing event: {e}")
            return False
    
    def _rebuild_storage(self):
        """Rebuild the storage file."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                for event in self.events.values():
                    f.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error rebuilding storage: {e}")
            raise
    
    def get_orchestration_summary(self) -> Dict[str, Any]:
        """Get a summary of orchestration activity."""
        pending_events = self.get_pending_events()
        executed_events = [e for e in self.events.values() if e.executed_timestamp]
        
        return {
            'total_events': len(self.events),
            'pending_events': len(pending_events),
            'executed_events': len(executed_events),
            'recent_events': len([e for e in pending_events if 
                                (datetime.datetime.now() - e.created_timestamp).days < 1]),
            'priority_breakdown': self._get_priority_breakdown(),
            'event_type_breakdown': self._get_event_type_breakdown()
        }
    
    def _get_priority_breakdown(self) -> Dict[str, int]:
        """Get breakdown of events by priority."""
        breakdown = {}
        for event in self.events.values():
            priority = event.priority.value
            breakdown[priority] = breakdown.get(priority, 0) + 1
        return breakdown
    
    def _get_event_type_breakdown(self) -> Dict[str, int]:
        """Get breakdown of events by type."""
        breakdown = {}
        for event in self.events.values():
            event_type = event.event_type.value
            breakdown[event_type] = breakdown.get(event_type, 0) + 1
        return breakdown
    
    def get_triggered_events(self, action_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get events that were triggered by the last action.
        
        Args:
            action_context: Context about the action that was just performed
            
        Returns:
            List of triggered event data for UI display
        """
        triggered_events = []
        
        # Check for events that might be triggered by this action
        for event in self.events.values():
            if event.executed_timestamp is None:  # Only pending events
                # Check if this action relates to the event
                if self._action_triggers_event(action_context, event):
                    triggered_events.append(self._format_event_for_ui(event))
        
        return triggered_events
    
    def _action_triggers_event(self, action_context: Dict[str, Any], event: OrchestrationEvent) -> bool:
        """Check if an action triggers a specific event."""
        action_text = action_context.get('action', '').lower()
        character = action_context.get('character', '').lower()
        
        # Check if action involves target characters
        if event.target_characters and any(char.lower() in action_text for char in event.target_characters):
            return True
        
        # Check if action relates to location
        if event.location_hint and event.location_hint.lower() in action_text:
            return True
        
        # Check if action relates to emotional context
        if event.emotional_context and any(emotion.lower() in action_text for emotion in event.emotional_context):
            return True
        
        # Check if action relates to suggested actions
        if event.suggested_actions and any(suggestion.lower() in action_text for suggestion in event.suggested_actions):
            return True
        
        return False
    
    def _format_event_for_ui(self, event: OrchestrationEvent) -> Dict[str, Any]:
        """Format an event for UI display."""
        return {
            'event_id': event.event_id,
            'title': event.title,
            'description': event.description,
            'event_type': event.event_type.value,
            'priority': event.priority.value,
            'urgency_level': event.urgency_level,
            'event_icon': event.event_icon,
            'involved_characters': event.involved_characters,
            'memory_tie_ins': event.memory_tie_ins,
            'arc_impact': event.arc_impact,
            'thread_impact': event.thread_impact,
            'suggested_responses': event.suggested_responses,
            'suggested_actions': event.suggested_actions,
            'emotional_context': event.emotional_context,
            'location_hint': event.location_hint,
            'timing_hint': event.timing_hint,
            'created_timestamp': event.created_timestamp.isoformat(),
            'metadata': event.metadata
        }
    
    def get_event_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent event history for timeline display.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events formatted for UI
        """
        # Get all events sorted by creation time (newest first)
        sorted_events = sorted(
            self.events.values(),
            key=lambda x: x.created_timestamp,
            reverse=True
        )
        
        # Return the most recent events
        recent_events = sorted_events[:limit]
        return [self._format_event_for_ui(event) for event in recent_events]
    
    def enhance_event_with_context(self, event: OrchestrationEvent, campaign_state: CampaignState) -> OrchestrationEvent:
        """
        Enhance an event with additional context from campaign state.
        
        Args:
            event: The event to enhance
            campaign_state: Current campaign state
            
        Returns:
            Enhanced event with additional context
        """
        # Set urgency level based on priority
        if event.priority == OrchestrationPriority.CRITICAL:
            event.urgency_level = "critical"
        elif event.priority == OrchestrationPriority.HIGH:
            event.urgency_level = "high"
        elif event.priority == OrchestrationPriority.LOW:
            event.urgency_level = "low"
        else:
            event.urgency_level = "normal"
        
        # Set event icon based on type
        icon_map = {
            OrchestrationEventType.QUEST_SUGGESTION: "🗺️",
            OrchestrationEventType.ENCOUNTER_TRIGGER: "⚔️",
            OrchestrationEventType.CHARACTER_DEVELOPMENT: "👤",
            OrchestrationEventType.PLOT_DEVELOPMENT: "📖",
            OrchestrationEventType.WORLD_EVENT: "🌍",
            OrchestrationEventType.EMOTIONAL_MOMENT: "❤️",
            OrchestrationEventType.RELATIONSHIP_DEVELOPMENT: "🤝",
            OrchestrationEventType.MYSTERY_REVELATION: "👁️"
        }
        event.event_icon = icon_map.get(event.event_type, "⚔️")
        
        # Add memory tie-ins
        if campaign_state.recent_memories:
            recent_memory = campaign_state.recent_memories[0]
            event.memory_tie_ins.append(f"Related to recent memory: {recent_memory.get('summary', 'Unknown')}")
        
        # Add arc impacts
        for arc in campaign_state.active_arcs:
            if arc.get('title') in event.title or arc.get('description') in event.description:
                event.arc_impact[arc.get('id', 'unknown')] = f"Advances arc: {arc.get('title')}"
        
        # Add thread impacts
        for thread in campaign_state.open_threads:
            if thread.get('title') in event.title or thread.get('description') in event.description:
                event.thread_impact[thread.get('id', 'unknown')] = f"Develops thread: {thread.get('title')}"
        
        # Generate suggested responses
        event.suggested_responses = self._generate_suggested_responses(event, campaign_state)
        
        return event
    
    def _generate_suggested_responses(self, event: OrchestrationEvent, campaign_state: CampaignState) -> List[Dict[str, Any]]:
        """Generate suggested response options for an event."""
        responses = []
        
        # Add suggested actions as response options
        for i, action in enumerate(event.suggested_actions[:3]):  # Limit to 3 responses
            responses.append({
                'id': f"response_{event.event_id}_{i}",
                'text': action,
                'type': 'action',
                'description': f"Choose to {action.lower()}",
                'emotional_impact': event.emotional_context[i % len(event.emotional_context)] if event.emotional_context else "neutral"
            })
        
        # Add a "wait and observe" option
        responses.append({
            'id': f"response_{event.event_id}_wait",
            'text': "Wait and observe",
            'type': 'passive',
            'description': "Take a moment to assess the situation",
            'emotional_impact': "caution"
        })
        
        return responses

    def _load_conflicts(self):
        """Load existing conflicts from storage."""
        try:
            conflict_path = self.storage_path.replace('.jsonl', '_conflicts.jsonl')
            with open(conflict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        conflict = ConflictNode.from_dict(data)
                        self.conflicts[conflict.conflict_id] = conflict
            logger.info(f"Loaded {len(self.conflicts)} conflicts")
        except FileNotFoundError:
            logger.info("No existing conflicts found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading conflicts: {e}")
    
    def _save_conflict(self, conflict: ConflictNode):
        """Save a single conflict to persistent storage."""
        try:
            conflict_path = self.storage_path.replace('.jsonl', '_conflicts.jsonl')
            with open(conflict_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(conflict.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error saving conflict: {e}")
            raise
    
    def _load_conflict_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load conflict generation templates."""
        return {
            'internal': [
                {
                    'title_template': "The Weight of {value}",
                    'description_template': "{character} struggles with the conflict between {value1} and {value2}.",
                    'emotional_context': ["doubt", "confusion", "determination"],
                    'value_contradictions': ["loyalty vs survival", "honor vs pragmatism", "duty vs desire"]
                },
                {
                    'title_template': "A Moment of Doubt",
                    'description_template': "Recent events have caused {character} to question their path and beliefs.",
                    'emotional_context': ["uncertainty", "reflection", "growth"],
                    'value_contradictions': ["faith vs evidence", "tradition vs progress", "caution vs action"]
                }
            ],
            'interpersonal': [
                {
                    'title_template': "Clash of {value}",
                    'description_template': "{character1} and {character2} find themselves at odds over {issue}.",
                    'emotional_context': ["tension", "frustration", "misunderstanding"],
                    'value_contradictions': ["trust vs suspicion", "loyalty vs truth", "mercy vs justice"]
                },
                {
                    'title_template': "The Price of Leadership",
                    'description_template': "{character1} must make a decision that will affect {character2}, creating tension.",
                    'emotional_context': ["responsibility", "guilt", "determination"],
                    'value_contradictions': ["individual vs group", "safety vs progress", "truth vs harmony"]
                }
            ],
            'external': [
                {
                    'title_template': "The {threat} Approaches",
                    'description_template': "A {threat} threatens {target}, forcing {character} to choose between {option1} and {option2}.",
                    'emotional_context': ["urgency", "fear", "resolve"],
                    'value_contradictions': ["safety vs duty", "retreat vs stand", "caution vs action"]
                },
                {
                    'title_template': "A Test of {value}",
                    'description_template': "The situation challenges {character}'s commitment to {value}, forcing a difficult choice.",
                    'emotional_context': ["challenge", "determination", "growth"],
                    'value_contradictions': ["ideals vs reality", "hope vs despair", "faith vs doubt"]
                }
            ]
        }
    
    def detect_conflicts(self, campaign_state: CampaignState) -> List[ConflictNode]:
        """
        Detect potential conflicts based on campaign state.
        
        Args:
            campaign_state: Current state of the campaign
            
        Returns:
            List of detected conflict nodes
        """
        conflicts = []
        
        # Analyze for internal conflicts
        internal_conflicts = self._detect_internal_conflicts(campaign_state)
        conflicts.extend(internal_conflicts)
        
        # Analyze for interpersonal conflicts
        interpersonal_conflicts = self._detect_interpersonal_conflicts(campaign_state)
        conflicts.extend(interpersonal_conflicts)
        
        # Analyze for external threats
        external_conflicts = self._detect_external_conflicts(campaign_state)
        conflicts.extend(external_conflicts)
        
        return conflicts
    
    def _detect_internal_conflicts(self, campaign_state: CampaignState) -> List[ConflictNode]:
        """Detect internal character conflicts."""
        conflicts = []
        
        # Check for stalled character arcs (potential internal struggle)
        for arc in campaign_state.active_arcs:
            if arc.get('status') == 'active':
                # Check if arc has been stalled for a while
                created_at = datetime.datetime.fromisoformat(arc.get('created_at', '2024-01-01'))
                days_since_creation = (datetime.datetime.now() - created_at).days
                
                if days_since_creation > 3:  # Arc stalled for 3+ days
                    conflict = self._generate_internal_conflict(arc, campaign_state)
                    if conflict:
                        conflicts.append(conflict)
        
        # Check for emotional contradictions
        emotional_conflicts = self._detect_emotional_contradictions(campaign_state)
        conflicts.extend(emotional_conflicts)
        
        return conflicts
    
    def _detect_interpersonal_conflicts(self, campaign_state: CampaignState) -> List[ConflictNode]:
        """Detect conflicts between characters."""
        conflicts = []
        
        # Check for characters with opposing goals
        character_goals = self._extract_character_goals(campaign_state)
        
        for char1, goals1 in character_goals.items():
            for char2, goals2 in character_goals.items():
                if char1 != char2:
                    # Check for conflicting goals
                    conflicting_goals = self._find_conflicting_goals(goals1, goals2)
                    if conflicting_goals:
                        conflict = self._generate_interpersonal_conflict(char1, char2, conflicting_goals, campaign_state)
                        if conflict:
                            conflicts.append(conflict)
        
        return conflicts
    
    def _detect_external_conflicts(self, campaign_state: CampaignState) -> List[ConflictNode]:
        """Detect external threats and challenges."""
        conflicts = []
        
        # Check for high-priority threads that need immediate attention
        for thread in campaign_state.open_threads:
            if thread.get('priority', 1) >= 7:  # High priority thread
                conflict = self._generate_external_conflict(thread, campaign_state)
                if conflict:
                    conflicts.append(conflict)
        
        # Check for world events that create pressure
        for event in campaign_state.world_events:
            if event.get('urgency', 'low') in ['high', 'critical']:
                conflict = self._generate_world_event_conflict(event, campaign_state)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _generate_internal_conflict(self, arc: Dict[str, Any], campaign_state: CampaignState) -> Optional[ConflictNode]:
        """Generate an internal conflict based on a stalled character arc."""
        try:
            character_id = arc.get('character_id', 'player')
            arc_title = arc.get('title', 'Character Development')
            
            # Select a template
            templates = self.conflict_templates['internal']
            template = random.choice(templates)
            
            # Fill the template
            title = self._fill_template(template['title_template'], {
                'value': arc_title,
                'character': character_id
            }, campaign_state)
            
            description = self._fill_template(template['description_template'], {
                'character': character_id,
                'value1': 'their goals',
                'value2': 'their fears'
            }, campaign_state)
            
            # Generate conflict ID
            conflict_id = f"internal_{character_id}_{int(time.time())}"
            
            # Create suggested resolutions
            resolutions = [
                {
                    'id': f"{conflict_id}_face",
                    'text': "Face the challenge head-on",
                    'description': "Confront the internal struggle directly",
                    'emotional_impact': "determination",
                    'arc_impact': "progress"
                },
                {
                    'id': f"{conflict_id}_adapt",
                    'text': "Adapt and compromise",
                    'description': "Find a middle ground",
                    'emotional_impact': "growth",
                    'arc_impact': "evolution"
                },
                {
                    'id': f"{conflict_id}_avoid",
                    'text': "Avoid the conflict for now",
                    'description': "Set aside the issue temporarily",
                    'emotional_impact': "relief",
                    'arc_impact': "stagnation"
                }
            ]
            
            # Create impact preview
            impact_preview = {
                'emotional_changes': {
                    'determination': 0.3,
                    'growth': 0.2,
                    'uncertainty': -0.1
                },
                'arc_progress': 0.25,
                'relationship_effects': {},
                'world_implications': []
            }
            
            conflict = ConflictNode(
                conflict_id=conflict_id,
                conflict_type=ConflictType.INTERNAL,
                urgency=ConflictUrgency.MEDIUM,
                title=title,
                description=description,
                characters_involved=[character_id],
                related_arcs=[arc.get('id', 'unknown')],
                suggested_resolutions=resolutions,
                impact_preview=impact_preview,
                emotional_context=template['emotional_context'],
                value_contradictions=template['value_contradictions'],
                conflict_icon="🧠"
            )
            
            # Save the conflict
            self.conflicts[conflict_id] = conflict
            self._save_conflict(conflict)
            
            return conflict
            
        except Exception as e:
            logger.error(f"Error generating internal conflict: {e}")
            return None
    
    def _generate_interpersonal_conflict(self, char1: str, char2: str, conflicting_goals: List[str], campaign_state: CampaignState) -> Optional[ConflictNode]:
        """Generate an interpersonal conflict between characters."""
        try:
            # Select a template
            templates = self.conflict_templates['interpersonal']
            template = random.choice(templates)
            
            # Fill the template
            title = self._fill_template(template['title_template'], {
                'value': conflicting_goals[0] if conflicting_goals else 'values',
                'character1': char1,
                'character2': char2
            }, campaign_state)
            
            description = self._fill_template(template['description_template'], {
                'character1': char1,
                'character2': char2,
                'issue': conflicting_goals[0] if conflicting_goals else 'their different approaches'
            }, campaign_state)
            
            # Generate conflict ID
            conflict_id = f"interpersonal_{char1}_{char2}_{int(time.time())}"
            
            # Create suggested resolutions
            resolutions = [
                {
                    'id': f"{conflict_id}_compromise",
                    'text': "Seek compromise",
                    'description': "Find a solution that satisfies both parties",
                    'emotional_impact': "cooperation",
                    'relationship_impact': "improvement"
                },
                {
                    'id': f"{conflict_id}_support",
                    'text': "Support one side",
                    'description': "Choose to support one character's position",
                    'emotional_impact': "loyalty",
                    'relationship_impact': "polarization"
                },
                {
                    'id': f"{conflict_id}_mediate",
                    'text': "Mediate the conflict",
                    'description': "Act as a neutral mediator",
                    'emotional_impact': "diplomacy",
                    'relationship_impact': "respect"
                }
            ]
            
            # Create impact preview
            impact_preview = {
                'emotional_changes': {
                    'tension': 0.4,
                    'cooperation': 0.2,
                    'loyalty': 0.1
                },
                'relationship_effects': {
                    f"{char1}_{char2}": -0.2,
                    f"{char2}_{char1}": -0.2
                },
                'arc_progress': 0.15,
                'world_implications': []
            }
            
            conflict = ConflictNode(
                conflict_id=conflict_id,
                conflict_type=ConflictType.INTERPERSONAL,
                urgency=ConflictUrgency.HIGH,
                title=title,
                description=description,
                characters_involved=[char1, char2],
                suggested_resolutions=resolutions,
                impact_preview=impact_preview,
                emotional_context=template['emotional_context'],
                value_contradictions=template['value_contradictions'],
                conflict_icon="🗣️"
            )
            
            # Save the conflict
            self.conflicts[conflict_id] = conflict
            self._save_conflict(conflict)
            
            return conflict
            
        except Exception as e:
            logger.error(f"Error generating interpersonal conflict: {e}")
            return None
    
    def _generate_external_conflict(self, thread: Dict[str, Any], campaign_state: CampaignState) -> Optional[ConflictNode]:
        """Generate an external conflict based on a high-priority thread."""
        try:
            thread_title = thread.get('title', 'External Threat')
            thread_description = thread.get('description', 'A significant challenge')
            
            # Select a template
            templates = self.conflict_templates['external']
            template = random.choice(templates)
            
            # Fill the template
            title = self._fill_template(template['title_template'], {
                'threat': thread_title,
                'target': 'the party',
                'character': 'player'
            }, campaign_state)
            
            description = self._fill_template(template['description_template'], {
                'threat': thread_title,
                'target': 'the party',
                'character': 'player',
                'option1': 'safety',
                'option2': 'duty'
            }, campaign_state)
            
            # Generate conflict ID
            conflict_id = f"external_{thread.get('id', 'unknown')}_{int(time.time())}"
            
            # Create suggested resolutions
            resolutions = [
                {
                    'id': f"{conflict_id}_confront",
                    'text': "Confront the threat",
                    'description': "Face the challenge directly",
                    'emotional_impact': "courage",
                    'risk_level': "high"
                },
                {
                    'id': f"{conflict_id}_strategize",
                    'text': "Develop a strategy",
                    'description': "Plan carefully before acting",
                    'emotional_impact': "caution",
                    'risk_level': "medium"
                },
                {
                    'id': f"{conflict_id}_avoid",
                    'text': "Avoid the threat",
                    'description': "Find an alternative approach",
                    'emotional_impact': "relief",
                    'risk_level': "low"
                }
            ]
            
            # Create impact preview
            impact_preview = {
                'emotional_changes': {
                    'fear': 0.3,
                    'determination': 0.4,
                    'caution': 0.2
                },
                'risk_assessment': "high",
                'world_implications': [f"Failure could result in {thread_title} becoming worse"],
                'arc_progress': 0.4
            }
            
            conflict = ConflictNode(
                conflict_id=conflict_id,
                conflict_type=ConflictType.EXTERNAL_THREAT,
                urgency=ConflictUrgency.CRITICAL,
                title=title,
                description=description,
                characters_involved=['player'],
                related_threads=[thread.get('id', 'unknown')],
                suggested_resolutions=resolutions,
                impact_preview=impact_preview,
                emotional_context=template['emotional_context'],
                value_contradictions=template['value_contradictions'],
                conflict_icon="⚔️"
            )
            
            # Save the conflict
            self.conflicts[conflict_id] = conflict
            self._save_conflict(conflict)
            
            return conflict
            
        except Exception as e:
            logger.error(f"Error generating external conflict: {e}")
            return None
    
    def _detect_emotional_contradictions(self, campaign_state: CampaignState) -> List[ConflictNode]:
        """Detect conflicts based on emotional contradictions."""
        conflicts = []
        
        # Analyze emotional context for contradictions
        emotional_context = campaign_state.emotional_context
        
        # Check for fear vs determination (common internal conflict)
        if emotional_context.get('fear', 0) > 0.5 and emotional_context.get('determination', 0) > 0.5:
            conflict = self._generate_emotional_conflict('fear', 'determination', campaign_state)
            if conflict:
                conflicts.append(conflict)
        
        # Check for loyalty vs suspicion
        if emotional_context.get('loyalty', 0) > 0.5 and emotional_context.get('suspicion', 0) > 0.5:
            conflict = self._generate_emotional_conflict('loyalty', 'suspicion', campaign_state)
            if conflict:
                conflicts.append(conflict)
        
        return conflicts
    
    def _generate_emotional_conflict(self, emotion1: str, emotion2: str, campaign_state: CampaignState) -> Optional[ConflictNode]:
        """Generate a conflict based on emotional contradiction."""
        try:
            conflict_id = f"emotional_{emotion1}_{emotion2}_{int(time.time())}"
            
            title = f"The Conflict of {emotion1.title()} and {emotion2.title()}"
            description = f"The character feels torn between {emotion1} and {emotion2}, creating internal tension."
            
            resolutions = [
                {
                    'id': f"{conflict_id}_embrace",
                    'text': f"Embrace the {emotion1}",
                    'description': f"Choose to follow the path of {emotion1}",
                    'emotional_impact': emotion1,
                    'internal_impact': "clarity"
                },
                {
                    'id': f"{conflict_id}_balance",
                    'text': "Find balance",
                    'description': "Seek harmony between conflicting emotions",
                    'emotional_impact': "peace",
                    'internal_impact': "growth"
                },
                {
                    'id': f"{conflict_id}_suppress",
                    'text': f"Suppress the {emotion2}",
                    'description': f"Push aside feelings of {emotion2}",
                    'emotional_impact': "control",
                    'internal_impact': "tension"
                }
            ]
            
            impact_preview = {
                'emotional_changes': {
                    emotion1: 0.3,
                    emotion2: -0.2,
                    'clarity': 0.1
                },
                'internal_impact': "resolution",
                'arc_progress': 0.2
            }
            
            conflict = ConflictNode(
                conflict_id=conflict_id,
                conflict_type=ConflictType.INTERNAL,
                urgency=ConflictUrgency.MEDIUM,
                title=title,
                description=description,
                characters_involved=['player'],
                suggested_resolutions=resolutions,
                impact_preview=impact_preview,
                emotional_context=[emotion1, emotion2, 'conflict'],
                value_contradictions=[f"{emotion1} vs {emotion2}"],
                conflict_icon="🧠"
            )
            
            # Save the conflict
            self.conflicts[conflict_id] = conflict
            self._save_conflict(conflict)
            
            return conflict
            
        except Exception as e:
            logger.error(f"Error generating emotional conflict: {e}")
            return None
    
    def _extract_character_goals(self, campaign_state: CampaignState) -> Dict[str, List[str]]:
        """Extract character goals from arcs and memories."""
        goals = {}
        
        for arc in campaign_state.active_arcs:
            character_id = arc.get('character_id', 'player')
            if character_id not in goals:
                goals[character_id] = []
            
            # Extract goals from arc description
            description = arc.get('description', '')
            if 'goal' in description.lower() or 'seek' in description.lower():
                goals[character_id].append(description)
        
        return goals
    
    def _find_conflicting_goals(self, goals1: List[str], goals2: List[str]) -> List[str]:
        """Find conflicting goals between two characters."""
        conflicts = []
        
        # Simple keyword-based conflict detection
        conflict_keywords = {
            'power': ['peace', 'harmony'],
            'wealth': ['generosity', 'charity'],
            'revenge': ['forgiveness', 'mercy'],
            'control': ['freedom', 'independence'],
            'safety': ['adventure', 'risk']
        }
        
        for goal1 in goals1:
            for goal2 in goals2:
                for keyword, opposites in conflict_keywords.items():
                    if keyword in goal1.lower() and any(opp in goal2.lower() for opp in opposites):
                        conflicts.append(f"{goal1} vs {goal2}")
        
        return conflicts
    
    def get_active_conflicts(self) -> List[ConflictNode]:
        """Get all active (unresolved) conflicts."""
        return [conflict for conflict in self.conflicts.values() if conflict.resolved_timestamp is None]
    
    def resolve_conflict(self, conflict_id: str, resolution_id: str, narrative_bridge) -> bool:
        """
        Resolve a conflict with a specific resolution.
        
        Args:
            conflict_id: ID of the conflict to resolve
            resolution_id: ID of the chosen resolution
            narrative_bridge: Bridge for updating game state
            
        Returns:
            True if resolution was successful
        """
        try:
            if conflict_id not in self.conflicts:
                return False
            
            conflict = self.conflicts[conflict_id]
            resolution = next((r for r in conflict.suggested_resolutions if r['id'] == resolution_id), None)
            
            if not resolution:
                return False
            
            # Mark conflict as resolved
            conflict.resolved_timestamp = datetime.datetime.now()
            conflict.resolution_chosen = resolution_id
            
            # Apply resolution effects
            self._apply_resolution_effects(conflict, resolution, narrative_bridge)
            
            # Save the updated conflict
            self._save_conflict(conflict)
            
            logger.info(f"Resolved conflict {conflict_id} with resolution {resolution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {e}")
            return False
    
    def _apply_resolution_effects(self, conflict: ConflictNode, resolution: Dict[str, Any], narrative_bridge):
        """Apply the effects of a conflict resolution."""
        try:
            # Update emotional memory
            emotional_impact = resolution.get('emotional_impact', 'neutral')
            narrative_bridge.store_dnd_memory(
                content=f"Resolved conflict '{conflict.title}' by choosing '{resolution['text']}'",
                memory_type="conflict_resolution",
                metadata={
                    'conflict_id': conflict.conflict_id,
                    'resolution_id': resolution['id'],
                    'emotional_impact': emotional_impact
                },
                tags=["conflict", "resolution", emotional_impact],
                primary_emotion=EmotionType.DETERMINATION,
                emotional_intensity=0.6
            )
            
            # Update character arcs if applicable
            for arc_id in conflict.related_arcs:
                # Add milestone to the arc
                narrative_bridge.add_arc_milestone(
                    arc_id=arc_id,
                    title=f"Conflict Resolution: {conflict.title}",
                    description=f"Resolved by choosing: {resolution['text']}",
                    emotional_context=emotional_impact,
                    completion_percentage=resolution.get('arc_impact', 0.2)
                )
            
            # Update plot threads if applicable
            for thread_id in conflict.related_threads:
                # Add update to the thread
                narrative_bridge.add_thread_update(
                    thread_id=thread_id,
                    title=f"Conflict Resolution Impact",
                    description=f"The resolution of '{conflict.title}' affects this plot thread",
                    status_change=ThreadStatus.ACTIVE
                )
            
        except Exception as e:
            logger.error(f"Error applying resolution effects: {e}")
    
    def get_conflict_summary(self) -> Dict[str, Any]:
        """Get a summary of conflict activity."""
        active_conflicts = self.get_active_conflicts()
        resolved_conflicts = [c for c in self.conflicts.values() if c.resolved_timestamp]
        
        return {
            'total_conflicts': len(self.conflicts),
            'active_conflicts': len(active_conflicts),
            'resolved_conflicts': len(resolved_conflicts),
            'conflict_types': self._get_conflict_type_breakdown(),
            'urgency_breakdown': self._get_conflict_urgency_breakdown()
        }
    
    def _get_conflict_type_breakdown(self) -> Dict[str, int]:
        """Get breakdown of conflicts by type."""
        breakdown = {}
        for conflict in self.conflicts.values():
            conflict_type = conflict.conflict_type.value
            breakdown[conflict_type] = breakdown.get(conflict_type, 0) + 1
        return breakdown
    
    def _get_conflict_urgency_breakdown(self) -> Dict[str, int]:
        """Get breakdown of conflicts by urgency."""
        breakdown = {}
        for conflict in self.conflicts.values():
            urgency = conflict.urgency.value
            breakdown[urgency] = breakdown.get(urgency, 0) + 1
        return breakdown 