#!/usr/bin/env python3
"""
Test script for the enhanced combat and skill check system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_campaign_manager import EnhancedCampaignManager
from core.combat_system import Combatant, skill_check_system, DiceRoller

def test_dice_rolling():
    """Test dice rolling functionality"""
    print("🎲 Testing Dice Rolling System")
    print("=" * 40)
    
    # Test various dice notations
    test_dice = ["1d20", "2d6", "1d8+3", "2d4-1", "1d6"]
    
    for dice in test_dice:
        total, breakdown = DiceRoller.roll_dice(dice)
        print(f"{dice}: {breakdown} = {total}")
    
    print()

def test_skill_checks():
    """Test skill check system"""
    print("🎯 Testing Skill Check System")
    print("=" * 40)
    
    # Create a test character
    test_character = Combatant(
        name="Test Character",
        character_type="player",
        armor_class=15,
        max_hit_points=20,
        current_hit_points=20,
        initiative_modifier=2,
        attack_bonus=5,
        damage_dice="1d8+3",
        abilities={
            "strength": 16,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 10,
            "wisdom": 14,
            "charisma": 8
        },
        skills={
            "athletics": 3,
            "perception": 2,
            "stealth": 2
        }
    )
    
    # Test various skill checks
    test_skills = [
        ("athletics", "climbing a wall"),
        ("perception", "searching for hidden enemies"),
        ("stealth", "sneaking past guards")
    ]
    
    for skill, description in test_skills:
        dc = skill_check_system.determine_dc(description)
        result = skill_check_system.make_skill_check(test_character, skill, dc)
        formatted = skill_check_system.format_skill_check_result(result)
        print(f"{skill.title()} ({description}): {formatted}")
    
    print()

def test_combat_system():
    """Test combat system"""
    print("⚔️ Testing Combat System")
    print("=" * 40)
    
    # Create a campaign manager
    manager = EnhancedCampaignManager("Test Campaign")
    
    # Create a test character
    from core.character_manager import Character, Race, CharacterClass, AbilityScore
    
    test_char = Character(
        name="Hero",
        race=Race.HUMAN,
        character_class=CharacterClass.FIGHTER,
        level=3,
        background="Soldier",
        personality_traits=["Brave", "Loyal"],
        ability_scores={
            AbilityScore.STRENGTH: 16,
            AbilityScore.DEXTERITY: 14,
            AbilityScore.CONSTITUTION: 14,
            AbilityScore.INTELLIGENCE: 10,
            AbilityScore.WISDOM: 12,
            AbilityScore.CHARISMA: 8
        }
    )
    
    # Add combat stats
    test_char.armor_class = 16
    test_char.max_hit_points = 28
    test_char.hit_points = 28
    test_char.attack_bonus = 5
    test_char.damage_dice = "1d8+3"
    
    # Add character to manager
    manager.player_characters["Hero"] = test_char
    
    # Create enemies
    enemies = [
        {
            "name": "Goblin",
            "armor_class": 12,
            "hit_points": 8,
            "initiative_modifier": 2,
            "attack_bonus": 4,
            "damage_dice": "1d6+2",
            "abilities": {"strength": 8, "dexterity": 14, "constitution": 10, "intelligence": 8, "wisdom": 8, "charisma": 8},
            "skills": {}
        },
        {
            "name": "Orc",
            "armor_class": 14,
            "hit_points": 15,
            "initiative_modifier": 1,
            "attack_bonus": 5,
            "damage_dice": "1d8+3",
            "abilities": {"strength": 16, "dexterity": 12, "constitution": 14, "intelligence": 7, "wisdom": 11, "charisma": 10},
            "skills": {}
        }
    ]
    
    # Start combat
    print("Starting combat encounter...")
    combat_status = manager.start_combat(enemies)
    
    print(f"Combat started! Round {combat_status['round']}")
    print("Initiative order:")
    for entry in combat_status['initiative_order']:
        print(f"  {entry['position']}. {entry['combatant']['name']} (Initiative: {entry['total']})")
    
    print()
    
    # Simulate a few rounds of combat
    for round_num in range(1, 4):
        print(f"--- Round {round_num} ---")
        
        # Get current combatant
        current = manager.get_combat_status()['current_combatant']
        print(f"Current turn: {current}")
        
        # Make an attack (simplified - just attack the first available target)
        combatants = list(manager.combat_system.combatants.keys())
        if len(combatants) >= 2:
            attacker = current
            # Find a target (not the attacker)
            targets = [c for c in combatants if c != attacker]
            if targets:
                target = targets[0]
                print(f"{attacker} attacks {target}...")
                
                attack_result = manager.make_attack(attacker, target)
                if attack_result.get('hit'):
                    print(f"  HIT! {attack_result['damage_roll']} = {attack_result['damage_dealt']} damage")
                    if attack_result.get('critical_hit'):
                        print("  CRITICAL HIT!")
                else:
                    print(f"  MISS! ({attack_result['total_attack']} vs AC {attack_result['target_ac']})")
        
        # Advance to next turn
        next_combatant = manager.next_combat_turn()
        print(f"Next turn: {next_combatant}")
        print()
    
    # End combat
    print("Ending combat...")
    final_status = manager.end_combat()
    print("Combat ended!")
    print(f"Survivors: {final_status.get('survivors', [])}")

def test_automatic_skill_checks():
    """Test automatic skill check detection"""
    print("🔍 Testing Automatic Skill Check Detection")
    print("=" * 40)
    
    # Create a campaign manager
    manager = EnhancedCampaignManager("Test Campaign")
    
    # Create a test character
    from core.character_manager import Character, Race, CharacterClass, AbilityScore
    
    test_char = Character(
        name="Rogue",
        race=Race.ELF,
        character_class=CharacterClass.ROGUE,
        level=2,
        background="Criminal",
        personality_traits=["Sneaky", "Quick"],
        ability_scores={
            AbilityScore.STRENGTH: 10,
            AbilityScore.DEXTERITY: 16,
            AbilityScore.CONSTITUTION: 12,
            AbilityScore.INTELLIGENCE: 14,
            AbilityScore.WISDOM: 12,
            AbilityScore.CHARISMA: 14
        }
    )
    
    # Add combat stats
    test_char.armor_class = 14
    test_char.max_hit_points = 18
    test_char.hit_points = 18
    test_char.attack_bonus = 5
    test_char.damage_dice = "1d6+3"
    
    # Add character to manager
    manager.player_characters["Rogue"] = test_char
    
    # Test messages that should trigger skill checks
    test_messages = [
        "I try to climb the wall",
        "I search for hidden enemies",
        "I sneak past the guards",
        "I try to persuade the merchant",
        "I investigate the crime scene"
    ]
    
    for message in test_messages:
        print(f"Player: {message}")
        response = manager.process_player_action(message, test_char)
        print(f"Response: {response}")
        print()

def main():
    """Run all tests"""
    print("🧪 Testing Enhanced DnD Combat and Skill Check System")
    print("=" * 60)
    print()
    
    try:
        test_dice_rolling()
        test_skill_checks()
        test_combat_system()
        test_automatic_skill_checks()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 