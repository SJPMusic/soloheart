#!/usr/bin/env python3
"""
Narrative Engine Demo - Showcasing Domain-Agnostic Capabilities

This demo demonstrates how the Narrative Engine can work across different domains:
- Gaming (DnD-style adventures)
- Therapy (narrative therapy sessions)
- Education (story-based learning)
- Organizational (company narratives)
- Creative Writing (story development)
"""

import json
import sys
import os
from datetime import datetime

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from narrative_engine_core import (
    NarrativeEngineCore, NarrativeDomain, StoryStructure, EmotionalValence,
    Character, Setting, PlotPoint, Theme, BasicNarrativeAnalyzer,
    BasicNarrativeGenerator, BasicDomainAdapter
)


def create_gaming_narrative(engine: NarrativeEngineCore) -> str:
    """Create a DnD-style gaming narrative"""
    print("\n🎲 Creating Gaming Narrative...")
    
    # Create the narrative
    narrative_id = engine.create_narrative(
        "The Lost Artifact of Eldara",
        StoryStructure.HERO_JOURNEY
    )
    
    # Create characters
    protagonist = Character(
        name="Aria the Ranger",
        description="A skilled ranger seeking the lost artifact",
        personality_traits=["brave", "curious", "loyal"],
        motivations=["find the artifact", "prove herself", "protect her village"],
        role="protagonist",
        emotional_state=EmotionalValence.POSITIVE
    )
    
    mentor = Character(
        name="Elder Thorne",
        description="Wise mentor who knows the artifact's location",
        personality_traits=["wise", "mysterious", "protective"],
        motivations=["guide Aria", "protect the artifact", "pass on knowledge"],
        role="mentor",
        emotional_state=EmotionalValence.NEUTRAL
    )
    
    antagonist = Character(
        name="Shadow Lord Malakar",
        description="Dark sorcerer seeking the artifact for evil",
        personality_traits=["ambitious", "ruthless", "powerful"],
        motivations=["obtain the artifact", "gain ultimate power", "destroy Eldara"],
        role="antagonist",
        emotional_state=EmotionalValence.NEGATIVE
    )
    
    # Add characters to narrative
    engine.add_character(narrative_id, protagonist)
    engine.add_character(narrative_id, mentor)
    engine.add_character(narrative_id, antagonist)
    
    # Create setting
    setting = Setting(
        name="The Kingdom of Eldara",
        description="A mystical kingdom with ancient ruins and magical forests",
        location_type="fantasy_kingdom",
        atmosphere="mysterious and magical",
        rules=["magic exists", "ancient artifacts have power", "good vs evil"],
        history="Once a great kingdom, now in decline due to lost artifacts",
        current_state="Threatened by dark forces seeking ancient power"
    )
    
    # Create plot points
    call_to_adventure = PlotPoint(
        name="The Prophecy",
        description="Aria discovers an ancient prophecy about the lost artifact",
        story_structure_position=0.1,
        emotional_impact=EmotionalValence.POSITIVE,
        characters_involved=[protagonist.id],
        conflict_type="internal",
        resolution="Aria decides to embark on the quest"
    )
    
    meeting_mentor = PlotPoint(
        name="Meeting Elder Thorne",
        description="Aria meets the wise Elder Thorne who becomes her mentor",
        story_structure_position=0.2,
        emotional_impact=EmotionalValence.POSITIVE,
        characters_involved=[protagonist.id, mentor.id],
        conflict_type="none",
        resolution="Elder Thorne agrees to guide Aria"
    )
    
    first_conflict = PlotPoint(
        name="Shadow Lord's Ambush",
        description="Malakar's minions ambush Aria in the Dark Forest",
        story_structure_position=0.3,
        emotional_impact=EmotionalValence.NEGATIVE,
        characters_involved=[protagonist.id],
        conflict_type="external",
        resolution="Aria escapes but realizes the danger"
    )
    
    # Add plot points
    engine.add_plot_point(narrative_id, call_to_adventure)
    engine.add_plot_point(narrative_id, meeting_mentor)
    engine.add_plot_point(narrative_id, first_conflict)
    
    print(f"✅ Created gaming narrative: {narrative_id}")
    return narrative_id


