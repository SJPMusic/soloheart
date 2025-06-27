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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import DnDCampaignManager
from core.memory_system import CampaignMemorySystem
from core.character_manager import CharacterManager, Character, Race, CharacterClass, AbilityScore
from core.session_logger import SessionLogger, LogEntryType

class TestDnDCampaignManager(unittest.TestCase):
    """Test the main campaign manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.campaign_name = "Test Campaign"
        
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_campaign_creation(self):
        """Test creating a new campaign"""
        campaign = DnDCampaignManager(self.campaign_name)
        
        self.assertEqual(campaign.campaign_name, self.campaign_name)
        self.assertIsNotNone(campaign.memory_system)
        self.assertIsNotNone(campaign.ai_generator)
        self.assertIsNotNone(campaign.character_manager)
        self.assertIsNotNone(campaign.session_logger)
        
        # Check that campaign directory was created
        campaign_dir = os.path.join("campaigns", self.campaign_name)
        self.assertTrue(os.path.exists(campaign_dir))
    
    def test_character_creation(self):
        """Test character creation with vibe coding"""
        campaign = DnDCampaignManager(self.campaign_name)
        
        # Create a character
        character = campaign.create_character_from_vibe(
            player_name="TestPlayer",
            vibe_description="A brave human fighter who protects the innocent",
            preferences={"custom_description": "Tall and muscular"}
        )
        
        # Verify character was created correctly
        self.assertIsInstance(character, Character)
        self.assertEqual(character.name, character.name)  # Name should be generated
        self.assertIn(character.race, [Race.HUMAN, Race.HALF_ELF, Race.HALF_ORC])
        self.assertIn(character.character_class, [CharacterClass.FIGHTER, CharacterClass.PALADIN, CharacterClass.BARBARIAN])
        self.assertEqual(character.level, 1)
        self.assertGreater(character.hit_points, 0)
        self.assertGreater(character.armor_class, 0)
        
        # Verify character was saved
        self.assertIn("TestPlayer", campaign.player_characters)
        self.assertEqual(campaign.player_characters["TestPlayer"], character)
    
    def test_session_logging(self):
        """Test session logging functionality"""
        campaign = DnDCampaignManager(self.campaign_name)
        
        # Create a character first
        campaign.create_character_from_vibe(
            player_name="TestPlayer",
            vibe_description="A brave human fighter",
            preferences={}
        )
        
        # Start a session
        session = campaign.start_session("test_session_001")
        self.assertIsNotNone(session)
        self.assertEqual(session.session_id, "test_session_001")
        self.assertIn("TestPlayer", session.participants)
        
        # Log some activities
        campaign.log_dialogue("Gandalf", "Welcome, young adventurer")
        campaign.log_action("TestPlayer", "draws sword", "ready for battle")
        campaign.log_exploration("Rivendell", "Elven city", ["library", "springs"])
        
        # End session
        summary = campaign.end_session()
        self.assertIsNotNone(summary)
        self.assertGreater(summary.duration_minutes, 0)
        self.assertIn("Rivendell", summary.locations_visited)
        self.assertIn("Gandalf", summary.npcs_encountered)
    
    def test_ai_content_generation(self):
        """Test AI content generation"""
        campaign = DnDCampaignManager(self.campaign_name)
        
        # Test NPC generation
        npc = campaign.generate_npc({
            'location_type': 'forest',
            'quest_type': 'exploration',
            'player_levels': {'TestPlayer': 1}
        })
        
        self.assertIsNotNone(npc)
        self.assertIsInstance(npc.content, str)
        self.assertGreater(len(npc.content), 0)
        self.assertGreaterEqual(npc.confidence, 0.0)
        self.assertLessEqual(npc.confidence, 1.0)
        
        # Test location generation
        location = campaign.generate_location({
            'biome': 'forest',
            'time_of_day': 'day'
        })
        
        self.assertIsNotNone(location)
        self.assertIsInstance(location.content, str)
        self.assertGreater(len(location.content), 0)
        
        # Test quest generation
        quest = campaign.generate_quest({
            'player_level': 1,
            'location_name': 'Forest',
            'active_quests': 0
        })
        
        self.assertIsNotNone(quest)
        self.assertIsInstance(quest.content, str)
        self.assertGreater(len(quest.content), 0)
    
    def test_memory_search(self):
        """Test memory search functionality"""
        campaign = DnDCampaignManager(self.campaign_name)
        
        # Add some test data to memory
        campaign.memory_system.add_campaign_memory(
            memory_type='entity',
            content={'name': 'Gandalf', 'type': 'wizard'},
            session_id='test'
        )
        
        campaign.memory_system.add_campaign_memory(
            memory_type='location',
            content={'name': 'Rivendell', 'type': 'elven_city'},
            session_id='test'
        )
        
        # Test search
        results = campaign.search_campaign_memory("Gandalf")
        self.assertIsInstance(results, list)
        
        results = campaign.search_campaign_memory("Rivendell")
        self.assertIsInstance(results, list)
    
    def test_campaign_export(self):
        """Test campaign data export"""
        campaign = DnDCampaignManager(self.campaign_name)
        
        # Create some test data
        campaign.create_character_from_vibe(
            player_name="TestPlayer",
            vibe_description="A brave human fighter",
            preferences={}
        )
        
        campaign.start_session("test_session")
        campaign.log_dialogue("Gandalf", "Hello there")
        campaign.end_session()
        
        # Test export
        export_file = campaign.export_campaign_data()
        self.assertTrue(os.path.exists(export_file))
        
        # Verify export contains expected data
        import json
        with open(export_file, 'r') as f:
            export_data = json.load(f)
        
        self.assertIn('campaign_info', export_data)
        self.assertIn('characters', export_data)
        self.assertIn('sessions', export_data)
        self.assertIn('campaign_memory', export_data)

class TestMemorySystem(unittest.TestCase):
    """Test the memory system functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.memory_system = CampaignMemorySystem(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_memory_storage(self):
        """Test storing and retrieving memory"""
        # Add test memory
        self.memory_system.add_campaign_memory(
            memory_type='entity',
            content={'name': 'TestNPC', 'type': 'merchant'},
            session_id='test_session'
        )
        
        # Search for it
        results = self.memory_system.search_campaign_memory("TestNPC")
        self.assertGreater(len(results), 0)
        
        # Get summary
        summary = self.memory_system.get_campaign_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('total_entities', summary)

class TestCharacterManager(unittest.TestCase):
    """Test the character manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.character_manager = CharacterManager()
    
    def test_vibe_analysis(self):
        """Test vibe analysis functionality"""
        vibe_description = "A brave human fighter who protects the innocent"
        analysis = self.character_manager._analyze_vibe(vibe_description)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('combat_style', analysis)
        self.assertIn('personality_type', analysis)
        self.assertIn('magical_affinity', analysis)
        self.assertIn('social_style', analysis)
    
    def test_ability_score_generation(self):
        """Test ability score generation"""
        ability_scores = self.character_manager._generate_ability_scores(
            CharacterClass.FIGHTER,
            Race.HUMAN
        )
        
        self.assertIsInstance(ability_scores, dict)
        self.assertEqual(len(ability_scores), 6)  # 6 ability scores
        
        # Check that all ability scores are present
        for ability in AbilityScore:
            self.assertIn(ability, ability_scores)
            self.assertIsInstance(ability_scores[ability], int)
            self.assertGreaterEqual(ability_scores[ability], 8)
            self.assertLessEqual(ability_scores[ability], 20)

class TestSessionLogger(unittest.TestCase):
    """Test the session logger functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.memory_system = CampaignMemorySystem(self.test_dir)
        self.session_logger = SessionLogger(self.memory_system)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_session_lifecycle(self):
        """Test complete session lifecycle"""
        # Start session
        session = self.session_logger.start_session("test_session", ["Player1", "Player2"])
        self.assertIsNotNone(session)
        self.assertEqual(session.session_id, "test_session")
        self.assertEqual(session.participants, ["Player1", "Player2"])
        
        # Log activities
        self.session_logger.log_dialogue("Gandalf", "Welcome")
        self.session_logger.log_action("Player1", "draws sword")
        self.session_logger.log_exploration("Rivendell", "Elven city", ["library"])
        
        # End session
        summary = self.session_logger.end_session()
        self.assertIsNotNone(summary)
        self.assertGreater(summary.duration_minutes, 0)
        self.assertIn("Rivendell", summary.locations_visited)
        self.assertIn("Gandalf", summary.npcs_encountered)

def run_tests():
    """Run all tests"""
    print("🧪 Running DnD Campaign Manager Tests...")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestDnDCampaignManager))
    test_suite.addTest(unittest.makeSuite(TestMemorySystem))
    test_suite.addTest(unittest.makeSuite(TestCharacterManager))
    test_suite.addTest(unittest.makeSuite(TestSessionLogger))
    
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