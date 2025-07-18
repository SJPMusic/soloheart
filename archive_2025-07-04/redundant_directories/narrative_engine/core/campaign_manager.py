"""
Campaign Manager for Structured Game Flow

This module manages the overall game flow including:
- New campaign creation
- Character creation (step-by-step or vibe-based)
- Backstory integration
- Campaign launching
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os
from .core import Character
from .engine_interface import EnhancedNarrativeEngine
from .quest_journal import Quest, QuestObjective
from .conversational_parser import ConversationalParser


@dataclass
class Campaign:
    """Represents a DnD campaign with metadata and state."""
    id: str
    name: str
    created_date: datetime
    last_played: datetime = None
    character: Character = None
    backstory: str = ""
    campaign_state: Dict[str, Any] = None
    settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.campaign_state is None:
            self.campaign_state = {}
        if self.settings is None:
            self.settings = {
                "difficulty": "Medium",
                "narration_style": "Descriptive",
                "auto_save": True,
                "quest_frequency": "Normal"
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert campaign to dictionary for serialization."""
        campaign_dict = asdict(self)
        # Convert datetime objects to ISO strings
        if self.created_date:
            campaign_dict['created_date'] = self.created_date.isoformat()
        if self.last_played:
            campaign_dict['last_played'] = self.last_played.isoformat()
        return campaign_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Campaign':
        """Create campaign from dictionary (deserialization)."""
        # Convert ISO strings back to datetime objects
        if 'created_date' in data and data['created_date']:
            data['created_date'] = datetime.fromisoformat(data['created_date'])
        if 'last_played' in data and data['last_played']:
            data['last_played'] = datetime.fromisoformat(data['last_played'])
        
        # Reconstruct character if present
        if 'character' in data and data['character']:
            data['character'] = Character(**data['character'])
        
        return cls(**data)


