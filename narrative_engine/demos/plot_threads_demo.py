#!/usr/bin/env python3
"""
Plot Threads Demo

Demonstrates the plot thread tracking system for managing unresolved
narrative threads and their resolution status.
"""

import sys
import os
import datetime
from pathlib import Path

# Add the parent directory to the path to import the narrative structure module
sys.path.insert(0, str(Path(__file__).parent.parent))

from narrative_structure.plot_threads import (
    PlotThreadManager,
    PlotThread,
    ThreadType,
    ThreadStatus
)


def demo_plot_threads_system():
    """Demonstrate the plot threads system functionality."""
    print("🧵 Plot Threads System Demo")
    print("=" * 50)
    
    # Initialize the plot thread manager
    thread_manager = PlotThreadManager("demo_plot_threads.jsonl")
    
    # Demo 1: Create plot threads
    print("\n1. Creating Plot Threads")
    print("-" * 25)
    
    # Thread 1: Mystery thread
    mystery_thread = thread_manager.create_thread(
        campaign_id="Test Campaign",
        name="The Disappearing Villagers",
        thread_type=ThreadType.MYSTERY,
        description="Villagers have been disappearing from the town of Riverdale. No bodies are found, and there are no signs of struggle. The disappearances happen during the full moon.",
        priority=8,
        assigned_characters=["Aelric", "Detective Mara"],
        tags=["mystery", "disappearances", "full moon", "supernatural"],
        metadata={"clues_found": 0, "victims_count": 5}
    )
    print(f"✅ Created mystery thread: {mystery_thread.name}")
    
    # Thread 2: Quest thread
    quest_thread = thread_manager.create_thread(
        campaign_id="Test Campaign",
        name="The Lost Artifact Quest",
        thread_type=ThreadType.MAIN_QUEST,
        description="The ancient artifact that can save the kingdom has been stolen. Aelric must track down the thieves and recover the artifact before it falls into the wrong hands.",
        priority=10,
        assigned_characters=["Aelric"],
        tags=["quest", "artifact", "thieves", "urgent"],
        metadata={"artifact_type": "Crown of Light", "thieves_known": False}
    )
    print(f"✅ Created quest thread: {quest_thread.name}")
    
    # Thread 3: Relationship thread
    relationship_thread = thread_manager.create_thread(
        campaign_id="Test Campaign",
        name="Aelric and Mara's Growing Friendship",
        thread_type=ThreadType.RELATIONSHIP,
        description="Aelric and Detective Mara have been working together on cases and their friendship is deepening. However, Mara has a mysterious past that she's reluctant to share.",
        priority=6,
        assigned_characters=["Aelric", "Mara"],
        tags=["relationship", "friendship", "mystery", "trust"],
        metadata={"relationship_level": "friends", "secrets_shared": 0}
    )
    print(f"✅ Created relationship thread: {relationship_thread.name}")
    
    # Thread 4: World event thread
    world_thread = thread_manager.create_thread(
        campaign_id="Test Campaign",
        name="The Rising Darkness",
        thread_type=ThreadType.WORLD_EVENT,
        description="Dark forces are gathering in the northern mountains. Ancient evils that were sealed away are beginning to stir, threatening the entire realm.",
        priority=9,
        assigned_characters=["Aelric", "King Aldric", "Council of Mages"],
        tags=["world_event", "darkness", "ancient_evil", "apocalyptic"],
        metadata={"seals_broken": 2, "total_seals": 7, "time_remaining": "unknown"}
    )
    print(f"✅ Created world event thread: {world_thread.name}")
    
    # Thread 5: Political thread
    political_thread = thread_manager.create_thread(
        campaign_id="Test Campaign",
        name="The Council's Internal Conflict",
        thread_type=ThreadType.POLITICAL,
        description="The Royal Council is divided over how to handle the rising darkness. Some want to prepare for war, others want to seek diplomatic solutions, and a few may have ulterior motives.",
        priority=7,
        assigned_characters=["King Aldric", "Council Members"],
        tags=["political", "conflict", "council", "diplomacy"],
        metadata={"factions": ["war_hawks", "doves", "unknown"], "votes_needed": 5}
    )
    print(f"✅ Created political thread: {political_thread.name}")
    
    # Demo 2: Add updates to threads
    print("\n2. Adding Updates to Threads")
    print("-" * 30)
    
    # Mystery thread updates
    thread_manager.add_update_to_thread(
        mystery_thread.thread_id,
        title="First Clue Discovered",
        description="Aelric found a silver pendant near the last disappearance site. The pendant has strange markings that glow in moonlight.",
        memory_ids=["memory_pendant_001", "memory_investigation_001"],
        priority_change=9  # Increased priority due to new clue
    )
    print("✅ Added update: First Clue Discovered")
    
    thread_manager.add_update_to_thread(
        mystery_thread.thread_id,
        title="Pattern Emerges",
        description="All disappearances happen on the night of the full moon, and all victims were wearing silver jewelry. The pattern suggests a supernatural predator.",
        memory_ids=["memory_pattern_001", "memory_silver_001"],
        priority_change=9
    )
    print("✅ Added update: Pattern Emerges")
    
    # Quest thread updates
    thread_manager.add_update_to_thread(
        quest_thread.thread_id,
        title="Thieves Identified",
        description="The thieves have been identified as members of the Shadow Brotherhood, a notorious criminal organization. They were last seen heading toward the Black Forest.",
        memory_ids=["memory_thieves_001", "memory_shadow_brotherhood_001"],
        priority_change=10
    )
    print("✅ Added update: Thieves Identified")
    
    thread_manager.add_update_to_thread(
        quest_thread.thread_id,
        title="Artifact Location Discovered",
        description="The artifact is being held in an ancient temple in the Black Forest. The temple is heavily guarded and protected by deadly traps.",
        memory_ids=["memory_temple_001", "memory_traps_001"],
        priority_change=10
    )
    print("✅ Added update: Artifact Location Discovered")
    
    # Relationship thread updates
    thread_manager.add_update_to_thread(
        relationship_thread.thread_id,
        title="Mara Shares Her Past",
        description="Mara finally opened up about her past. She was once a member of the Shadow Brotherhood but left when she discovered their true nature. She's been hiding from them ever since.",
        memory_ids=["memory_mara_past_001", "memory_trust_001"],
        priority_change=7
    )
    print("✅ Added update: Mara Shares Her Past")
    
    # World event updates
    thread_manager.add_update_to_thread(
        world_thread.thread_id,
        title="Third Seal Broken",
        description="Another ancient seal has been broken. The darkness is spreading faster than expected. The Council estimates only 30 days before all seals are broken.",
        memory_ids=["memory_seal_001", "memory_urgency_001"],
        priority_change=10
    )
    print("✅ Added update: Third Seal Broken")
    
    # Demo 3: Query and display threads
    print("\n3. Querying Plot Threads")
    print("-" * 25)
    
    # Get all threads for the campaign
    campaign_threads = thread_manager.get_threads_by_campaign("Test Campaign")
    print(f"📚 Found {len(campaign_threads)} threads for Test Campaign:")
    
    for thread in campaign_threads:
        print(f"\n🧵 {thread.name} ({thread.thread_type.value})")
        print(f"   Status: {thread.status.value}")
        print(f"   Priority: {thread.priority}/10")
        print(f"   Assigned: {', '.join(thread.assigned_characters)}")
        print(f"   Updates: {len(thread.updates)}")
        print(f"   Description: {thread.description[:80]}...")
        
        # Show recent updates
        if thread.updates:
            print("   Recent updates:")
            for update in thread.updates[-2:]:  # Show last 2 updates
                print(f"     - {update.title}")
    
    # Demo 4: Filter threads by type
    print("\n4. Filtering Threads by Type")
    print("-" * 30)
    
    mystery_threads = thread_manager.get_threads_by_type(ThreadType.MYSTERY, "Test Campaign")
    print(f"🔍 Mystery threads: {len(mystery_threads)}")
    for thread in mystery_threads:
        print(f"  - {thread.name} (Priority: {thread.priority})")
    
    quest_threads = thread_manager.get_threads_by_type(ThreadType.MAIN_QUEST, "Test Campaign")
    print(f"⚔️ Main quest threads: {len(quest_threads)}")
    for thread in quest_threads:
        print(f"  - {thread.name} (Priority: {thread.priority})")
    
    relationship_threads = thread_manager.get_threads_by_type(ThreadType.RELATIONSHIP, "Test Campaign")
    print(f"💕 Relationship threads: {len(relationship_threads)}")
    for thread in relationship_threads:
        print(f"  - {thread.name} (Priority: {thread.priority})")
    
    # Demo 5: Get open threads
    print("\n5. Open Threads")
    print("-" * 15)
    
    open_threads = thread_manager.get_open_threads("Test Campaign", min_priority=7)
    print(f"🔓 High-priority open threads (priority >= 7): {len(open_threads)}")
    for thread in open_threads:
        print(f"  - {thread.name} (Priority: {thread.priority})")
    
    # Demo 6: Threads by character
    print("\n6. Threads by Character")
    print("-" * 20)
    
    aelric_threads = thread_manager.get_threads_by_character("Aelric", "Test Campaign")
    print(f"👤 Threads assigned to Aelric: {len(aelric_threads)}")
    for thread in aelric_threads:
        print(f"  - {thread.name} ({thread.thread_type.value}, Priority: {thread.priority})")
    
    mara_threads = thread_manager.get_threads_by_character("Mara", "Test Campaign")
    print(f"👤 Threads assigned to Mara: {len(mara_threads)}")
    for thread in mara_threads:
        print(f"  - {thread.name} ({thread.thread_type.value}, Priority: {thread.priority})")
    
    # Demo 7: Resolve a thread
    print("\n7. Resolving a Thread")
    print("-" * 20)
    
    # Resolve the mystery thread
    thread_manager.resolve_thread(
        mystery_thread.thread_id,
        "The mystery was solved when Aelric discovered that a werewolf was responsible for the disappearances. The werewolf was defeated and the villagers were found alive in its lair.",
        memory_ids=["memory_werewolf_001", "memory_rescue_001", "memory_resolution_001"]
    )
    print(f"✅ Resolved thread: {mystery_thread.name}")
    
    # Demo 8: Search functionality
    print("\n8. Search Functionality")
    print("-" * 20)
    
    # Search for threads containing "artifact"
    artifact_threads = thread_manager.search_threads("artifact", "Test Campaign")
    print(f"🔍 Found {len(artifact_threads)} threads containing 'artifact':")
    for thread in artifact_threads:
        print(f"  - {thread.name}")
    
    # Search for threads containing "darkness"
    darkness_threads = thread_manager.search_threads("darkness", "Test Campaign")
    print(f"🔍 Found {len(darkness_threads)} threads containing 'darkness':")
    for thread in darkness_threads:
        print(f"  - {thread.name}")
    
    # Demo 9: Thread summary statistics
    print("\n9. Thread Summary Statistics")
    print("-" * 30)
    
    stats = thread_manager.get_thread_summary("Test Campaign")
    print(f"📊 Thread Statistics for Test Campaign:")
    print(f"  Total threads: {stats['total_threads']}")
    print(f"  Average priority: {stats['average_priority']:.1f}")
    
    print("\n  Thread types:")
    for thread_type, count in stats['thread_types'].items():
        print(f"    {thread_type}: {count}")
    
    print("\n  Status breakdown:")
    for status, count in stats['status_counts'].items():
        print(f"    {status}: {count}")
    
    print("\n  Priority distribution:")
    for priority, count in stats['priority_distribution'].items():
        print(f"    Priority {priority}: {count}")
    
    print("\n🎉 Plot Threads System Demo Complete!")
    print("\nKey features demonstrated:")
    print("  ✅ Thread creation and management")
    print("  ✅ Update tracking")
    print("  ✅ Priority management")
    print("  ✅ Character assignment")
    print("  ✅ Type-based filtering")
    print("  ✅ Status tracking")
    print("  ✅ Thread resolution")
    print("  ✅ Search functionality")
    print("  ✅ Statistical analysis")


if __name__ == "__main__":
    demo_plot_threads_system() 