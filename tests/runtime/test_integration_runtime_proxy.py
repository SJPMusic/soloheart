"""
Integration tests for SoloHeart runtime modules with NarrativeEngineProxy.

Tests that all runtime modules properly instantiate and use NarrativeEngineProxy
for TNE communication, with fallback behavior when TNE is offline.
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import runtime modules
from runtime.narrative_engine_proxy import NarrativeEngineProxy
from runtime.scene_manager import SceneManager
from runtime.memory_tracker import MemoryTracker
from runtime.context_manager import ContextManager
from runtime.interaction_engine import InteractionEngine
from runtime.runtime_entry import SoloHeartRuntime, create_runtime


class TestRuntimeIntegration(unittest.TestCase):
    """Integration tests for SoloHeart runtime modules."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.campaign_id = "test_campaign_123"
        self.base_url = "http://localhost:5002"
        
        # Mock the TNEClient to avoid actual HTTP calls
        self.mock_tne_client = Mock()
        self.mock_tne_client.is_healthy.return_value = {"status": "healthy"}
        self.mock_tne_client.add_scene.return_value = {"status": "success"}
        self.mock_tne_client.add_memory_entry.return_value = {"status": "success"}
        self.mock_tne_client.get_symbolic_summary.return_value = "Test narrative summary"
        self.mock_tne_client.query_identity.return_value = {"status": "success", "identity": {"name": "Test Character"}}
        self.mock_tne_client.query_concepts.return_value = {"status": "success", "results": []}
        self.mock_tne_client.get_scene_stats.return_value = {"status": "success", "stats": {"total_scenes": 5}}
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_narrative_engine_proxy_initialization(self, mock_tne_client_class):
        """Test that NarrativeEngineProxy initializes correctly."""
        mock_tne_client_class.return_value = self.mock_tne_client
        
        proxy = NarrativeEngineProxy(self.campaign_id, self.base_url)
        
        # Verify TNEClient was initialized with correct parameters
        mock_tne_client_class.assert_called_once_with(base_url=self.base_url, campaign_id=self.campaign_id)
        
        # Test proxy methods
        self.assertTrue(proxy.is_online())
        
        # Test scene recording
        result = proxy.record_scene("Test scene", {"test": "metadata"})
        self.assertEqual(result.get('status'), 'success')
        self.mock_tne_client.add_scene.assert_called_once()
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_scene_manager_integration(self, mock_tne_client_class):
        """Test SceneManager integration with NarrativeEngineProxy."""
        mock_tne_client_class.return_value = self.mock_tne_client
        
        scene_manager = SceneManager(self.campaign_id, self.base_url)
        
        # Test scene recording
        success = scene_manager.record_scene(
            "The hero enters the tavern",
            location="Tavern",
            participants=["Hero", "Innkeeper"],
            scene_type="dialogue"
        )
        
        self.assertTrue(success)
        self.assertEqual(len(scene_manager.scene_history), 1)
        
        # Test scene stats
        stats = scene_manager.get_scene_stats()
        self.assertIn("stats", stats)
        self.assertIn("total_scenes", stats["stats"])
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_memory_tracker_integration(self, mock_tne_client_class):
        """Test MemoryTracker integration with NarrativeEngineProxy."""
        mock_tne_client_class.return_value = self.mock_tne_client
        
        memory_tracker = MemoryTracker(self.campaign_id, self.base_url)
        
        # Test memory addition
        success = memory_tracker.add_memory(
            "The hero fought bravely",
            memory_type="episodic",
            tags=["combat", "heroism"],
            emotional_intensity=0.8
        )
        
        self.assertTrue(success)
        self.assertEqual(len(memory_tracker.local_memory_cache), 1)
        
        # Test memory search
        memories = memory_tracker.search_memory("hero")
        self.assertIsInstance(memories, list)
        
        # Test memory summary
        summary = memory_tracker.get_memory_summary()
        self.assertIsInstance(summary, str)
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_context_manager_integration(self, mock_tne_client_class):
        """Test ContextManager integration with NarrativeEngineProxy."""
        mock_tne_client_class.return_value = self.mock_tne_client
        
        context_manager = ContextManager(self.campaign_id, self.base_url)
        
        # Test narrative summary
        summary = context_manager.get_narrative_summary()
        self.assertIsInstance(summary, str)
        
        # Test identity profile
        identity = context_manager.get_identity_profile()
        self.assertIsInstance(identity, dict)
        
        # Test character context update
        success = context_manager.update_character_context(
            "Test Character",
            "Fighter",
            "Human",
            level=5
        )
        
        self.assertTrue(success)
        self.assertIn("character_info", context_manager.local_context_cache)
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_interaction_engine_integration(self, mock_tne_client_class):
        """Test InteractionEngine integration with NarrativeEngineProxy."""
        mock_tne_client_class.return_value = self.mock_tne_client
        
        interaction_engine = InteractionEngine(self.campaign_id, self.base_url)
        
        # Test player input processing
        result = interaction_engine.process_player_input(
            "I attack the goblin",
            input_type="combat"
        )
        
        self.assertTrue(result.get('success'))
        self.assertIn('response', result)
        self.assertEqual(len(interaction_engine.interaction_history), 1)
        
        # Test interaction stats
        stats = interaction_engine.get_interaction_stats()
        self.assertEqual(stats["total_interactions"], 1)
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_runtime_entry_integration(self, mock_tne_client_class):
        """Test SoloHeartRuntime integration with all modules."""
        mock_tne_client_class.return_value = self.mock_tne_client
        
        runtime = SoloHeartRuntime(self.campaign_id, self.base_url)
        
        # Test initialization
        self.assertTrue(runtime.initialize())
        self.assertTrue(runtime.is_initialized)
        
        # Test game action processing
        result = runtime.process_game_action(
            "The hero explores the ancient ruins",
            action_type="exploration",
            location="Ancient Ruins",
            participants=["Hero"]
        )
        
        self.assertTrue(result.get('success'))
        self.assertTrue(result.get('scene_recorded'))
        self.assertTrue(result.get('memory_added'))
        self.assertTrue(result.get('context_updated'))
        
        # Test campaign summary
        summary = runtime.get_campaign_summary()
        self.assertIn('campaign_id', summary)
        self.assertIn('runtime_stats', summary)
        
        # Test runtime health
        health = runtime.get_runtime_health()
        self.assertIn('is_initialized', health)
        self.assertIn('tne_online', health)
        self.assertIn('module_status', health)
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_runtime_factory_function(self, mock_tne_client_class):
        """Test the create_runtime factory function."""
        mock_tne_client_class.return_value = self.mock_tne_client
        
        runtime = create_runtime(self.campaign_id, self.base_url)
        
        self.assertIsInstance(runtime, SoloHeartRuntime)
        self.assertTrue(runtime.is_initialized)
        self.assertEqual(runtime.campaign_id, self.campaign_id)
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_offline_fallback_behavior(self, mock_tne_client_class):
        """Test fallback behavior when TNE is offline."""
        # Mock TNE as offline
        offline_mock = Mock()
        offline_mock.is_healthy.return_value = {"status": "unhealthy"}
        offline_mock.add_scene.return_value = {"status": "error", "error": "Connection refused"}
        offline_mock.add_memory_entry.return_value = {"status": "error", "error": "Connection refused"}
        offline_mock.get_symbolic_summary.return_value = "Error: Connection refused"
        offline_mock.query_identity.return_value = {"status": "error", "error": "Connection refused"}
        offline_mock.query_concepts.return_value = {"status": "error", "error": "Connection refused"}
        offline_mock.get_scene_stats.return_value = {"status": "error", "error": "Connection refused"}
        
        mock_tne_client_class.return_value = offline_mock
        
        # Test runtime initialization with offline TNE
        runtime = SoloHeartRuntime(self.campaign_id, self.base_url)
        self.assertTrue(runtime.initialize())
        
        # Verify TNE is detected as offline
        health = runtime.get_runtime_health()
        self.assertFalse(health['tne_online'])
        
        # Test that modules still work with local fallbacks
        result = runtime.process_game_action("Test action")
        self.assertTrue(result.get('success'))
        
        # Test scene manager fallback
        scene_manager = runtime.scene_manager
        stats = scene_manager.get_scene_stats()
        self.assertIn("total_scenes", stats)
        
        # Test memory tracker fallback
        memory_tracker = runtime.memory_tracker
        summary = memory_tracker.get_memory_summary()
        self.assertIsInstance(summary, str)
        
        # Test context manager fallback
        context_manager = runtime.context_manager
        context_summary = context_manager.get_narrative_summary()
        self.assertIsInstance(context_summary, str)
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_campaign_data_search(self, mock_tne_client_class):
        """Test searching across all campaign data."""
        mock_tne_client_class.return_value = self.mock_tne_client
        
        runtime = SoloHeartRuntime(self.campaign_id, self.base_url)
        runtime.initialize()
        
        # Add some test data
        runtime.process_game_action("Hero fights goblin", "combat", "Forest", ["Hero", "Goblin"])
        runtime.process_game_action("Hero talks to merchant", "dialogue", "Town", ["Hero", "Merchant"])
        
        # Test search across all data
        results = runtime.search_campaign_data("hero", "all", max_results=5)
        
        self.assertIn("query", results)
        self.assertIn("results", results)
        self.assertIn("scenes", results["results"])
        self.assertIn("memories", results["results"])
        self.assertIn("context", results["results"])
        self.assertIn("interactions", results["results"])
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_runtime_shutdown(self, mock_tne_client_class):
        """Test runtime shutdown and cleanup."""
        mock_tne_client_class.return_value = self.mock_tne_client
        
        runtime = SoloHeartRuntime(self.campaign_id, self.base_url)
        runtime.initialize()
        
        # Add some data
        runtime.process_game_action("Test action")
        
        # Verify data exists
        self.assertGreater(len(runtime.scene_manager.scene_history), 0)
        self.assertGreater(len(runtime.memory_tracker.local_memory_cache), 0)
        self.assertGreater(len(runtime.interaction_engine.interaction_history), 0)
        
        # Test shutdown
        runtime.shutdown()
        
        # Verify data is cleared
        self.assertEqual(len(runtime.scene_manager.scene_history), 0)
        self.assertEqual(len(runtime.memory_tracker.local_memory_cache), 0)
        self.assertEqual(len(runtime.interaction_engine.interaction_history), 0)


