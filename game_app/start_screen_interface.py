#!/usr/bin/env python3
"""
Start Screen Interface for SoloHeart
Handles the initial game flow: campaign management and character creation.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_session import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'start-screen-key')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = 'flask_session'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
Session(app)
CORS(app)

class StartScreenManager:
    """Manages the start screen flow and campaign operations."""
    
    def __init__(self):
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure necessary directories exist."""
        directories = ['campaign_saves', 'character_saves']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
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
                                'last_modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                                'character_name': campaign_data.get('active_character', {}).get('name', 'Unknown')
                            })
                        except Exception as e:
                            logger.error(f"Error reading campaign {campaign_id}: {e}")
                            # Still include it but mark as corrupted
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
            
            # Delete associated files (character arcs, plot threads, etc.)
            associated_files = [
                f'character_arcs_{campaign_id}.jsonl',
                f'plot_threads_{campaign_id}.jsonl',
                f'journal_entries_{campaign_id}.jsonl',
                f'orchestrator_{campaign_id}.jsonl',
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
    
    def create_new_campaign(self, character_data, campaign_name=None):
        """Create a new campaign with the given character."""
        try:
            if not campaign_name:
                campaign_name = f"Adventure of {character_data.get('name', 'the Hero')}"
            
            campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            campaign_data = {
                'campaign_id': campaign_id,
                'name': campaign_name,
                'created_date': datetime.now().isoformat(),
                'active_character': character_data,
                'conversation_history': [],
                'world_state': {},
                'session_memory': []
            }
            
            # Save the campaign
            filename = f"campaign_saves/{campaign_id}.json"
            with open(filename, 'w') as f:
                json.dump(campaign_data, f, indent=2)
            
            return campaign_data
        except Exception as e:
            logger.error(f"Error creating new campaign: {e}")
            return None

# Initialize manager
start_manager = StartScreenManager()

@app.route('/')
def start_screen():
    """Main start screen."""
    return render_template('start_screen.html')

@app.route('/api/campaigns')
def list_campaigns():
    """List all saved campaigns."""
    campaigns = start_manager.get_saved_campaigns()
    return jsonify({'success': True, 'campaigns': campaigns})

@app.route('/api/campaigns/<campaign_id>/delete', methods=['POST'])
def delete_campaign(campaign_id):
    """Delete a campaign."""
    success = start_manager.delete_campaign(campaign_id)
    return jsonify({'success': success})

@app.route('/api/campaigns/<campaign_id>/load', methods=['POST'])
def load_campaign(campaign_id):
    """Load a campaign and redirect to game."""
    try:
        session['campaign_id'] = campaign_id
        return jsonify({'success': True, 'redirect': '/game'})
    except Exception as e:
        logger.error(f"Error loading campaign: {e}")
        return jsonify({'success': False, 'message': 'Error loading campaign'})

@app.route('/character-creation')
def character_creation():
    """Character creation screen."""
    return render_template('character_creation.html')

@app.route('/api/character/create/start', methods=['POST'])
def start_character_creation():
    """Start the character creation process."""
    try:
        data = request.get_json()
        description = data.get('description', '')
        campaign_name = data.get('campaign_name', '')
        
        if not description:
            return jsonify({'success': False, 'message': 'Character description is required'})
        
        # Initialize character creation state
        session['character_creation_state'] = {
            'description': description,
            'campaign_name': campaign_name,
            'step': 'race',
            'character_data': {
                'description': description,
                'name': '',
                'race': '',
                'class': '',
                'level': 1,
                'background': '',
                'personality': '',
                'ability_scores': {'str': 10, 'dex': 10, 'con': 10, 'int': 10, 'wis': 10, 'cha': 10},
                'hit_points': 10,
                'armor_class': 10
            }
        }
        
        response = f"I understand you want to create a character described as: '{description}'. Let me ask you some questions to flesh out the details. What race would you like to play?"
        
        return jsonify({
            'success': True,
            'message': response,
            'is_complete': False
        })
    
    except Exception as e:
        logger.error(f"Error starting character creation: {e}")
        return jsonify({'success': False, 'message': 'Error starting character creation'})

@app.route('/api/character/create/continue', methods=['POST'])
def continue_character_creation():
    """Continue the character creation conversation."""
    try:
        data = request.get_json()
        player_input = data.get('input', '')
        
        if not player_input:
            return jsonify({'success': False, 'message': 'Input is required'})
        
        # Debug session info
        logger.info(f"Session ID: {session.get('_id', 'No ID')}")
        logger.info(f"All session keys: {list(session.keys())}")
        
        # Get current state
        state = session.get('character_creation_state', {})
        if not state:
            return jsonify({'success': False, 'message': 'Character creation session not found. Please start over.'})
        
        current_step = state.get('step', 'race')
        character_data = state.get('character_data', {})
        
        logger.info(f"Processing step: {current_step}, input: {player_input}")
        logger.info(f"Current state before processing: {state}")
        
        # Process input based on current step
        if current_step == 'race':
            # Validate race input
            valid_races = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling']
            if player_input.title() in valid_races:
                character_data['race'] = player_input.title()
                state['step'] = 'class'
                state['character_data'] = character_data
                session['character_creation_state'] = state
                session.modified = True
                logger.info(f"Updated state after race: {state}")
                logger.info(f"Session after update: {session.get('character_creation_state', 'NOT FOUND')}")
                response = f"Great! A {character_data['race']}. Now, what class would you like to play?"
            else:
                response = f"I didn't recognize '{player_input}' as a valid race. Please choose from: {', '.join(valid_races)}"
        
        elif current_step == 'class':
            # Validate class input
            valid_classes = ['Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard']
            if player_input.title() in valid_classes:
                character_data['class'] = player_input.title()
                state['step'] = 'name'
                state['character_data'] = character_data
                session['character_creation_state'] = state
                session.modified = True
                logger.info(f"Updated state after class: {state}")
                response = f"Excellent! A {character_data['class']}. What is your character's name?"
            else:
                response = f"I didn't recognize '{player_input}' as a valid class. Please choose from: {', '.join(valid_classes)}"
        
        elif current_step == 'name':
            character_data['name'] = player_input.strip()
            state['step'] = 'background'
            state['character_data'] = character_data
            session['character_creation_state'] = state
            session.modified = True
            logger.info(f"Updated state after name: {state}")
            response = f"Nice to meet you, {character_data['name']}! What background does your character have? (e.g., Acolyte, Criminal, Folk Hero, Noble, Sage, Soldier)"
        
        elif current_step == 'background':
            character_data['background'] = player_input.strip()
            state['step'] = 'personality'
            state['character_data'] = character_data
            session['character_creation_state'] = state
            session.modified = True
            logger.info(f"Updated state after background: {state}")
            response = f"Interesting background! Now, tell me about {character_data['name']}'s personality. What are they like?"
        
        elif current_step == 'personality':
            character_data['personality'] = player_input.strip()
            state['step'] = 'complete'
            state['character_data'] = character_data
            session['character_creation_state'] = state
            session.modified = True
            logger.info(f"Updated state after personality: {state}")
            response = f"Perfect! I have enough information to create your character. Let me finalize {character_data['name']} the {character_data['race']} {character_data['class']}..."
        
        # Check if character creation is complete
        if state['step'] == 'complete':
            # Create the character and campaign
            campaign_data = start_manager.create_new_campaign(character_data, state.get('campaign_name', ''))
            if campaign_data:
                session['campaign_id'] = campaign_data['campaign_id']
                # Clear character creation state
                session.pop('character_creation_state', None)
                session.modified = True
                
                response += f"\n\n✅ Character created successfully!\n\n{character_data['name']} the {character_data['race']} {character_data['class']} is ready for adventure!"
                
                return jsonify({
                    'success': True,
                    'message': response,
                    'is_complete': True,
                    'character_data': character_data
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Error creating character. Please try again.'
                })
        
        return jsonify({
            'success': True,
            'message': response,
            'is_complete': False
        })
    
    except Exception as e:
        logger.error(f"Error continuing character creation: {e}")
        return jsonify({'success': False, 'message': 'Error continuing character creation'})

@app.route('/api/character/create', methods=['POST'])
def create_character():
    """Create a character and start new campaign (step-by-step method)."""
    try:
        data = request.get_json()
        
        # Extract character data from form
        character_data = {
            'name': data.get('name'),
            'race': data.get('race'),
            'class': data.get('class'),
            'level': data.get('level'),
            'background': data.get('background', 'Adventurer'),
            'personality': data.get('personality', 'A brave adventurer seeking fortune and glory.'),
            'stats': {
                'strength': data.get('str', 10),
                'dexterity': data.get('dex', 10),
                'constitution': data.get('con', 10),
                'intelligence': data.get('int', 10),
                'wisdom': data.get('wis', 10),
                'charisma': data.get('cha', 10)
            },
            'hit_points': data.get('hp', 10),
            'armor_class': 10,  # Default AC
            'saving_throws': data.get('savingThrows', ''),
            'skills': data.get('skills', ''),
            'feats': data.get('feats', ''),
            'weapons': data.get('weapons', ''),
            'gear': data.get('gear', ''),
            'spells': data.get('spells', ''),
            'background_freeform': data.get('backgroundFreeform', '')
        }
        
        campaign_name = data.get('campaign_name', 'New Adventure')
        
        # Validate required fields
        required_fields = ['name', 'class', 'race', 'level']
        for field in required_fields:
            if not character_data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'})
        
        # Create campaign with character
        campaign_data = start_manager.create_new_campaign(character_data, campaign_name)
        
        if campaign_data:
            session['campaign_id'] = campaign_data['campaign_id']
            return jsonify({'success': True, 'redirect': '/game'})
        else:
            return jsonify({'success': False, 'message': 'Failed to create campaign'})
    
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        return jsonify({'success': False, 'message': 'Error creating character'})

@app.route('/game')
def game_screen():
    """Main game screen."""
    if 'campaign_id' not in session:
        return redirect('/')
    
    # For now, just show a simple game interface
    return render_template('game_interface.html')

if __name__ == '__main__':
    print("🎲 Starting SoloHeart - Start Screen Interface...")
    print("Access the game at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5001) 