#!/usr/bin/env python3
"""
AI Dungeon Master Engine Demo
=============================

This demo showcases the AI-powered Dungeon Master functionality for solo DnD gameplay.
It demonstrates campaign creation, encounter generation, player action processing,
and adaptive difficulty adjustment.
"""

import sys
import os
import time
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.memory_system import CampaignMemorySystem
from core.character_manager import CharacterManager
from narrative_core.ai_dm_engine import AIDungeonMaster, GameState, EncounterType, DifficultyLevel

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title: str):
    """Print a formatted section"""
    print(f"\n--- {title} ---")

def print_campaign_info(campaign_state):
    """Print campaign information"""
    print_section("Campaign Information")
    print(f"Campaign ID: {campaign_state.campaign_id}")
    print(f"Character: {campaign_state.player_character.name}")
    print(f"Current Location: {campaign_state.current_location}")
    print(f"Game State: {campaign_state.game_state.value}")
    print(f"Session: {campaign_state.session_number}")
    print(f"XP Gained: {campaign_state.xp_gained}")
    print(f"Gold Gained: {campaign_state.gold_gained}")
    print(f"Difficulty Adjustment: {campaign_state.difficulty_adjustment:.2f}")

def print_character_info(character):
    """Print character information"""
    print_section("Character Information")
    print(f"Name: {character.name}")
    print(f"Race: {character.race}")
    print(f"Class: {character.character_class}")
    print(f"Level: {character.level}")
    print(f"Background: {character.background}")
    print(f"Ability Scores: {character.ability_scores}")

def print_encounter_info(encounter):
    """Print encounter information"""
    print_section("Current Encounter")
    print(f"Title: {encounter.title}")
    print(f"Type: {encounter.encounter_type.value}")
    print(f"Difficulty: {encounter.difficulty.value}")
    print(f"Description: {encounter.description}")
    
    if encounter.enemies:
        print(f"Enemies: {len(encounter.enemies)}")
        for enemy in encounter.enemies:
            print(f"  - {enemy['name']} (CR: {enemy['cr']}, HP: {enemy['hp']}, AC: {enemy['ac']})")
    
    if encounter.npcs:
        print(f"NPCs: {len(encounter.npcs)}")
        for npc in encounter.npcs:
            print(f"  - {npc['name']} ({npc['type']}, {npc['personality']})")
    
    print(f"Environment: {encounter.environment}")
    print(f"Rewards: {encounter.rewards}")

def print_ai_response(response):
    """Print AI DM response"""
    print_section("AI Dungeon Master Response")
    print(f"Description: {response['description']}")
    print(f"Requires Roll: {response['requires_roll']}")
    if response.get('next_encounter'):
        print(f"Next Encounter Type: {response['next_encounter'].value}")
    print(f"Story Progress: {response.get('story_progress', 0):.1f}")
    print(f"Difficulty Adjustment: {response.get('difficulty_adjustment', 0):.1f}")

def demo_character_creation():
    """Demo character creation"""
    print_header("Character Creation Demo")
    
    character_manager = CharacterManager()
    
    # Create a character using vibe-based generation
    print("Creating a character with vibe: 'A wise and mysterious elf wizard who seeks ancient knowledge'")
    
    # Define player preferences
    player_preferences = {
        "combat_style": "magical",
        "personality": "scholarly",
        "magic_school": "divination",
        "background_preference": "sage",
        "equipment_preference": "light",
        "spell_focus": "utility"
    }
    
    character = character_manager.create_character_from_vibe(
        "A wise and mysterious elf wizard who seeks ancient knowledge",
        player_preferences
    )
    
    print_character_info(character)
    return character

def demo_campaign_start(character):
    """Demo campaign start"""
    print_header("Campaign Start Demo")
    
    # Initialize memory system and AI DM
    memory_system = CampaignMemorySystem()
    ai_dm = AIDungeonMaster(memory_system)
    
    # Start a new campaign
    print("Starting a new 'Heroic Journey' campaign...")
    campaign_state = ai_dm.start_new_campaign(character, "heroic_journey")
    
    print_campaign_info(campaign_state)
    
    # Show story beats
    print_section("Story Beats")
    for i, beat in enumerate(ai_dm.story_beats, 1):
        print(f"{i}. {beat.title}: {beat.description}")
    
    return ai_dm, campaign_state

def demo_encounter_generation(ai_dm):
    """Demo encounter generation"""
    print_header("Encounter Generation Demo")
    
    # Generate different types of encounters
    encounter_types = [EncounterType.EXPLORATION, EncounterType.SOCIAL, EncounterType.COMBAT]
    
    for encounter_type in encounter_types:
        print(f"\nGenerating {encounter_type.value} encounter...")
        encounter = ai_dm.generate_encounter(encounter_type)
        print_encounter_info(encounter)
        time.sleep(1)  # Brief pause for readability

def demo_player_actions(ai_dm):
    """Demo player action processing"""
    print_header("Player Action Processing Demo")
    
    # Sample player actions
    actions = [
        ("explore", "ancient ruins", {"skill_check": "investigation", "result": "success"}),
        ("talk", "merchant", {"skill_check": "persuasion", "result": "partial_success"}),
        ("attack", "goblin", {"weapon": "sword", "result": "success"}),
        ("cast", "fireball", {"spell_level": 3, "result": "success"}),
        ("search", "treasure chest", {"skill_check": "perception", "result": "failure"})
    ]
    
    for action, target, context in actions:
        print(f"\nPlayer Action: {action} {target}")
        print(f"Context: {context}")
        
        response = ai_dm.process_player_action(action, target, context)
        print_ai_response(response)
        
        # Show updated campaign state
        print_section("Updated Campaign State")
        summary = ai_dm.get_campaign_summary()
        print(f"Current Game State: {summary['current_game_state']}")
        print(f"Player Skills: {summary['player_skills']}")
        print(f"Difficulty Adjustment: {summary['difficulty_adjustment']:.2f}")
        
        time.sleep(1)  # Brief pause for readability

