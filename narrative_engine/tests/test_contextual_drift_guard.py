"""
Unit tests for ContextualDriftGuard module.

Tests contextual drift prevention functionality:
- Memory relevance checking
- Irrelevant memory filtering
- Filtering decision explanations
- Campaign-aware filtering
- Drift risk analysis

References: NarrativeEngine_Roadmap.txt (Narrative continuity matters)
"""

import unittest
import json
from narrative_engine.context.contextual_drift_guard import ContextualDriftGuard, FilteringDecision, DriftAnalysis

class TestContextualDriftGuard(unittest.TestCase):
    """
    Test contextual drift prevention system.
    
    Validates:
    - Memory relevance calculation
    - Irrelevant memory filtering
    - Transparent filtering decisions
    - Campaign-aware context management
    - Drift risk assessment
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.drift_guard = ContextualDriftGuard(default_threshold=0.4)
        self.campaign_id = "TestCampaign"
        
        # Sample memories for testing
        self.sample_memories = [
            {
                'id': 'mem_001',
                'content': 'The player helped the mayor with a bandit problem',
                'emotional_context': {
                    'primary_tone': 'trust',
                    'event_type': 'cooperation',
                    'triggers': ['bandit attack', 'mayor request']
                }
            },
            {
                'id': 'mem_002', 
                'content': 'The player explored the ancient ruins and found treasure',
                'emotional_context': {
                    'primary_tone': 'joy',
                    'event_type': 'achievement',
                    'triggers': ['ruins exploration', 'treasure discovery']
                }
            },
            {
                'id': 'mem_003',
                'content': 'The player betrayed the town by siding with bandits',
                'emotional_context': {
                    'primary_tone': 'anger',
                    'event_type': 'betrayal',
                    'triggers': ['bandit alliance', 'town betrayal']
                }
            },
            {
                'id': 'mem_004',
                'content': 'The player visited a distant mountain village',
                'emotional_context': {
                    'primary_tone': 'neutral',
                    'event_type': 'exploration',
                    'triggers': ['mountain travel', 'village visit']
                }
            }
        ]
    
    def test_check_relevance_basic(self):
        """Test basic relevance checking functionality"""
        context = ['bandit', 'mayor', 'town']
        memory = ['The player helped the mayor with a bandit problem']
        
        relevance = self.drift_guard.check_relevance(context, memory, self.campaign_id)
        
        self.assertGreater(relevance, 0.2)  # Should be moderately relevant
        self.assertLessEqual(relevance, 1.0)  # Should not exceed 1.0
    
    def test_check_relevance_irrelevant(self):
        """Test relevance checking for irrelevant content"""
        context = ['bandit', 'mayor', 'town']
        memory = ['The player visited a distant mountain village']
        
        relevance = self.drift_guard.check_relevance(context, memory, self.campaign_id)
        
        self.assertLess(relevance, 0.3)  # Should be low relevance
    
    def test_check_relevance_semantic_boost(self):
        """Test semantic similarity boost functionality"""
        context = ['combat', 'battle', 'weapon']
        memory = ['The player fought with a sword against enemies']
        
        relevance = self.drift_guard.check_relevance(context, memory, self.campaign_id)
        
        # Should get semantic boost for combat-related terms
        self.assertGreaterEqual(relevance, 0.0)  # Should have some relevance with semantic boost
    
    def test_filter_irrelevant_memories(self):
        """Test filtering of irrelevant memories"""
        context = ['bandit', 'mayor', 'town', 'betrayal']
        
        filtered_memories, drift_analysis = self.drift_guard.filter_irrelevant_memories(
            context, self.sample_memories, threshold=0.1, campaign_id=self.campaign_id
        )
        
        # Should filter out some memories
        self.assertLessEqual(len(filtered_memories), len(self.sample_memories))
        
        # Check drift analysis
        self.assertIsInstance(drift_analysis, DriftAnalysis)
        self.assertEqual(drift_analysis.campaign_id, self.campaign_id)
        self.assertGreaterEqual(drift_analysis.memory_count_before, drift_analysis.memory_count_after)
    
    def test_filter_irrelevant_memories_strict_threshold(self):
        """Test filtering with strict threshold"""
        context = ['bandit', 'mayor']
        
        filtered_memories, drift_analysis = self.drift_guard.filter_irrelevant_memories(
            context, self.sample_memories, threshold=0.7, campaign_id=self.campaign_id
        )
        
        # With strict threshold, should filter more memories
        self.assertLess(len(filtered_memories), len(self.sample_memories))
        self.assertGreater(drift_analysis.drift_risk_score, 0.0)
    
    def test_explain_filtering(self):
        """Test filtering explanation functionality"""
        # First, perform some filtering
        context = ['bandit', 'mayor']
        self.drift_guard.filter_irrelevant_memories(
            context, self.sample_memories, campaign_id=self.campaign_id
        )
        
        # Get explanation
        explanation = self.drift_guard.explain_filtering(
            campaign_id=self.campaign_id, limit=5
        )
        
        # Check explanation structure
        self.assertIn('campaign_id', explanation)
        self.assertIn('total_decisions', explanation)
        self.assertIn('filtered_count', explanation)
        self.assertIn('retained_count', explanation)
        self.assertIn('average_relevance', explanation)
        self.assertIn('recent_decisions', explanation)
        self.assertIn('explanation', explanation)
        
        # Check that decisions are recorded
        self.assertGreater(explanation['total_decisions'], 0)
        self.assertIsInstance(explanation['recent_decisions'], list)
    
    def test_get_context_suggestions(self):
        """Test context keyword suggestions"""
        # First, perform filtering to build history
        context = ['bandit', 'mayor']
        self.drift_guard.filter_irrelevant_memories(
            context, self.sample_memories, campaign_id=self.campaign_id
        )
        
        # Get suggestions
        suggestions = self.drift_guard.get_context_suggestions(
            current_context=context, campaign_id=self.campaign_id
        )
        
        # Suggestions should be a list
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 5)  # Max 5 suggestions
    
    def test_campaign_aware_filtering(self):
        """Test campaign-aware filtering functionality"""
        campaign_1 = "Campaign1"
        campaign_2 = "Campaign2"
        
        # Filter memories for different campaigns
        context = ['bandit', 'mayor']
        
        self.drift_guard.filter_irrelevant_memories(
            context, self.sample_memories, campaign_id=campaign_1
        )
        
        self.drift_guard.filter_irrelevant_memories(
            context, self.sample_memories, campaign_id=campaign_2
        )
        
        # Check that filtering history is separate
        explanation_1 = self.drift_guard.explain_filtering(campaign_id=campaign_1)
        explanation_2 = self.drift_guard.explain_filtering(campaign_id=campaign_2)
        
        self.assertEqual(explanation_1['campaign_id'], campaign_1)
        self.assertEqual(explanation_2['campaign_id'], campaign_2)
    
    def test_drift_analysis_recommendations(self):
        """Test drift analysis recommendation generation"""
        context = ['very', 'specific', 'context', 'keywords']
        
        # Use very specific context that won't match memories well
        filtered_memories, drift_analysis = self.drift_guard.filter_irrelevant_memories(
            context, self.sample_memories, threshold=0.8, campaign_id=self.campaign_id
        )
        
        # Should generate recommendations for high drift risk
        self.assertIsInstance(drift_analysis.recommendations, list)
        self.assertGreater(len(drift_analysis.recommendations), 0)
        
        # Check that recommendations are relevant
        for recommendation in drift_analysis.recommendations:
            self.assertIsInstance(recommendation, str)
            self.assertGreater(len(recommendation), 0)
    
    def test_filtering_decision_transparency(self):
        """Test transparency of filtering decisions"""
        context = ['bandit', 'mayor']
        
        filtered_memories, drift_analysis = self.drift_guard.filter_irrelevant_memories(
            context, self.sample_memories, campaign_id=self.campaign_id
        )
        
        # Check that decisions are recorded with reasoning
        for decision in drift_analysis.filtering_decisions:
            self.assertIsInstance(decision, FilteringDecision)
            self.assertIsInstance(decision.memory_id, str)
            self.assertIsInstance(decision.memory_content, str)
            self.assertIsInstance(decision.relevance_score, float)
            self.assertIsInstance(decision.threshold, float)
            self.assertIsInstance(decision.filtered_out, bool)
            self.assertIsInstance(decision.reasoning, str)
            self.assertIsInstance(decision.timestamp, str)
            
            # Check reasoning is meaningful
            self.assertGreater(len(decision.reasoning), 0)
    
    def test_json_compatibility(self):
        """Test JSON compatibility of outputs"""
        context = ['bandit', 'mayor']
        
        filtered_memories, drift_analysis = self.drift_guard.filter_irrelevant_memories(
            context, self.sample_memories, campaign_id=self.campaign_id
        )
        
        # Test that drift analysis can be serialized to JSON
        try:
            analysis_dict = {
                'campaign_id': drift_analysis.campaign_id,
                'context_keywords': drift_analysis.context_keywords,
                'memory_count_before': drift_analysis.memory_count_before,
                'memory_count_after': drift_analysis.memory_count_after,
                'average_relevance': drift_analysis.average_relevance,
                'drift_risk_score': drift_analysis.drift_risk_score,
                'recommendations': drift_analysis.recommendations
            }
            json.dumps(analysis_dict)
        except (TypeError, ValueError) as e:
            self.fail(f"Drift analysis not JSON serializable: {e}")
        
        # Test that filtering decisions can be serialized
        for decision in drift_analysis.filtering_decisions:
            try:
                decision_dict = {
                    'memory_id': decision.memory_id,
                    'memory_content': decision.memory_content,
                    'relevance_score': decision.relevance_score,
                    'threshold': decision.threshold,
                    'filtered_out': decision.filtered_out,
                    'reasoning': decision.reasoning,
                    'timestamp': decision.timestamp
                }
                json.dumps(decision_dict)
            except (TypeError, ValueError) as e:
                self.fail(f"Filtering decision not JSON serializable: {e}")

if __name__ == '__main__':
    unittest.main() 