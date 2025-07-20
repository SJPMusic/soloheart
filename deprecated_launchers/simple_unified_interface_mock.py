#!/usr/bin/env python3
"""
Simple Unified Solo DnD 5E Narrative Interface (Mock Version)
A single Flask server that provides the complete immersive solo DnD experience.
This version uses mock responses instead of OpenAI API calls for testing.
"""

import os
import json
import logging
import uuid
import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'unified-narrative-key')

class MockCharacterGenerator:
    """Mock character generator for vibe code creation."""
    
    def __init__(self):
        self.conversation_history = []
        self.character_data = {}
        self.is_complete = False
        self.step_count = 0
    
    def start_character_creation(self, description: str, campaign_name: str = "") -> Dict[str, Any]:
        """Start character creation conversation."""
        try:
            # Mock response based on description
            if "warrior" in description.lower():
                response = "Great! I can help you create a warrior character. What would you like to name your character?"
            elif "wizard" in description.lower():
                response = "Excellent! A wizard character. What would you like to name your character?"
            elif "rogue" in description.lower():
                response = "Perfect! A rogue character. What would you like to name your character?"
            else:
                response = "Interesting character concept! What would you like to name your character?"
            
            # Store conversation
            self.conversation_history = [
                {"role": "user", "content": f"I want to create a character. Here's my concept: {description}"},
                {"role": "assistant", "content": response}
            ]
            
            return {
                "success": True,
                "message": response,
                "is_complete": False
            }
            
        except Exception as e:
            logger.error(f"Error starting character creation: {e}")
            return {
                "success": False,
                "message": "Error starting character creation. Please try again."
            }
    
    def continue_conversation(self, user_input: str) -> Dict[str, Any]:
        """Continue the character creation conversation."""
        try:
            # Add user input to history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.step_count += 1
            
            # Mock conversation flow
            if self.step_count == 1:
                # Name provided, ask for race
                response = "Great name! What race would you like to be? (Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling)"
            elif self.step_count == 2:
                # Race provided, ask for class
                response = "Excellent choice! What class would you like to be? (Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard)"
            elif self.step_count == 3:
                # Class provided, ask for background
                response = "Perfect! What background would you like? (Acolyte, Criminal, Folk Hero, Noble, Sage, Soldier, or custom)"
            elif self.step_count == 4:
                # Background provided, complete
                response = "Character creation complete! Your character has been created successfully."
                self.is_complete = True
                # Create mock character data
                self.character_data = {
                    "name": "Adventurer",
                    "race": "Human",
                    "class": "Fighter",
                    "level": 1,
                    "background": "Adventurer",
                    "personality": "A brave adventurer",
                    "created_date": datetime.datetime.now().isoformat()
                }
            else:
                response = "Thank you for that information! Character creation complete!"
                self.is_complete = True
            
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return {
                "success": True,
                "message": response,
                "is_complete": self.is_complete
            }
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return {
                "success": False,
                "message": "Error continuing conversation. Please try again."
            }
    
    def get_character_data(self) -> Dict[str, Any]:
        """Get the completed character data."""
        return self.character_data
    
    def save_character(self, campaign_id: str):
        """Save character data to file."""
        try:
            os.makedirs("character_saves", exist_ok=True)
            character_file = f"character_saves/{campaign_id}_character.json"
            with open(character_file, 'w') as f:
                json.dump(self.character_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving character: {e}")

class MockNarrativeBridge:
    """Mock narrative bridge for game interactions."""
    
    def __init__(self):
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure necessary directories exist."""
        os.makedirs("campaign_saves", exist_ok=True)
        os.makedirs("character_saves", exist_ok=True)
    
    def initialize_campaign(self, character_data: Dict[str, Any], campaign_name: str = None) -> Optional[Dict[str, Any]]:
        """Initialize a new campaign with character data."""
        try:
            campaign_id = str(uuid.uuid4())
            campaign_name = campaign_name or f"Campaign {campaign_id[:8]}"
            
            campaign_data = {
                "id": campaign_id,
                "name": campaign_name,
                "character": character_data,
                "created_date": datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat(),
                "conversation_history": [],
                "setting_introduction": self.generate_setting_introduction(character_data, campaign_name)
            }
            
            # Save campaign
            campaign_file = f"campaign_saves/{campaign_id}.json"
            with open(campaign_file, 'w') as f:
                json.dump(campaign_data, f, indent=2)
            
            return campaign_data
            
        except Exception as e:
            logger.error(f"Error initializing campaign: {e}")
            return None
    
    def generate_setting_introduction(self, character_data: Dict[str, Any], campaign_name: str) -> str:
        """Generate setting introduction for the campaign."""
        name = character_data.get('name', 'Adventurer')
        race = character_data.get('race', 'Human')
        character_class = character_data.get('class', 'Fighter')
        
        return f"""Welcome to your adventure, {name}!

You are a {race} {character_class} who has just arrived in the bustling town of Riverdale. The town is abuzz with rumors of strange happenings in the nearby forest - missing travelers, mysterious lights at night, and whispers of ancient ruins hidden among the trees.

As you walk through the town square, you notice a weathered notice board with various quests and requests from the townsfolk. The air is thick with anticipation and adventure.

What would you like to do first?"""
    
    def load_campaign(self, campaign_id: str) -> bool:
        """Load an existing campaign."""
        try:
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if os.path.exists(campaign_file):
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading campaign: {e}")
            return False
    
    def process_player_input(self, player_input: str, campaign_id: str) -> str:
        """Process player input and return DM response."""
        try:
            # Mock DM responses based on input
            input_lower = player_input.lower()
            
            if "hello" in input_lower or "greet" in input_lower:
                return "The townsfolk greet you warmly, though you can see curiosity in their eyes. 'Welcome to Riverdale, traveler! We don't see many adventurers these days.'"
            
            elif "quest" in input_lower or "job" in input_lower or "work" in input_lower:
                return "An elderly woman approaches you. 'Oh, thank goodness! We've been hoping for someone like you. My granddaughter went missing in the forest three days ago. Will you help us find her?'"
            
            elif "forest" in input_lower or "woods" in input_lower:
                return "The forest looms dark and mysterious ahead. Ancient trees tower overhead, their branches creating a natural canopy. You can hear strange sounds coming from within - the rustling of leaves, distant animal calls, and something else... something that doesn't sound quite natural."
            
            elif "inn" in input_lower or "tavern" in input_lower or "rest" in input_lower:
                return "The Prancing Pony Inn welcomes you with the warm glow of candlelight and the inviting smell of roasted meat. The innkeeper, a stout halfling named Barliman, waves you over. 'Welcome, friend! Room and board for the night?'"
            
            elif "shop" in input_lower or "buy" in input_lower or "equipment" in input_lower:
                return "The general store is well-stocked with adventuring gear. The shopkeeper, a knowledgeable gnome, eyes your equipment with interest. 'Looking to upgrade your gear? I've got the finest weapons and armor in town.'"
            
            else:
                return "You consider your options. The town offers many possibilities - you could seek out quests, explore the mysterious forest, rest at the inn, or visit the shops. What interests you most?"
            
        except Exception as e:
            logger.error(f"Error processing player input: {e}")
            return "Something unexpected happens. You feel a strange energy in the air..."
    
    def save_campaign(self, campaign_id: str) -> bool:
        """Save campaign data."""
        try:
            # Mock save - just return success
            return True
        except Exception as e:
            logger.error(f"Error saving campaign: {e}")
            return False
    
    def get_campaign_data(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign data."""
        try:
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if os.path.exists(campaign_file):
                with open(campaign_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error getting campaign data: {e}")
            return None

class MockUnifiedGame:
    """Mock unified game controller."""
    
    def __init__(self):
        self.character_generator = MockCharacterGenerator()
        self.narrative_bridge = MockNarrativeBridge()
    
    def get_saved_campaigns(self):
        """Get list of saved campaigns."""
        try:
            campaigns = []
            if os.path.exists("campaign_saves"):
                for filename in os.listdir("campaign_saves"):
                    if filename.endswith('.json'):
                        campaign_id = filename.replace('.json', '')
                        try:
                            with open(f"campaign_saves/{filename}", 'r') as f:
                                campaign_data = json.load(f)
                                campaigns.append({
                                    'id': campaign_id,
                                    'name': campaign_data.get('name', 'Unknown Campaign'),
                                    'character_name': campaign_data.get('character', {}).get('name', 'Unknown'),
                                    'created_date': campaign_data.get('created_date', ''),
                                    'last_updated': campaign_data.get('last_updated', '')
                                })
                        except Exception as e:
                            logger.error(f"Error reading campaign {filename}: {e}")
            return campaigns
        except Exception as e:
            logger.error(f"Error getting saved campaigns: {e}")
            return []
    
    def delete_campaign(self, campaign_id):
        """Delete a campaign."""
        try:
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if os.path.exists(campaign_file):
                os.remove(campaign_file)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting campaign: {e}")
            return False

# Global game instance
game = MockUnifiedGame()

@app.route('/')
def start_screen():
    """Start screen with campaign options."""
    return render_template('start_screen.html')

@app.route('/api/campaigns')
def list_campaigns():
    """List saved campaigns."""
    campaigns = game.get_saved_campaigns()
    return jsonify(campaigns)

@app.route('/api/campaigns/<campaign_id>/delete', methods=['POST'])
def delete_campaign(campaign_id):
    """Delete a campaign."""
    success = game.delete_campaign(campaign_id)
    return jsonify({'success': success})

@app.route('/api/campaigns/<campaign_id>/load', methods=['POST'])
def load_campaign(campaign_id):
    """Load a campaign."""
    try:
        success = game.narrative_bridge.load_campaign(campaign_id)
        if success:
            session['campaign_id'] = campaign_id
            return jsonify({'success': True, 'redirect': '/game'})
        else:
            return jsonify({'success': False, 'message': 'Campaign not found'})
    except Exception as e:
        logger.error(f"Error loading campaign: {e}")
        return jsonify({'success': False, 'message': 'Error loading campaign'})

@app.route('/character-creation')
def character_creation():
    """Step-by-step character creation."""
    return render_template('character_creation.html')

@app.route('/vibe-code-creation')
def vibe_code_creation():
    """Natural language character creation."""
    return render_template('vibe_code_creation.html')

@app.route('/api/character/vibe-code/start', methods=['POST'])
def start_vibe_code_creation():
    """Start the vibe code character creation process."""
    try:
        data = request.get_json()
        description = data.get('description', '')
        campaign_name = data.get('campaign_name', '')
        
        if not description:
            return jsonify({'success': False, 'message': 'Character description is required'})
        
        # Start character creation conversation
        result = game.character_generator.start_character_creation(description, campaign_name)
        
        if result['success']:
            # Store the character generator state in session
            session['character_creation_active'] = True
            session['campaign_name'] = campaign_name
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'is_complete': result['is_complete']
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to start character creation'})
    
    except Exception as e:
        logger.error(f"Error starting vibe code creation: {e}")
        return jsonify({'success': False, 'message': 'Error starting character creation'})

@app.route('/api/character/vibe-code/continue', methods=['POST'])
def continue_vibe_code_creation():
    """Continue the vibe code character creation conversation."""
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        
        if not user_input:
            return jsonify({'success': False, 'message': 'User input is required'})
        
        # Continue character creation conversation
        result = game.character_generator.continue_conversation(user_input)
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'is_complete': result['is_complete']
        })
    
    except Exception as e:
        logger.error(f"Error continuing vibe code creation: {e}")
        return jsonify({'success': False, 'message': 'Error continuing character creation'})

