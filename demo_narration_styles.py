#!/usr/bin/env python3
"""
Demo: DM Narration Styles Feature
Showcases the comprehensive narration style system for AI-powered DnD campaigns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from narrative_core.engine_interface import EnhancedNarrativeEngine
from narrative_core.core import Character
from narrative_core.campaign_manager import CampaignManager
import json

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🎭 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📖 {title}")
    print("-" * 40)

def demo_narration_styles():
    """Demonstrate the narration style system"""
    print_header("DM NARRATION STYLES DEMO")
    
    # Initialize the engine
    print("🚀 Initializing Enhanced Narrative Engine...")
    engine = EnhancedNarrativeEngine()
    
    # Create a sample character
    character = Character(
        name="Thorin Ironfist",
        character_class="Fighter",
        level=5,
        stats={"STR": 16, "DEX": 14, "CON": 16, "INT": 10, "WIS": 12, "CHA": 8}
    )
    
    print(f"✅ Created character: {character.name} the {character.character_class}")
    
    # Demo 1: Show all available styles
    print_section("AVAILABLE NARRATION STYLES")
    
    all_styles = engine.dm_style.get_all_styles()
    for i, (style_key, style_info) in enumerate(all_styles.items(), 1):
        print(f"\n{i}. {style_info['name']}")
        print(f"   Description: {style_info['description']}")
        print(f"   Tone: {style_info['tone']}")
        print(f"   Example phrase: {engine.dm_style.get_style_phrase(style_key)}")
    
    # Demo 2: Test each style with different content types
    styles_to_test = ["epic", "gritty", "comedic", "poetic", "neutral", "eerie", "mystical"]
    
    for style in styles_to_test:
        print_section(f"TESTING {style.upper()} STYLE")
        
        # Set the style
        engine.change_narration_style(style)
        style_info = engine.dm_style.get_style_info()
        print(f"Current style: {style_info['name']}")
        print(f"AI Prompt: {style_info['ai_prompt'][:100]}...")
        
        # Test quest description
        quest_data = {
            "name": "The Lost Artifact",
            "description": "Recover an ancient magical artifact from the depths of the abandoned temple"
        }
        quest_desc = engine.generate_quest_description(quest_data, character)
        print(f"\n🎯 Quest Description:")
        print(f"   {quest_desc}")
        
        # Test NPC dialogue
        npc_dialogue = engine.generate_npc_dialogue("Eldara", "Wise Sage", "quest_offer")
        print(f"\n🗣️ NPC Dialogue:")
        print(f"   {npc_dialogue}")
        
        # Test location description
        location_desc = engine.generate_location_description(
            "The Crystal Caverns", 
            "underground cave system", 
            ["glowing crystals", "echoing chambers", "ancient runes"]
        )
        print(f"\n🏔️ Location Description:")
        print(f"   {location_desc}")
        
        # Test narrative response
        narrative_response = engine.generate_narrative_response("draw your sword", {"combat": True})
        print(f"\n⚔️ Narrative Response:")
        print(f"   {narrative_response}")
        
        # Test combat description
        combat_desc = engine.generate_combat_description("swings their mighty axe", "Thorin", "Goblin", 12, True)
        print(f"\n⚔️ Combat Description:")
        print(f"   {combat_desc}")
        
        print("\n" + "─" * 40)
    
    # Demo 3: Style switching and persistence
    print_section("STYLE SWITCHING AND PERSISTENCE")
    
    # Show style history
    style_summary = engine.get_narration_style_summary()
    print(f"Current style: {style_summary['current_style']}")
    print(f"Style history: {style_summary['style_history']}")
    
    # Test style switching
    print("\n🔄 Switching to Epic style...")
    result = engine.change_narration_style("epic")
    print(f"Result: {result['message']}")
    print(f"Example phrase: {result['example_phrase']}")
    
    # Demo 4: Campaign integration
    print_section("CAMPAIGN INTEGRATION")
    
    # Create a campaign manager
    campaign_manager = CampaignManager("demo_campaigns")
    campaign_manager.engine = engine
    
    print("🎮 Creating a new campaign with narration style selection...")
    print("(This would normally prompt for user input)")
    
    # Simulate campaign creation with style selection
    campaign_name = "Demo Campaign"
    character = Character(
        name="Aria Shadowstep",
        character_class="Rogue",
        level=3,
        stats={"STR": 12, "DEX": 18, "CON": 14, "INT": 14, "WIS": 12, "CHA": 16}
    )
    
    # Set a specific style for the campaign
    engine.change_narration_style("mystical")
    
    # Generate campaign content with the selected style
    print(f"\n✨ Campaign: {campaign_name}")
    print(f"Character: {character.name} the {character.character_class}")
    print(f"Narration Style: {engine.dm_style.get_style_info()['name']}")
    
    # Generate quest with mystical style
    quest_data = {
        "name": "The Whispering Shadows",
        "description": "Investigate mysterious disappearances in the enchanted forest"
    }
    quest_desc = engine.generate_quest_description(quest_data, character)
    print(f"\n🎯 Campaign Quest:")
    print(f"   {quest_desc}")
    
    # Generate NPC interaction
    npc_dialogue = engine.generate_npc_dialogue("Mystic Elara", "Forest Guardian", "information")
    print(f"\n🗣️ NPC Interaction:")
    print(f"   {npc_dialogue}")
    
    # Demo 5: Style-specific vocabulary and prompts
    print_section("STYLE-SPECIFIC FEATURES")
    
    for style in ["epic", "gritty", "poetic"]:
        engine.change_narration_style(style)
        style_info = engine.dm_style.get_style_info()
        vocabulary = engine.dm_style.get_style_vocabulary()
        
        print(f"\n{style_info['name']} Style:")
        print(f"   Vocabulary suggestions: {', '.join(vocabulary[:5])}...")
        print(f"   AI Prompt: {style_info['ai_prompt'][:80]}...")
    
    # Demo 6: Integration with other systems
    print_section("SYSTEM INTEGRATION")
    
    # Test with dice rolling
    print("\n🎲 Dice rolling with style:")
    dice_result = engine.roll_dice("2d6+3")
    print(f"   Roll: {dice_result['formatted']}")
    
    # Test with class mechanics
    print("\n⚔️ Class mechanics with style:")
    rage_result = engine.use_class_feature(character, "rage")
    print(f"   Rage: {rage_result['message']}")
    
    # Test with quest generation
    print("\n📋 Quest generation with style:")
    quest = engine.generate_quest(character, {"location": "forest", "danger_level": "medium"})
    quest_desc = engine.generate_quest_description(quest, character)
    print(f"   Generated quest: {quest_desc}")
    
    print_header("DEMO COMPLETE")
    print("✅ All narration style features demonstrated successfully!")
    print("\nKey Features Showcased:")
    print("  • 7 different narration styles (Epic, Gritty, Comedic, Poetic, Neutral, Eerie, Mystical)")
    print("  • Style-specific AI prompts for consistent tone")
    print("  • Dynamic content generation (quests, NPCs, locations, combat)")
    print("  • Style switching and persistence")
    print("  • Campaign integration")
    print("  • Vocabulary suggestions and phrase generation")
    print("  • Integration with dice rolling and class mechanics")
    
    print("\n🎮 To use in a real campaign:")
    print("  1. Run 'python main_game.py'")
    print("  2. Choose 'Start New Campaign'")
    print("  3. Select your preferred narration style")
    print("  4. Enjoy your stylized adventure!")

if __name__ == "__main__":
    try:
        demo_narration_styles()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc() 