def create_therapy_narrative(engine: NarrativeEngineCore) -> str:
    """Create a narrative therapy session"""
    print("\n🧠 Creating Therapy Narrative...")
    
    # Create the narrative
    narrative_id = engine.create_narrative(
        "Sarah's Journey to Self-Acceptance",
        StoryStructure.THREE_ACT
    )
    
    # Create characters (in therapy, these might be different aspects of self)
    client = Character(
        name="Sarah",
        description="A young professional struggling with self-doubt",
        personality_traits=["intelligent", "perfectionist", "anxious"],
        motivations=["find self-acceptance", "overcome anxiety", "build confidence"],
        role="protagonist",
        emotional_state=EmotionalValence.NEGATIVE
    )
    
    inner_critic = Character(
        name="Inner Critic",
        description="Sarah's harsh internal voice",
        personality_traits=["critical", "demanding", "fearful"],
        motivations=["protect Sarah from failure", "maintain high standards"],
        role="internal_antagonist",
        emotional_state=EmotionalValence.NEGATIVE
    )
    
    inner_wisdom = Character(
        name="Inner Wisdom",
        description="Sarah's compassionate inner voice",
        personality_traits=["compassionate", "wise", "supportive"],
        motivations=["help Sarah grow", "promote self-compassion"],
        role="internal_mentor",
        emotional_state=EmotionalValence.POSITIVE
    )
    
    # Add characters
    engine.add_character(narrative_id, client)
    engine.add_character(narrative_id, inner_critic)
    engine.add_character(narrative_id, inner_wisdom)
    
    # Create setting (therapeutic space)
    setting = Setting(
        name="Therapeutic Space",
        description="A safe, supportive environment for self-exploration",
        location_type="therapeutic_environment",
        atmosphere="safe, supportive, non-judgmental",
        rules=["confidentiality", "non-judgment", "self-compassion"],
        history="Sarah has been struggling with self-doubt for years",
        current_state="Beginning to explore her inner narrative"
    )
    
    # Create plot points (therapeutic moments)
    awareness = PlotPoint(
        name="Awareness of Inner Critic",
        description="Sarah becomes aware of her harsh inner voice",
        story_structure_position=0.2,
        emotional_impact=EmotionalValence.NEUTRAL,
        characters_involved=[client.id, inner_critic.id],
        conflict_type="internal",
        resolution="Sarah recognizes the critic's presence"
    )
    
    compassion = PlotPoint(
        name="Meeting Inner Wisdom",
        description="Sarah discovers her compassionate inner voice",
        story_structure_position=0.5,
        emotional_impact=EmotionalValence.POSITIVE,
        characters_involved=[client.id, inner_wisdom.id],
        conflict_type="none",
        resolution="Sarah begins to practice self-compassion"
    )
    
    # Add plot points
    engine.add_plot_point(narrative_id, awareness)
    engine.add_plot_point(narrative_id, compassion)
    
    print(f"✅ Created therapy narrative: {narrative_id}")
    return narrative_id


