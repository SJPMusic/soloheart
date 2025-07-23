#!/usr/bin/env python3
"""
Lore & Worldbuilding Management System
Tracks world lore, discoveries, factions, locations, and cosmology
with narrative metadata and linking to memory, arcs, and conflicts.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class LoreType(Enum):
    """Types of lore entries"""
    LOCATION = "location"
    FACTION = "faction"
    CHARACTER = "character"
    ITEM = "item"
    EVENT = "event"
    DISCOVERY = "discovery"
    HISTORY = "history"
    COSMOLOGY = "cosmology"
    CULTURE = "culture"
    MAGIC = "magic"
    CREATURE = "creature"
    PLOT = "plot"

class LoreEntry:
    """Represents a single lore entry with metadata and links"""
    
    def __init__(self, 
                 campaign_id: str,
                 title: str,
                 lore_type: LoreType,
                 content: str,
                 tags: List[str] = None,
                 linked_items: Dict[str, List[str]] = None,
                 discovered_by: str = None,
                 discovery_context: str = None,
                 importance_level: int = 1,
                 is_secret: bool = False,
                 created_at: datetime = None,
                 updated_at: datetime = None,
                 lore_id: str = None):
        
        self.lore_id = lore_id or str(uuid.uuid4())
        self.campaign_id = campaign_id
        self.title = title
        self.lore_type = lore_type
        self.content = content
        self.tags = tags or []
        self.linked_items = linked_items or {
            "characters": [],
            "locations": [],
            "memory_entries": [],
            "arcs": [],
            "conflicts": [],
            "plot_threads": []
        }
        self.discovered_by = discovered_by
        self.discovery_context = discovery_context
        self.importance_level = importance_level  # 1-5 scale
        self.is_secret = is_secret
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "lore_id": self.lore_id,
            "campaign_id": self.campaign_id,
            "title": self.title,
            "lore_type": self.lore_type.value,
            "content": self.content,
            "tags": self.tags,
            "linked_items": self.linked_items,
            "discovered_by": self.discovered_by,
            "discovery_context": self.discovery_context,
            "importance_level": self.importance_level,
            "is_secret": self.is_secret,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LoreEntry':
        """Create from dictionary"""
        return cls(
            lore_id=data.get("lore_id"),
            campaign_id=data["campaign_id"],
            title=data["title"],
            lore_type=LoreType(data["lore_type"]),
            content=data["content"],
            tags=data.get("tags", []),
            linked_items=data.get("linked_items", {}),
            discovered_by=data.get("discovered_by"),
            discovery_context=data.get("discovery_context"),
            importance_level=data.get("importance_level", 1),
            is_secret=data.get("is_secret", False),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def add_link(self, link_type: str, item_id: str):
        """Add a link to another item"""
        if link_type not in self.linked_items:
            self.linked_items[link_type] = []
        if item_id not in self.linked_items[link_type]:
            self.linked_items[link_type].append(item_id)
        self.updated_at = datetime.now()
    
    def remove_link(self, link_type: str, item_id: str):
        """Remove a link to another item"""
        if link_type in self.linked_items and item_id in self.linked_items[link_type]:
            self.linked_items[link_type].remove(item_id)
        self.updated_at = datetime.now()
    
    def add_tag(self, tag: str):
        """Add a tag to the lore entry"""
        if tag not in self.tags:
            self.tags.append(tag)
        self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str):
        """Remove a tag from the lore entry"""
        if tag in self.tags:
            self.tags.remove(tag)
        self.updated_at = datetime.now()

class LoreManager:
    """Manages lore entries for campaigns"""
    
    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        self.lore_file = f"lore_{campaign_id}.jsonl"
        self.entries: Dict[str, LoreEntry] = {}
        self.load_lore()
    
    def load_lore(self):
        """Load lore entries from file"""
        try:
            with open(self.lore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        entry = LoreEntry.from_dict(data)
                        self.entries[entry.lore_id] = entry
            logger.info(f"Loaded {len(self.entries)} lore entries for campaign {self.campaign_id}")
        except FileNotFoundError:
            logger.info(f"No existing lore file found for campaign {self.campaign_id}")
        except Exception as e:
            logger.error(f"Error loading lore: {e}")
    
    def save_lore(self):
        """Save lore entries to file"""
        try:
            with open(self.lore_file, 'w', encoding='utf-8') as f:
                for entry in self.entries.values():
                    f.write(json.dumps(entry.to_dict()) + '\n')
            logger.info(f"Saved {len(self.entries)} lore entries for campaign {self.campaign_id}")
        except Exception as e:
            logger.error(f"Error saving lore: {e}")
    
    def add_lore_entry(self, 
                      title: str,
                      lore_type: LoreType,
                      content: str,
                      tags: List[str] = None,
                      linked_items: Dict[str, List[str]] = None,
                      discovered_by: str = None,
                      discovery_context: str = None,
                      importance_level: int = 1,
                      is_secret: bool = False) -> LoreEntry:
        """Add a new lore entry"""
        
        entry = LoreEntry(
            campaign_id=self.campaign_id,
            title=title,
            lore_type=lore_type,
            content=content,
            tags=tags or [],
            linked_items=linked_items or {},
            discovered_by=discovered_by,
            discovery_context=discovery_context,
            importance_level=importance_level,
            is_secret=is_secret
        )
        
        self.entries[entry.lore_id] = entry
        self.save_lore()
        
        logger.info(f"Added lore entry: {title} ({lore_type.value})")
        return entry
    
    def get_lore_entries(self, 
                        lore_type: Optional[LoreType] = None,
                        include_secrets: bool = False,
                        min_importance: int = 1) -> List[LoreEntry]:
        """Get all lore entries with optional filtering"""
        
        entries = list(self.entries.values())
        
        # Filter by type
        if lore_type:
            entries = [e for e in entries if e.lore_type == lore_type]
        
        # Filter secrets
        if not include_secrets:
            entries = [e for e in entries if not e.is_secret]
        
        # Filter by importance
        entries = [e for e in entries if e.importance_level >= min_importance]
        
        # Sort by importance (descending) then by creation date (newest first)
        entries.sort(key=lambda x: (-x.importance_level, -x.created_at.timestamp()))
        
        return entries
    
    def search_lore(self, 
                   query: str,
                   search_fields: List[str] = None,
                   lore_types: List[LoreType] = None,
                   tags: List[str] = None) -> List[LoreEntry]:
        """Search lore entries by text, tags, or type"""
        
        if search_fields is None:
            search_fields = ["title", "content", "tags"]
        
        query_lower = query.lower()
        results = []
        
        for entry in self.entries.values():
            # Filter by type
            if lore_types and entry.lore_type not in lore_types:
                continue
            
            # Filter by tags
            if tags and not any(tag in entry.tags for tag in tags):
                continue
            
            # Search in specified fields
            matches = False
            for field in search_fields:
                if field == "title" and query_lower in entry.title.lower():
                    matches = True
                    break
                elif field == "content" and query_lower in entry.content.lower():
                    matches = True
                    break
                elif field == "tags" and any(query_lower in tag.lower() for tag in entry.tags):
                    matches = True
                    break
            
            if matches:
                results.append(entry)
        
        # Sort by relevance (importance + recency)
        results.sort(key=lambda x: (-x.importance_level, -x.created_at.timestamp()))
        
        return results
    
    def get_lore_entry_by_id(self, lore_id: str) -> Optional[LoreEntry]:
        """Get a specific lore entry by ID"""
        return self.entries.get(lore_id)
    
    def update_lore_entry(self, 
                         lore_id: str,
                         title: str = None,
                         content: str = None,
                         tags: List[str] = None,
                         importance_level: int = None,
                         is_secret: bool = None) -> Optional[LoreEntry]:
        """Update an existing lore entry"""
        
        entry = self.entries.get(lore_id)
        if not entry:
            return None
        
        if title is not None:
            entry.title = title
        if content is not None:
            entry.content = content
        if tags is not None:
            entry.tags = tags
        if importance_level is not None:
            entry.importance_level = importance_level
        if is_secret is not None:
            entry.is_secret = is_secret
        
        entry.updated_at = datetime.now()
        self.save_lore()
        
        logger.info(f"Updated lore entry: {entry.title}")
        return entry
    
    def delete_lore_entry(self, lore_id: str) -> bool:
        """Delete a lore entry"""
        if lore_id in self.entries:
            title = self.entries[lore_id].title
            del self.entries[lore_id]
            self.save_lore()
            logger.info(f"Deleted lore entry: {title}")
            return True
        return False
    
    def get_lore_by_type(self, lore_type: LoreType) -> List[LoreEntry]:
        """Get all lore entries of a specific type"""
        return [entry for entry in self.entries.values() if entry.lore_type == lore_type]
    
    def get_lore_by_tag(self, tag: str) -> List[LoreEntry]:
        """Get all lore entries with a specific tag"""
        return [entry for entry in self.entries.values() if tag in entry.tags]
    
    def get_linked_lore(self, item_type: str, item_id: str) -> List[LoreEntry]:
        """Get all lore entries linked to a specific item"""
        linked_entries = []
        for entry in self.entries.values():
            if (item_type in entry.linked_items and 
                item_id in entry.linked_items[item_type]):
                linked_entries.append(entry)
        return linked_entries
    
    def get_lore_summary(self) -> Dict:
        """Get a summary of all lore entries"""
        total_entries = len(self.entries)
        type_counts = {}
        tag_counts = {}
        importance_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for entry in self.entries.values():
            # Count by type
            type_counts[entry.lore_type.value] = type_counts.get(entry.lore_type.value, 0) + 1
            
            # Count by importance
            importance_counts[entry.importance_level] += 1
            
            # Count by tags
            for tag in entry.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            "total_entries": total_entries,
            "type_distribution": type_counts,
            "tag_distribution": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "importance_distribution": importance_counts,
            "recent_entries": len([e for e in self.entries.values() 
                                 if (datetime.now() - e.created_at).days <= 7])
        }
    
    def auto_generate_from_memory(self, memory_entry: Dict) -> Optional[LoreEntry]:
        """Auto-generate lore entry from memory entry"""
        
        content = memory_entry.get("content", "")
        character = memory_entry.get("character", "Unknown")
        
        # Check for discovery keywords
        discovery_keywords = [
            "discovered", "found", "uncovered", "revealed", "learned about",
            "encountered", "met", "explored", "investigated", "studied"
        ]
        
        if any(keyword in content.lower() for keyword in discovery_keywords):
            # Determine lore type based on content
            lore_type = self._determine_lore_type(content)
            
            # Extract title from content
            title = self._extract_title(content, lore_type)
            
            # Generate tags
            tags = self._extract_tags(content, lore_type)
            
            # Determine importance
            importance = self._determine_importance(content, memory_entry)
            
            return self.add_lore_entry(
                title=title,
                lore_type=lore_type,
                content=content,
                tags=tags,
                discovered_by=character,
                discovery_context=f"Memory entry: {memory_entry.get('id', 'unknown')}",
                importance_level=importance
            )
        
        return None
    
    def _determine_lore_type(self, content: str) -> LoreType:
        """Determine lore type based on content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["ruin", "temple", "castle", "city", "village", "forest", "mountain"]):
            return LoreType.LOCATION
        elif any(word in content_lower for word in ["guild", "order", "faction", "clan", "tribe", "kingdom"]):
            return LoreType.FACTION
        elif any(word in content_lower for word in ["sword", "staff", "ring", "artifact", "weapon", "armor"]):
            return LoreType.ITEM
        elif any(word in content_lower for word in ["dragon", "beast", "monster", "creature"]):
            return LoreType.CREATURE
        elif any(word in content_lower for word in ["spell", "magic", "enchantment", "ritual"]):
            return LoreType.MAGIC
        elif any(word in content_lower for word in ["ancient", "history", "legend", "myth"]):
            return LoreType.HISTORY
        elif any(word in content_lower for word in ["god", "deity", "plane", "realm", "cosmos"]):
            return LoreType.COSMOLOGY
        else:
            return LoreType.DISCOVERY
    
    def _extract_title(self, content: str, lore_type: LoreType) -> str:
        """Extract a title from content"""
        # Simple extraction - take first sentence or phrase
        sentences = content.split('.')
        if sentences:
            title = sentences[0].strip()
            if len(title) > 60:
                title = title[:57] + "..."
            return title
        return f"Unknown {lore_type.value.title()}"
    
    def _extract_tags(self, content: str, lore_type: LoreType) -> List[str]:
        """Extract tags from content"""
        tags = [lore_type.value]
        
        # Add common tags based on content
        content_lower = content.lower()
        
        if "ancient" in content_lower:
            tags.append("ancient")
        if "magical" in content_lower or "magic" in content_lower:
            tags.append("magical")
        if "dangerous" in content_lower or "threat" in content_lower:
            tags.append("dangerous")
        if "valuable" in content_lower or "treasure" in content_lower:
            tags.append("valuable")
        if "secret" in content_lower or "hidden" in content_lower:
            tags.append("secret")
        
        return tags
    
    def _determine_importance(self, content: str, memory_entry: Dict) -> int:
        """Determine importance level based on content and memory"""
        importance = 1
        
        # Check for importance indicators in content
        content_lower = content.lower()
        if any(word in content_lower for word in ["legendary", "mythical", "ancient", "powerful"]):
            importance += 1
        if any(word in content_lower for word in ["dangerous", "threat", "enemy"]):
            importance += 1
        if any(word in content_lower for word in ["treasure", "valuable", "precious"]):
            importance += 1
        
        # Check memory emotion intensity
        emotion_intensity = memory_entry.get("emotion_intensity", 0)
        if emotion_intensity > 0.7:
            importance += 1
        
        return min(importance, 5)  # Cap at 5 