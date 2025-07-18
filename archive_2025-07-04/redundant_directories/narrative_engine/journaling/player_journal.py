"""
Player Journaling System

Provides persistent journaling capabilities for player characters in narrative campaigns.
Supports both user-written and AI-generated entries with full metadata tracking.
"""

import json
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class JournalEntryType(Enum):
    """Types of journal entries."""
    PLAYER_WRITTEN = "player_written"
    AI_GENERATED = "ai_generated"
    EVENT_SUMMARY = "event_summary"
    QUEST_LOG = "quest_log"
    CHARACTER_DEVELOPMENT = "character_development"
    WORLD_OBSERVATION = "world_observation"
    CHARACTER_CREATION = "character_creation"


@dataclass
class JournalEntry:
    """Represents a single journal entry."""
    entry_id: str
    character_id: str
    campaign_id: str
    session_id: Optional[str]
    entry_type: JournalEntryType
    title: str
    content: str
    timestamp: datetime.datetime
    location: Optional[str] = None
    scene: Optional[str] = None
    tags: List[str] = None
    emotional_context: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.emotional_context is None:
            self.emotional_context = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for serialization."""
        data = asdict(self)
        data['entry_type'] = self.entry_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JournalEntry':
        """Create entry from dictionary."""
        data['entry_type'] = JournalEntryType(data['entry_type'])
        data['timestamp'] = datetime.datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class PlayerJournal:
    """
    Manages persistent player journaling for narrative campaigns.
    
    Supports both user-written and AI-generated entries with full metadata tracking,
    including character ID, campaign ID, session ID, location, and emotional context.
    """
    
    def __init__(self, storage_path: str = "journal_entries.jsonl"):
        """
        Initialize the player journal system.
        
        Args:
            storage_path: Path to the JSONL file for persistent storage
        """
        self.storage_path = storage_path
        self.entries: Dict[str, JournalEntry] = {}
        self._load_entries()
    
    def _load_entries(self):
        """Load existing journal entries from storage."""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        entry = JournalEntry.from_dict(data)
                        self.entries[entry.entry_id] = entry
            logger.info(f"Loaded {len(self.entries)} journal entries")
        except FileNotFoundError:
            logger.info("No existing journal entries found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading journal entries: {e}")
    
    def _save_entry(self, entry: JournalEntry):
        """Save a single entry to persistent storage."""
        try:
            with open(self.storage_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error saving journal entry: {e}")
            raise
    
    def add_entry(
        self,
        character_id: str,
        campaign_id: str,
        entry_type: JournalEntryType,
        title: str,
        content: str,
        session_id: Optional[str] = None,
        location: Optional[str] = None,
        scene: Optional[str] = None,
        tags: Optional[List[str]] = None,
        emotional_context: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JournalEntry:
        """
        Add a new journal entry.
        
        Args:
            character_id: ID of the character making the entry
            campaign_id: ID of the campaign
            entry_type: Type of journal entry
            title: Entry title
            content: Entry content
            session_id: Optional session ID
            location: Optional location
            scene: Optional scene description
            tags: Optional tags for categorization
            emotional_context: Optional emotional context
            metadata: Optional additional metadata
            
        Returns:
            The created JournalEntry
        """
        entry_id = f"journal_{character_id}_{campaign_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        entry = JournalEntry(
            entry_id=entry_id,
            character_id=character_id,
            campaign_id=campaign_id,
            session_id=session_id,
            entry_type=entry_type,
            title=title,
            content=content,
            timestamp=datetime.datetime.now(),
            location=location,
            scene=scene,
            tags=tags or [],
            emotional_context=emotional_context or [],
            metadata=metadata or {}
        )
        
        self.entries[entry_id] = entry
        self._save_entry(entry)
        
        logger.info(f"Added journal entry: {entry_id} for character {character_id}")
        return entry
    
    def get_entries_by_character(
        self,
        character_id: str,
        campaign_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[JournalEntry]:
        """
        Get journal entries for a specific character.
        
        Args:
            character_id: ID of the character
            campaign_id: Optional campaign filter
            limit: Optional limit on number of entries
            
        Returns:
            List of journal entries
        """
        entries = [
            entry for entry in self.entries.values()
            if entry.character_id == character_id
            and (campaign_id is None or entry.campaign_id == campaign_id)
        ]
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            entries = entries[:limit]
        
        return entries
    
    def get_entries_by_session(
        self,
        session_id: str,
        character_id: Optional[str] = None
    ) -> List[JournalEntry]:
        """
        Get journal entries for a specific session.
        
        Args:
            session_id: ID of the session
            character_id: Optional character filter
            
        Returns:
            List of journal entries
        """
        entries = [
            entry for entry in self.entries.values()
            if entry.session_id == session_id
            and (character_id is None or entry.character_id == character_id)
        ]
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return entries
    
    def get_entries_by_location(
        self,
        location: str,
        campaign_id: Optional[str] = None
    ) -> List[JournalEntry]:
        """
        Get journal entries for a specific location.
        
        Args:
            location: Location name
            campaign_id: Optional campaign filter
            
        Returns:
            List of journal entries
        """
        entries = [
            entry for entry in self.entries.values()
            if entry.location and entry.location.lower() == location.lower()
            and (campaign_id is None or entry.campaign_id == campaign_id)
        ]
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return entries
    
    def search_entries(
        self,
        query: str,
        character_id: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> List[JournalEntry]:
        """
        Search journal entries by content or title.
        
        Args:
            query: Search query
            character_id: Optional character filter
            campaign_id: Optional campaign filter
            
        Returns:
            List of matching journal entries
        """
        query_lower = query.lower()
        entries = []
        
        for entry in self.entries.values():
            if (character_id and entry.character_id != character_id):
                continue
            if (campaign_id and entry.campaign_id != campaign_id):
                continue
            
            # Search in title and content
            if (query_lower in entry.title.lower() or 
                query_lower in entry.content.lower()):
                entries.append(entry)
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return entries
    
    def get_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """
        Get a specific journal entry by ID.
        
        Args:
            entry_id: ID of the entry
            
        Returns:
            JournalEntry or None if not found
        """
        return self.entries.get(entry_id)
    
    def delete_entry(self, entry_id: str) -> bool:
        """
        Delete a journal entry.
        
        Args:
            entry_id: ID of the entry to delete
            
        Returns:
            True if deleted, False if not found
        """
        if entry_id in self.entries:
            del self.entries[entry_id]
            # Rebuild the file without the deleted entry
            self._rebuild_storage()
            logger.info(f"Deleted journal entry: {entry_id}")
            return True
        return False
    
    def _rebuild_storage(self):
        """Rebuild the storage file after deletions."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                for entry in self.entries.values():
                    f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error rebuilding storage: {e}")
            raise
    
    def get_journal_stats(
        self,
        character_id: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about journal entries.
        
        Args:
            character_id: Optional character filter
            campaign_id: Optional campaign filter
            
        Returns:
            Dictionary with journal statistics
        """
        filtered_entries = [
            entry for entry in self.entries.values()
            if (character_id is None or entry.character_id == character_id)
            and (campaign_id is None or entry.campaign_id == campaign_id)
        ]
        
        if not filtered_entries:
            return {
                'total_entries': 0,
                'entry_types': {},
                'characters': {},
                'campaigns': {},
                'date_range': None
            }
        
        # Count entry types
        entry_types = {}
        for entry in filtered_entries:
            entry_type = entry.entry_type.value
            entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
        
        # Count characters
        characters = {}
        for entry in filtered_entries:
            char_id = entry.character_id
            characters[char_id] = characters.get(char_id, 0) + 1
        
        # Count campaigns
        campaigns = {}
        for entry in filtered_entries:
            camp_id = entry.campaign_id
            campaigns[camp_id] = campaigns.get(camp_id, 0) + 1
        
        # Date range
        timestamps = [entry.timestamp for entry in filtered_entries]
        date_range = {
            'earliest': min(timestamps).isoformat(),
            'latest': max(timestamps).isoformat()
        }
        
        return {
            'total_entries': len(filtered_entries),
            'entry_types': entry_types,
            'characters': characters,
            'campaigns': campaigns,
            'date_range': date_range
        } 