def create_education_narrative(engine: NarrativeEngineCore) -> str:
    """Create an educational narrative for learning"""
    print("\n📚 Creating Education Narrative...")
    
    # Create the narrative
    narrative_id = engine.create_narrative(
        "The Scientific Method Adventure",
        StoryStructure.THREE_ACT
    )
    
    # Create characters
    student = Character(
        name="Alex",
        description="A curious student learning about the scientific method",
        personality_traits=["curious", "analytical", "enthusiastic"],
        motivations=["learn the scientific method", "solve problems", "discover new things"],
        role="protagonist",
        emotional_state=EmotionalValence.POSITIVE
    )
    
    teacher = Character(
        name="Dr. Maria",
        description="Experienced science teacher guiding Alex",
        personality_traits=["knowledgeable", "patient", "encouraging"],
        motivations=["teach effectively", "inspire curiosity", "guide learning"],
        role="mentor",
        emotional_state=EmotionalValence.POSITIVE
    )
    
    # Add characters
    engine.add_character(narrative_id, student)
    engine.add_character(narrative_id, teacher)
    
    # Create setting
    setting = Setting(
        name="Science Laboratory",
        description="A well-equipped science lab for hands-on learning",
        location_type="educational_environment",
        atmosphere="exciting, safe, collaborative",
        rules=["safety first", "ask questions", "test hypotheses"],
        history="Many students have learned scientific thinking here",
        current_state="Ready for new discoveries"
    )
    
    # Create plot points (learning moments)
    question = PlotPoint(
        name="The Burning Question",
        description="Alex wonders why plants grow better in sunlight",
        story_structure_position=0.1,
        emotional_impact=EmotionalValence.POSITIVE,
        characters_involved=[student.id],
        conflict_type="none",
        resolution="Alex decides to investigate"
    )
    
    hypothesis = PlotPoint(
        name="Forming a Hypothesis",
        description="Alex and Dr. Maria develop a testable hypothesis",
        story_structure_position=0.3,
        emotional_impact=EmotionalValence.POSITIVE,
        characters_involved=[student.id, teacher.id],
        conflict_type="none",
        resolution="They create a clear, testable hypothesis"
    )
    
    experiment = PlotPoint(
        name="The Experiment",
        description="Alex conducts an experiment to test the hypothesis",
        story_structure_position=0.6,
        emotional_impact=EmotionalValence.POSITIVE,
        characters_involved=[student.id, teacher.id],
        conflict_type="none",
        resolution="Alex collects data systematically"
    )
    
    # Add plot points
    engine.add_plot_point(narrative_id, question)
    engine.add_plot_point(narrative_id, hypothesis)
    engine.add_plot_point(narrative_id, experiment)
    
    print(f"✅ Created education narrative: {narrative_id}")
    return narrative_id


def create_organizational_narrative(engine: NarrativeEngineCore) -> str:
    """Create an organizational narrative"""
    print("\n🏢 Creating Organizational Narrative...")
    
    # Create the narrative
    narrative_id = engine.create_narrative(
        "TechCorp's Digital Transformation",
        StoryStructure.FIVE_ACT
    )
    
    # Create characters (organizational roles)
    ceo = Character(
        name="CEO Sarah Chen",
        description="Visionary leader driving digital transformation",
        personality_traits=["visionary", "decisive", "communicative"],
        motivations=["modernize the company", "increase efficiency", "stay competitive"],
        role="protagonist",
        emotional_state=EmotionalValence.POSITIVE
    )
    
    resistance_leader = Character(
        name="Manager Tom Wilson",
        description="Long-time manager resistant to change",
        personality_traits=["traditional", "cautious", "loyal"],
        motivations=["protect his team", "maintain stability", "avoid disruption"],
        role="antagonist",
        emotional_state=EmotionalValence.NEGATIVE
    )
    
    change_agent = Character(
        name="Digital Lead Lisa Park",
        description="Young tech-savvy leader championing change",
        personality_traits=["innovative", "collaborative", "energetic"],
        motivations=["implement new systems", "empower employees", "drive success"],
        role="supporting",
        emotional_state=EmotionalValence.POSITIVE
    )
    
    # Add characters
    engine.add_character(narrative_id, ceo)
    engine.add_character(narrative_id, resistance_leader)
    engine.add_character(narrative_id, change_agent)
    
    # Create setting
    setting = Setting(
        name="TechCorp Headquarters",
        description="A traditional company transitioning to digital-first",
        location_type="corporate_environment",
        atmosphere="transitional, challenging, opportunity-filled",
        rules=["respect all perspectives", "data-driven decisions", "employee well-being"],
        history="50-year-old company with traditional processes",
        current_state="Undergoing major digital transformation"
    )
    
    # Create plot points
    announcement = PlotPoint(
        name="The Transformation Announcement",
        description="CEO announces the digital transformation initiative",
        story_structure_position=0.1,
        emotional_impact=EmotionalValence.NEUTRAL,
        characters_involved=[ceo.id],
        conflict_type="none",
        resolution="Company commits to transformation"
    )
    
    resistance = PlotPoint(
        name="Resistance Emerges",
        description="Tom and other managers express concerns about the changes",
        story_structure_position=0.3,
        emotional_impact=EmotionalValence.NEGATIVE,
        characters_involved=[resistance_leader.id, ceo.id],
        conflict_type="interpersonal",
        resolution="CEO acknowledges concerns and promises support"
    )
    
    collaboration = PlotPoint(
        name="Building Bridges",
        description="Lisa works with Tom to address his concerns",
        story_structure_position=0.6,
        emotional_impact=EmotionalValence.POSITIVE,
        characters_involved=[change_agent.id, resistance_leader.id],
        conflict_type="none",
        resolution="Tom becomes an advocate for change"
    )
    
    # Add plot points
    engine.add_plot_point(narrative_id, announcement)
    engine.add_plot_point(narrative_id, resistance)
    engine.add_plot_point(narrative_id, collaboration)
    
    print(f"✅ Created organizational narrative: {narrative_id}")
    return narrative_id


