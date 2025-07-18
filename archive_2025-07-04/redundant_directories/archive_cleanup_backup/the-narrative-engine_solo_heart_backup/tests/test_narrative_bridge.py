#!/usr/bin/env python3
"""
Test suite for NarrativeBridge class functionality.

Tests all major methods including:
- NarrativeBridge initialization
- get_lore_panel_data()
- create_lore_entry()
- get_diagnostic_report()
- Integration with other systems
"""

import unittest
import json
import tempfile
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from narrative_bridge import NarrativeBridge
from narrative_engine.memory.emotional_memory import EmotionType
from narrative_engine.journaling.player_journal import JournalEntryType
from narrative_engine.narrative_structure.character_arcs import ArcType, ArcStatus
from narrative_engine.narrative_structure.plot_threads import ThreadType, ThreadStatus


class TestNarrativeBridge(unittest.TestCase):
    """Test cases for NarrativeBridge class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.campaign_id = "test-bridge-campaign"
        
        # Initialize NarrativeBridge
        self.bridge = NarrativeBridge(self.campaign_id, data_dir=self.test_dir)
        
        # Sample data for testing
        self.sample_lore = {
            "title": "The Mysterious Cave",
            "content": "A dark cave that seems to whisper ancient secrets.",
            "lore_type": "location",
            "importance": 4,
            "tags": ["cave", "mysterious", "ancient"],
            "discovered": True
        }
        
        self.sample_memory = {
            "content": "You discover a mysterious cave entrance.",
            "memory_type": "discovery",
            "metadata": {"location": "forest", "phenomenon": "cave"},
            "tags": ["discovery", "cave", "mystery"],
            "primary_emotion": EmotionType.WONDER,
            "emotional_intensity": 0.8
        }
    
    def tearDown(self):
        """Clean up after each test."""
        # Clean up test directory
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test NarrativeBridge initialization."""
        self.assertEqual(self.bridge.campaign_id, self.campaign_id)
        self.assertIsNotNone(self.bridge.lore_manager)
        self.assertIsNotNone(self.bridge.memory_system)
        self.assertIsNotNone(self.bridge.emotional_memory)
        self.assertIsNotNone(self.bridge.character_arcs)
        self.assertIsNotNone(self.bridge.plot_threads)
        self.assertIsNotNone(self.bridge.orchestrator)
    
    def test_create_lore_entry(self):
        """Test creating a lore entry through the bridge."""
        lore_id = self.bridge.create_lore_entry(
            title=self.sample_lore["title"],
            content=self.sample_lore["content"],
            lore_type=self.sample_lore["lore_type"],
            importance=self.sample_lore["importance"],
            tags=self.sample_lore["tags"],
            discovered=self.sample_lore["discovered"]
        )
        
        # Verify entry was created
        self.assertIsNotNone(lore_id)
        
        # Verify entry exists in lore manager
        lore_entries = self.bridge.lore_manager.lore_entries
        self.assertIn(lore_id, lore_entries)
        
        entry = lore_entries[lore_id]
        self.assertEqual(entry["title"], self.sample_lore["title"])
        self.assertEqual(entry["content"], self.sample_lore["content"])
        self.assertEqual(entry["lore_type"], self.sample_lore["lore_type"])
        self.assertEqual(entry["importance"], self.sample_lore["importance"])
        self.assertEqual(entry["tags"], self.sample_lore["tags"])
        self.assertEqual(entry["discovered"], self.sample_lore["discovered"])
    
    def test_get_lore_panel_data(self):
        """Test getting lore panel data."""
        # Create multiple lore entries
        lore_entries = [
            {
                "title": "The Ancient Forest",
                "content": "A mysterious forest filled with ancient trees.",
                "lore_type": "location",
                "importance": 4,
                "tags": ["forest", "ancient"],
                "discovered": True
            },
            {
                "title": "Eldara the Wise",
                "content": "An ancient elf who guards the forest.",
                "lore_type": "character",
                "importance": 5,
                "tags": ["elf", "wise"],
                "discovered": True
            },
            {
                "title": "The Crystal of Truth",
                "content": "A powerful artifact that reveals hidden truths.",
                "lore_type": "item",
                "importance": 5,
                "tags": ["crystal", "truth"],
                "discovered": False
            }
        ]
        
        for lore_data in lore_entries:
            self.bridge.create_lore_entry(**lore_data)
        
        # Get lore panel data
        panel_data = self.bridge.get_lore_panel_data()
        
        # Verify structure
        self.assertIn("summary", panel_data)
        self.assertIn("entries", panel_data)
        self.assertIn("types", panel_data)
        self.assertIn("importance_levels", panel_data)
        
        # Verify summary
        summary = panel_data["summary"]
        self.assertEqual(summary["total_entries"], 3)
        self.assertEqual(summary["discovered_entries"], 2)
        self.assertEqual(summary["undiscovered_entries"], 1)
        self.assertEqual(summary["average_importance"], 4.67)  # (4+5+5)/3
        
        # Verify entries
        entries = panel_data["entries"]
        self.assertEqual(len(entries), 3)
        
        # Verify types
        types = panel_data["types"]
        self.assertEqual(types["location"], 1)
        self.assertEqual(types["character"], 1)
        self.assertEqual(types["item"], 1)
        
        # Verify importance levels
        importance = panel_data["importance_levels"]
        self.assertEqual(importance["4"], 1)
        self.assertEqual(importance["5"], 2)
    
    def test_get_lore_panel_data_with_filters(self):
        """Test getting lore panel data with filters."""
        # Create lore entries
        lore_entries = [
            {
                "title": "The Ancient Forest",
                "content": "A mysterious forest filled with ancient trees.",
                "lore_type": "location",
                "importance": 4,
                "tags": ["forest", "ancient"],
                "discovered": True
            },
            {
                "title": "Eldara the Wise",
                "content": "An ancient elf who guards the forest.",
                "lore_type": "character",
                "importance": 5,
                "tags": ["elf", "wise"],
                "discovered": True
            }
        ]
        
        for lore_data in lore_entries:
            self.bridge.create_lore_entry(**lore_data)
        
        # Test filtering by type
        location_data = self.bridge.get_lore_panel_data(lore_type="location")
        self.assertEqual(len(location_data["entries"]), 1)
        self.assertEqual(location_data["entries"][0]["title"], "The Ancient Forest")
        
        # Test filtering by importance
        high_importance_data = self.bridge.get_lore_panel_data(min_importance=5)
        self.assertEqual(len(high_importance_data["entries"]), 1)
        self.assertEqual(high_importance_data["entries"][0]["title"], "Eldara the Wise")
        
        # Test filtering by discovery status
        discovered_data = self.bridge.get_lore_panel_data(discovered_only=True)
        self.assertEqual(len(discovered_data["entries"]), 2)
    
    def test_get_diagnostic_report(self):
        """Test getting diagnostic report."""
        # Create some test data
        self.bridge.store_dnd_memory(**self.sample_memory)
        
        # Create character arc
        self.bridge.create_character_arc(
            character_id="player",
            name="The Hero's Journey",
            arc_type=ArcType.GROWTH,
            description="Your journey from ordinary to extraordinary.",
            tags=["hero", "growth"],
            emotional_themes=["determination", "courage"]
        )
        
        # Create plot thread
        self.bridge.create_plot_thread(
            name="The Mysterious Artifacts",
            thread_type=ThreadType.MYSTERY,
            description="Ancient artifacts have appeared in the world.",
            priority=8,
            assigned_characters=["player"],
            tags=["mystery", "artifacts"]
        )
        
        # Get diagnostic report
        report = self.bridge.get_diagnostic_report()
        
        # Verify structure
        self.assertIn("campaign_id", report)
        self.assertIn("total_actions", report)
        self.assertIn("total_conflicts", report)
        self.assertIn("resolved_conflicts", report)
        self.assertIn("unresolved_conflicts", report)
        self.assertIn("campaign_health_score", report)
        self.assertIn("narrative_coherence", report)
        self.assertIn("character_engagement", report)
        self.assertIn("dominant_emotions", report)
        self.assertIn("arc_progress_summary", report)
        self.assertIn("plot_thread_summary", report)
        self.assertIn("memory_summary", report)
        self.assertIn("lore_summary", report)
        
        # Verify data types
        self.assertIsInstance(report["total_actions"], int)
        self.assertIsInstance(report["total_conflicts"], int)
        self.assertIsInstance(report["resolved_conflicts"], int)
        self.assertIsInstance(report["unresolved_conflicts"], int)
        self.assertIsInstance(report["campaign_health_score"], float)
        self.assertIsInstance(report["narrative_coherence"], float)
        self.assertIsInstance(report["character_engagement"], float)
        self.assertIsInstance(report["dominant_emotions"], dict)
        self.assertIsInstance(report["arc_progress_summary"], dict)
        self.assertIsInstance(report["plot_thread_summary"], dict)
        self.assertIsInstance(report["memory_summary"], dict)
        self.assertIsInstance(report["lore_summary"], dict)
        
        # Verify campaign ID
        self.assertEqual(report["campaign_id"], self.campaign_id)
    
    def test_get_diagnostic_report_with_rich_data(self):
        """Test getting diagnostic report with rich test data."""
        # Create multiple memories with different emotions
        emotions = [EmotionType.JOY, EmotionType.FEAR, EmotionType.ANGER, EmotionType.CURIOSITY]
        for i, emotion in enumerate(emotions):
            self.bridge.store_dnd_memory(
                content=f"Memory {i+1} with {emotion.name}",
                memory_type="test",
                metadata={"test": True, "index": i},
                tags=["test", emotion.name.lower()],
                primary_emotion=emotion,
                emotional_intensity=0.5 + (i * 0.1)
            )
        
        # Create multiple character arcs
        arc_types = [ArcType.GROWTH, ArcType.REDEMPTION, ArcType.TRAGEDY]
        for i, arc_type in enumerate(arc_types):
            self.bridge.create_character_arc(
                character_id=f"character_{i}",
                name=f"Arc {i+1}",
                arc_type=arc_type,
                description=f"Test arc {i+1}",
                tags=["test", arc_type.name.lower()],
                emotional_themes=["test_emotion"]
            )
        
        # Create multiple plot threads
        thread_types = [ThreadType.MYSTERY, ThreadType.CONFLICT, ThreadType.QUEST]
        for i, thread_type in enumerate(thread_types):
            self.bridge.create_plot_thread(
                name=f"Thread {i+1}",
                thread_type=thread_type,
                description=f"Test thread {i+1}",
                priority=5 + i,
                assigned_characters=[f"character_{i}"],
                tags=["test", thread_type.name.lower()]
            )
        
        # Create lore entries
        lore_types = ["location", "character", "item", "event"]
        for i, lore_type in enumerate(lore_types):
            self.bridge.create_lore_entry(
                title=f"Lore {i+1}",
                content=f"Test lore {i+1}",
                lore_type=lore_type,
                importance=3 + i,
                tags=["test", lore_type],
                discovered=i % 2 == 0  # Alternate discovered status
            )
        
        # Get diagnostic report
        report = self.bridge.get_diagnostic_report()
        
        # Verify counts
        self.assertGreaterEqual(report["total_actions"], 4)  # At least our test memories
        self.assertGreaterEqual(len(report["dominant_emotions"]), 1)
        self.assertGreaterEqual(len(report["arc_progress_summary"]), 3)
        self.assertGreaterEqual(len(report["plot_thread_summary"]), 3)
        self.assertGreaterEqual(report["lore_summary"]["total_entries"], 4)
        
        # Verify health scores are between 0 and 1
        self.assertGreaterEqual(report["campaign_health_score"], 0.0)
        self.assertLessEqual(report["campaign_health_score"], 1.0)
        self.assertGreaterEqual(report["narrative_coherence"], 0.0)
        self.assertLessEqual(report["narrative_coherence"], 1.0)
        self.assertGreaterEqual(report["character_engagement"], 0.0)
        self.assertLessEqual(report["character_engagement"], 1.0)
    
    def test_integration_with_emotional_memory(self):
        """Test integration with emotional memory system."""
        # Store memory with emotion
        self.bridge.store_dnd_memory(**self.sample_memory)
        
        # Verify emotion was stored
        memories = self.bridge.recall_related_memories("cave", max_results=5)
        self.assertGreater(len(memories), 0)
        
        # Check if emotional context is present
        memory = memories[0]
        self.assertIn("emotional_context", memory)
        self.assertEqual(memory["emotional_context"]["primary_emotion"], "WONDER")
        self.assertEqual(memory["emotional_context"]["intensity"], 0.8)
    
    def test_integration_with_character_arcs(self):
        """Test integration with character arcs system."""
        # Create character arc
        arc_id = self.bridge.create_character_arc(
            character_id="player",
            name="The Hero's Journey",
            arc_type=ArcType.GROWTH,
            description="Your journey from ordinary to extraordinary.",
            tags=["hero", "growth"],
            emotional_themes=["determination", "courage"]
        )
        
        # Verify arc was created
        self.assertIsNotNone(arc_id)
        
        # Get character arcs
        arcs = self.bridge.get_character_arcs("player")
        self.assertGreater(len(arcs), 0)
        
        # Verify arc content
        arc = arcs[0]
        self.assertEqual(arc["title"], "The Hero's Journey")
        self.assertEqual(arc["arc_type"], "GROWTH")
        self.assertEqual(arc["status"], "ACTIVE")
    
    def test_integration_with_plot_threads(self):
        """Test integration with plot threads system."""
        # Create plot thread
        thread_id = self.bridge.create_plot_thread(
            name="The Mysterious Artifacts",
            thread_type=ThreadType.MYSTERY,
            description="Ancient artifacts have appeared in the world.",
            priority=8,
            assigned_characters=["player"],
            tags=["mystery", "artifacts"]
        )
        
        # Verify thread was created
        self.assertIsNotNone(thread_id)
        
        # Get plot threads
        threads = self.bridge.get_plot_threads()
        self.assertGreater(len(threads), 0)
        
        # Verify thread content
        thread = threads[0]
        self.assertEqual(thread["name"], "The Mysterious Artifacts")
        self.assertEqual(thread["thread_type"], "MYSTERY")
        self.assertEqual(thread["status"], "ACTIVE")
        self.assertEqual(thread["priority"], 8)
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test creating lore entry with invalid data
        with self.assertRaises(Exception):
            self.bridge.create_lore_entry(
                title="",  # Empty title should cause error
                content="Test content",
                lore_type="invalid_type",  # Invalid type
                importance=10,  # Invalid importance
                tags="not_a_list",  # Invalid tags format
                discovered="not_boolean"  # Invalid discovered format
            )
        
        # Test getting diagnostic report with no data
        empty_bridge = NarrativeBridge("empty-campaign", data_dir=self.test_dir)
        report = empty_bridge.get_diagnostic_report()
        
        # Should return valid report with zero values
        self.assertEqual(report["total_actions"], 0)
        self.assertEqual(report["total_conflicts"], 0)
        self.assertEqual(report["resolved_conflicts"], 0)
        self.assertEqual(report["unresolved_conflicts"], 0)
    
    def test_data_persistence(self):
        """Test that data persists between bridge instances."""
        # Create data with first bridge
        self.bridge.create_lore_entry(**self.sample_lore)
        self.bridge.store_dnd_memory(**self.sample_memory)
        
        # Create new bridge instance
        new_bridge = NarrativeBridge(self.campaign_id, data_dir=self.test_dir)
        
        # Verify data was loaded
        lore_entries = new_bridge.lore_manager.lore_entries
        self.assertGreater(len(lore_entries), 0)
        
        memories = new_bridge.recall_related_memories("cave", max_results=5)
        self.assertGreater(len(memories), 0)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 