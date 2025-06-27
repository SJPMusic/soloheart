#!/usr/bin/env python3
"""
Development Journal CLI
=======================

Command-line interface for managing the DnD game development journal
"""

import sys
import argparse
import datetime
from typing import List
from core.development_journal import (
    DevelopmentJournal, JournalEntryType, Priority, 
    JournalEntry, DevelopmentMilestone
)

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_section(title: str):
    """Print a formatted section"""
    print(f"\n--- {title} ---")

def format_timestamp(timestamp: datetime.datetime) -> str:
    """Format timestamp for display"""
    return timestamp.strftime("%Y-%m-%d %H:%M")

def format_date(date: datetime.date) -> str:
    """Format date for display"""
    return date.strftime("%Y-%m-%d")

def display_entry(entry: JournalEntry, show_content: bool = True):
    """Display a journal entry"""
    print(f"\n📝 {entry.title}")
    print(f"   ID: {entry.id}")
    print(f"   Type: {entry.entry_type.value}")
    print(f"   Priority: {entry.priority.value}")
    print(f"   Status: {entry.status}")
    print(f"   Date: {format_timestamp(entry.timestamp)}")
    
    if entry.assignee:
        print(f"   Assignee: {entry.assignee}")
    
    if entry.tags:
        print(f"   Tags: {', '.join(entry.tags)}")
    
    if entry.estimated_hours:
        print(f"   Estimated: {entry.estimated_hours}h")
    
    if entry.actual_hours:
        print(f"   Actual: {entry.actual_hours}h")
    
    if show_content:
        print(f"   Content: {entry.content}")
    
    if entry.related_files:
        print(f"   Files: {', '.join(entry.related_files)}")

def display_milestone(milestone: DevelopmentMilestone):
    """Display a milestone"""
    print(f"\n🎯 {milestone.title}")
    print(f"   ID: {milestone.id}")
    print(f"   Status: {milestone.status}")
    print(f"   Target: {format_date(milestone.target_date)}")
    
    if milestone.completed_date:
        print(f"   Completed: {format_date(milestone.completed_date)}")
    
    print(f"   Description: {milestone.description}")
    print(f"   Entries: {len(milestone.entry_ids)}")

def add_entry_interactive(journal: DevelopmentJournal) -> JournalEntry:
    """Interactively add a new journal entry"""
    print_header("Add New Journal Entry")
    
    # Get entry type
    print("\nEntry types:")
    for i, entry_type in enumerate(JournalEntryType, 1):
        print(f"  {i}. {entry_type.value}")
    
    while True:
        try:
            choice = int(input("\nSelect entry type (1-10): ")) - 1
            if 0 <= choice < len(JournalEntryType):
                entry_type = list(JournalEntryType)[choice]
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")
    
    # Get title
    title = input("\nTitle: ").strip()
    if not title:
        print("Title is required!")
        return None
    
    # Get content
    print("\nContent (press Enter twice to finish):")
    content_lines = []
    while True:
        line = input()
        if line == "" and content_lines and content_lines[-1] == "":
            break
        content_lines.append(line)
    
    content = "\n".join(content_lines[:-1])  # Remove the last empty line
    
    # Get priority
    print("\nPriority levels:")
    for i, priority in enumerate(Priority, 1):
        print(f"  {i}. {priority.value}")
    
    while True:
        try:
            choice = int(input("Select priority (1-4): ")) - 1
            if 0 <= choice < len(Priority):
                priority = list(Priority)[choice]
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")
    
    # Get tags
    tags_input = input("\nTags (comma-separated, optional): ").strip()
    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
    
    # Get assignee
    assignee = input("\nAssignee (optional): ").strip() or None
    
    # Get estimated hours
    estimated_hours = None
    hours_input = input("\nEstimated hours (optional): ").strip()
    if hours_input:
        try:
            estimated_hours = float(hours_input)
        except ValueError:
            print("Invalid number format. Skipping estimated hours.")
    
    # Create entry
    entry = journal.add_entry(
        entry_type=entry_type,
        title=title,
        content=content,
        priority=priority,
        tags=tags,
        assignee=assignee,
        estimated_hours=estimated_hours
    )
    
    print(f"\n✅ Entry created: {entry.id}")
    return entry

