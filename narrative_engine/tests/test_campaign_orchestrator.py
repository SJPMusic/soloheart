"""
Unit tests for the Dynamic Campaign Orchestrator.

Tests the orchestrator's ability to analyze campaign state, generate events,
and manage orchestration decisions.
"""

import unittest
import tempfile
import os
import json
import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the parent directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.campaign_orchestrator import (
    DynamicCampaignOrchestrator,
    OrchestrationEvent,
    OrchestrationEventType,
    OrchestrationPriority,
    CampaignState
)


class TestOrchestrationEvent(unittest.TestCase):
    """Test the OrchestrationEvent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.event = OrchestrationEvent(
            event_id="test_event_001",
            event_type=OrchestrationEventType.QUEST_SUGGESTION,
            priority=OrchestrationPriority.HIGH,
            title="Test Quest",
            description="A test quest for the player",
            suggested_actions=["Investigate", "Ask around"],
            emotional_context=["curiosity", "determination"],
            related_arcs=["arc_001"],
            related_threads=["thread_001"],
            target_characters=["player"],
            location_hint="the town square",
            timing_hint="soon",
            prerequisites=[],
            consequences=["Character growth", "Plot advancement"],
            metadata={"test": True}
        )
    
    def test_event_creation(self):
        """Test that events are created correctly."""
        self.assertEqual(self.event.event_id, "test_event_001")
        self.assertEqual(self.event.event_type, OrchestrationEventType.QUEST_SUGGESTION)
        self.assertEqual(self.event.priority, OrchestrationPriority.HIGH)
        self.assertEqual(self.event.title, "Test Quest")
        self.assertEqual(len(self.event.suggested_actions), 2)
        self.assertEqual(len(self.event.emotional_context), 2)
    
    def test_event_serialization(self):
        """Test event serialization to dictionary."""
        data = self.event.to_dict()
        
        self.assertEqual(data['event_id'], "test_event_001")
        self.assertEqual(data['event_type'], "quest_suggestion")
        self.assertEqual(data['priority'], "high")
        self.assertEqual(data['title'], "Test Quest")
        self.assertIn('created_timestamp', data)
        self.assertIsNone(data['executed_timestamp'])
    
    def test_event_deserialization(self):
        """Test event deserialization from dictionary."""
        data = self.event.to_dict()
        new_event = OrchestrationEvent.from_dict(data)
        
        self.assertEqual(new_event.event_id, self.event.event_id)
        self.assertEqual(new_event.event_type, self.event.event_type)
        self.assertEqual(new_event.priority, self.event.priority)
        self.assertEqual(new_event.title, self.event.title)
        self.assertEqual(new_event.suggested_actions, self.event.suggested_actions)
    
    def test_event_execution(self):
        """Test marking an event as executed."""
        self.assertIsNone(self.event.executed_timestamp)
        
        execution_time = datetime.datetime.now()
        self.event.executed_timestamp = execution_time
        
        self.assertEqual(self.event.executed_timestamp, execution_time)
        
        data = self.event.to_dict()
        self.assertIn('executed_timestamp', data)


class TestCampaignState(unittest.TestCase):
    """Test the CampaignState class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state = CampaignState(
            campaign_id="test_campaign",
            active_arcs=[
                {
                    'arc_id': 'arc_001',
                    'name': 'Test Arc',
                    'completion_percentage': 0.3
                }
            ],
            open_threads=[
                {
                    'thread_id': 'thread_001',
                    'name': 'Test Thread',
                    'priority': 7
                }
            ],
            recent_memories=[
                {
                    'content': 'Test memory',
                    'emotional_context': ['curiosity']
                }
            ],
            emotional_context={'curiosity': 0.6, 'determination': 0.4},
            character_locations={'player': 'town square'},
            world_events=[],
            session_count=1
        )
    
    def test_state_creation(self):
        """Test that campaign state is created correctly."""
        self.assertEqual(self.state.campaign_id, "test_campaign")
        self.assertEqual(len(self.state.active_arcs), 1)
        self.assertEqual(len(self.state.open_threads), 1)
        self.assertEqual(len(self.state.recent_memories), 1)
        self.assertEqual(len(self.state.emotional_context), 2)
        self.assertEqual(self.state.session_count, 1)
    
    def test_state_serialization(self):
        """Test state serialization to dictionary."""
        data = self.state.to_dict()
        
        self.assertEqual(data['campaign_id'], "test_campaign")
        self.assertEqual(len(data['active_arcs']), 1)
        self.assertEqual(len(data['open_threads']), 1)
        self.assertEqual(len(data['recent_memories']), 1)
        self.assertIn('timestamp', data)


