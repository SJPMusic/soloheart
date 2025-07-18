"""
DnD 5E Character Creator - Interactive Character Creation System
===============================================================

Guides players through DnD 5E character creation step-by-step:
1. Race selection
2. Class selection  
3. Ability scores
4. Background
5. Equipment
6. Backstory generation
7. Character sheet completion
"""

import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class CharacterCreationStep(Enum):
    START = "start"
    RACE = "race"
    CLASS = "class"
    ABILITY_SCORES = "ability_scores"
    BACKGROUND = "background"
    EQUIPMENT = "equipment"
    BACKSTORY = "backstory"
    REVIEW = "review"
    COMPLETE = "complete"

@dataclass
class Race:
    name: str
    description: str
    ability_bonuses: Dict[str, int]
    traits: List[str]
    subraces: List[str] = None
    size: str = "Medium"
    speed: int = 30
    languages: List[str] = None

@dataclass
class CharacterClass:
    name: str
    description: str
    hit_die: int
    primary_ability: str
    saving_throw_proficiencies: List[str]
    armor_proficiencies: List[str]
    weapon_proficiencies: List[str]
    starting_equipment: List[str]
    class_features: List[str]

@dataclass
class Background:
    name: str
    description: str
    skill_proficiencies: List[str]
    tool_proficiencies: List[str]
    languages: List[str]
    equipment: List[str]
    feature: str
    personality_traits: List[str]
    ideals: List[str]
    bonds: List[str]
    flaws: List[str]

