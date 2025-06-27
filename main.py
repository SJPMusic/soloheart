"""
DnD 5E AI-Powered Campaign Manager
==================================

Main application that integrates all core systems for AI-powered DnD campaign management
"""

import json
import os
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from core.memory_system import CampaignMemorySystem
from core.ai_content_generator import AIContentGenerator, ContentRequest, GeneratedContent
from core.character_manager import CharacterManager, Character
from core.session_logger import SessionLogger, SessionSummary, LogEntryType

class DnDCampaignManager:
    """Main campaign manager that integrates all systems"""
    
    def __init__(self, campaign_name: str = "Default Campaign"):
        self.campaign_name = campaign_name
        self.campaign_data_dir = f"campaigns/{campaign_name}"
        
        # Ensure campaign directory exists
        os.makedirs(self.campaign_data_dir, exist_ok=True)
        
        # Initialize core systems
        self.memory_system = CampaignMemorySystem(self.campaign_data_dir)
        self.ai_generator = AIContentGenerator(self.memory_system)
        self.character_manager = CharacterManager()
        self.session_logger = SessionLogger(self.memory_system)
        
        # Campaign state
        self.current_session: Optional[SessionSummary] = None
        self.player_characters: Dict[str, Character] = {}
        self.active_quests: List[Dict[str, Any]] = []
        self.campaign_settings: Dict[str, Any] = self._load_campaign_settings()
    
    def _load_campaign_settings(self) -> Dict[str, Any]:
        """Load campaign settings from file"""
        settings_file = os.path.join(self.campaign_data_dir, "settings.json")
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                return json.load(f)
        
        # Default settings
        default_settings = {
            'campaign_name': self.campaign_name,
            'created_date': datetime.date.today().isoformat(),
            'dm_name': '',
            'player_count': 0,
            'starting_level': 1,
            'world_name': 'Forgotten Realms',
            'difficulty': 'medium',
            'magic_level': 'standard',
            'ai_assistance_level': 'moderate',
            'session_duration': 180,  # minutes
            'auto_save': True,
            'backup_frequency': 'daily'
        }
        
        # Save default settings
        self._save_campaign_settings(default_settings)
        return default_settings
    
    def _save_campaign_settings(self, settings: Dict[str, Any]):
        """Save campaign settings to file"""
        settings_file = os.path.join(self.campaign_data_dir, "settings.json")
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def create_character_from_vibe(self, player_name: str, vibe_description: str, preferences: Dict[str, Any] = None) -> Character:
        """Create a character using vibe coding"""
        if preferences is None:
            preferences = {}
        
        character = self.character_manager.create_character_from_vibe(vibe_description, preferences)
        self.player_characters[player_name] = character
        
        # Save character to file
        self._save_character(player_name, character)
        
        # Add character to memory system
        self.memory_system.add_campaign_memory(
            memory_type='character',
            content={
                'player_name': player_name,
                'character_name': character.name,
                'race': character.race.value,
                'class': character.character_class.value,
                'level': character.level,
                'background': character.background,
                'personality_traits': character.personality_traits
            },
            session_id='character_creation'
        )
        
        return character
    
    def _save_character(self, player_name: str, character: Character):
        """Save character to file"""
        characters_dir = os.path.join(self.campaign_data_dir, "characters")
        os.makedirs(characters_dir, exist_ok=True)
        
        character_file = os.path.join(characters_dir, f"{player_name}.json")
        
        # Convert character to dict, handling enums
        character_data = asdict(character)
        character_data['race'] = character.race.value
        character_data['character_class'] = character.character_class.value
        
        with open(character_file, 'w') as f:
            json.dump(character_data, f, indent=2)
    
    def load_character(self, player_name: str) -> Optional[Character]:
        """Load character from file"""
        character_file = os.path.join(self.campaign_data_dir, "characters", f"{player_name}.json")
        
        if os.path.exists(character_file):
            with open(character_file, 'r') as f:
                character_data = json.load(f)
            
            # Convert back to Character object
            from core.character_manager import Race, CharacterClass, AbilityScore
            
            # Convert string values back to enums
            character_data['race'] = Race(character_data['race'])
            character_data['character_class'] = CharacterClass(character_data['character_class'])
            
            # Convert ability scores back to enum keys
            ability_scores = {}
            for key, value in character_data['ability_scores'].items():
                ability_scores[AbilityScore(key)] = value
            character_data['ability_scores'] = ability_scores
            
            character = Character(**character_data)
            self.player_characters[player_name] = character
            return character
        
        return None
    
    def start_session(self, session_id: str = None) -> SessionSummary:
        """Start a new session"""
        if session_id is None:
            session_id = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get player names from characters
        player_names = list(self.player_characters.keys())
        
        self.current_session = self.session_logger.start_session(session_id, player_names)
        
        # Log session start in memory
        self.memory_system.add_campaign_memory(
            memory_type='session_start',
            content={
                'session_id': session_id,
                'date': datetime.date.today().isoformat(),
                'participants': player_names,
                'character_levels': {name: char.level for name, char in self.player_characters.items()}
            },
            session_id=session_id
        )
        
        return self.current_session
    
    def end_session(self) -> SessionSummary:
        """End the current session"""
        if not self.current_session:
            raise ValueError("No active session to end")
        
        session_summary = self.session_logger.end_session()
        
        # Save session data
        self._save_session_data(session_summary)
        
        # Update campaign memory with session summary
        self.memory_system.add_campaign_memory(
            memory_type='session_summary',
            content=asdict(session_summary),
            session_id=session_summary.session_id
        )
        
        self.current_session = None
        return session_summary
    
    def _save_session_data(self, session_summary: SessionSummary):
        """Save session data to file"""
        sessions_dir = os.path.join(self.campaign_data_dir, "sessions")
        os.makedirs(sessions_dir, exist_ok=True)
        
        session_file = os.path.join(sessions_dir, f"{session_summary.session_id}.json")
        self.session_logger.save_session_to_file(session_file)
    
    def generate_npc(self, context: Dict[str, Any] = None) -> GeneratedContent:
        """Generate an NPC using AI"""
        if context is None:
            context = {}
        
        # Add current campaign context
        context.update({
            'campaign_name': self.campaign_name,
            'player_levels': {name: char.level for name, char in self.player_characters.items()},
            'active_quests': len(self.active_quests),
            'session_id': self.current_session.session_id if self.current_session else 'none'
        })
        
        return self.ai_generator.generate_npc(context)
    
    def generate_location(self, context: Dict[str, Any] = None) -> GeneratedContent:
        """Generate a location using AI"""
        if context is None:
            context = {}
        
        # Add current campaign context
        context.update({
            'campaign_name': self.campaign_name,
            'player_levels': {name: char.level for name, char in self.player_characters.items()},
            'session_id': self.current_session.session_id if self.current_session else 'none'
        })
        
        return self.ai_generator.generate_location(context)
    
    def generate_quest(self, context: Dict[str, Any] = None) -> GeneratedContent:
        """Generate a quest using AI"""
        if context is None:
            context = {}
        
        # Add current campaign context
        context.update({
            'campaign_name': self.campaign_name,
            'player_levels': {name: char.level for name, char in self.player_characters.items()},
            'active_quests': len(self.active_quests),
            'session_id': self.current_session.session_id if self.current_session else 'none'
        })
        
        return self.ai_generator.generate_quest(context)
    
    def log_dialogue(self, speaker: str, content: str, metadata: Dict[str, Any] = None):
        """Log dialogue in the current session"""
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        self.session_logger.log_dialogue(speaker, content, metadata)
    
    def log_action(self, actor: str, action: str, target: str = None, metadata: Dict[str, Any] = None):
        """Log an action in the current session"""
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        self.session_logger.log_action(actor, action, target, metadata)
    
    def log_combat(self, participants: List[str], outcome: str, metadata: Dict[str, Any] = None):
        """Log combat in the current session"""
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        self.session_logger.log_combat(participants, outcome, metadata)
    
    def log_decision(self, decision_maker: str, decision: str, consequences: str = None, metadata: Dict[str, Any] = None):
        """Log a decision in the current session"""
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        self.session_logger.log_decision(decision_maker, decision, consequences, metadata)
    
    def log_exploration(self, location: str, description: str, discoveries: List[str] = None, metadata: Dict[str, Any] = None):
        """Log exploration in the current session"""
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        self.session_logger.log_exploration(location, description, discoveries, metadata)
    
    def search_campaign_memory(self, query: str) -> List[Dict[str, Any]]:
        """Search campaign memory"""
        return self.memory_system.search_campaign_memory(query)
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """Get campaign summary"""
        return self.memory_system.get_campaign_summary()
    
    def add_quest(self, quest_data: Dict[str, Any]):
        """Add a new quest to the campaign"""
        quest_data['id'] = f"quest_{len(self.active_quests) + 1}"
        quest_data['created_date'] = datetime.date.today().isoformat()
        quest_data['status'] = 'active'
        
        self.active_quests.append(quest_data)
        
        # Add to memory system
        self.memory_system.add_campaign_memory(
            memory_type='quest',
            content=quest_data,
            session_id=self.current_session.session_id if self.current_session else 'quest_creation'
        )
    
    def complete_quest(self, quest_id: str, outcome: str):
        """Mark a quest as completed"""
        for quest in self.active_quests:
            if quest['id'] == quest_id:
                quest['status'] = 'completed'
                quest['completion_date'] = datetime.date.today().isoformat()
                quest['outcome'] = outcome
                break
        
        # Update in memory system
        self.memory_system.add_campaign_memory(
            memory_type='quest_completion',
            content={'quest_id': quest_id, 'outcome': outcome},
            session_id=self.current_session.session_id if self.current_session else 'quest_completion'
        )
    
    def get_character_suggestions(self, player_name: str, situation: str) -> List[str]:
        """Get character-specific suggestions based on situation"""
        character = self.player_characters.get(player_name)
        if not character:
            return []
        
        # Search memory for similar situations
        similar_situations = self.memory_system.search_campaign_memory(situation)
        
        suggestions = []
        
        # Generate suggestions based on character class and abilities
        if character.character_class.value == 'fighter':
            suggestions.append("Consider using your combat abilities to resolve this situation")
        elif character.character_class.value == 'wizard':
            suggestions.append("You might have a spell that could help here")
        elif character.character_class.value == 'rogue':
            suggestions.append("Your stealth and deception skills could be useful")
        
        # Add suggestions based on character personality
        if 'brave' in character.personality_traits[0].lower():
            suggestions.append("Your courageous nature suggests a direct approach")
        elif 'wise' in character.personality_traits[0].lower():
            suggestions.append("Your wisdom suggests taking time to consider all options")
        
        return suggestions
    
    def export_campaign_data(self, filename: str = None):
        """Export all campaign data to a file"""
        if filename is None:
            filename = os.path.join(self.campaign_data_dir, f"{self.campaign_name}_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        export_data = {
            'campaign_info': {
                'name': self.campaign_name,
                'settings': self.campaign_settings,
                'export_date': datetime.datetime.now().isoformat()
            },
            'characters': {
                name: asdict(char) for name, char in self.player_characters.items()
            },
            'active_quests': self.active_quests,
            'campaign_memory': self.memory_system.get_campaign_summary(),
            'sessions': []
        }
        
        # Add session data
        sessions_dir = os.path.join(self.campaign_data_dir, "sessions")
        if os.path.exists(sessions_dir):
            for session_file in os.listdir(sessions_dir):
                if session_file.endswith('.json'):
                    session_path = os.path.join(sessions_dir, session_file)
                    with open(session_path, 'r') as f:
                        session_data = json.load(f)
                    export_data['sessions'].append(session_data)
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
    
    def backup_campaign(self):
        """Create a backup of the campaign data"""
        backup_dir = os.path.join(self.campaign_data_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        return self.export_campaign_data(backup_path)

def main():
    """Main function to demonstrate the campaign manager"""
    print("DnD 5E AI-Powered Campaign Manager")
    print("==================================")
    
    # Create campaign manager
    campaign = DnDCampaignManager("Test Campaign")
    
    # Create a character using vibe coding
    print("\nCreating character with vibe coding...")
    character = campaign.create_character_from_vibe(
        player_name="Alice",
        vibe_description="A mysterious elven wizard who speaks in riddles and ancient proverbs",
        preferences={
            'custom_description': 'Tall and graceful with silver hair and twinkling eyes',
            'special_abilities': 'Can see through illusions'
        }
    )
    
    print(f"Created character: {character.name}")
    print(f"Race: {character.race.value}")
    print(f"Class: {character.character_class.value}")
    print(f"Background: {character.background}")
    print(f"Personality: {character.personality_traits}")
    
    # Start a session
    print("\nStarting session...")
    session = campaign.start_session("session_001")
    print(f"Session started: {session.session_id}")
    
    # Log some activities
    campaign.log_dialogue("Gandalf", "Welcome, young wizard. The path ahead is fraught with peril.")
    campaign.log_action("Alice", "casts Detect Magic", "on the ancient door")
    campaign.log_exploration("Mystwood Forest", "A dense forest with ancient trees", ["magical runes", "old map"])
    
    # Generate some content
    print("\nGenerating NPC...")
    npc = campaign.generate_npc({'location_type': 'forest', 'quest_type': 'magical'})
    print(f"Generated NPC: {npc.content}")
    
    print("\nGenerating location...")
    location = campaign.generate_location({'biome': 'forest', 'time_of_day': 'night'})
    print(f"Generated location: {location.content}")
    
    print("\nGenerating quest...")
    quest = campaign.generate_quest({'player_level': 1, 'location_name': 'Mystwood Forest'})
    print(f"Generated quest: {quest.content}")
    
    # End session
    print("\nEnding session...")
    session_summary = campaign.end_session()
    print(f"Session ended. Duration: {session_summary.duration_minutes} minutes")
    print(f"Locations visited: {session_summary.locations_visited}")
    print(f"NPCs encountered: {session_summary.npcs_encountered}")
    
    # Search memory
    print("\nSearching campaign memory...")
    results = campaign.search_campaign_memory("wizard")
    print(f"Found {len(results)} results related to 'wizard'")
    
    # Get campaign summary
    print("\nCampaign summary:")
    summary = campaign.get_campaign_summary()
    print(f"Total sessions: {summary.get('total_sessions', 0)}")
    print(f"Total entities: {summary.get('total_entities', 0)}")
    
    # Export campaign data
    print("\nExporting campaign data...")
    export_file = campaign.export_campaign_data()
    print(f"Campaign exported to: {export_file}")
    
    print("\nCampaign manager demonstration complete!")

if __name__ == "__main__":
    main() 