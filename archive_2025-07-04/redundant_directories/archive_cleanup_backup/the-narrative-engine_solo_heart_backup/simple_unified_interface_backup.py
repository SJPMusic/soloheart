#!/usr/bin/env python3
"""
Simple Unified Solo DnD 5E Narrative Interface
A single Flask server that provides the complete immersive solo DnD experience.
"""

import os
import json
import logging
import uuid
import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'unified-narrative-key')

class SimpleCharacterGenerator:
    """Simple character generator for vibe code creation."""
    
    def __init__(self):
        self.conversation_history = []
        self.character_data = {}
        self.is_complete = False
    
    def start_character_creation(self, description: str, campaign_name: str = "") -> Dict[str, Any]:
        """Start character creation conversation."""
        try:
            system_prompt = """You are a helpful DnD 5e character creation assistant. Your job is to help players create characters through natural conversation.

When a player describes their character concept, ask clarifying questions to gather all necessary information:
- Name
- Race (Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling)
- Class (Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard)
- Level (1-5)
- Background (Acolyte, Criminal, Folk Hero, Noble, Sage, Soldier, or custom)
- Personality traits
- Appearance
- Backstory

Ask one or two questions at a time. Be conversational and helpful. When you have all the information, say "Character creation complete!" and provide a summary."""
            
            user_message = f"I want to create a character. Here's my concept: {description}"
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Store conversation
            self.conversation_history = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": ai_response}
            ]
            
            return {
                "success": True,
                "message": ai_response,
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
            
            # Check if this looks like completion
            if "complete" in user_input.lower() or "done" in user_input.lower():
                # Try to extract character data from conversation
                character_data = self._extract_character_data()
                if character_data:
                    self.character_data = character_data
                    self.is_complete = True
                    return {
                        "success": True,
                        "message": "Character creation complete! Your character has been created successfully.",
                        "is_complete": True
                    }
            
            # Continue conversation
            messages = [
                {"role": "system", "content": "You are a helpful DnD 5e character creation assistant. Continue the conversation naturally. When you have all the information, say 'Character creation complete!' and provide a summary."}
            ] + self.conversation_history
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Check if AI says it's complete
            if "character creation complete" in ai_response.lower():
                character_data = self._extract_character_data()
                if character_data:
                    self.character_data = character_data
                    self.is_complete = True
            
            return {
                "success": True,
                "message": ai_response,
                "is_complete": self.is_complete
            }
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return {
                "success": False,
                "message": "Error continuing conversation. Please try again."
            }
    
    def _extract_character_data(self) -> Optional[Dict[str, Any]]:
        """Extract character data from conversation history."""
        try:
            # Simple extraction - look for key information in the conversation
            conversation_text = " ".join([msg["content"] for msg in self.conversation_history])
            
            # Extract basic info using simple patterns
            import re
            
            # Name - look for "name is" or "called" patterns
            name_match = re.search(r'(?:name is|called|named)\s+([A-Z][a-z]+)', conversation_text, re.IGNORECASE)
            name = name_match.group(1) if name_match else "Adventurer"
            
            # Race - look for race mentions
            races = ["Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome", "Half-Elf", "Half-Orc", "Tiefling"]
            race = "Human"
            for r in races:
                if r.lower() in conversation_text.lower():
                    race = r
                    break
            
            # Class - look for class mentions
            classes = ["Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"]
            character_class = "Fighter"
            for c in classes:
                if c.lower() in conversation_text.lower():
                    character_class = c
                    break
            
            # Level - default to 1
            level = 1
            
            # Background - default to Adventurer
            background = "Adventurer"
            
            return {
                "name": name,
                "race": race,
                "class": character_class,
                "level": level,
                "background": background,
                "personality": f"A {race} {character_class} named {name}",
                "created_date": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting character data: {e}")
            return None
    
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

class SimpleNarrativeBridge:
    """Simple narrative bridge for basic DnD functionality."""
    
    def __init__(self):
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure necessary directories exist."""
        directories = ['campaign_saves', 'character_saves']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def initialize_campaign(self, character_data: Dict[str, Any], campaign_name: str = None) -> Optional[Dict[str, Any]]:
        """Initialize a new campaign with the given character."""
        try:
            if not campaign_name:
                campaign_name = f"Adventure of {character_data.get('name', 'the Hero')}"
            
            campaign_id = f"campaign-{uuid.uuid4().hex[:8]}"
            
            # Save character data
            character_file = f"character_saves/{campaign_id}_character.json"
            with open(character_file, 'w') as f:
                json.dump(character_data, f, indent=2)
            
            # Create campaign data
            campaign_data = {
                "campaign_id": campaign_id,
                "name": campaign_name,
                "created_date": datetime.datetime.now().isoformat(),
                "active_character": character_data,
                "session_count": 0,
                "current_location": "Starting Area",
                "world_state": {}
            }
            
            # Save campaign data
            campaign_file = f"campaign_saves/{campaign_id}.json"
            with open(campaign_file, 'w') as f:
                json.dump(campaign_data, f, indent=2)
            
            logger.info(f"Initialized campaign: {campaign_id}")
            return campaign_data
            
        except Exception as e:
            logger.error(f"Error initializing campaign: {e}")
            return None
    
    def generate_setting_introduction(self, character_data: Dict[str, Any], campaign_name: str) -> str:
        """Generate LLM-created setting introduction."""
        try:
            prompt = f"""
            You are a master storyteller creating an immersive opening scene for a DnD 5e solo adventure.
            
            Character: {character_data.get('name', 'the Hero')} - a {character_data.get('race', 'adventurer')} {character_data.get('class', 'hero')}
            Campaign: {campaign_name}
            
            Create a vivid, atmospheric opening scene that introduces the character to their adventure. 
            This should be 2-3 paragraphs that set the mood, establish the immediate environment, 
            and hint at the adventure to come. Make it feel like the opening of an epic fantasy novel.
            
            Focus on:
            - Sensory details (sights, sounds, smells)
            - Atmospheric mood
            - Immediate surroundings
            - A sense of mystery or adventure
            - The character's current situation
            
            Write in third person, present tense, as if narrating the scene to the player.
            """
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a master DnD storyteller creating immersive opening scenes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating setting introduction: {e}")
            return f"You find yourself in a mysterious land, ready to begin your adventure as {character_data.get('name', 'a hero')}..."
    
    def load_campaign(self, campaign_id: str) -> bool:
        """Load an existing campaign."""
        try:
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if not os.path.exists(campaign_file):
                logger.error(f"Campaign file not found: {campaign_file}")
                return False
            
            logger.info(f"Loaded campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading campaign: {e}")
            return False
    
    def process_player_input(self, player_input: str, campaign_id: str) -> str:
        """Process player input and return DM response."""
        try:
            prompt = f"""
            You are a Dungeon Master running a solo DnD 5e adventure. The player has just said: "{player_input}"
            
            Respond as a DM would, describing what happens next, asking for clarification if needed, 
            and moving the story forward. Be descriptive, atmospheric, and engaging.
            
            Keep your response to 2-3 paragraphs maximum. Focus on the immediate consequences and 
            what the player sees/hears/experiences.
            """
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an experienced Dungeon Master running a solo DnD 5e adventure. Be descriptive, atmospheric, and engaging."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error processing player input: {e}")
            return "I'm sorry, but I'm having trouble processing that right now. Please try again."
    
    def save_campaign(self, campaign_id: str) -> bool:
        """Save current campaign state."""
        try:
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if os.path.exists(campaign_file):
                with open(campaign_file, 'r') as f:
                    campaign_data = json.load(f)
                
                campaign_data["last_modified"] = datetime.datetime.now().isoformat()
                campaign_data["session_count"] = campaign_data.get("session_count", 0) + 1
                
                with open(campaign_file, 'w') as f:
                    json.dump(campaign_data, f, indent=2)
            
            logger.info(f"Saved campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving campaign: {e}")
            return False
    
    def get_campaign_data(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign data."""
        try:
            campaign_file = f"campaign_saves/{campaign_id}.json"
            if not os.path.exists(campaign_file):
                return None
            
            with open(campaign_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error getting campaign data: {e}")
            return None

class SimpleUnifiedGame:
    """Simple unified game manager."""
    
    def __init__(self):
        self.character_generator = SimpleCharacterGenerator()
        self.narrative_bridge = SimpleNarrativeBridge()
    
    def get_saved_campaigns(self):
        """Get list of all saved campaigns."""
        campaigns = []
        try:
            if os.path.exists('campaign_saves'):
                for filename in os.listdir('campaign_saves'):
                    if filename.endswith('.json'):
                        campaign_id = filename.replace('.json', '')
                        filepath = os.path.join('campaign_saves', filename)
                        
                        try:
                            with open(filepath, 'r') as f:
                                campaign_data = json.load(f)
                            
                            campaigns.append({
                                'id': campaign_id,
                                'name': campaign_data.get('name', f'Campaign {campaign_id}'),
                                'created_date': campaign_data.get('created_date', 'Unknown'),
                                'last_modified': datetime.datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                                'character_name': campaign_data.get('active_character', {}).get('name', 'Unknown')
                            })
                        except Exception as e:
                            logger.error(f"Error reading campaign {campaign_id}: {e}")
                            campaigns.append({
                                'id': campaign_id,
                                'name': f'Campaign {campaign_id} (Corrupted)',
                                'created_date': 'Unknown',
                                'last_modified': 'Unknown',
                                'character_name': 'Unknown'
                            })
        except Exception as e:
            logger.error(f"Error listing campaigns: {e}")
        
        return sorted(campaigns, key=lambda x: x['last_modified'], reverse=True)
    
    def delete_campaign(self, campaign_id):
        """Delete a campaign and all its associated files."""
        try:
            # Delete main campaign file
            campaign_file = os.path.join('campaign_saves', f'{campaign_id}.json')
            if os.path.exists(campaign_file):
                os.remove(campaign_file)
            
            # Delete associated files
            associated_files = [
                f'{campaign_id}_character.json'
            ]
            
            for filename in associated_files:
                filepath = os.path.join('character_saves', filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            return True
        except Exception as e:
            logger.error(f"Error deleting campaign {campaign_id}: {e}")
            return False

# Initialize game manager
game = SimpleUnifiedGame()

@app.route('/')
def start_screen():
    """Start screen - the only gamified portion of the UI."""
    return render_template('start_screen.html')

@app.route('/api/campaigns')
def list_campaigns():
    """List all saved campaigns."""
    campaigns = game.get_saved_campaigns()
    return jsonify({'success': True, 'campaigns': campaigns})

@app.route('/api/campaigns/<campaign_id>/delete', methods=['POST'])
def delete_campaign(campaign_id):
    """Delete a campaign."""
    success = game.delete_campaign(campaign_id)
    return jsonify({'success': success})

@app.route('/api/campaigns/<campaign_id>/load', methods=['POST'])
def load_campaign(campaign_id):
    """Load a campaign and redirect to game."""
    try:
        success = game.narrative_bridge.load_campaign(campaign_id)
        if success:
            session['campaign_id'] = campaign_id
            return jsonify({'success': True, 'redirect': '/game'})
        else:
            return jsonify({'success': False, 'message': 'Failed to load campaign'})
    except Exception as e:
        logger.error(f"Error loading campaign: {e}")
        return jsonify({'success': False, 'message': 'Error loading campaign'})

@app.route('/character-creation')
def character_creation():
    """Character creation screen with two options."""
    return render_template('character_creation.html')

@app.route('/vibe-code-creation')
def vibe_code_creation():
    """Vibe code character creation interface."""
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
        player_input = data.get('input', '')
        
        if not player_input:
            return jsonify({'success': False, 'message': 'Input is required'})
        
        # Continue the conversation
        result = game.character_generator.continue_conversation(player_input)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'is_complete': result['is_complete']
            })
        else:
            return jsonify({'success': False, 'message': result['message']})
    
    except Exception as e:
        logger.error(f"Error continuing vibe code creation: {e}")
        return jsonify({'success': False, 'message': 'Error continuing character creation'})

@app.route('/api/character/vibe-code/complete', methods=['POST'])
def complete_vibe_code_creation():
    """Complete the vibe code character creation and generate setting introduction."""
    try:
        if not game.character_generator.is_complete:
            return jsonify({'success': False, 'message': 'Character creation is not complete'})
        
        # Get the completed character data
        character_data = game.character_generator.get_character_data()
        campaign_name = session.get('campaign_name', '')
        
        # Create the campaign
        campaign_data = game.narrative_bridge.initialize_campaign(character_data, campaign_name)
        
        if campaign_data:
            # Generate LLM-created setting introduction
            setting_introduction = game.narrative_bridge.generate_setting_introduction(character_data, campaign_name)
            
            # Save the character data
            game.character_generator.save_character(campaign_data['campaign_id'])
            
            # Set session and redirect
            session['campaign_id'] = campaign_data['campaign_id']
            session['setting_introduction'] = setting_introduction
            session.pop('character_creation_active', None)
            session.pop('campaign_name', None)
            
            return jsonify({
                'success': True,
                'redirect': '/game',
                'character': character_data,
                'setting_introduction': setting_introduction
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to create campaign'})
    
    except Exception as e:
        logger.error(f"Error completing vibe code creation: {e}")
        return jsonify({'success': False, 'message': 'Error completing character creation'})

@app.route('/api/character/create', methods=['POST'])
def create_character():
    """Create a character and start new campaign (step-by-step method)."""
    try:
        data = request.get_json()
        creation_method = data.get('method')  # 'step_by_step' or 'vibe_code'
        
        if creation_method == 'step_by_step':
            # Handle step-by-step character creation
            character_data = data.get('character_data', {})
            campaign_name = data.get('campaign_name', '')
            
            # Validate required fields
            required_fields = ['name', 'class', 'race', 'level']
            for field in required_fields:
                if not character_data.get(field):
                    return jsonify({'success': False, 'message': f'Missing required field: {field}'})
            
            # Create campaign with character
            campaign_data = game.narrative_bridge.initialize_campaign(character_data, campaign_name)
            
            if campaign_data:
                # Generate setting introduction
                setting_introduction = game.narrative_bridge.generate_setting_introduction(character_data, campaign_name)
                session['campaign_id'] = campaign_data['campaign_id']
                session['setting_introduction'] = setting_introduction
                return jsonify({'success': True, 'redirect': '/game'})
            else:
                return jsonify({'success': False, 'message': 'Failed to create campaign'})
        
        elif creation_method == 'vibe_code':
            # Redirect to vibe code creation interface
            return jsonify({'success': True, 'redirect': '/vibe-code-creation'})
        
        else:
            return jsonify({'success': False, 'message': 'Invalid creation method'})
    
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        return jsonify({'success': False, 'message': 'Error creating character'})

@app.route('/game')
def game_screen():
    """Main game screen - pure narrative experience."""
    if 'campaign_id' not in session:
        return redirect('/')
    
    return render_template('game_screen.html')

@app.route('/api/game/action', methods=['POST'])
def process_game_action():
    """Process player action and return LLM DM response."""
    try:
        data = request.get_json()
        player_input = data.get('action', '').strip()
        
        if not player_input:
            return jsonify({'success': False, 'message': 'No action provided'})
        
        campaign_id = session.get('campaign_id')
        if not campaign_id:
            return jsonify({'success': False, 'message': 'No active campaign'})
        
        # Process the input through the narrative bridge
        response = game.narrative_bridge.process_player_input(player_input, campaign_id)
        
        return jsonify({
            'success': True,
            'dm_response': response
        })
        
    except Exception as e:
        logger.error(f"Error processing action: {e}")
        return jsonify({
            'success': False,
            'message': 'Error processing action. Please try again.'
        })

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
        setting_introduction = session.get('setting_introduction', '')
        
        return jsonify({
            'success': True,
            'campaign': campaign_data,
            'setting_introduction': setting_introduction
        })
        
    except Exception as e:
        logger.error(f"Error getting current game: {e}")
        return jsonify({'success': False, 'message': 'Error getting game state'})

if __name__ == '__main__':
    print("Starting Simple Unified Solo DnD 5E Narrative Interface...")
    print("Access the game at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5001)