class CharacterCreator:
    """Handles character creation with step-by-step or vibe-based options."""
    
    def __init__(self, engine: EnhancedNarrativeEngine):
        self.engine = engine
        self.available_classes = ["Fighter", "Wizard", "Rogue", "Cleric", "Barbarian", "Bard", "Druid", "Monk", "Paladin", "Ranger", "Sorcerer", "Warlock"]
    
    def create_character_step_by_step(self) -> Character:
        """Create a character following DnD 5E rules step by step."""
        print("\n🎭 STEP-BY-STEP CHARACTER CREATION")
        print("=" * 50)
        
        # Step 1: Basic Information
        print("\n📝 Step 1: Basic Information")
        name = input("Enter character name: ").strip()
        if not name:
            name = "Adventurer"
        
        print(f"\nAvailable classes: {', '.join(self.available_classes)}")
        character_class = input("Choose character class: ").strip().title()
        if character_class not in self.available_classes:
            print(f"Invalid class. Using Fighter as default.")
            character_class = "Fighter"
        
        # Step 2: Ability Scores (simplified - in full DnD you'd roll 4d6 drop lowest)
        print("\n📊 Step 2: Ability Scores")
        print("You can either:")
        print("1. Use standard array (15, 14, 13, 12, 10, 8)")
        print("2. Roll randomly")
        print("3. Use point buy (27 points)")
        
        choice = input("Choose method (1-3): ").strip()
        
        if choice == "1":
            stats = self._standard_array()
        elif choice == "2":
            stats = self._roll_random_stats()
        else:
            stats = self._point_buy()
        
        # Step 3: Assign stats to abilities
        print("\n🎯 Step 3: Assign Ability Scores")
        print(f"Your scores: {stats}")
        print("Assign these scores to: STR, DEX, CON, INT, WIS, CHA")
        
        abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        assigned_stats = {}
        
        for ability in abilities:
            while True:
                try:
                    score = int(input(f"Assign score to {ability}: "))
                    if score in stats:
                        assigned_stats[ability] = score
                        stats.remove(score)
                        break
                    else:
                        print(f"Score {score} not available. Available: {stats}")
                except ValueError:
                    print("Please enter a valid number.")
        
        # Step 4: Background and personality
        print("\n📖 Step 4: Background")
        background = input("Describe your character's background (optional): ").strip()
        
        # Create character
        character = Character(
            name=name,
            character_class=character_class,
            level=1,
            stats=assigned_stats
        )
        
        print(f"\n✅ Character created: {character.name} the {character.character_class}")
        print(f"   Level: {character.level}")
        print(f"   HP: {character.current_hp}/{character.max_hp}")
        print(f"   Stats: {assigned_stats}")
        
        return character
    
    def create_character_vibe_based(self, vibe_description: str) -> Character:
        """Create a character based on a vibe description."""
        print("\n🎭 VIBE-BASED CHARACTER CREATION")
        print("=" * 50)
        print(f"Vibe: {vibe_description}")
        
        # Analyze the vibe to determine character traits
        character_traits = self._analyze_vibe(vibe_description)
        
        # Generate character based on traits
        name = character_traits.get('name', 'Adventurer')
        character_class = character_traits.get('class', 'Fighter')
        stats = character_traits.get('stats', self._roll_random_stats())
        
        # Create character
        character = Character(
            name=name,
            character_class=character_class,
            level=1,
            stats=stats
        )
        
        print(f"\n✅ Character created based on vibe: {character.name} the {character.character_class}")
        print(f"   Level: {character.level}")
        print(f"   HP: {character.current_hp}/{character.max_hp}")
        print(f"   Stats: {stats}")
        print(f"   Traits: {character_traits.get('traits', [])}")
        
        return character
    
    def _standard_array(self) -> List[int]:
        """Return standard array of ability scores."""
        return [15, 14, 13, 12, 10, 8]
    
    def _roll_random_stats(self) -> List[int]:
        """Roll random ability scores (4d6 drop lowest)."""
        import random
        stats = []
        for _ in range(6):
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.sort(reverse=True)
            stats.append(sum(rolls[:3]))  # Drop lowest
        return stats
    
    def _point_buy(self) -> List[int]:
        """Generate stats using point buy system."""
        # Simplified point buy - in full DnD this is more complex
        return [15, 14, 13, 12, 10, 8]
    
    def _analyze_vibe(self, vibe_description: str) -> Dict[str, Any]:
        """Analyze vibe description to determine character traits."""
        vibe_lower = vibe_description.lower()
        
        # Simple keyword analysis
        traits = []
        stats = self._roll_random_stats()
        
        # Class determination
        if any(word in vibe_lower for word in ['magic', 'spell', 'wizard', 'arcane']):
            character_class = "Wizard"
            traits.extend(['scholarly', 'intellectual'])
        elif any(word in vibe_lower for word in ['stealth', 'sneak', 'thief', 'rogue']):
            character_class = "Rogue"
            traits.extend(['stealthy', 'agile'])
        elif any(word in vibe_lower for word in ['rage', 'barbarian', 'fury', 'wild']):
            character_class = "Barbarian"
            traits.extend(['fierce', 'strong'])
        elif any(word in vibe_lower for word in ['holy', 'divine', 'cleric', 'heal']):
            character_class = "Cleric"
            traits.extend(['devout', 'wise'])
        else:
            character_class = "Fighter"
            traits.extend(['brave', 'skilled'])
        
        # Name generation
        names = {
            "Wizard": ["Merlin", "Gandalf", "Zara", "Eldrin"],
            "Rogue": ["Shadow", "Raven", "Kestrel", "Whisper"],
            "Barbarian": ["Thorgar", "Ragnar", "Valka", "Storm"],
            "Cleric": ["Aria", "Theo", "Luna", "Sol"],
            "Fighter": ["Aric", "Valen", "Sara", "Kael"]
        }
        
        name = names.get(character_class, ["Adventurer"])[0]
        
        return {
            'name': name,
            'class': character_class,
            'stats': stats,
            'traits': traits
        }


