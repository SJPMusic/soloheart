#!/usr/bin/env python3
"""
Enhanced DnD 5E Mechanics Demo
Demonstrates dice rolling, class mechanics, quest generation, and DM narration styles
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from narrative_core.engine_interface import EnhancedNarrativeEngine
from narrative_core.core import Character
import random

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🎲 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_dice_rolling(engine):
    """Demonstrate dice rolling mechanics"""
    print_header("DICE ROLLING MECHANICS")
    
    # Basic dice rolls
    print_section("Basic Dice Rolls")
    dice_notations = ["1d20", "2d6+3", "1d100", "4d6"]
    
    for notation in dice_notations:
        result = engine.roll_dice(notation)
        if result["success"]:
            print(f"🎲 {result['formatted']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    # Ability checks
    print_section("Ability Checks")
    character = engine.create_character("Demo Hero", "Fighter", 3)
    
    abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    for ability in abilities:
        result = engine.roll_ability_check(character, ability)
        print(f"💪 {result['formatted']}")
    
    # Skill checks
    print_section("Skill Checks")
    skills = ["athletics", "stealth", "perception", "persuasion"]
    for skill in skills:
        result = engine.roll_skill_check(character, skill)
        print(f"🎯 {result['formatted']}")
    
    # Advantage and disadvantage
    print_section("Advantage and Disadvantage")
    result = engine.roll_ability_check(character, "STR", advantage=True)
    print(f"✅ With Advantage: {result['formatted']}")
    
    result = engine.roll_ability_check(character, "DEX", disadvantage=True)
    print(f"❌ With Disadvantage: {result['formatted']}")

def demo_class_mechanics(engine):
    """Demonstrate class-specific mechanics"""
    print_header("CLASS-SPECIFIC MECHANICS")
    
    # Create characters of different classes
    barbarian = engine.create_character("Grommash", "Barbarian", 3)
    fighter = engine.create_character("Aria", "Fighter", 3)
    rogue = engine.create_character("Shadow", "Rogue", 3)
    wizard = engine.create_character("Merlin", "Wizard", 3)
    
    characters = [barbarian, fighter, rogue, wizard]
    
    print_section("Character Creation")
    for char in characters:
        info = engine.get_character_info(char)
        print(f"👤 {info['name']} - Level {info['level']} {info['class']}")
        print(f"   HP: {info['hp']['current']}/{info['hp']['max']}")
        print(f"   Class Features: {list(info['class_features'].keys())}")
    
    # Barbarian Rage
    print_section("Barbarian Rage")
    result = engine.use_class_feature(barbarian, "rage")
    print(f"😤 {result['message']}")
    if result['success']:
        print(f"   Damage Bonus: +{result['damage_bonus']}")
        print(f"   Resistances: {', '.join(result['resistances'])}")
    
    # Fighter Second Wind
    print_section("Fighter Second Wind")
    result = engine.use_class_feature(fighter, "second_wind")
    print(f"💪 {result['message']}")
    if result['success']:
        print(f"   HP Gained: {result['hp_gained']}")
        print(f"   New HP: {result['new_hp']}")
    
    # Rogue Sneak Attack
    print_section("Rogue Sneak Attack")
    result = engine.use_class_feature(rogue, "sneak_attack")
    print(f"🗡️ {result['message']}")
    if result['success']:
        print(f"   Damage: {result['damage']}")
        print(f"   Dice Rolled: {result['dice_rolled']}")
    
    # Wizard Arcane Recovery
    print_section("Wizard Arcane Recovery")
    result = engine.use_class_feature(wizard, "arcane_recovery")
    print(f"✨ {result['message']}")
    if result['success']:
        print(f"   Recovered Slots: {result['recovered_slots']}")

def demo_quest_generation(engine):
    """Demonstrate quest generation"""
    print_header("QUEST GENERATION")
    
    character = engine.create_character("Adventurer", "Fighter", 5)
    
    print_section("Quest Generation")
    context = {
        "location": "urban",
        "time": "night",
        "danger_level": "high"
    }
    
    result = engine.generate_quest(character, context)
    quest = result["quest"]
    
    print(f"📜 {quest['name']}")
    print(f"📝 {quest['description']}")
    print(f"🎯 Difficulty: {quest['difficulty']}")
    print(f"💰 Rewards: {quest['rewards']['gold']} gold, {quest['rewards']['experience']} XP")
    print(f"🎁 Items: {', '.join(quest['rewards']['items'])}")
    
    print(f"\n📋 Objectives:")
    for i, objective in enumerate(quest['objectives'], 1):
        print(f"   {i}. {objective}")
    
    if 'difficulty_modifiers' in quest:
        print(f"\n⚠️ Difficulty Modifiers:")
        for modifier in quest['difficulty_modifiers']:
            print(f"   • {modifier}")
    
    print(f"\n🔗 Context Hooks:")
    for hook in quest['context_hooks']:
        print(f"   • {hook}")
    
    # Complete an objective
    print_section("Quest Progress")
    result = engine.complete_quest_objective(0)
    print(f"✅ {result['message']}")

def demo_dm_narration_styles(engine):
    """Demonstrate DM narration styles"""
    print_header("DM NARRATION STYLES")
    
    styles = ["epic", "eerie", "comedic", "gritty", "mystical"]
    sample_text = "You draw your sword and prepare for battle."
    
    print_section("Available Styles")
    for style in styles:
        info = engine.get_narration_style(style)
        print(f"🎭 {info['name']}: {info['description']}")
        print(f"   Tone: {info['tone']}")
    
    print_section("Style Examples")
    for style in styles:
        engine.set_narration_style(style)
        formatted = engine.format_narration(sample_text)
        phrase = engine.get_style_phrase()
        print(f"🎭 {style.upper()}:")
        print(f"   Text: {formatted}")
        print(f"   Phrase: {phrase}")
    
    # Set back to epic
    engine.set_narration_style("epic")

def demo_combat_system(engine):
    """Demonstrate combat mechanics"""
    print_header("COMBAT SYSTEM")
    
    # Create characters for combat
    player = engine.create_character("Hero", "Fighter", 3)
    enemy1 = engine.create_character("Goblin", "Fighter", 1)
    enemy2 = engine.create_character("Orc", "Barbarian", 2)
    
    # Make enemies non-player characters
    enemy1.is_player = False
    enemy2.is_player = False
    
    characters = [player, enemy1, enemy2]
    
    print_section("Combat Setup")
    result = engine.start_combat(characters)
    print(f"⚔️ {result['message']}")
    print(f"📋 Initiative Order: {' → '.join(result['initiative_order'])}")
    print(f"🎯 Current Turn: {result['current_turn']}")
    
    print_section("Combat Turns")
    for i in range(3):
        result = engine.next_turn()
        current_char = result['character']
        print(f"🔄 Turn {i+1}: {result['current_turn']}")
        print(f"   HP: {current_char.current_hp}/{current_char.max_hp}")
        print(f"   Class: {current_char.character_class}")
        
        # Simulate some damage
        if not current_char.is_player:
            damage = random.randint(1, 8)
            current_char.apply_damage(damage)
            print(f"   💥 Took {damage} damage!")
    
    print_section("Combat Status")
    status = engine.get_combat_status()
    print(f"⚔️ Combat Active: {status['combat_active']}")
    if status['combat_active']:
        print(f"🎯 Current Turn: {status['current_turn']}")
    
    # End combat
    result = engine.end_combat()
    print(f"🏁 {result['message']}")

def demo_character_progression(engine):
    """Demonstrate character progression"""
    print_header("CHARACTER PROGRESSION")
    
    character = engine.create_character("Novice", "Wizard", 1)
    
    print_section("Starting Character")
    info = engine.get_character_info(character)
    print(f"👤 {info['name']} - Level {info['level']} {info['class']}")
    print(f"📊 Experience: {info['experience']}/{info['experience_to_next']}")
    print(f"💙 HP: {info['hp']['current']}/{info['hp']['max']}")
    print(f"📚 Spell Slots: {info['class_features']['spell_slots']}")
    
    print_section("Gaining Experience")
    xp_gain = 500
    result = engine.add_experience(character, xp_gain)
    print(f"⭐ {result['message']}")
    
    if result['leveled_up']:
        print(f"🎉 Leveled up to level {result['new_level']}!")
        
        # Show updated character info
        info = engine.get_character_info(character)
        print(f"📊 New Experience: {info['experience']}/{info['experience_to_next']}")
        print(f"💙 New HP: {info['hp']['current']}/{info['hp']['max']}")
        print(f"📚 New Spell Slots: {info['class_features']['spell_slots']}")
    
    print_section("Available Actions")
    actions = engine.get_available_actions(character)
    print(f"🎯 Basic Actions: {', '.join(actions['basic'])}")
    print(f"🏃 Movement Actions: {', '.join(actions['movement'])}")
    print(f"✨ Class Actions: {', '.join(actions['class_specific'])}")

def main():
    """Run the complete demo"""
    print("🎲 Enhanced DnD 5E Mechanics Demo")
    print("Demonstrating dice rolling, class mechanics, quest generation, and more!")
    
    # Initialize the engine
    engine = EnhancedNarrativeEngine()
    
    try:
        # Run all demos
        demo_dice_rolling(engine)
        demo_class_mechanics(engine)
        demo_quest_generation(engine)
        demo_dm_narration_styles(engine)
        demo_combat_system(engine)
        demo_character_progression(engine)
        
        print_header("DEMO COMPLETE")
        print("✅ All enhanced DnD mechanics demonstrated successfully!")
        print("\n🎮 Features implemented:")
        print("   • Comprehensive dice rolling with modifiers")
        print("   • Class-specific mechanics (Rage, Second Wind, Sneak Attack, etc.)")
        print("   • Dynamic quest generation with context")
        print("   • Multiple DM narration styles")
        print("   • Turn-based combat system")
        print("   • Character progression and experience")
        print("   • Skill and ability checks with advantage/disadvantage")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 