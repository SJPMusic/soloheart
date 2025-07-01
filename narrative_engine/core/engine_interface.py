"""
Enhanced Narrative Engine Interface
Integrates dice rolling, class mechanics, quest generation, and DM narration styles
"""

from typing import Dict, List, Optional, Any, Tuple
from .core import Character, TurnOrder, roll_initiative
from .encounters import Encounter, generate_encounter
from .world import WorldState, Location
from .rules import (
    DiceRoller, ClassMechanics, DMNarrationStyle, QuestGenerator,
    saving_throw, apply_condition, remove_condition, CONDITIONS,
    dice_roller, class_mechanics, dm_style, quest_generator
)
from .quest_journal import QuestJournal, Quest, QuestObjective
import random
from .save_manager import save_game as save_game_file, load_game as load_game_file
from ..memory.vector_memory_module import VectorMemoryModule

# --- Engine Interface ---

def create_character(name: str, character_class: str, level: int = 1, stats: dict = None) -> Character:
    return Character(name=name, character_class=character_class, level=level, stats=stats or {})

def create_world() -> WorldState:
    return WorldState()

def create_encounter(encounter_type: str, participants: list, description: str = "") -> Encounter:
    return generate_encounter(encounter_type, participants, description)

def advance_world_time(world: WorldState, hours: int = 1):
    world.advance_time(hours)

def perform_saving_throw(character: Character, stat: str, dc: int) -> bool:
    return saving_throw(character, stat, dc)

def add_condition(character: Character, condition: str):
    apply_condition(character, condition)

def remove_condition_from_character(character: Character, condition: str):
    remove_condition(character, condition)

def get_conditions() -> list:
    return CONDITIONS

