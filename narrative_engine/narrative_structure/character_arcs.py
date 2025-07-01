"""
Character Arc Management System

Provides tracking and management of character arcs for long-term narrative development.
Supports arc creation, progression tracking, and memory association.
"""

import json
import datetime
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ArcStatus(Enum):
    """Status of a character arc."""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"
    PLANNED = "planned"


class ArcType(Enum):
    """Types of character arcs."""
    # Personal development arcs
    GROWTH = "growth"
    REDEMPTION = "redemption"
    FALL = "fall"
    TRANSFORMATION = "transformation"
    SELF_DISCOVERY = "self_discovery"
    
    # Relationship arcs
    FRIENDSHIP = "friendship"
    ROMANCE = "romance"
    RIVALRY = "rivalry"
    MENTORSHIP = "mentorship"
    FAMILY = "family"
    
    # Goal-oriented arcs
    QUEST = "quest"
    REVENGE = "revenge"
    POWER = "power"
    KNOWLEDGE = "knowledge"
    FREEDOM = "freedom"
    
    # Conflict arcs
    INTERNAL_CONFLICT = "internal_conflict"
    EXTERNAL_CONFLICT = "external_conflict"
    MORAL_DILEMMA = "moral_dilemma"
    IDENTITY_CRISIS = "identity_crisis"


