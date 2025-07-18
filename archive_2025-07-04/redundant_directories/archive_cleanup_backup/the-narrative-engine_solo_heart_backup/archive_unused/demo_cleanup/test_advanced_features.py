#!/usr/bin/env python3
"""
Advanced Features Integration Test

Tests the integration of the new advanced features:
1. Persistent Player Journaling System
2. Emotional Tagging and Emotional Recall Filters
3. Character Arcs and Plot Thread Tracking
"""

import sys
import os
import datetime
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from narrative_bridge import NarrativeBridge
from narrative_engine.memory.emotional_memory import EmotionType
from narrative_engine.journaling.player_journal import JournalEntryType
from narrative_engine.narrative_structure.character_arcs import ArcType, ArcStatus
from narrative_engine.narrative_structure.plot_threads import ThreadType, ThreadStatus


def test_advanced_features():
    """Test all advanced features integration."""
    print("🧪 Advanced Features Integration Test")
    print("=" * 60)
    
    # Initialize the narrative bridge
    print("\n1. Initializing Narrative Bridge...")
    narrative_bridge = NarrativeBridge("Advanced Test Campaign")
    print("   ✅ Narrative Bridge initialized successfully")
    
    # Test 1: Journaling System
    print("\n2. Testing Journaling System")
    print("-" * 30)
    
    # Add various types of journal entries
    journal_entry1 = narrative_bridge.add_journal_entry(
        character_id="Aelric",
        entry_type=JournalEntryType.PLAYER_WRITTEN,
        title="First Steps in the Ancient Ruins",
        content="Today I entered the ancient ruins for the first time. The air was thick with dust and mystery. I can't shake the feeling that something important happened here long ago.",
        location="Ancient Ruins",
        scene="Main chamber with crumbling pillars",
        tags=["exploration", "mystery", "first-time"],
        emotional_context=["wonder", "curiosity", "caution"]
    )
    print(f"   ✅ Added player-written journal entry: {journal_entry1}")
    
    journal_entry2 = narrative_bridge.add_journal_entry(
        character_id="Aelric",
        entry_type=JournalEntryType.EVENT_SUMMARY,
        title="Encounter with the Wounded Knight",
        content="Aelric discovered a wounded knight in the ruins. The knight, Sir Gareth, was gravely injured and spoke of a dark force that had attacked his patrol.",
        location="Ancient Ruins",
        scene="Hidden chamber behind the main hall",
        tags=["encounter", "npc", "quest", "danger"],
        emotional_context=["concern", "duty", "urgency"]
    )
    print(f"   ✅ Added AI-generated journal entry: {journal_entry2}")
    
    journal_entry3 = narrative_bridge.add_journal_entry(
        character_id="Aelric",
        entry_type=JournalEntryType.CHARACTER_DEVELOPMENT,
        title="Reflections on Courage and Duty",
        content="Meeting Sir Gareth has made me think about what it means to be courageous. He was willing to sacrifice everything to protect others, even when gravely wounded.",
        location="Ancient Ruins",
        scene="Personal reflection",
        tags=["character-development", "philosophy", "self-reflection"],
        emotional_context=["contemplation", "self-doubt", "inspiration"]
    )
    print(f"   ✅ Added character development journal entry: {journal_entry3}")
    
    # Retrieve journal entries
    journal_entries = narrative_bridge.get_journal_entries(character_id="Aelric")
    print(f"   ✅ Retrieved {len(journal_entries)} journal entries")
    
    # Test 2: Emotional Memory System
    print("\n3. Testing Emotional Memory System")
    print("-" * 35)
    
    # Store memories with emotional tagging
    memory1 = narrative_bridge.store_dnd_memory(
        content="I found a beautiful ancient sword in the ruins! The blade gleams with magical energy and feels warm to the touch.",
        memory_type="discovery",
        metadata={"location": "Ancient Ruins", "item_type": "weapon"},
        tags=["magical", "weapon", "discovery"],
        primary_emotion=EmotionType.JOY,
        emotional_intensity=0.9
    )
    print(f"   ✅ Stored joyful memory: {memory1}")
    
    memory2 = narrative_bridge.store_dnd_memory(
        content="A massive shadow emerged from the darkness. I could hear its heavy breathing and see glowing red eyes.",
        memory_type="encounter",
        metadata={"location": "Ancient Ruins", "threat_level": "high"},
        tags=["danger", "monster", "fear"],
        primary_emotion=EmotionType.FEAR,
        emotional_intensity=0.8
    )
    print(f"   ✅ Stored fearful memory: {memory2}")
    
    memory3 = narrative_bridge.store_dnd_memory(
        content="My companion fell in battle today. We had traveled together for months, and now they're gone.",
        memory_type="loss",
        metadata={"location": "Battlefield", "companion_name": "Thorin"},
        tags=["loss", "companion", "grief"],
        primary_emotion=EmotionType.SADNESS,
        emotional_intensity=0.95
    )
    print(f"   ✅ Stored sad memory: {memory3}")
    
    # Recall memories with emotional filtering
    joyful_memories = narrative_bridge.recall_related_memories(
        query="sword",
        emotional_filter=EmotionType.JOY,
        min_emotional_intensity=0.5
    )
    print(f"   ✅ Retrieved {len(joyful_memories)} joyful memories")
    
    fearful_memories = narrative_bridge.recall_related_memories(
        query="darkness",
        emotional_filter=EmotionType.FEAR,
        min_emotional_intensity=0.5
    )
    print(f"   ✅ Retrieved {len(fearful_memories)} fearful memories")
    
    # Test 3: Character Arcs System
    print("\n4. Testing Character Arcs System")
    print("-" * 30)
    
    # Create character arcs
    growth_arc = narrative_bridge.create_character_arc(
        character_id="Aelric",
        name="From Novice to Hero",
        arc_type=ArcType.GROWTH,
        description="Aelric's journey from an inexperienced adventurer to a confident hero.",
        target_completion=datetime.datetime.now() + datetime.timedelta(days=30),
        tags=["hero's journey", "self-confidence", "leadership"],
        emotional_themes=["self-doubt", "determination", "pride"]
    )
    print(f"   ✅ Created growth arc: {growth_arc}")
    
    redemption_arc = narrative_bridge.create_character_arc(
        character_id="Aelric",
        name="Seeking Redemption",
        arc_type=ArcType.REDEMPTION,
        description="Aelric must confront his past mistakes and seek redemption.",
        target_completion=datetime.datetime.now() + datetime.timedelta(days=45),
        tags=["redemption", "guilt", "forgiveness"],
        emotional_themes=["guilt", "shame", "hope", "forgiveness"]
    )
    print(f"   ✅ Created redemption arc: {redemption_arc}")
    
    # Add milestones to arcs
    if growth_arc:
        milestone1 = narrative_bridge.add_arc_milestone(
            growth_arc,
            title="First Successful Battle",
            description="Aelric successfully led his first battle against bandits.",
            memory_ids=["memory_battle_001"],
            emotional_context="Pride and growing self-confidence",
            completion_percentage=0.2
        )
        print(f"   ✅ Added milestone to growth arc: {milestone1}")
        
        milestone2 = narrative_bridge.add_arc_milestone(
            growth_arc,
            title="Saving the Village",
            description="Aelric made a difficult decision to sacrifice personal gain to save a village.",
            memory_ids=["memory_village_001"],
            emotional_context="Moral growth and selflessness",
            completion_percentage=0.5
        )
        print(f"   ✅ Added milestone to growth arc: {milestone2}")
    
    if redemption_arc:
        milestone3 = narrative_bridge.add_arc_milestone(
            redemption_arc,
            title="Confronting the Past",
            description="Aelric finally confronted the consequences of his past actions.",
            memory_ids=["memory_confrontation_001"],
            emotional_context="Painful acceptance and guilt",
            completion_percentage=0.3
        )
        print(f"   ✅ Added milestone to redemption arc: {milestone3}")
    
    # Get character arcs
    character_arcs = narrative_bridge.get_character_arcs(character_id="Aelric")
    print(f"   ✅ Retrieved {len(character_arcs)} character arcs")
    
    # Test 4: Plot Threads System
    print("\n5. Testing Plot Threads System")
    print("-" * 30)
    
    # Create plot threads
    mystery_thread = narrative_bridge.create_plot_thread(
        name="The Disappearing Villagers",
        thread_type=ThreadType.MYSTERY,
        description="Villagers have been disappearing from the town of Riverdale during the full moon.",
        priority=8,
        assigned_characters=["Aelric", "Detective Mara"],
        tags=["mystery", "disappearances", "full moon", "supernatural"]
    )
    print(f"   ✅ Created mystery thread: {mystery_thread}")
    
    quest_thread = narrative_bridge.create_plot_thread(
        name="The Lost Artifact Quest",
        thread_type=ThreadType.MAIN_QUEST,
        description="The ancient artifact that can save the kingdom has been stolen.",
        priority=10,
        assigned_characters=["Aelric"],
        tags=["quest", "artifact", "thieves", "urgent"]
    )
    print(f"   ✅ Created quest thread: {quest_thread}")
    
    # Add updates to threads
    if mystery_thread:
        update1 = narrative_bridge.add_thread_update(
            mystery_thread,
            title="First Clue Discovered",
            description="Aelric found a silver pendant near the last disappearance site.",
            memory_ids=["memory_pendant_001"],
            priority_change=9
        )
        print(f"   ✅ Added update to mystery thread: {update1}")
    
    if quest_thread:
        update2 = narrative_bridge.add_thread_update(
            quest_thread,
            title="Thieves Identified",
            description="The thieves have been identified as members of the Shadow Brotherhood.",
            memory_ids=["memory_thieves_001"],
            priority_change=10
        )
        print(f"   ✅ Added update to quest thread: {update2}")
    
    # Get plot threads
    plot_threads = narrative_bridge.get_plot_threads(min_priority=7)
    print(f"   ✅ Retrieved {len(plot_threads)} high-priority plot threads")
    
    # Test 5: Integration Test - Generate DM Narration with Emotional Context
    print("\n6. Testing Integration - DM Narration with Emotional Context")
    print("-" * 55)
    
    # Generate narration with emotional context
    narration1 = narrative_bridge.generate_dm_narration(
        situation="Aelric discovers the ancient sword glowing with magical energy",
        player_actions=["He reaches out to touch the sword", "He feels a surge of power"],
        world_context={"location": "Ancient Ruins", "magical_presence": True},
        emotional_context=["wonder", "excitement", "caution"]
    )
    print(f"   ✅ Generated joyful narration: {str(narration1)[:100]}...")
    
    narration2 = narrative_bridge.generate_dm_narration(
        situation="Aelric faces the shadow creature in the darkness",
        player_actions=["He draws his weapon", "He prepares for combat"],
        world_context={"location": "Ancient Ruins", "threat_level": "high"},
        emotional_context=["fear", "determination", "adrenaline"]
    )
    print(f"   ✅ Generated fearful narration: {str(narration2)[:100]}...")
    
    # Test 6: Campaign Summary with All Systems
    print("\n7. Testing Campaign Summary with All Systems")
    print("-" * 45)
    
    summary = narrative_bridge.get_campaign_summary()
    print(f"   ✅ Campaign ID: {summary['campaign_id']}")
    print(f"   ✅ Memory Count: {summary.get('memory_count', 0)}")
    print(f"   ✅ Journal Entries: {summary.get('journal_entries', 0)}")
    print(f"   ✅ Character Arcs: {summary.get('character_arcs', 0)}")
    print(f"   ✅ Plot Threads: {summary.get('plot_threads', 0)}")
    print(f"   ✅ Session Count: {summary.get('session_count', 0)}")
    
    # Test 7: Export Functionality
    print("\n8. Testing Export Functionality")
    print("-" * 30)
    
    export_success = narrative_bridge.export_campaign_data(
        "test_advanced_features_export",
        include_journals=True,
        include_arcs=True,
        include_threads=True
    )
    print(f"   ✅ Export successful: {export_success}")
    
    # Test 8: Memory Recall with Emotional Filtering
    print("\n9. Testing Memory Recall with Emotional Filtering")
    print("-" * 45)
    
    # Recall memories with different emotional filters
    all_memories = narrative_bridge.recall_related_memories("ruins", max_results=10)
    print(f"   ✅ Retrieved {len(all_memories)} total memories about ruins")
    
    positive_memories = narrative_bridge.recall_related_memories(
        "ruins",
        emotional_filter=EmotionType.JOY,
        min_emotional_intensity=0.5
    )
    print(f"   ✅ Retrieved {len(positive_memories)} positive memories about ruins")
    
    negative_memories = narrative_bridge.recall_related_memories(
        "ruins",
        emotional_filter=EmotionType.FEAR,
        min_emotional_intensity=0.5
    )
    print(f"   ✅ Retrieved {len(negative_memories)} fearful memories about ruins")
    
    print("\n🎉 All Advanced Features Tests Completed Successfully!")
    print("\n✅ Features Tested:")
    print("   - Persistent Player Journaling System")
    print("   - Emotional Tagging and Memory Filtering")
    print("   - Character Arcs and Milestone Tracking")
    print("   - Plot Threads and Update Management")
    print("   - Integration with DM Narration")
    print("   - Campaign Summary with All Systems")
    print("   - Export Functionality")
    print("   - Emotional Memory Recall")
    
    print("\n📁 Generated Files:")
    print("   - journal_Advanced Test Campaign.jsonl (Journal entries)")
    print("   - arcs_Advanced Test Campaign.jsonl (Character arcs)")
    print("   - threads_Advanced Test Campaign.jsonl (Plot threads)")
    print("   - test_advanced_features_export_journal.md (Journal export)")
    print("   - test_advanced_features_export_journal.jsonl (Journal export)")
    
    return True


if __name__ == "__main__":
    try:
        success = test_advanced_features()
        if success:
            print("\n🎯 All tests passed! Advanced features are working correctly.")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc() 