#!/usr/bin/env python3
"""
Seed data generator for test campaign.

Creates a comprehensive test campaign with:
- 5-10 varied lore entries (locations, people, artifacts, events)
- Simulated emotion log data for 2 characters
- Character arcs and plot threads
- Journal entries and memories
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from narrative_bridge import NarrativeBridge
from narrative_engine.memory.emotional_memory import EmotionType
from narrative_engine.journaling.player_journal import JournalEntryType
from narrative_engine.narrative_structure.character_arcs import ArcType, ArcStatus
from narrative_engine.narrative_structure.plot_threads import ThreadType, ThreadStatus


class TestCampaignSeeder:
    """Generates comprehensive test data for a campaign."""
    
    def __init__(self, campaign_id="test-campaign", data_dir=None):
        self.campaign_id = campaign_id
        self.data_dir = data_dir
        self.bridge = NarrativeBridge(campaign_id, data_dir=data_dir)
        
        # Sample data templates
        self.lore_templates = {
            "locations": [
                {
                    "title": "The Whispering Woods",
                    "content": "A dense forest where the trees seem to whisper ancient secrets. The air is thick with magic, and strange lights dance between the branches at night.",
                    "lore_type": "location",
                    "importance": 4,
                    "tags": ["forest", "magical", "ancient", "whispering"],
                    "discovered": True
                },
                {
                    "title": "The Crystal Caverns",
                    "content": "Deep beneath the mountains lie vast caverns filled with glowing crystals. The crystals seem to pulse with their own inner light and emit a faint humming sound.",
                    "lore_type": "location",
                    "importance": 5,
                    "tags": ["cavern", "crystal", "underground", "glowing"],
                    "discovered": False
                },
                {
                    "title": "The Ruined Temple of Eldara",
                    "content": "An ancient temple dedicated to the goddess of wisdom. Though in ruins, the temple still radiates powerful magic and contains many hidden chambers.",
                    "lore_type": "location",
                    "importance": 5,
                    "tags": ["temple", "ruins", "ancient", "magical"],
                    "discovered": True
                }
            ],
            "characters": [
                {
                    "title": "Eldara the Wise",
                    "content": "An ancient elf who has lived for over a thousand years. She guards the secrets of the forest and serves as a mentor to those who seek wisdom.",
                    "lore_type": "character",
                    "importance": 5,
                    "tags": ["elf", "wise", "ancient", "mentor"],
                    "discovered": True
                },
                {
                    "title": "Grimtooth the Blacksmith",
                    "content": "A skilled dwarf blacksmith who crafts magical weapons. He lives in a small village and is known for his gruff personality but kind heart.",
                    "lore_type": "character",
                    "importance": 3,
                    "tags": ["dwarf", "blacksmith", "magical", "craftsman"],
                    "discovered": True
                },
                {
                    "title": "The Shadow Walker",
                    "content": "A mysterious figure who appears in times of great need. No one knows their true identity, but they always seem to know more than they should.",
                    "lore_type": "character",
                    "importance": 4,
                    "tags": ["mysterious", "shadow", "helper", "unknown"],
                    "discovered": False
                }
            ],
            "artifacts": [
                {
                    "title": "The Crystal of Truth",
                    "content": "A powerful artifact that reveals hidden truths and can dispel illusions. It glows with a pure white light and feels warm to the touch.",
                    "lore_type": "item",
                    "importance": 5,
                    "tags": ["crystal", "truth", "powerful", "magical"],
                    "discovered": False
                },
                {
                    "title": "The Whispering Blade",
                    "content": "A sword that whispers secrets to its wielder. The blade is made of an unknown metal that never dulls and seems to have a mind of its own.",
                    "lore_type": "item",
                    "importance": 4,
                    "tags": ["sword", "whispering", "magical", "sentient"],
                    "discovered": True
                },
                {
                    "title": "The Map of Hidden Paths",
                    "content": "An ancient map that shows secret paths and hidden locations. The map seems to change and update itself, revealing new routes as needed.",
                    "lore_type": "item",
                    "importance": 3,
                    "tags": ["map", "ancient", "magical", "changing"],
                    "discovered": True
                }
            ],
            "events": [
                {
                    "title": "The Great Awakening",
                    "content": "A magical event that occurred 100 years ago, awakening ancient powers and causing the forest to become sentient. Many believe this event changed the world forever.",
                    "lore_type": "event",
                    "importance": 5,
                    "tags": ["awakening", "magical", "ancient", "world-changing"],
                    "discovered": True
                },
                {
                    "title": "The Crystal Storm",
                    "content": "A rare meteorological phenomenon where crystals rain from the sky. The crystals contain magical energy and are highly sought after by mages.",
                    "lore_type": "event",
                    "importance": 4,
                    "tags": ["storm", "crystal", "magical", "rare"],
                    "discovered": False
                }
            ]
        }
        
        self.emotion_templates = [
            {
                "content": "You feel a sense of wonder as you discover the ancient temple.",
                "memory_type": "discovery",
                "metadata": {"location": "temple", "phenomenon": "ancient"},
                "tags": ["discovery", "temple", "wonder"],
                "primary_emotion": EmotionType.WONDER,
                "emotional_intensity": 0.8
            },
            {
                "content": "Fear grips your heart as you hear strange whispers in the forest.",
                "memory_type": "exploration",
                "metadata": {"location": "forest", "phenomenon": "whispers"},
                "tags": ["exploration", "forest", "fear"],
                "primary_emotion": EmotionType.FEAR,
                "emotional_intensity": 0.7
            },
            {
                "content": "Anger burns within you as you discover the desecration of the sacred site.",
                "memory_type": "conflict",
                "metadata": {"location": "sacred_site", "phenomenon": "desecration"},
                "tags": ["conflict", "sacred", "anger"],
                "primary_emotion": EmotionType.ANGER,
                "emotional_intensity": 0.9
            },
            {
                "content": "Joy fills your heart as you successfully craft your first magical item.",
                "memory_type": "achievement",
                "metadata": {"location": "workshop", "phenomenon": "crafting"},
                "tags": ["achievement", "crafting", "joy"],
                "primary_emotion": EmotionType.JOY,
                "emotional_intensity": 0.8
            },
            {
                "content": "Curiosity drives you to investigate the mysterious crystal formation.",
                "memory_type": "investigation",
                "metadata": {"location": "cavern", "phenomenon": "crystals"},
                "tags": ["investigation", "crystals", "curiosity"],
                "primary_emotion": EmotionType.CURIOSITY,
                "emotional_intensity": 0.6
            },
            {
                "content": "Sadness overwhelms you as you learn of the ancient civilization's fall.",
                "memory_type": "revelation",
                "metadata": {"location": "ruins", "phenomenon": "history"},
                "tags": ["revelation", "history", "sadness"],
                "primary_emotion": EmotionType.SADNESS,
                "emotional_intensity": 0.7
            }
        ]
        
        self.journal_templates = [
            {
                "title": "First Steps into the Unknown",
                "content": "Today I ventured into the Whispering Woods for the first time. The trees seem to speak to each other, and I can't shake the feeling that I'm being watched. I found an ancient stone marker with strange runes that I couldn't decipher.",
                "entry_type": JournalEntryType.PLAYER_WRITTEN,
                "tags": ["exploration", "forest", "ancient", "runes"]
            },
            {
                "title": "Meeting Eldara",
                "content": "I encountered Eldara the Wise today. She's even more ancient and mysterious than the stories suggested. She told me about the Great Awakening and how it changed everything. I feel like I'm only beginning to understand the true nature of this world.",
                "entry_type": JournalEntryType.PLAYER_WRITTEN,
                "tags": ["character", "eldara", "wisdom", "awakening"]
            },
            {
                "title": "The Crystal Caverns",
                "content": "I discovered the entrance to the Crystal Caverns today. The crystals glow with an inner light that seems to pulse with life. I can hear a faint humming sound that seems to resonate with my very soul. This place feels important somehow.",
                "entry_type": JournalEntryType.PLAYER_WRITTEN,
                "tags": ["discovery", "caverns", "crystals", "magical"]
            },
            {
                "title": "Crafting the Whispering Blade",
                "content": "Grimtooth helped me craft my first magical weapon today. The Whispering Blade is beautiful and deadly, and it seems to have a mind of its own. It whispers secrets to me when I hold it, though I can't always understand what it's trying to tell me.",
                "entry_type": JournalEntryType.PLAYER_WRITTEN,
                "tags": ["crafting", "weapon", "magical", "whispering"]
            }
        ]
    
    def seed_lore_entries(self):
        """Seed the campaign with lore entries."""
        print("Seeding lore entries...")
        
        lore_count = 0
        for category, templates in self.lore_templates.items():
            for template in templates:
                # Add some randomization
                if random.random() < 0.8:  # 80% chance to add each entry
                    lore_id = self.bridge.create_lore_entry(
                        title=template["title"],
                        content=template["content"],
                        lore_type=template["lore_type"],
                        importance=template["importance"],
                        tags=template["tags"],
                        discovered=template["discovered"]
                    )
                    lore_count += 1
                    print(f"  Created lore: {template['title']}")
        
        print(f"Created {lore_count} lore entries")
        return lore_count
    
    def seed_emotional_memories(self, character_ids=None):
        """Seed the campaign with emotional memories for multiple characters."""
        if character_ids is None:
            character_ids = ["player", "companion"]
        
        print("Seeding emotional memories...")
        
        memory_count = 0
        for character_id in character_ids:
            # Create 3-6 memories per character
            num_memories = random.randint(3, 6)
            
            for i in range(num_memories):
                template = random.choice(self.emotion_templates)
                
                # Modify content to be character-specific
                content = template["content"].replace("You", f"{character_id.title()}")
                
                # Add timestamp variation
                timestamp = datetime.now() - timedelta(
                    days=random.randint(1, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                memory_id = self.bridge.store_dnd_memory(
                    content=content,
                    memory_type=template["memory_type"],
                    metadata={
                        **template["metadata"],
                        "character_id": character_id,
                        "timestamp": timestamp.isoformat()
                    },
                    tags=template["tags"] + [character_id],
                    primary_emotion=template["primary_emotion"],
                    emotional_intensity=template["emotional_intensity"] + random.uniform(-0.2, 0.2)
                )
                memory_count += 1
                print(f"  Created memory for {character_id}: {content[:50]}...")
        
        print(f"Created {memory_count} emotional memories")
        return memory_count
    
    def seed_character_arcs(self):
        """Seed the campaign with character arcs."""
        print("Seeding character arcs...")
        
        arc_templates = [
            {
                "character_id": "player",
                "name": "The Hero's Journey",
                "arc_type": ArcType.GROWTH,
                "description": "Your journey from ordinary adventurer to legendary hero.",
                "tags": ["hero", "growth", "legendary"],
                "emotional_themes": ["determination", "courage", "wisdom"]
            },
            {
                "character_id": "player",
                "name": "The Burden of Knowledge",
                "arc_type": ArcType.TRAGEDY,
                "description": "Learning ancient secrets comes with a heavy price.",
                "tags": ["knowledge", "burden", "secrets"],
                "emotional_themes": ["sadness", "responsibility", "isolation"]
            },
            {
                "character_id": "companion",
                "name": "The Loyal Friend",
                "arc_type": ArcType.GROWTH,
                "description": "Proving loyalty through trials and tribulations.",
                "tags": ["loyalty", "friendship", "trials"],
                "emotional_themes": ["loyalty", "courage", "sacrifice"]
            }
        ]
        
        arc_count = 0
        for template in arc_templates:
            arc_id = self.bridge.create_character_arc(
                character_id=template["character_id"],
                name=template["name"],
                arc_type=template["arc_type"],
                description=template["description"],
                tags=template["tags"],
                emotional_themes=template["emotional_themes"]
            )
            arc_count += 1
            print(f"  Created arc: {template['name']} for {template['character_id']}")
        
        print(f"Created {arc_count} character arcs")
        return arc_count
    
    def seed_plot_threads(self):
        """Seed the campaign with plot threads."""
        print("Seeding plot threads...")
        
        thread_templates = [
            {
                "name": "The Mysterious Artifacts",
                "thread_type": ThreadType.MYSTERY,
                "description": "Ancient artifacts have appeared throughout the world, causing strange phenomena and attracting dangerous attention.",
                "priority": 8,
                "assigned_characters": ["player", "companion"],
                "tags": ["mystery", "artifacts", "ancient", "dangerous"]
            },
            {
                "name": "The Forest's Awakening",
                "thread_type": ThreadType.QUEST,
                "description": "The Whispering Woods are becoming more active, and the trees seem to be calling for help with an ancient threat.",
                "priority": 7,
                "assigned_characters": ["player"],
                "tags": ["quest", "forest", "awakening", "threat"]
            },
            {
                "name": "The Shadow Conspiracy",
                "thread_type": ThreadType.CONFLICT,
                "description": "A shadowy organization is working behind the scenes to control the ancient magic and artifacts.",
                "priority": 9,
                "assigned_characters": ["player", "companion"],
                "tags": ["conflict", "conspiracy", "shadow", "control"]
            }
        ]
        
        thread_count = 0
        for template in thread_templates:
            thread_id = self.bridge.create_plot_thread(
                name=template["name"],
                thread_type=template["thread_type"],
                description=template["description"],
                priority=template["priority"],
                assigned_characters=template["assigned_characters"],
                tags=template["tags"]
            )
            thread_count += 1
            print(f"  Created thread: {template['name']}")
        
        print(f"Created {thread_count} plot threads")
        return thread_count
    
    def seed_journal_entries(self):
        """Seed the campaign with journal entries."""
        print("Seeding journal entries...")
        
        entry_count = 0
        for template in self.journal_templates:
            entry_id = self.bridge.add_journal_entry(
                title=template["title"],
                content=template["content"],
                character_id="player",
                entry_type=template["entry_type"]
            )
            entry_count += 1
            print(f"  Created journal entry: {template['title']}")
        
        print(f"Created {entry_count} journal entries")
        return entry_count
    
    def seed_all_data(self):
        """Seed all types of data for the campaign."""
        print(f"Seeding test campaign: {self.campaign_id}")
        print("=" * 50)
        
        lore_count = self.seed_lore_entries()
        memory_count = self.seed_emotional_memories()
        arc_count = self.seed_character_arcs()
        thread_count = self.seed_plot_threads()
        journal_count = self.seed_journal_entries()
        
        print("=" * 50)
        print("Seeding complete!")
        print(f"Total created:")
        print(f"  - Lore entries: {lore_count}")
        print(f"  - Emotional memories: {memory_count}")
        print(f"  - Character arcs: {arc_count}")
        print(f"  - Plot threads: {thread_count}")
        print(f"  - Journal entries: {journal_count}")
        
        return {
            "lore_entries": lore_count,
            "memories": memory_count,
            "arcs": arc_count,
            "threads": thread_count,
            "journal_entries": journal_count
        }
    
    def get_campaign_summary(self):
        """Get a summary of the seeded campaign."""
        print("\nCampaign Summary:")
        print("=" * 30)
        
        # Get lore summary
        lore_data = self.bridge.get_lore_panel_data()
        print(f"Lore entries: {lore_data['summary']['total_entries']}")
        print(f"  - Discovered: {lore_data['summary']['discovered_entries']}")
        print(f"  - Undiscovered: {lore_data['summary']['undiscovered_entries']}")
        print(f"  - Average importance: {lore_data['summary']['average_importance']:.1f}")
        
        # Get diagnostic report
        report = self.bridge.get_diagnostic_report()
        print(f"Campaign health: {report['campaign_health_score']:.1%}")
        print(f"Narrative coherence: {report['narrative_coherence']:.1%}")
        print(f"Character engagement: {report['character_engagement']:.1%}")
        
        # Get character arcs
        arcs = self.bridge.get_character_arcs("player")
        print(f"Player arcs: {len(arcs)}")
        
        # Get plot threads
        threads = self.bridge.get_plot_threads()
        print(f"Active threads: {len(threads)}")
        
        return {
            "lore_summary": lore_data['summary'],
            "diagnostic_report": report,
            "character_arcs": len(arcs),
            "plot_threads": len(threads)
        }


def main():
    """Main function to run the seeder."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed test campaign data")
    parser.add_argument("--campaign-id", default="test-campaign", help="Campaign ID")
    parser.add_argument("--data-dir", help="Data directory")
    parser.add_argument("--summary-only", action="store_true", help="Only show summary")
    
    args = parser.parse_args()
    
    seeder = TestCampaignSeeder(args.campaign_id, args.data_dir)
    
    if args.summary_only:
        seeder.get_campaign_summary()
    else:
        seeder.seed_all_data()
        seeder.get_campaign_summary()


if __name__ == "__main__":
    main() 