class EnhancedNarrativeEngine:
    """
    Enhanced narrative engine with full DnD 5E mechanics integration
    """
    
    def __init__(self, memory_system=None, campaign_id: str = "Default Campaign"):
        self.memory_system = memory_system
        self.dice_roller = dice_roller
        self.class_mechanics = class_mechanics
        self.dm_style = dm_style
        self.quest_generator = quest_generator
        self.quest_journal = QuestJournal()  # Add quest journal
        self.current_quest = None
        self.combat_active = False
        self.turn_order = None
        # Vector memory module (optional)
        try:
            self.vector_memory = VectorMemoryModule(campaign_id=campaign_id)
        except Exception as e:
            print(f"[EnhancedNarrativeEngine] VectorMemoryModule unavailable: {e}")
            self.vector_memory = None
        
    # --- Dice Rolling Interface ---
    
    def roll_dice(self, dice_notation: str) -> Dict[str, Any]:
        """Roll dice and return detailed results"""
        try:
            total, rolls = self.dice_roller.roll_dice(dice_notation)
            return {
                "success": True,
                "dice_notation": dice_notation,
                "total": total,
                "rolls": rolls,
                "formatted": f"{dice_notation}: {rolls} = {total}"
            }
        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "dice_notation": dice_notation
            }
    
    def roll_ability_check(self, character: Character, ability: str, 
                          advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """Roll an ability check for a character"""
        modifier = character.get_modifier(ability)
        
        if advantage and disadvantage:
            # Cancel each other out
            roll, rolls = self.dice_roller.roll_dice("1d20")
            total = roll + modifier
        elif advantage:
            total, rolls = self.dice_roller.roll_with_advantage(modifier)
        elif disadvantage:
            total, rolls = self.dice_roller.roll_with_disadvantage(modifier)
        else:
            roll, rolls = self.dice_roller.roll_dice("1d20")
            total = roll + modifier
        
        # Determine success/failure
        if rolls[0] == 20:
            result = "critical_success"
        elif rolls[0] == 1:
            result = "critical_failure"
        elif total >= 15:  # Arbitrary DC for now
            result = "success"
        else:
            result = "failure"
        
        return {
            "success": True,
            "ability": ability,
            "modifier": modifier,
            "total": total,
            "rolls": rolls,
            "result": result,
            "formatted": f"{ability} check: {rolls} + {modifier} = {total} ({result})"
        }
    
    def roll_skill_check(self, character: Character, skill: str,
                        advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """Roll a skill check for a character"""
        bonus = character.get_skill_bonus(skill)
        
        if advantage and disadvantage:
            roll, rolls = self.dice_roller.roll_dice("1d20")
            total = roll + bonus
        elif advantage:
            total, rolls = self.dice_roller.roll_with_advantage(bonus)
        elif disadvantage:
            total, rolls = self.dice_roller.roll_with_disadvantage(bonus)
        else:
            roll, rolls = self.dice_roller.roll_dice("1d20")
            total = roll + bonus
        
        # Determine success/failure
        if rolls[0] == 20:
            result = "critical_success"
        elif rolls[0] == 1:
            result = "critical_failure"
        elif total >= 15:  # Arbitrary DC for now
            result = "success"
        else:
            result = "failure"
        
        return {
            "success": True,
            "skill": skill,
            "bonus": bonus,
            "total": total,
            "rolls": rolls,
            "result": result,
            "formatted": f"{skill} check: {rolls} + {bonus} = {total} ({result})"
        }
    
    # --- Class Mechanics Interface ---
    
    def use_class_feature(self, character: Character, feature: str, **kwargs) -> Dict[str, Any]:
        """Use a class-specific feature"""
        if feature.lower() == "rage":
            return self.class_mechanics.apply_rage(character)
        elif feature.lower() == "second_wind":
            return self._use_second_wind(character)
        elif feature.lower() == "arcane_recovery":
            return self._use_arcane_recovery(character)
        elif feature.lower() == "sneak_attack":
            return self._calculate_sneak_attack(character, **kwargs)
        else:
            return {"success": False, "message": f"Unknown feature: {feature}"}
    
    def _use_second_wind(self, character: Character) -> Dict[str, Any]:
        """Use Fighter's Second Wind"""
        if character.character_class != "Fighter":
            return {"success": False, "message": "Only Fighters can use Second Wind"}
        
        if not character.second_wind_available:
            return {"success": False, "message": "Second Wind not available"}
        
        recovery, rolls = self.dice_roller.roll_dice(f"1d10+{character.level}")
        old_hp = character.current_hp
        character.current_hp = min(character.current_hp + recovery, character.max_hp)
        character.second_wind_available = False
        
        return {
            "success": True,
            "message": f"Second Wind: {recovery} HP recovered (rolled {rolls})",
            "hp_gained": recovery,
            "old_hp": old_hp,
            "new_hp": character.current_hp
        }
    
    def _use_arcane_recovery(self, character: Character) -> Dict[str, Any]:
        """Use Wizard's Arcane Recovery"""
        if character.character_class != "Wizard":
            return {"success": False, "message": "Only Wizards can use Arcane Recovery"}
        
        if not character.arcane_recovery_available:
            return {"success": False, "message": "Arcane Recovery not available"}
        
        # Recover spell slots equal to half wizard level (rounded up)
        recovery_slots = (character.level + 1) // 2
        max_recovery_level = min(5, character.level // 2 + 1)
        
        recovered = {}
        for level in range(max_recovery_level, 0, -1):
            if recovery_slots > 0 and level in character.spell_slots:
                slots_recovered = min(recovery_slots, character.spell_slots.get(level, 0))
                character.spell_slots[level] += slots_recovered
                recovered[level] = slots_recovered
                recovery_slots -= slots_recovered
        
        character.arcane_recovery_available = False
        
        return {
            "success": True,
            "message": f"Arcane Recovery: Recovered {recovered} spell slots",
            "recovered_slots": recovered
        }
    
    def _calculate_sneak_attack(self, character: Character, **kwargs) -> Dict[str, Any]:
        """Calculate sneak attack damage"""
        if character.character_class != "Rogue":
            return {"success": False, "message": "Only Rogues can use Sneak Attack"}
        
        sneak_dice = self.class_mechanics.calculate_sneak_attack_damage(character, character.level)
        damage, rolls = self.dice_roller.roll_dice(f"{sneak_dice}d6")
        
        return {
            "success": True,
            "message": f"Sneak Attack: {damage} damage (rolled {rolls})",
            "damage": damage,
            "dice_rolled": f"{sneak_dice}d6",
            "rolls": rolls
        }
    
    # --- Quest System Interface ---
    
    def generate_quest(self, character: Character, context: Dict = None) -> Dict[str, Any]:
        """Generate a new quest for the character"""
        quest = self.quest_generator.generate_quest(character, context)
        self.current_quest = quest
        
        # Format quest description with current DM style
        formatted_description = self.dm_style.format_narration(quest["description"])
        
        return {
            "success": True,
            "quest": quest,
            "formatted_description": formatted_description,
            "message": f"New quest generated: {quest['name']}"
        }
    
    def get_current_quest(self) -> Optional[Dict]:
        """Get the current active quest"""
        return self.current_quest
    
    def complete_quest_objective(self, objective_index: int) -> Dict[str, Any]:
        """Mark a quest objective as complete"""
        if not self.current_quest:
            return {"success": False, "message": "No active quest"}
        
        if objective_index >= len(self.current_quest["objectives"]):
            return {"success": False, "message": "Invalid objective index"}
        
        objective = self.current_quest["objectives"][objective_index]
        # In a full implementation, you'd track completion status
        # For now, we'll just return success
        
        return {
            "success": True,
            "message": f"Objective completed: {objective}",
            "objective": objective,
            "index": objective_index
        }
    
    # --- DM Narration Interface ---
    
    def set_narration_style(self, style: str) -> Dict[str, Any]:
        """Set the DM narration style"""
        success = self.dm_style.set_style(style)
        if success:
            style_info = self.dm_style.get_style_info(style)
            return {
                "success": True,
                "style": style,
                "description": style_info.get("description", ""),
                "message": f"DM style set to: {style_info.get('name', style)}"
            }
        else:
            return {
                "success": False,
                "message": f"Unknown style: {style}",
                "available_styles": list(self.dm_style.styles.keys())
            }
    
    def get_narration_style(self, style_name: str = None) -> Dict[str, Any]:
        """Get current narration style information"""
        style = style_name or self.dm_style.current_style
        style_info = self.dm_style.get_style_info(style)
        return {
            "current_style": style,
            "name": style_info.get("name", ""),
            "description": style_info.get("description", ""),
            "tone": style_info.get("tone", "")
        }
    
    def format_narration(self, text: str, style: str = None) -> str:
        """Format text according to the current or specified narration style"""
        return self.dm_style.format_narration(text, style)
    
    def get_style_phrase(self, style: str = None) -> str:
        """Get a random phrase for the current or specified style"""
        return self.dm_style.get_style_phrase(style)
    
    # --- Combat Interface ---
    
    def start_combat(self, characters: List[Character]) -> Dict[str, Any]:
        """Start a combat encounter"""
        if len(characters) < 2:
            return {"success": False, "message": "Need at least 2 characters for combat"}
        
        # Roll initiative
        ordered_characters = roll_initiative(characters)
        self.turn_order = TurnOrder(ordered_characters)
        self.combat_active = True
        
        return {
            "success": True,
            "message": "Combat started!",
            "initiative_order": [c.name for c in ordered_characters],
            "current_turn": self.turn_order.current().name
        }
    
    def end_combat(self) -> Dict[str, Any]:
        """End the current combat encounter"""
        self.combat_active = False
        self.turn_order = None
        
        return {
            "success": True,
            "message": "Combat ended"
        }
    
    def next_turn(self) -> Dict[str, Any]:
        """Advance to the next turn in combat"""
        if not self.combat_active or not self.turn_order:
            return {"success": False, "message": "No active combat"}
        
        current_character = self.turn_order.current()
        next_character = self.turn_order.next()
        
        return {
            "success": True,
            "previous_turn": current_character.name,
            "current_turn": next_character.name,
            "character": next_character
        }
    
    def get_combat_status(self) -> Dict[str, Any]:
        """Get current combat status"""
        if not self.combat_active:
            return {"combat_active": False}
        
        return {
            "combat_active": True,
            "current_turn": self.turn_order.current().name if self.turn_order else None,
            "turn_order": [c.name for c in self.turn_order.participants] if self.turn_order else []
        }
    
    # --- Character Management Interface ---
    
    def create_character(self, name: str, character_class: str, level: int = 1) -> Character:
        """Create a new character with the specified class"""
        # Generate stats (simplified - in full DnD you'd roll 4d6 drop lowest)
        stats = {
            "STR": random.randint(8, 18),
            "DEX": random.randint(8, 18),
            "CON": random.randint(8, 18),
            "INT": random.randint(8, 18),
            "WIS": random.randint(8, 18),
            "CHA": random.randint(8, 18)
        }
        
        # Set base HP based on class
        class_data = self.class_mechanics.class_data.get('classes', {}).get(character_class, {})
        base_hp = class_data.get('base_hp', 8)
        
        character = Character(
            name=name,
            character_class=character_class,
            level=level,
            stats=stats,
            current_hp=base_hp,
            max_hp=base_hp
        )
        
        return character
    
    def level_up_character(self, character: Character) -> Dict[str, Any]:
        """Level up a character"""
        old_level = character.level
        result = character.level_up()
        
        return {
            "success": True,
            "old_level": old_level,
            "new_level": character.level,
            "hp_gained": character.max_hp - (character.max_hp - result.get("hp_gain", 0)),
            "message": f"{character.name} leveled up to level {character.level}!"
        }
    
    def add_experience(self, character: Character, amount: int) -> Dict[str, Any]:
        """Add experience to a character"""
        result = character.add_experience(amount)
        
        response = {
            "success": True,
            "experience_gained": amount,
            "total_experience": character.experience,
            "leveled_up": result["leveled_up"],
            "new_level": result["new_level"]
        }
        
        if result["leveled_up"]:
            response["message"] = f"{character.name} gained {amount} XP and leveled up to level {result['new_level']}!"
        else:
            response["message"] = f"{character.name} gained {amount} XP"
        
        return response
    
    # --- Utility Interface ---
    
    def get_character_info(self, character: Character) -> Dict[str, Any]:
        """Get comprehensive character information"""
        return {
            "name": character.name,
            "class": character.character_class,
            "level": character.level,
            "experience": character.experience,
            "experience_to_next": character.experience_to_next_level,
            "stats": character.stats,
            "modifiers": {stat: character.get_modifier(stat) for stat in character.stats},
            "hp": {
                "current": character.current_hp,
                "max": character.max_hp,
                "percentage": (character.current_hp / character.max_hp) * 100
            },
            "armor_class": character.armor_class,
            "proficiency_bonus": character.proficiency_bonus,
            "conditions": character.conditions,
            "inventory": character.inventory,
            "class_features": {
                "spell_slots": character.spell_slots,
                "rage_charges": character.rage_charges,
                "second_wind_available": character.second_wind_available,
                "arcane_recovery_available": character.arcane_recovery_available
            }
        }
    
    def get_available_actions(self, character: Character) -> Dict[str, Any]:
        """Get available actions for a character"""
        actions = {
            "basic": ["attack", "dodge", "help", "hide", "search", "use_object"],
            "movement": ["move", "dash", "disengage"],
            "class_specific": []
        }
        
        # Add class-specific actions
        if character.character_class == "Barbarian" and character.rage_charges > 0:
            actions["class_specific"].append("rage")
        if character.character_class == "Fighter" and character.second_wind_available:
            actions["class_specific"].append("second_wind")
        if character.character_class == "Wizard" and character.arcane_recovery_available:
            actions["class_specific"].append("arcane_recovery")
        if character.character_class == "Rogue":
            actions["class_specific"].append("sneak_attack")
        
        return actions

    # --- Save/Load Game State ---
    def get_game_state(self) -> dict:
        """Gather the full game state as a serializable dict."""
        # This is a stub; expand as new systems are added
        state = {
            "characters": [self._serialize_character(c) for c in getattr(self, 'characters', [])],
            "current_quest": self.current_quest,
            "world": self._serialize_world(getattr(self, 'world', None)),
            "encounter": self._serialize_encounter(getattr(self, 'encounter', None)),
            "session_context": getattr(self, 'session_context', {})
        }
        return state

    def set_game_state(self, state: dict):
        """Restore the full game state from a dict."""
        # This is a stub; expand as new systems are added
        self.characters = [self._deserialize_character(c) for c in state.get("characters", [])]
        self.current_quest = state.get("current_quest")
        self.world = self._deserialize_world(state.get("world"))
        self.encounter = self._deserialize_encounter(state.get("encounter"))
        self.session_context = state.get("session_context", {})

    def save_game(self, filename: str):
        """Save the current game state to a file."""
        state = self.get_game_state()
        save_game_file(filename, state)

    def load_game(self, filename: str):
        """Load game state from a file and restore it."""
        state = load_game_file(filename)
        self.set_game_state(state)

    # --- Serialization helpers (expand as needed) ---
    def _serialize_character(self, character):
        if hasattr(character, '__dict__'):
            return character.__dict__
        return character
    def _deserialize_character(self, data):
        return Character(**data)
    def _serialize_world(self, world):
        if world and hasattr(world, '__dict__'):
            return world.__dict__
        return world
    def _deserialize_world(self, data):
        from .world import WorldState
        if data:
            return WorldState(**data)
        return None
    def _serialize_encounter(self, encounter):
        if encounter and hasattr(encounter, '__dict__'):
            return encounter.__dict__
        return encounter
    def _deserialize_encounter(self, data):
        from .encounters import Encounter
        if data:
            return Encounter(**data)
        return None

    # --- Quest Journal Interface ---
    
    def add_quest(self, quest: Quest) -> str:
        """Add a new quest to the journal"""
        quest_id = self.quest_journal.add_quest(quest)
        self.auto_checkpoint(f"quest_added_{quest_id}")
        return quest_id
    
    def update_quest_progress(self, quest_id: str, progress: str) -> bool:
        """Update progress on a quest"""
        success = self.quest_journal.update_quest_progress(quest_id, progress)
        if success:
            self.auto_checkpoint(f"quest_progress_{quest_id}")
        return success
    
    def complete_quest(self, quest_id: str, outcome: str = "Success") -> bool:
        """Complete a quest"""
        success = self.quest_journal.complete_quest(quest_id, outcome)
        if success:
            self.auto_checkpoint(f"quest_completed_{quest_id}")
        return success
    
    def get_quest_status(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a quest"""
        return self.quest_journal.get_quest_status(quest_id)
    
    def list_active_quests(self) -> List[Dict[str, Any]]:
        """List all active quests"""
        return self.quest_journal.list_active_quests()
    
    def list_completed_quests(self) -> List[Dict[str, Any]]:
        """List all completed quests"""
        return self.quest_journal.list_completed_quests()
    
    def get_quest_summary(self) -> Dict[str, Any]:
        """Get overall quest journal summary"""
        return self.quest_journal.get_quest_summary()
    
    def create_quest_from_generator(self, character: Character, context: Dict = None) -> Optional[str]:
        """Generate a quest and add it to the journal"""
        quest_data = self.generate_quest(character, context)
        if not quest_data.get("success"):
            return None
        
        # Convert quest data to Quest object
        objectives = [
            QuestObjective(description=obj) 
            for obj in quest_data.get("objectives", [])
        ]
        
        quest = Quest(
            id="",
            title=quest_data.get("title", "Generated Quest"),
            description=quest_data.get("description", ""),
            quest_giver=quest_data.get("quest_giver", "Unknown"),
            objectives=objectives,
            rewards=quest_data.get("rewards", {}),
            difficulty=quest_data.get("difficulty", "Medium"),
            quest_type=quest_data.get("type", "Adventure")
        )
        
        return self.add_quest(quest)

    # --- Auto-checkpoint stubs ---
    def auto_checkpoint(self, event: str = ""):
        """Auto-save game state"""
        if self.memory_system:
            self.memory_system.save_checkpoint(event)
    
    # --- AI Content Generation with Narration Style Integration ---
    
    def generate_quest_description(self, quest_data: Dict[str, Any], character: Character = None) -> str:
        """Generate a quest description using the current narration style"""
        style_info = self.dm_style.get_style_info()
        ai_prompt = self.dm_style.get_ai_prompt()
        
        # Base quest description
        base_description = f"{quest_data.get('name', 'Unknown Quest')}: {quest_data.get('description', 'No description available')}"
        
        # Apply narration style
        styled_description = self.dm_style.format_narration(base_description)
        
        # Add style-specific elements
        if style_info.get('name') == 'Epic':
            styled_description = f"**A quest of legendary proportions awaits!** {styled_description}"
        elif style_info.get('name') == 'Gritty':
            styled_description = f"**The harsh reality of adventure calls.** {styled_description}"
        elif style_info.get('name') == 'Comedic':
            styled_description = f"**Another day, another quest!** 😄 {styled_description}"
        elif style_info.get('name') == 'Poetic':
            styled_description = f"**The winds of destiny whisper of a new journey.** 🌙 {styled_description}"
        elif style_info.get('name') == 'Eerie':
            styled_description = f"**Shadows gather around this mysterious task.** {styled_description}"
        elif style_info.get('name') == 'Mystical':
            styled_description = f"**Ancient forces align to present this quest.** ✨ {styled_description}"
        
        return styled_description
    
    def generate_npc_dialogue(self, npc_name: str, npc_role: str, dialogue_type: str = "greeting", 
                             context: Dict[str, Any] = None) -> str:
        """Generate NPC dialogue using the current narration style"""
        style_info = self.dm_style.get_style_info()
        style_phrase = self.dm_style.get_style_phrase()
        
        # Base dialogue templates
        dialogue_templates = {
            "greeting": f"{npc_name} approaches you with a {style_info.get('tone', 'neutral')} expression.",
            "quest_offer": f"{npc_name} looks at you with {style_info.get('tone', 'neutral')} eyes, seeking your aid.",
            "information": f"{npc_name} shares knowledge with a {style_info.get('tone', 'neutral')} demeanor.",
            "farewell": f"{npc_name} bids you farewell with a {style_info.get('tone', 'neutral')} nod."
        }
        
        base_dialogue = dialogue_templates.get(dialogue_type, dialogue_templates["greeting"])
        
        # Apply narration style
        styled_dialogue = self.dm_style.format_narration(base_dialogue)
        
        # Add style-specific dialogue elements
        if style_info.get('name') == 'Epic':
            styled_dialogue = f"**{npc_name} speaks with the weight of destiny:** {styled_dialogue}"
        elif style_info.get('name') == 'Gritty':
            styled_dialogue = f"**{npc_name} speaks with the weariness of experience:** {styled_dialogue}"
        elif style_info.get('name') == 'Comedic':
            styled_dialogue = f"**{npc_name} says with a twinkle in their eye:** {styled_dialogue}"
        elif style_info.get('name') == 'Poetic':
            styled_dialogue = f"**{npc_name} speaks like poetry in motion:** {styled_dialogue}"
        elif style_info.get('name') == 'Eerie':
            styled_dialogue = f"**{npc_name} speaks with an unsettling tone:** {styled_dialogue}"
        elif style_info.get('name') == 'Mystical':
            styled_dialogue = f"**{npc_name} speaks with otherworldly wisdom:** {styled_dialogue}"
        
        return styled_dialogue
    
    def generate_location_description(self, location_name: str, location_type: str, 
                                     features: List[str] = None) -> str:
        """Generate location description using the current narration style"""
        style_info = self.dm_style.get_style_info()
        style_vocabulary = self.dm_style.get_style_vocabulary()
        
        # Base location description
        features = features or []
        feature_text = ", ".join(features) if features else "mysterious"
        base_description = f"You find yourself in {location_name}, a {location_type} that is {feature_text}."
        
        # Apply narration style
        styled_description = self.dm_style.format_narration(base_description)
        
        # Add style-specific location elements
        if style_info.get('name') == 'Epic':
            styled_description = f"**A place of legend unfolds before you:** {styled_description}"
        elif style_info.get('name') == 'Gritty':
            styled_description = f"**The harsh reality of this place is evident:** {styled_description}"
        elif style_info.get('name') == 'Comedic':
            styled_description = f"**Well, this is certainly... interesting:** {styled_description}"
        elif style_info.get('name') == 'Poetic':
            styled_description = f"**The very air seems to dance with stories:** {styled_description}"
        elif style_info.get('name') == 'Eerie':
            styled_description = f"**An unsettling atmosphere pervades this place:** {styled_description}"
        elif style_info.get('name') == 'Mystical':
            styled_description = f"**Ancient magic lingers in the air:** {styled_description}"
        
        return styled_description
    
    def generate_narrative_response(self, player_action: str, context: Dict[str, Any] = None) -> str:
        """Generate a narrative response to player actions using the current narration style"""
        style_info = self.dm_style.get_style_info()
        style_phrase = self.dm_style.get_style_phrase()
        
        # Base response
        base_response = f"As you {player_action}, the world responds accordingly."
        
        # Apply narration style
        styled_response = self.dm_style.format_narration(base_response)
        
        # Add style-specific narrative elements
        if style_info.get('name') == 'Epic':
            styled_response = f"**The forces of destiny align as you {player_action}:** {styled_response}"
        elif style_info.get('name') == 'Gritty':
            styled_response = f"**The harsh consequences of your actions become clear:** {styled_response}"
        elif style_info.get('name') == 'Comedic':
            styled_response = f"**In what can only be described as a 'bold move', you {player_action}:** {styled_response}"
        elif style_info.get('name') == 'Poetic':
            styled_response = f"**Like a leaf caught in autumn's embrace, you {player_action}:** {styled_response}"
        elif style_info.get('name') == 'Eerie':
            styled_response = f"**Shadows seem to whisper as you {player_action}:** {styled_response}"
        elif style_info.get('name') == 'Mystical':
            styled_response = f"**The weave of magic responds to your will as you {player_action}:** {styled_response}"
        
        return styled_response
    
    def generate_combat_description(self, action: str, attacker: str, target: str = None, 
                                   damage: int = None, hit: bool = True) -> str:
        """Generate combat descriptions using the current narration style"""
        style_info = self.dm_style.get_style_info()
        
        # Base combat description
        if hit and damage:
            base_description = f"{attacker} {action} and deals {damage} damage!"
        elif hit:
            base_description = f"{attacker} {action} successfully!"
        else:
            base_description = f"{attacker} {action} but misses!"
        
        # Apply narration style
        styled_description = self.dm_style.format_narration(base_description)
        
        # Add style-specific combat elements
        if style_info.get('name') == 'Epic':
            if hit and damage:
                styled_description = f"**With thunderous might, {attacker} {action} for {damage} damage!**"
            else:
                styled_description = f"**{attacker} {action} with legendary skill!**"
        elif style_info.get('name') == 'Gritty':
            if hit and damage:
                styled_description = f"**Blood and sweat mingle as {attacker} {action} for {damage} damage!**"
            else:
                styled_description = f"**The harsh reality of combat hits home as {attacker} {action}!**"
        elif style_info.get('name') == 'Comedic':
            if hit and damage:
                styled_description = f"**In a move that would make a circus performer proud, {attacker} {action} for {damage} damage!** 😄"
            else:
                styled_description = f"**With the grace of a drunken penguin, {attacker} {action}!** 😄"
        elif style_info.get('name') == 'Poetic':
            if hit and damage:
                styled_description = f"**The moonlight dances upon {attacker}'s blade as they {action} for {damage} damage!** 🌙"
            else:
                styled_description = f"**Time flows like a river as {attacker} {action}!** 🌙"
        elif style_info.get('name') == 'Eerie':
            if hit and damage:
                styled_description = f"**Shadows seem to whisper as {attacker} {action} for {damage} damage!**"
            else:
                styled_description = f"**An unnatural silence falls as {attacker} {action}!**"
        elif style_info.get('name') == 'Mystical':
            if hit and damage:
                styled_description = f"**The weave of magic responds to {attacker}'s will as they {action} for {damage} damage!** ✨"
            else:
                styled_description = f"**Reality itself seems to bend around {attacker} as they {action}!** ✨"
        
        return styled_description
    
    def get_narration_style_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the current narration style"""
        return self.dm_style.get_style_summary()
    
    def change_narration_style(self, new_style: str) -> Dict[str, Any]:
        """Change the narration style and return the new style info"""
        success = self.dm_style.set_style(new_style)
        if success:
            style_info = self.dm_style.get_style_info()
            return {
                "success": True,
                "message": f"Narration style changed to {style_info['name']}",
                "style_info": style_info,
                "example_phrase": self.dm_style.get_style_phrase()
            }
        else:
            return {
                "success": False,
                "message": f"Unknown narration style: {new_style}",
                "available_styles": list(self.dm_style.get_all_styles().keys())
            }

    def store_narrative_embedding(self, text: str, metadata: dict):
        if self.vector_memory and self.vector_memory.is_available():
            self.vector_memory.store_memory(text, metadata)
    def retrieve_similar_memories(self, query: str, top_n: int = 5, filters: dict = None):
        if self.vector_memory and self.vector_memory.is_available():
            return self.vector_memory.retrieve_similar(query, top_n, filters)
        return []
    def decay_vector_memories(self, decay_rate: float = 0.01):
        if self.vector_memory and self.vector_memory.is_available():
            self.vector_memory.decay_memory(decay_rate)
    @property
    def vector_memory_context(self):
        """Get top relevant vector memories for current context pipeline (JSON-compatible)."""
        if self.vector_memory and self.vector_memory.is_available():
            # Example: retrieve last 5 most important memories for this campaign
            return self.vector_memory.retrieve_similar("current session", top_n=5, filters={"campaign_id": self.vector_memory.campaign_id})
        return []

# Global instance for easy access
enhanced_engine = EnhancedNarrativeEngine()