def demo_adaptive_difficulty(ai_dm):
    """Demo adaptive difficulty system"""
    print_header("Adaptive Difficulty Demo")
    
    # Simulate different player performance scenarios
    scenarios = [
        ("Player struggling", [
            ("attack", "orc", {"result": "failure"}),
            ("talk", "noble", {"result": "failure"}),
            ("explore", "cave", {"result": "failure"})
        ]),
        ("Player doing well", [
            ("attack", "dragon", {"result": "success"}),
            ("talk", "king", {"result": "success"}),
            ("explore", "temple", {"result": "success"})
        ]),
        ("Mixed performance", [
            ("attack", "troll", {"result": "success"}),
            ("talk", "merchant", {"result": "failure"}),
            ("explore", "forest", {"result": "partial_success"})
        ])
    ]
    
    for scenario_name, actions in scenarios:
        print(f"\nScenario: {scenario_name}")
        
        # Reset difficulty for demo
        ai_dm.campaign_state.difficulty_adjustment = 1.0
        
        for action, target, context in actions:
            print(f"  Action: {action} {target} ({context['result']})")
            response = ai_dm.process_player_action(action, target, context)
            print(f"  Difficulty Adjustment: {ai_dm.campaign_state.difficulty_adjustment:.2f}")
        
        # Generate encounter with adjusted difficulty
        encounter = ai_dm.generate_encounter()
        print(f"  Generated {encounter.difficulty.value} difficulty encounter: {encounter.title}")

def demo_campaign_persistence(ai_dm):
    """Demo campaign save/load functionality"""
    print_header("Campaign Persistence Demo")
    
    # Save campaign
    print("Saving campaign...")
    save_filename = ai_dm.save_campaign()
    print(f"Campaign saved to: {save_filename}")
    
    # Create new AI DM instance
    memory_system = CampaignMemorySystem()
    new_ai_dm = AIDungeonMaster(memory_system)
    
    # Load campaign
    print("Loading campaign in new AI DM instance...")
    loaded_campaign = new_ai_dm.load_campaign(save_filename)
    
    print_section("Loaded Campaign Information")
    print_campaign_info(loaded_campaign)
    
    # Verify data integrity
    print_section("Data Integrity Check")
    original_summary = ai_dm.get_campaign_summary()
    loaded_summary = new_ai_dm.get_campaign_summary()
    
    print(f"Original Campaign ID: {original_summary['campaign_id']}")
    print(f"Loaded Campaign ID: {loaded_summary['campaign_id']}")
    print(f"Character Names Match: {original_summary['character_name'] == loaded_summary['character_name']}")
    print(f"XP Gained Match: {original_summary['xp_gained'] == loaded_summary['xp_gained']}")

def demo_memory_integration(ai_dm):
    """Demo memory system integration"""
    print_header("Memory System Integration Demo")
    
    # Show campaign memories
    print_section("Campaign Memories")
    memories = ai_dm.memory.get_campaign_memories(ai_dm.campaign_state.campaign_id)
    
    for memory in memories:
        print(f"Type: {memory['memory_type']}")
        print(f"Content: {memory['content']}")
        print(f"Timestamp: {memory['timestamp']}")
        print()
    
    # Search memories
    print_section("Memory Search")
    search_results = ai_dm.memory.search_campaign_memories(
        ai_dm.campaign_state.campaign_id,
        "attack"
    )
    
    print(f"Found {len(search_results)} memories containing 'attack'")
    for result in search_results:
        print(f"  - {result['memory_type']}: {result['content'].get('action', 'N/A')}")

def main():
    """Main demo function"""
    print_header("AI Dungeon Master Engine Demo")
    print("This demo showcases the AI-powered solo DnD game system.")
    print("Press Enter to continue through each section...")
    
    try:
        # Character creation demo
        input("\nPress Enter to start character creation demo...")
        character = demo_character_creation()
        
        # Campaign start demo
        input("\nPress Enter to start campaign demo...")
        ai_dm, campaign_state = demo_campaign_start(character)
        
        # Encounter generation demo
        input("\nPress Enter to start encounter generation demo...")
        demo_encounter_generation(ai_dm)
        
        # Player action processing demo
        input("\nPress Enter to start player action processing demo...")
        demo_player_actions(ai_dm)
        
        # Adaptive difficulty demo
        input("\nPress Enter to start adaptive difficulty demo...")
        demo_adaptive_difficulty(ai_dm)
        
        # Campaign persistence demo
        input("\nPress Enter to start campaign persistence demo...")
        demo_campaign_persistence(ai_dm)
        
        # Memory integration demo
        input("\nPress Enter to start memory integration demo...")
        demo_memory_integration(ai_dm)
        
        print_header("Demo Complete")
        print("The AI Dungeon Master Engine demo has completed successfully!")
        print("\nKey Features Demonstrated:")
        print("- Character creation with vibe-based generation")
        print("- Campaign management with story beats")
        print("- Dynamic encounter generation")
        print("- Player action processing with AI responses")
        print("- Adaptive difficulty adjustment")
        print("- Campaign persistence (save/load)")
        print("- Memory system integration")
        
        print("\nNext Steps:")
        print("1. Integrate with AI content generation for richer descriptions")
        print("2. Implement 5E rules engine for combat and skill checks")
        print("3. Create cross-platform user interface")
        print("4. Add voice interaction capabilities")
        print("5. Implement cloud-based campaign storage")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 