def demonstrate_analysis(engine: NarrativeEngineCore, narrative_id: str, domain: NarrativeDomain):
    """Demonstrate narrative analysis capabilities"""
    print(f"\n🔍 Analyzing {domain.value} narrative...")
    
    try:
        analysis = engine.analyze_narrative(narrative_id, domain)
        
        print(f"📊 Analysis Results for {domain.value}:")
        print(f"   Coherence Score: {analysis['coherence_score']:.2f}")
        print(f"   Themes Identified: {len(analysis['themes'])}")
        print(f"   Character Arcs: {len(analysis['character_arcs'])}")
        print(f"   Conflicts Detected: {len(analysis['conflicts'])}")
        
        if analysis['themes']:
            print("   Main Themes:")
            for theme in analysis['themes'][:3]:  # Show first 3 themes
                print(f"     - {theme.name}: {theme.message}")
        
        if analysis['conflicts']:
            print("   Conflicts:")
            for conflict in analysis['conflicts'][:2]:  # Show first 2 conflicts
                print(f"     - {conflict['conflict_type']}: {conflict['resolution']}")
                
    except Exception as e:
        print(f"   ❌ Analysis failed: {e}")


def demonstrate_generation(engine: NarrativeEngineCore, narrative_id: str, domain: NarrativeDomain):
    """Demonstrate narrative generation capabilities"""
    print(f"\n✨ Generating next plot point for {domain.value} narrative...")
    
    try:
        context = {
            'user_input': 'Continue the story naturally',
            'current_emotion': 'curious',
            'session_length': 'medium'
        }
        
        plot_point = engine.generate_next_plot_point(narrative_id, domain, context)
        
        print(f"   Generated: {plot_point.name}")
        print(f"   Description: {plot_point.description}")
        print(f"   Position: {plot_point.story_structure_position:.2f}")
        print(f"   Emotional Impact: {plot_point.emotional_impact.name}")
        
        # Add the generated plot point to the narrative
        engine.add_plot_point(narrative_id, plot_point)
        
    except Exception as e:
        print(f"   ❌ Generation failed: {e}")


def demonstrate_adaptation(engine: NarrativeEngineCore, narrative_id: str, target_domain: NarrativeDomain):
    """Demonstrate narrative adaptation capabilities"""
    print(f"\n🔄 Adapting narrative for {target_domain.value} domain...")
    
    try:
        adapted_narrative = engine.adapt_for_domain(narrative_id, target_domain)
        
        print(f"   ✅ Successfully adapted narrative")
        print(f"   New Name: {adapted_narrative.name}")
        print(f"   Characters: {len(adapted_narrative.characters)}")
        print(f"   Plot Points: {len(adapted_narrative.plot_points)}")
        
        # Show domain-specific adaptations
        if adapted_narrative.characters:
            char = adapted_narrative.characters[0]
            domain_tags = [tag for tag in char.tags if tag.startswith('domain:')]
            if domain_tags:
                print(f"   Domain Tags: {domain_tags}")
        
    except Exception as e:
        print(f"   ❌ Adaptation failed: {e}")


