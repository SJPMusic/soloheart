"""
The Narrative Engine Demo
=========================

Demonstrates the core capabilities of The Narrative Engine across multiple domains.
Shows memory system, narrative creation, analysis, and adaptation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.narrative_engine import NarrativeEngine, NarrativeDomain, StoryStructure, CharacterRole, PlotPointType
from core.memory_system import MemoryType, MemoryLayer, EmotionalContext
import json

def demo_gaming_narrative():
    """Demonstrate gaming narrative creation and analysis."""
    print("\n🎮 GAMING NARRATIVE DEMO")
    print("=" * 50)
    
    engine = NarrativeEngine()
    
    # Create a gaming narrative
    narrative = engine.create_narrative(
        title="The Lost Kingdom",
        description="An epic fantasy adventure where heroes must restore a fallen kingdom",
        domain=NarrativeDomain.GAMING,
        story_structure=StoryStructure.HERO_JOURNEY
    )
    
    print(f"Created narrative: {narrative.title}")
    
    # Add characters
    hero = engine.add_character(narrative.id, {
        'name': 'Aria',
        'role': CharacterRole.PROTAGONIST,
        'description': 'A young warrior with mysterious powers',
        'traits': ['brave', 'curious', 'determined'],
        'goals': ['Restore the kingdom', 'Discover her true heritage'],
        'conflicts': ['Internal struggle with power', 'External threat from dark forces'],
        'background': {'origin': 'Unknown', 'training': 'Self-taught warrior'}
    })
    
    mentor = engine.add_character(narrative.id, {
        'name': 'Eldric',
        'role': CharacterRole.MENTOR,
        'description': 'Wise old wizard who guides the hero',
        'traits': ['wise', 'mysterious', 'protective'],
        'goals': ['Guide Aria to her destiny', 'Protect ancient knowledge'],
        'conflicts': ['Balancing guidance with independence'],
        'background': {'origin': 'Ancient order', 'knowledge': 'Arcane secrets'}
    })
    
    print(f"Added characters: {hero.name}, {mentor.name}")
    
    # Generate plot points
    inciting_incident = engine.generate_plot_point(narrative.id, {
        'type': PlotPointType.INCITING_INCIDENT,
        'title': 'The Prophecy Revealed',
        'description': 'Aria discovers an ancient prophecy about her role in restoring the kingdom',
        'characters_involved': [hero.id],
        'narrative_significance': 0.9,
        'thematic_elements': ['destiny', 'prophecy', 'discovery'],
        'world_state_changes': {'prophecy_known': True}
    })
    
    first_turning = engine.generate_plot_point(narrative.id, {
        'type': PlotPointType.FIRST_TURNING_POINT,
        'title': 'The Dark Army Rises',
        'description': 'Ancient enemies return, forcing Aria to begin her quest',
        'characters_involved': [hero.id, mentor.id],
        'narrative_significance': 0.8,
        'thematic_elements': ['conflict', 'urgency', 'responsibility'],
        'world_state_changes': {'dark_army_active': True, 'quest_begun': True}
    })
    
    print(f"Generated plot points: {inciting_incident.title}, {first_turning.title}")
    
    # Analyze the narrative
    analysis = engine.analyze_narrative(narrative.id)
    print(f"\nNarrative Analysis:")
    print(f"- Coherence Score: {analysis.coherence_score:.2f}")
    print(f"- Plot Complexity: {analysis.plot_complexity:.2f}")
    print(f"- Themes: {', '.join(analysis.themes)}")
    print(f"- Character Development: {len(analysis.character_development)} characters tracked")
    
    return narrative

def demo_therapy_narrative():
    """Demonstrate therapeutic narrative creation and analysis."""
    print("\n🧠 THERAPY NARRATIVE DEMO")
    print("=" * 50)
    
    engine = NarrativeEngine()
    
    # Create a therapy narrative
    narrative = engine.create_narrative(
        title="Journey to Healing",
        description="A personal growth story about overcoming trauma and finding inner peace",
        domain=NarrativeDomain.THERAPY,
        story_structure=StoryStructure.CIRCULAR
    )
    
    print(f"Created narrative: {narrative.title}")
    
    # Add characters (representing aspects of self)
    inner_child = engine.add_character(narrative.id, {
        'name': 'Inner Child',
        'role': CharacterRole.PROTAGONIST,
        'description': 'The vulnerable, authentic self that needs healing',
        'traits': ['vulnerable', 'creative', 'innocent'],
        'goals': ['Feel safe and loved', 'Express authentic self'],
        'conflicts': ['Fear of rejection', 'Past trauma memories'],
        'background': {'trauma_history': 'Childhood experiences', 'coping_mechanisms': 'Withdrawal'}
    })
    
    inner_healer = engine.add_character(narrative.id, {
        'name': 'Inner Healer',
        'role': CharacterRole.MENTOR,
        'description': 'The wise, compassionate part that guides healing',
        'traits': ['compassionate', 'wise', 'patient'],
        'goals': ['Guide healing process', 'Restore wholeness'],
        'conflicts': ['Balancing guidance with self-discovery'],
        'background': {'healing_approach': 'Gentle, patient', 'knowledge': 'Inner wisdom'}
    })
    
    print(f"Added characters: {inner_child.name}, {inner_healer.name}")
    
    # Generate therapeutic plot points
    awareness = engine.generate_plot_point(narrative.id, {
        'type': PlotPointType.INCITING_INCIDENT,
        'title': 'Recognition of Pain',
        'description': 'The person becomes aware of their emotional wounds and need for healing',
        'characters_involved': [inner_child.id],
        'narrative_significance': 0.9,
        'thematic_elements': ['awareness', 'vulnerability', 'acceptance'],
        'world_state_changes': {'healing_journey_begun': True, 'pain_acknowledged': True}
    })
    
    acceptance = engine.generate_plot_point(narrative.id, {
        'type': PlotPointType.FIRST_TURNING_POINT,
        'title': 'Self-Acceptance',
        'description': 'Learning to accept and love all parts of oneself, including the wounded child',
        'characters_involved': [inner_child.id, inner_healer.id],
        'narrative_significance': 0.8,
        'thematic_elements': ['self-acceptance', 'compassion', 'integration'],
        'world_state_changes': {'self_acceptance_achieved': True}
    })
    
    print(f"Generated plot points: {awareness.title}, {acceptance.title}")
    
    # Analyze the narrative
    analysis = engine.analyze_narrative(narrative.id)
    print(f"\nNarrative Analysis:")
    print(f"- Coherence Score: {analysis.coherence_score:.2f}")
    print(f"- Plot Complexity: {analysis.plot_complexity:.2f}")
    print(f"- Themes: {', '.join(analysis.themes)}")
    print(f"- Recommendations: {analysis.recommendations[0] if analysis.recommendations else 'None'}")
    
    return narrative

def demo_education_narrative():
    """Demonstrate educational narrative creation and analysis."""
    print("\n📚 EDUCATION NARRATIVE DEMO")
    print("=" * 50)
    
    engine = NarrativeEngine()
    
    # Create an educational narrative
    narrative = engine.create_narrative(
        title="The Learning Journey",
        description="A student's journey through mastering complex concepts and developing skills",
        domain=NarrativeDomain.EDUCATION,
        story_structure=StoryStructure.EPISODIC
    )
    
    print(f"Created narrative: {narrative.title}")
    
    # Add characters
    student = engine.add_character(narrative.id, {
        'name': 'Alex',
        'role': CharacterRole.PROTAGONIST,
        'description': 'A curious student learning advanced mathematics',
        'traits': ['curious', 'persistent', 'analytical'],
        'goals': ['Master calculus', 'Understand mathematical beauty'],
        'conflicts': ['Math anxiety', 'Complex problem solving'],
        'background': {'learning_style': 'Visual and hands-on', 'strengths': 'Pattern recognition'}
    })
    
    teacher = engine.add_character(narrative.id, {
        'name': 'Dr. Chen',
        'role': CharacterRole.MENTOR,
        'description': 'Inspiring mathematics professor who makes complex concepts accessible',
        'traits': ['patient', 'inspiring', 'knowledgeable'],
        'goals': ['Help students discover math joy', 'Build confidence'],
        'conflicts': ['Balancing rigor with accessibility'],
        'background': {'teaching_approach': 'Discovery-based', 'expertise': 'Applied mathematics'}
    })
    
    print(f"Added characters: {student.name}, {teacher.name}")
    
    # Generate educational plot points
    challenge = engine.generate_plot_point(narrative.id, {
        'type': PlotPointType.INCITING_INCIDENT,
        'title': 'The Calculus Challenge',
        'description': 'Alex encounters their first truly difficult calculus problem',
        'characters_involved': [student.id, teacher.id],
        'narrative_significance': 0.8,
        'thematic_elements': ['challenge', 'growth', 'perseverance'],
        'world_state_changes': {'calculus_learning_begun': True, 'confidence_tested': True}
    })
    
    breakthrough = engine.generate_plot_point(narrative.id, {
        'type': PlotPointType.FIRST_TURNING_POINT,
        'title': 'The Aha Moment',
        'description': 'Alex experiences a breakthrough in understanding calculus concepts',
        'characters_involved': [student.id],
        'narrative_significance': 0.9,
        'thematic_elements': ['breakthrough', 'understanding', 'confidence'],
        'world_state_changes': {'calculus_understood': True, 'confidence_boosted': True}
    })
    
    print(f"Generated plot points: {challenge.title}, {breakthrough.title}")
    
    # Analyze the narrative
    analysis = engine.analyze_narrative(narrative.id)
    print(f"\nNarrative Analysis:")
    print(f"- Coherence Score: {analysis.coherence_score:.2f}")
    print(f"- Plot Complexity: {analysis.plot_complexity:.2f}")
    print(f"- Themes: {', '.join(analysis.themes)}")
    print(f"- Structural Integrity: {analysis.structural_integrity:.2f}")
    
    return narrative

def demo_memory_system():
    """Demonstrate the memory system capabilities."""
    print("\n🧠 MEMORY SYSTEM DEMO")
    print("=" * 50)
    
    engine = NarrativeEngine()
    
    # Add various types of memories
    engine.memory_system.add_memory(
        content={'event': 'Character creation', 'character': 'Aria', 'domain': 'gaming'},
        memory_type=MemoryType.CHARACTER_DEVELOPMENT,
        layer=MemoryLayer.MID_TERM,
        user_id='demo_user',
        session_id='demo_session_1',
        emotional_weight=0.7,
        emotional_context=[EmotionalContext.JOY, EmotionalContext.ANTICIPATION],
        thematic_tags=['character_creation', 'gaming', 'hero_journey']
    )
    
    engine.memory_system.add_memory(
        content={'event': 'Plot point generation', 'plot': 'The Prophecy Revealed', 'significance': 'high'},
        memory_type=MemoryType.PLOT_POINT,
        layer=MemoryLayer.MID_TERM,
        user_id='demo_user',
        session_id='demo_session_1',
        emotional_weight=0.8,
        emotional_context=[EmotionalContext.SURPRISE, EmotionalContext.CURIOSITY],
        thematic_tags=['prophecy', 'destiny', 'discovery']
    )
    
    engine.memory_system.add_memory(
        content={'event': 'Narrative analysis', 'coherence': 0.85, 'themes': ['destiny', 'heroism']},
        memory_type=MemoryType.THEME,
        layer=MemoryLayer.LONG_TERM,
        user_id='demo_user',
        session_id='demo_session_1',
        emotional_weight=0.6,
        emotional_context=[EmotionalContext.TRUST],
        thematic_tags=['analysis', 'coherence', 'thematic_analysis']
    )
    
    print("Added memories to the system")
    
    # Recall memories
    gaming_memories = engine.memory_system.recall(
        thematic=['gaming'],
        limit=5
    )
    
    emotional_memories = engine.memory_system.recall(
        emotional=EmotionalContext.JOY,
        limit=5
    )
    
    print(f"Recalled {len(gaming_memories)} gaming-related memories")
    print(f"Recalled {len(emotional_memories)} joy-related memories")
    
    # Get memory statistics
    stats = engine.memory_system.get_memory_stats()
    print(f"\nMemory System Statistics:")
    print(f"- Total memories created: {stats['created']}")
    print(f"- Short-term memories: {stats['short_term_count']}")
    print(f"- Mid-term memories: {stats['mid_term_count']}")
    print(f"- Long-term memories: {stats['long_term_count']}")
    print(f"- User profiles: {stats['user_profiles_count']}")

def demo_cross_domain_analysis():
    """Demonstrate cross-domain narrative analysis."""
    print("\n🔄 CROSS-DOMAIN ANALYSIS DEMO")
    print("=" * 50)
    
    engine = NarrativeEngine()
    
    # Create narratives in different domains
    gaming_narrative = demo_gaming_narrative()
    therapy_narrative = demo_therapy_narrative()
    education_narrative = demo_education_narrative()
    
    # Get overall statistics
    stats = engine.get_narrative_stats()
    print(f"\nCross-Domain Statistics:")
    print(f"- Total narratives: {stats['total_narratives']}")
    print(f"- Narratives by domain: {stats['narratives_by_domain']}")
    print(f"- Total characters: {stats['total_characters']}")
    print(f"- Total plot points: {stats['total_plot_points']}")
    
    # Export a narrative
    export_data = engine.export_narrative(gaming_narrative.id)
    print(f"\nExported narrative '{gaming_narrative.title}' with {len(export_data['narrative']['characters'])} characters and {len(export_data['narrative']['plot_points'])} plot points")
    
    # Import the narrative (simulating sharing between systems)
    imported_id = engine.import_narrative(export_data)
    print(f"Imported narrative with ID: {imported_id}")
    
    return engine

def main():
    """Run the complete demo."""
    print("🚀 THE NARRATIVE ENGINE DEMO")
    print("=" * 60)
    print("This demo showcases the core capabilities of The Narrative Engine")
    print("across multiple domains: gaming, therapy, education, and more.")
    print()
    
    try:
        # Run individual domain demos
        demo_gaming_narrative()
        demo_therapy_narrative()
        demo_education_narrative()
        
        # Run memory system demo
        demo_memory_system()
        
        # Run cross-domain analysis
        engine = demo_cross_domain_analysis()
        
        print("\n✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("The Narrative Engine successfully demonstrated:")
        print("✓ Multi-domain narrative creation")
        print("✓ Character development tracking")
        print("✓ Plot point generation")
        print("✓ Narrative analysis and coherence scoring")
        print("✓ Layered memory system with emotional context")
        print("✓ Cross-domain statistics and insights")
        print("✓ Export/import functionality")
        print()
        print("The engine is ready for integration with domain-specific adapters")
        print("and can be extended for various narrative applications.")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 