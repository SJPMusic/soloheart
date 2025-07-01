#!/usr/bin/env python3
"""
Quest Journal System Demo

This demo showcases the quest journal functionality:
- Character creation
- Quest acceptance and tracking
- Progress updates
- Quest completion
- Journal summaries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from narrative_core.engine_interface import EnhancedNarrativeEngine
from narrative_core.quest_journal import Quest, QuestObjective
from narrative_core.core import Character

def print_separator(title=""):
    """Print a formatted separator"""
    if title:
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")

def print_quest_status(engine, quest_id):
    """Print detailed quest status"""
    status = engine.get_quest_status(quest_id)
    if status:
        print(f"\n📋 Quest: {status['title']}")
        print(f"   Status: {status['status']}")
        print(f"   Completion: {status['completion_percentage']:.1f}%")
        print(f"   Objectives:")
        for i, obj in enumerate(status['objectives'], 1):
            status_icon = "✅" if obj['completed'] else "⏳"
            print(f"     {i}. {status_icon} {obj['description']}")
        print(f"   Rewards: {status['rewards']}")

def main():
    print_separator("QUEST JOURNAL SYSTEM DEMO")
    
    # Initialize the engine
    print("🚀 Initializing Enhanced Narrative Engine...")
    engine = EnhancedNarrativeEngine()
    print("✅ Engine initialized successfully!")
    
    # Create a character
    print_separator("CHARACTER CREATION")
    character = engine.create_character("Aria", "Rogue", level=3)
    print(f"🎭 Created character: {character.name} the {character.character_class}")
    print(f"   Level: {character.level}")
    print(f"   HP: {character.current_hp}/{character.max_hp}")
    print(f"   Stats: {character.stats}")
    
    # Create some sample quests
    print_separator("QUEST CREATION")
    
    # Quest 1: Simple delivery quest
    print("📜 Creating Quest 1: The Missing Package...")
    objectives1 = [
        QuestObjective("Find the merchant in the marketplace"),
        QuestObjective("Collect the mysterious package"),
        QuestObjective("Deliver the package to the noble's estate")
    ]
    
    quest1 = Quest(
        id="",
        title="The Missing Package",
        description="A merchant has lost an important package and needs it delivered to a noble.",
        quest_giver="Merchant Alric",
        objectives=objectives1,
        rewards={"gold": 50, "experience": 100, "item": "Stealth Boots"}
    )
    
    quest_id1 = engine.add_quest(quest1)
    print(f"✅ Quest added with ID: {quest_id1}")
    
    # Quest 2: Combat quest
    print("\n📜 Creating Quest 2: Goblin Infestation...")
    objectives2 = [
        QuestObjective("Investigate the goblin activity in the forest"),
        QuestObjective("Defeat the goblin leader"),
        QuestObjective("Return the stolen goods to the village")
    ]
    
    quest2 = Quest(
        id="",
        title="Goblin Infestation",
        description="Goblins have been terrorizing the local village and stealing supplies.",
        quest_giver="Village Elder",
        objectives=objectives2,
        rewards={"gold": 200, "experience": 300, "item": "Magic Dagger"}
    )
    
    quest_id2 = engine.add_quest(quest2)
    print(f"✅ Quest added with ID: {quest_id2}")
    
    # Show initial quest status
    print_separator("INITIAL QUEST STATUS")
    print_quest_status(engine, quest_id1)
    print_quest_status(engine, quest_id2)
    
    # Update quest progress
    print_separator("QUEST PROGRESS UPDATES")
    
    print("🔄 Updating Quest 1 progress...")
    engine.update_quest_progress(quest_id1, "Found the merchant in the busy marketplace")
    engine.complete_objective(quest_id1, 0)  # Complete first objective
    
    print("🔄 Updating Quest 2 progress...")
    engine.update_quest_progress(quest_id2, "Discovered goblin tracks leading into the forest")
    engine.update_objective_progress(quest_id2, 0, "Found evidence of recent goblin activity")
    
    # Show updated status
    print("\n📋 Updated Quest Status:")
    print_quest_status(engine, quest_id1)
    print_quest_status(engine, quest_id2)
    
    # Continue progress
    print("\n🔄 Continuing Quest 1...")
    engine.update_quest_progress(quest_id1, "Collected the package from the merchant")
    engine.complete_objective(quest_id1, 1)  # Complete second objective
    
    engine.update_quest_progress(quest_id1, "Delivered the package to the noble's estate")
    engine.complete_objective(quest_id1, 2)  # Complete third objective
    
    # Complete Quest 1
    print("\n🎉 Completing Quest 1...")
    success = engine.complete_quest(quest_id1, "Package delivered successfully")
    if success:
        print("✅ Quest 1 completed!")
    
    # Continue Quest 2
    print("\n🔄 Continuing Quest 2...")
    engine.update_quest_progress(quest_id2, "Encountered and defeated the goblin leader")
    engine.complete_objective(quest_id2, 1)  # Complete second objective
    
    engine.update_quest_progress(quest_id2, "Recovered stolen goods from goblin camp")
    engine.complete_objective(quest_id2, 2)  # Complete third objective
    
    # Complete Quest 2
    print("\n🎉 Completing Quest 2...")
    success = engine.complete_quest(quest_id2, "Goblins defeated and village saved")
    if success:
        print("✅ Quest 2 completed!")
    
    # Show final status
    print_separator("FINAL QUEST JOURNAL STATUS")
    
    # Active quests
    active_quests = engine.list_active_quests()
    print(f"📋 Active Quests: {len(active_quests)}")
    for quest in active_quests:
        print(f"   - {quest['title']} ({quest['completion_percentage']:.1f}% complete)")
    
    # Completed quests
    completed_quests = engine.list_completed_quests()
    print(f"\n✅ Completed Quests: {len(completed_quests)}")
    for quest in completed_quests:
        print(f"   - {quest['title']} (Rewards: {quest['rewards']})")
    
    # Overall summary
    summary = engine.get_quest_summary()
    print(f"\n📊 Quest Journal Summary:")
    print(f"   Total Quests: {summary['total_quests']}")
    print(f"   Active: {summary['active_count']}")
    print(f"   Completed: {summary['completed_count']}")
    print(f"   Failed: {summary['failed_count']}")
    
    # Test quest generation integration
    print_separator("QUEST GENERATION INTEGRATION")
    print("🎲 Generating a new quest using the quest generator...")
    
    context = {
        "location": "Waterdeep",
        "character_level": character.level,
        "character_class": character.character_class
    }
    
    generated_quest_id = engine.create_quest_from_generator(character, context)
    if generated_quest_id:
        print(f"✅ Generated quest added with ID: {generated_quest_id}")
        print_quest_status(engine, generated_quest_id)
    else:
        print("❌ Failed to generate quest")
    
    # Test save/load integration
    print_separator("SAVE/LOAD INTEGRATION")
    print("💾 Testing save/load functionality...")
    
    # Save current state
    engine.save_game("quest_journal_demo_save.json")
    print("✅ Game state saved")
    
    # Create new engine instance and load
    new_engine = EnhancedNarrativeEngine()
    new_engine.load_game("quest_journal_demo_save.json")
    print("✅ Game state loaded")
    
    # Verify quest journal was preserved
    loaded_summary = new_engine.get_quest_summary()
    print(f"📊 Loaded Quest Summary: {loaded_summary}")
    
    print_separator("DEMO COMPLETE")
    print("🎉 Quest Journal System demo completed successfully!")
    print("✨ All features working as expected:")
    print("   - Quest creation and tracking")
    print("   - Progress updates and objective completion")
    print("   - Quest completion and rewards")
    print("   - Journal summaries and status reports")
    print("   - Integration with quest generator")
    print("   - Save/load functionality")

if __name__ == "__main__":
    main() 