#!/usr/bin/env python3
"""
Test suite for LoreManager class functionality.

Tests all major methods including:
- add_lore_entry()
- get_lore_by_type()
- to_dict() output format
- search functionality
- tag management
- importance levels
"""

import unittest
import json
import tempfile
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lore_manager import LoreManager
from narrative_engine.memory.emotional_memory import EmotionType


class TestLoreManager(unittest.TestCase):
    """Test cases for LoreManager class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.campaign_id = "test-campaign"
        self.lore_file = os.path.join(self.test_dir, f"lore_{self.campaign_id}.jsonl")
        
        # Initialize LoreManager
        self.lore_manager = LoreManager(self.campaign_id, data_dir=self.test_dir)
        
        # Sample lore data for testing
        self.sample_lore = {
            "location": {
                "title": "The Ancient Forest",
                "content": "A mysterious forest filled with ancient trees and hidden secrets.",
                "lore_type": "location",
                "importance": 4,
                "tags": ["forest", "ancient", "mysterious"],
                "discovered": True,
                "discovery_date": datetime.now().isoformat()
            },
            "character": {
                "title": "Eldara the Wise",
                "content": "An ancient elf who guards the forest's secrets.",
                "lore_type": "character",
                "importance": 5,
                "tags": ["elf", "wise", "guardian"],
                "discovered": True,
                "discovery_date": datetime.now().isoformat()
            },
            "artifact": {
                "title": "The Crystal of Truth",
                "content": "A powerful artifact that reveals hidden truths.",
                "lore_type": "item",
                "importance": 5,
                "tags": ["crystal", "truth", "powerful"],
                "discovered": False,
                "discovery_date": None
            }
        }
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove test files
        if os.path.exists(self.lore_file):
            os.remove(self.lore_file)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def test_initialization(self):
        """Test LoreManager initialization."""
        self.assertEqual(self.lore_manager.campaign_id, self.campaign_id)
        self.assertEqual(self.lore_manager.data_dir, self.test_dir)
        self.assertEqual(len(self.lore_manager.lore_entries), 0)
    
    def test_add_lore_entry(self):
        """Test adding a lore entry."""
        lore_data = self.sample_lore["location"]
        lore_id = self.lore_manager.add_lore_entry(
            title=lore_data["title"],
            content=lore_data["content"],
            lore_type=lore_data["lore_type"],
            importance=lore_data["importance"],
            tags=lore_data["tags"],
            discovered=lore_data["discovered"]
        )
        
        # Verify entry was added
        self.assertIsNotNone(lore_id)
        self.assertEqual(len(self.lore_manager.lore_entries), 1)
        
        # Verify entry content
        entry = self.lore_manager.lore_entries[lore_id]
        self.assertEqual(entry["title"], lore_data["title"])
        self.assertEqual(entry["content"], lore_data["content"])
        self.assertEqual(entry["lore_type"], lore_data["lore_type"])
        self.assertEqual(entry["importance"], lore_data["importance"])
        self.assertEqual(entry["tags"], lore_data["tags"])
        self.assertEqual(entry["discovered"], lore_data["discovered"])
    
    def test_add_lore_entry_with_metadata(self):
        """Test adding a lore entry with additional metadata."""
        lore_data = self.sample_lore["character"]
        lore_id = self.lore_manager.add_lore_entry(
            title=lore_data["title"],
            content=lore_data["content"],
            lore_type=lore_data["lore_type"],
            importance=lore_data["importance"],
            tags=lore_data["tags"],
            discovered=lore_data["discovered"],
            metadata={
                "age": "ancient",
                "location": "forest",
                "role": "guardian"
            }
        )
        
        entry = self.lore_manager.lore_entries[lore_id]
        self.assertIn("metadata", entry)
        self.assertEqual(entry["metadata"]["age"], "ancient")
        self.assertEqual(entry["metadata"]["location"], "forest")
        self.assertEqual(entry["metadata"]["role"], "guardian")
    
    def test_get_lore_by_type(self):
        """Test retrieving lore entries by type."""
        # Add multiple entries of different types
        for lore_data in self.sample_lore.values():
            self.lore_manager.add_lore_entry(
                title=lore_data["title"],
                content=lore_data["content"],
                lore_type=lore_data["lore_type"],
                importance=lore_data["importance"],
                tags=lore_data["tags"],
                discovered=lore_data["discovered"]
            )
        
        # Test getting location entries
        location_entries = self.lore_manager.get_lore_by_type("location")
        self.assertEqual(len(location_entries), 1)
        self.assertEqual(location_entries[0]["title"], "The Ancient Forest")
        
        # Test getting character entries
        character_entries = self.lore_manager.get_lore_by_type("character")
        self.assertEqual(len(character_entries), 1)
        self.assertEqual(character_entries[0]["title"], "Eldara the Wise")
        
        # Test getting item entries
        item_entries = self.lore_manager.get_lore_by_type("item")
        self.assertEqual(len(item_entries), 1)
        self.assertEqual(item_entries[0]["title"], "The Crystal of Truth")
        
        # Test getting non-existent type
        empty_entries = self.lore_manager.get_lore_by_type("nonexistent")
        self.assertEqual(len(empty_entries), 0)
    
    def test_get_lore_by_tag(self):
        """Test retrieving lore entries by tag."""
        # Add entries
        for lore_data in self.sample_lore.values():
            self.lore_manager.add_lore_entry(
                title=lore_data["title"],
                content=lore_data["content"],
                lore_type=lore_data["lore_type"],
                importance=lore_data["importance"],
                tags=lore_data["tags"],
                discovered=lore_data["discovered"]
            )
        
        # Test getting entries by tag
        ancient_entries = self.lore_manager.get_lore_by_tag("ancient")
        self.assertEqual(len(ancient_entries), 2)  # forest and elf
        
        mysterious_entries = self.lore_manager.get_lore_by_tag("mysterious")
        self.assertEqual(len(mysterious_entries), 1)  # forest only
        
        # Test non-existent tag
        empty_entries = self.lore_manager.get_lore_by_tag("nonexistent")
        self.assertEqual(len(empty_entries), 0)
    
    def test_search_lore_entries(self):
        """Test searching lore entries by text."""
        # Add entries
        for lore_data in self.sample_lore.values():
            self.lore_manager.add_lore_entry(
                title=lore_data["title"],
                content=lore_data["content"],
                lore_type=lore_data["lore_type"],
                importance=lore_data["importance"],
                tags=lore_data["tags"],
                discovered=lore_data["discovered"]
            )
        
        # Test search by title
        forest_results = self.lore_manager.search_lore_entries("Forest")
        self.assertEqual(len(forest_results), 1)
        self.assertEqual(forest_results[0]["title"], "The Ancient Forest")
        
        # Test search by content
        secret_results = self.lore_manager.search_lore_entries("secrets")
        self.assertEqual(len(secret_results), 1)
        self.assertEqual(secret_results[0]["title"], "The Ancient Forest")
        
        # Test search by tag
        elf_results = self.lore_manager.search_lore_entries("elf")
        self.assertEqual(len(elf_results), 1)
        self.assertEqual(elf_results[0]["title"], "Eldara the Wise")
    
    def test_to_dict_output_format(self):
        """Test the to_dict() method output format."""
        # Add a lore entry
        lore_data = self.sample_lore["location"]
        lore_id = self.lore_manager.add_lore_entry(
            title=lore_data["title"],
            content=lore_data["content"],
            lore_type=lore_data["lore_type"],
            importance=lore_data["importance"],
            tags=lore_data["tags"],
            discovered=lore_data["discovered"]
        )
        
        # Get dictionary representation
        lore_dict = self.lore_manager.to_dict()
        
        # Verify structure
        self.assertIn("campaign_id", lore_dict)
        self.assertIn("lore_entries", lore_dict)
        self.assertEqual(lore_dict["campaign_id"], self.campaign_id)
        self.assertIsInstance(lore_dict["lore_entries"], dict)
        
        # Verify entry structure
        entry = lore_dict["lore_entries"][lore_id]
        required_fields = ["lore_id", "title", "content", "lore_type", "importance", 
                          "tags", "discovered", "created_date"]
        
        for field in required_fields:
            self.assertIn(field, entry)
        
        # Verify data types
        self.assertIsInstance(entry["lore_id"], str)
        self.assertIsInstance(entry["title"], str)
        self.assertIsInstance(entry["content"], str)
        self.assertIsInstance(entry["lore_type"], str)
        self.assertIsInstance(entry["importance"], int)
        self.assertIsInstance(entry["tags"], list)
        self.assertIsInstance(entry["discovered"], bool)
        self.assertIsInstance(entry["created_date"], str)
    
    def test_persistence(self):
        """Test that lore entries persist between instances."""
        # Add entries to first instance
        for lore_data in self.sample_lore.values():
            self.lore_manager.add_lore_entry(
                title=lore_data["title"],
                content=lore_data["content"],
                lore_type=lore_data["lore_type"],
                importance=lore_data["importance"],
                tags=lore_data["tags"],
                discovered=lore_data["discovered"]
            )
        
        # Create new instance (should load existing data)
        new_lore_manager = LoreManager(self.campaign_id, data_dir=self.test_dir)
        
        # Verify data was loaded
        self.assertEqual(len(new_lore_manager.lore_entries), 3)
        
        # Verify content
        for lore_data in self.sample_lore.values():
            found = False
            for entry in new_lore_manager.lore_entries.values():
                if entry["title"] == lore_data["title"]:
                    found = True
                    self.assertEqual(entry["content"], lore_data["content"])
                    self.assertEqual(entry["lore_type"], lore_data["lore_type"])
                    break
            self.assertTrue(found, f"Entry {lore_data['title']} not found")
    
    def test_importance_filtering(self):
        """Test filtering by importance level."""
        # Add entries with different importance levels
        for lore_data in self.sample_lore.values():
            self.lore_manager.add_lore_entry(
                title=lore_data["title"],
                content=lore_data["content"],
                lore_type=lore_data["lore_type"],
                importance=lore_data["importance"],
                tags=lore_data["tags"],
                discovered=lore_data["discovered"]
            )
        
        # Test filtering by minimum importance
        high_importance = self.lore_manager.get_lore_by_importance(min_importance=5)
        self.assertEqual(len(high_importance), 2)  # character and artifact
        
        medium_importance = self.lore_manager.get_lore_by_importance(min_importance=4)
        self.assertEqual(len(medium_importance), 3)  # all entries
        
        low_importance = self.lore_manager.get_lore_by_importance(min_importance=1)
        self.assertEqual(len(low_importance), 3)  # all entries
    
    def test_discovery_status(self):
        """Test filtering by discovery status."""
        # Add entries with different discovery status
        for lore_data in self.sample_lore.values():
            self.lore_manager.add_lore_entry(
                title=lore_data["title"],
                content=lore_data["content"],
                lore_type=lore_data["lore_type"],
                importance=lore_data["importance"],
                tags=lore_data["tags"],
                discovered=lore_data["discovered"]
            )
        
        # Test getting discovered entries
        discovered = self.lore_manager.get_discovered_lore()
        self.assertEqual(len(discovered), 2)  # location and character
        
        # Test getting undiscovered entries
        undiscovered = self.lore_manager.get_undiscovered_lore()
        self.assertEqual(len(undiscovered), 1)  # artifact
    
    def test_update_lore_entry(self):
        """Test updating existing lore entries."""
        # Add initial entry
        lore_data = self.sample_lore["location"]
        lore_id = self.lore_manager.add_lore_entry(
            title=lore_data["title"],
            content=lore_data["content"],
            lore_type=lore_data["lore_type"],
            importance=lore_data["importance"],
            tags=lore_data["tags"],
            discovered=lore_data["discovered"]
        )
        
        # Update the entry
        self.lore_manager.update_lore_entry(
            lore_id=lore_id,
            title="Updated Forest Title",
            content="Updated forest content with new information.",
            importance=5,
            tags=["forest", "updated", "new"],
            discovered=True
        )
        
        # Verify updates
        entry = self.lore_manager.lore_entries[lore_id]
        self.assertEqual(entry["title"], "Updated Forest Title")
        self.assertEqual(entry["content"], "Updated forest content with new information.")
        self.assertEqual(entry["importance"], 5)
        self.assertEqual(entry["tags"], ["forest", "updated", "new"])
        self.assertTrue(entry["discovered"])
    
    def test_delete_lore_entry(self):
        """Test deleting lore entries."""
        # Add entries
        for lore_data in self.sample_lore.values():
            self.lore_manager.add_lore_entry(
                title=lore_data["title"],
                content=lore_data["content"],
                lore_type=lore_data["lore_type"],
                importance=lore_data["importance"],
                tags=lore_data["tags"],
                discovered=lore_data["discovered"]
            )
        
        initial_count = len(self.lore_manager.lore_entries)
        
        # Delete an entry
        lore_id = list(self.lore_manager.lore_entries.keys())[0]
        self.lore_manager.delete_lore_entry(lore_id)
        
        # Verify deletion
        self.assertEqual(len(self.lore_manager.lore_entries), initial_count - 1)
        self.assertNotIn(lore_id, self.lore_manager.lore_entries)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 