@dataclass
class ArcMilestone:
    """Represents a milestone in a character arc."""
    milestone_id: str
    title: str
    description: str
    timestamp: datetime.datetime
    memory_ids: List[str] = field(default_factory=list)
    emotional_context: Optional[str] = None
    completion_percentage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArcMilestone':
        """Create from dictionary."""
        data['timestamp'] = datetime.datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class CharacterArc:
    """Represents a character arc with progression tracking."""
    arc_id: str
    character_id: str
    campaign_id: str
    name: str
    arc_type: ArcType
    status: ArcStatus
    description: str
    created_timestamp: datetime.datetime
    updated_timestamp: datetime.datetime
    target_completion: Optional[datetime.datetime] = None
    milestones: List[ArcMilestone] = field(default_factory=list)
    associated_memory_ids: Set[str] = field(default_factory=set)
    tags: List[str] = field(default_factory=list)
    emotional_themes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert set to list for serialization."""
        if isinstance(self.associated_memory_ids, set):
            self.associated_memory_ids = list(self.associated_memory_ids)
    
    def add_milestone(
        self,
        title: str,
        description: str,
        memory_ids: Optional[List[str]] = None,
        emotional_context: Optional[str] = None,
        completion_percentage: float = 0.0
    ) -> ArcMilestone:
        """
        Add a milestone to the arc.
        
        Args:
            title: Milestone title
            description: Milestone description
            memory_ids: Associated memory IDs
            emotional_context: Emotional context
            completion_percentage: Completion percentage (0.0 to 1.0)
            
        Returns:
            The created milestone
        """
        milestone_id = f"milestone_{self.arc_id}_{len(self.milestones) + 1}"
        
        milestone = ArcMilestone(
            milestone_id=milestone_id,
            title=title,
            description=description,
            timestamp=datetime.datetime.now(),
            memory_ids=memory_ids or [],
            emotional_context=emotional_context,
            completion_percentage=max(0.0, min(1.0, completion_percentage))
        )
        
        self.milestones.append(milestone)
        self.updated_timestamp = datetime.datetime.now()
        
        # Update associated memory IDs
        if memory_ids:
            self.associated_memory_ids.extend(memory_ids)
            self.associated_memory_ids = list(set(self.associated_memory_ids))
        
        logger.info(f"Added milestone '{title}' to arc '{self.name}'")
        return milestone
    
    def get_completion_percentage(self) -> float:
        """
        Calculate overall completion percentage based on milestones.
        
        Returns:
            Completion percentage (0.0 to 1.0)
        """
        if not self.milestones:
            return 0.0
        
        total_percentage = sum(m.completion_percentage for m in self.milestones)
        return min(1.0, total_percentage / len(self.milestones))
    
    def update_status(self, new_status: ArcStatus):
        """Update the arc status."""
        self.status = new_status
        self.updated_timestamp = datetime.datetime.now()
        logger.info(f"Updated arc '{self.name}' status to {new_status.value}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['arc_type'] = self.arc_type.value
        data['status'] = self.status.value
        data['created_timestamp'] = self.created_timestamp.isoformat()
        data['updated_timestamp'] = self.updated_timestamp.isoformat()
        if self.target_completion:
            data['target_completion'] = self.target_completion.isoformat()
        data['milestones'] = [m.to_dict() for m in self.milestones]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterArc':
        """Create from dictionary."""
        data['arc_type'] = ArcType(data['arc_type'])
        data['status'] = ArcStatus(data['status'])
        data['created_timestamp'] = datetime.datetime.fromisoformat(data['created_timestamp'])
        data['updated_timestamp'] = datetime.datetime.fromisoformat(data['updated_timestamp'])
        if data.get('target_completion'):
            data['target_completion'] = datetime.datetime.fromisoformat(data['target_completion'])
        data['milestones'] = [ArcMilestone.from_dict(m) for m in data['milestones']]
        return cls(**data)


class CharacterArcManager:
    """
    Manages character arcs for narrative campaigns.
    
    Provides creation, tracking, and querying of character arcs with full
    memory association and progression tracking.
    """
    
    def __init__(self, storage_path: str = "character_arcs.jsonl"):
        """
        Initialize the character arc manager.
        
        Args:
            storage_path: Path to the JSONL file for persistent storage
        """
        self.storage_path = storage_path
        self.arcs: Dict[str, CharacterArc] = {}
        self._load_arcs()
    
    def _load_arcs(self):
        """Load existing character arcs from storage."""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        arc = CharacterArc.from_dict(data)
                        self.arcs[arc.arc_id] = arc
            logger.info(f"Loaded {len(self.arcs)} character arcs")
        except FileNotFoundError:
            logger.info("No existing character arcs found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading character arcs: {e}")
    
    def _save_arc(self, arc: CharacterArc):
        """Save a single arc to persistent storage."""
        try:
            with open(self.storage_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(arc.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error saving character arc: {e}")
            raise
    
    def create_arc(
        self,
        character_id: str,
        campaign_id: str,
        name: str,
        arc_type: ArcType,
        description: str,
        target_completion: Optional[datetime.datetime] = None,
        tags: Optional[List[str]] = None,
        emotional_themes: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CharacterArc:
        """
        Create a new character arc.
        
        Args:
            character_id: ID of the character
            campaign_id: ID of the campaign
            name: Arc name
            arc_type: Type of arc
            description: Arc description
            target_completion: Optional target completion date
            tags: Optional tags
            emotional_themes: Optional emotional themes
            metadata: Optional additional metadata
            
        Returns:
            The created CharacterArc
        """
        arc_id = f"arc_{character_id}_{campaign_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        arc = CharacterArc(
            arc_id=arc_id,
            character_id=character_id,
            campaign_id=campaign_id,
            name=name,
            arc_type=arc_type,
            status=ArcStatus.ACTIVE,
            description=description,
            created_timestamp=datetime.datetime.now(),
            updated_timestamp=datetime.datetime.now(),
            target_completion=target_completion,
            tags=tags or [],
            emotional_themes=emotional_themes or [],
            metadata=metadata or {}
        )
        
        self.arcs[arc_id] = arc
        self._save_arc(arc)
        
        logger.info(f"Created character arc: {name} for character {character_id}")
        return arc
    
    def get_arc(self, arc_id: str) -> Optional[CharacterArc]:
        """
        Get a specific character arc by ID.
        
        Args:
            arc_id: ID of the arc
            
        Returns:
            CharacterArc or None if not found
        """
        return self.arcs.get(arc_id)
    
    def get_arcs_by_character(
        self,
        character_id: str,
        campaign_id: Optional[str] = None,
        status: Optional[ArcStatus] = None
    ) -> List[CharacterArc]:
        """
        Get character arcs for a specific character.
        
        Args:
            character_id: ID of the character
            campaign_id: Optional campaign filter
            status: Optional status filter
            
        Returns:
            List of character arcs
        """
        arcs = [
            arc for arc in self.arcs.values()
            if arc.character_id == character_id
            and (campaign_id is None or arc.campaign_id == campaign_id)
            and (status is None or arc.status == status)
        ]
        
        # Sort by updated timestamp (newest first)
        arcs.sort(key=lambda x: x.updated_timestamp, reverse=True)
        
        return arcs
    
    def get_arcs_by_campaign(
        self,
        campaign_id: str,
        status: Optional[ArcStatus] = None
    ) -> List[CharacterArc]:
        """
        Get character arcs for a specific campaign.
        
        Args:
            campaign_id: ID of the campaign
            status: Optional status filter
            
        Returns:
            List of character arcs
        """
        arcs = [
            arc for arc in self.arcs.values()
            if arc.campaign_id == campaign_id
            and (status is None or arc.status == status)
        ]
        
        # Sort by updated timestamp (newest first)
        arcs.sort(key=lambda x: x.updated_timestamp, reverse=True)
        
        return arcs
    
    def get_arcs_by_type(
        self,
        arc_type: ArcType,
        campaign_id: Optional[str] = None
    ) -> List[CharacterArc]:
        """
        Get character arcs by type.
        
        Args:
            arc_type: Type of arc to filter by
            campaign_id: Optional campaign filter
            
        Returns:
            List of character arcs
        """
        arcs = [
            arc for arc in self.arcs.values()
            if arc.arc_type == arc_type
            and (campaign_id is None or arc.campaign_id == campaign_id)
        ]
        
        # Sort by updated timestamp (newest first)
        arcs.sort(key=lambda x: x.updated_timestamp, reverse=True)
        
        return arcs
    
    def add_milestone_to_arc(
        self,
        arc_id: str,
        title: str,
        description: str,
        memory_ids: Optional[List[str]] = None,
        emotional_context: Optional[str] = None,
        completion_percentage: float = 0.0
    ) -> Optional[ArcMilestone]:
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
            The created milestone or None if arc not found
        """
        arc = self.get_arc(arc_id)
        if not arc:
            logger.warning(f"Arc not found: {arc_id}")
            return None
        
        milestone = arc.add_milestone(
            title=title,
            description=description,
            memory_ids=memory_ids,
            emotional_context=emotional_context,
            completion_percentage=completion_percentage
        )
        
        # Update the arc in storage
        self._update_arc_storage(arc)
        
        return milestone
    
    def update_arc_status(self, arc_id: str, new_status: ArcStatus) -> bool:
        """
        Update the status of a character arc.
        
        Args:
            arc_id: ID of the arc
            new_status: New status
            
        Returns:
            True if updated, False if arc not found
        """
        arc = self.get_arc(arc_id)
        if not arc:
            logger.warning(f"Arc not found: {arc_id}")
            return False
        
        arc.update_status(new_status)
        self._update_arc_storage(arc)
        return True
    
    def _update_arc_storage(self, arc: CharacterArc):
        """Update arc in storage after modifications."""
        # Rebuild the file with the updated arc
        self._rebuild_storage()
    
    def _rebuild_storage(self):
        """Rebuild the storage file."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                for arc in self.arcs.values():
                    f.write(json.dumps(arc.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error rebuilding storage: {e}")
            raise
    
    def get_arc_summary(
        self,
        character_id: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a summary of character arcs.
        
        Args:
            character_id: Optional character filter
            campaign_id: Optional campaign filter
            
        Returns:
            Dictionary with arc summary statistics
        """
        filtered_arcs = [
            arc for arc in self.arcs.values()
            if (character_id is None or arc.character_id == character_id)
            and (campaign_id is None or arc.campaign_id == campaign_id)
        ]
        
        if not filtered_arcs:
            return {
                'total_arcs': 0,
                'arc_types': {},
                'status_counts': {},
                'characters': {},
                'campaigns': {},
                'average_completion': 0.0
            }
        
        # Count arc types
        arc_types = {}
        for arc in filtered_arcs:
            arc_type = arc.arc_type.value
            arc_types[arc_type] = arc_types.get(arc_type, 0) + 1
        
        # Count statuses
        status_counts = {}
        for arc in filtered_arcs:
            status = arc.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count characters
        characters = {}
        for arc in filtered_arcs:
            char_id = arc.character_id
            characters[char_id] = characters.get(char_id, 0) + 1
        
        # Count campaigns
        campaigns = {}
        for arc in filtered_arcs:
            camp_id = arc.campaign_id
            campaigns[camp_id] = campaigns.get(camp_id, 0) + 1
        
        # Average completion
        total_completion = sum(arc.get_completion_percentage() for arc in filtered_arcs)
        average_completion = total_completion / len(filtered_arcs)
        
        return {
            'total_arcs': len(filtered_arcs),
            'arc_types': arc_types,
            'status_counts': status_counts,
            'characters': characters,
            'campaigns': campaigns,
            'average_completion': average_completion
        }
    
    def search_arcs(
        self,
        query: str,
        character_id: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> List[CharacterArc]:
        """
        Search character arcs by name or description.
        
        Args:
            query: Search query
            character_id: Optional character filter
            campaign_id: Optional campaign filter
            
        Returns:
            List of matching character arcs
        """
        query_lower = query.lower()
        arcs = []
        
        for arc in self.arcs.values():
            if (character_id and arc.character_id != character_id):
                continue
            if (campaign_id and arc.campaign_id != campaign_id):
                continue
            
            # Search in name and description
            if (query_lower in arc.name.lower() or 
                query_lower in arc.description.lower()):
                arcs.append(arc)
        
        # Sort by updated timestamp (newest first)
        arcs.sort(key=lambda x: x.updated_timestamp, reverse=True)
        
        return arcs 