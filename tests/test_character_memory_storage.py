#!/usr/bin/env python3
"""
Test script to verify character creation memory storage functionality.
"""

import sys
import os
import json
from datetime import datetime

# Add the solo_heart directory to the path
sys.path.append('SoloHeart')
sys.path.append('.')

def test_character_memory_storage():
    """Test that character creation data is properly stored in memory."""
    
    print("🧪 Testing Character Memory Storage")
    print("=" * 50)
    
    # Sample character data (similar to what would be created via vibe code)
    test_character_data = {
        "name": "Test Character",
        "race": "Elf",
        "class": "Wizard",
        "level": 1,
        "background": "Sage",
        "personality": "A curious and studious elf wizard",
        "ability_scores": {
            "strength": 8,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 10
        },
        "hit_points": 8,
        "armor_class": 12,
        "saving_throws": ["INT", "WIS"],
        "skills": ["Arcana", "History", "Investigation", "Religion"],
        "feats": [],
        "weapons": ["Quarterstaff"],
        "gear": ["Scholar's Pack", "Spellbook"],
        "spells": ["Fire Bolt", "Mage Hand", "Prestidigitation"],
        "background_freeform": "A young elf wizard who left their homeland to seek ancient knowledge.",
        "created_date": datetime.now().isoformat()
    }
    
    try:
        # Import the NarrativeBridge
        from narrative_bridge import NarrativeBridge
        
        # Create a test campaign ID
        test_campaign_id = "test-character-memory"
        
        # Initialize the bridge
        print("📚 Initializing Narrative Bridge...")
        bridge = NarrativeBridge(test_campaign_id)
        
        # Test the store_character_creation method
        print("💾 Testing store_character_creation method...")
        success = bridge.store_character_creation(test_character_data, test_campaign_id)
        
        if success:
            print("✅ Character creation data stored successfully!")
            
            # Test retrieving the memory
            print("🔍 Testing memory retrieval...")
            memories = bridge.recall_related_memories(
                "Test Character",
                max_results=5,
                memory_type="character_creation"
            )
            
            if memories:
                print(f"✅ Found {len(memories)} character creation memories:")
                for i, memory in enumerate(memories, 1):
                    print(f"  {i}. Memory Type: {memory.get('metadata', {}).get('memory_type', 'Unknown')}")
                    print(f"     Character: {memory.get('metadata', {}).get('character_id', 'Unknown')}")
                    print(f"     Content Preview: {memory.get('content', '')[:100]}...")
                    print()
            else:
                print("⚠️  No character creation memories found")
            
            # Test journal entries
            print("📖 Testing journal entry creation...")
            journal_entries = bridge.get_journal_entries(
                character_id="Test Character",
                entry_type="character_creation"
            )
            
            if journal_entries:
                print(f"✅ Found {len(journal_entries)} journal entries:")
                for entry in journal_entries:
                    print(f"  - {entry.get('title', 'No title')}")
            else:
                print("⚠️  No journal entries found")
                
        else:
            print("❌ Failed to store character creation data")
            return False
            
        print("\n🎉 Character Memory Storage Test Completed Successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        return False

if __name__ == "__main__":
    success = test_character_memory_storage()
    sys.exit(0 if success else 1) 