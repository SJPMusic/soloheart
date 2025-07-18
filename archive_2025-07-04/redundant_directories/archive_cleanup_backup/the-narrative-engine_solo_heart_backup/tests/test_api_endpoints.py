#!/usr/bin/env python3
"""
Test suite for API endpoints using Flask test client.

Tests all major endpoints including:
- GET /api/campaign/<id>/lore
- POST /api/campaign/<id>/lore
- GET /api/campaign/<id>/diagnostics/*
- Error handling and response formats
"""

import unittest
import json
import tempfile
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_interface import app
from narrative_bridge import NarrativeBridge


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.campaign_id = "test-api-campaign"
        
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Initialize test data
        self.setup_test_data()
        
        # Sample request data
        self.sample_lore_data = {
            "title": "The Ancient Temple",
            "content": "A mysterious temple hidden in the mountains.",
            "lore_type": "location",
            "importance": 4,
            "tags": ["temple", "ancient", "mysterious"],
            "discovered": True
        }
        
        self.sample_action_data = {
            "action": "I explore the ancient temple",
            "character_id": "player",
            "context": "Mountain exploration"
        }
    
    def tearDown(self):
        """Clean up after each test."""
        # Clean up test directory
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def setup_test_data(self):
        """Set up test data for the campaign."""
        # Create a test session
        from web_interface import get_or_create_session
        session = get_or_create_session(self.campaign_id)
        
        # Add some test lore entries
        session.bridge.create_lore_entry(
            title="The Mysterious Cave",
            content="A dark cave that whispers ancient secrets.",
            lore_type="location",
            importance=4,
            tags=["cave", "mysterious"],
            discovered=True
        )
        
        session.bridge.create_lore_entry(
            title="Eldara the Wise",
            content="An ancient elf who guards the forest.",
            lore_type="character",
            importance=5,
            tags=["elf", "wise"],
            discovered=True
        )
        
        # Add some test memories
        session.bridge.store_dnd_memory(
            content="You discover a mysterious cave entrance.",
            memory_type="discovery",
            metadata={"location": "forest"},
            tags=["discovery", "cave"],
            primary_emotion="WONDER",
            emotional_intensity=0.8
        )
        
        # Add character arc
        session.bridge.create_character_arc(
            character_id="player",
            name="The Hero's Journey",
            arc_type="GROWTH",
            description="Your journey from ordinary to extraordinary.",
            tags=["hero", "growth"],
            emotional_themes=["determination", "courage"]
        )
        
        # Add plot thread
        session.bridge.create_plot_thread(
            name="The Mysterious Artifacts",
            thread_type="MYSTERY",
            description="Ancient artifacts have appeared in the world.",
            priority=8,
            assigned_characters=["player"],
            tags=["mystery", "artifacts"]
        )
    
    def test_get_lore_endpoint(self):
        """Test GET /api/campaign/<id>/lore endpoint."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/lore')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIn('entries', data)
        self.assertIn('summary', data)
        self.assertIn('types', data)
        self.assertIn('importance_levels', data)
        
        # Verify data
        self.assertGreater(len(data['entries']), 0)
        self.assertGreater(data['summary']['total_entries'], 0)
        self.assertIn('location', data['types'])
        self.assertIn('character', data['types'])
    
    def test_get_lore_with_filters(self):
        """Test GET /api/campaign/<id>/lore with query parameters."""
        # Test filtering by type
        response = self.client.get(f'/api/campaign/{self.campaign_id}/lore?lore_type=location')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data['entries']), 1)
        self.assertEqual(data['entries'][0]['lore_type'], 'location')
        
        # Test filtering by importance
        response = self.client.get(f'/api/campaign/{self.campaign_id}/lore?min_importance=5')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data['entries']), 1)
        self.assertEqual(data['entries'][0]['importance'], 5)
        
        # Test filtering by discovery status
        response = self.client.get(f'/api/campaign/{self.campaign_id}/lore?discovered_only=true')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data['entries']), 2)  # Both entries are discovered
    
    def test_post_lore_endpoint(self):
        """Test POST /api/campaign/<id>/lore endpoint."""
        response = self.client.post(
            f'/api/campaign/{self.campaign_id}/lore',
            data=json.dumps(self.sample_lore_data),
            content_type='application/json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIn('success', data)
        self.assertIn('lore_id', data)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['lore_id'])
        
        # Verify lore entry was created
        get_response = self.client.get(f'/api/campaign/{self.campaign_id}/lore')
        get_data = json.loads(get_response.data)
        
        # Find the new entry
        new_entry = None
        for entry in get_data['entries']:
            if entry['title'] == self.sample_lore_data['title']:
                new_entry = entry
                break
        
        self.assertIsNotNone(new_entry)
        self.assertEqual(new_entry['content'], self.sample_lore_data['content'])
        self.assertEqual(new_entry['lore_type'], self.sample_lore_data['lore_type'])
        self.assertEqual(new_entry['importance'], self.sample_lore_data['importance'])
        self.assertEqual(new_entry['tags'], self.sample_lore_data['tags'])
        self.assertEqual(new_entry['discovered'], self.sample_lore_data['discovered'])
    
    def test_post_lore_invalid_data(self):
        """Test POST /api/campaign/<id>/lore with invalid data."""
        invalid_data = {
            "title": "",  # Empty title
            "content": "Test content",
            "lore_type": "invalid_type",  # Invalid type
            "importance": 10,  # Invalid importance
            "tags": "not_a_list",  # Invalid tags
            "discovered": "not_boolean"  # Invalid discovered
        }
        
        response = self.client.post(
            f'/api/campaign/{self.campaign_id}/lore',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # Should return error
        self.assertNotEqual(response.status_code, 200)
    
    def test_get_diagnostics_timeline(self):
        """Test GET /api/campaign/<id>/diagnostics/timeline endpoint."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/diagnostics/timeline')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIsInstance(data, list)
        
        # If there are conflicts, verify structure
        if len(data) > 0:
            conflict = data[0]
            self.assertIn('id', conflict)
            self.assertIn('description', conflict)
            self.assertIn('type', conflict)
            self.assertIn('urgency', conflict)
            self.assertIn('resolved', conflict)
            self.assertIn('characters_involved', conflict)
    
    def test_get_diagnostics_arcs(self):
        """Test GET /api/campaign/<id>/diagnostics/arcs endpoint."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/diagnostics/arcs')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIsInstance(data, dict)
        
        # Verify character arcs exist
        self.assertIn('player', data)
        self.assertGreater(len(data['player']), 0)
        
        # Verify arc structure
        arc = data['player'][0]
        self.assertIn('arc_id', arc)
        self.assertIn('title', arc)
        self.assertIn('description', arc)
        self.assertIn('arc_type', arc)
        self.assertIn('status', arc)
        self.assertIn('milestones', arc)
    
    def test_get_diagnostics_heatmap(self):
        """Test GET /api/campaign/<id>/diagnostics/heatmap endpoint."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/diagnostics/heatmap')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIsInstance(data, dict)
        
        # If there's emotion data, verify structure
        if len(data) > 0:
            character_data = list(data.values())[0]
            self.assertIsInstance(character_data, list)
            
            if len(character_data) > 0:
                emotion_point = character_data[0]
                self.assertIn('timestamp', emotion_point)
                self.assertIn('emotion', emotion_point)
                self.assertIn('intensity', emotion_point)
                self.assertIn('context', emotion_point)
    
    def test_get_diagnostics_report(self):
        """Test GET /api/campaign/<id>/diagnostics/report endpoint."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/diagnostics/report')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIn('campaign_id', data)
        self.assertIn('total_actions', data)
        self.assertIn('total_conflicts', data)
        self.assertIn('resolved_conflicts', data)
        self.assertIn('unresolved_conflicts', data)
        self.assertIn('campaign_health_score', data)
        self.assertIn('narrative_coherence', data)
        self.assertIn('character_engagement', data)
        self.assertIn('dominant_emotions', data)
        self.assertIn('arc_progress_summary', data)
        self.assertIn('plot_thread_summary', data)
        self.assertIn('memory_summary', data)
        self.assertIn('lore_summary', data)
        
        # Verify data types
        self.assertIsInstance(data['total_actions'], int)
        self.assertIsInstance(data['total_conflicts'], int)
        self.assertIsInstance(data['resolved_conflicts'], int)
        self.assertIsInstance(data['unresolved_conflicts'], int)
        self.assertIsInstance(data['campaign_health_score'], float)
        self.assertIsInstance(data['narrative_coherence'], float)
        self.assertIsInstance(data['character_engagement'], float)
        self.assertIsInstance(data['dominant_emotions'], dict)
        self.assertIsInstance(data['arc_progress_summary'], dict)
        self.assertIsInstance(data['plot_thread_summary'], dict)
        self.assertIsInstance(data['memory_summary'], dict)
        self.assertIsInstance(data['lore_summary'], dict)
        
        # Verify campaign ID
        self.assertEqual(data['campaign_id'], self.campaign_id)
    
    def test_post_action_endpoint(self):
        """Test POST /api/campaign/<id>/action endpoint."""
        response = self.client.post(
            f'/api/campaign/{self.campaign_id}/action',
            data=json.dumps(self.sample_action_data),
            content_type='application/json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIn('success', data)
        self.assertIn('narration', data)
        self.assertIn('orchestration_events', data)
        self.assertIn('campaign_state', data)
        self.assertIn('recent_memories', data)
        self.assertIn('character', data)
        self.assertIn('timestamp', data)
        
        self.assertTrue(data['success'])
        self.assertIsInstance(data['narration'], str)
        self.assertIsInstance(data['orchestration_events'], list)
        self.assertIsInstance(data['campaign_state'], dict)
        self.assertIsInstance(data['recent_memories'], list)
        self.assertIsInstance(data['character'], dict)
        self.assertIsInstance(data['timestamp'], str)
    
    def test_get_campaign_summary(self):
        """Test GET /api/campaign/<id>/summary endpoint."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/summary')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIn('campaign_id', data)
        self.assertIn('session_start', data)
        self.assertIn('total_actions', data)
        self.assertIn('characters', data)
        self.assertIn('active_character', data)
        self.assertIn('debug_mode', data)
        
        # Verify data
        self.assertEqual(data['campaign_id'], self.campaign_id)
        self.assertIsInstance(data['total_actions'], int)
        self.assertIsInstance(data['characters'], dict)
        self.assertIsInstance(data['debug_mode'], bool)
    
    def test_get_sidebar_data(self):
        """Test GET /api/campaign/<id>/sidebar endpoint."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/sidebar')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIn('character_info', data)
        self.assertIn('character_arcs', data)
        self.assertIn('plot_threads', data)
        self.assertIn('journal_entries', data)
        self.assertIn('recent_memories', data)
        
        # Verify data types
        self.assertIsInstance(data['character_info'], dict)
        self.assertIsInstance(data['character_arcs'], list)
        self.assertIsInstance(data['plot_threads'], list)
        self.assertIsInstance(data['journal_entries'], list)
        self.assertIsInstance(data['recent_memories'], list)
    
    def test_get_narrative_dynamics(self):
        """Test GET /api/campaign/<id>/narrative-dynamics endpoint."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/narrative-dynamics')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIn('campaign_momentum', data)
        self.assertIn('active_events', data)
        self.assertIn('recent_events', data)
        self.assertIn('emotional_themes', data)
        self.assertIn('pressure_points', data)
        self.assertIn('emergent_conflicts', data)
        self.assertIn('suggested_actions', data)
        
        # Verify data types
        self.assertIsInstance(data['campaign_momentum'], dict)
        self.assertIsInstance(data['active_events'], list)
        self.assertIsInstance(data['recent_events'], list)
        self.assertIsInstance(data['emotional_themes'], list)
        self.assertIsInstance(data['pressure_points'], list)
        self.assertIsInstance(data['emergent_conflicts'], list)
        self.assertIsInstance(data['suggested_actions'], list)
    
    def test_get_conflicts(self):
        """Test GET /api/campaign/<id>/conflicts endpoint."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/conflicts')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIsInstance(data, list)
        
        # If there are conflicts, verify structure
        if len(data) > 0:
            conflict = data[0]
            self.assertIn('id', conflict)
            self.assertIn('title', conflict)
            self.assertIn('description', conflict)
            self.assertIn('type', conflict)
            self.assertIn('urgency', conflict)
            self.assertIn('characters_involved', conflict)
            self.assertIn('resolutions', conflict)
            self.assertIn('impact', conflict)
    
    def test_error_handling_invalid_campaign(self):
        """Test error handling for invalid campaign ID."""
        invalid_campaign_id = "nonexistent-campaign"
        
        # Test lore endpoint
        response = self.client.get(f'/api/campaign/{invalid_campaign_id}/lore')
        self.assertEqual(response.status_code, 200)  # Should create new session
        
        # Test diagnostics endpoint
        response = self.client.get(f'/api/campaign/{invalid_campaign_id}/diagnostics/report')
        self.assertEqual(response.status_code, 200)  # Should create new session
    
    def test_error_handling_invalid_endpoint(self):
        """Test error handling for invalid endpoints."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/lore')
        
        # Verify CORS headers
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)
        self.assertIn('Access-Control-Allow-Headers', response.headers)
    
    def test_content_type_headers(self):
        """Test that content type headers are correct."""
        response = self.client.get(f'/api/campaign/{self.campaign_id}/lore')
        
        # Verify content type
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('application/json', response.headers.get('Content-Type', ''))


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 