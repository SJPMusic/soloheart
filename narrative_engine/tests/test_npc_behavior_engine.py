"""
Unit tests for NPCBehaviorEngine module.

Tests adaptive NPC behavior functionality:
- Emotional state-based response generation
- Memory-driven behavior modifiers
- Response confidence calculation
- Campaign-aware behavior history
- JSON compatibility

References: NarrativeEngine_Roadmap.txt (Emotional realism matters)
"""

import unittest
import json
from narrative_engine.npc.npc_behavior_engine import NPCBehaviorEngine, BehaviorModifier, NPCResponse

class TestNPCBehaviorEngine(unittest.TestCase):
    """
    Test adaptive NPC behavior engine.
    
    Validates:
    - Emotional state-based responses
    - Memory-driven behavior modifiers
    - Response confidence calculation
    - Campaign-aware behavior tracking
    - JSON compatibility
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.behavior_engine = NPCBehaviorEngine()
        self.campaign_id = "TestCampaign"
        self.npc_id = "Mayor_Elric"
        
        # Sample emotional states
        self.angry_emotion_state = {
            'character_name': 'Mayor_Elric',
            'dominant_emotion': 'anger',
            'emotional_intensity': 2.5,
            'emotional_stability': 0.6,
            'recent_emotional_events': [],
            'emotional_tendencies': {'anger': 2.5}
        }
        
        self.trusting_emotion_state = {
            'character_name': 'Mayor_Elric',
            'dominant_emotion': 'trust',
            'emotional_intensity': 1.8,
            'emotional_stability': 0.9,
            'recent_emotional_events': [],
            'emotional_tendencies': {'trust': 1.8}
        }
        
        self.neutral_emotion_state = {
            'character_name': 'Mayor_Elric',
            'dominant_emotion': 'neutral',
            'emotional_intensity': 0.5,
            'emotional_stability': 0.8,
            'recent_emotional_events': [],
            'emotional_tendencies': {'neutral': 0.5}
        }
        
        # Sample memory contexts
        self.betrayal_memories = [
            {
                'event_type': 'betrayal',
                'content': 'Player sided with bandits',
                'emotional_context': {'primary_tone': 'anger'}
            }
        ]
        
        self.kindness_memories = [
            {
                'event_type': 'kindness',
                'content': 'Player helped the town',
                'emotional_context': {'primary_tone': 'trust'}
            }
        ]
        
        self.empty_memories = []
    
    def test_generate_response_angry_npc(self):
        """Test response generation for angry NPC"""
        player_input = "Hello, can you help me?"
        
        response = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.angry_emotion_state,
            memory_context=self.betrayal_memories,
            player_input=player_input,
            campaign_id=self.campaign_id
        )
        
        # Check response structure
        self.assertIsInstance(response, NPCResponse)
        self.assertEqual(response.npc_id, self.npc_id)
        self.assertIsInstance(response.response_text, str)
        self.assertGreater(len(response.response_text), 0)
        
        # Check emotional state is preserved
        self.assertEqual(response.emotional_state['dominant_emotion'], 'anger')
        
        # Check behavior modifiers reflect anger + betrayal memory
        # With betrayal memories, tone should be "guarded and suspicious" not "sharp"
        self.assertIn('guarded', response.behavior_modifiers.tone_modifier.lower())
        self.assertLess(response.behavior_modifiers.cooperation_level, 0.5)
        self.assertLess(response.behavior_modifiers.trust_level, 0.5)
    
    def test_generate_response_trusting_npc(self):
        """Test response generation for trusting NPC"""
        player_input = "Hello, can you help me?"
        
        response = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.trusting_emotion_state,
            memory_context=self.kindness_memories,
            player_input=player_input,
            campaign_id=self.campaign_id
        )
        
        # Check behavior modifiers reflect trust
        self.assertIn('friendly', response.behavior_modifiers.tone_modifier.lower())
        self.assertGreater(response.behavior_modifiers.cooperation_level, 0.8)
        self.assertGreater(response.behavior_modifiers.trust_level, 0.8)
        self.assertEqual(response.behavior_modifiers.detail_level, 'detailed')
    
    def test_generate_response_neutral_npc(self):
        """Test response generation for neutral NPC"""
        player_input = "Hello, can you help me?"
        
        response = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.neutral_emotion_state,
            memory_context=self.empty_memories,
            player_input=player_input,
            campaign_id=self.campaign_id
        )
        
        # Check behavior modifiers reflect neutrality
        self.assertIn('calm', response.behavior_modifiers.tone_modifier.lower())
        self.assertAlmostEqual(response.behavior_modifiers.cooperation_level, 0.7, delta=0.1)
        self.assertAlmostEqual(response.behavior_modifiers.trust_level, 0.6, delta=0.1)
        self.assertEqual(response.behavior_modifiers.detail_level, 'normal')
    
    def test_memory_driven_behavior_modifiers(self):
        """Test memory-driven behavior modifications"""
        # Test betrayal memory impact
        response_betrayal = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.neutral_emotion_state,
            memory_context=self.betrayal_memories,
            player_input="Hello",
            campaign_id=self.campaign_id
        )
        
        # Test kindness memory impact
        response_kindness = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.neutral_emotion_state,
            memory_context=self.kindness_memories,
            player_input="Hello",
            campaign_id=self.campaign_id
        )
        
        # Betrayal should reduce cooperation and trust
        self.assertLess(
            response_betrayal.behavior_modifiers.cooperation_level,
            response_kindness.behavior_modifiers.cooperation_level
        )
        self.assertLess(
            response_betrayal.behavior_modifiers.trust_level,
            response_kindness.behavior_modifiers.trust_level
        )
    
    def test_response_confidence_calculation(self):
        """Test response confidence calculation"""
        # High stability, relevant memories
        response_high_confidence = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.trusting_emotion_state,
            memory_context=self.kindness_memories,
            player_input="Hello",
            campaign_id=self.campaign_id
        )
        
        # Low stability, no memories
        low_stability_state = self.neutral_emotion_state.copy()
        low_stability_state['emotional_stability'] = 0.2
        
        response_low_confidence = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=low_stability_state,
            memory_context=self.empty_memories,
            player_input="Hello",
            campaign_id=self.campaign_id
        )
        
        # High confidence response should have higher confidence
        self.assertGreater(
            response_high_confidence.response_confidence,
            response_low_confidence.response_confidence
        )
        
        # Both should be between 0 and 1
        self.assertGreaterEqual(response_high_confidence.response_confidence, 0.0)
        self.assertLessEqual(response_high_confidence.response_confidence, 1.0)
        self.assertGreaterEqual(response_low_confidence.response_confidence, 0.0)
        self.assertLessEqual(response_low_confidence.response_confidence, 1.0)
    
    def test_behavior_modifier_reasoning(self):
        """Test behavior modifier reasoning generation"""
        response = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.angry_emotion_state,
            memory_context=self.betrayal_memories,
            player_input="Hello",
            campaign_id=self.campaign_id
        )
        
        reasoning = response.behavior_modifiers.reasoning
        
        # Check reasoning includes key elements
        self.assertIn('anger', reasoning.lower())
        self.assertIn('betrayal', reasoning.lower())
        self.assertIsInstance(reasoning, str)
        self.assertGreater(len(reasoning), 0)
    
    def test_campaign_aware_behavior_history(self):
        """Test campaign-aware behavior history tracking"""
        campaign_1 = "Campaign1"
        campaign_2 = "Campaign2"
        
        # Generate responses for different campaigns
        response_1 = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.angry_emotion_state,
            memory_context=self.betrayal_memories,
            player_input="Hello",
            campaign_id=campaign_1
        )
        
        response_2 = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.trusting_emotion_state,
            memory_context=self.kindness_memories,
            player_input="Hello",
            campaign_id=campaign_2
        )
        
        # Get behavior history for each campaign
        history_1 = self.behavior_engine.get_behavior_history(
            npc_id=self.npc_id, campaign_id=campaign_1
        )
        history_2 = self.behavior_engine.get_behavior_history(
            npc_id=self.npc_id, campaign_id=campaign_2
        )
        
        # Check that histories are separate
        self.assertEqual(len(history_1), 1)
        self.assertEqual(len(history_2), 1)
        self.assertNotEqual(history_1[0]['emotional_state']['dominant_emotion'],
                           history_2[0]['emotional_state']['dominant_emotion'])
    
    def test_response_text_variation(self):
        """Test that response text varies based on emotional state"""
        responses = []
        
        # Generate responses for different emotional states
        for emotion_state in [self.angry_emotion_state, self.trusting_emotion_state, self.neutral_emotion_state]:
            response = self.behavior_engine.generate_response(
                npc_id=self.npc_id,
                emotion_state=emotion_state,
                memory_context=self.empty_memories,
                player_input="Hello",
                campaign_id=self.campaign_id
            )
            responses.append(response.response_text)
        
        # Responses should be different (allowing for some randomness)
        unique_responses = set(responses)
        self.assertGreater(len(unique_responses), 1)
    
    def test_behavior_modifier_consistency(self):
        """Test consistency of behavior modifiers"""
        response = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.angry_emotion_state,
            memory_context=self.betrayal_memories,
            player_input="Hello",
            campaign_id=self.campaign_id
        )
        
        modifiers = response.behavior_modifiers
        
        # Check that modifiers are within valid ranges
        self.assertGreaterEqual(modifiers.cooperation_level, 0.0)
        self.assertLessEqual(modifiers.cooperation_level, 1.0)
        self.assertGreaterEqual(modifiers.trust_level, 0.0)
        self.assertLessEqual(modifiers.trust_level, 1.0)
        
        # Check that detail level is valid
        valid_detail_levels = ['minimal', 'normal', 'detailed']
        self.assertIn(modifiers.detail_level, valid_detail_levels)
        
        # Check that tone and pacing modifiers are strings
        self.assertIsInstance(modifiers.tone_modifier, str)
        self.assertIsInstance(modifiers.pacing_modifier, str)
        self.assertGreater(len(modifiers.tone_modifier), 0)
        self.assertGreater(len(modifiers.pacing_modifier), 0)
    
    def test_json_compatibility(self):
        """Test JSON compatibility of NPC responses"""
        response = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.trusting_emotion_state,
            memory_context=self.kindness_memories,
            player_input="Hello",
            campaign_id=self.campaign_id
        )
        
        # Test that response can be serialized to JSON
        try:
            response_dict = {
                'npc_id': response.npc_id,
                'response_text': response.response_text,
                'emotional_state': response.emotional_state,
                'memory_influence': response.memory_influence,
                'response_confidence': response.response_confidence,
                'timestamp': response.timestamp
            }
            json.dumps(response_dict)
        except (TypeError, ValueError) as e:
            self.fail(f"NPC response not JSON serializable: {e}")
        
        # Test that behavior modifiers can be serialized
        try:
            modifiers_dict = {
                'tone_modifier': response.behavior_modifiers.tone_modifier,
                'pacing_modifier': response.behavior_modifiers.pacing_modifier,
                'cooperation_level': response.behavior_modifiers.cooperation_level,
                'detail_level': response.behavior_modifiers.detail_level,
                'trust_level': response.behavior_modifiers.trust_level,
                'reasoning': response.behavior_modifiers.reasoning
            }
            json.dumps(modifiers_dict)
        except (TypeError, ValueError) as e:
            self.fail(f"Behavior modifiers not JSON serializable: {e}")
    
    def test_npc_personality_setting(self):
        """Test NPC personality trait setting"""
        personality_traits = {
            'bravery': 0.8,
            'wisdom': 0.9,
            'charisma': 0.6,
            'background': 'former soldier'
        }
        
        self.behavior_engine.set_npc_personality(
            npc_id=self.npc_id,
            personality_traits=personality_traits,
            campaign_id=self.campaign_id
        )
        
        # Check that personality was stored
        key = f"{self.campaign_id}_{self.npc_id}"
        self.assertIn(key, self.behavior_engine.npc_personalities)
        self.assertEqual(
            self.behavior_engine.npc_personalities[key],
            personality_traits
        )
    
    def test_emotional_realism_alignment(self):
        """Test that responses align with emotional realism principle"""
        # Test that angry NPCs are less cooperative
        angry_response = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.angry_emotion_state,
            memory_context=self.betrayal_memories,
            player_input="Can you help me?",
            campaign_id=self.campaign_id
        )
        
        # Test that trusting NPCs are more cooperative
        trusting_response = self.behavior_engine.generate_response(
            npc_id=self.npc_id,
            emotion_state=self.trusting_emotion_state,
            memory_context=self.kindness_memories,
            player_input="Can you help me?",
            campaign_id=self.campaign_id
        )
        
        # Angry NPC should be less cooperative than trusting NPC
        self.assertLess(
            angry_response.behavior_modifiers.cooperation_level,
            trusting_response.behavior_modifiers.cooperation_level
        )
        
        # Angry NPC should have lower trust level
        self.assertLess(
            angry_response.behavior_modifiers.trust_level,
            trusting_response.behavior_modifiers.trust_level
        )
        
        # Angry NPC should give less detailed responses
        self.assertNotEqual(
            angry_response.behavior_modifiers.detail_level,
            'detailed'
        )

if __name__ == '__main__':
    unittest.main() 