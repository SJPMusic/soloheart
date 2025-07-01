from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

# --- Player Character ---
@dataclass
class Character:
    name: str
    character_class: str
    level: int = 1
    stats: Dict[str, int] = field(default_factory=lambda: {s: 10 for s in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]})
    current_hp: int = 10
    max_hp: int = 10
    inventory: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    inspiration: bool = False
    initiative: Optional[int] = None
    is_player: bool = True
    
    # Class-specific attributes
    spell_slots: Dict[int, int] = field(default_factory=dict)  # {spell_level: remaining_slots}
    rage_charges: int = 0  # Barbarian rage charges
    second_wind_available: bool = True  # Fighter second wind
    arcane_recovery_available: bool = True  # Wizard arcane recovery
    sneak_attack_dice: int = 1  # Rogue sneak attack dice
    
    # Combat attributes
    armor_class: int = 10
    proficiency_bonus: int = 2
    
    # Experience and progression
    experience: int = 0
    experience_to_next_level: int = 300
    
    def __post_init__(self):
        """Initialize character after creation"""
        self._calculate_proficiency_bonus()
        self._initialize_class_features()
    
    def _calculate_proficiency_bonus(self):
        """Calculate proficiency bonus based on level"""
        self.proficiency_bonus = 2 + (self.level - 1) // 4
    
    def _initialize_class_features(self):
        """Initialize class-specific features"""
        if self.character_class == "Barbarian":
            self.rage_charges = 2  # 2 rages per long rest at level 1
        elif self.character_class == "Wizard":
            # Initialize spell slots based on level
            from .rules import class_mechanics
            self.spell_slots = class_mechanics.calculate_spell_slots(self.character_class, self.level)
    
    def apply_damage(self, amount: int):
        """Apply damage to the character"""
        self.current_hp = max(0, self.current_hp - amount)
        return self.current_hp
    
    def heal(self, amount: int):
        """Heal the character"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp
    
    def add_condition(self, condition: str):
        """Add a condition to the character"""
        if condition not in self.conditions:
            self.conditions.append(condition)
    
    def remove_condition(self, condition: str):
        """Remove a condition from the character"""
        if condition in self.conditions:
            self.conditions.remove(condition)
    
    def add_experience(self, amount: int) -> Dict[str, Any]:
        """Add experience and check for level up"""
        self.experience += amount
        leveled_up = False
        old_level = self.level
        # Handle multiple level-ups if enough XP is gained
        while self.experience >= self.experience_to_next_level:
            self.level_up()
            leveled_up = True
        return {
            "leveled_up": leveled_up,
            "new_level": self.level
        }
    
    def level_up(self):
        """Level up the character"""
        self.level += 1
        self._calculate_proficiency_bonus()
        
        # Update experience requirements
        self.experience_to_next_level = self._calculate_next_level_xp()
        
        # Update class features
        self._initialize_class_features()
        
        # Increase max HP
        from .rules import dice_roller
        if self.character_class == "Fighter":
            hp_gain, _ = dice_roller.roll_dice("1d10")
        elif self.character_class == "Rogue":
            hp_gain, _ = dice_roller.roll_dice("1d8")
        elif self.character_class == "Wizard":
            hp_gain, _ = dice_roller.roll_dice("1d6")
        else:
            hp_gain, _ = dice_roller.roll_dice("1d8")
        
        # Add Constitution modifier
        con_mod = (self.stats.get("CON", 10) - 10) // 2
        hp_gain = max(1, hp_gain + con_mod)  # Minimum 1 HP gain
        
        self.max_hp += hp_gain
        self.current_hp += hp_gain  # Heal to full on level up
    
    def _calculate_next_level_xp(self) -> int:
        """Calculate experience required for next level"""
        xp_table = {
            1: 300, 2: 900, 3: 2700, 4: 6500, 5: 14000,
            6: 23000, 7: 34000, 8: 48000, 9: 64000, 10: 85000,
            11: 100000, 12: 120000, 13: 140000, 14: 165000, 15: 195000,
            16: 225000, 17: 265000, 18: 305000, 19: 355000, 20: 355000
        }
        return xp_table.get(self.level + 1, 355000)
    
    def get_modifier(self, stat: str) -> int:
        """Get the modifier for a given stat"""
        stat_value = self.stats.get(stat.upper(), 10)
        return (stat_value - 10) // 2
    
    def get_skill_bonus(self, skill: str) -> int:
        """Get the total bonus for a skill check"""
        # This is a simplified version - in full DnD, skills are tied to specific stats
        # For now, we'll use the most appropriate stat for common skills
        skill_to_stat = {
            "acrobatics": "DEX", "athletics": "STR", "deception": "CHA",
            "insight": "WIS", "intimidation": "CHA", "investigation": "INT",
            "perception": "WIS", "persuasion": "CHA", "stealth": "DEX",
            "survival": "WIS"
        }
        
        stat = skill_to_stat.get(skill.lower(), "STR")
        stat_mod = self.get_modifier(stat)
        
        # Add proficiency bonus if proficient (simplified - assume all skills are proficient)
        return stat_mod + self.proficiency_bonus
    
    def long_rest(self):
        """Take a long rest - restore all resources"""
        self.current_hp = self.max_hp
        self.conditions.clear()
        
        # Restore class-specific resources
        if self.character_class == "Barbarian":
            self.rage_charges = 2  # Reset rage charges
        elif self.character_class == "Fighter":
            self.second_wind_available = True
        elif self.character_class == "Wizard":
            self.arcane_recovery_available = True
            # Restore all spell slots
            from .rules import class_mechanics
            self.spell_slots = class_mechanics.calculate_spell_slots(self.character_class, self.level)
    
    def short_rest(self) -> str:
        """Take a short rest - restore some resources"""
        from .rules import class_mechanics
        return class_mechanics.short_rest_recovery(self)
    
    @property
    def hp(self) -> int:
        """Backward compatibility property"""
        return self.current_hp
    
    @hp.setter
    def hp(self, value: int):
        """Backward compatibility setter"""
        self.current_hp = value

# --- Turn Logic ---
@dataclass
class TurnOrder:
    participants: List[Character]
    current_index: int = 0
    
    def next(self) -> Character:
        self.current_index = (self.current_index + 1) % len(self.participants)
        return self.participants[self.current_index]
    
    def current(self) -> Character:
        return self.participants[self.current_index]
    
    def reset(self):
        self.current_index = 0

# --- Utility ---
def roll_initiative(characters: List[Character], rng=None) -> List[Character]:
    import random
    rng = rng or random
    for c in characters:
        c.initiative = rng.randint(1, 20) + c.get_modifier("DEX")
    return sorted(characters, key=lambda c: c.initiative or 0, reverse=True)
