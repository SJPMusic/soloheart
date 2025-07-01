"""
Session Logging System for DnD 5E Campaign
==========================================

Captures and processes session data for AI memory system
"""

import json
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from ..memory.layered_memory import LayeredMemorySystem, MemoryType, MemoryLayer, EmotionalContext

class LogEntryType(Enum):
    DIALOGUE = "dialogue"
    ACTION = "action"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    DECISION = "decision"
    ENVIRONMENT = "environment"
    SYSTEM = "system"

@dataclass
class SessionLogEntry:
    """Individual log entry for a session"""
    timestamp: datetime.datetime
    entry_type: LogEntryType
    speaker: Optional[str] = None
    content: str = ""
    metadata: Dict[str, Any] = None
    entities_mentioned: List[str] = None
    locations_mentioned: List[str] = None
    actions_taken: List[str] = None
    decisions_made: List[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.entities_mentioned is None:
            self.entities_mentioned = []
        if self.locations_mentioned is None:
            self.locations_mentioned = []
        if self.actions_taken is None:
            self.actions_taken = []
        if self.decisions_made is None:
            self.decisions_made = []

@dataclass
class SessionSummary:
    """Summary of a complete session"""
    session_id: str
    date: datetime.date
    duration_minutes: int
    participants: List[str]
    locations_visited: List[str]
    npcs_encountered: List[str]
    major_events: List[str]
    decisions_made: List[str]
    combat_encounters: List[str]
    items_found: List[str]
    quests_progressed: List[str]
    quests_completed: List[str]
    xp_gained: int
    gold_gained: int
    notes: str = ""
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.locations_visited is None:
            self.locations_visited = []
        if self.npcs_encountered is None:
            self.npcs_encountered = []
        if self.major_events is None:
            self.major_events = []
        if self.decisions_made is None:
            self.decisions_made = []
        if self.combat_encounters is None:
            self.combat_encounters = []
        if self.items_found is None:
            self.items_found = []
        if self.quests_progressed is None:
            self.quests_progressed = []
        if self.quests_completed is None:
            self.quests_completed = []

class SessionLogger:
    """Logs and processes DnD session data"""
    
    def __init__(self, memory_system: LayeredMemorySystem):
        self.memory = memory_system
        self.current_session: Optional[SessionSummary] = None
        self.session_entries: List[SessionLogEntry] = []
        self.entity_extractor = EntityExtractor()
        self.action_parser = ActionParser()
    
    def start_session(self, session_id: str, participants: List[str]) -> SessionSummary:
        """Start a new session"""
        self.current_session = SessionSummary(
            session_id=session_id,
            date=datetime.date.today(),
            duration_minutes=0,
            participants=participants,
            locations_visited=[],
            npcs_encountered=[],
            major_events=[],
            decisions_made=[],
            combat_encounters=[],
            items_found=[],
            quests_progressed=[],
            quests_completed=[],
            xp_gained=0,
            gold_gained=0
        )
        self.session_entries = []
        
        # Log session start
        self.log_entry(
            LogEntryType.SYSTEM,
            f"Session {session_id} started with participants: {', '.join(participants)}",
            metadata={'event': 'session_start'}
        )
        
        return self.current_session
    
    def end_session(self) -> SessionSummary:
        """End the current session and generate summary"""
        if not self.current_session:
            raise ValueError("No active session to end")
        
        # Log session end
        self.log_entry(
            LogEntryType.SYSTEM,
            f"Session {self.current_session.session_id} ended",
            metadata={'event': 'session_end'}
        )
        
        # Generate summary from entries
        self._generate_session_summary()
        
        # Process session data for memory system
        self._process_session_for_memory()
        
        return self.current_session
    
    def log_dialogue(self, speaker: str, content: str, metadata: Dict[str, Any] = None):
        """Log dialogue between characters"""
        entry = self.log_entry(
            LogEntryType.DIALOGUE,
            content,
            speaker=speaker,
            metadata=metadata or {}
        )
        
        # Extract entities mentioned in dialogue
        entities = self.entity_extractor.extract_entities(content)
        entry.entities_mentioned = entities
        
        # Update session NPCs encountered
        if speaker not in self.current_session.participants:
            if speaker not in self.current_session.npcs_encountered:
                self.current_session.npcs_encountered.append(speaker)
    
    def log_action(self, actor: str, action: str, target: str = None, metadata: Dict[str, Any] = None):
        """Log character actions"""
        content = f"{actor} {action}"
        if target:
            content += f" {target}"
        
        entry = self.log_entry(
            LogEntryType.ACTION,
            content,
            speaker=actor,
            metadata=metadata or {}
        )
        
        # Parse action for entities and locations
        entities = self.entity_extractor.extract_entities(content)
        locations = self.entity_extractor.extract_locations(content)
        actions = self.action_parser.parse_action(action)
        
        entry.entities_mentioned = entities
        entry.locations_mentioned = locations
        entry.actions_taken = actions
        
        # Update session data
        self.current_session.locations_visited.extend(locations)
        self.current_session.major_events.append(content)
    
    def log_combat(self, participants: List[str], outcome: str, metadata: Dict[str, Any] = None):
        """Log combat encounters"""
        content = f"Combat between {', '.join(participants)}: {outcome}"
        
        entry = self.log_entry(
            LogEntryType.COMBAT,
            content,
            metadata=metadata or {}
        )
        
        entry.entities_mentioned = participants
        entry.actions_taken = ['combat']
        
        # Update session data
        self.current_session.combat_encounters.append(content)
        self.current_session.npcs_encountered.extend([p for p in participants if p not in self.current_session.participants])
    
    def log_decision(self, decision_maker: str, decision: str, consequences: str = None, metadata: Dict[str, Any] = None):
        """Log player decisions and consequences"""
        content = f"{decision_maker} decided to {decision}"
        if consequences:
            content += f". Consequences: {consequences}"
        
        entry = self.log_entry(
            LogEntryType.DECISION,
            content,
            speaker=decision_maker,
            metadata=metadata or {}
        )
        
        entry.decisions_made = [decision]
        
        # Update session data
        self.current_session.decisions_made.append(decision)
    
    def log_exploration(self, location: str, description: str, discoveries: List[str] = None, metadata: Dict[str, Any] = None):
        """Log exploration of locations"""
        content = f"Explored {location}: {description}"
        if discoveries:
            content += f". Discoveries: {', '.join(discoveries)}"
        
        entry = self.log_entry(
            LogEntryType.EXPLORATION,
            content,
            metadata=metadata or {}
        )
        
        entry.locations_mentioned = [location]
        entry.entities_mentioned = discoveries or []
        
        # Update session data
        if location not in self.current_session.locations_visited:
            self.current_session.locations_visited.append(location)
        if discoveries:
            self.current_session.items_found.extend(discoveries)
    
    def log_entry(self, entry_type: LogEntryType, content: str, speaker: str = None, metadata: Dict[str, Any] = None) -> SessionLogEntry:
        """Log a generic entry"""
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        entry = SessionLogEntry(
            timestamp=datetime.datetime.now(),
            entry_type=entry_type,
            speaker=speaker,
            content=content,
            metadata=metadata or {}
        )
        
        self.session_entries.append(entry)
        return entry
    
    def _generate_session_summary(self):
        """Generate summary from session entries"""
        if not self.current_session or not self.session_entries:
            return
        
        # Calculate duration
        if len(self.session_entries) >= 2:
            start_time = self.session_entries[0].timestamp
            end_time = self.session_entries[-1].timestamp
            duration = end_time - start_time
            self.current_session.duration_minutes = int(duration.total_seconds() / 60)
        
        # Extract unique entities and locations
        all_entities = set()
        all_locations = set()
        
        for entry in self.session_entries:
            all_entities.update(entry.entities_mentioned)
            all_locations.update(entry.locations_mentioned)
        
        # Update session data with unique values
        self.current_session.npcs_encountered = list(set(self.current_session.npcs_encountered))
        self.current_session.locations_visited = list(set(self.current_session.locations_visited))
        self.current_session.items_found = list(set(self.current_session.items_found))
    
    def _process_session_for_memory(self):
        """Process session data for the memory system"""
        if not self.current_session:
            return
        
        # Create session entity for memory system
        session_data = {
            'session_id': self.current_session.session_id,
            'date': self.current_session.date.isoformat(),
            'duration': self.current_session.duration_minutes,
            'participants': self.current_session.participants,
            'summary': self._create_session_summary_text()
        }
        
        # Add session to memory
        self.memory.add_memory(
            content=session_data,
            memory_type=MemoryType.EVENT,
            layer=MemoryLayer.MID_TERM,
            user_id='dm',
            session_id=self.current_session.session_id,
            emotional_weight=0.8,
            thematic_tags=['session_summary', 'campaign_management']
        )
        
        # Process each entry for entity extraction
        for entry in self.session_entries:
            self._process_entry_for_memory(entry)
    
    def _create_session_summary_text(self) -> str:
        """Create a text summary of the session"""
        summary_parts = []
        
        if self.current_session.locations_visited:
            summary_parts.append(f"Visited: {', '.join(self.current_session.locations_visited)}")
        
        if self.current_session.npcs_encountered:
            summary_parts.append(f"Encountered: {', '.join(self.current_session.npcs_encountered)}")
        
        if self.current_session.combat_encounters:
            summary_parts.append(f"Combat: {len(self.current_session.combat_encounters)} encounters")
        
        if self.current_session.decisions_made:
            summary_parts.append(f"Decisions: {len(self.current_session.decisions_made)} made")
        
        if self.current_session.items_found:
            summary_parts.append(f"Found: {', '.join(self.current_session.items_found)}")
        
        return ". ".join(summary_parts)
    
    def _process_entry_for_memory(self, entry: SessionLogEntry):
        """Process individual entry for memory system"""
        # Extract entities and add to memory
        for entity_name in entry.entities_mentioned:
            if entity_name and entity_name not in self.current_session.participants:
                # Check for existing entity in memory
                existing = self.memory.recall(query=entity_name, limit=1)
                if not existing:
                    # Create new entity
                    entity_data = {
                        'name': entity_name,
                        'first_mentioned': self.current_session.session_id,
                        'last_updated': self.current_session.session_id,
                        'context_snippets': [entry.content]
                    }
                    self.memory.add_memory(
                        content=entity_data,
                        memory_type=MemoryType.CHARACTER_DEVELOPMENT,
                        layer=MemoryLayer.MID_TERM,
                        user_id='dm',
                        session_id=self.current_session.session_id,
                        emotional_weight=0.6,
                        thematic_tags=['entity', 'character']
                    )
        
        # Extract locations and add to memory
        for location_name in entry.locations_mentioned:
            if location_name:
                location_data = {
                    'name': location_name,
                    'first_mentioned': self.current_session.session_id,
                    'last_updated': self.current_session.session_id,
                    'context_snippets': [entry.content]
                }
                self.memory.add_memory(
                    content=location_data,
                    memory_type=MemoryType.WORLD_STATE,
                    layer=MemoryLayer.MID_TERM,
                    user_id='dm',
                    session_id=self.current_session.session_id,
                    emotional_weight=0.5,
                    thematic_tags=['location', 'world_state']
                )
    
    def get_session_export(self) -> Dict[str, Any]:
        """Export session data for external use"""
        if not self.current_session:
            return {}
        
        return {
            'session': asdict(self.current_session),
            'entries': [asdict(entry) for entry in self.session_entries]
        }
    
    def save_session_to_file(self, filename: str):
        """Save current session to a JSON file"""
        export_data = self.get_session_export()
        
        def convert_datetime(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            elif isinstance(obj, datetime.date):
                return obj.isoformat()
            return obj
        
        def convert_recursive(data):
            if isinstance(data, dict):
                return {k: convert_recursive(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [convert_recursive(item) for item in data]
            else:
                return convert_datetime(data)
        
        export_data = convert_recursive(export_data)
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

    def get_session_count(self) -> int:
        """Get the total number of sessions logged."""
        # This is a simple implementation - in a real system you'd track this
        return 1 if self.current_session else 0

    def export_sessions(self) -> Dict[str, Any]:
        """Export all session data for save/load functionality."""
        return {
            'current_session': asdict(self.current_session) if self.current_session else None,
            'session_entries': [asdict(entry) for entry in self.session_entries],
            'session_count': self.get_session_count()
        }

    def import_sessions(self, data: Dict[str, Any]):
        """Import session data from save/load data."""
        if data.get('current_session'):
            session_data = data['current_session']
            # Convert date string back to date object
            if 'date' in session_data and isinstance(session_data['date'], str):
                session_data['date'] = datetime.datetime.fromisoformat(session_data['date']).date()
            self.current_session = SessionSummary(**session_data)
        
        if data.get('session_entries'):
            self.session_entries = []
            for entry_data in data['session_entries']:
                # Convert timestamp string back to datetime object
                if 'timestamp' in entry_data and isinstance(entry_data['timestamp'], str):
                    entry_data['timestamp'] = datetime.datetime.fromisoformat(entry_data['timestamp'])
                # Convert entry_type string back to enum
                if 'entry_type' in entry_data and isinstance(entry_data['entry_type'], str):
                    entry_data['entry_type'] = LogEntryType(entry_data['entry_type'])
                self.session_entries.append(SessionLogEntry(**entry_data))

class EntityExtractor:
    """Extracts entities and locations from text"""
    
    def __init__(self):
        self.name_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last names
            r'\b[A-Z][a-z]+ the [A-Z][a-z]+\b',  # Titles
            r'\b[A-Z][a-z]+ of [A-Z][a-z]+\b',  # Of names
        ]
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract entity names from text"""
        import re
        
        entities = []
        
        # Simple extraction - look for capitalized words that might be names
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                # Check if it's followed by another capitalized word (full name)
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    full_name = f"{word} {words[i + 1]}"
                    if full_name not in entities:
                        entities.append(full_name)
                elif word not in entities:
                    entities.append(word)
        
        return entities
    
    def extract_locations(self, text: str) -> List[str]:
        """Extract location names from text"""
        import re
        
        locations = []
        
        # Look for location indicators
        location_indicators = ['in', 'at', 'to', 'from', 'near', 'around']
        words = text.split()
        
        for i, word in enumerate(words):
            if word.lower() in location_indicators and i + 1 < len(words):
                next_word = words[i + 1]
                if next_word[0].isupper():
                    locations.append(next_word)
        
        return locations

class ActionParser:
    """Parses actions from text"""
    
    def __init__(self):
        self.action_verbs = [
            'attack', 'cast', 'move', 'search', 'investigate', 'talk', 'persuade',
            'intimidate', 'deceive', 'stealth', 'hide', 'sneak', 'climb', 'jump',
            'swim', 'fly', 'teleport', 'heal', 'cure', 'bless', 'curse', 'summon'
        ]
    
    def parse_action(self, action_text: str) -> List[str]:
        """Parse action text to extract specific actions"""
        actions = []
        words = action_text.lower().split()
        
        for word in words:
            if word in self.action_verbs:
                actions.append(word)
        
        return actions 