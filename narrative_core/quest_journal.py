"""
Quest Journal System for Narrative Engine

This module provides quest tracking and journaling functionality for the solo DnD game engine.
Supports active quest management, progress tracking, and completion logging.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional, Any
import json
import uuid


@dataclass
class QuestObjective:
    """Represents a single objective within a quest."""
    description: str
    completed: bool = False
    progress_notes: List[str] = None
    
    def __post_init__(self):
        if self.progress_notes is None:
            self.progress_notes = []
    
    def add_progress(self, note: str):
        """Add a progress note to this objective."""
        self.progress_notes.append(f"{datetime.now().isoformat()}: {note}")
    
    def complete(self):
        """Mark this objective as completed."""
        self.completed = True
        self.add_progress("Objective completed")


@dataclass
class Quest:
    """Represents a quest with objectives, rewards, and tracking."""
    id: str
    title: str
    description: str
    quest_giver: str
    objectives: List[QuestObjective]
    rewards: Dict[str, Any]
    difficulty: str = "Medium"
    quest_type: str = "Adventure"
    start_time: datetime = None
    completion_time: datetime = None
    status: str = "active"  # active, completed, failed
    progress_notes: List[str] = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.progress_notes is None:
            self.progress_notes = []
    
    def add_progress(self, note: str):
        """Add a progress note to the quest."""
        self.progress_notes.append(f"{datetime.now().isoformat()}: {note}")
    
    def is_completed(self) -> bool:
        """Check if all objectives are completed."""
        return all(obj.completed for obj in self.objectives)
    
    def get_completion_percentage(self) -> float:
        """Get the percentage of completed objectives."""
        if not self.objectives:
            return 0.0
        completed = sum(1 for obj in self.objectives if obj.completed)
        return (completed / len(self.objectives)) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert quest to dictionary for JSON serialization."""
        quest_dict = asdict(self)
        # Convert datetime objects to ISO strings
        if self.start_time:
            quest_dict['start_time'] = self.start_time.isoformat()
        if self.completion_time:
            quest_dict['completion_time'] = self.completion_time.isoformat()
        return quest_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quest':
        """Create quest from dictionary (JSON deserialization)."""
        # Convert ISO strings back to datetime objects
        if 'start_time' in data and data['start_time']:
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if 'completion_time' in data and data['completion_time']:
            data['completion_time'] = datetime.fromisoformat(data['completion_time'])
        
        # Reconstruct objectives
        if 'objectives' in data:
            objectives = []
            for obj_data in data['objectives']:
                objective = QuestObjective(
                    description=obj_data['description'],
                    completed=obj_data['completed'],
                    progress_notes=obj_data.get('progress_notes', [])
                )
                objectives.append(objective)
            data['objectives'] = objectives
        
        return cls(**data)


