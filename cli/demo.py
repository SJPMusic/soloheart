#!/usr/bin/env python3
"""
DnD 5E AI-Powered Campaign Manager - Demo
==========================================

This demo showcases the key features of the AI-powered campaign manager.
"""

import os
import sys
import datetime
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import DnDCampaignManager

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title: str):
    """Print a formatted section"""
    print(f"\n--- {title} ---")

def demo_character_creation():
    """Demonstrate character creation with vibe coding"""
    print_header("CHARACTER CREATION WITH VIBE CODING")
    
    campaign = DnDCampaignManager("Demo Campaign")
    
    # Create characters using vibe coding
    characters = [
        {
            "player_name": "Alice",
            "vibe": "A mysterious elven wizard who speaks in riddles and ancient proverbs",
            "preferences": {"custom_description": "Tall and graceful with silver hair and twinkling eyes"}
        },
        {
            "player_name": "Bob",
            "vibe": "A brave human fighter who protects the innocent and wields a mighty sword",
            "preferences": {"custom_description": "Tall and muscular with a scar on his cheek"}
        },
        {
            "player_name": "Charlie",
            "vibe": "A cunning halfling rogue who can sneak through shadows and pick any lock",
            "preferences": {"custom_description": "Small and quick with nimble fingers"}
        }
    ]
    
    for char_data in characters:
        print_section(f"Creating {char_data['player_name']}'s Character")
        print(f"Vibe: {char_data['vibe']}")
        
        character = campaign.create_character_from_vibe(
            player_name=char_data['player_name'],
            vibe_description=char_data['vibe'],
            preferences=char_data['preferences']
        )
        
        print(f"✅ Created: {character.name}")
        print(f"   Race: {character.race.value}")
        print(f"   Class: {character.character_class.value}")
        print(f"   Background: {character.background}")
        print(f"   Personality: {character.personality_traits[0]}")
        print(f"   HP: {character.hit_points}, AC: {character.armor_class}")
        
        # Show ability scores
        print("   Ability Scores:")
        for ability, score in character.ability_scores.items():
            modifier = (score - 10) // 2
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            print(f"     {ability.value.title()}: {score} ({modifier_str})")
    
    return campaign

def demo_session_logging(campaign: DnDCampaignManager):
    """Demonstrate session logging and AI memory"""
    print_header("SESSION LOGGING AND AI MEMORY")
    
    # Start a session
    print_section("Starting Session")
    session = campaign.start_session("demo_session_001")
    print(f"✅ Session started: {session.session_id}")
    print(f"   Participants: {', '.join(session.participants)}")
    
    # Log various activities
    print_section("Logging Session Activities")
    
    # Dialogue
    print("📝 Logging dialogue...")
    campaign.log_dialogue("Gandalf", "Welcome to Rivendell, young adventurers. I am Gandalf the Grey.")
    campaign.log_dialogue("Alice", "We seek your wisdom, Gandalf. We have encountered strange creatures in the forest.")
    campaign.log_dialogue("Gandalf", "The forest has grown dark of late. Ancient evil stirs in the depths of Mirkwood.")
    
    # Actions
    print("⚔️ Logging actions...")
    campaign.log_action("Bob", "draws his sword", "ready for battle")
    campaign.log_action("Charlie", "sneaks forward", "to scout the area")
    campaign.log_action("Alice", "casts Detect Magic", "on the ancient door")
    
    # Exploration
    print("🗺️ Logging exploration...")
    campaign.log_exploration(
        "Rivendell", 
        "Elven city with flowing waterfalls and ancient architecture", 
        ["ancient library", "healing springs", "Council Chamber"]
    )
    campaign.log_exploration(
        "Mirkwood Forest", 
        "Dark and foreboding forest with twisted trees", 
        ["strange tracks", "abandoned campsite", "magical barrier"]
    )
    
    # Combat
    print("⚔️ Logging combat...")
    campaign.log_combat(
        ["Alice", "Bob", "Charlie", "Orc Warriors"], 
        "Victory! The orcs were defeated, but one escaped into the forest."
    )
    
    # Decisions
    print("🤔 Logging decisions...")
    campaign.log_decision(
        "Alice", 
        "follow the escaped orc", 
        "This could lead us to their lair and reveal their plans."
    )
    campaign.log_decision(
        "Bob", 
        "return to Rivendell for reinforcements", 
        "We need more help before facing a larger force."
    )
    
    # End session
    print_section("Ending Session")
    summary = campaign.end_session()
    print(f"✅ Session ended")
    print(f"   Duration: {summary.duration_minutes} minutes")
    print(f"   Locations visited: {', '.join(summary.locations_visited)}")
    print(f"   NPCs encountered: {', '.join(summary.npcs_encountered)}")
    print(f"   Combat encounters: {len(summary.combat_encounters)}")
    print(f"   Decisions made: {len(summary.decisions_made)}")
    
    return campaign