def add_milestone_interactive(journal: DevelopmentJournal) -> DevelopmentMilestone:
    """Interactively add a new milestone"""
    print_header("Add New Milestone")
    
    # Get title
    title = input("\nTitle: ").strip()
    if not title:
        print("Title is required!")
        return None
    
    # Get description
    description = input("\nDescription: ").strip()
    if not description:
        print("Description is required!")
        return None
    
    # Get target date
    while True:
        date_input = input("\nTarget date (YYYY-MM-DD): ").strip()
        try:
            target_date = datetime.date.fromisoformat(date_input)
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
    
    # Create milestone
    milestone = journal.add_milestone(
        title=title,
        description=description,
        target_date=target_date
    )
    
    print(f"\n✅ Milestone created: {milestone.id}")
    return milestone

def search_entries_interactive(journal: DevelopmentJournal):
    """Interactively search entries"""
    print_header("Search Journal Entries")
    
    # Get search query
    query = input("\nSearch query (optional): ").strip() or None
    
    # Get entry type filter
    print("\nFilter by entry type (optional):")
    print("  0. All types")
    for i, entry_type in enumerate(JournalEntryType, 1):
        print(f"  {i}. {entry_type.value}")
    
    entry_type = None
    choice = input("Select type (0-10): ").strip()
    if choice != "0":
        try:
            choice_num = int(choice) - 1
            if 0 <= choice_num < len(JournalEntryType):
                entry_type = list(JournalEntryType)[choice_num]
        except ValueError:
            pass
    
    # Get status filter
    print("\nFilter by status (optional):")
    print("  0. All statuses")
    print("  1. open")
    print("  2. in_progress")
    print("  3. completed")
    print("  4. blocked")
    
    status = None
    choice = input("Select status (0-4): ").strip()
    status_map = {"1": "open", "2": "in_progress", "3": "completed", "4": "blocked"}
    if choice in status_map:
        status = status_map[choice]
    
    # Get priority filter
    print("\nFilter by priority (optional):")
    print("  0. All priorities")
    for i, priority in enumerate(Priority, 1):
        print(f"  {i}. {priority.value}")
    
    priority = None
    choice = input("Select priority (0-4): ").strip()
    if choice != "0":
        try:
            choice_num = int(choice) - 1
            if 0 <= choice_num < len(Priority):
                priority = list(Priority)[choice_num]
        except ValueError:
            pass
    
    # Perform search
    results = journal.search_entries(
        query=query,
        entry_type=entry_type,
        status=status,
        priority=priority
    )
    
    print(f"\nFound {len(results)} entries:")
    for entry in results:
        display_entry(entry, show_content=False)

def show_project_summary(journal: DevelopmentJournal):
    """Show project summary"""
    print_header("Project Summary")
    
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
    
    if summary['recent_entries']:
        print(f"\nRecent Activity:")
        for entry in summary['recent_entries']:
            print(f"  {format_timestamp(datetime.datetime.fromisoformat(entry['timestamp']))} - {entry['title']}")

def list_entries(journal: DevelopmentJournal, limit: int = 10):
    """List recent entries"""
    print_header(f"Recent Journal Entries (Last {limit})")
    
    entries = sorted(journal.entries.values(), key=lambda x: x.timestamp, reverse=True)[:limit]
    
    if not entries:
        print("No entries found.")
        return
    
    for entry in entries:
        display_entry(entry, show_content=False)

def list_milestones(journal: DevelopmentJournal):
    """List all milestones"""
    print_header("Development Milestones")
    
    milestones = journal.get_milestones()
    
    if not milestones:
        print("No milestones found.")
        return
    
    for milestone in milestones:
        display_milestone(milestone)

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="DnD Game Development Journal CLI")
    parser.add_argument("command", choices=[
        "add", "search", "list", "milestones", "summary", "backup", "export"
    ], help="Command to execute")
    parser.add_argument("--limit", type=int, default=10, help="Limit for list command")
    
    args = parser.parse_args()
    
    # Initialize journal
    journal = DevelopmentJournal()
    
    try:
        if args.command == "add":
            add_entry_interactive(journal)
        
        elif args.command == "search":
            search_entries_interactive(journal)
        
        elif args.command == "list":
            list_entries(journal, args.limit)
        
        elif args.command == "milestones":
            list_milestones(journal)
        
        elif args.command == "summary":
            show_project_summary(journal)
        
        elif args.command == "backup":
            backup_file = journal.backup_journal()
            print(f"✅ Journal backed up to: {backup_file}")
        
        elif args.command == "export":
            export_file = journal.export_journal()
            print(f"✅ Journal exported to: {export_file}")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 