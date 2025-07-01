#!/usr/bin/env python3
"""
Character Arcs Demo

Demonstrates the character arc tracking system for managing long-term
character development and narrative progression.
"""

import sys
import os
import datetime
from pathlib import Path

# Add the parent directory to the path to import the narrative structure module
sys.path.insert(0, str(Path(__file__).parent.parent))

from narrative_structure.character_arcs import (
    CharacterArcManager,
    CharacterArc,
    ArcType,
    ArcStatus,
    ArcMilestone
)


def demo_character_arcs_system():
    """Demonstrate the character arcs system functionality."""
    print("🎭 Character Arcs System Demo")
    print("=" * 50)
    
    # Initialize the character arc manager
    arc_manager = CharacterArcManager("demo_character_arcs.jsonl")
    
    # Demo 1: Create character arcs
    print("\n1. Creating Character Arcs")
    print("-" * 25)
    
    # Arc 1: Personal growth arc
    growth_arc = arc_manager.create_arc(
        character_id="Aelric",
        campaign_id="Test Campaign",
        name="From Novice to Hero",
        arc_type=ArcType.GROWTH,
        description="Aelric's journey from an inexperienced adventurer to a confident hero, learning to trust his abilities and make difficult decisions.",
        target_completion=datetime.datetime.now() + datetime.timedelta(days=30),
        tags=["hero's journey", "self-confidence", "leadership"],
        emotional_themes=["self-doubt", "determination", "pride"]
    )
    print(f"✅ Created growth arc: {growth_arc.name}")
    
    # Arc 2: Redemption arc
    redemption_arc = arc_manager.create_arc(
        character_id="Aelric",
        campaign_id="Test Campaign",
        name="Seeking Redemption",
        arc_type=ArcType.REDEMPTION,
        description="Aelric must confront his past mistakes and seek redemption for actions that led to innocent lives being lost.",
        target_completion=datetime.datetime.now() + datetime.timedelta(days=45),
        tags=["redemption", "guilt", "forgiveness"],
        emotional_themes=["guilt", "shame", "hope", "forgiveness"]
    )
    print(f"✅ Created redemption arc: {redemption_arc.name}")
    
    # Arc 3: Quest arc
    quest_arc = arc_manager.create_arc(
        character_id="Aelric",
        campaign_id="Test Campaign",
        name="The Lost Artifact Quest",
        arc_type=ArcType.QUEST,
        description="Aelric's quest to find the ancient artifact that could save his homeland from destruction.",
        target_completion=datetime.datetime.now() + datetime.timedelta(days=60),
        tags=["quest", "artifact", "save homeland"],
        emotional_themes=["duty", "responsibility", "urgency"]
    )
    print(f"✅ Created quest arc: {quest_arc.name}")
    
    # Demo 2: Add milestones to arcs
    print("\n2. Adding Milestones to Arcs")
    print("-" * 30)
    
    # Growth arc milestones
    arc_manager.add_milestone_to_arc(
        growth_arc.arc_id,
        title="First Successful Battle",
        description="Aelric successfully led his first battle against bandits, gaining confidence in his combat abilities.",
        memory_ids=["memory_battle_001", "memory_confidence_001"],
        emotional_context="Pride and growing self-confidence",
        completion_percentage=0.2
    )
    print("✅ Added milestone: First Successful Battle")
    
    arc_manager.add_milestone_to_arc(
        growth_arc.arc_id,
        title="Saving the Village",
        description="Aelric made a difficult decision to sacrifice personal gain to save a village from destruction.",
        memory_ids=["memory_village_001", "memory_sacrifice_001"],
        emotional_context="Moral growth and selflessness",
        completion_percentage=0.5
    )
    print("✅ Added milestone: Saving the Village")
    
    arc_manager.add_milestone_to_arc(
        growth_arc.arc_id,
        title="Becoming a Leader",
        description="Aelric was chosen to lead a group of adventurers, showing his growth into a leadership role.",
        memory_ids=["memory_leadership_001", "memory_trust_001"],
        emotional_context="Pride and responsibility",
        completion_percentage=0.8
    )
    print("✅ Added milestone: Becoming a Leader")
    
    # Redemption arc milestones
    arc_manager.add_milestone_to_arc(
        redemption_arc.arc_id,
        title="Confronting the Past",
        description="Aelric finally confronted the consequences of his past actions and accepted responsibility.",
        memory_ids=["memory_confrontation_001", "memory_guilt_001"],
        emotional_context="Painful acceptance and guilt",
        completion_percentage=0.3
    )
    print("✅ Added milestone: Confronting the Past")
    
    arc_manager.add_milestone_to_arc(
        redemption_arc.arc_id,
        title="First Act of Redemption",
        description="Aelric saved a child from danger, beginning his path toward redemption.",
        memory_ids=["memory_save_child_001", "memory_hope_001"],
        emotional_context="Hope and determination",
        completion_percentage=0.6
    )
    print("✅ Added milestone: First Act of Redemption")
    
    # Quest arc milestones
    arc_manager.add_milestone_to_arc(
        quest_arc.arc_id,
        title="Discovering the Artifact's Location",
        description="Aelric found ancient texts revealing the location of the lost artifact.",
        memory_ids=["memory_discovery_001", "memory_urgency_001"],
        emotional_context="Excitement and urgency",
        completion_percentage=0.25
    )
    print("✅ Added milestone: Discovering the Artifact's Location")
    
    arc_manager.add_milestone_to_arc(
        quest_arc.arc_id,
        title="Overcoming the Guardian",
        description="Aelric defeated the ancient guardian protecting the artifact.",
        memory_ids=["memory_guardian_001", "memory_victory_001"],
        emotional_context="Triumph and determination",
        completion_percentage=0.7
    )
    print("✅ Added milestone: Overcoming the Guardian")
    
    # Demo 3: Query and display arcs
    print("\n3. Querying Character Arcs")
    print("-" * 25)
    
    # Get all arcs for Aelric
    aelric_arcs = arc_manager.get_arcs_by_character("Aelric", "Test Campaign")
    print(f"📚 Found {len(aelric_arcs)} arcs for Aelric:")
    
    for arc in aelric_arcs:
        print(f"\n🎭 {arc.name} ({arc.arc_type.value})")
        print(f"   Status: {arc.status.value}")
        print(f"   Completion: {arc.get_completion_percentage():.1%}")
        print(f"   Milestones: {len(arc.milestones)}")
        print(f"   Description: {arc.description[:80]}...")
        
        # Show recent milestones
        if arc.milestones:
            print("   Recent milestones:")
            for milestone in arc.milestones[-2:]:  # Show last 2 milestones
                print(f"     - {milestone.title} ({milestone.completion_percentage:.1%})")
    
    # Demo 4: Filter arcs by type
    print("\n4. Filtering Arcs by Type")
    print("-" * 25)
    
    growth_arcs = arc_manager.get_arcs_by_type(ArcType.GROWTH, "Test Campaign")
    print(f"🌱 Growth arcs: {len(growth_arcs)}")
    for arc in growth_arcs:
        print(f"  - {arc.name} ({arc.get_completion_percentage():.1%} complete)")
    
    quest_arcs = arc_manager.get_arcs_by_type(ArcType.QUEST, "Test Campaign")
    print(f"⚔️ Quest arcs: {len(quest_arcs)}")
    for arc in quest_arcs:
        print(f"  - {arc.name} ({arc.get_completion_percentage():.1%} complete)")
    
    # Demo 5: Update arc status
    print("\n5. Updating Arc Status")
    print("-" * 25)
    
    # Complete the growth arc
    arc_manager.update_arc_status(growth_arc.arc_id, ArcStatus.COMPLETED)
    print(f"✅ Updated '{growth_arc.name}' status to COMPLETED")
    
    # Pause the redemption arc
    arc_manager.update_arc_status(redemption_arc.arc_id, ArcStatus.PAUSED)
    print(f"✅ Updated '{redemption_arc.name}' status to PAUSED")
    
    # Demo 6: Search functionality
    print("\n6. Search Functionality")
    print("-" * 25)
    
    # Search for arcs containing "hero"
    hero_arcs = arc_manager.search_arcs("hero", character_id="Aelric")
    print(f"🔍 Found {len(hero_arcs)} arcs containing 'hero':")
    for arc in hero_arcs:
        print(f"  - {arc.name}")
    
    # Search for arcs containing "redemption"
    redemption_arcs = arc_manager.search_arcs("redemption", character_id="Aelric")
    print(f"🔍 Found {len(redemption_arcs)} arcs containing 'redemption':")
    for arc in redemption_arcs:
        print(f"  - {arc.name}")
    
    # Demo 7: Arc summary statistics
    print("\n7. Arc Summary Statistics")
    print("-" * 30)
    
    stats = arc_manager.get_arc_summary(character_id="Aelric", campaign_id="Test Campaign")
    print(f"📊 Arc Statistics for Aelric:")
    print(f"  Total arcs: {stats['total_arcs']}")
    print(f"  Average completion: {stats['average_completion']:.1%}")
    
    print("\n  Arc types:")
    for arc_type, count in stats['arc_types'].items():
        print(f"    {arc_type}: {count}")
    
    print("\n  Status breakdown:")
    for status, count in stats['status_counts'].items():
        print(f"    {status}: {count}")
    
    print("\n🎉 Character Arcs System Demo Complete!")
    print("\nKey features demonstrated:")
    print("  ✅ Arc creation and management")
    print("  ✅ Milestone tracking")
    print("  ✅ Status updates")
    print("  ✅ Type-based filtering")
    print("  ✅ Search functionality")
    print("  ✅ Completion tracking")
    print("  ✅ Statistical analysis")


if __name__ == "__main__":
    demo_character_arcs_system() 