class QuestJournal:
    """Manages quest tracking and journaling for the narrative engine."""
    
    def __init__(self):
        self.active_quests: Dict[str, Quest] = {}
        self.completed_quests: Dict[str, Quest] = {}
        self.failed_quests: Dict[str, Quest] = {}
    
    def add_quest(self, quest: Quest) -> str:
        """Add a new quest to the active quests."""
        if not quest.id:
            quest.id = str(uuid.uuid4())
        
        self.active_quests[quest.id] = quest
        quest.add_progress("Quest accepted and added to journal")
        return quest.id
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID from any status."""
        return (self.active_quests.get(quest_id) or 
                self.completed_quests.get(quest_id) or 
                self.failed_quests.get(quest_id))
    
    def update_quest_progress(self, quest_id: str, progress: str) -> bool:
        """Add progress notes to an active quest."""
        quest = self.active_quests.get(quest_id)
        if not quest:
            return False
        
        quest.add_progress(progress)
        return True
    
    def update_objective_progress(self, quest_id: str, objective_index: int, progress: str) -> bool:
        """Add progress to a specific objective."""
        quest = self.active_quests.get(quest_id)
        if not quest or objective_index >= len(quest.objectives):
            return False
        
        quest.objectives[objective_index].add_progress(progress)
        return True
    
    def complete_objective(self, quest_id: str, objective_index: int) -> bool:
        """Mark a specific objective as completed."""
        quest = self.active_quests.get(quest_id)
        if not quest or objective_index >= len(quest.objectives):
            return False
        
        quest.objectives[objective_index].complete()
        quest.add_progress(f"Objective {objective_index + 1} completed")
        return True
    
    def complete_quest(self, quest_id: str, outcome: str = "Success") -> bool:
        """Complete a quest and move it to completed quests."""
        quest = self.active_quests.get(quest_id)
        if not quest:
            return False
        
        quest.status = "completed"
        quest.completion_time = datetime.now()
        quest.add_progress(f"Quest completed: {outcome}")
        
        # Move to completed quests
        del self.active_quests[quest_id]
        self.completed_quests[quest_id] = quest
        return True
    
    def fail_quest(self, quest_id: str, reason: str = "Failed") -> bool:
        """Fail a quest and move it to failed quests."""
        quest = self.active_quests.get(quest_id)
        if not quest:
            return False
        
        quest.status = "failed"
        quest.completion_time = datetime.now()
        quest.add_progress(f"Quest failed: {reason}")
        
        # Move to failed quests
        del self.active_quests[quest_id]
        self.failed_quests[quest_id] = quest
        return True
    
    def get_quest_status(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a specific quest."""
        quest = self.get_quest(quest_id)
        if not quest:
            return None
        
        return {
            'id': quest.id,
            'title': quest.title,
            'status': quest.status,
            'completion_percentage': quest.get_completion_percentage(),
            'objectives': [
                {
                    'description': obj.description,
                    'completed': obj.completed,
                    'progress_notes': obj.progress_notes[-3:]  # Last 3 notes
                }
                for obj in quest.objectives
            ],
            'rewards': quest.rewards,
            'start_time': quest.start_time.isoformat() if quest.start_time else None,
            'completion_time': quest.completion_time.isoformat() if quest.completion_time else None,
            'recent_progress': quest.progress_notes[-5:]  # Last 5 progress notes
        }
    
    def list_active_quests(self) -> List[Dict[str, Any]]:
        """Get summary of all active quests."""
        return [
            {
                'id': quest.id,
                'title': quest.title,
                'quest_giver': quest.quest_giver,
                'completion_percentage': quest.get_completion_percentage(),
                'objectives_count': len(quest.objectives),
                'completed_objectives': sum(1 for obj in quest.objectives if obj.completed),
                'start_time': quest.start_time.isoformat() if quest.start_time else None
            }
            for quest in self.active_quests.values()
        ]
    
    def list_completed_quests(self) -> List[Dict[str, Any]]:
        """Get summary of all completed quests."""
        return [
            {
                'id': quest.id,
                'title': quest.title,
                'quest_giver': quest.quest_giver,
                'rewards': quest.rewards,
                'completion_time': quest.completion_time.isoformat() if quest.completion_time else None
            }
            for quest in self.completed_quests.values()
        ]
    
    def list_failed_quests(self) -> List[Dict[str, Any]]:
        """Get summary of all failed quests."""
        return [
            {
                'id': quest.id,
                'title': quest.title,
                'quest_giver': quest.quest_giver,
                'completion_time': quest.completion_time.isoformat() if quest.completion_time else None
            }
            for quest in self.failed_quests.values()
        ]
    
    def get_quest_summary(self) -> Dict[str, Any]:
        """Get overall quest journal summary."""
        return {
            'active_count': len(self.active_quests),
            'completed_count': len(self.completed_quests),
            'failed_count': len(self.failed_quests),
            'total_quests': len(self.active_quests) + len(self.completed_quests) + len(self.failed_quests)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert journal to dictionary for JSON serialization."""
        return {
            'active_quests': {qid: quest.to_dict() for qid, quest in self.active_quests.items()},
            'completed_quests': {qid: quest.to_dict() for qid, quest in self.completed_quests.items()},
            'failed_quests': {qid: quest.to_dict() for qid, quest in self.failed_quests.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestJournal':
        """Create journal from dictionary (JSON deserialization)."""
        journal = cls()
        
        # Reconstruct active quests
        for qid, quest_data in data.get('active_quests', {}).items():
            journal.active_quests[qid] = Quest.from_dict(quest_data)
        
        # Reconstruct completed quests
        for qid, quest_data in data.get('completed_quests', {}).items():
            journal.completed_quests[qid] = Quest.from_dict(quest_data)
        
        # Reconstruct failed quests
        for qid, quest_data in data.get('failed_quests', {}).items():
            journal.failed_quests[qid] = Quest.from_dict(quest_data)
        
        return journal 