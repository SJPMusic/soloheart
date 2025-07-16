import unittest
import json
from solo_heart.simple_unified_interface import app

class TestTransformationResolution(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.narrative_history = [
            {'role': 'assistant', 'content': 'The orphan wandered the land, seeking answers.'},
            {'role': 'assistant', 'content': 'He became a warrior, fighting for justice.'},
            {'role': 'assistant', 'content': 'In time, he learned the secrets of magic.'}
        ]
        self.symbolic_tags = [
            {'type': 'archetype', 'symbol': 'Orphan', 'confidence': 0.8},
            {'type': 'archetype', 'symbol': 'Warrior', 'confidence': 0.8},
            {'type': 'archetype', 'symbol': 'Magician', 'confidence': 0.8}
        ]
        self.character_stats = {'level': 5, 'hit_points': 30}
        self.goals = [
            {'type': 'Change', 'confidence': 0.9, 'progress': 0.8},
            {'type': 'Protect', 'confidence': 0.7, 'progress': 0.5}
        ]
        self.world_state = {'story_flags': {'quest_started': True, 'boss_defeated': False}}
        self.memory_context = {'recent_memories': 'The orphan lost his home.'}

    def test_transformation_infer(self):
        resp = self.app.post('/api/transformation/infer', json={
            'narrative_history': self.narrative_history,
            'symbolic_tags': self.symbolic_tags,
            'character_stats': self.character_stats
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        t = data['transformation']
        self.assertIn('transformation_type', t)
        self.assertIn('confidence_score', t)
        self.assertGreaterEqual(t['confidence_score'], 0.5)

    def test_resolution_monitor(self):
        # Use transformation from previous test
        transformation = {
            'transformation_type': 'Innocent → Orphan → Seeker → Warrior → Magician',
            'archetypal_shift': "Hero's Journey",
            'confidence_score': 0.9,
            'evidence_snippets': ['The orphan wandered the land', 'He became a warrior']
        }
        resp = self.app.post('/api/resolution/monitor', json={
            'goals': self.goals,
            'world_state': self.world_state,
            'memory_context': self.memory_context,
            'transformations': [transformation]
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        r = data['resolution']
        self.assertIn('resolution_state', r)
        self.assertIn(r['resolution_state'], ['early', 'mid', 'climax', 'denouement'])
        self.assertIn('recommendation', r)

    def test_prompt_integration(self):
        # Simulate prompt build (internal method)
        from solo_heart.simple_unified_interface import TNEDemoBridge
        bridge = TNEDemoBridge()
        campaign_id = 'test_campaign'
        bridge.conversation_history = {campaign_id: self.narrative_history}
        prompt = bridge._build_enhanced_prompt('Test action', campaign_id, {})
        self.assertIn('transformation', prompt)
        self.assertIn('resolution', prompt)
        self.assertTrue('[Transformation]' in prompt['transformation'])
        self.assertTrue('[Resolution]' in prompt['resolution'])

if __name__ == '__main__':
    unittest.main() 