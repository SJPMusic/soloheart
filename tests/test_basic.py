#!/usr/bin/env python3
"""
Basic Tests for DnD 5E AI-Powered Campaign Manager
==================================================

Simple tests to verify core functionality works correctly.
"""

import os
import sys
import tempfile
import shutil
import unittest
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from the narrative bridge instead of direct imports
from SoloHeart.narrative_bridge import (
    NarrativeBridge, DnDMemoryEntry, DnDNPCResponse,
    create_dnd_bridge, store_combat_memory, store_quest_memory
)
from narrative_engine.memory.layered_memory import LayeredMemorySystem
from narrative_engine.core.character_manager import CharacterManager, Character, Race, CharacterClass, AbilityScore
from narrative_engine.core.session_logger import SessionLogger, LogEntryType

class TestNarrativeBridge(unittest.TestCase):
    """Test the narrative bridge functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.campaign_name = "Test Campaign"
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_bridge_creation(self):
        """Test creating a narrative bridge"""
        try:
            bridge = create_dnd_bridge(campaign_id=self.campaign_name)
            
            self.assertIsInstance(bridge, NarrativeBridge)
            self.assertEqual(bridge.campaign_id, self.campaign_name)
            
        except Exception as e:
            self.fail(f"Failed to create narrative bridge: {e}")
    
    def test_memory_operations(self):
        """Test memory operations through the bridge"""
        bridge = create_dnd_bridge(campaign_id=self.campaign_name)
        
        # Store a test memory
        memory_entry = DnDMemoryEntry(
            content="Test memory content",
            memory_type="episodic",
            tags=["test"]
        )
        
        success = bridge.store_dnd_memory(memory_entry)
        self.assertTrue(success)
        
        # Recall memories
        memories = bridge.recall_related_memories(query="test", max_results=5)
        self.assertIsInstance(memories, list)

def run_tests():
    """Run all tests"""
    print("🧪 Running DnD Campaign Manager Tests...")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestNarrativeBridge))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(run_tests()) 