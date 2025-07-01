import unittest
import json
import time
from narrative_engine.memory.vector_memory_module import VectorMemoryModule
from narrative_engine.memory.memory_trace_logger import memory_trace_logger
from narrative_engine.memory.emotional_memory import EmotionalContext, EmotionalTone, EmotionalIntensity, EventType, emotional_memory_system

# Mock LayeredMemorySystem for test (replace with actual import if available)
class MockLayeredMemorySystem:
    def __init__(self, campaign_id):
        self.campaign_id = campaign_id
        self.memories = []
    def add_memory(self, content, memory_type, layer, user_id, session_id, emotional_weight, thematic_tags, narrative_context):
        entry = {
            'content': content,
            'memory_type': memory_type,
            'layer': layer,
            'user_id': user_id,
            'session_id': session_id,
            'emotional_weight': emotional_weight,
            'thematic_tags': thematic_tags,
            'narrative_context': narrative_context,
            'campaign_id': self.campaign_id
        }
        self.memories.append(entry)
        return entry
    def recall(self, query=None, thematic=None, limit=10):
        return self.memories[:limit]

class TestMemorySystem(unittest.TestCase):
    """
    Roadmap-based unit tests for memory integrity, JSON compatibility, and emotional realism.
    References: NarrativeEngine_Roadmap.txt
    """
    def setUp(self):
        self.campaign_id = "TestCampaign"
        self.vector_memory = VectorMemoryModule(self.campaign_id)
        self.layered_memory = MockLayeredMemorySystem(self.campaign_id)

    def test_json_compatibility(self):
        """Test 1: All memory outputs are valid JSON (Goal: Narrative continuity, JSON compatibility)"""
        entry = self.layered_memory.add_memory({'text': 'Test'}, 'event', 'short_term', 'user', 'sess', 0.5, ['test'], {'foo': 'bar'})
        try:
            json_str = json.dumps(entry)
            loaded = json.loads(json_str)
            self.assertEqual(loaded['content']['text'], 'Test')
        except Exception as e:
            self.fail(f"Memory output not JSON-compatible: {e}")

    def test_vector_memory_entry_fields(self):
        """Test 2: Vector memory entries include campaign_id and importance (Goal: Memory as sacred, campaign-aware)"""
        self.vector_memory.available = False  # Force fallback mode for test
        meta = {'character': 'NPC', 'importance': 0.8}
        self.vector_memory.store_memory("A betrayal occurred", meta)
        found = any('campaign_id' in m and 'importance' in m['metadata'] for m in self.vector_memory.memories)
        self.assertTrue(found, "Vector memory entry missing campaign_id or importance")

    def test_memory_decay(self):
        """Test 3: Memory decay reduces importance over time (Goal: Memory is sacred, decay)"""
        self.vector_memory.available = False
        meta = {'character': 'NPC', 'importance': 1.0}
        self.vector_memory.store_memory("Old memory", meta)
        before = self.vector_memory.memories[0]['metadata']['importance']
        self.vector_memory.decay_memory(decay_rate=0.5)  # Simulate decay
        after = self.vector_memory.memories[0]['metadata']['importance']
        self.assertLess(after, before, "Decay did not reduce importance")

    def test_retrieve_similar(self):
        """Test 4: Recall returns top-N results with expected similarity (Goal: Narrative continuity, semantic recall)"""
        self.vector_memory.available = False
        self.vector_memory.memories = []
        self.vector_memory.store_memory("The hero saved the town", {'importance': 0.9})
        self.vector_memory.store_memory("The villain betrayed the town", {'importance': 0.8})
        results = self.vector_memory.retrieve_similar("town", top_n=2)
        self.assertEqual(len(results), 2)
        self.assertTrue(all('text' in r for r in results))

    def test_emotional_tags_persist(self):
        """Test 5: Emotional tags persist and are retrievable (Goal: Emotional realism, memory as sacred)"""
        ctx = EmotionalContext(
            primary_tone=EmotionalTone.ANGER,
            intensity=EmotionalIntensity.INTENSE,
            event_type=EventType.BETRAYAL,
            character_name="NPC1"
        )
        emotional_memory_system.add_emotional_memory(self.campaign_id, "NPC1", ctx)
        state = emotional_memory_system.get_character_emotional_state("NPC1", self.campaign_id)
        self.assertEqual(state['dominant_emotion'], EmotionalTone.ANGER.value)
        memories = emotional_memory_system.recall_emotional_context("NPC1", campaign_id=self.campaign_id)
        self.assertTrue(any(m.event_type == EventType.BETRAYAL for m in memories))

    def test_edge_case_fallbacks(self):
        """Test 6: Edge cases (empty memory, unknown emotion) trigger fallback logic (Goal: Robustness, narrative continuity)"""
        # Empty memory
        self.vector_memory.memories = []
        results = self.vector_memory.retrieve_similar("anything", top_n=1)
        self.assertEqual(results, [])
        # Unknown emotion
        state = emotional_memory_system.get_character_emotional_state("UnknownNPC", self.campaign_id)
        self.assertEqual(state['dominant_emotion'], EmotionalTone.NEUTRAL.value)
        response = emotional_memory_system.generate_emotional_response("UnknownNPC", "test situation", campaign_id=self.campaign_id)
        self.assertTrue(response['emotional_response'].get('fallback_used', False))

if __name__ == "__main__":
    unittest.main() 