class TestRuntimeErrorHandling(unittest.TestCase):
    """Test error handling in runtime modules."""
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_proxy_error_handling(self, mock_tne_client_class):
        """Test error handling in NarrativeEngineProxy."""
        # Mock TNE client that raises exceptions
        error_mock = Mock()
        error_mock.is_healthy.side_effect = Exception("Connection error")
        error_mock.add_scene.side_effect = Exception("API error")
        error_mock.add_memory_entry.side_effect = Exception("Memory error")
        
        mock_tne_client_class.return_value = error_mock
        
        proxy = NarrativeEngineProxy("test_campaign", "http://localhost:5002")
        
        # Test error handling in is_online
        self.assertFalse(proxy.is_online())
        
        # Test error handling in record_scene
        result = proxy.record_scene("Test scene")
        self.assertIn("error", result)
        
        # Test error handling in add_memory
        result = proxy.add_memory({"text": "Test memory"})
        self.assertIn("error", result)
    
    @patch('runtime.narrative_engine_proxy.TNEClient')
    def test_module_error_handling(self, mock_tne_client_class):
        """Test error handling in runtime modules."""
        # Mock TNE client that returns errors
        error_mock = Mock()
        error_mock.is_healthy.return_value = {"status": "healthy"}
        error_mock.add_scene.return_value = {"status": "error", "error": "Scene error"}
        error_mock.add_memory_entry.return_value = {"status": "error", "error": "Memory error"}
        error_mock.get_symbolic_summary.return_value = "Error: Summary unavailable"
        error_mock.query_identity.return_value = {"status": "error", "error": "Identity error"}
        error_mock.query_concepts.return_value = {"status": "error", "error": "Search error"}
        
        mock_tne_client_class.return_value = error_mock
        
        # Test scene manager error handling
        scene_manager = SceneManager("test_campaign", "http://localhost:5002")
        success = scene_manager.record_scene("Test scene")
        self.assertFalse(success)  # Should fail due to TNE error
        
        # Test memory tracker error handling
        memory_tracker = MemoryTracker("test_campaign", "http://localhost:5002")
        success = memory_tracker.add_memory("Test memory")
        self.assertFalse(success)  # Should fail due to TNE error
        
        # Test context manager error handling
        context_manager = ContextManager("test_campaign", "http://localhost:5002")
        summary = context_manager.get_narrative_summary()
        self.assertIn("No narrative context available", summary)  # Should use fallback
        
        identity = context_manager.get_identity_profile()
        self.assertIn("status", identity)  # Should use fallback


if __name__ == '__main__':
    unittest.main() 