#!/usr/bin/env python3
"""
Test script for the Emergent Conflict System.

This script demonstrates:
1. Internal conflicts (character struggles)
2. Interpersonal conflicts (party disagreements)
3. External conflicts (threats and challenges)
4. Conflict resolution and impact tracking
"""

import sys
import os
import datetime
import json
from pathlib import Path

# Add the parent directory to the path to import narrative_engine
sys.path.insert(0, str(Path(__file__).parent.parent))

from narrative_engine.core.campaign_orchestrator import (
    DynamicCampaignOrchestrator, 
    ConflictType, 
    ConflictUrgency,
    CampaignState
)
from narrative_engine.memory.emotional_memory import EmotionType
from narrative_engine.narrative_structure.character_arcs import ArcType, ArcStatus
from narrative_engine.narrative_structure.plot_threads import ThreadType, ThreadStatus
from dnd_game.narrative_bridge import NarrativeBridge


def create_test_campaign_state():
    """Create a test campaign state with multiple characters and arcs."""
    return CampaignState(
        campaign_id="conflict-test-campaign",
        active_arcs=[
            {
                'id': 'arc_1',
                'character_id': 'player',
                'title': 'The Hero\'s Journey',
                'description': 'Seeking to become a legendary hero and gain power',
                'status': 'active',
                'created_at': (datetime.datetime.now() - datetime.timedelta(days=5)).isoformat(),
                'arc_type': ArcType.HERO_JOURNEY.value,
                'completion_percentage': 0.3
            },
            {
                'id': 'arc_2',
                'character_id': 'companion',
                'title': 'The Path of Peace',
                'description': 'Seeking harmony and avoiding conflict',
                'status': 'active',
                'created_at': (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
                'arc_type': ArcType.REDEMPTION.value,
                'completion_percentage': 0.1
            }
        ],
        open_threads=[
            {
                'id': 'thread_1',
                'title': 'The Dark Threat',
                'description': 'A powerful evil force approaches',
                'status': ThreadStatus.ACTIVE.value,
                'priority': 8,
                'thread_type': ThreadType.MAIN_QUEST.value
            },
            {
                'id': 'thread_2',
                'title': 'The Ancient Artifacts',
                'description': 'Mysterious artifacts with unknown power',
                'status': ThreadStatus.ACTIVE.value,
                'priority': 6,
                'thread_type': ThreadType.SIDE_QUEST.value
            }
        ],
        recent_memories=[
            {
                'content': 'Fought a difficult battle and felt fear',
                'metadata': {
                    'emotional_context': ['fear', 'determination'],
                    'emotional_intensity': 0.8
                }
            },
            {
                'content': 'Betrayed by a trusted ally',
                'metadata': {
                    'emotional_context': ['loyalty', 'suspicion'],
                    'emotional_intensity': 0.9
                }
            }
        ],
        emotional_context={
            'fear': 0.7,
            'determination': 0.8,
            'loyalty': 0.6,
            'suspicion': 0.7,
            'anger': 0.4,
            'hope': 0.3
        },
        character_locations={
            'player': 'Town Square',
            'companion': 'Town Square'
        },
        world_events=[
            {
                'title': 'Dark Clouds Gather',
                'description': 'Storm clouds approach from the north',
                'urgency': 'high',
                'impact': 'environmental'
            }
        ],
        session_count=5
    )


def test_conflict_detection():
    """Test conflict detection in the orchestrator."""
    print("🔍 Testing Conflict Detection...")
    
    # Initialize orchestrator
    orchestrator = DynamicCampaignOrchestrator("test_conflicts.jsonl")
    
    # Create test campaign state
    campaign_state = create_test_campaign_state()
    
    # Detect conflicts
    conflicts = orchestrator.detect_conflicts(campaign_state)
    
    print(f"📊 Detected {len(conflicts)} conflicts:")
    
    for i, conflict in enumerate(conflicts, 1):
        print(f"\n{i}. {conflict.title}")
        print(f"   Type: {conflict.conflict_type.value}")
        print(f"   Urgency: {conflict.urgency.value}")
        print(f"   Description: {conflict.description}")
        print(f"   Characters: {', '.join(conflict.characters_involved)}")
        print(f"   Resolutions: {len(conflict.suggested_resolutions)} options")
        
        if conflict.value_contradictions:
            print(f"   Value Contradictions: {', '.join(conflict.value_contradictions)}")
    
    return conflicts


def test_conflict_resolution():
    """Test conflict resolution with the narrative bridge."""
    print("\n🎯 Testing Conflict Resolution...")
    
    # Initialize narrative bridge
    bridge = NarrativeBridge("conflict-test-campaign")
    
    # Create test campaign state
    campaign_state = create_test_campaign_state()
    
    # Detect conflicts
    conflicts = bridge.campaign_orchestrator.detect_conflicts(campaign_state)
    
    if not conflicts:
        print("No conflicts detected for resolution testing")
        return
    
    # Test resolving the first conflict
    conflict = conflicts[0]
    resolution = conflict.suggested_resolutions[0] if conflict.suggested_resolutions else None
    
    if resolution:
        print(f"Resolving conflict: {conflict.title}")
        print(f"Resolution: {resolution['text']}")
        
        success = bridge.campaign_orchestrator.resolve_conflict(
            conflict.conflict_id, 
            resolution['id'], 
            bridge
        )
        
        if success:
            print("✅ Conflict resolved successfully!")
            
            # Check if conflict is marked as resolved
            resolved_conflict = bridge.campaign_orchestrator.conflicts.get(conflict.conflict_id)
            if resolved_conflict and resolved_conflict.resolved_timestamp:
                print(f"Resolution timestamp: {resolved_conflict.resolved_timestamp}")
                print(f"Chosen resolution: {resolved_conflict.resolution_chosen}")
        else:
            print("❌ Failed to resolve conflict")
    else:
        print("No resolutions available for testing")


def test_conflict_api():
    """Test the conflict API endpoints."""
    print("\n🌐 Testing Conflict API...")
    
    # Initialize narrative bridge
    bridge = NarrativeBridge("conflict-api-test")
    
    # Test getting conflict nodes
    conflicts = bridge.get_conflict_nodes("conflict-api-test")
    print(f"API returned {len(conflicts)} conflicts")
    
    # Test getting conflict summary
    summary = bridge.get_conflict_summary("conflict-api-test")
    print(f"Conflict summary: {summary}")
    
    # Test resolving a conflict via API
    if conflicts:
        conflict = conflicts[0]
        resolution = conflict['suggested_resolutions'][0] if conflict['suggested_resolutions'] else None
        
        if resolution:
            print(f"Testing API resolution for: {conflict['title']}")
            success = bridge.resolve_conflict(
                conflict['id'], 
                resolution['id'], 
                "conflict-api-test"
            )
            print(f"API resolution result: {success}")


def test_emotional_conflicts():
    """Test emotional contradiction detection."""
    print("\n💭 Testing Emotional Conflicts...")
    
    # Initialize orchestrator
    orchestrator = DynamicCampaignOrchestrator("emotional_conflicts.jsonl")
    
    # Create campaign state with emotional contradictions
    emotional_state = CampaignState(
        campaign_id="emotional-test",
        active_arcs=[],
        open_threads=[],
        recent_memories=[],
        emotional_context={
            'fear': 0.8,      # High fear
            'determination': 0.9,  # High determination (contradiction)
            'loyalty': 0.7,   # High loyalty
            'suspicion': 0.8,  # High suspicion (contradiction)
            'hope': 0.2,      # Low hope
            'despair': 0.6    # High despair (contradiction)
        },
        character_locations={},
        world_events=[],
        session_count=1
    )
    
    # Detect emotional conflicts
    conflicts = orchestrator.detect_conflicts(emotional_state)
    
    print(f"Detected {len(conflicts)} emotional conflicts:")
    for conflict in conflicts:
        if conflict.conflict_type == ConflictType.INTERNAL:
            print(f"  - {conflict.title}: {conflict.description}")
            print(f"    Value contradictions: {conflict.value_contradictions}")


def test_conflict_persistence():
    """Test that conflicts are properly saved and loaded."""
    print("\n💾 Testing Conflict Persistence...")
    
    # Initialize orchestrator with specific storage
    storage_path = "test_conflict_persistence.jsonl"
    orchestrator = DynamicCampaignOrchestrator(storage_path)
    
    # Create test campaign state
    campaign_state = create_test_campaign_state()
    
    # Detect and save conflicts
    conflicts = orchestrator.detect_conflicts(campaign_state)
    print(f"Created {len(conflicts)} conflicts")
    
    # Create new orchestrator instance to test loading
    new_orchestrator = DynamicCampaignOrchestrator(storage_path)
    
    # Check if conflicts were loaded
    loaded_conflicts = list(new_orchestrator.conflicts.values())
    print(f"Loaded {len(loaded_conflicts)} conflicts from storage")
    
    # Verify conflict data integrity
    for conflict in loaded_conflicts:
        print(f"  - {conflict.title} ({conflict.conflict_type.value})")
        print(f"    Urgency: {conflict.urgency.value}")
        print(f"    Resolutions: {len(conflict.suggested_resolutions)}")
    
    # Clean up test file
    try:
        os.remove(storage_path)
        os.remove(storage_path.replace('.jsonl', '_conflicts.jsonl'))
    except FileNotFoundError:
        pass


def test_conflict_integration():
    """Test full integration with narrative bridge."""
    print("\n🔗 Testing Full Conflict Integration...")
    
    # Initialize narrative bridge
    bridge = NarrativeBridge("integration-test")
    
    # Store some memories to create context
    bridge.store_dnd_memory(
        content="Faced a moral dilemma between saving a friend or completing the mission",
        memory_type="episodic",
        tags=["moral_choice", "loyalty", "duty"],
        primary_emotion=EmotionType.CONFUSION,
        emotional_intensity=0.8
    )
    
    bridge.store_dnd_memory(
        content="Discovered that a trusted ally has been keeping secrets",
        memory_type="episodic",
        tags=["betrayal", "trust", "suspicion"],
        primary_emotion=EmotionType.SUSPICION,
        emotional_intensity=0.9
    )
    
    # Create character arcs
    bridge.create_character_arc(
        character_id="player",
        name="The Hero's Dilemma",
        arc_type=ArcType.HERO_JOURNEY,
        description="Struggling between personal desires and heroic duty",
        emotional_themes=["duty", "desire", "sacrifice"]
    )
    
    bridge.create_character_arc(
        character_id="companion",
        name="The Path of Peace",
        arc_type=ArcType.REDEMPTION,
        description="Seeking to avoid violence and find peaceful solutions",
        emotional_themes=["peace", "violence", "redemption"]
    )
    
    # Create plot threads
    bridge.create_plot_thread(
        name="The Dark Threat",
        thread_type=ThreadType.MAIN_QUEST,
        description="A powerful evil force threatens the realm",
        priority=9,
        assigned_characters=["player", "companion"]
    )
    
    # Get narrative dynamics (should include conflicts)
    dynamics = bridge.get_narrative_dynamics("integration-test")
    
    print("Narrative Dynamics Results:")
    print(f"  Campaign Momentum: {dynamics.get('momentum', 'unknown')}")
    print(f"  Active Events: {len(dynamics.get('active_events', []))}")
    print(f"  Active Conflicts: {len(dynamics.get('active_conflicts', []))}")
    print(f"  Emotional Themes: {dynamics.get('emotional_themes', [])}")
    
    # Display conflicts
    conflicts = dynamics.get('active_conflicts', [])
    if conflicts:
        print(f"\nDetected Conflicts:")
        for conflict in conflicts:
            print(f"  - {conflict['title']} ({conflict['type']})")
            print(f"    Urgency: {conflict['urgency']}")
            print(f"    Description: {conflict['description']}")
            print(f"    Resolutions: {len(conflict['suggested_resolutions'])}")


def main():
    """Run all conflict system tests."""
    print("🎭 EMERGENT CONFLICT SYSTEM TEST SUITE")
    print("=" * 50)
    
    try:
        # Test basic conflict detection
        test_conflict_detection()
        
        # Test conflict resolution
        test_conflict_resolution()
        
        # Test API endpoints
        test_conflict_api()
        
        # Test emotional conflicts
        test_emotional_conflicts()
        
        # Test persistence
        test_conflict_persistence()
        
        # Test full integration
        test_conflict_integration()
        
        print("\n✅ All conflict system tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 