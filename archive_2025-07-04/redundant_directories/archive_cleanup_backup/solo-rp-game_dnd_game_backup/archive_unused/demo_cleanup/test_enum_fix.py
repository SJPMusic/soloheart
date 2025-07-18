#!/usr/bin/env python3
"""
Test script to verify enum fixes and orchestrator functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dnd_game.narrative_bridge import NarrativeBridge
from narrative_engine.narrative_structure.character_arcs import ArcType, ArcStatus
from narrative_engine.narrative_structure.plot_threads import ThreadType, ThreadStatus
from narrative_engine.memory.emotional_memory import EmotionType

def test_enum_fixes():
    """Test if enum issues are resolved."""
    print("🧪 Testing Enum Fixes")
    print("=" * 40)
    
    # Initialize bridge
    bridge = NarrativeBridge("test-enum-campaign")
    
    # Test 1: Create character arc with enum
    print("\n1. Testing Character Arc Creation")
    try:
        arc_id = bridge.create_character_arc(
            character_id="test_player",
            name="Test Growth Arc",
            arc_type=ArcType.GROWTH,  # Using enum object
            description="A test character arc for growth.",
            tags=["test", "growth"],
            emotional_themes=["determination", "curiosity"]
        )
        print(f"✅ Character arc created successfully: {arc_id}")
    except Exception as e:
        print(f"❌ Character arc creation failed: {e}")
    
    # Test 2: Create plot thread with enum
    print("\n2. Testing Plot Thread Creation")
    try:
        thread_id = bridge.create_plot_thread(
            name="Test Mystery Thread",
            thread_type=ThreadType.MYSTERY,  # Using enum object
            description="A test mystery plot thread.",
            priority=8,
            assigned_characters=["test_player"],
            tags=["test", "mystery"]
        )
        print(f"✅ Plot thread created successfully: {thread_id}")
    except Exception as e:
        print(f"❌ Plot thread creation failed: {e}")
    
    # Test 3: Get character arcs
    print("\n3. Testing Character Arc Retrieval")
    try:
        arcs = bridge.get_character_arcs(status=ArcStatus.ACTIVE)  # Using enum object
        print(f"✅ Retrieved {len(arcs)} active character arcs")
        for arc in arcs:
            print(f"   - {arc.get('name', 'Unknown')} ({arc.get('arc_type', 'Unknown')})")
    except Exception as e:
        print(f"❌ Character arc retrieval failed: {e}")
    
    # Test 4: Get plot threads
    print("\n4. Testing Plot Thread Retrieval")
    try:
        threads = bridge.get_plot_threads(status=ThreadStatus.OPEN)  # Using enum object
        print(f"✅ Retrieved {len(threads)} open plot threads")
        for thread in threads:
            print(f"   - {thread.get('name', 'Unknown')} (Priority: {thread.get('priority', 0)})")
    except Exception as e:
        print(f"❌ Plot thread retrieval failed: {e}")
    
    # Test 5: Test emotional memory
    print("\n5. Testing Emotional Memory")
    try:
        # Store memory with emotion
        success = bridge.store_dnd_memory(
            content="Test memory with fear emotion",
            memory_type="test",
            tags=["test", "fear"],
            primary_emotion=EmotionType.FEAR,
            emotional_intensity=0.8
        )
        print(f"✅ Memory stored with emotion: {success}")
        
        # Recall memories
        memories = bridge.recall_related_memories("fear", max_results=3)
        print(f"✅ Retrieved {len(memories)} related memories")
        for memory in memories:
            print(f"   - {memory.get('content', 'Unknown')} (Emotion: {memory.get('emotion', 'Unknown')})")
    except Exception as e:
        print(f"❌ Emotional memory test failed: {e}")
    
    # Test 6: Test orchestrator events
    print("\n6. Testing Orchestrator Events")
    try:
        events = bridge.generate_orchestration_events(max_events=2)
        print(f"✅ Generated {len(events)} orchestration events")
        for event in events:
            print(f"   - {event.event_type} (Priority: {event.priority})")
    except Exception as e:
        print(f"❌ Orchestrator events failed: {e}")
    
    print("\n🎯 Enum Fix Test Complete!")

if __name__ == "__main__":
    test_enum_fixes() 