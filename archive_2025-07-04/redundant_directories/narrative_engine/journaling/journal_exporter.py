"""
Journal Export Utilities

Provides functionality to export journal entries to various formats including
JSONL and Markdown for easy sharing and documentation.
"""

import json
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .player_journal import JournalEntry

logger = logging.getLogger(__name__)


class JournalExporter:
    """Handles export of journal entries to various formats."""
    
    @staticmethod
    def export_to_jsonl(
        entries: List[JournalEntry],
        output_path: str,
        include_metadata: bool = True
    ) -> bool:
        """
        Export journal entries to JSONL format.
        
        Args:
            entries: List of journal entries to export
            output_path: Path for the output file
            include_metadata: Whether to include full metadata
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for entry in entries:
                    if include_metadata:
                        data = entry.to_dict()
                    else:
                        # Minimal export with essential fields only
                        data = {
                            'entry_id': entry.entry_id,
                            'character_id': entry.character_id,
                            'campaign_id': entry.campaign_id,
                            'entry_type': entry.entry_type.value,
                            'title': entry.title,
                            'content': entry.content,
                            'timestamp': entry.timestamp.isoformat(),
                            'location': entry.location,
                            'scene': entry.scene,
                            'tags': entry.tags
                        }
                    
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
            
            logger.info(f"Exported {len(entries)} entries to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to JSONL: {e}")
            return False
    
    @staticmethod
    def export_to_markdown(
        entries: List[JournalEntry],
        output_path: str,
        include_metadata: bool = True,
        group_by: Optional[str] = None
    ) -> bool:
        """
        Export journal entries to Markdown format.
        
        Args:
            entries: List of journal entries to export
            output_path: Path for the output file
            include_metadata: Whether to include metadata sections
            group_by: Optional grouping ('character', 'session', 'location', 'date')
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("# Campaign Journal\n\n")
                f.write(f"*Exported on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                
                if not entries:
                    f.write("*No journal entries found.*\n")
                    return True
                
                # Group entries if requested
                if group_by:
                    grouped_entries = JournalExporter._group_entries(entries, group_by)
                    for group_key, group_entries in grouped_entries.items():
                        f.write(f"## {group_key}\n\n")
                        JournalExporter._write_entries_markdown(f, group_entries, include_metadata)
                        f.write("\n")
                else:
                    JournalExporter._write_entries_markdown(f, entries, include_metadata)
                
                # Write summary
                f.write("\n---\n\n")
                f.write("## Summary\n\n")
                f.write(f"- **Total Entries**: {len(entries)}\n")
                f.write(f"- **Date Range**: {entries[-1].timestamp.strftime('%Y-%m-%d')} to {entries[0].timestamp.strftime('%Y-%m-%d')}\n")
                
                # Entry type breakdown
                entry_types = {}
                for entry in entries:
                    entry_type = entry.entry_type.value
                    entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
                
                f.write("- **Entry Types**:\n")
                for entry_type, count in entry_types.items():
                    f.write(f"  - {entry_type}: {count}\n")
            
            logger.info(f"Exported {len(entries)} entries to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to Markdown: {e}")
            return False
    
    @staticmethod
    def _group_entries(
        entries: List[JournalEntry],
        group_by: str
    ) -> Dict[str, List[JournalEntry]]:
        """Group entries by the specified criteria."""
        grouped = {}
        
        for entry in entries:
            if group_by == 'character':
                key = f"Character: {entry.character_id}"
            elif group_by == 'session':
                key = f"Session: {entry.session_id or 'No Session'}"
            elif group_by == 'location':
                key = f"Location: {entry.location or 'Unknown'}"
            elif group_by == 'date':
                key = f"Date: {entry.timestamp.strftime('%Y-%m-%d')}"
            else:
                key = "Other"
            
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(entry)
        
        # Sort groups and entries within groups
        for group_entries in grouped.values():
            group_entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return dict(sorted(grouped.items()))
    
    @staticmethod
    def _write_entries_markdown(
        f,
        entries: List[JournalEntry],
        include_metadata: bool
    ):
        """Write entries in Markdown format to the file."""
        for entry in entries:
            # Entry header
            f.write(f"### {entry.title}\n\n")
            
            # Metadata line
            f.write(f"**{entry.entry_type.value.title()}** | ")
            f.write(f"Character: {entry.character_id} | ")
            f.write(f"Campaign: {entry.campaign_id} | ")
            f.write(f"{entry.timestamp.strftime('%Y-%m-%d %H:%M')}\n\n")
            
            # Location and scene
            if entry.location or entry.scene:
                f.write("*")
                if entry.location:
                    f.write(f"Location: {entry.location}")
                if entry.location and entry.scene:
                    f.write(" | ")
                if entry.scene:
                    f.write(f"Scene: {entry.scene}")
                f.write("*\n\n")
            
            # Content
            f.write(f"{entry.content}\n\n")
            
            # Tags
            if entry.tags:
                f.write("**Tags**: " + ", ".join(f"`{tag}`" for tag in entry.tags) + "\n\n")
            
            # Emotional context
            if entry.emotional_context:
                f.write("**Emotional Context**: " + ", ".join(entry.emotional_context) + "\n\n")
            
            # Full metadata section
            if include_metadata and entry.metadata:
                f.write("<details>\n<summary>Metadata</summary>\n\n")
                f.write("```json\n")
                f.write(json.dumps(entry.metadata, indent=2, ensure_ascii=False))
                f.write("\n```\n\n</details>\n\n")
            
            f.write("---\n\n")
    
    @staticmethod
    def export_character_summary(
        entries: List[JournalEntry],
        character_id: str,
        output_path: str
    ) -> bool:
        """
        Export a character-specific journal summary.
        
        Args:
            entries: List of journal entries
            character_id: ID of the character
            output_path: Path for the output file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            character_entries = [e for e in entries if e.character_id == character_id]
            
            if not character_entries:
                logger.warning(f"No entries found for character {character_id}")
                return False
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# Character Journal: {character_id}\n\n")
                
                # Character overview
                f.write("## Overview\n\n")
                f.write(f"- **Character ID**: {character_id}\n")
                f.write(f"- **Total Entries**: {len(character_entries)}\n")
                f.write(f"- **First Entry**: {character_entries[-1].timestamp.strftime('%Y-%m-%d')}\n")
                f.write(f"- **Latest Entry**: {character_entries[0].timestamp.strftime('%Y-%m-%d')}\n\n")
                
                # Campaign breakdown
                campaigns = {}
                for entry in character_entries:
                    camp_id = entry.campaign_id
                    campaigns[camp_id] = campaigns.get(camp_id, 0) + 1
                
                f.write("## Campaigns\n\n")
                for campaign_id, count in campaigns.items():
                    f.write(f"- **{campaign_id}**: {count} entries\n")
                f.write("\n")
                
                # Recent entries
                f.write("## Recent Entries\n\n")
                recent_entries = character_entries[:10]  # Last 10 entries
                JournalExporter._write_entries_markdown(f, recent_entries, False)
                
                # Entry type breakdown
                entry_types = {}
                for entry in character_entries:
                    entry_type = entry.entry_type.value
                    entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
                
                f.write("## Entry Types\n\n")
                for entry_type, count in entry_types.items():
                    f.write(f"- **{entry_type}**: {count}\n")
            
            logger.info(f"Exported character summary for {character_id} to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting character summary: {e}")
            return False
    
    @staticmethod
    def export_campaign_summary(
        entries: List[JournalEntry],
        campaign_id: str,
        output_path: str
    ) -> bool:
        """
        Export a campaign-specific journal summary.
        
        Args:
            entries: List of journal entries
            campaign_id: ID of the campaign
            output_path: Path for the output file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            campaign_entries = [e for e in entries if e.campaign_id == campaign_id]
            
            if not campaign_entries:
                logger.warning(f"No entries found for campaign {campaign_id}")
                return False
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# Campaign Journal: {campaign_id}\n\n")
                
                # Campaign overview
                f.write("## Overview\n\n")
                f.write(f"- **Campaign ID**: {campaign_id}\n")
                f.write(f"- **Total Entries**: {len(campaign_entries)}\n")
                f.write(f"- **First Entry**: {campaign_entries[-1].timestamp.strftime('%Y-%m-%d')}\n")
                f.write(f"- **Latest Entry**: {campaign_entries[0].timestamp.strftime('%Y-%m-%d')}\n\n")
                
                # Character breakdown
                characters = {}
                for entry in campaign_entries:
                    char_id = entry.character_id
                    characters[char_id] = characters.get(char_id, 0) + 1
                
                f.write("## Characters\n\n")
                for character_id, count in characters.items():
                    f.write(f"- **{character_id}**: {count} entries\n")
                f.write("\n")
                
                # Recent entries
                f.write("## Recent Entries\n\n")
                recent_entries = campaign_entries[:15]  # Last 15 entries
                JournalExporter._write_entries_markdown(f, recent_entries, False)
                
                # Entry type breakdown
                entry_types = {}
                for entry in campaign_entries:
                    entry_type = entry.entry_type.value
                    entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
                
                f.write("## Entry Types\n\n")
                for entry_type, count in entry_types.items():
                    f.write(f"- **{entry_type}**: {count}\n")
            
            logger.info(f"Exported campaign summary for {campaign_id} to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting campaign summary: {e}")
            return False 