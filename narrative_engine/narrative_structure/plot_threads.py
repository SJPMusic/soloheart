"""
Plot Thread Management System

Provides tracking and management of plot threads for narrative campaigns.
Supports thread creation, resolution tracking, and memory association.
"""

import json
import datetime
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ThreadStatus(Enum):
    """Status of a plot thread."""
    OPEN = "open"
    RESOLVED = "resolved"
    ABANDONED = "abandoned"
    SUSPENDED = "suspended"
    ESCALATED = "escalated"


class ThreadType(Enum):
    """Types of plot threads."""
    # Mystery threads
    MYSTERY = "mystery"
    INVESTIGATION = "investigation"
    CONSPIRACY = "conspiracy"
    SECRET = "secret"
    
    # Quest threads
    QUEST = "quest"
    SIDE_QUEST = "side_quest"
    MAIN_QUEST = "main_quest"
    PERSONAL_QUEST = "personal_quest"
    
    # Relationship threads
    RELATIONSHIP = "relationship"
    CONFLICT = "conflict"
    ALLIANCE = "alliance"
    BETRAYAL = "betrayal"
    
    # World threads
    WORLD_EVENT = "world_event"
    POLITICAL = "political"
    RELIGIOUS = "religious"
    ECONOMIC = "economic"
    
    # Character threads
    CHARACTER_DEVELOPMENT = "character_development"
    BACKSTORY = "backstory"
    TRANSFORMATION = "transformation"
    REDEMPTION = "redemption"


@dataclass
class ThreadUpdate:
    """Represents an update to a plot thread."""
    update_id: str
    title: str
    description: str
    timestamp: datetime.datetime
    memory_ids: List[str] = field(default_factory=list)
    status_change: Optional[ThreadStatus] = None
    priority_change: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.status_change:
            data['status_change'] = self.status_change.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThreadUpdate':
        """Create from dictionary."""
        data['timestamp'] = datetime.datetime.fromisoformat(data['timestamp'])
        if data.get('status_change'):
            data['status_change'] = ThreadStatus(data['status_change'])
        return cls(**data)


