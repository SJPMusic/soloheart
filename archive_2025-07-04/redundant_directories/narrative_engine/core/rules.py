from typing import Dict, List, Optional, Tuple, Any
from .core import Character
import random
import json
import os

# --- Dice Roll Logic ---
class DiceRoller:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
    
    def roll_dice(self, dice_notation: str) -> Tuple[int, List[int]]:
        """Roll dice in standard notation (e.g., '2d6+3', '1d20')"""
        import re
        
        # Parse dice notation
        pattern = r'(\d+)d(\d+)([+-]\d+)?'
        match = re.match(pattern, dice_notation.lower())
        
        if not match:
            raise ValueError(f"Invalid dice notation: {dice_notation}")
        
        num_dice = int(match.group(1))
        dice_size = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        # Roll the dice
        rolls = [self.rng.randint(1, dice_size) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        return total, rolls
    
    def roll_with_advantage(self, modifier: int = 0) -> Tuple[int, List[int]]:
        """Roll 2d20 and take the higher result"""
        roll1 = self.rng.randint(1, 20) + modifier
        roll2 = self.rng.randint(1, 20) + modifier
        rolls = [roll1 - modifier, roll2 - modifier]
        return max(roll1, roll2), rolls
    
    def roll_with_disadvantage(self, modifier: int = 0) -> Tuple[int, List[int]]:
        """Roll 2d20 and take the lower result"""
        roll1 = self.rng.randint(1, 20) + modifier
        roll2 = self.rng.randint(1, 20) + modifier
        rolls = [roll1 - modifier, roll2 - modifier]
        return min(roll1, roll2), rolls

# --- Conditions ---
CONDITIONS = [
    "blinded", "charmed", "deafened", "frightened", "grappled", "incapacitated",
    "invisible", "paralyzed", "petrified", "poisoned", "prone", "restrained",
    "stunned", "unconscious"
]

# --- Saving Throws ---
def saving_throw(character: Character, stat: str, dc: int, rng=None) -> bool:
    rng = rng or random
    roll = rng.randint(1, 20) + (character.stats.get(stat.upper(), 0) - 10) // 2
    return roll >= dc

# --- Apply Condition ---
def apply_condition(character: Character, condition: str):
    if condition in CONDITIONS:
        character.add_condition(condition)

# --- Remove Condition ---
def remove_condition(character: Character, condition: str):
    character.remove_condition(condition)

# --- Class-Specific Mechanics ---
class ClassMechanics:
    def __init__(self):
        self.class_data = self._load_class_data()
    
    def _load_class_data(self) -> Dict:
        """Load class data from JSON file"""
        # Look for SRD data in the project root srd_data directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_path = os.path.join(project_root, 'srd_data', 'classes.json')
        
        # Fallback to narrative_engine directory if not found
        if not os.path.exists(data_path):
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'srd_data', 'classes.json')
        
        with open(data_path, 'r') as f:
            content = f.read()
            
        # Skip license header if present (lines that don't start with { or [)
        lines = content.split('\n')
        json_start = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('{') or line.startswith('['):
                json_start = i
                break
        
        json_content = '\n'.join(lines[json_start:])
        return json.loads(json_content)
    
    def get_class_features(self, class_name: str) -> List[Dict]:
        """Get features for a specific class"""
        return self.class_data.get('classes', {}).get(class_name, {}).get('features', [])
    
    def calculate_spell_slots(self, class_name: str, level: int) -> Dict[int, int]:
        """Calculate spell slots for spellcasting classes"""
        if class_name == "Wizard":
            # Wizard spell slot progression
            slots = {
                1: 2, 2: 3, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4, 10: 4,
                11: 4, 12: 4, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 4, 19: 4, 20: 4
            }
            return {i: slots.get(i, 0) for i in range(1, min(level + 1, 10))}
        return {}
    
    def apply_rage(self, character: Character) -> Dict[str, Any]:
        """Apply Barbarian rage mechanics"""
        if character.character_class != "Barbarian":
            return {"success": False, "message": "Only Barbarians can rage"}
        
        # Check if rage is available
        if character.rage_charges <= 0:
            return {"success": False, "message": "No rage charges remaining"}
        
        character.rage_charges -= 1
        character.add_condition("raging")
        
        # Rage benefits: +2 damage, resistance to bludgeoning/piercing/slashing
        return {
            "success": True,
            "message": f"{character.name} enters a rage! +2 damage, resistance to B/P/S damage",
            "damage_bonus": 2,
            "resistances": ["bludgeoning", "piercing", "slashing"]
        }
    
    def calculate_sneak_attack_damage(self, character: Character, level: int) -> int:
        """Calculate sneak attack damage for Rogues"""
        if character.character_class != "Rogue":
            return 0
        
        # Sneak attack damage progression: 1d6 at level 1, +1d6 every 2 levels
        sneak_dice = (level + 1) // 2
        return sneak_dice
    
    def use_spell_slot(self, character: Character, spell_level: int) -> bool:
        """Use a spell slot for spellcasting"""
        if not character.spell_slots:
            return False
        
        if spell_level in character.spell_slots and character.spell_slots[spell_level] > 0:
            character.spell_slots[spell_level] -= 1
            return True
        return False
    
    def short_rest_recovery(self, character: Character):
        """Apply short rest recovery benefits"""
        if character.character_class == "Fighter":
            # Second Wind recovery
            if character.second_wind_available:
                dice_roller = DiceRoller()
                recovery, rolls = dice_roller.roll_dice(f"1d10+{character.level}")
                character.current_hp = min(character.current_hp + recovery, character.max_hp)
                character.second_wind_available = False
                return f"Second Wind: {recovery} HP recovered (rolled {rolls})"
        
        elif character.character_class == "Wizard":
            # Arcane Recovery
            if character.arcane_recovery_available:
                # Recover spell slots equal to half wizard level (rounded up)
                recovery_slots = (character.level + 1) // 2
                # Can't recover slots higher than 5th level
                max_recovery_level = min(5, character.level // 2 + 1)
                
                for level in range(max_recovery_level, 0, -1):
                    if recovery_slots > 0 and level in character.spell_slots:
                        recovered = min(recovery_slots, character.spell_slots.get(level, 0))
                        character.spell_slots[level] += recovered
                        recovery_slots -= recovered
                
                character.arcane_recovery_available = False
                return f"Arcane Recovery: Recovered spell slots"
        
        return "No short rest features available"

# --- DM Narration Styles ---
class DMNarrationStyle:
    def __init__(self):
        self.styles = {
            "epic": {
                "name": "Epic",
                "description": "Grand, heroic, and cinematic language like a high fantasy novel",
                "tone": "heroic, dramatic, grandiose, legendary",
                "ai_prompt": "Use grand, heroic language with dramatic flair. Employ epic metaphors, emphasize the significance of every action, and create a sense of legendary scale. Use words like 'thunderous', 'legendary', 'mighty', 'epic', 'heroic'.",
                "phrases": [
                    "With thunderous might, you...",
                    "The very air crackles with power as...",
                    "In a display of legendary skill...",
                    "The gods themselves seem to hold their breath as...",
                    "Your actions echo through the annals of history as...",
                    "The forces of destiny align as you..."
                ],
                "vocabulary": ["legendary", "epic", "heroic", "mighty", "thunderous", "grand", "magnificent", "awe-inspiring", "destined", "fateful"]
            },
            "gritty": {
                "name": "Gritty",
                "description": "Harsh, grounded, realistic tones with focus on consequences and survival",
                "tone": "realistic, visceral, intense, harsh, grounded",
                "ai_prompt": "Use harsh, realistic language that emphasizes the brutal nature of adventure. Focus on pain, consequences, and the harsh realities of combat and survival. Use visceral descriptions and emphasize the cost of actions.",
                "phrases": [
                    "Blood and sweat mingle as you...",
                    "Every muscle screams in protest as...",
                    "The harsh reality of combat hits home as...",
                    "Pain and determination fuel your actions as...",
                    "The cold bite of steel reminds you that...",
                    "Survival instincts kick in as you..."
                ],
                "vocabulary": ["brutal", "harsh", "visceral", "painful", "realistic", "grim", "bleak", "survival", "consequences", "cost"]
            },
            "comedic": {
                "name": "Comedic",
                "description": "Lighthearted, ironic, or playful narration that uses humor or sarcasm",
                "tone": "funny, light-hearted, playful, ironic, sarcastic",
                "ai_prompt": "Use lighthearted, humorous language with wit and irony. Include clever wordplay, situational humor, and a playful tone. Don't be afraid to break the fourth wall or add meta-commentary.",
                "phrases": [
                    "In a move that would make a circus performer proud...",
                    "The laws of physics take a coffee break as...",
                    "With the grace of a drunken penguin, you...",
                    "Chaos theory gets a new data point as...",
                    "The universe clearly didn't get the memo as...",
                    "In what can only be described as a 'bold strategy'..."
                ],
                "vocabulary": ["hilarious", "ridiculous", "absurd", "comical", "witty", "clever", "playful", "ironic", "sarcastic", "amusing"]
            },
            "poetic": {
                "name": "Poetic",
                "description": "Lyrical, evocative language with metaphor and rhythm",
                "tone": "lyrical, evocative, metaphorical, rhythmic, beautiful",
                "ai_prompt": "Use lyrical, poetic language with rich metaphors and evocative imagery. Create rhythm and flow in your descriptions. Use beautiful, flowing language that paints vivid mental pictures.",
                "phrases": [
                    "Like a leaf caught in autumn's embrace, you...",
                    "The moonlight dances upon your blade as...",
                    "Time flows like a river as you...",
                    "The wind whispers ancient secrets as...",
                    "Your spirit soars like an eagle as...",
                    "The world holds its breath in wonder as..."
                ],
                "vocabulary": ["lyrical", "evocative", "metaphorical", "rhythmic", "flowing", "beautiful", "graceful", "ethereal", "mystical", "enchanting"]
            },
            "neutral": {
                "name": "Neutral",
                "description": "A balanced, default storytelling voice that isn't strongly stylized",
                "tone": "balanced, clear, straightforward, professional",
                "ai_prompt": "Use clear, straightforward language that focuses on clarity and information. Maintain a professional, balanced tone without strong stylistic flourishes. Be descriptive but not overly dramatic.",
                "phrases": [
                    "You carefully...",
                    "With practiced skill, you...",
                    "The situation requires you to...",
                    "Your training guides you as...",
                    "The circumstances demand that you...",
                    "You find yourself..."
                ],
                "vocabulary": ["carefully", "skillfully", "methodically", "precisely", "effectively", "efficiently", "professionally", "competently", "thoroughly", "systematically"]
            },
            "eerie": {
                "name": "Eerie",
                "description": "Dark, atmospheric, and unsettling",
                "tone": "dark, mysterious, unsettling, atmospheric",
                "ai_prompt": "Use dark, atmospheric language that creates an unsettling mood. Emphasize shadows, mystery, and the unknown. Create a sense of dread and foreboding through your descriptions.",
                "phrases": [
                    "Shadows seem to whisper as you...",
                    "An unnatural silence falls as...",
                    "The air grows thick with dread while...",
                    "Something ancient and malevolent stirs as...",
                    "The darkness itself seems to watch as...",
                    "A chill runs down your spine as..."
                ],
                "vocabulary": ["dark", "mysterious", "unsettling", "eerie", "foreboding", "malevolent", "ancient", "shadowy", "ominous", "haunting"]
            },
            "mystical": {
                "name": "Mystical",
                "description": "Ethereal, magical, and otherworldly",
                "tone": "ethereal, magical, otherworldly, mystical",
                "ai_prompt": "Use ethereal, magical language that emphasizes the mystical and otherworldly aspects. Focus on magic, ancient forces, and the supernatural. Create a sense of wonder and the unknown.",
                "phrases": [
                    "The weave of magic responds to your will as...",
                    "Reality itself seems to bend around you as...",
                    "Ancient forces stir in response to...",
                    "The boundary between worlds grows thin as...",
                    "Mystical energies flow through you as...",
                    "The fabric of existence trembles as..."
                ],
                "vocabulary": ["ethereal", "magical", "mystical", "otherworldly", "ancient", "supernatural", "enchanting", "mysterious", "divine", "transcendent"]
            }
        }
        self.current_style = "neutral"
        self.style_history = []
    
    def set_style(self, style_name: str) -> bool:
        """Set the current narration style"""
        if style_name in self.styles:
            self.style_history.append(self.current_style)
            self.current_style = style_name
            return True
        return False
    
    def get_style_info(self, style_name: str = None) -> Dict:
        """Get information about a narration style"""
        style = style_name or self.current_style
        return self.styles.get(style, {})
    
    def get_all_styles(self) -> Dict[str, Dict]:
        """Get all available styles"""
        return self.styles.copy()
    
    def get_current_style(self) -> str:
        """Get the current style name"""
        return self.current_style
    
    def get_ai_prompt(self, style_name: str = None) -> str:
        """Get the AI prompt for a specific style"""
        style = style_name or self.current_style
        style_info = self.styles.get(style, {})
        return style_info.get("ai_prompt", "")
    
    def format_narration(self, base_text: str, style_name: str = None) -> str:
        """Format narration text according to the current style"""
        style = style_name or self.current_style
        style_info = self.styles.get(style, {})
        
        if style == "epic":
            return f"**{base_text}**"
        elif style == "eerie":
            return f"*{base_text}*"
        elif style == "comedic":
            return f"😄 {base_text}"
        elif style == "gritty":
            return f"💀 {base_text}"
        elif style == "mystical":
            return f"✨ {base_text}"
        elif style == "poetic":
            return f"🌙 {base_text}"
        elif style == "neutral":
            return base_text
        
        return base_text
    
    def get_style_phrase(self, style_name: str = None) -> str:
        """Get a random phrase for the current style"""
        style = style_name or self.current_style
        style_info = self.styles.get(style, {})
        phrases = style_info.get("phrases", [])
        
        if phrases:
            return random.choice(phrases)
        return ""
    
    def get_style_vocabulary(self, style_name: str = None) -> List[str]:
        """Get vocabulary suggestions for the current style"""
        style = style_name or self.current_style
        style_info = self.styles.get(style, {})
        return style_info.get("vocabulary", [])
    
    def get_style_summary(self) -> Dict[str, Any]:
        """Get a summary of the current style"""
        style_info = self.get_style_info()
        return {
            "current_style": self.current_style,
            "name": style_info.get("name", ""),
            "description": style_info.get("description", ""),
            "tone": style_info.get("tone", ""),
            "ai_prompt": style_info.get("ai_prompt", ""),
            "available_styles": list(self.styles.keys()),
            "style_history": self.style_history[-5:]  # Last 5 styles
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "current_style": self.current_style,
            "style_history": self.style_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DMNarrationStyle':
        """Create from dictionary (deserialization)"""
        instance = cls()
        instance.current_style = data.get("current_style", "neutral")
        instance.style_history = data.get("style_history", [])
        return instance

# --- Quest Generation ---
class QuestGenerator:
    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self.quest_templates = {
            "rescue": {
                "name": "Rescue Mission",
                "description": "Someone important has been captured and needs rescue",
                "objectives": ["Locate the captive", "Defeat the captors", "Escort to safety"],
                "difficulty_modifiers": ["hostile environment", "time pressure", "stealth required"]
            },
            "investigation": {
                "name": "Mystery Investigation",
                "description": "Uncover the truth behind mysterious events",
                "objectives": ["Gather clues", "Interview witnesses", "Solve the mystery"],
                "difficulty_modifiers": ["false leads", "dangerous witnesses", "time-sensitive"]
            },
            "retrieval": {
                "name": "Item Retrieval",
                "description": "Recover a valuable or important item",
                "objectives": ["Find the item", "Overcome obstacles", "Return safely"],
                "difficulty_modifiers": ["heavily guarded", "cursed item", "competing parties"]
            },
            "escort": {
                "name": "Escort Mission",
                "description": "Protect someone or something during travel",
                "objectives": ["Protect the target", "Navigate safely", "Reach destination"],
                "difficulty_modifiers": ["fragile cargo", "multiple threats", "time pressure"]
            },
            "elimination": {
                "name": "Target Elimination",
                "description": "Defeat a specific enemy or group",
                "objectives": ["Locate the target", "Engage in combat", "Confirm elimination"],
                "difficulty_modifiers": ["powerful enemy", "reinforcements", "escape routes"]
            }
        }
    
    def generate_quest(self, character: Character, context: Dict = None) -> Dict:
        """Generate a dynamic quest based on character and context"""
        import random
        
        # Choose quest type
        quest_type = random.choice(list(self.quest_templates.keys()))
        template = self.quest_templates[quest_type]
        
        # Generate quest details
        quest = {
            "type": quest_type,
            "name": template["name"],
            "description": template["description"],
            "objectives": template["objectives"].copy(),
            "difficulty": self._calculate_difficulty(character, context),
            "rewards": self._generate_rewards(character),
            "context_hooks": self._generate_context_hooks(character, context)
        }
        
        # Add difficulty modifiers
        if random.random() < 0.7:  # 70% chance of having modifiers
            num_modifiers = random.randint(1, 2)
            quest["difficulty_modifiers"] = random.sample(template["difficulty_modifiers"], 
                                                        min(num_modifiers, len(template["difficulty_modifiers"])))
        
        return quest
    
    def _calculate_difficulty(self, character: Character, context: Dict = None) -> str:
        """Calculate quest difficulty based on character level and context"""
        level = character.level
        
        if level <= 3:
            base_difficulty = "easy"
        elif level <= 7:
            base_difficulty = "medium"
        elif level <= 12:
            base_difficulty = "hard"
        else:
            base_difficulty = "epic"
        
        # Adjust based on context
        if context and context.get("danger_level") == "high":
            if base_difficulty == "easy":
                base_difficulty = "medium"
            elif base_difficulty == "medium":
                base_difficulty = "hard"
            elif base_difficulty == "hard":
                base_difficulty = "epic"
        
        return base_difficulty
    
    def _generate_rewards(self, character: Character) -> Dict:
        """Generate appropriate rewards for the quest"""
        level = character.level
        
        # Base rewards
        gold_reward = level * random.randint(10, 25)
        xp_reward = level * random.randint(50, 100)
        
        rewards = {
            "gold": gold_reward,
            "experience": xp_reward,
            "items": []
        }
        
        # Add items based on character class
        if character.character_class == "Fighter":
            rewards["items"].append("Potion of Healing")
        elif character.character_class == "Rogue":
            rewards["items"].append("Thieves' Tools")
        elif character.character_class == "Wizard":
            rewards["items"].append("Spell Scroll")
        
        return rewards
    
    def _generate_context_hooks(self, character: Character, context: Dict = None) -> List[str]:
        """Generate context hooks based on character history and current situation"""
        hooks = []
        
        # Add hooks based on character class
        if character.character_class == "Fighter":
            hooks.append("Your military training makes this mission familiar")
        elif character.character_class == "Rogue":
            hooks.append("Your street connections provide valuable information")
        elif character.character_class == "Wizard":
            hooks.append("Your arcane knowledge reveals hidden magical threats")
        
        # Add hooks based on context
        if context:
            if context.get("location") == "urban":
                hooks.append("The city's criminal underworld is involved")
            elif context.get("location") == "wilderness":
                hooks.append("Nature itself seems to oppose your mission")
            elif context.get("time") == "night":
                hooks.append("Darkness provides both cover and danger")
        
        return hooks

# Global instances
dice_roller = DiceRoller()
class_mechanics = ClassMechanics()
dm_style = DMNarrationStyle()
quest_generator = QuestGenerator()
