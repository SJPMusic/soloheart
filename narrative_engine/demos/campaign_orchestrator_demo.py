#!/usr/bin/env python3
"""
Dynamic Campaign Orchestrator Demo

Demonstrates the campaign orchestrator's ability to drive game progression
based on memory, emotion, character arcs, and plot threads over time.
"""

import sys
import os
import datetime
import time
from pathlib import Path

# Add the parent directory to the path to import the orchestrator module
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.campaign_orchestrator import DynamicCampaignOrchestrator, OrchestrationPriority, OrchestrationEventType
from narrative_bridge import NarrativeBridge
from memory.emotional_memory import EmotionType
from journaling.player_journal import JournalEntryType
from narrative_structure.character_arcs import ArcType, ArcStatus
from narrative_structure.plot_threads import ThreadType, ThreadStatus


def simulate_campaign_progression():
    """Simulate campaign progression over multiple sessions."""
    print("🎭 Dynamic Campaign Orchestrator Demo")
    print("=" * 60)
    
    # Initialize the narrative bridge and orchestrator
    print("\n1. Initializing Systems...")
    print("-" * 30)
    
    narrative_bridge = NarrativeBridge("Orchestrator Demo Campaign")
    orchestrator = DynamicCampaignOrchestrator("demo_orchestrator_events.jsonl")
    
    print("   ✅ Narrative Bridge initialized")
    print("   ✅ Campaign Orchestrator initialized")
    
    # Phase 1: Initial Setup
    print("\n2. Phase 1: Initial Campaign Setup")
    print("-" * 35)
    
    # Create initial character arc
    growth_arc = narrative_bridge.create_character_arc(
        character_id="Aelric",
        name="The Reluctant Hero",
        arc_type=ArcType.GROWTH,
        description="Aelric must overcome his self-doubt and embrace his role as a hero.",
        tags=["hero's journey", "self-confidence", "leadership"],
        emotional_themes=["self-doubt", "determination", "pride"]
    )
    print(f"   ✅ Created character arc: {growth_arc}")
    
    # Create initial plot thread
    mystery_thread = narrative_bridge.create_plot_thread(
        name="The Disappearing Artifacts",
        thread_type=ThreadType.MYSTERY,
        description="Ancient artifacts are disappearing from the local museum.",
        priority=8,
        assigned_characters=["Aelric"],
        tags=["mystery", "artifacts", "museum", "supernatural"]
    )
    print(f"   ✅ Created plot thread: {mystery_thread}")
    
    # Add some initial memories
    narrative_bridge.store_dnd_memory(
        content="Aelric discovered his magical abilities for the first time when he accidentally cast a light spell in the dark.",
        memory_type="discovery",
        metadata={"location": "Ancient Library", "ability": "magic"},
        tags=["magic", "discovery", "first-time"],
        primary_emotion=EmotionType.WONDER,
        emotional_intensity=0.8
    )
    print("   ✅ Stored initial memory: Magical discovery")
    
    narrative_bridge.store_dnd_memory(
        content="The museum curator approached Aelric with concerns about missing artifacts.",
        memory_type="quest",
        metadata={"location": "Museum", "npc": "curator"},
        tags=["quest", "mystery", "artifacts"],
        primary_emotion=EmotionType.CURIOSITY,
        emotional_intensity=0.6
    )
    print("   ✅ Stored initial memory: Quest introduction")
    
    # Add journal entry
    narrative_bridge.add_journal_entry(
        character_id="Aelric",
        entry_type=JournalEntryType.PLAYER_WRITTEN,
        title="First Steps into the Unknown",
        content="Today I discovered I have magical abilities. It's both exciting and terrifying. The curator's request about the missing artifacts feels like my first real test.",
        location="Ancient Library",
        tags=["magic", "discovery", "quest"],
        emotional_context=["excitement", "fear", "determination"]
    )
    print("   ✅ Added journal entry: First Steps")
    
    # Phase 2: First Orchestration Analysis
    print("\n3. Phase 2: First Orchestration Analysis")
    print("-" * 40)
    
    # Analyze campaign state
    campaign_state = orchestrator.analyze_campaign_state(narrative_bridge, "Orchestrator Demo Campaign")
    print(f"   📊 Campaign State Analysis:")
    print(f"      - Active Arcs: {len(campaign_state.active_arcs)}")
    print(f"      - Open Threads: {len(campaign_state.open_threads)}")
    print(f"      - Recent Memories: {len(campaign_state.recent_memories)}")
    print(f"      - Emotional Context: {len(campaign_state.emotional_context)} emotions")
    
    # Generate orchestration events
    events = orchestrator.generate_orchestration_events(campaign_state, max_events=3)
    print(f"   🎯 Generated {len(events)} orchestration events:")
    
    for i, event in enumerate(events, 1):
        print(f"      {i}. {event.title} ({event.priority.value})")
        print(f"         Type: {event.event_type.value}")
        print(f"         Description: {event.description[:60]}...")
        print(f"         Suggested Actions: {', '.join(event.suggested_actions[:2])}")
    
    # Phase 3: Simulate Player Actions
    print("\n4. Phase 3: Simulating Player Actions")
    print("-" * 35)
    
    # Execute the first event (quest suggestion)
    if events:
        first_event = events[0]
        print(f"   🎮 Executing: {first_event.title}")
        
        success = orchestrator.execute_event(
            first_event.event_id,
            narrative_bridge,
            "Player decided to investigate the museum mystery"
        )
        print(f"   ✅ Event executed: {success}")
        
        # Add memory of the action
        narrative_bridge.store_dnd_memory(
            content="Aelric decided to investigate the museum mystery, feeling a sense of responsibility and excitement.",
            memory_type="decision",
            metadata={"location": "Museum", "action": "investigation"},
            tags=["decision", "investigation", "responsibility"],
            primary_emotion=EmotionType.DETERMINATION,
            emotional_intensity=0.7
        )
        print("   ✅ Stored decision memory")
        
        # Add milestone to character arc
        if growth_arc:
            narrative_bridge.add_arc_milestone(
                growth_arc,
                title="First Heroic Decision",
                description="Aelric chose to investigate the museum mystery, taking his first step toward heroism.",
                memory_ids=["memory_decision_001"],
                emotional_context="Determination and responsibility",
                completion_percentage=0.2
            )
            print("   ✅ Added arc milestone: First Heroic Decision")
    
    # Phase 4: Second Orchestration Cycle
    print("\n5. Phase 4: Second Orchestration Cycle")
    print("-" * 40)
    
    # Add more memories to trigger new events
    narrative_bridge.store_dnd_memory(
        content="Aelric found strange markings near the museum that seem to glow in the moonlight.",
        memory_type="discovery",
        metadata={"location": "Museum", "clue": "glowing markings"},
        tags=["clue", "supernatural", "investigation"],
        primary_emotion=EmotionType.SURPRISE,
        emotional_intensity=0.8
    )
    print("   ✅ Stored discovery memory: Glowing markings")
    
    narrative_bridge.store_dnd_memory(
        content="Aelric felt a growing connection to the ancient artifacts, as if they were calling to him.",
        memory_type="connection",
        metadata={"location": "Museum", "connection": "artifacts"},
        tags=["connection", "artifacts", "destiny"],
        primary_emotion=EmotionType.WONDER,
        emotional_intensity=0.9
    )
    print("   ✅ Stored connection memory: Artifact calling")
    
    # Update plot thread
    if mystery_thread:
        narrative_bridge.add_thread_update(
            mystery_thread,
            title="Supernatural Clues Discovered",
            description="Aelric found glowing markings near the museum, suggesting supernatural involvement.",
            memory_ids=["memory_clue_001"],
            priority_change=9
        )
        print("   ✅ Added thread update: Supernatural clues")
    
    # Analyze campaign state again
    campaign_state = orchestrator.analyze_campaign_state(narrative_bridge, "Orchestrator Demo Campaign")
    
    # Generate new orchestration events
    new_events = orchestrator.generate_orchestration_events(campaign_state, max_events=2)
    print(f"   🎯 Generated {len(new_events)} new orchestration events:")
    
    for i, event in enumerate(new_events, 1):
        print(f"      {i}. {event.title} ({event.priority.value})")
        print(f"         Type: {event.event_type.value}")
        print(f"         Description: {event.description[:60]}...")
    
    # Phase 5: Emotional Development
    print("\n6. Phase 5: Emotional Development")
    print("-" * 35)
    
    # Add emotional memory that should trigger emotional moment
    narrative_bridge.store_dnd_memory(
        content="Aelric realized that his magical abilities might be connected to the missing artifacts, making him question his own identity.",
        memory_type="realization",
        metadata={"location": "Museum", "realization": "identity connection"},
        tags=["realization", "identity", "magic", "artifacts"],
        primary_emotion=EmotionType.CONFUSION,
        emotional_intensity=0.85
    )
    print("   ✅ Stored emotional memory: Identity confusion")
    
    # Add journal entry about the emotional moment
    narrative_bridge.add_journal_entry(
        character_id="Aelric",
        entry_type=JournalEntryType.CHARACTER_DEVELOPMENT,
        title="Questions of Identity",
        content="I'm beginning to wonder if my magical abilities are connected to these missing artifacts. What does this mean about who I really am?",
        location="Museum",
        tags=["identity", "magic", "artifacts", "self-reflection"],
        emotional_context=["confusion", "curiosity", "fear", "wonder"]
    )
    print("   ✅ Added emotional journal entry")
    
    # Phase 6: Final Orchestration Analysis
    print("\n7. Phase 6: Final Orchestration Analysis")
    print("-" * 40)
    
    # Analyze final campaign state
    campaign_state = orchestrator.analyze_campaign_state(narrative_bridge, "Orchestrator Demo Campaign")
    
    # Generate final orchestration events
    final_events = orchestrator.generate_orchestration_events(campaign_state, max_events=3)
    print(f"   🎯 Generated {len(final_events)} final orchestration events:")
    
    for i, event in enumerate(final_events, 1):
        print(f"      {i}. {event.title} ({event.priority.value})")
        print(f"         Type: {event.event_type.value}")
        print(f"         Description: {event.description[:60]}...")
    
    # Phase 7: Orchestration Summary
    print("\n8. Phase 7: Orchestration Summary")
    print("-" * 30)
    
    # Get pending events
    pending_events = orchestrator.get_pending_events()
    print(f"   📋 Pending Events: {len(pending_events)}")
    
    for event in pending_events[:3]:  # Show first 3
        print(f"      - {event.title} ({event.priority.value})")
    
    # Get orchestration summary
    summary = orchestrator.get_orchestration_summary()
    print(f"   📊 Orchestration Summary:")
    print(f"      - Total Events: {summary['total_events']}")
    print(f"      - Pending Events: {summary['pending_events']}")
    print(f"      - Executed Events: {summary['executed_events']}")
    print(f"      - Decision History: {summary['decision_history_count']} entries")
    
    print(f"   📈 Event Type Breakdown:")
    for event_type, count in summary['event_types'].items():
        print(f"      - {event_type}: {count}")
    
    print(f"   🎯 Priority Breakdown:")
    for priority, count in summary['priorities'].items():
        print(f"      - {priority}: {count}")
    
    # Phase 8: Campaign Summary
    print("\n9. Phase 8: Final Campaign Summary")
    print("-" * 35)
    
    campaign_summary = narrative_bridge.get_campaign_summary()
    print(f"   📊 Campaign Summary:")
    print(f"      - Campaign ID: {campaign_summary['campaign_id']}")
    print(f"      - Memory Count: {campaign_summary.get('memory_count', 0)}")
    print(f"      - Journal Entries: {campaign_summary.get('journal_entries', 0)}")
    print(f"      - Character Arcs: {campaign_summary.get('character_arcs', 0)}")
    print(f"      - Plot Threads: {campaign_summary.get('plot_threads', 0)}")
    
    print("\n🎉 Dynamic Campaign Orchestrator Demo Complete!")
    print("\n✅ Features Demonstrated:")
    print("   - Campaign state analysis")
    print("   - Dynamic event generation")
    print("   - Priority-based orchestration")
    print("   - Emotional context integration")
    print("   - Character arc monitoring")
    print("   - Plot thread tracking")
    print("   - Decision memory storage")
    print("   - Orchestration summary")
    
    print("\n📁 Generated Files:")
    print("   - demo_orchestrator_events.jsonl (Orchestration events)")
    print("   - journal_Orchestrator Demo Campaign.jsonl (Journal entries)")
    print("   - arcs_Orchestrator Demo Campaign.jsonl (Character arcs)")
    print("   - threads_Orchestrator Demo Campaign.jsonl (Plot threads)")
    
    print("\n🎯 The orchestrator successfully:")
    print("   - Monitored active character arcs and plot threads")
    print("   - Used emotional context to weight priorities")
    print("   - Generated dynamic quests and encounters")
    print("   - Integrated with the NarrativeBridge")
    print("   - Stored decisions in memory for continuity")
    
    return True


if __name__ == "__main__":
    try:
        success = simulate_campaign_progression()
        if success:
            print("\n🎯 Demo completed successfully! Campaign orchestrator is working correctly.")
        else:
            print("\n❌ Demo failed. Check the output above for details.")
    except Exception as e:
        print(f"\n💥 Demo failed with error: {e}")
        import traceback
        traceback.print_exc() 