class TestDynamicCampaignOrchestrator(unittest.TestCase):
    """Test the DynamicCampaignOrchestrator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
        self.temp_file.close()
        
        self.orchestrator = DynamicCampaignOrchestrator(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_file.name)
        except OSError:
            pass
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        self.assertIsNotNone(self.orchestrator)
        self.assertEqual(self.orchestrator.storage_path, self.temp_file.name)
        self.assertIsInstance(self.orchestrator.events, dict)
        self.assertIsInstance(self.orchestrator.decision_history, list)
        self.assertIn('arc_completion', self.orchestrator.weights)
        self.assertIn('quest_suggestion', self.orchestrator.event_templates)
    
    def test_analyze_emotional_context(self):
        """Test emotional context analysis."""
        memories = [
            {
                'emotional_context': ['curiosity', 'wonder'],
                'content': 'Test memory 1'
            },
            {
                'emotional_context': ['curiosity', 'determination'],
                'content': 'Test memory 2'
            },
            {
                'emotional_context': [],
                'content': 'Test memory 3'
            }
        ]
        
        emotional_context = self.orchestrator._analyze_emotional_context(memories)
        
        self.assertIn('curiosity', emotional_context)
        self.assertIn('wonder', emotional_context)
        self.assertIn('determination', emotional_context)
        self.assertGreater(emotional_context['curiosity'], emotional_context['wonder'])
    
    def test_calculate_priorities(self):
        """Test priority calculation."""
        state = CampaignState(
            campaign_id="test",
            active_arcs=[
                {
                    'arc_id': 'arc_001',
                    'name': 'Test Arc',
                    'completion_percentage': 0.2
                },
                {
                    'arc_id': 'arc_002',
                    'name': 'Test Arc 2',
                    'completion_percentage': 0.8
                }
            ],
            open_threads=[
                {
                    'thread_id': 'thread_001',
                    'name': 'Test Thread',
                    'priority': 9
                },
                {
                    'thread_id': 'thread_002',
                    'name': 'Test Thread 2',
                    'priority': 3
                }
            ],
            recent_memories=[],
            emotional_context={'curiosity': 0.7},
            character_locations={},
            world_events=[],
            session_count=1
        )
        
        priorities = self.orchestrator._calculate_priorities(state)
        
        # Should have priorities for arcs and threads
        self.assertGreater(len(priorities), 0)
        
        # Check that critical priorities come first
        critical_priorities = [p for p in priorities if p['priority'] == OrchestrationPriority.CRITICAL]
        high_priorities = [p for p in priorities if p['priority'] == OrchestrationPriority.HIGH]
        
        # Critical priorities should be for high-completion arcs and high-priority threads
        self.assertGreater(len(critical_priorities), 0)
    
    def test_generate_orchestration_events(self):
        """Test orchestration event generation."""
        state = CampaignState(
            campaign_id="test",
            active_arcs=[
                {
                    'arc_id': 'arc_001',
                    'name': 'Hero\'s Journey',
                    'completion_percentage': 0.3
                }
            ],
            open_threads=[
                {
                    'thread_id': 'thread_001',
                    'name': 'Mystery Quest',
                    'priority': 8
                }
            ],
            recent_memories=[],
            emotional_context={'determination': 0.6},
            character_locations={'player': 'town'},
            world_events=[],
            session_count=1
        )
        
        events = self.orchestrator.generate_orchestration_events(state, max_events=2)
        
        self.assertLessEqual(len(events), 2)
        
        if events:
            event = events[0]
            self.assertIsInstance(event, OrchestrationEvent)
            self.assertIsNotNone(event.event_id)
            self.assertIsNotNone(event.title)
            self.assertIsNotNone(event.description)
            self.assertGreater(len(event.suggested_actions), 0)
    
    def test_get_pending_events(self):
        """Test getting pending events."""
        # Create a test event
        event = OrchestrationEvent(
            event_id="test_pending",
            event_type=OrchestrationEventType.QUEST_SUGGESTION,
            priority=OrchestrationPriority.HIGH,
            title="Test Pending Event",
            description="A test pending event",
            suggested_actions=["Test action"],
            emotional_context=["curiosity"]
        )
        
        self.orchestrator.events[event.event_id] = event
        
        # Get pending events
        pending = self.orchestrator.get_pending_events()
        
        self.assertIn(event, pending)
        
        # Test filtering by priority
        high_priority = self.orchestrator.get_pending_events(priority=OrchestrationPriority.HIGH)
        self.assertIn(event, high_priority)
        
        low_priority = self.orchestrator.get_pending_events(priority=OrchestrationPriority.LOW)
        self.assertNotIn(event, low_priority)
        
        # Test filtering by event type
        quest_events = self.orchestrator.get_pending_events(event_type=OrchestrationEventType.QUEST_SUGGESTION)
        self.assertIn(event, quest_events)
        
        encounter_events = self.orchestrator.get_pending_events(event_type=OrchestrationEventType.ENCOUNTER_TRIGGER)
        self.assertNotIn(event, encounter_events)
    
    def test_execute_event(self):
        """Test event execution."""
        # Create a test event
        event = OrchestrationEvent(
            event_id="test_execute",
            event_type=OrchestrationEventType.QUEST_SUGGESTION,
            priority=OrchestrationPriority.HIGH,
            title="Test Execute Event",
            description="A test event to execute",
            suggested_actions=["Test action"],
            emotional_context=["determination"]
        )
        
        self.orchestrator.events[event.event_id] = event
        
        # Mock narrative bridge
        mock_bridge = Mock()
        
        # Execute the event
        success = self.orchestrator.execute_event(
            event.event_id,
            mock_bridge,
            "Test execution notes"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(event.executed_timestamp)
        
        # Check that store_dnd_memory was called
        mock_bridge.store_dnd_memory.assert_called_once()
        
        # Check decision history
        self.assertEqual(len(self.orchestrator.decision_history), 1)
        decision = self.orchestrator.decision_history[0]
        self.assertEqual(decision['event_id'], event.event_id)
        self.assertEqual(decision['notes'], "Test execution notes")
    
    def test_execute_nonexistent_event(self):
        """Test executing a non-existent event."""
        mock_bridge = Mock()
        
        success = self.orchestrator.execute_event("nonexistent", mock_bridge)
        
        self.assertFalse(success)
        mock_bridge.store_dnd_memory.assert_not_called()
    
    def test_get_orchestration_summary(self):
        """Test getting orchestration summary."""
        # Create some test events
        events = [
            OrchestrationEvent(
                event_id="test_1",
                event_type=OrchestrationEventType.QUEST_SUGGESTION,
                priority=OrchestrationPriority.HIGH,
                title="Test 1",
                description="Test 1",
                suggested_actions=["Action 1"],
                emotional_context=["curiosity"]
            ),
            OrchestrationEvent(
                event_id="test_2",
                event_type=OrchestrationEventType.ENCOUNTER_TRIGGER,
                priority=OrchestrationPriority.MEDIUM,
                title="Test 2",
                description="Test 2",
                suggested_actions=["Action 2"],
                emotional_context=["surprise"]
            )
        ]
        
        # Mark one as executed
        events[1].executed_timestamp = datetime.datetime.now()
        
        for event in events:
            self.orchestrator.events[event.event_id] = event
        
        summary = self.orchestrator.get_orchestration_summary()
        
        self.assertEqual(summary['total_events'], 2)
        self.assertEqual(summary['pending_events'], 1)
        self.assertEqual(summary['executed_events'], 1)
        self.assertEqual(summary['decision_history_count'], 0)
        
        self.assertIn('quest_suggestion', summary['event_types'])
        self.assertIn('encounter_trigger', summary['event_types'])
        self.assertIn('high', summary['priorities'])
        self.assertIn('medium', summary['priorities'])
    
    def test_template_filling(self):
        """Test template filling functionality."""
        template = "While traveling to {location}, {character} encounters someone connected to {related_arc}."
        data = {
            'location': 'the forest',
            'name': 'Hero\'s Journey'
        }
        
        # Mock campaign state
        mock_state = Mock()
        
        filled = self.orchestrator._fill_template(template, data, mock_state)
        
        self.assertIn('the forest', filled)
        self.assertIn('the player', filled)  # Default character replacement
        self.assertIn('Hero\'s Journey', filled)
    
    def test_event_storage_persistence(self):
        """Test that events are persisted to storage."""
        # Create a test event
        event = OrchestrationEvent(
            event_id="test_persist",
            event_type=OrchestrationEventType.QUEST_SUGGESTION,
            priority=OrchestrationPriority.HIGH,
            title="Test Persist Event",
            description="A test event for persistence",
            suggested_actions=["Test action"],
            emotional_context=["curiosity"]
        )
        
        # Save the event
        self.orchestrator._save_event(event)
        
        # Create a new orchestrator instance to test loading
        new_orchestrator = DynamicCampaignOrchestrator(self.temp_file.name)
        
        # Check that the event was loaded
        self.assertIn(event.event_id, new_orchestrator.events)
        loaded_event = new_orchestrator.events[event.event_id]
        self.assertEqual(loaded_event.title, event.title)
        self.assertEqual(loaded_event.description, event.description)


if __name__ == '__main__':
    unittest.main() 