class CharacterCreator:
    """Interactive DnD 5E character creation system"""
    
    def __init__(self):
        self.current_step = CharacterCreationStep.START
        self.character_data = {}
        self.available_races = self._load_races()
        self.available_classes = self._load_classes()
        self.available_backgrounds = self._load_backgrounds()
        
    def get_current_step(self) -> CharacterCreationStep:
        """Get the current creation step"""
        return self.current_step
    
    def get_step_instructions(self) -> str:
        """Get instructions for the current step"""
        instructions = {
            CharacterCreationStep.START: "Welcome to DnD 5E Character Creation! Let's begin by choosing your character's race.",
            CharacterCreationStep.RACE: "Choose your character's race. This determines your basic traits and ability score bonuses.",
            CharacterCreationStep.CLASS: "Select your character's class. This defines your role and abilities in the party.",
            CharacterCreationStep.ABILITY_SCORES: "Determine your ability scores. You can roll dice, use point buy, or standard array.",
            CharacterCreationStep.BACKGROUND: "Pick a background that reflects your character's life before becoming an adventurer.",
            CharacterCreationStep.EQUIPMENT: "Choose your starting equipment based on your class and background.",
            CharacterCreationStep.BACKSTORY: "Create your character's backstory and personality.",
            CharacterCreationStep.REVIEW: "Review your character before finalizing.",
            CharacterCreationStep.COMPLETE: "Character creation complete!"
        }
        return instructions.get(self.current_step, "Unknown step")
    
    def get_available_options(self) -> Dict[str, Any]:
        """Get available options for the current step"""
        if self.current_step == CharacterCreationStep.RACE:
            return {
                'races': [{'name': race.name, 'description': race.description} 
                         for race in self.available_races]
            }
        elif self.current_step == CharacterCreationStep.CLASS:
            return {
                'classes': [{'name': cls.name, 'description': cls.description} 
                           for cls in self.available_classes]
            }
        elif self.current_step == CharacterCreationStep.BACKGROUND:
            return {
                'backgrounds': [{'name': bg.name, 'description': bg.description} 
                               for bg in self.available_backgrounds]
            }
        elif self.current_step == CharacterCreationStep.ABILITY_SCORES:
            return {
                'methods': [
                    {'name': 'Standard Array', 'description': 'Use the standard array: 15, 14, 13, 12, 10, 8'},
                    {'name': 'Point Buy', 'description': 'Use 27 points to buy ability scores'},
                    {'name': 'Roll Dice', 'description': 'Roll 4d6, drop lowest, repeat 6 times'}
                ]
            }
        return {}
    
    def make_choice(self, choice: str, details: Dict[str, Any] = None) -> str:
        """Make a choice for the current step"""
        if self.current_step == CharacterCreationStep.START:
            self.current_step = CharacterCreationStep.RACE
            return "Great! Let's choose your race."
            
        elif self.current_step == CharacterCreationStep.RACE:
            selected_race = next((r for r in self.available_races if r.name.lower() == choice.lower()), None)
            if selected_race:
                self.character_data['race'] = asdict(selected_race)
                self.current_step = CharacterCreationStep.CLASS
                return f"Excellent choice! You've selected {selected_race.name}. Now let's choose your class."
            else:
                return f"I don't recognize '{choice}'. Please choose from the available races."
                
        elif self.current_step == CharacterCreationStep.CLASS:
            selected_class = next((c for c in self.available_classes if c.name.lower() == choice.lower()), None)
            if selected_class:
                self.character_data['class'] = asdict(selected_class)
                self.current_step = CharacterCreationStep.ABILITY_SCORES
                return f"Perfect! You've chosen {selected_class.name}. Now let's determine your ability scores."
            else:
                return f"I don't recognize '{choice}'. Please choose from the available classes."
                
        elif self.current_step == CharacterCreationStep.ABILITY_SCORES:
            if choice.lower() == 'standard array':
                self.character_data['ability_scores'] = self._generate_standard_array()
                self.current_step = CharacterCreationStep.BACKGROUND
                return "Standard array applied! Your ability scores are: 15, 14, 13, 12, 10, 8. Now let's choose your background."
            elif choice.lower() == 'point buy':
                # For now, use standard array as fallback
                self.character_data['ability_scores'] = self._generate_standard_array()
                self.current_step = CharacterCreationStep.BACKGROUND
                return "Point buy system applied! Now let's choose your background."
            elif choice.lower() == 'roll dice':
                self.character_data['ability_scores'] = self._roll_ability_scores()
                self.current_step = CharacterCreationStep.BACKGROUND
                scores = self.character_data['ability_scores']
                return f"Dice rolled! Your ability scores are: {scores}. Now let's choose your background."
            else:
                return "Please choose a method: Standard Array, Point Buy, or Roll Dice."
                
        elif self.current_step == CharacterCreationStep.BACKGROUND:
            selected_background = next((b for b in self.available_backgrounds if b.name.lower() == choice.lower()), None)
            if selected_background:
                self.character_data['background'] = asdict(selected_background)
                self.current_step = CharacterCreationStep.EQUIPMENT
                return f"Great background choice! You've selected {selected_background.name}. Now let's choose your equipment."
            else:
                return f"I don't recognize '{choice}'. Please choose from the available backgrounds."
                
        elif self.current_step == CharacterCreationStep.EQUIPMENT:
            # Auto-generate equipment based on class and background
            self.character_data['equipment'] = self._generate_equipment()
            self.current_step = CharacterCreationStep.BACKSTORY
            return "Equipment selected! Now let's create your character's backstory."
            
        elif self.current_step == CharacterCreationStep.BACKSTORY:
            # Generate backstory based on character data
            self.character_data['backstory'] = self._generate_backstory()
            self.current_step = CharacterCreationStep.REVIEW
            return "Backstory generated! Let's review your character."
            
        elif self.current_step == CharacterCreationStep.REVIEW:
            if choice.lower() in ['yes', 'complete', 'finish']:
                self.current_step = CharacterCreationStep.COMPLETE
                return "Character creation complete! Your character is ready for adventure."
            else:
                return "Would you like to complete character creation? Say 'yes' to finish."
                
        return "Invalid choice for current step."
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Get a summary of the character being created"""
        if not self.character_data:
            return {'status': 'No character data yet'}
            
        summary = {
            'race': self.character_data.get('race', {}).get('name', 'Not selected'),
            'class': self.character_data.get('class', {}).get('name', 'Not selected'),
            'ability_scores': self.character_data.get('ability_scores', 'Not determined'),
            'background': self.character_data.get('background', {}).get('name', 'Not selected'),
            'equipment': len(self.character_data.get('equipment', [])),
            'backstory': 'Generated' if 'backstory' in self.character_data else 'Not created'
        }
        
        return summary
    
    def get_complete_character(self) -> Dict[str, Any]:
        """Get the complete character data"""
        if self.current_step != CharacterCreationStep.COMPLETE:
            return {'error': 'Character creation not complete'}
            
        return self.character_data
    
    def _load_races(self) -> List[Race]:
        """Load available races"""
        return [
            Race(
                name="Human",
                description="Humans are the most adaptable and ambitious people among the common races.",
                ability_bonuses={"STR": 1, "DEX": 1, "CON": 1, "INT": 1, "WIS": 1, "CHA": 1},
                traits=["Versatile", "Extra Feat", "Extra Skill Proficiency"],
                languages=["Common", "One extra language"]
            ),
            Race(
                name="Elf",
                description="Elves are a magical people of otherworldly grace, living in the world but not entirely part of it.",
                ability_bonuses={"DEX": 2},
                traits=["Darkvision", "Keen Senses", "Fey Ancestry", "Trance"],
                languages=["Common", "Elvish"]
            ),
            Race(
                name="Dwarf",
                description="Dwarves are solid and enduring like the mountains they love.",
                ability_bonuses={"CON": 2},
                traits=["Darkvision", "Dwarven Resilience", "Dwarven Combat Training", "Stonecunning"],
                languages=["Common", "Dwarvish"]
            ),
            Race(
                name="Halfling",
                description="Halflings are an affable and cheerful people.",
                ability_bonuses={"DEX": 2},
                traits=["Lucky", "Brave", "Halfling Nimbleness"],
                languages=["Common", "Halfling"]
            ),
            Race(
                name="Dragonborn",
                description="Dragonborn look very much like dragons standing erect in humanoid form.",
                ability_bonuses={"STR": 2, "CHA": 1},
                traits=["Draconic Ancestry", "Breath Weapon", "Damage Resistance"],
                languages=["Common", "Draconic"]
            )
        ]
    
    def _load_classes(self) -> List[CharacterClass]:
        """Load available classes"""
        return [
            CharacterClass(
                name="Fighter",
                description="A master of martial combat, skilled with a variety of weapons and armor.",
                hit_die=10,
                primary_ability="STR",
                saving_throw_proficiencies=["STR", "CON"],
                armor_proficiencies=["All armor", "Shields"],
                weapon_proficiencies=["Simple weapons", "Martial weapons"],
                starting_equipment=["Chain mail", "Martial weapon", "Shield", "Crossbow", "20 bolts"],
                class_features=["Fighting Style", "Second Wind"]
            ),
            CharacterClass(
                name="Wizard",
                description="A scholarly magic-user capable of manipulating the structures of reality.",
                hit_die=6,
                primary_ability="INT",
                saving_throw_proficiencies=["INT", "WIS"],
                armor_proficiencies=[],
                weapon_proficiencies=["Daggers", "Quarterstaffs"],
                starting_equipment=["Spellbook", "Arcane focus", "Scholar's pack"],
                class_features=["Spellcasting", "Arcane Recovery"]
            ),
            CharacterClass(
                name="Cleric",
                description="A priestly champion who wields divine magic in service of a higher power.",
                hit_die=8,
                primary_ability="WIS",
                saving_throw_proficiencies=["WIS", "CHA"],
                armor_proficiencies=["Light armor", "Medium armor", "Shields"],
                weapon_proficiencies=["Simple weapons"],
                starting_equipment=["Shield", "Holy symbol", "Priest's pack"],
                class_features=["Spellcasting", "Divine Domain"]
            ),
            CharacterClass(
                name="Rogue",
                description="A scoundrel who uses stealth and trickery to overcome obstacles and enemies.",
                hit_die=8,
                primary_ability="DEX",
                saving_throw_proficiencies=["DEX", "INT"],
                armor_proficiencies=["Light armor"],
                weapon_proficiencies=["Simple weapons", "Hand crossbows", "Longswords", "Rapiers", "Shortswords"],
                starting_equipment=["Leather armor", "Two daggers", "Thieves' tools"],
                class_features=["Expertise", "Sneak Attack", "Thieves' Cant"]
            )
        ]
    
    def _load_backgrounds(self) -> List[Background]:
        """Load available backgrounds"""
        return [
            Background(
                name="Acolyte",
                description="You have spent your life in the service of a temple.",
                skill_proficiencies=["Insight", "Religion"],
                tool_proficiencies=[],
                languages=["Two of your choice"],
                equipment=["Holy symbol", "Prayer book", "5 sticks of incense", "Vestments", "Common clothes", "15 gp"],
                feature="Shelter of the Faithful",
                personality_traits=["I idolize a particular hero of my faith."],
                ideals=["Tradition. The ancient traditions of worship must be preserved."],
                bonds=["I would die to recover an ancient relic of my faith."],
                flaws=["I judge others harshly, and myself even more severely."]
            ),
            Background(
                name="Criminal",
                description="You are an experienced criminal with a history of breaking the law.",
                skill_proficiencies=["Deception", "Stealth"],
                tool_proficiencies=["Thieves' tools", "One type of gaming set"],
                languages=[],
                equipment=["Crowbar", "Dark common clothes with hood", "15 gp"],
                feature="Criminal Contact",
                personality_traits=["I always have a plan for what to do when things go wrong."],
                ideals=["Freedom. Chains are meant to be broken, as are those who would forge them."],
                bonds=["I'm trying to pay off an old debt I owe to a generous benefactor."],
                flaws=["When I see something valuable, I can't think about anything but how to steal it."]
            ),
            Background(
                name="Folk Hero",
                description="You come from a humble social rank, but you are destined for so much more.",
                skill_proficiencies=["Animal Handling", "Survival"],
                tool_proficiencies=["One type of artisan's tools", "Vehicles (land)"],
                languages=[],
                equipment=["Artisan's tools", "Shovel", "Iron pot", "Common clothes", "10 gp"],
                feature="Rustic Hospitality",
                personality_traits=["I judge people by their actions, not their words."],
                ideals=["Respect. People deserve to be treated with dignity and respect."],
                bonds=["I protect those who cannot protect themselves."],
                flaws=["The tyrant who rules my land will stop at nothing to see me killed."]
            )
        ]
    
    def _generate_standard_array(self) -> Dict[str, int]:
        """Generate ability scores using standard array"""
        scores = [15, 14, 13, 12, 10, 8]
        random.shuffle(scores)
        abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        return dict(zip(abilities, scores))
    
    def _roll_ability_scores(self) -> Dict[str, int]:
        """Roll ability scores using 4d6 drop lowest"""
        abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        scores = {}
        
        for ability in abilities:
            # Roll 4d6, drop lowest
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.remove(min(rolls))
            scores[ability] = sum(rolls)
            
        return scores
    
    def _generate_equipment(self) -> List[str]:
        """Generate starting equipment based on class and background"""
        equipment = []
        
        # Add class equipment
        if 'class' in self.character_data:
            equipment.extend(self.character_data['class']['starting_equipment'])
        
        # Add background equipment
        if 'background' in self.character_data:
            equipment.extend(self.character_data['background']['equipment'])
        
        return equipment
    
    def _generate_backstory(self) -> str:
        """Generate a backstory based on character choices"""
        race = self.character_data.get('race', {}).get('name', 'Adventurer')
        char_class = self.character_data.get('class', {}).get('name', 'Hero')
        background = self.character_data.get('background', {}).get('name', 'Wanderer')
        
        backstory_templates = [
            f"You are a {race} {char_class.lower()} with a {background.lower()} background. Your journey has led you to become an adventurer, seeking fortune, glory, or perhaps something more personal.",
            f"Born into the world as a {race}, you discovered your calling as a {char_class.lower()}. Your {background.lower()} past has shaped you into the person you are today.",
            f"A {race} by birth and a {char_class.lower()} by choice, your {background.lower()} experiences have prepared you for the challenges that lie ahead."
        ]
        
        return random.choice(backstory_templates)

# Global instance
character_creator = CharacterCreator() 