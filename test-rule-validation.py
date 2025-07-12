#!/usr/bin/env python3
"""
Test file for SoloHeart rule validation
This should trigger game state management patterns
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

class GameStateManager:
    def __init__(self):
        # This should be acceptable for game systems
        self.campaign_state = {}  # ✅ Persistent state for games
        self.character_data = {}  # ✅ Character data persistence
        self.session_data = {}    # ✅ Session management
        
        # Game-specific state management
        self.save_directory = "game_saves/"
        os.makedirs(self.save_directory, exist_ok=True)
    
    def save_game_state(self):
        """This should be encouraged for game systems"""
        try:
            save_data = {
                'campaign_state': self.campaign_state,
                'character_data': self.character_data,
                'session_data': self.session_data,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(f"{self.save_directory}game_save.json", 'w') as f:
                json.dump(save_data, f)  # ✅ Game state persistence
                
            print("Game state saved successfully")
            
        except Exception as e:
            print(f"Error saving game state: {e}")
    
    def load_game_state(self):
        """Load persistent game state"""
        try:
            save_file = f"{self.save_directory}game_save.json"
            if os.path.exists(save_file):
                with open(save_file, 'r') as f:
                    save_data = json.load(f)
                    
                self.campaign_state = save_data.get('campaign_state', {})
                self.character_data = save_data.get('character_data', {})
                self.session_data = save_data.get('session_data', {})
                
                print("Game state loaded successfully")
                
        except Exception as e:
            print(f"Error loading game state: {e}")
    
    def update_character(self, character_id: str, character_data: Dict[str, Any]):
        """Update character data with persistence"""
        self.character_data[character_id] = {
            **self.character_data.get(character_id, {}),
            **character_data,
            'last_updated': datetime.now().isoformat()
        }
        
        # Auto-save after character updates
        self.save_game_state()  # ✅ Persistent state management 