@dataclass
class PlotThread:
    """Represents a plot thread with tracking and resolution status."""
    thread_id: str
    campaign_id: str
    name: str
    thread_type: ThreadType
    status: ThreadStatus
    description: str
    created_timestamp: datetime.datetime
    updated_timestamp: datetime.datetime
    priority: int = 1  # 1-10, higher is more important
    assigned_characters: List[str] = field(default_factory=list)
    updates: List[ThreadUpdate] = field(default_factory=list)
    associated_memory_ids: Set[str] = field(default_factory=set)
    tags: List[str] = field(default_factory=list)
    resolution_notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert set to list for serialization."""
        if isinstance(self.associated_memory_ids, set):
            self.associated_memory_ids = list(self.associated_memory_ids)
    
    def add_update(
        self,
        title: str,
        description: str,
        memory_ids: Optional[List[str]] = None,
        status_change: Optional[ThreadStatus] = None,
        priority_change: Optional[int] = None
    ) -> ThreadUpdate:
        """
        Add an update to the plot thread.
        
        Args:
            title: Update title
            description: Update description
            memory_ids: Associated memory IDs
            status_change: Optional status change
            priority_change: Optional priority change
            
        Returns:
            The created update
        """
        update_id = f"update_{self.thread_id}_{len(self.updates) + 1}"
        
        update = ThreadUpdate(
            update_id=update_id,
            title=title,
            description=description,
            timestamp=datetime.datetime.now(),
            memory_ids=memory_ids or [],
            status_change=status_change,
            priority_change=priority_change
        )
        
        self.updates.append(update)
        self.updated_timestamp = datetime.datetime.now()
        
        # Apply status change if provided
        if status_change:
            self.status = status_change
        
        # Apply priority change if provided
        if priority_change is not None:
            self.priority = max(1, min(10, priority_change))
        
        # Update associated memory IDs
        if memory_ids:
            self.associated_memory_ids.extend(memory_ids)
            self.associated_memory_ids = list(set(self.associated_memory_ids))
        
        logger.info(f"Added update '{title}' to thread '{self.name}'")
        return update
    
    def resolve_thread(self, resolution_notes: str, memory_ids: Optional[List[str]] = None):
        """
        Mark the thread as resolved.
        
        Args:
            resolution_notes: Notes about how the thread was resolved
            memory_ids: Associated memory IDs for the resolution
        """
        self.status = ThreadStatus.RESOLVED
        self.resolution_notes = resolution_notes
        self.updated_timestamp = datetime.datetime.now()
        
        # Add resolution update
        self.add_update(
            title="Thread Resolved",
            description=resolution_notes,
            memory_ids=memory_ids,
            status_change=ThreadStatus.RESOLVED
        )
        
        logger.info(f"Resolved thread '{self.name}'")
    
    def assign_character(self, character_id: str):
        """Assign a character to this thread."""
        if character_id not in self.assigned_characters:
            self.assigned_characters.append(character_id)
            self.updated_timestamp = datetime.datetime.now()
            logger.info(f"Assigned character {character_id} to thread '{self.name}'")
    
    def unassign_character(self, character_id: str):
        """Unassign a character from this thread."""
        if character_id in self.assigned_characters:
            self.assigned_characters.remove(character_id)
            self.updated_timestamp = datetime.datetime.now()
            logger.info(f"Unassigned character {character_id} from thread '{self.name}'")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['thread_type'] = self.thread_type.value
        data['status'] = self.status.value
        data['created_timestamp'] = self.created_timestamp.isoformat()
        data['updated_timestamp'] = self.updated_timestamp.isoformat()
        data['updates'] = [u.to_dict() for u in self.updates]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlotThread':
        """Create from dictionary."""
        data['thread_type'] = ThreadType(data['thread_type'])
        data['status'] = ThreadStatus(data['status'])
        data['created_timestamp'] = datetime.datetime.fromisoformat(data['created_timestamp'])
        data['updated_timestamp'] = datetime.datetime.fromisoformat(data['updated_timestamp'])
        data['updates'] = [ThreadUpdate.from_dict(u) for u in data['updates']]
        return cls(**data)


class PlotThreadManager:
    """
    Manages plot threads for narrative campaigns.
    
    Provides creation, tracking, and querying of plot threads with full
    memory association and resolution tracking.
    """
    
    def __init__(self, storage_path: str = "plot_threads.jsonl"):
        """
        Initialize the plot thread manager.
        
        Args:
            storage_path: Path to the JSONL file for persistent storage
        """
        self.storage_path = storage_path
        self.threads: Dict[str, PlotThread] = {}
        self._load_threads()
    
    def _load_threads(self):
        """Load existing plot threads from storage."""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        thread = PlotThread.from_dict(data)
                        self.threads[thread.thread_id] = thread
            logger.info(f"Loaded {len(self.threads)} plot threads")
        except FileNotFoundError:
            logger.info("No existing plot threads found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading plot threads: {e}")
    
    def _save_thread(self, thread: PlotThread):
        """Save a single thread to persistent storage."""
        try:
            with open(self.storage_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(thread.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error saving plot thread: {e}")
            raise
    
    def create_thread(
        self,
        campaign_id: str,
        name: str,
        thread_type: ThreadType,
        description: str,
        priority: int = 1,
        assigned_characters: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PlotThread:
        """
        Create a new plot thread.
        
        Args:
            campaign_id: ID of the campaign
            name: Thread name
            thread_type: Type of thread
            description: Thread description
            priority: Thread priority (1-10)
            assigned_characters: Optional assigned characters
            tags: Optional tags
            metadata: Optional additional metadata
            
        Returns:
            The created PlotThread
        """
        thread_id = f"thread_{campaign_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        thread = PlotThread(
            thread_id=thread_id,
            campaign_id=campaign_id,
            name=name,
            thread_type=thread_type,
            status=ThreadStatus.OPEN,
            description=description,
            created_timestamp=datetime.datetime.now(),
            updated_timestamp=datetime.datetime.now(),
            priority=max(1, min(10, priority)),
            assigned_characters=assigned_characters or [],
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.threads[thread_id] = thread
        self._save_thread(thread)
        
        logger.info(f"Created plot thread: {name} for campaign {campaign_id}")
        return thread
    
    def get_thread(self, thread_id: str) -> Optional[PlotThread]:
        """
        Get a specific plot thread by ID.
        
        Args:
            thread_id: ID of the thread
            
        Returns:
            PlotThread or None if not found
        """
        return self.threads.get(thread_id)
    
    def get_threads_by_campaign(
        self,
        campaign_id: str,
        status: Optional[ThreadStatus] = None
    ) -> List[PlotThread]:
        """
        Get plot threads for a specific campaign.
        
        Args:
            campaign_id: ID of the campaign
            status: Optional status filter
            
        Returns:
            List of plot threads
        """
        threads = [
            thread for thread in self.threads.values()
            if thread.campaign_id == campaign_id
            and (status is None or thread.status == status)
        ]
        
        # Sort by priority (highest first), then by updated timestamp (newest first)
        threads.sort(key=lambda x: (-x.priority, x.updated_timestamp), reverse=True)
        
        return threads
    
    def get_threads_by_character(
        self,
        character_id: str,
        campaign_id: Optional[str] = None,
        status: Optional[ThreadStatus] = None
    ) -> List[PlotThread]:
        """
        Get plot threads assigned to a specific character.
        
        Args:
            character_id: ID of the character
            campaign_id: Optional campaign filter
            status: Optional status filter
            
        Returns:
            List of plot threads
        """
        threads = [
            thread for thread in self.threads.values()
            if character_id in thread.assigned_characters
            and (campaign_id is None or thread.campaign_id == campaign_id)
            and (status is None or thread.status == status)
        ]
        
        # Sort by priority (highest first), then by updated timestamp (newest first)
        threads.sort(key=lambda x: (-x.priority, x.updated_timestamp), reverse=True)
        
        return threads
    
    def get_threads_by_type(
        self,
        thread_type: ThreadType,
        campaign_id: Optional[str] = None
    ) -> List[PlotThread]:
        """
        Get plot threads by type.
        
        Args:
            thread_type: Type of thread to filter by
            campaign_id: Optional campaign filter
            
        Returns:
            List of plot threads
        """
        threads = [
            thread for thread in self.threads.values()
            if thread.thread_type == thread_type
            and (campaign_id is None or thread.campaign_id == campaign_id)
        ]
        
        # Sort by priority (highest first), then by updated timestamp (newest first)
        threads.sort(key=lambda x: (-x.priority, x.updated_timestamp), reverse=True)
        
        return threads
    
    def get_open_threads(
        self,
        campaign_id: Optional[str] = None,
        min_priority: int = 1
    ) -> List[PlotThread]:
        """
        Get open plot threads.
        
        Args:
            campaign_id: Optional campaign filter
            min_priority: Minimum priority filter
            
        Returns:
            List of open plot threads
        """
        threads = [
            thread for thread in self.threads.values()
            if thread.status == ThreadStatus.OPEN
            and thread.priority >= min_priority
            and (campaign_id is None or thread.campaign_id == campaign_id)
        ]
        
        # Sort by priority (highest first), then by updated timestamp (newest first)
        threads.sort(key=lambda x: (-x.priority, x.updated_timestamp), reverse=True)
        
        return threads
    
    def add_update_to_thread(
        self,
        thread_id: str,
        title: str,
        description: str,
        memory_ids: Optional[List[str]] = None,
        status_change: Optional[ThreadStatus] = None,
        priority_change: Optional[int] = None
    ) -> Optional[ThreadUpdate]:
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
            The created update or None if thread not found
        """
        thread = self.get_thread(thread_id)
        if not thread:
            logger.warning(f"Thread not found: {thread_id}")
            return None
        
        update = thread.add_update(
            title=title,
            description=description,
            memory_ids=memory_ids,
            status_change=status_change,
            priority_change=priority_change
        )
        
        # Update the thread in storage
        self._update_thread_storage(thread)
        
        return update
    
    def resolve_thread(
        self,
        thread_id: str,
        resolution_notes: str,
        memory_ids: Optional[List[str]] = None
    ) -> bool:
        """
        Mark a plot thread as resolved.
        
        Args:
            thread_id: ID of the thread
            resolution_notes: Notes about how the thread was resolved
            memory_ids: Associated memory IDs for the resolution
            
        Returns:
            True if resolved, False if thread not found
        """
        thread = self.get_thread(thread_id)
        if not thread:
            logger.warning(f"Thread not found: {thread_id}")
            return False
        
        thread.resolve_thread(resolution_notes, memory_ids)
        self._update_thread_storage(thread)
        return True
    
    def assign_character_to_thread(self, thread_id: str, character_id: str) -> bool:
        """
        Assign a character to a plot thread.
        
        Args:
            thread_id: ID of the thread
            character_id: ID of the character
            
        Returns:
            True if assigned, False if thread not found
        """
        thread = self.get_thread(thread_id)
        if not thread:
            logger.warning(f"Thread not found: {thread_id}")
            return False
        
        thread.assign_character(character_id)
        self._update_thread_storage(thread)
        return True
    
    def unassign_character_from_thread(self, thread_id: str, character_id: str) -> bool:
        """
        Unassign a character from a plot thread.
        
        Args:
            thread_id: ID of the thread
            character_id: ID of the character
            
        Returns:
            True if unassigned, False if thread not found
        """
        thread = self.get_thread(thread_id)
        if not thread:
            logger.warning(f"Thread not found: {thread_id}")
            return False
        
        thread.unassign_character(character_id)
        self._update_thread_storage(thread)
        return True
    
    def _update_thread_storage(self, thread: PlotThread):
        """Update thread in storage after modifications."""
        # Rebuild the file with the updated thread
        self._rebuild_storage()
    
    def _rebuild_storage(self):
        """Rebuild the storage file."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                for thread in self.threads.values():
                    f.write(json.dumps(thread.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error rebuilding storage: {e}")
            raise
    
    def get_thread_summary(
        self,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a summary of plot threads.
        
        Args:
            campaign_id: Optional campaign filter
            
        Returns:
            Dictionary with thread summary statistics
        """
        filtered_threads = [
            thread for thread in self.threads.values()
            if campaign_id is None or thread.campaign_id == campaign_id
        ]
        
        if not filtered_threads:
            return {
                'total_threads': 0,
                'thread_types': {},
                'status_counts': {},
                'priority_distribution': {},
                'campaigns': {},
                'average_priority': 0.0
            }
        
        # Count thread types
        thread_types = {}
        for thread in filtered_threads:
            thread_type = thread.thread_type.value
            thread_types[thread_type] = thread_types.get(thread_type, 0) + 1
        
        # Count statuses
        status_counts = {}
        for thread in filtered_threads:
            status = thread.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Priority distribution
        priority_distribution = {}
        for thread in filtered_threads:
            priority = thread.priority
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        # Count campaigns
        campaigns = {}
        for thread in filtered_threads:
            camp_id = thread.campaign_id
            campaigns[camp_id] = campaigns.get(camp_id, 0) + 1
        
        # Average priority
        total_priority = sum(thread.priority for thread in filtered_threads)
        average_priority = total_priority / len(filtered_threads)
        
        return {
            'total_threads': len(filtered_threads),
            'thread_types': thread_types,
            'status_counts': status_counts,
            'priority_distribution': priority_distribution,
            'campaigns': campaigns,
            'average_priority': average_priority
        }
    
    def search_threads(
        self,
        query: str,
        campaign_id: Optional[str] = None
    ) -> List[PlotThread]:
        """
        Search plot threads by name or description.
        
        Args:
            query: Search query
            campaign_id: Optional campaign filter
            
        Returns:
            List of matching plot threads
        """
        query_lower = query.lower()
        threads = []
        
        for thread in self.threads.values():
            if campaign_id and thread.campaign_id != campaign_id:
                continue
            
            # Search in name and description
            if (query_lower in thread.name.lower() or 
                query_lower in thread.description.lower()):
                threads.append(thread)
        
        # Sort by priority (highest first), then by updated timestamp (newest first)
        threads.sort(key=lambda x: (-x.priority, x.updated_timestamp), reverse=True)
        
        return threads 