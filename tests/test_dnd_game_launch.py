"""
Test DnD Game Launch and Integration

This test file validates that the DnD game can launch successfully
and interact with the modularized Narrative Engine through the bridge.
"""

import unittest
import tempfile
import shutil
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dnd_game.narrative_bridge import (
    NarrativeBridge, DnDMemoryEntry, DnDNPCResponse,
    create_dnd_bridge, store_combat_memory, store_quest_memory
)
from dnd_game.enhanced_campaign_manager import EnhancedCampaignManager


class TestDnDGameLaunch(unittest.TestCase):
    """Test the DnD game launch and basic functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.campaign_name = "Test Campaign"
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_narrative_bridge_creation(self):
        """Test that the narrative bridge can be created successfully"""
        try:
            bridge = create_dnd_bridge(
                campaign_id=self.campaign_name,
                api_key=None  # Use environment variable
            )
            
            self.assertIsInstance(bridge, NarrativeBridge)
            self.assertEqual(bridge.campaign_id, self.campaign_name)
            
            # Test that all core components are initialized
            self.assertIsNotNone(bridge.memory_system)
            self.assertIsNotNone(bridge.character_manager)
            self.assertIsNotNone(bridge.ai_dm_engine)
            self.assertIsNotNone(bridge.campaign_manager)
            self.assertIsNotNone(bridge.npc_behavior_engine)
            self.assertIsNotNone(bridge.world_simulator)
            
        except Exception as e:
            self.fail(f"Failed to create narrative bridge: {e}")
    
    def test_memory_storage_and_recall(self):
        """Test memory storage and recall through the bridge"""
        bridge = create_dnd_bridge(campaign_id=self.campaign_name)
        
        # Store a test memory
        memory_entry = DnDMemoryEntry(
            content="The party helped a wounded traveler in the forest",
            memory_type="episodic",
            location="Forest",
            emotional_context={"valence": 0.8, "arousal": 0.6, "dominance": 0.7},
            tags=["helping", "traveler", "forest"]
        )
        
        success = bridge.store_dnd_memory(memory_entry)
        self.assertTrue(success)
        
        # Recall the memory
        memories = bridge.recall_related_memories(
            query="traveler",
            max_results=5
        )
        
        self.assertIsInstance(memories, list)
        self.assertGreater(len(memories), 0)
        
        # Check that our memory is in the results
        found_memory = False
        for memory in memories:
            if "wounded traveler" in memory.get("content", ""):
                found_memory = True
                break
        
        self.assertTrue(found_memory, "Stored memory not found in recall results")
    
    def test_npc_response_generation(self):
        """Test NPC response generation through the bridge"""
        bridge = create_dnd_bridge(campaign_id=self.campaign_name)
        
        # Generate an NPC response
        npc_response = bridge.get_npc_response(
            npc_name="Eldrin",
            context="The player approaches Eldrin in the tavern",
            player_emotion={"valence": 0.7, "arousal": 0.4}
        )
        
        self.assertIsInstance(npc_response, DnDNPCResponse)
        self.assertEqual(npc_response.npc_name, "Eldrin")
        self.assertIsInstance(npc_response.text, str)
        self.assertGreater(len(npc_response.text), 0)
        self.assertIn(npc_response.emotional_tone, ["positive", "negative", "neutral"])
    
    def test_dm_narration_generation(self):
        """Test DM narration generation through the bridge"""
        bridge = create_dnd_bridge(campaign_id=self.campaign_name)
        
        # Generate DM narration
        narration = bridge.generate_dm_narration(
            situation="The party enters a mysterious cave",
            player_actions=["Player draws their sword", "Player lights a torch"],
            world_context={"location": "Cave", "time": "night"}
        )
        
        self.assertIsInstance(narration, str)
        self.assertGreater(len(narration), 0)
    
    def test_world_state_management(self):
        """Test world state management through the bridge"""
        bridge = create_dnd_bridge(campaign_id=self.campaign_name)
        
        # Update world state
        success = bridge.update_world_state(
            location="Tavern",
            changes={
                "atmosphere": "tense",
                "patrons": ["merchant", "guard", "mysterious_stranger"],
                "events": ["recent_brawl", "rumors_of_war"]
            }
        )
        
        self.assertTrue(success)
        
        # Get campaign summary
        summary = bridge.get_campaign_summary()
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary["campaign_id"], self.campaign_name)
    
    def test_campaign_save_and_load(self):
        """Test campaign state save and load functionality"""
        bridge = create_dnd_bridge(campaign_id=self.campaign_name)
        
        # Store some test data
        memory_entry = DnDMemoryEntry(
            content="Test memory for save/load",
            memory_type="episodic",
            tags=["test"]
        )
        bridge.store_dnd_memory(memory_entry)
        
        # Save campaign state
        save_file = os.path.join(self.test_dir, "test_campaign.json")
        success = bridge.save_campaign_state(save_file)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(save_file))
        
        # Create a new bridge and load the state
        new_bridge = create_dnd_bridge(campaign_id="New Campaign")
        success = new_bridge.load_campaign_state(save_file)
        self.assertTrue(success)
    
    def test_enhanced_campaign_manager_integration(self):
        """Test integration with the enhanced campaign manager"""
        try:
            campaign_manager = EnhancedCampaignManager(self.campaign_name)
            
            self.assertEqual(campaign_manager.campaign_name, self.campaign_name)
            self.assertIsNotNone(campaign_manager.campaign_settings)
            
            # Test session management
            session = campaign_manager.start_session("test_session")
            self.assertIsNotNone(session)
            self.assertEqual(session.session_id, "test_session")
            
            # End session
            summary = campaign_manager.end_session()
            self.assertIsNotNone(summary)
            
        except Exception as e:
            self.fail(f"Enhanced campaign manager test failed: {e}")
    
    def test_combat_memory_helper(self):
        """Test the combat memory helper function"""
        bridge = create_dnd_bridge(campaign_id=self.campaign_name)
        
        success = store_combat_memory(
            bridge=bridge,
            combat_description="The party fought three goblins in the forest",
            location="Forest",
            participants=["Player", "Goblin1", "Goblin2", "Goblin3"]
        )
        
        self.assertTrue(success)
    
    def test_quest_memory_helper(self):
        """Test the quest memory helper function"""
        bridge = create_dnd_bridge(campaign_id=self.campaign_name)
        
        success = store_quest_memory(
            bridge=bridge,
            quest_description="The party accepted a quest to find a lost artifact",
            quest_name="Lost Artifact Quest",
            location="Tavern"
        )
        
        self.assertTrue(success)
    
    @patch('dnd_game.narrative_bridge.NarrativeBridge')
    def test_bridge_error_handling(self, mock_bridge_class):
        """Test error handling in the bridge"""
        # Mock the bridge to raise an exception
        mock_bridge_class.side_effect = Exception("Test error")
        
        with self.assertRaises(Exception):
            create_dnd_bridge(campaign_id="test")


class TestDnDGameIntegration(unittest.TestCase):
    """Test full DnD game integration scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.campaign_name = "Integration Test Campaign"
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_complete_gameplay_scenario(self):
        """Test a complete gameplay scenario"""
        bridge = create_dnd_bridge(campaign_id=self.campaign_name)
        
        # 1. Start with DM narration
        narration = bridge.generate_dm_narration(
            situation="The party enters the village of Oakdale",
            player_actions=["Player walks into the village square"],
            world_context={"location": "Oakdale", "time": "morning"}
        )
        self.assertIsInstance(narration, str)
        self.assertGreater(len(narration), 0)
        
        # 2. Store the scene in memory
        scene_memory = DnDMemoryEntry(
            content=f"Scene: {narration}",
            memory_type="episodic",
            location="Oakdale",
            tags=["village", "arrival"]
        )
        success = bridge.store_dnd_memory(scene_memory)
        self.assertTrue(success)
        
        # 3. Generate NPC interaction
        npc_response = bridge.get_npc_response(
            npc_name="Village Elder",
            context="The village elder approaches the party",
            player_emotion={"valence": 0.6, "arousal": 0.3}
        )
        self.assertIsInstance(npc_response, DnDNPCResponse)
        
        # 4. Store the interaction
        interaction_memory = DnDMemoryEntry(
            content=f"NPC Interaction: {npc_response.text}",
            memory_type="episodic",
            location="Oakdale",
            tags=["npc", "dialogue", "village_elder"]
        )
        success = bridge.store_dnd_memory(interaction_memory)
        self.assertTrue(success)
        
        # 5. Recall relevant memories
        memories = bridge.recall_related_memories(
            query="village",
            max_results=5
        )
        self.assertIsInstance(memories, list)
        self.assertGreater(len(memories), 0)
        
        # 6. Get campaign summary
        summary = bridge.get_campaign_summary()
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary["campaign_id"], self.campaign_name)


def run_tests():
    """Run all DnD game tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestDnDGameLaunch))
    test_suite.addTest(unittest.makeSuite(TestDnDGameIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    if success:
        print("\n✅ All DnD game tests passed!")
    else:
        print("\n❌ Some DnD game tests failed!") 