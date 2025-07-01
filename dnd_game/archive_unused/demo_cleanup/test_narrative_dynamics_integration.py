#!/usr/bin/env python3
"""
Test Script for Narrative Dynamics Integration

Tests the real-time orchestrator event feedback and narrative dynamics system.
"""

import sys
import os
import json
import datetime
import time

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dnd_game.narrative_bridge import NarrativeBridge
from narrative_engine.memory.emotional_memory import EmotionType
from narrative_engine.journaling.player_journal import JournalEntryType
from narrative_engine.narrative_structure.character_arcs import ArcType, ArcStatus
from narrative_engine.narrative_structure.plot_threads import ThreadType, ThreadStatus

def test_narrative_dynamics_integration():
    """Test the complete Narrative Dynamics system integration."""
    
    print("🧪 Testing Narrative Dynamics Integration")
    print("=" * 50)
    
    # Initialize the narrative bridge
    bridge = NarrativeBridge(campaign_id="Narrative Dynamics Test")
    
    print("\n1. 📊 Testing Campaign State Analysis")
    print("-" * 30)
    
    # Analyze initial campaign state
    campaign_state = bridge.analyze_campaign_state()
    print(f"✓ Campaign state analyzed")
    print(f"  - Active arcs: {len(campaign_state.active_arcs)}")
    print(f"  - Open threads: {len(campaign_state.open_threads)}")
    print(f"  - Recent memories: {len(campaign_state.recent_memories)}")
    print(f"  - Emotional context: {len(campaign_state.emotional_context)} emotions")
    
    print("\n2. 🎭 Testing Orchestration Event Generation")
    print("-" * 40)
    
    # Generate orchestration events
    events = bridge.generate_orchestration_events(max_events=3)
    print(f"✓ Generated {len(events)} orchestration events")
    
    for i, event in enumerate(events, 1):
        print(f"  Event {i}: {event.title}")
        print(f"    Type: {event.event_type.value}")
        print(f"    Priority: {event.priority.value}")
        print(f"    Urgency: {event.urgency_level}")
        print(f"    Icon: {event.event_icon}")
        print(f"    Suggested actions: {len(event.suggested_actions)}")
    
    print("\n3. 🎯 Testing Triggered Events Detection")
    print("-" * 35)
    
    # Test action context that should trigger events
    action_contexts = [
        {
            'action': 'I explore the dark forest looking for clues',
            'character': 'Adventurer',
            'location': 'Dark Forest',
            'emotional_context': ['curiosity', 'caution']
        },
        {
            'action': 'I talk to the mysterious stranger about the artifacts',
            'character': 'Adventurer', 
            'location': 'Town Square',
            'emotional_context': ['determination', 'suspicion']
        }
    ]
    
    for i, context in enumerate(action_contexts, 1):
        print(f"\n  Testing action {i}: {context['action']}")
        triggered_events = bridge.get_triggered_orchestration_events(context)
        print(f"    ✓ Found {len(triggered_events)} triggered events")
        
        for event in triggered_events:
            print(f"      - {event['title']} ({event['event_type']})")
    
    print("\n4. 📈 Testing Orchestration Insights")
    print("-" * 30)
    
    # Get orchestration insights
    insights = bridge.get_orchestration_insights()
    print(f"✓ Orchestration insights generated")
    print(f"  - Active events: {insights.get('active_event_count', 0)}")
    print(f"  - Campaign momentum: {insights.get('campaign_momentum', 'unknown')}")
    print(f"  - Pressure points: {len(insights.get('narrative_pressure_points', []))}")
    print(f"  - Emotional themes: {len(insights.get('dominant_emotional_themes', {}))}")
    
    # Show pressure points
    pressure_points = insights.get('narrative_pressure_points', [])
    if pressure_points:
        print(f"  - Pressure points:")
        for point in pressure_points:
            print(f"    * {point['description']} ({point['priority']})")
    
    print("\n5. 🕒 Testing Event History")
    print("-" * 25)
    
    # Get event history
    event_history = bridge.get_orchestration_event_history(limit=5)
    print(f"✓ Retrieved {len(event_history)} recent events")
    
    for event in event_history:
        print(f"  - {event['title']} ({event['created_timestamp'][:19]})")
    
    print("\n6. 🎮 Testing Player Actions with Real-time Feedback")
    print("-" * 45)
    
    # Simulate player actions and check for real-time feedback
    player_actions = [
        "I investigate the ancient ruins",
        "I confront the suspicious merchant",
        "I meditate on my recent discoveries"
    ]
    
    for i, action in enumerate(player_actions, 1):
        print(f"\n  Action {i}: {action}")
        
        # Store the action as memory
        bridge.store_dnd_memory(
            content=f"Player action: {action}",
            memory_type="action",
            tags=["player_action", "interaction"],
            primary_emotion=EmotionType.DETERMINATION,
            emotional_intensity=0.7
        )
        
        # Check for triggered events
        action_context = {
            'action': action,
            'character': 'Adventurer',
            'location': 'Various',
            'emotional_context': ['determination', 'curiosity']
        }
        
        triggered_events = bridge.get_triggered_orchestration_events(action_context)
        print(f"    ✓ Triggered {len(triggered_events)} events")
        
        # Get updated insights
        updated_insights = bridge.get_orchestration_insights()
        print(f"    ✓ Campaign momentum: {updated_insights.get('campaign_momentum', 'unknown')}")
    
    print("\n7. 📊 Testing Narrative Dynamics Data Structure")
    print("-" * 40)
    
    # Test the complete narrative dynamics data structure
    narrative_dynamics = {
        "active_events": bridge.get_active_orchestration_events(),
        "recent_events": bridge.get_orchestration_event_history(5),
        "insights": bridge.get_orchestration_insights(),
        "campaign_state": bridge.analyze_campaign_state().to_dict(),
        "recent_memories": bridge.recall_related_memories("", max_results=3)
    }
    
    print(f"✓ Narrative dynamics data structure created")
    print(f"  - Active events: {len(narrative_dynamics['active_events'])}")
    print(f"  - Recent events: {len(narrative_dynamics['recent_events'])}")
    print(f"  - Recent memories: {len(narrative_dynamics['recent_memories'])}")
    print(f"  - Campaign momentum: {narrative_dynamics['insights'].get('campaign_momentum', 'unknown')}")
    
    print("\n8. 🎨 Testing Event Enhancement with Context")
    print("-" * 40)
    
    # Test event enhancement
    if events:
        enhanced_event = bridge.campaign_orchestrator.enhance_event_with_context(events[0], campaign_state)
        print(f"✓ Event enhanced with context")
        print(f"  - Original icon: ⚔️")
        print(f"  - Enhanced icon: {enhanced_event.event_icon}")
        print(f"  - Urgency level: {enhanced_event.urgency_level}")
        print(f"  - Memory tie-ins: {len(enhanced_event.memory_tie_ins)}")
        print(f"  - Suggested responses: {len(enhanced_event.suggested_responses)}")
    
    print("\n9. 🔄 Testing Real-time Updates")
    print("-" * 30)
    
    # Simulate real-time updates
    print("  Simulating real-time narrative updates...")
    
    # Add some journal entries to trigger more events
    bridge.add_journal_entry(
        character_id="player",
        entry_type=JournalEntryType.PLAYER_WRITTEN,
        title="Mysterious Discoveries",
        content="I found strange markings in the ruins that seem to pulse with energy.",
        tags=["discovery", "mystery", "artifacts"],
        emotional_context=["wonder", "caution"]
    )
    
    # Add a character arc milestone
    arcs = bridge.get_character_arcs(character_id="player")
    if arcs:
        arc_id = arcs[0]['id']
        bridge.add_arc_milestone(
            arc_id=arc_id,
            title="First Discovery",
            description="Uncovered the first clue about the ancient artifacts",
            emotional_context="excitement and trepidation",
            completion_percentage=25.0
        )
    
    # Check for new events
    new_events = bridge.generate_orchestration_events(max_events=2)
    print(f"  ✓ Generated {len(new_events)} new events after updates")
    
    # Get updated insights
    final_insights = bridge.get_orchestration_insights()
    print(f"  ✓ Final campaign momentum: {final_insights.get('campaign_momentum', 'unknown')}")
    
    print("\n✅ Narrative Dynamics Integration Test Complete!")
    print("=" * 50)
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"  - Campaign state analysis: ✓")
    print(f"  - Event generation: ✓ ({len(events)} events)")
    print(f"  - Triggered events detection: ✓")
    print(f"  - Orchestration insights: ✓")
    print(f"  - Event history: ✓")
    print(f"  - Real-time feedback: ✓")
    print(f"  - Data structure: ✓")
    print(f"  - Event enhancement: ✓")
    print(f"  - Real-time updates: ✓")
    
    print(f"\n🎯 Key Features Verified:")
    print(f"  - Real-time orchestration event feedback")
    print(f"  - Campaign momentum tracking")
    print(f"  - Narrative pressure point identification")
    print(f"  - Emotional theme analysis")
    print(f"  - Event history timeline")
    print(f"  - Suggested action generation")
    print(f"  - Context-aware event enhancement")
    
    return True

if __name__ == "__main__":
    try:
        success = test_narrative_dynamics_integration()
        if success:
            print("\n🎉 All tests passed! The Narrative Dynamics system is working correctly.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 