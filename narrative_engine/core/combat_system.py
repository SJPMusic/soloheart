"""
DnD 5E AI-Powered Game - Combat System
=====================================

Comprehensive combat and skill check system for DnD 5E
"""

import random
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class Combatant:
    """Represents a participant in combat"""
    name: str
    character_type: str  # 'player', 'npc', 'monster'
    armor_class: int
    max_hit_points: int
    current_hit_points: int
    initiative_modifier: int
    attack_bonus: int
    damage_dice: str  # e.g., "1d8+3"
    abilities: Dict[str, int]  # ability scores
    skills: Dict[str, int]  # skill modifiers
    
    def is_alive(self) -> bool:
        return self.current_hit_points > 0
    
    def take_damage(self, damage: int) -> int:
        """Apply damage and return actual damage dealt"""
        actual_damage = min(damage, self.current_hit_points)
        self.current_hit_points = max(0, self.current_hit_points - damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Apply healing and return actual healing done"""
        actual_healing = min(amount, self.max_hit_points - self.current_hit_points)
        self.current_hit_points = min(self.max_hit_points, self.current_hit_points + amount)
        return actual_healing

@dataclass
class InitiativeEntry:
    """Represents an initiative roll result"""
    combatant: Combatant
    roll: int
    total: int
    position: int = 0

@dataclass
class SkillCheckResult:
    """Represents the result of a skill check"""
    skill_name: str
    dice_roll: int
    modifier: int
    total: int
    difficulty_class: int
    success: bool
    critical_success: bool = False
    critical_failure: bool = False
    
    def __post_init__(self):
        self.critical_success = self.dice_roll == 20
        self.critical_failure = self.dice_roll == 1

@dataclass
class AttackResult:
    """Represents the result of an attack"""
    attacker: str
    target: str
    attack_roll: int
    attack_bonus: int
    total_attack: int
    target_ac: int
    hit: bool
    critical_hit: bool = False
    damage_roll: Optional[str] = None
    damage_dealt: Optional[int] = None

class DiceRoller:
    """Handles all dice rolling operations"""
    
    @staticmethod
    def roll_d20() -> int:
        """Roll a single d20"""
        return random.randint(1, 20)
    
    @staticmethod
    def roll_dice(dice_notation: str) -> Tuple[int, str]:
        """
        Roll dice based on notation (e.g., "2d6+3", "1d8", "1d4-1")
        Returns (total, breakdown_string)
        """
        try:
            # Parse dice notation
            if '+' in dice_notation:
                dice_part, modifier_part = dice_notation.split('+', 1)
                modifier = int(modifier_part)
            elif '-' in dice_notation:
                dice_part, modifier_part = dice_notation.split('-', 1)
                modifier = -int(modifier_part)
            else:
                dice_part = dice_notation
                modifier = 0
            
            # Parse dice part (e.g., "2d6")
            if 'd' in dice_part:
                count, sides = dice_part.split('d')
                count, sides = int(count), int(sides)
            else:
                count, sides = 1, int(dice_part)
            
            # Roll the dice
            rolls = [random.randint(1, sides) for _ in range(count)]
            total = sum(rolls) + modifier
            
            # Create breakdown string
            if count == 1:
                breakdown = f"{rolls[0]}"
            else:
                breakdown = f"({' + '.join(map(str, rolls))})"
            
            if modifier > 0:
                breakdown += f" + {modifier}"
            elif modifier < 0:
                breakdown += f" - {abs(modifier)}"
            
            return total, breakdown
            
        except Exception as e:
            logger.error(f"Error parsing dice notation '{dice_notation}': {e}")
            return 0, "error"

class CombatSystem:
    """Manages combat encounters and related mechanics"""
    
    def __init__(self):
        self.combatants: Dict[str, Combatant] = {}
        self.initiative_order: List[InitiativeEntry] = []
        self.current_turn: int = 0
        self.round: int = 0
        self.in_combat: bool = False
        self.combat_log: List[Dict[str, Any]] = []
    
    def add_combatant(self, combatant: Combatant) -> None:
        """Add a combatant to the combat"""
        self.combatants[combatant.name] = combatant
    
    def remove_combatant(self, name: str) -> None:
        """Remove a combatant from combat"""
        if name in self.combatants:
            del self.combatants[name]
            # Remove from initiative order
            self.initiative_order = [entry for entry in self.initiative_order if entry.combatant.name != name]
    
    def roll_initiative(self) -> List[InitiativeEntry]:
        """Roll initiative for all combatants and establish turn order"""
        self.initiative_order = []
        
        for combatant in self.combatants.values():
            roll = DiceRoller.roll_d20()
            total = roll + combatant.initiative_modifier
            
            entry = InitiativeEntry(
                combatant=combatant,
                roll=roll,
                total=total
            )
            self.initiative_order.append(entry)
        
        # Sort by total initiative (highest first), then by roll (highest first)
        self.initiative_order.sort(key=lambda x: (x.total, x.roll), reverse=True)
        
        # Assign positions
        for i, entry in enumerate(self.initiative_order):
            entry.position = i + 1
        
        self.current_turn = 0
        self.round = 1
        self.in_combat = True
        
        # Log the initiative roll
        self.log_event("initiative", {
            "combatants": [asdict(entry) for entry in self.initiative_order]
        })
        
        return self.initiative_order
    
    def get_current_combatant(self) -> Optional[Combatant]:
        """Get the combatant whose turn it currently is"""
        if not self.in_combat or not self.initiative_order:
            return None
        
        return self.initiative_order[self.current_turn].combatant
    
    def next_turn(self) -> Optional[Combatant]:
        """Advance to the next turn"""
        if not self.in_combat or not self.initiative_order:
            return None
        
        self.current_turn += 1
        
        # Check if we need to start a new round
        if self.current_turn >= len(self.initiative_order):
            self.current_turn = 0
            self.round += 1
        
        return self.get_current_combatant()
    
    def make_attack(self, attacker_name: str, target_name: str, 
                   attack_type: str = "melee") -> AttackResult:
        """Make an attack roll"""
        if attacker_name not in self.combatants or target_name not in self.combatants:
            raise ValueError(f"Invalid attacker or target: {attacker_name} -> {target_name}")
        
        attacker = self.combatants[attacker_name]
        target = self.combatants[target_name]
        
        # Roll attack
        attack_roll = DiceRoller.roll_d20()
        total_attack = attack_roll + attacker.attack_bonus
        
        # Determine if hit
        hit = total_attack >= target.armor_class
        critical_hit = attack_roll == 20
        
        result = AttackResult(
            attacker=attacker_name,
            target=target_name,
            attack_roll=attack_roll,
            attack_bonus=attacker.attack_bonus,
            total_attack=total_attack,
            target_ac=target.armor_class,
            hit=hit,
            critical_hit=critical_hit
        )
        
        # If hit, roll damage
        if hit:
            damage, damage_breakdown = DiceRoller.roll_dice(attacker.damage_dice)
            if critical_hit:
                # Critical hit: roll damage dice twice
                crit_damage, crit_breakdown = DiceRoller.roll_dice(attacker.damage_dice)
                damage += crit_damage
                damage_breakdown = f"({damage_breakdown} + {crit_breakdown}) CRITICAL!"
            
            actual_damage = target.take_damage(damage)
            
            result.damage_roll = damage_breakdown
            result.damage_dealt = actual_damage
            
            # Check if target is defeated
            if not target.is_alive():
                self.log_event("defeat", {
                    "defeated": target_name,
                    "defeated_by": attacker_name
                })
        
        # Log the attack
        self.log_event("attack", asdict(result))
        
        return result
    
    def end_combat(self) -> None:
        """End the current combat encounter"""
        self.in_combat = False
        self.current_turn = 0
        self.round = 0
        self.log_event("combat_end", {
            "survivors": [name for name, combatant in self.combatants.items() if combatant.is_alive()]
        })
    
    def get_combat_status(self) -> Dict[str, Any]:
        """Get current combat status"""
        return {
            "in_combat": self.in_combat,
            "round": self.round,
            "current_turn": self.current_turn,
            "initiative_order": [asdict(entry) for entry in self.initiative_order],
            "combatants": {name: asdict(combatant) for name, combatant in self.combatants.items()},
            "current_combatant": self.get_current_combatant().name if self.get_current_combatant() else None
        }
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log a combat event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "data": data
        }
        self.combat_log.append(event)
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the combat system"""
        return {
            "combatants": {name: asdict(combatant) for name, combatant in self.combatants.items()},
            "initiative_order": [asdict(entry) for entry in self.initiative_order],
            "current_turn": self.current_turn,
            "round": self.round,
            "in_combat": self.in_combat,
            "combat_log": self.combat_log
        }
    
    def load_state(self, state: Dict[str, Any]) -> None:
        """Load combat state from saved data"""
        # Reconstruct combatants
        self.combatants = {}
        for name, data in state.get("combatants", {}).items():
            self.combatants[name] = Combatant(**data)
        
        # Reconstruct initiative order
        self.initiative_order = []
        for entry_data in state.get("initiative_order", []):
            combatant_name = entry_data["combatant"]["name"]
            if combatant_name in self.combatants:
                entry = InitiativeEntry(
                    combatant=self.combatants[combatant_name],
                    roll=entry_data["roll"],
                    total=entry_data["total"],
                    position=entry_data["position"]
                )
                self.initiative_order.append(entry)
        
        self.current_turn = state.get("current_turn", 0)
        self.round = state.get("round", 0)
        self.in_combat = state.get("in_combat", False)
        self.combat_log = state.get("combat_log", [])

class SkillCheckSystem:
    """Handles skill checks and ability checks"""
    
    # Standard skill mappings
    SKILL_ABILITY_MAP = {
        "acrobatics": "dexterity",
        "animal_handling": "wisdom",
        "arcana": "intelligence",
        "athletics": "strength",
        "deception": "charisma",
        "history": "intelligence",
        "insight": "wisdom",
        "intimidation": "charisma",
        "investigation": "intelligence",
        "medicine": "wisdom",
        "nature": "intelligence",
        "perception": "wisdom",
        "performance": "charisma",
        "persuasion": "charisma",
        "religion": "intelligence",
        "sleight_of_hand": "dexterity",
        "stealth": "dexterity",
        "survival": "wisdom"
    }
    
    @staticmethod
    def calculate_modifier(ability_score: int) -> int:
        """Calculate ability modifier from ability score"""
        return (ability_score - 10) // 2
    
    @staticmethod
    def make_skill_check(character: Combatant, skill_name: str, 
                        difficulty_class: int, advantage: bool = False, 
                        disadvantage: bool = False) -> SkillCheckResult:
        """Make a skill check"""
        # Get the base ability for this skill
        ability_name = SkillCheckSystem.SKILL_ABILITY_MAP.get(skill_name.lower(), skill_name.lower())
        ability_score = character.abilities.get(ability_name, 10)
        base_modifier = SkillCheckSystem.calculate_modifier(ability_score)
        
        # Add skill proficiency if applicable
        skill_modifier = character.skills.get(skill_name.lower(), 0)
        total_modifier = base_modifier + skill_modifier
        
        # Roll the dice
        if advantage and disadvantage:
            # Advantage and disadvantage cancel out
            dice_roll = DiceRoller.roll_d20()
        elif advantage:
            # Roll twice, take the higher
            roll1 = DiceRoller.roll_d20()
            roll2 = DiceRoller.roll_d20()
            dice_roll = max(roll1, roll2)
        elif disadvantage:
            # Roll twice, take the lower
            roll1 = DiceRoller.roll_d20()
            roll2 = DiceRoller.roll_d20()
            dice_roll = min(roll1, roll2)
        else:
            dice_roll = DiceRoller.roll_d20()
        
        total = dice_roll + total_modifier
        success = total >= difficulty_class
        
        return SkillCheckResult(
            skill_name=skill_name,
            dice_roll=dice_roll,
            modifier=total_modifier,
            total=total,
            difficulty_class=difficulty_class,
            success=success
        )
    
    @staticmethod
    def determine_dc(task_description: str, character_level: int = 1) -> int:
        """Determine difficulty class based on task description and character level"""
        # Base DC on task complexity
        task_lower = task_description.lower()
        
        # Very easy tasks
        if any(word in task_lower for word in ["simple", "basic", "easy", "trivial"]):
            return 5
        
        # Easy tasks
        if any(word in task_lower for word in ["straightforward", "routine", "normal"]):
            return 10
        
        # Medium tasks
        if any(word in task_lower for word in ["challenging", "moderate", "standard"]):
            return 15
        
        # Hard tasks
        if any(word in task_lower for word in ["difficult", "hard", "complex"]):
            return 20
        
        # Very hard tasks
        if any(word in task_lower for word in ["very hard", "extremely difficult", "nearly impossible"]):
            return 25
        
        # Nearly impossible
        if any(word in task_lower for word in ["impossible", "legendary", "mythic"]):
            return 30
        
        # Default to medium difficulty
        return 15
    
    @staticmethod
    def format_skill_check_result(result: SkillCheckResult) -> str:
        """Format a skill check result as a readable string"""
        status = "SUCCESS" if result.success else "FAILURE"
        if result.critical_success:
            status = "CRITICAL SUCCESS!"
        elif result.critical_failure:
            status = "CRITICAL FAILURE!"
        
        return (f"{result.skill_name.title()} Check: "
                f"{result.dice_roll} + {result.modifier} = {result.total} "
                f"(DC {result.difficulty_class}) - {status}")

# Global instances
combat_system = CombatSystem()
skill_check_system = SkillCheckSystem() 