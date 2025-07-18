#!/usr/bin/env python3
"""
Journaling System Demo

Demonstrates the persistent player journaling system with writing,
retrieving, and exporting capabilities.
"""

import sys
import os
import datetime
from pathlib import Path

# Add the parent directory to the path to import the journaling module
sys.path.insert(0, str(Path(__file__).parent.parent))

from journaling.player_journal import PlayerJournal, JournalEntryType
from journaling.journal_exporter import JournalExporter


def demo_journaling_system():
    """Demonstrate the journaling system functionality."""
    print("📖 Journaling System Demo")
    print("=" * 50)
    
    # Initialize the journal system
    journal = PlayerJournal("demo_journal_entries.jsonl")
    
    # Demo 1: Add various types of journal entries
    print("\n1. Adding Journal Entries")
    print("-" * 30)
    
    # Player-written entry
    player_entry = journal.add_entry(
        character_id="Aelric",
        campaign_id="Test Campaign",
        entry_type=JournalEntryType.PLAYER_WRITTEN,
        title="First Steps in the Ancient Ruins",
        content="Today I entered the ancient ruins for the first time. The air was thick with dust and mystery. I can't shake the feeling that something important happened here long ago. The stone walls seem to whisper secrets to those who listen carefully.",
        location="Ancient Ruins",
        scene="Main chamber with crumbling pillars",
        tags=["exploration", "mystery", "first-time"],
        emotional_context=["wonder", "curiosity", "caution"]
    )
    print(f"✅ Added player-written entry: {player_entry.title}")
    
    # AI-generated event summary
    ai_summary = journal.add_entry(
        character_id="Aelric",
        campaign_id="Test Campaign",
        entry_type=JournalEntryType.EVENT_SUMMARY,
        title="Encounter with the Wounded Knight",
        content="Aelric discovered a wounded knight in the ruins. The knight, Sir Gareth, was gravely injured and spoke of a dark force that had attacked his patrol. He warned of increasing danger in the surrounding lands and begged Aelric to carry a message to the nearby town of Riverdale.",
        location="Ancient Ruins",
        scene="Hidden chamber behind the main hall",
        tags=["encounter", "npc", "quest", "danger"],
        emotional_context=["concern", "duty", "urgency"]
    )
    print(f"✅ Added AI-generated summary: {ai_summary.title}")
    
    # Quest log entry
    quest_entry = journal.add_entry(
        character_id="Aelric",
        campaign_id="Test Campaign",
        entry_type=JournalEntryType.QUEST_LOG,
        title="Quest: Deliver Sir Gareth's Message",
        content="Sir Gareth has entrusted me with delivering an urgent message to the town of Riverdale. The message warns of a dark force that has been attacking patrols in the area. I should make haste to Riverdale and find the town's leader, Mayor Thorne.",
        location="Ancient Ruins",
        scene="Planning next steps",
        tags=["quest", "urgent", "delivery"],
        emotional_context=["responsibility", "urgency", "determination"]
    )
    print(f"✅ Added quest log entry: {quest_entry.title}")
    
    # Character development entry
    dev_entry = journal.add_entry(
        character_id="Aelric",
        campaign_id="Test Campaign",
        entry_type=JournalEntryType.CHARACTER_DEVELOPMENT,
        title="Reflections on Courage and Duty",
        content="Meeting Sir Gareth has made me think about what it means to be courageous. He was willing to sacrifice everything to protect others, even when gravely wounded. I find myself questioning whether I would have the same strength of character in such a situation. Perhaps this quest is not just about delivering a message, but about discovering what kind of person I truly am.",
        location="Ancient Ruins",
        scene="Personal reflection",
        tags=["character-development", "philosophy", "self-reflection"],
        emotional_context=["contemplation", "self-doubt", "inspiration"]
    )
    print(f"✅ Added character development entry: {dev_entry.title}")
    
    # Demo 2: Retrieve and display entries
    print("\n2. Retrieving Journal Entries")
    print("-" * 30)
    
    # Get all entries for Aelric
    aelric_entries = journal.get_entries_by_character("Aelric", "Test Campaign")
    print(f"📚 Found {len(aelric_entries)} entries for Aelric:")
    
    for i, entry in enumerate(aelric_entries, 1):
        print(f"  {i}. {entry.title} ({entry.entry_type.value})")
        print(f"     Location: {entry.location or 'Unknown'}")
        print(f"     Date: {entry.timestamp.strftime('%Y-%m-%d %H:%M')}")
        print(f"     Tags: {', '.join(entry.tags) if entry.tags else 'None'}")
        print()
    
    # Demo 3: Search functionality
    print("\n3. Search Functionality")
    print("-" * 30)
    
    # Search for entries containing "knight"
    knight_entries = journal.search_entries("knight", character_id="Aelric")
    print(f"🔍 Found {len(knight_entries)} entries containing 'knight':")
    for entry in knight_entries:
        print(f"  - {entry.title}")
    
    # Search for entries containing "quest"
    quest_entries = journal.search_entries("quest", character_id="Aelric")
    print(f"🔍 Found {len(quest_entries)} entries containing 'quest':")
    for entry in quest_entries:
        print(f"  - {entry.title}")
    
    # Demo 4: Export functionality
    print("\n4. Export Functionality")
    print("-" * 30)
    
    # Export to JSONL
    jsonl_success = JournalExporter.export_to_jsonl(
        aelric_entries,
        "demo_aelric_journal.jsonl",
        include_metadata=True
    )
    if jsonl_success:
        print("✅ Exported to JSONL: demo_aelric_journal.jsonl")
    
    # Export to Markdown
    markdown_success = JournalExporter.export_to_markdown(
        aelric_entries,
        "demo_aelric_journal.md",
        include_metadata=True,
        group_by="entry_type"
    )
    if markdown_success:
        print("✅ Exported to Markdown: demo_aelric_journal.md")
    
    # Export character summary
    summary_success = JournalExporter.export_character_summary(
        aelric_entries,
        "Aelric",
        "demo_aelric_summary.md"
    )
    if summary_success:
        print("✅ Exported character summary: demo_aelric_summary.md")
    
    # Demo 5: Journal statistics
    print("\n5. Journal Statistics")
    print("-" * 30)
    
    stats = journal.get_journal_stats(character_id="Aelric", campaign_id="Test Campaign")
    print(f"📊 Journal Statistics for Aelric:")
    print(f"  Total Entries: {stats['total_entries']}")
    print(f"  Entry Types: {stats['entry_types']}")
    print(f"  Date Range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
    
    print("\n🎉 Journaling System Demo Complete!")
    print("\nGenerated files:")
    print("  - demo_journal_entries.jsonl (raw journal data)")
    print("  - demo_aelric_journal.jsonl (JSONL export)")
    print("  - demo_aelric_journal.md (Markdown export)")
    print("  - demo_aelric_summary.md (Character summary)")


if __name__ == "__main__":
    demo_journaling_system() 