def demonstrate_export_import(engine: NarrativeEngineCore, narrative_id: str):
    """Demonstrate export and import capabilities"""
    print(f"\n💾 Demonstrating export/import capabilities...")
    
    try:
        # Export narrative
        export_data = engine.export_narrative(narrative_id)
        
        # Save to file
        filename = f"narrative_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            f.write(export_data)
        
        print(f"   ✅ Exported narrative to {filename}")
        print(f"   File size: {len(export_data)} characters")
        
        # Import the narrative back
        new_narrative_id = engine.import_narrative(export_data)
        print(f"   ✅ Imported narrative with new ID: {new_narrative_id}")
        
        # Compare summaries
        original_summary = engine.get_narrative_summary(narrative_id)
        imported_summary = engine.get_narrative_summary(new_narrative_id)
        
        print(f"   Original characters: {original_summary['character_count']}")
        print(f"   Imported characters: {imported_summary['character_count']}")
        print(f"   Original plot points: {original_summary['plot_point_count']}")
        print(f"   Imported plot points: {imported_summary['plot_point_count']}")
        
    except Exception as e:
        print(f"   ❌ Export/import failed: {e}")


def main():
    """Main demo function"""
    print("🚀 Narrative Engine Demo - Domain-Agnostic Capabilities")
    print("=" * 60)
    
    # Initialize the Narrative Engine
    engine = NarrativeEngineCore()
    
    # Register basic implementations for all domains
    basic_analyzer = BasicNarrativeAnalyzer()
    basic_generator = BasicNarrativeGenerator()
    basic_adapter = BasicDomainAdapter()
    
    for domain in NarrativeDomain:
        engine.register_analyzer(domain, basic_analyzer)
        engine.register_generator(domain, basic_generator)
        engine.register_adapter(domain, basic_adapter)
    
    print("✅ Registered components for all domains")
    
    # Create narratives for different domains
    narratives = {}
    
    narratives['gaming'] = create_gaming_narrative(engine)
    narratives['therapy'] = create_therapy_narrative(engine)
    narratives['education'] = create_education_narrative(engine)
    narratives['organizational'] = create_organizational_narrative(engine)
    
    # Demonstrate analysis for each domain
    for domain_name, narrative_id in narratives.items():
        domain = NarrativeDomain(domain_name)
        demonstrate_analysis(engine, narrative_id, domain)
    
    # Demonstrate generation for a couple of domains
    demonstrate_generation(engine, narratives['gaming'], NarrativeDomain.GAMING)
    demonstrate_generation(engine, narratives['therapy'], NarrativeDomain.THERAPY)
    
    # Demonstrate adaptation
    demonstrate_adaptation(engine, narratives['gaming'], NarrativeDomain.EDUCATION)
    demonstrate_adaptation(engine, narratives['therapy'], NarrativeDomain.ORGANIZATIONAL)
    
    # Demonstrate export/import
    demonstrate_export_import(engine, narratives['gaming'])
    
    # Show final summary
    print(f"\n📋 Final Summary:")
    print(f"   Total narratives created: {len(narratives)}")
    print(f"   Domains supported: {len(NarrativeDomain)}")
    print(f"   Components registered: {len(engine.analyzers)} analyzers, {len(engine.generators)} generators, {len(engine.adapters)} adapters")
    
    # Show narrative summaries
    print(f"\n📖 Narrative Summaries:")
    for domain_name, narrative_id in narratives.items():
        summary = engine.get_narrative_summary(narrative_id)
        print(f"   {domain_name.title()}: {summary['name']}")
        print(f"     Characters: {summary['character_count']}, Plot Points: {summary['plot_point_count']}")
        print(f"     Coherence: {summary['coherence_score']:.2f}")
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"   The Narrative Engine demonstrates true domain-agnostic capabilities")
    print(f"   across gaming, therapy, education, and organizational contexts.")


if __name__ == "__main__":
    main() 