def demo_ai_content_generation(campaign: DnDCampaignManager):
    """Demonstrate AI content generation"""
    print_header("AI CONTENT GENERATION")
    
    print_section("Generating NPCs")
    
    # Generate NPCs for different contexts
    contexts = [
        {
            "name": "Forest Guide",
            "context": {"location_type": "forest", "quest_type": "exploration", "player_levels": {"Alice": 3, "Bob": 3, "Charlie": 3}}
        },
        {
            "name": "City Merchant",
            "context": {"location_type": "city", "quest_type": "social", "player_levels": {"Alice": 3, "Bob": 3, "Charlie": 3}}
        },
        {
            "name": "Mysterious Wizard",
            "context": {"location_type": "tower", "quest_type": "magical", "player_levels": {"Alice": 3, "Bob": 3, "Charlie": 3}}
        }
    ]
    
    for npc_data in contexts:
        print(f"\n🎭 Generating {npc_data['name']}...")
        npc = campaign.generate_npc(npc_data['context'])
        print(f"✅ {npc.content}")
        print(f"   Confidence: {npc.confidence}")
        print(f"   Entities involved: {', '.join(npc.entities_involved)}")
    
    print_section("Generating Locations")
    
    # Generate locations
    location_contexts = [
        {"biome": "forest", "time_of_day": "night"},
        {"biome": "mountain", "time_of_day": "day"},
        {"biome": "swamp", "time_of_day": "dusk"}
    ]
    
    for i, context in enumerate(location_contexts, 1):
        print(f"\n🗺️ Generating Location {i}...")
        location = campaign.generate_location(context)
        print(f"✅ {location.content}")
        print(f"   Confidence: {location.confidence}")
    
    print_section("Generating Quests")
    
    # Generate quests
    quest_contexts = [
        {"player_level": 3, "location_name": "Rivendell", "active_quests": 1},
        {"player_level": 3, "location_name": "Mirkwood Forest", "active_quests": 2},
        {"player_level": 3, "location_name": "Mountain Pass", "active_quests": 0}
    ]
    
    for i, context in enumerate(quest_contexts, 1):
        print(f"\n📜 Generating Quest {i}...")
        quest = campaign.generate_quest(context)
        print(f"✅ {quest.content}")
        print(f"   Confidence: {quest.confidence}")
        print(f"   Continuity notes: {', '.join(quest.continuity_notes)}")

