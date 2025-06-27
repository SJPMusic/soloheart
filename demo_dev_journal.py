#!/usr/bin/env python3
"""
Development Journal Demo
========================

Demonstrates the development journal functionality with sample entries
"""

import datetime
from core.development_journal import (
    DevelopmentJournal, JournalEntryType, Priority
)

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def demo_development_journal():
    """Demonstrate the development journal system"""
    print_header("DEVELOPMENT JOURNAL DEMO")
    
    # Initialize journal
    journal = DevelopmentJournal()
    
    # Add some sample entries
    print_section("Adding Sample Journal Entries")
    
    # Progress entry
    progress_entry = journal.add_entry(
        entry_type=JournalEntryType.PROGRESS,
        title="Core Session Logger Implementation",
        content="""
Successfully implemented the core session logging system with the following features:
- Dialogue logging with speaker tracking
- Action logging with entity extraction
- Combat encounter logging
- Exploration logging with location tracking
- Decision logging with consequence tracking

The system integrates well with the AI memory system and provides comprehensive session summaries.
        """.strip(),
        priority=Priority.HIGH,
        tags=["core-system", "session-logging", "ai-integration"],
        related_files=["core/session_logger.py", "core/memory_system.py"],
        assignee="Stephen",
        estimated_hours=8.0
    )
    # Update with actual hours
    journal.update_entry(progress_entry.id, actual_hours=7.5, status="completed")
    print(f"✅ Added progress entry: {progress_entry.title}")
    
    # Idea entry
    idea_entry = journal.add_entry(
        entry_type=JournalEntryType.IDEA,
        title="Character Development AI Assistant",
        content="""
Create an AI assistant that helps players develop their characters by:
- Suggesting personality traits based on race/class combinations
- Recommending character arcs and development paths
- Generating backstory elements and motivations
- Providing roleplaying tips and suggestions

This could integrate with the existing character manager and provide personalized guidance.
        """.strip(),
        priority=Priority.MEDIUM,
        tags=["ai-feature", "character-development", "player-experience"],
        related_files=["core/character_manager.py"],
        assignee="Stephen",
        estimated_hours=12.0
    )
    print(f"✅ Added idea entry: {idea_entry.title}")
    
    # Bug fix entry
    bug_entry = journal.add_entry(
        entry_type=JournalEntryType.BUG_FIX,
        title="Fix Entity Extraction in Memory System",
        content="""
Fixed issue where entity extraction was not properly handling compound names like "Gandalf the Grey".
The regex pattern needed to be updated to capture full titles and epithets.

Changes made:
- Updated entity extraction regex in memory_system.py
- Added test cases for compound entity names
- Improved entity confidence scoring for titles
        """.strip(),
        priority=Priority.HIGH,
        tags=["bug-fix", "memory-system", "entity-extraction"],
        related_files=["core/memory_system.py", "test_basic.py"],
        assignee="Stephen",
        estimated_hours=2.0
    )
    # Update with actual hours and status
    journal.update_entry(bug_entry.id, actual_hours=1.5, status="completed")
    print(f"✅ Added bug fix entry: {bug_entry.title}")
    
    # Feature request entry
    feature_entry = journal.add_entry(
        entry_type=JournalEntryType.FEATURE_REQUEST,
        title="Web Interface for Campaign Management",
        content="""
Create a web-based interface for the campaign manager that includes:
- Real-time session logging interface
- Character sheet viewer/editor
- Campaign timeline visualization
- AI-generated content browser
- Player dashboard with session summaries

This would make the tool more accessible to non-technical users and provide a better user experience.
        """.strip(),
        priority=Priority.MEDIUM,
        tags=["web-interface", "user-experience", "accessibility"],
        related_files=["interface/"],
        assignee="Stephen",
        estimated_hours=40.0
    )
    print(f"✅ Added feature request entry: {feature_entry.title}")
    
    # Design decision entry
    design_entry = journal.add_entry(
        entry_type=JournalEntryType.DESIGN_DECISION,
        title="JSON vs SQLite for Data Storage",
        content="""
Decided to use a hybrid approach for data storage:
- JSON files for human-readable session logs and campaign data
- SQLite database for AI memory system and complex queries

Rationale:
- JSON provides easy backup/restore and human inspection
- SQLite enables efficient AI queries and relationship mapping
- Hybrid approach balances simplicity with performance
- Allows for future migration to other databases if needed
        """.strip(),
        priority=Priority.LOW,
        tags=["architecture", "data-storage", "design"],
        related_files=["core/memory_system.py", "core/session_logger.py"],
        assignee="Stephen",
        estimated_hours=0.5
    )
    print(f"✅ Added design decision entry: {design_entry.title}")
    
    # Add milestones
    print_section("Adding Development Milestones")
    
    # Current milestone
    current_milestone = journal.add_milestone(
        title="Core System Foundation",
        description="Complete the foundational systems: session logging, memory system, and character management",
        target_date=datetime.date.today() + datetime.timedelta(days=7)
    )
    print(f"✅ Added milestone: {current_milestone.title}")
    
    # Link entries to milestone
    journal.link_entry_to_milestone(progress_entry.id, current_milestone.id)
    journal.link_entry_to_milestone(bug_entry.id, current_milestone.id)
    
    # Future milestone
    future_milestone = journal.add_milestone(
        title="AI Content Generation",
        description="Implement AI-powered content generation for NPCs, locations, and quests",
        target_date=datetime.date.today() + datetime.timedelta(days=30)
    )
    print(f"✅ Added milestone: {future_milestone.title}")
    
    journal.link_entry_to_milestone(idea_entry.id, future_milestone.id)
    
    # Show project summary
    print_section("Project Summary")
    summary = journal.get_project_summary()
    
    print(f"Project: {summary['project_name']}")
    print(f"Version: {summary['version']}")
    print(f"\nEntries:")
    print(f"  Total: {summary['total_entries']}")
    print(f"  Completed: {summary['completed_entries']}")
    print(f"  Open: {summary['open_entries']}")
    print(f"  In Progress: {summary['in_progress_entries']}")
    
    print(f"\nMilestones:")
    print(f"  Total: {summary['total_milestones']}")
    print(f"  Completed: {summary['completed_milestones']}")
    
    print(f"\nTime Tracking:")
    print(f"  Estimated: {summary['total_estimated_hours']:.1f}h")
    print(f"  Actual: {summary['total_actual_hours']:.1f}h")
    
    # Search demonstration
    print_section("Search Demonstration")
    
    print("Searching for entries with 'AI' tag:")
    ai_entries = journal.search_entries(tags=["ai-feature"])
    for entry in ai_entries:
        print(f"  - {entry.title} ({entry.entry_type.value})")
    
    print("\nSearching for high priority entries:")
    high_priority = journal.search_entries(priority=Priority.HIGH)
    for entry in high_priority:
        print(f"  - {entry.title} ({entry.status})")
    
    # Export demonstration
    print_section("Export Demonstration")
    
    export_file = journal.export_journal()
    print(f"✅ Journal exported to: {export_file}")
    
    backup_file = journal.backup_journal()
    print(f"✅ Journal backed up to: {backup_file}")
    
    print("\n🎉 Development Journal Demo Complete!")
    print("\nYou can now use the CLI to manage your development journal:")
    print("  python3 dev_journal_cli.py add      # Add new entries")
    print("  python3 dev_journal_cli.py list     # List recent entries")
    print("  python3 dev_journal_cli.py search   # Search entries")
    print("  python3 dev_journal_cli.py summary  # Show project summary")

def print_section(title: str):
    """Print a formatted section"""
    print(f"\n--- {title} ---")

if __name__ == "__main__":
    demo_development_journal() 