"""
Test The Narrative Engine Core Functionality
===========================================

Basic tests to verify the core narrative engine works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from narrative_engine.core.narrative_engine import NarrativeEngine, NarrativeDomain, StoryStructure, CharacterRole, PlotPointType
from narrative_engine.memory.layered_memory import MemoryType, MemoryLayer, EmotionalContext

class TestNarrativeEngine(unittest.TestCase):
    """Test the core narrative engine functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = NarrativeEngine()
    
    def test_create_narrative(self):
        """Test narrative creation."""
        narrative = self.engine.create_narrative(
            title="Test Narrative",
            description="A test narrative for unit testing",
            domain=NarrativeDomain.GAMING,
            story_structure=StoryStructure.THREE_ACT
        )
        
        self.assertIsNotNone(narrative.id)
        self.assertEqual(narrative.title, "Test Narrative")
        self.assertEqual(narrative.domain, NarrativeDomain.GAMING)
        self.assertEqual(narrative.story_structure, StoryStructure.THREE_ACT)
        self.assertEqual(len(narrative.characters), 0)
        self.assertEqual(len(narrative.plot_points), 0)
    
    def test_add_character(self):
        """Test character addition."""
        narrative = self.engine.create_narrative(
            title="Character Test",
            description="Testing character addition",
            domain=NarrativeDomain.GAMING
        )
        
        character = self.engine.add_character(narrative.id, {
            'name': 'Test Hero',
            'role': CharacterRole.PROTAGONIST,
            'description': 'A test character',
            'traits': ['brave', 'curious'],
            'goals': ['Save the world'],
            'conflicts': ['Internal struggle']
        })
        
        self.assertIsNotNone(character.id)
        self.assertEqual(character.name, 'Test Hero')
        self.assertEqual(character.role, CharacterRole.PROTAGONIST)
        self.assertEqual(len(narrative.characters), 1)
        self.assertIn(character.id, narrative.characters)
    
    def test_generate_plot_point(self):
        """Test plot point generation."""
        narrative = self.engine.create_narrative(
            title="Plot Test",
            description="Testing plot point generation",
            domain=NarrativeDomain.GAMING
        )
        
        plot_point = self.engine.generate_plot_point(narrative.id, {
            'type': PlotPointType.INCITING_INCIDENT,
            'title': 'The Call to Adventure',
            'description': 'The hero receives a quest',
            'narrative_significance': 0.8,
            'thematic_elements': ['destiny', 'adventure']
        })
        
        self.assertIsNotNone(plot_point.id)
        self.assertEqual(plot_point.plot_point_type, PlotPointType.INCITING_INCIDENT)
        self.assertEqual(plot_point.title, 'The Call to Adventure')
        self.assertEqual(len(narrative.plot_points), 1)
        self.assertIn(plot_point.id, narrative.plot_points)
    
    def test_analyze_narrative(self):
        """Test narrative analysis."""
        narrative = self.engine.create_narrative(
            title="Analysis Test",
            description="Testing narrative analysis",
            domain=NarrativeDomain.GAMING
        )
        
        # Add some content for analysis
        character = self.engine.add_character(narrative.id, {
            'name': 'Hero',
            'role': CharacterRole.PROTAGONIST,
            'description': 'Main character',
            'traits': ['brave'],
            'goals': ['Save world'],
            'conflicts': ['Evil forces']
        })
        
        plot_point = self.engine.generate_plot_point(narrative.id, {
            'type': PlotPointType.INCITING_INCIDENT,
            'title': 'Quest Begins',
            'description': 'The adventure starts',
            'narrative_significance': 0.9,
            'thematic_elements': ['destiny']
        })
        
        analysis = self.engine.analyze_narrative(narrative.id)
        
        self.assertIsNotNone(analysis)
        self.assertGreaterEqual(analysis.coherence_score, 0.0)
        self.assertLessEqual(analysis.coherence_score, 1.0)
        self.assertIsInstance(analysis.themes, list)
        self.assertIsInstance(analysis.character_development, dict)
    
    def test_memory_system(self):
        """Test memory system functionality."""
        # Test memory addition
        memory_id = self.engine.memory_system.add_memory(
            content={'event': 'Test event', 'domain': 'gaming'},
            memory_type=MemoryType.EVENT,
            layer=MemoryLayer.MID_TERM,
            user_id='test_user',
            session_id='test_session',
            emotional_weight=0.5,
            thematic_tags=['test', 'gaming']
        )
        
        self.assertIsNotNone(memory_id)
        
        # Test memory recall
        memories = self.engine.memory_system.recall(
            thematic=['gaming'],
            limit=5
        )
        
        self.assertIsInstance(memories, list)
        self.assertGreater(len(memories), 0)
        
        # Test memory statistics
        stats = self.engine.memory_system.get_memory_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('created', stats)
        self.assertIn('short_term_count', stats)
        self.assertIn('mid_term_count', stats)
        self.assertIn('long_term_count', stats)
    
    def test_domain_adapter_registration(self):
        """Test domain adapter registration."""
        gaming_adapter = GamingAdapter()
        self.engine.register_domain_adapter(NarrativeDomain.GAMING, gaming_adapter)
        
        self.assertIn(NarrativeDomain.GAMING, self.engine.domain_adapters)
        self.assertEqual(self.engine.domain_adapters[NarrativeDomain.GAMING], gaming_adapter)
    
    def test_narrative_stats(self):
        """Test narrative statistics."""
        # Create multiple narratives
        for i in range(3):
            self.engine.create_narrative(
                title=f"Test Narrative {i}",
                description=f"Test narrative {i}",
                domain=NarrativeDomain.GAMING
            )
        
        stats = self.engine.get_narrative_stats()
        
        self.assertEqual(stats['total_narratives'], 3)
        self.assertIn('gaming', stats['narratives_by_domain'])
        self.assertEqual(stats['narratives_by_domain']['gaming'], 3)
        self.assertIn('memory_stats', stats)
    
    def test_export_import_narrative(self):
        """Test narrative export and import."""
        # Create a narrative with content
        narrative = self.engine.create_narrative(
            title="Export Test",
            description="Testing export/import",
            domain=NarrativeDomain.GAMING
        )
        
        character = self.engine.add_character(narrative.id, {
            'name': 'Export Hero',
            'role': CharacterRole.PROTAGONIST,
            'description': 'Character for export test',
            'traits': ['exportable'],
            'goals': ['Test export'],
            'conflicts': ['Import issues']
        })
        
        plot_point = self.engine.generate_plot_point(narrative.id, {
            'type': PlotPointType.INCITING_INCIDENT,
            'title': 'Export Event',
            'description': 'An event to export',
            'narrative_significance': 0.7,
            'thematic_elements': ['export', 'test']
        })
        
        # Export the narrative
        export_data = self.engine.export_narrative(narrative.id)
        
        self.assertIsInstance(export_data, dict)
        self.assertIn('narrative', export_data)
        self.assertIn('analysis', export_data)
        self.assertIn('export_metadata', export_data)
        
        # Import the narrative
        imported_id = self.engine.import_narrative(export_data)
        
        self.assertIsNotNone(imported_id)
        self.assertIn(imported_id, self.engine.narratives)
        
        # Verify imported content
        imported_narrative = self.engine.narratives[imported_id]
        self.assertEqual(imported_narrative.title, "Export Test")
        self.assertEqual(len(imported_narrative.characters), 1)
        self.assertEqual(len(imported_narrative.plot_points), 1)

class TestGamingAdapter(unittest.TestCase):
    """Test the gaming domain adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.adapter = GamingAdapter()
    
    def test_adapter_initialization(self):
        """Test gaming adapter initialization."""
        self.assertEqual(self.adapter.domain, NarrativeDomain.GAMING)
        self.assertIsNotNone(self.adapter.quest_templates)
        self.assertIsNotNone(self.adapter.combat_patterns)
        self.assertIsNotNone(self.adapter.world_building_elements)
    
    def test_quest_templates(self):
        """Test quest template loading."""
        templates = self.adapter.quest_templates
        
        self.assertIn('rescue_quest', templates)
        self.assertIn('collection_quest', templates)
        self.assertIn('elimination_quest', templates)
        
        rescue_quest = templates['rescue_quest']
        self.assertIn('title', rescue_quest)
        self.assertIn('description', rescue_quest)
        self.assertIn('themes', rescue_quest)

if __name__ == '__main__':
    unittest.main() 