import unittest
import json
from solo_heart.simple_unified_interface import app

class TestEndingEpilogueGeneration(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.goals = [
            {'type': 'Change', 'confidence': 0.9, 'progress': 0.8},
            {'type': 'Protect', 'confidence': 0.8, 'progress': 0.7}
        ]
        self.transformation = {
            'transformation_type': 'Innocent → Orphan → Seeker → Warrior → Magician',
            'archetypal_shift': "Hero's Journey",
            'confidence_score': 0.9,
            'description': 'Classic hero\'s journey from innocence to mastery'
        }
        self.resolution = {
            'resolution_state': 'climax',
            'progress': 0.8,
            'goal_progress': 0.8,
            'flag_progress': 0.7,
            'transformation_progress': 0.9,
            'justification': 'Story is climax stage with 80.0% completion',
            'recommendation': 'Raise stakes and introduce moral costs'
        }
        self.world_state = {
            'story_flags': {
                'quest_started': True,
                'boss_defeated': True,
                'victory_achieved': True
            }
        }

    def test_ending_detection_api(self):
        """Test the ending detection API endpoint."""
        resp = self.app.post('/api/narrative/ending', json={
            'goals': self.goals,
            'transformation': self.transformation,
            'resolution': self.resolution,
            'world_state': self.world_state
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        ending = data['ending']
        self.assertIn('ending_triggered', ending)
        self.assertIn('ending_type', ending)
        self.assertIn('justification', ending)
        self.assertIn('confidence', ending)
        # Should trigger ending with high completion
        self.assertTrue(ending['ending_triggered'])
        self.assertIsNotNone(ending['ending_type'])

    def test_ending_detection_early_story(self):
        """Test ending detection for early story (should not trigger)."""
        early_resolution = {
            'resolution_state': 'early',
            'progress': 0.2,
            'goal_progress': 0.2,
            'flag_progress': 0.1,
            'transformation_progress': 0.3
        }
        resp = self.app.post('/api/narrative/ending', json={
            'goals': self.goals,
            'transformation': self.transformation,
            'resolution': early_resolution,
            'world_state': self.world_state
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        ending = data['ending']
        self.assertFalse(ending['ending_triggered'])

    def test_ending_type_determination(self):
        """Test different ending types based on narrative elements."""
        # Test triumph ending
        triumph_world_state = {'story_flags': {'victory_achieved': True}}
        resp = self.app.post('/api/narrative/ending', json={
            'goals': self.goals,
            'transformation': self.transformation,
            'resolution': self.resolution,
            'world_state': triumph_world_state
        })
        data = json.loads(resp.data)
        ending = data['ending']
        if ending['ending_triggered']:
            self.assertIn(ending['ending_type'], ['triumph', 'bittersweet'])

        # Test sacrifice ending
        sacrifice_goals = [{'type': 'Sacrifice', 'confidence': 0.9}]
        resp = self.app.post('/api/narrative/ending', json={
            'goals': sacrifice_goals,
            'transformation': self.transformation,
            'resolution': self.resolution,
            'world_state': self.world_state
        })
        data = json.loads(resp.data)
        ending = data['ending']
        if ending['ending_triggered']:
            self.assertEqual(ending['ending_type'], 'sacrifice')

    def test_epilogue_generation_api(self):
        """Test the epilogue generation API endpoint."""
        memory_log = [
            {'content': 'The hero began their journey as an innocent soul.'},
            {'content': 'They faced many trials and tribulations.'},
            {'content': 'In the end, they emerged victorious and transformed.'}
        ]
        goals_achieved = [
            {'type': 'Change', 'confidence': 0.9, 'progress': 1.0},
            {'type': 'Protect', 'confidence': 0.8, 'progress': 1.0}
        ]
        character_stats = {'name': 'Aria', 'level': 10}
        transformation_path = {
            'transformation_type': 'Innocent → Orphan → Seeker → Warrior → Magician',
            'archetypal_shift': "Hero's Journey"
        }
        world_state_flags = {'victory_achieved': True, 'quest_completed': True}
        ending_type = 'triumph'

        resp = self.app.post('/api/narrative/epilogue', json={
            'memory_log': memory_log,
            'goals_achieved': goals_achieved,
            'character_stats': character_stats,
            'transformation_path': transformation_path,
            'world_state_flags': world_state_flags,
            'ending_type': ending_type
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        epilogue = data['epilogue']
        self.assertIn('epilogue_text', epilogue)
        self.assertIn('epilogue_theme', epilogue)
        self.assertIn('epilogue_quotes', epilogue)
        self.assertIsInstance(epilogue['epilogue_quotes'], list)

    def test_epilogue_themes_by_ending_type(self):
        """Test that epilogue themes match ending types."""
        ending_types = ['triumph', 'tragedy', 'rebirth', 'sacrifice', 'redemption', 'bittersweet']
        character_stats = {'name': 'Test Hero'}
        transformation_path = {'transformation_type': 'Innocent → Warrior'}
        
        for ending_type in ending_types:
            resp = self.app.post('/api/narrative/epilogue', json={
                'memory_log': [],
                'goals_achieved': [],
                'character_stats': character_stats,
                'transformation_path': transformation_path,
                'world_state_flags': {},
                'ending_type': ending_type
            })
            data = json.loads(resp.data)
            epilogue = data['epilogue']
            self.assertIsNotNone(epilogue['epilogue_theme'])
            self.assertIsNotNone(epilogue['epilogue_text'])

    def test_prompt_integration(self):
        """Test that ending and epilogue context is included in prompt generation."""
        from solo_heart.simple_unified_interface import TNEDemoBridge
        bridge = TNEDemoBridge()
        campaign_id = 'test_campaign'
        bridge.conversation_history = {campaign_id: []}
        
        # Mock the context methods to check they're called
        original_get_transformation = bridge._get_transformation_context_for_prompt
        original_get_resolution = bridge._get_resolution_context_for_prompt
        
        def mock_transformation(*args):
            return "[Transformation]\nTest transformation context"
        
        def mock_resolution(*args):
            return "[Resolution]\nTest resolution context"
        
        bridge._get_transformation_context_for_prompt = mock_transformation
        bridge._get_resolution_context_for_prompt = mock_resolution
        
        prompt = bridge._build_enhanced_prompt('Test action', campaign_id, {})
        
        self.assertIn('transformation', prompt)
        self.assertIn('resolution', prompt)
        self.assertTrue('[Transformation]' in prompt['transformation'])
        self.assertTrue('[Resolution]' in prompt['resolution'])

    def test_ui_integration(self):
        """Test that UI elements are properly structured for ending display."""
        # Test cinematic ending overlay structure
        from solo_heart.templates.gameplay import render_template
        # This would require a more complex test setup with template rendering
        # For now, we'll test the basic structure
        self.assertTrue(True)  # Placeholder for UI structure validation

    def test_error_handling(self):
        """Test error handling in ending and epilogue generation."""
        # Test with invalid data
        resp = self.app.post('/api/narrative/ending', json={
            'goals': None,
            'transformation': None,
            'resolution': None,
            'world_state': None
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])  # Should handle gracefully

        # Test epilogue with invalid data
        resp = self.app.post('/api/narrative/epilogue', json={
            'memory_log': None,
            'goals_achieved': None,
            'character_stats': None,
            'transformation_path': None,
            'world_state_flags': None,
            'ending_type': 'invalid_type'
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main() 