"""
Development Journal System for DnD 5E Campaign Manager
=====================================================

Tracks ongoing development progress, ideas, and milestones for the DnD game project
"""

import json
import os
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

class JournalEntryType(Enum):
    """Types of development journal entries"""
    PROGRESS = "progress"
    IDEA = "idea"
    BUG_FIX = "bug_fix"
    FEATURE_REQUEST = "feature_request"
    MILESTONE = "milestone"
    REFACTOR = "refactor"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DESIGN_DECISION = "design_decision"
    NOTE = "note"

class Priority(Enum):
    """Priority levels for journal entries"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class JournalEntry:
    """Individual development journal entry"""
    id: str
    timestamp: datetime.datetime
    entry_type: JournalEntryType
    title: str
    content: str
    priority: Priority = Priority.MEDIUM
    tags: List[str] = None
    related_files: List[str] = None
    status: str = "open"  # open, in_progress, completed, blocked
    assignee: str = None
    estimated_hours: float = None
    actual_hours: float = None
    dependencies: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.related_files is None:
            self.related_files = []
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class DevelopmentMilestone:
    """Development milestone or sprint"""
    id: str
    title: str
    description: str
    target_date: datetime.date
    completed_date: Optional[datetime.date] = None
    entry_ids: List[str] = None
    status: str = "planned"  # planned, in_progress, completed, delayed
    
    def __post_init__(self):
        if self.entry_ids is None:
            self.entry_ids = []

class DevelopmentJournal:
    """Manages development journal entries and milestones"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.journal_dir = self.project_root / "development_journal"
        self.journal_dir.mkdir(exist_ok=True)
        
        self.entries_file = self.journal_dir / "entries.json"
        self.milestones_file = self.journal_dir / "milestones.json"
        self.settings_file = self.journal_dir / "settings.json"
        
        # Load existing data
        self.entries: Dict[str, JournalEntry] = {}
        self.milestones: Dict[str, DevelopmentMilestone] = {}
        self.settings: Dict[str, Any] = {}
        
        self._load_data()
    
    def _load_data(self):
        """Load existing journal data from files"""
        # Load entries
        if self.entries_file.exists():
            with open(self.entries_file, 'r') as f:
                entries_data = json.load(f)
                for entry_data in entries_data.values():
                    entry = JournalEntry(
                        id=entry_data['id'],
                        timestamp=datetime.datetime.fromisoformat(entry_data['timestamp']),
                        entry_type=JournalEntryType(entry_data['entry_type']),
                        title=entry_data['title'],
                        content=entry_data['content'],
                        priority=Priority(entry_data['priority']),
                        tags=entry_data.get('tags', []),
                        related_files=entry_data.get('related_files', []),
                        status=entry_data.get('status', 'open'),
                        assignee=entry_data.get('assignee'),
                        estimated_hours=entry_data.get('estimated_hours'),
                        actual_hours=entry_data.get('actual_hours'),
                        dependencies=entry_data.get('dependencies', []),
                        metadata=entry_data.get('metadata', {})
                    )
                    self.entries[entry.id] = entry
        
        # Load milestones
        if self.milestones_file.exists():
            with open(self.milestones_file, 'r') as f:
                milestones_data = json.load(f)
                for milestone_data in milestones_data.values():
                    milestone = DevelopmentMilestone(
                        id=milestone_data['id'],
                        title=milestone_data['title'],
                        description=milestone_data['description'],
                        target_date=datetime.date.fromisoformat(milestone_data['target_date']),
                        completed_date=datetime.date.fromisoformat(milestone_data['completed_date']) if milestone_data.get('completed_date') else None,
                        entry_ids=milestone_data.get('entry_ids', []),
                        status=milestone_data.get('status', 'planned')
                    )
                    self.milestones[milestone.id] = milestone
        
        # Load settings
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                'project_name': 'DnD 5E AI-Powered Campaign Manager',
                'version': '1.0.0',
                'created_date': datetime.date.today().isoformat(),
                'default_assignee': None,
                'auto_backup': True,
                'backup_frequency': 'daily'
            }
            self._save_settings()
    
    def _save_data(self):
        """Save journal data to files"""
        # Save entries
        entries_data = {}
        for entry in self.entries.values():
            entry_dict = asdict(entry)
            # Convert datetime to string for JSON serialization
            entry_dict['timestamp'] = entry.timestamp.isoformat()
            # Convert Enums to their values
            entry_dict['entry_type'] = entry.entry_type.value
            entry_dict['priority'] = entry.priority.value
            entries_data[entry.id] = entry_dict
        
        with open(self.entries_file, 'w') as f:
            json.dump(entries_data, f, indent=2)
        
        # Save milestones
        milestones_data = {}
        for milestone in self.milestones.values():
            milestone_dict = asdict(milestone)
            # Convert dates to strings for JSON serialization
            milestone_dict['target_date'] = milestone.target_date.isoformat()
            if milestone.completed_date:
                milestone_dict['completed_date'] = milestone.completed_date.isoformat()
            milestones_data[milestone.id] = milestone_dict
        
        with open(self.milestones_file, 'w') as f:
            json.dump(milestones_data, f, indent=2)
    
    def _save_settings(self):
        """Save settings to file"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def add_entry(self, entry_type: JournalEntryType, title: str, content: str, 
                  priority: Priority = Priority.MEDIUM, tags: List[str] = None,
                  related_files: List[str] = None, assignee: str = None,
                  estimated_hours: float = None) -> JournalEntry:
        """Add a new development journal entry"""
        entry_id = f"entry_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        entry = JournalEntry(
            id=entry_id,
            timestamp=datetime.datetime.now(),
            entry_type=entry_type,
            title=title,
            content=content,
            priority=priority,
            tags=tags or [],
            related_files=related_files or [],
            assignee=assignee or self.settings.get('default_assignee'),
            estimated_hours=estimated_hours
        )
        
        self.entries[entry_id] = entry
        self._save_data()
        
        return entry
    
    def update_entry(self, entry_id: str, **kwargs) -> Optional[JournalEntry]:
        """Update an existing journal entry"""
        if entry_id not in self.entries:
            return None
        
        entry = self.entries[entry_id]
        
        # Update allowed fields
        allowed_fields = ['title', 'content', 'priority', 'tags', 'related_files', 
                         'status', 'assignee', 'estimated_hours', 'actual_hours', 
                         'dependencies', 'metadata']
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(entry, field, value)
        
        self._save_data()
        return entry
    
    def get_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Get a specific journal entry"""
        return self.entries.get(entry_id)
    
    def search_entries(self, query: str = None, entry_type: JournalEntryType = None,
                      priority: Priority = None, status: str = None,
                      tags: List[str] = None, assignee: str = None) -> List[JournalEntry]:
        """Search journal entries with various filters"""
        results = []
        
        for entry in self.entries.values():
            # Text search
            if query and query.lower() not in entry.title.lower() and query.lower() not in entry.content.lower():
                continue
            
            # Type filter
            if entry_type and entry.entry_type != entry_type:
                continue
            
            # Priority filter
            if priority and entry.priority != priority:
                continue
            
            # Status filter
            if status and entry.status != status:
                continue
            
            # Tags filter
            if tags and not any(tag in entry.tags for tag in tags):
                continue
            
            # Assignee filter
            if assignee and entry.assignee != assignee:
                continue
            
            results.append(entry)
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results
    
    def add_milestone(self, title: str, description: str, target_date: datetime.date,
                     entry_ids: List[str] = None) -> DevelopmentMilestone:
        """Add a new development milestone"""
        milestone_id = f"milestone_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        milestone = DevelopmentMilestone(
            id=milestone_id,
            title=title,
            description=description,
            target_date=target_date,
            entry_ids=entry_ids or []
        )
        
        self.milestones[milestone_id] = milestone
        self._save_data()
        
        return milestone
    
    def update_milestone(self, milestone_id: str, **kwargs) -> Optional[DevelopmentMilestone]:
        """Update an existing milestone"""
        if milestone_id not in self.milestones:
            return None
        
        milestone = self.milestones[milestone_id]
        
        # Update allowed fields
        allowed_fields = ['title', 'description', 'target_date', 'completed_date', 
                         'entry_ids', 'status']
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(milestone, field, value)
        
        self._save_data()
        return milestone
    
    def get_milestone(self, milestone_id: str) -> Optional[DevelopmentMilestone]:
        """Get a specific milestone"""
        return self.milestones.get(milestone_id)
    
    def get_milestones(self, status: str = None) -> List[DevelopmentMilestone]:
        """Get all milestones, optionally filtered by status"""
        results = list(self.milestones.values())
        
        if status:
            results = [m for m in results if m.status == status]
        
        # Sort by target date
        results.sort(key=lambda x: x.target_date)
        return results
    
    def link_entry_to_milestone(self, entry_id: str, milestone_id: str) -> bool:
        """Link a journal entry to a milestone"""
        if entry_id not in self.entries or milestone_id not in self.milestones:
            return False
        
        milestone = self.milestones[milestone_id]
        if entry_id not in milestone.entry_ids:
            milestone.entry_ids.append(entry_id)
            self._save_data()
        
        return True
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Get a summary of the development project"""
        total_entries = len(self.entries)
        completed_entries = len([e for e in self.entries.values() if e.status == 'completed'])
        open_entries = len([e for e in self.entries.values() if e.status == 'open'])
        in_progress_entries = len([e for e in self.entries.values() if e.status == 'in_progress'])
        
        total_milestones = len(self.milestones)
        completed_milestones = len([m for m in self.milestones.values() if m.status == 'completed'])
        
        # Calculate total estimated and actual hours
        total_estimated = sum(e.estimated_hours or 0 for e in self.entries.values())
        total_actual = sum(e.actual_hours or 0 for e in self.entries.values())
        
        # Get recent activity
        recent_entries = sorted(self.entries.values(), key=lambda x: x.timestamp, reverse=True)[:5]
        
        return {
            'project_name': self.settings.get('project_name', 'Unknown'),
            'version': self.settings.get('version', 'Unknown'),
            'total_entries': total_entries,
            'completed_entries': completed_entries,
            'open_entries': open_entries,
            'in_progress_entries': in_progress_entries,
            'total_milestones': total_milestones,
            'completed_milestones': completed_milestones,
            'total_estimated_hours': total_estimated,
            'total_actual_hours': total_actual,
            'recent_entries': [{'id': e.id, 'title': e.title, 'timestamp': e.timestamp.isoformat()} for e in recent_entries]
        }
    
    def export_journal(self, filename: str = None) -> str:
        """Export the entire journal to a file"""
        if filename is None:
            filename = self.journal_dir / f"journal_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'settings': self.settings,
            'entries': [],
            'milestones': [],
            'export_date': datetime.datetime.now().isoformat()
        }
        # Convert entries
        for entry in self.entries.values():
            entry_dict = asdict(entry)
            entry_dict['timestamp'] = entry.timestamp.isoformat()
            entry_dict['entry_type'] = entry.entry_type.value
            entry_dict['priority'] = entry.priority.value
            export_data['entries'].append(entry_dict)
        # Convert milestones
        for milestone in self.milestones.values():
            milestone_dict = asdict(milestone)
            milestone_dict['target_date'] = milestone.target_date.isoformat()
            if milestone.completed_date:
                milestone_dict['completed_date'] = milestone.completed_date.isoformat()
            export_data['milestones'].append(milestone_dict)
        
        # Convert datetime objects to strings
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
        
        return str(filename)
    
    def backup_journal(self) -> str:
        """Create a backup of the journal"""
        backup_dir = self.journal_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        backup_filename = backup_dir / f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        return self.export_journal(str(backup_filename)) 