@app.route('/api/character/vibe-code/complete', methods=['POST'])
def complete_vibe_code_creation():
    """Complete character creation and start campaign."""
    try:
        # Get character data
        character_data = game.character_generator.get_character_data()
        campaign_name = session.get('campaign_name', 'New Campaign')
        
        if not character_data:
            return jsonify({'success': False, 'message': 'No character data available'})
        
        # Initialize campaign
        campaign_data = game.narrative_bridge.initialize_campaign(character_data, campaign_name)
        
        if campaign_data:
            # Clear session data
            session.pop('character_creation_active', None)
            session.pop('campaign_name', None)
            session['campaign_id'] = campaign_data['id']
            
            return jsonify({
                'success': True,
                'message': 'Character created and campaign started!',
                'redirect': '/game'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to start campaign'})
    
    except Exception as e:
        logger.error(f"Error completing vibe code creation: {e}")
        return jsonify({'success': False, 'message': 'Error completing character creation'})

@app.route('/api/character/create', methods=['POST'])
def create_character():
    """Create character using step-by-step form."""
    try:
        data = request.get_json()
        
        # Extract character data from form
        character_data = {
            'name': data.get('name', 'Adventurer'),
            'race': data.get('race', 'Human'),
            'class': data.get('class', 'Fighter'),
            'level': int(data.get('level', 1)),
            'background': data.get('background', 'Adventurer'),
            'personality': data.get('personality', 'A brave adventurer'),
            'created_date': datetime.datetime.now().isoformat()
        }
        
        campaign_name = data.get('campaign_name', 'New Campaign')
        
        # Initialize campaign
        campaign_data = game.narrative_bridge.initialize_campaign(character_data, campaign_name)
        
        if campaign_data:
            session['campaign_id'] = campaign_data['id']
            return jsonify({
                'success': True,
                'message': 'Character created and campaign started!',
                'redirect': '/game'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to start campaign'})
    
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        return jsonify({'success': False, 'message': 'Error creating character'})

@app.route('/game')
def game_screen():
    """Main game interface - pure conversation."""
    return render_template('game_screen.html')

@app.route('/api/game/action', methods=['POST'])
def process_game_action():
    """Process player action in the game."""
    try:
        data = request.get_json()
        player_input = data.get('input', '')
        campaign_id = session.get('campaign_id')
        
        if not player_input:
            return jsonify({'success': False, 'message': 'Player input is required'})
        
        if not campaign_id:
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        # Process player input
        dm_response = game.narrative_bridge.process_player_input(player_input, campaign_id)
        
        # Save campaign
        game.narrative_bridge.save_campaign(campaign_id)
        
        return jsonify({
            'success': True,
            'response': dm_response
        })
    
    except Exception as e:
        logger.error(f"Error processing game action: {e}")
        return jsonify({'success': False, 'message': 'Error processing action'})

@app.route('/api/game/save', methods=['POST'])
def save_game():
    """Save current game state."""
    try:
        campaign_id = session.get('campaign_id')
        if not campaign_id:
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        success = game.narrative_bridge.save_campaign(campaign_id)
        return jsonify({'success': success})
    
    except Exception as e:
        logger.error(f"Error saving game: {e}")
        return jsonify({'success': False, 'message': 'Error saving game'})

@app.route('/api/game/current')
def get_current_game():
    """Get current game state."""
    try:
        campaign_id = session.get('campaign_id')
        if not campaign_id:
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        campaign_data = game.narrative_bridge.get_campaign_data(campaign_id)
        if not campaign_data:
            return jsonify({'success': False, 'message': 'Campaign not found'})
        
        return jsonify({
            'success': True,
            'campaign': campaign_data
        })
    
    except Exception as e:
        logger.error(f"Error getting current game: {e}")
        return jsonify({'success': False, 'message': 'Error getting game state'})

if __name__ == '__main__':
    print("🎲 Starting Mock Unified Solo DnD 5E Narrative Interface...")
    print("Access the game at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5001, debug=True) 