def demo_ai_memory_search(campaign: DnDCampaignManager):
    """Demonstrate AI memory search capabilities"""
    print_header("AI MEMORY SEARCH")
    
    print_section("Searching Campaign Memory")
    
    # Search for different types of information
    search_queries = [
        "Gandalf",
        "Rivendell",
        "combat",
        "magic",
        "forest",
        "orcs"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Searching for '{query}'...")
        results = campaign.search_campaign_memory(query)
        print(f"   Found {len(results)} results")
        
        for i, result in enumerate(results[:3], 1):  # Show first 3 results
            print(f"   {i}. {result['type']}: {result['content'][:100]}...")
    
    print_section("Campaign Summary")
    
    # Get overall campaign summary
    summary = campaign.get_campaign_summary()
    print(f"📊 Campaign Overview:")
    print(f"   Total sessions: {summary.get('total_sessions', 0)}")
    print(f"   Total entities: {summary.get('total_entities', 0)}")
    print(f"   Total locations: {summary.get('total_locations', 0)}")
    print(f"   Recent activity: {len(summary.get('recent_activity', []))} events")

def demo_character_suggestions(campaign: DnDCampaignManager):
    """Demonstrate AI-powered character suggestions"""
    print_header("AI-POWERED CHARACTER SUGGESTIONS")
    
    print_section("Context-Aware Suggestions")
    
    # Different situations for different characters
    situations = [
        ("Alice", "facing a locked magical door"),
        ("Bob", "encountering a group of bandits"),
        ("Charlie", "needing to gather information in a tavern"),
        ("Alice", "trying to understand ancient runes"),
        ("Bob", "protecting villagers from danger"),
        ("Charlie", "sneaking past guards")
    ]
    
    for player_name, situation in situations:
        print(f"\n💡 Suggestions for {player_name} - {situation}:")
        suggestions = campaign.get_character_suggestions(player_name, situation)
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   {i}. {suggestion}")
        else:
            print("   No specific suggestions available.")

def demo_campaign_management(campaign: DnDCampaignManager):
    """Demonstrate campaign management features"""
    print_header("CAMPAIGN MANAGEMENT")
    
    print_section("Adding Quests")
    
    # Add some quests
    quests = [
        {
            "title": "The Darkening of Mirkwood",
            "description": "Investigate the strange darkness spreading through Mirkwood Forest",
            "quest_giver": "Gandalf",
            "reward": "500 gold pieces and magical items",
            "difficulty": "medium"
        },
        {
            "title": "The Lost Library",
            "description": "Find the ancient library mentioned in the Council Chamber",
            "quest_giver": "Elrond",
            "reward": "Knowledge of ancient spells",
            "difficulty": "hard"
        }
    ]
    
    for quest in quests:
        print(f"\n📜 Adding quest: {quest['title']}")
        campaign.add_quest(quest)
        print(f"   ✅ Quest added successfully")
    
    print_section("Campaign Export")
    
    # Export campaign data
    print("💾 Exporting campaign data...")
    export_file = campaign.export_campaign_data("demo_campaign_export.json")
    print(f"   ✅ Campaign exported to: {export_file}")
    
    # Create backup
    print("💾 Creating backup...")
    backup_file = campaign.backup_campaign()
    print(f"   ✅ Backup created: {backup_file}")

def main():
    """Run the complete demo"""
    print("🎲 DnD 5E AI-Powered Campaign Manager - Demo")
    print("=" * 60)
    print("This demo showcases the key features of the AI-powered campaign manager.")
    print("It will create characters, run a session, generate content, and demonstrate")
    print("the AI memory system's capabilities.")
    
    try:
        # Run all demo sections
        campaign = demo_character_creation()
        campaign = demo_session_logging(campaign)
        demo_ai_content_generation(campaign)
        demo_ai_memory_search(campaign)
        demo_character_suggestions(campaign)
        demo_campaign_management(campaign)
        
        print_header("DEMO COMPLETE")
        print("✅ All demo sections completed successfully!")
        print("\n🎯 Key Features Demonstrated:")
        print("   • Character creation with 'vibe coding'")
        print("   • Session logging and AI memory")
        print("   • Dynamic content generation")
        print("   • AI-powered search and suggestions")
        print("   • Campaign management and export")
        
        print("\n🚀 Next Steps:")
        print("   • Run 'python main.py' to start your own campaign")
        print("   • Check the generated files in the 'campaigns/' directory")
        print("   • Explore the exported campaign data")
        print("   • Customize the system for your needs")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Please check that all dependencies are installed and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 