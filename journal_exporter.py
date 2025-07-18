#!/usr/bin/env python3
"""
Simple Journal Exporter

Exports campaign journal entries including memory events from TNE integration.
Supports JSON and Markdown export formats.
"""

import json
import os
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

def load_campaign_entries(campaign_id: str) -> List[Dict[str, Any]]:
    """
    Load all journal entries for a campaign including memory events.
    
    Args:
        campaign_id: Campaign ID to load entries for
        
    Returns:
        List of journal entries
    """
    entries = []
    
    # Load from campaign_saves directory
    campaign_dir = f"campaign_saves/{campaign_id}"
    entries_file = f"{campaign_dir}/entries.json"
    
    if os.path.exists(entries_file):
        try:
            with open(entries_file, 'r') as f:
                entries = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Warning: Could not load entries from {entries_file}")
    
    return entries

def export_to_json(entries: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Export journal entries to JSON format.
    
    Args:
        entries: List of journal entries
        output_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(entries, f, indent=2)
        
        print(f"Exported {len(entries)} entries to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False

def export_to_markdown(entries: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Export journal entries to Markdown format.
    
    Args:
        entries: List of journal entries
        output_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# Campaign Journal\n\n")
            f.write(f"*Exported on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            if not entries:
                f.write("*No journal entries found.*\n")
                return True
            
            # Group entries by type
            grouped_entries = {}
            for entry in entries:
                entry_type = entry.get('type', 'unknown')
                if entry_type not in grouped_entries:
                    grouped_entries[entry_type] = []
                grouped_entries[entry_type].append(entry)
            
            # Write entries by type
            for entry_type, type_entries in grouped_entries.items():
                f.write(f"## {entry_type.title()} Entries\n\n")
                
                for entry in type_entries:
                    # Entry header
                    title = entry.get('content', 'No Title')[:50] + "..." if len(entry.get('content', '')) > 50 else entry.get('content', 'No Title')
                    f.write(f"### {title}\n\n")
                    
                    # Metadata
                    f.write(f"**Type**: {entry.get('type', 'unknown')} | ")
                    f.write(f"**Character**: {entry.get('character_id', 'unknown')} | ")
                    f.write(f"**Timestamp**: {entry.get('timestamp', 'unknown')}\n\n")
                    
                    # Layer and tags for memory entries
                    if entry.get('type') == 'memory':
                        f.write(f"**Layer**: {entry.get('layer', 'unknown')} | ")
                        f.write(f"**Importance**: {entry.get('importance', 0.0):.2f}\n\n")
                        
                        if entry.get('tags'):
                            f.write(f"**Tags**: {', '.join(entry['tags'])}\n\n")
                    
                    # Content
                    content = entry.get('content', 'No content')
                    f.write(f"{content}\n\n")
                    
                    # Metadata for memory entries
                    if entry.get('type') == 'memory' and entry.get('metadata'):
                        f.write("**Metadata**:\n")
                        for key, value in entry['metadata'].items():
                            f.write(f"- {key}: {value}\n")
                        f.write("\n")
                    
                    f.write("---\n\n")
            
            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- **Total Entries**: {len(entries)}\n")
            
            # Entry type breakdown
            entry_types = {}
            for entry in entries:
                entry_type = entry.get('type', 'unknown')
                entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
            
            f.write("- **Entry Types**:\n")
            for entry_type, count in entry_types.items():
                f.write(f"  - {entry_type}: {count}\n")
            
            # Memory layer breakdown
            memory_entries = [e for e in entries if e.get('type') == 'memory']
            if memory_entries:
                f.write("- **Memory Layers**:\n")
                layers = {}
                for entry in memory_entries:
                    layer = entry.get('layer', 'unknown')
                    layers[layer] = layers.get(layer, 0) + 1
                
                for layer, count in layers.items():
                    f.write(f"  - {layer}: {count}\n")
        
        print(f"Exported {len(entries)} entries to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error exporting to Markdown: {e}")
        return False

def export_campaign_journal(campaign_id: str, output_format: str = 'both') -> bool:
    """
    Export a campaign's journal entries.
    
    Args:
        campaign_id: Campaign ID to export
        output_format: 'json', 'markdown', or 'both'
        
    Returns:
        True if successful, False otherwise
    """
    # Load entries
    entries = load_campaign_entries(campaign_id)
    
    if not entries:
        print(f"No entries found for campaign {campaign_id}")
        return False
    
    # Create output directory
    output_dir = f"exports/{campaign_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    success = True
    
    # Export based on format
    if output_format in ['json', 'both']:
        json_path = f"{output_dir}/journal_export.json"
        success &= export_to_json(entries, json_path)
    
    if output_format in ['markdown', 'both']:
        md_path = f"{output_dir}/journal_export.md"
        success &= export_to_markdown(entries, md_path)
    
    return success

def main():
    """Main function for command-line usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python journal_exporter.py <campaign_id> [format]")
        print("Formats: json, markdown, both (default: both)")
        return
    
    campaign_id = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'both'
    
    if output_format not in ['json', 'markdown', 'both']:
        print("Invalid format. Use: json, markdown, or both")
        return
    
    success = export_campaign_journal(campaign_id, output_format)
    
    if success:
        print(f"Successfully exported journal for campaign {campaign_id}")
    else:
        print(f"Failed to export journal for campaign {campaign_id}")

if __name__ == "__main__":
    main() 