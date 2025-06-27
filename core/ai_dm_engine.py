"""
AI Dungeon Master Engine for Solo DnD 5E Game
=============================================

This module implements the core AI DM functionality that orchestrates the entire solo DnD experience.
The AI DM generates campaigns, manages story progression, handles NPC interactions, and adapts difficulty.
"""

import json
import datetime
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from .memory_system import CampaignMemorySystem
from .character_manager import Character

class GameState(Enum):
    """Current game state"""
    CHARACTER_CREATION = "character_creation"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    SOCIAL = "social"
    REST = "rest"
    SHOPPING = "shopping"
    CAMPING = "camping"

class EncounterType(Enum):
    """Types of encounters"""
    COMBAT = "combat"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    PUZZLE = "puzzle"
    TRAP = "trap"
    SHOPPING = "shopping"
    REST = "rest"

class DifficultyLevel(Enum):
    """Difficulty levels for encounters"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    DEADLY = "deadly"

@dataclass
class CampaignState:
    """Current campaign state"""
    campaign_id: str
    player_character: Character
    current_location: str
    current_quest: Optional[str]
    game_state: GameState
    session_number: int
    total_sessions: int
    current_encounter: Optional[str]
    npcs_met: List[str]
    locations_visited: List[str]
    items_found: List[str]
    quests_completed: List[str]
    xp_gained: int
    gold_gained: int
    difficulty_adjustment: float  # Multiplier for encounter difficulty
    player_skill_assessment: Dict[str, float]  # Skills and their ratings
    last_updated: datetime.datetime

@dataclass
class Encounter:
    """Encounter definition"""
    encounter_id: str
    encounter_type: EncounterType
    title: str
    description: str
    difficulty: DifficultyLevel
    enemies: List[Dict[str, Any]]
    npcs: List[Dict[str, Any]]
    environment: Dict[str, Any]
    rewards: Dict[str, Any]
    requirements: Dict[str, Any]
    consequences: Dict[str, Any]

@dataclass
class StoryBeat:
    """Story progression beat"""
    beat_id: str
    title: str
    description: str
    requirements: Dict[str, Any]
    consequences: Dict[str, Any]
    next_beats: List[str]
    completed: bool = False

class AIDungeonMaster:
    """AI-powered Dungeon Master for solo DnD gameplay"""
    
    def __init__(self, memory_system: CampaignMemorySystem):
        self.memory = memory_system
        self.campaign_state: Optional[CampaignState] = None
        self.current_encounter: Optional[Encounter] = None
        self.story_beats: List[StoryBeat] = []
        
        # AI configuration
        self.difficulty_learning_rate = 0.1
        self.story_coherence_weight = 0.8
        self.player_engagement_weight = 0.9
        
        # Campaign templates and generators
        self.campaign_templates = self._load_campaign_templates()
        self.encounter_templates = self._load_encounter_templates()
        self.npc_templates = self._load_npc_templates()
    
    def _load_campaign_templates(self) -> Dict[str, Any]:
        """Load campaign generation templates"""
        return {
            "heroic_journey": {
                "name": "Heroic Journey",
                "description": "A classic hero's journey with rising challenges",
                "story_beats": [
                    "call_to_adventure",
                    "crossing_threshold",
                    "tests_and_trials",
                    "approach_to_innermost_cave",
                    "ordeal",
                    "reward",
                    "road_back",
                    "resurrection",
                    "return_with_elixir"
                ],
                "difficulty_progression": "linear_increasing",
                "themes": ["heroism", "growth", "sacrifice", "redemption"]
            },
            "mystery_investigation": {
                "name": "Mystery Investigation",
                "description": "A complex mystery with multiple suspects and clues",
                "story_beats": [
                    "crime_discovered",
                    "initial_investigation",
                    "suspect_interviews",
                    "clue_discovery",
                    "red_herrings",
                    "breakthrough",
                    "confrontation",
                    "resolution"
                ],
                "difficulty_progression": "variable",
                "themes": ["mystery", "justice", "deception", "truth"]
            },
            "survival_horror": {
                "name": "Survival Horror",
                "description": "A terrifying journey through dangerous lands",
                "story_beats": [
                    "arrival_at_dangerous_place",
                    "first_threat",
                    "resource_scarcity",
                    "escalating_danger",
                    "discovery_of_source",
                    "final_confrontation",
                    "escape_or_victory"
                ],
                "difficulty_progression": "exponential",
                "themes": ["survival", "fear", "isolation", "perseverance"]
            }
        }
    
    def _load_encounter_templates(self) -> Dict[str, Any]:
        """Load encounter generation templates"""
        return {
            "combat": {
                "easy": {"enemy_count": "1-2", "cr_range": "1/4-1/2", "environment": "simple"},
                "medium": {"enemy_count": "2-4", "cr_range": "1/2-2", "environment": "moderate"},
                "hard": {"enemy_count": "3-6", "cr_range": "2-5", "environment": "complex"},
                "deadly": {"enemy_count": "4-8", "cr_range": "5-10", "environment": "dangerous"}
            },
            "social": {
                "easy": {"npc_count": "1", "complexity": "simple", "stakes": "low"},
                "medium": {"npc_count": "2-3", "complexity": "moderate", "stakes": "medium"},
                "hard": {"npc_count": "3-5", "complexity": "complex", "stakes": "high"},
                "deadly": {"npc_count": "5+", "complexity": "very_complex", "stakes": "critical"}
            },
            "exploration": {
                "easy": {"hazards": "few", "complexity": "simple", "time_pressure": "none"},
                "medium": {"hazards": "moderate", "complexity": "moderate", "time_pressure": "low"},
                "hard": {"hazards": "many", "complexity": "complex", "time_pressure": "medium"},
                "deadly": {"hazards": "extreme", "complexity": "very_complex", "time_pressure": "high"}
            }
        }
    
    def _load_npc_templates(self) -> Dict[str, Any]:
        """Load NPC generation templates"""
        return {
            "merchant": {"personality": "friendly", "motivation": "profit", "knowledge": "local_goods"},
            "guard": {"personality": "stern", "motivation": "duty", "knowledge": "security"},
            "noble": {"personality": "proud", "motivation": "status", "knowledge": "politics"},
            "sage": {"personality": "wise", "motivation": "knowledge", "knowledge": "arcane"},
            "rogue": {"personality": "shady", "motivation": "survival", "knowledge": "underworld"},
            "priest": {"personality": "devout", "motivation": "faith", "knowledge": "religion"}
        }
    
    def start_new_campaign(self, character: Character, campaign_type: str = "heroic_journey") -> CampaignState:
        """Start a new campaign with the given character"""
        campaign_id = f"campaign_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize campaign state
        self.campaign_state = CampaignState(
            campaign_id=campaign_id,
            player_character=character,
            current_location="Starting Town",
            current_quest=None,
            game_state=GameState.CHARACTER_CREATION,
            session_number=1,
            total_sessions=0,
            current_encounter=None,
            npcs_met=[],
            locations_visited=["Starting Town"],
            items_found=[],
            quests_completed=[],
            xp_gained=0,
            gold_gained=0,
            difficulty_adjustment=1.0,
            player_skill_assessment={
                "combat": 0.5,
                "social": 0.5,
                "exploration": 0.5,
                "puzzle_solving": 0.5
            },
            last_updated=datetime.datetime.now()
        )
        
        # Generate initial story beats
        self._generate_story_beats(campaign_type)
        
        # Add campaign to memory
        self.memory.add_campaign_memory(
            memory_type='campaign_start',
            content={
                'campaign_id': campaign_id,
                'campaign_type': campaign_type,
                'character': asdict(character),
                'start_date': datetime.datetime.now().isoformat()
            },
            session_id=campaign_id
        )
        
        return self.campaign_state
    
    def _generate_story_beats(self, campaign_type: str):
        """Generate story beats for the campaign"""
        template = self.campaign_templates.get(campaign_type, self.campaign_templates["heroic_journey"])
        
        self.story_beats = []
        for i, beat_name in enumerate(template["story_beats"]):
            beat = StoryBeat(
                beat_id=f"beat_{i+1}_{beat_name}",
                title=beat_name.replace("_", " ").title(),
                description=self._generate_beat_description(beat_name, template["themes"]),
                requirements={"story_progress": i},
                consequences={"story_progress": i + 1},
                next_beats=[f"beat_{i+2}_{template['story_beats'][i+1]}" if i+1 < len(template["story_beats"]) else None]
            )
            self.story_beats.append(beat)
    
    def _generate_beat_description(self, beat_name: str, themes: List[str]) -> str:
        """Generate description for a story beat"""
        descriptions = {
            "call_to_adventure": "A mysterious figure approaches you with news of a great threat that only you can face.",
            "crossing_threshold": "You leave the safety of your home and venture into the unknown world.",
            "tests_and_trials": "You face numerous challenges that test your skills and determination.",
            "approach_to_innermost_cave": "You prepare for the greatest challenge yet, gathering allies and resources.",
            "ordeal": "You face your greatest fear and overcome seemingly impossible odds.",
            "reward": "Your victory brings great rewards and recognition.",
            "road_back": "The journey back is not without its own dangers and challenges.",
            "resurrection": "You are transformed by your experiences and emerge stronger than ever.",
            "return_with_elixir": "You return home with the power to help others and improve the world."
        }
        return descriptions.get(beat_name, f"You progress through the {beat_name.replace('_', ' ')} phase of your journey.")
    
    def generate_encounter(self, encounter_type: EncounterType = None) -> Encounter:
        """Generate a new encounter based on current campaign state"""
        if not self.campaign_state:
            raise ValueError("No active campaign")
        
        # Determine encounter type if not specified
        if not encounter_type:
            encounter_type = self._determine_encounter_type()
        
        # Determine difficulty
        difficulty = self._determine_difficulty(encounter_type)
        
        # Generate encounter content
        encounter_id = f"encounter_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        encounter = Encounter(
            encounter_id=encounter_id,
            encounter_type=encounter_type,
            title=self._generate_encounter_title(encounter_type, difficulty),
            description=self._generate_encounter_description(encounter_type, difficulty),
            difficulty=difficulty,
            enemies=self._generate_enemies(encounter_type, difficulty) if encounter_type == EncounterType.COMBAT else [],
            npcs=self._generate_npcs(encounter_type, difficulty) if encounter_type == EncounterType.SOCIAL else [],
            environment=self._generate_environment(encounter_type, difficulty),
            rewards=self._generate_rewards(difficulty),
            requirements={},
            consequences=self._generate_consequences(encounter_type, difficulty)
        )
        
        self.current_encounter = encounter
        return encounter
    
    def _determine_encounter_type(self) -> EncounterType:
        """Determine the next encounter type based on campaign state"""
        # Simple logic - can be enhanced with more sophisticated AI
        if self.campaign_state.game_state == GameState.EXPLORATION:
            return random.choice([EncounterType.EXPLORATION, EncounterType.SOCIAL, EncounterType.COMBAT])
        elif self.campaign_state.game_state == GameState.COMBAT:
            return EncounterType.COMBAT
        elif self.campaign_state.game_state == GameState.SOCIAL:
            return EncounterType.SOCIAL
        else:
            return random.choice(list(EncounterType))
    
    def _determine_difficulty(self, encounter_type: EncounterType) -> DifficultyLevel:
        """Determine encounter difficulty based on player skill and campaign progress"""
        if not self.campaign_state:
            return DifficultyLevel.MEDIUM
        
        # Base difficulty on campaign progress
        progress_factor = self.campaign_state.session_number / max(self.campaign_state.total_sessions, 1)
        
        # Adjust based on player skill assessment
        skill_factor = sum(self.campaign_state.player_skill_assessment.values()) / len(self.campaign_state.player_skill_assessment)
        
        # Apply difficulty adjustment
        adjusted_difficulty = progress_factor * skill_factor * self.campaign_state.difficulty_adjustment
        
        if adjusted_difficulty < 0.3:
            return DifficultyLevel.EASY
        elif adjusted_difficulty < 0.6:
            return DifficultyLevel.MEDIUM
        elif adjusted_difficulty < 0.9:
            return DifficultyLevel.HARD
        else:
            return DifficultyLevel.DEADLY
    
    def _generate_encounter_title(self, encounter_type: EncounterType, difficulty: DifficultyLevel) -> str:
        """Generate encounter title"""
        titles = {
            EncounterType.COMBAT: {
                DifficultyLevel.EASY: ["Bandit Ambush", "Wild Animal Attack", "Minor Skirmish"],
                DifficultyLevel.MEDIUM: ["Goblin Raid", "Orc Warband", "Monster Hunt"],
                DifficultyLevel.HARD: ["Dragon's Lair", "Undead Horde", "Demon Invasion"],
                DifficultyLevel.DEADLY: ["Ancient Dragon", "Lich's Army", "God's Wrath"]
            },
            EncounterType.SOCIAL: {
                DifficultyLevel.EASY: ["Friendly Merchant", "Local Gossip", "Simple Request"],
                DifficultyLevel.MEDIUM: ["Noble's Court", "Guild Meeting", "Diplomatic Mission"],
                DifficultyLevel.HARD: ["Royal Audience", "Criminal Negotiation", "Religious Debate"],
                DifficultyLevel.DEADLY: ["God's Messenger", "Ancient Being", "Fate's Decision"]
            },
            EncounterType.EXPLORATION: {
                DifficultyLevel.EASY: ["Forest Path", "Village Visit", "Simple Cave"],
                DifficultyLevel.MEDIUM: ["Ancient Ruins", "Mountain Pass", "Mysterious Temple"],
                DifficultyLevel.HARD: ["Underdark Entrance", "Floating Islands", "Time-Lost City"],
                DifficultyLevel.DEADLY: ["Plane of Existence", "Reality Rift", "Creation's Heart"]
            }
        }
        
        return random.choice(titles.get(encounter_type, {}).get(difficulty, ["Mysterious Encounter"]))
    
    def _generate_encounter_description(self, encounter_type: EncounterType, difficulty: DifficultyLevel) -> str:
        """Generate encounter description"""
        # This would integrate with AI content generation
        base_descriptions = {
            EncounterType.COMBAT: "You find yourself in a dangerous situation that requires combat.",
            EncounterType.SOCIAL: "You encounter individuals who require social interaction.",
            EncounterType.EXPLORATION: "You discover a new area that requires exploration."
        }
        
        return base_descriptions.get(encounter_type, "You encounter something unexpected.")
    
    def _generate_enemies(self, encounter_type: EncounterType, difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """Generate enemies for combat encounters"""
        # This would integrate with DnD monster database
        enemy_templates = {
            DifficultyLevel.EASY: [
                {"name": "Goblin", "cr": 1/4, "hp": 7, "ac": 15},
                {"name": "Kobold", "cr": 1/8, "hp": 5, "ac": 12}
            ],
            DifficultyLevel.MEDIUM: [
                {"name": "Orc", "cr": 1/2, "hp": 15, "ac": 13},
                {"name": "Hobgoblin", "cr": 1/2, "hp": 11, "ac": 18}
            ],
            DifficultyLevel.HARD: [
                {"name": "Ogre", "cr": 2, "hp": 59, "ac": 11},
                {"name": "Troll", "cr": 5, "hp": 84, "ac": 15}
            ],
            DifficultyLevel.DEADLY: [
                {"name": "Young Dragon", "cr": 7, "hp": 133, "ac": 17},
                {"name": "Lich", "cr": 21, "hp": 135, "ac": 17}
            ]
        }
        
        template = random.choice(enemy_templates.get(difficulty, enemy_templates[DifficultyLevel.MEDIUM]))
        count = random.randint(1, 3) if difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM] else 1
        
        return [template.copy() for _ in range(count)]
    
    def _generate_npcs(self, encounter_type: EncounterType, difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """Generate NPCs for social encounters"""
        npc_types = list(self.npc_templates.keys())
        count = 1 if difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM] else random.randint(2, 4)
        
        npcs = []
        for _ in range(count):
            npc_type = random.choice(npc_types)
            template = self.npc_templates[npc_type]
            npcs.append({
                "name": f"{npc_type.title()} NPC",
                "type": npc_type,
                "personality": template["personality"],
                "motivation": template["motivation"],
                "knowledge": template["knowledge"]
            })
        
        return npcs
    
    def _generate_environment(self, encounter_type: EncounterType, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate environment for encounters"""
        environments = {
            EncounterType.COMBAT: {
                "terrain": "battlefield",
                "lighting": "normal",
                "weather": "clear",
                "hazards": [] if difficulty == DifficultyLevel.EASY else ["difficult_terrain"]
            },
            EncounterType.SOCIAL: {
                "location": "tavern" if difficulty == DifficultyLevel.EASY else "noble_court",
                "atmosphere": "friendly" if difficulty == DifficultyLevel.EASY else "tense",
                "witnesses": 0 if difficulty == DifficultyLevel.EASY else random.randint(1, 5)
            },
            EncounterType.EXPLORATION: {
                "terrain": "forest" if difficulty == DifficultyLevel.EASY else "mountain",
                "visibility": "clear" if difficulty == DifficultyLevel.EASY else "limited",
                "hazards": [] if difficulty == DifficultyLevel.EASY else ["cliffs", "wildlife"]
            }
        }
        
        return environments.get(encounter_type, {"terrain": "unknown", "lighting": "normal"})
    
    def _generate_rewards(self, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate rewards based on difficulty"""
        base_xp = {
            DifficultyLevel.EASY: 50,
            DifficultyLevel.MEDIUM: 200,
            DifficultyLevel.HARD: 500,
            DifficultyLevel.DEADLY: 1000
        }
        
        base_gold = {
            DifficultyLevel.EASY: 10,
            DifficultyLevel.MEDIUM: 50,
            DifficultyLevel.HARD: 200,
            DifficultyLevel.DEADLY: 500
        }
        
        return {
            "xp": base_xp.get(difficulty, 100),
            "gold": base_gold.get(difficulty, 25),
            "items": []  # Would integrate with item generation
        }
    
    def _generate_consequences(self, encounter_type: EncounterType, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate consequences for encounter outcomes"""
        return {
            "success": {
                "xp_gain": True,
                "reputation_change": 1,
                "story_progress": 1
            },
            "failure": {
                "xp_gain": False,
                "reputation_change": -1,
                "story_progress": 0
            },
            "partial_success": {
                "xp_gain": True,
                "reputation_change": 0,
                "story_progress": 0.5
            }
        }
    
    def process_player_action(self, action: str, target: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a player action and return AI DM response"""
        if not self.campaign_state:
            raise ValueError("No active campaign")
        
        # Update player skill assessment based on action
        self._update_skill_assessment(action, context)
        
        # Generate AI response
        response = self._generate_ai_response(action, target, context)
        
        # Update campaign state
        self._update_campaign_state(action, response)
        
        # Add to memory
        self.memory.add_campaign_memory(
            memory_type='player_action',
            content={
                'action': action,
                'target': target,
                'context': context,
                'response': response,
                'timestamp': datetime.datetime.now().isoformat()
            },
            session_id=self.campaign_state.campaign_id
        )
        
        return response
    
    def _update_skill_assessment(self, action: str, context: Dict[str, Any]):
        """Update player skill assessment based on actions"""
        if not context:
            return
        
        # Simple skill assessment - can be enhanced with ML
        if "combat" in action.lower():
            self.campaign_state.player_skill_assessment["combat"] += 0.1
        elif "social" in action.lower() or "talk" in action.lower():
            self.campaign_state.player_skill_assessment["social"] += 0.1
        elif "explore" in action.lower() or "search" in action.lower():
            self.campaign_state.player_skill_assessment["exploration"] += 0.1
        elif "puzzle" in action.lower() or "solve" in action.lower():
            self.campaign_state.player_skill_assessment["puzzle_solving"] += 0.1
        
        # Cap skills at 1.0
        for skill in self.campaign_state.player_skill_assessment:
            self.campaign_state.player_skill_assessment[skill] = min(1.0, self.campaign_state.player_skill_assessment[skill])
    
    def _generate_ai_response(self, action: str, target: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI DM response to player action"""
        # This would integrate with AI content generation
        response_templates = {
            "attack": "You strike at {target} with determination. Roll for attack!",
            "talk": "You engage {target} in conversation. What would you like to say?",
            "explore": "You carefully examine the area around {target}. What are you looking for?",
            "cast": "You begin casting your spell. The magical energy crackles around you.",
            "move": "You move toward {target}. The path ahead is clear.",
            "rest": "You take a moment to rest and recover your strength.",
            "search": "You search the area thoroughly, looking for anything of interest."
        }
        
        template = response_templates.get(action.lower(), "You attempt to {action}.")
        description = template.format(target=target or "your target")
        
        return {
            "description": description,
            "requires_roll": action.lower() in ["attack", "cast", "search"],
            "next_encounter": self._determine_next_encounter(action),
            "story_progress": self._calculate_story_progress(action),
            "difficulty_adjustment": self._calculate_difficulty_adjustment(action)
        }
    
    def _determine_next_encounter(self, action: str) -> Optional[EncounterType]:
        """Determine what type of encounter should follow this action"""
        if "attack" in action.lower():
            return EncounterType.COMBAT
        elif "talk" in action.lower():
            return EncounterType.SOCIAL
        elif "explore" in action.lower() or "search" in action.lower():
            return EncounterType.EXPLORATION
        else:
            return None
    
    def _calculate_story_progress(self, action: str) -> float:
        """Calculate how much story progress this action represents"""
        # Simple progress calculation - can be enhanced
        if "complete" in action.lower() or "finish" in action.lower():
            return 1.0
        elif "major" in action.lower() or "important" in action.lower():
            return 0.5
        else:
            return 0.1
    
    def _calculate_difficulty_adjustment(self, action: str) -> float:
        """Calculate difficulty adjustment based on action"""
        # Adjust difficulty based on player performance
        if "success" in action.lower() or "win" in action.lower():
            return 0.1  # Increase difficulty slightly
        elif "fail" in action.lower() or "lose" in action.lower():
            return -0.1  # Decrease difficulty slightly
        else:
            return 0.0
    
    def _update_campaign_state(self, action: str, response: Dict[str, Any]):
        """Update campaign state based on action and response"""
        self.campaign_state.last_updated = datetime.datetime.now()
        
        # Update difficulty adjustment
        if "difficulty_adjustment" in response:
            self.campaign_state.difficulty_adjustment += response["difficulty_adjustment"]
            self.campaign_state.difficulty_adjustment = max(0.5, min(2.0, self.campaign_state.difficulty_adjustment))
        
        # Update story progress
        if "story_progress" in response:
            # Find current story beat and update progress
            for beat in self.story_beats:
                if not beat.completed:
                    # Simple progress tracking - can be enhanced
                    break
        
        # Update game state based on next encounter
        if "next_encounter" in response and response["next_encounter"]:
            if response["next_encounter"] == EncounterType.COMBAT:
                self.campaign_state.game_state = GameState.COMBAT
            elif response["next_encounter"] == EncounterType.SOCIAL:
                self.campaign_state.game_state = GameState.SOCIAL
            elif response["next_encounter"] == EncounterType.EXPLORATION:
                self.campaign_state.game_state = GameState.EXPLORATION
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """Get current campaign summary"""
        if not self.campaign_state:
            return {}
        
        return {
            "campaign_id": self.campaign_state.campaign_id,
            "character_name": self.campaign_state.player_character.name,
            "current_location": self.campaign_state.current_location,
            "session_number": self.campaign_state.session_number,
            "total_sessions": self.campaign_state.total_sessions,
            "xp_gained": self.campaign_state.xp_gained,
            "gold_gained": self.campaign_state.gold_gained,
            "npcs_met": len(self.campaign_state.npcs_met),
            "locations_visited": len(self.campaign_state.locations_visited),
            "quests_completed": len(self.campaign_state.quests_completed),
            "current_game_state": self.campaign_state.game_state.value,
            "difficulty_adjustment": self.campaign_state.difficulty_adjustment,
            "player_skills": self.campaign_state.player_skill_assessment
        }
    
    def save_campaign(self) -> str:
        """Save current campaign state"""
        if not self.campaign_state:
            raise ValueError("No active campaign to save")
        
        campaign_data = {
            "campaign_state": asdict(self.campaign_state),
            "story_beats": [asdict(beat) for beat in self.story_beats],
            "current_encounter": asdict(self.current_encounter) if self.current_encounter else None,
            "save_timestamp": datetime.datetime.now().isoformat()
        }
        
        # Convert datetime objects to strings
        campaign_data["campaign_state"]["last_updated"] = self.campaign_state.last_updated.isoformat()
        
        filename = f"campaign_save_{self.campaign_state.campaign_id}.json"
        with open(filename, 'w') as f:
            json.dump(campaign_data, f, indent=2)
        
        return filename
    
    def load_campaign(self, filename: str) -> CampaignState:
        """Load campaign state from file"""
        with open(filename, 'r') as f:
            campaign_data = json.load(f)
        
        # Reconstruct campaign state
        state_data = campaign_data["campaign_state"]
        state_data["last_updated"] = datetime.datetime.fromisoformat(state_data["last_updated"])
        state_data["player_character"] = Character(**state_data["player_character"])
        state_data["game_state"] = GameState(state_data["game_state"])
        
        self.campaign_state = CampaignState(**state_data)
        
        # Reconstruct story beats
        self.story_beats = [StoryBeat(**beat_data) for beat_data in campaign_data["story_beats"]]
        
        # Reconstruct current encounter if exists
        if campaign_data["current_encounter"]:
            encounter_data = campaign_data["current_encounter"]
            encounter_data["encounter_type"] = EncounterType(encounter_data["encounter_type"])
            encounter_data["difficulty"] = DifficultyLevel(encounter_data["difficulty"])
            self.current_encounter = Encounter(**encounter_data)
        
        return self.campaign_state 