class CampaignManager:
    """Manages campaign creation, loading, and game flow."""
    
    def __init__(self, save_directory: str = "campaigns"):
        self.save_directory = save_directory
        self.engine = EnhancedNarrativeEngine()
        self.character_creator = CharacterCreator(self.engine)
        self.conversational_parser = ConversationalParser(self.engine.dm_style)
        self.current_campaign = None
        
        # Ensure save directory exists
        os.makedirs(save_directory, exist_ok=True)
    
    def start_new_campaign(self) -> Campaign:
        """Start a new campaign with character creation."""
        print("\n🎲 STARTING NEW CAMPAIGN")
        print("=" * 50)
        
        # Get campaign name
        campaign_name = input("Enter campaign name: ").strip()
        if not campaign_name:
            campaign_name = f"Campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Character creation choice
        print("\n🎭 CHARACTER CREATION")
        print("Choose your character creation method:")
        print("1. Step-by-step (follow DnD 5E rules)")
        print("2. Vibe-based (describe your character concept)")
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "2":
            print("\n💭 Describe your character concept:")
            print("Examples:")
            print("- 'A mysterious wizard who studies ancient magic'")
            print("- 'A stealthy rogue who grew up on the streets'")
            print("- 'A fierce barbarian from the northern tribes'")
            
            vibe_description = input("Describe your character: ").strip()
            if not vibe_description:
                vibe_description = "A brave adventurer seeking glory"
            
            character = self.character_creator.create_character_vibe_based(vibe_description)
        else:
            character = self.character_creator.create_character_step_by_step()
        
        # Backstory creation
        print("\n📖 CHARACTER BACKSTORY")
        print("Describe your character's backstory. This will be used to launch your campaign.")
        print("Include details like:")
        print("- Where they're from")
        print("- What motivates them")
        print("- Any important events in their past")
        print("- Their current situation")
        
        backstory = input("Enter your character's backstory: ").strip()
        if not backstory:
            backstory = f"{character.name} is a {character.character_class} seeking adventure and glory in the world."
        
        # Create campaign
        campaign = Campaign(
            id=f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=campaign_name,
            created_date=datetime.now(),
            character=character,
            backstory=backstory
        )
        
        self.current_campaign = campaign
        
        # Save campaign
        self.save_campaign(campaign)
        
        # Launch campaign
        self.launch_campaign(campaign)
        
        return campaign
    
    def load_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Load an existing campaign."""
        campaign_file = os.path.join(self.save_directory, f"{campaign_id}.json")
        
        if not os.path.exists(campaign_file):
            print(f"❌ Campaign {campaign_id} not found.")
            return None
        
        try:
            with open(campaign_file, 'r') as f:
                campaign_data = json.load(f)
            
            campaign = Campaign.from_dict(campaign_data)
            self.current_campaign = campaign
            
            # Restore narration style
            narration_style = campaign.settings.get("narration_style", "neutral")
            self.engine.dm_style.set_style(narration_style)
            
            print(f"✅ Loaded campaign: {campaign.name}")
            print(f"   Character: {campaign.character.name} the {campaign.character.character_class}")
            print(f"   Level: {campaign.character.level}")
            print(f"   Narration Style: {self.engine.dm_style.get_style_info()['name']}")
            print(f"   Last played: {campaign.last_played}")
            
            return campaign
        except Exception as e:
            print(f"❌ Error loading campaign: {e}")
            return None
    
    def list_campaigns(self) -> List[Dict[str, Any]]:
        """List all available campaigns."""
        campaigns = []
        
        for filename in os.listdir(self.save_directory):
            if filename.endswith('.json'):
                campaign_id = filename[:-5]  # Remove .json extension
                campaign_file = os.path.join(self.save_directory, filename)
                
                try:
                    with open(campaign_file, 'r') as f:
                        campaign_data = json.load(f)
                    
                    campaigns.append({
                        'id': campaign_id,
                        'name': campaign_data.get('name', 'Unknown'),
                        'created_date': campaign_data.get('created_date', ''),
                        'last_played': campaign_data.get('last_played', ''),
                        'character_name': campaign_data.get('character', {}).get('name', 'Unknown'),
                        'character_class': campaign_data.get('character', {}).get('character_class', 'Unknown')
                    })
                except Exception as e:
                    print(f"Warning: Could not read campaign file {filename}: {e}")
        
        return campaigns
    
    def save_campaign(self, campaign: Campaign):
        """Save a campaign to disk."""
        campaign.last_played = datetime.now()
        campaign_file = os.path.join(self.save_directory, f"{campaign.id}.json")
        
        try:
            with open(campaign_file, 'w') as f:
                json.dump(campaign.to_dict(), f, indent=2)
            print(f"✅ Campaign saved: {campaign.name}")
        except Exception as e:
            print(f"❌ Error saving campaign: {e}")
    
    def launch_campaign(self, campaign: Campaign):
        """Launch a campaign and begin the adventure."""
        print("\n🚀 LAUNCHING CAMPAIGN")
        print("=" * 50)
        print(f"Campaign: {campaign.name}")
        print(f"Character: {campaign.character.name} the {campaign.character.character_class}")
        print(f"Level: {campaign.character.level}")
        
        print("\n📖 YOUR STORY BEGINS...")
        print("-" * 30)
        
        # Use backstory to generate initial quest
        print(f"Based on your backstory: {campaign.backstory}")
        print("\nThe DM considers your background and begins to weave your tale...")
        
        # Generate initial quest based on backstory
        context = {
            "character_backstory": campaign.backstory,
            "character_level": campaign.character.level,
            "character_class": campaign.character.character_class,
            "campaign_name": campaign.name
        }
        
        quest_id = self.engine.create_quest_from_generator(campaign.character, context)
        
        if quest_id:
            quest_status = self.engine.get_quest_status(quest_id)
            print(f"\n🎯 Your first quest: {quest_status['title']}")
            print(f"   {quest_status['description']}")
            print(f"   Quest Giver: {quest_status.get('quest_giver', 'Unknown')}")
            print(f"   Objectives:")
            for i, obj in enumerate(quest_status['objectives'], 1):
                print(f"     {i}. {obj['description']}")
        
        print("\n🎲 Your adventure begins! The world awaits your choices...")
        print("\nCommands you can use:")
        print("- 'quests' - View your quest journal")
        print("- 'character' - View character sheet")
        print("- 'roll [dice]' - Roll dice (e.g., 'roll 1d20')")
        print("- 'save' - Save your progress")
        print("- 'quit' - Exit the game")
        print("\n🎭 You can change narration style naturally:")
        print("- 'Make it more epic' or 'That was too boring'")
        print("- 'I want it grittier' or 'Make it darker'")
        print("- 'Can you be funnier?' or 'Make it more entertaining'")
        print("- 'What styles can you use?' to see all options")
    
    def run_game_loop(self):
        """Main game loop for the campaign."""
        if not self.current_campaign:
            print("❌ No active campaign. Please start or load a campaign first.")
            return
        
        print(f"\n🎮 GAME LOOP - {self.current_campaign.name}")
        print("Type 'help' for available commands.")
        
        while True:
            try:
                command = input(f"\n{self.current_campaign.character.name}> ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    print("💾 Saving before exit...")
                    self.save_campaign(self.current_campaign)
                    print("👋 Thanks for playing!")
                    break
                
                elif command == 'help':
                    self._show_help()
                
                elif command == 'quests':
                    self._show_quests()
                
                elif command == 'character':
                    self._show_character()
                
                elif command.startswith('roll '):
                    dice_notation = command[5:].strip()
                    self._roll_dice(dice_notation)
                
                elif command == 'save':
                    self.save_campaign(self.current_campaign)
                
                elif command == 'status':
                    self._show_status()
                
                else:
                    # Check for conversational style switching
                    parsed_input = self.conversational_parser.parse_input(command)
                    
                    if parsed_input["type"] == "style_discovery":
                        print(f"\n🎭 {self.conversational_parser.generate_style_discovery_response()}")
                    
                    elif parsed_input["type"] == "style_change":
                        old_style = self.engine.dm_style.get_current_style()
                        new_style = parsed_input["style"]
                        
                        # Change the style
                        self.engine.dm_style.set_style(new_style)
                        
                        # Generate confirmation in the new style
                        confirmation = self.conversational_parser.generate_style_change_confirmation(new_style, old_style)
                        print(f"\n🎭 {confirmation}")
                        
                        # Save the campaign with the new style
                        self.current_campaign.settings["narration_style"] = new_style
                        self.save_campaign(self.current_campaign)
                    
                    elif parsed_input["type"] == "style_inference":
                        old_style = self.engine.dm_style.get_current_style()
                        new_style = parsed_input["style"]
                        
                        # Change the style
                        self.engine.dm_style.set_style(new_style)
                        
                        # Generate confirmation in the new style
                        confirmation = self.conversational_parser.generate_style_change_confirmation(new_style, old_style)
                        print(f"\n🎭 {confirmation}")
                        
                        # Save the campaign with the new style
                        self.current_campaign.settings["narration_style"] = new_style
                        self.save_campaign(self.current_campaign)
                    
                    else:
                        # Regular game input - pass to AI DM or handle normally
                        print("❓ Unknown command. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\n💾 Saving before exit...")
                self.save_campaign(self.current_campaign)
                print("👋 Thanks for playing!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _show_help(self):
        """Show available commands."""
        print("\n📚 AVAILABLE COMMANDS")
        print("-" * 30)
        print("quests          - View your quest journal")
        print("character       - View character sheet")
        print("roll [dice]     - Roll dice (e.g., 'roll 1d20')")
        print("save            - Save your progress")
        print("status          - Show campaign status")
        print("quit/exit       - Exit the game")
        print("\n🎭 NARRATION STYLE")
        print("You can change the storytelling style naturally:")
        print("- 'Make it more epic'")
        print("- 'I want it grittier'")
        print("- 'Can you be funnier?'")
        print("- 'What styles can you use?'")
        print("- 'That was too boring' (automatically switches to epic)")
        print("- 'Make it more mysterious' (automatically switches to eerie)")
    
    def _show_quests(self):
        """Show quest journal."""
        active_quests = self.engine.list_active_quests()
        completed_quests = self.engine.list_completed_quests()
        
        print(f"\n📋 QUEST JOURNAL")
        print(f"Active Quests: {len(active_quests)}")
        for quest in active_quests:
            print(f"  - {quest['title']} ({quest['completion_percentage']:.1f}% complete)")
        
        print(f"\nCompleted Quests: {len(completed_quests)}")
        for quest in completed_quests:
            print(f"  - {quest['title']}")
    
    def _show_character(self):
        """Show character sheet."""
        char_info = self.engine.get_character_info(self.current_campaign.character)
        
        print(f"\n🎭 CHARACTER SHEET")
        print(f"Name: {char_info['name']}")
        print(f"Class: {char_info['class']}")
        print(f"Level: {char_info['level']}")
        print(f"HP: {char_info['hp']['current']}/{char_info['hp']['max']}")
        print(f"Experience: {char_info['experience']}/{char_info['experience_to_next']}")
        
        print(f"\nAbility Scores:")
        for stat, value in char_info['stats'].items():
            modifier = char_info['modifiers'][stat]
            print(f"  {stat}: {value} ({modifier:+d})")
    
    def _roll_dice(self, dice_notation: str):
        """Roll dice and show results."""
        result = self.engine.roll_dice(dice_notation)
        if result['success']:
            print(f"🎲 {result['formatted']}")
        else:
            print(f"❌ {result['error']}")
    
    def _show_status(self):
        """Show current game status."""
        print(f"\n📊 GAME STATUS")
        print(f"Campaign: {self.current_campaign.name}")
        print(f"Character: {self.current_campaign.character.name}")
        print(f"Level: {self.current_campaign.character.level}")
        
        summary = self.engine.get_quest_summary()
        print(f"Quests: {summary['active_count']} active, {summary['completed_count']} completed")
    
    def _change_narration_style(self):
        """Change the narration style."""
        print("\n🎭 CHANGE NARRATION STYLE")
        print("=" * 50)
        
        # Get available styles from the engine
        dm_style = self.engine.dm_style
        all_styles = dm_style.get_all_styles()
        
        print("\nAvailable styles:")
        for i, (style_key, style_info) in enumerate(all_styles.items(), 1):
            print(f"  {i}. {style_info['name']} - {style_info['description']}")
        
        while True:
            try:
                choice = input(f"\nEnter style number (1-{len(all_styles)}): ").strip()
                style_index = int(choice) - 1
                
                if 0 <= style_index < len(all_styles):
                    style_keys = list(all_styles.keys())
                    selected_style = style_keys[style_index]
                    dm_style.set_style(selected_style)
                    
                    style_info = all_styles[selected_style]
                    print(f"\n✅ Selected: {style_info['name']}")
                    print(f"   Tone: {style_info['tone']}")
                    print(f"   Example phrase: {dm_style.get_style_phrase()}")
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(all_styles)}")
            except ValueError:
                print("❌ Please enter a valid number") 