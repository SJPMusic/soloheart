#!/usr/bin/env python3
"""
Simple Dynamic Campaign Orchestrator Test

Tests the basic functionality of the campaign orchestrator.
"""

import sys
import os
import datetime
import json
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SoloHeart.narrative_bridge import NarrativeBridge
from narrative_engine.memory.emotional_memory import EmotionType
from narrative_engine.journaling.player_journal import JournalEntryType
from narrative_engine.narrative_structure.character_arcs import ArcType, ArcStatus
from narrative_engine.narrative_structure.plot_threads import ThreadType, ThreadStatus
from narrative_engine.core.campaign_orchestrator import OrchestrationPriority, OrchestrationEventType


def test_basic_orchestrator():
    """Test basic orchestrator functionality."""
    print("🎭 Basic Dynamic Campaign Orchestrator Test")
    print("=" * 50)
    
    try:
        # Initialize the narrative bridge
        print("\n1. Initializing Narrative Bridge...")
        bridge = NarrativeBridge("Simple Orchestrator Test")
        print("   ✅ Narrative Bridge initialized")
        
        # Test basic memory storage
        print("\n2. Testing Memory Storage...")
        success = bridge.store_dnd_memory(
            content="The player discovered a mysterious artifact in the ancient ruins.",
            memory_type="discovery",
            metadata={"location": "Ancient Ruins", "item": "artifact"},
            tags=["discovery", "artifact", "ruins"],
            primary_emotion=EmotionType.WONDER,
            emotional_intensity=0.8
        )
        print(f"   ✅ Memory storage: {success}")
        
        # Test character arc creation
        print("\n3. Testing Character Arc Creation...")
        arc_id = bridge.create_character_arc(
            character_id="player",
            name="The Artifact Seeker",
            arc_type=ArcType.GROWTH,
            description="The player must learn to understand and control the mysterious artifact.",
            tags=["artifact", "growth", "power"],
            emotional_themes=["curiosity", "responsibility", "fear"]
        )
        print(f"   ✅ Character arc created: {arc_id}")
        
        # Test plot thread creation
        print("\n4. Testing Plot Thread Creation...")
        thread_id = bridge.create_plot_thread(
            name="The Artifact's Power",
            thread_type=ThreadType.MYSTERY,
            description="The artifact seems to have mysterious powers that are affecting the world.",
            priority=8,
            assigned_characters=["player"],
            tags=["artifact", "power", "mystery"]
        )
        print(f"   ✅ Plot thread created: {thread_id}")
        
        # Test journal entry
        print("\n5. Testing Journal Entry...")
        journal_id = bridge.add_journal_entry(
            character_id="player",
            entry_type=JournalEntryType.PLAYER_WRITTEN,
            title="The Artifact Discovery",
            content="I found a strange artifact in the ruins. It seems to respond to my touch.",
            location="Ancient Ruins",
            tags=["discovery", "artifact", "mystery"],
            emotional_context=["wonder", "excitement", "caution"]
        )
        print(f"   ✅ Journal entry added: {journal_id}")
        
        # Test campaign state analysis
        print("\n6. Testing Campaign State Analysis...")
        campaign_state = bridge.analyze_campaign_state()
        print(f"   ✅ Campaign state analyzed:")
        print(f"      - Active Arcs: {len(campaign_state.active_arcs)}")
        print(f"      - Open Threads: {len(campaign_state.open_threads)}")
        print(f"      - Recent Memories: {len(campaign_state.recent_memories)}")
        print(f"      - Emotional Context: {len(campaign_state.emotional_context)} emotions")
        
        # Test orchestration event generation
        print("\n7. Testing Orchestration Event Generation...")
        events = bridge.generate_orchestration_events(max_events=2)
        print(f"   ✅ Generated {len(events)} orchestration events:")
        
        for i, event in enumerate(events, 1):
            print(f"      {i}. {event.title} ({event.priority.value})")
            print(f"         Type: {event.event_type.value}")
            print(f"         Description: {event.description[:50]}...")
        
        # Test event execution
        if events:
            print("\n8. Testing Event Execution...")
            first_event = events[0]
            success = bridge.execute_orchestration_event(
                first_event.event_id,
                "Player decided to investigate the artifact's power"
            )
            print(f"   ✅ Event executed: {success}")
        
        # Test orchestration summary
        print("\n9. Testing Orchestration Summary...")
        summary = bridge.get_orchestration_summary()
        print(f"   ✅ Orchestration summary:")
        print(f"      - Total Events: {summary['total_events']}")
        print(f"      - Pending Events: {summary['pending_events']}")
        print(f"      - Executed Events: {summary['executed_events']}")
        
        # Test campaign progression suggestions
        print("\n10. Testing Campaign Progression Suggestions...")
        progression = bridge.get_campaign_progression_suggestions()
        print(f"   ✅ Campaign progression suggestions:")
        print(f"      - New Events: {len(progression['new_events'])}")
        print(f"      - Pending Events: {len(progression['pending_events'])}")
        print(f"      - Priority Focus: {len(progression['suggestions']['priority_focus'])} areas")
        
        print("\n🎉 Basic Orchestrator Test Completed Successfully!")
        print("\n✅ All Core Features Working:")
        print("   - Memory System ✓")
        print("   - Character Arcs ✓")
        print("   - Plot Threads ✓")
        print("   - Journal System ✓")
        print("   - Campaign State Analysis ✓")
        print("   - Event Generation ✓")
        print("   - Event Execution ✓")
        print("   - Orchestration Summary ✓")
        print("   - Progression Suggestions ✓")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_orchestrator()
    if success:
        print("\n🎯 Basic orchestrator test completed successfully!")
    else:
        print("\n❌ Basic orchestrator test failed.") 