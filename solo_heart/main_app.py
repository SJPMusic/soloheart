#!/usr/bin/env python3
"""
SoloHeart Main Application
Core Flask app for SoloHeart game interface.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'soloheart-secret-key-2024'
CORS(app)

class SoloHeartGame:
    """Main game controller for SoloHeart."""
    
    def __init__(self):
        self.current_campaign = None
        self.active_character = None
        self.conversation_history = []
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure necessary directories exist."""
        directories = ['campaign_saves', 'character_saves', 'logs']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def create_default_character(self):
        """Create a default character for new games."""
        return {
            'id': 'player',
            'name': 'Adventurer',
            'class': 'Fighter',
            'race': 'Human',
            'level': 1,
            'stats': {
                'strength': 15,
                'dexterity': 14,
                'constitution': 13,
                'intelligence': 10,
                'wisdom': 12,
                'charisma': 8
            },
            'hit_points': 12,
            'armor_class': 16,
            'background': 'Soldier',
            'alignment': 'Lawful Good'
        }
    
    def start_new_campaign(self, character_data=None):
        """Start a new campaign."""
        if character_data is None:
            character_data = self.create_default_character()
        
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_campaign = {
            'campaign_id': campaign_id,
            'name': 'New Adventure',
            'created_date': datetime.now().isoformat(),
            'active_character': character_data,
            'conversation_history': [],
            'world_state': {},
            'session_memory': []
        }
        
        self.active_character = character_data
        self.conversation_history = []
        
        return self.current_campaign
    
    def process_player_input(self, player_input):
        """Process player input and return DM response."""
        if not self.current_campaign:
            return "I'm sorry, but no campaign is currently active. Please start a new game."
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'speaker': 'player',
            'content': player_input
        })
        
        # Generate DM response (placeholder for now)
        dm_response = f"You say: '{player_input}'. As your Dungeon Master, I acknowledge your action and will respond accordingly. This is a placeholder response - the full narrative engine integration would provide a rich, contextual response based on your character, the world state, and our conversation history."
        
        # Add DM response to history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'speaker': 'dm',
            'content': dm_response
        })
        
        return dm_response
    
    def save_campaign(self):
        """Save current campaign state."""
        if not self.current_campaign:
            return False
        
        try:
            filename = f"campaign_saves/{self.current_campaign['campaign_id']}.json"
            with open(filename, 'w') as f:
                json.dump(self.current_campaign, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving campaign: {e}")
            return False
    
    def load_campaign(self, campaign_id):
        """Load a saved campaign."""
        try:
            filename = f"campaign_saves/{campaign_id}.json"
            with open(filename, 'r') as f:
                campaign_data = json.load(f)
            
            self.current_campaign = campaign_data
            self.active_character = campaign_data['active_character']
            self.conversation_history = campaign_data.get('conversation_history', [])
            
            return True
        except Exception as e:
            logger.error(f"Error loading campaign: {e}")
            return False
    
    def get_saved_campaigns(self):
        """Get list of saved campaigns."""
        campaigns = []
        try:
            if os.path.exists('campaign_saves'):
                for filename in os.listdir('campaign_saves'):
                    if filename.endswith('.json'):
                        campaign_id = filename.replace('.json', '')
                        campaigns.append({
                            'id': campaign_id,
                            'name': f'Campaign {campaign_id}'
                        })
        except Exception as e:
            logger.error(f"Error listing campaigns: {e}")
        
        return campaigns

# Initialize game controller
game = SoloHeartGame()

@app.route('/')
def index():
    """Main game interface."""
    if not game.current_campaign:
        return redirect(url_for('start_screen'))
    
    return render_template('game_interface.html')

@app.route('/start')
def start_screen():
    """Start screen for campaign management."""
    return render_template('start_screen.html')

@app.route('/api/campaigns')
def list_campaigns():
    """List all saved campaigns."""
    campaigns = game.get_saved_campaigns()
    return jsonify({'success': True, 'campaigns': campaigns})

@app.route('/api/campaigns/new', methods=['POST'])
def create_campaign():
    """Create a new campaign."""
    try:
        data = request.get_json()
        character_data = data.get('character_data')
        campaign_name = data.get('campaign_name', 'New Adventure')
        
        campaign_data = game.start_new_campaign(character_data)
        session['campaign_id'] = campaign_data['campaign_id']
        
        return jsonify({
            'success': True,
            'campaign': campaign_data
        })
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        return jsonify({'success': False, 'message': 'Error creating campaign'})

@app.route('/api/campaigns/<campaign_id>/load', methods=['POST'])
def load_campaign(campaign_id):
    """Load a specific campaign."""
    success = game.load_campaign(campaign_id)
    if success:
        session['campaign_id'] = campaign_id
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to load campaign'})

@app.route('/api/campaigns/<campaign_id>/delete', methods=['POST'])
def delete_campaign(campaign_id):
    """Delete a campaign."""
    try:
        filename = f"campaign_saves/{campaign_id}.json"
        if os.path.exists(filename):
            os.remove(filename)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Campaign not found'})
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        return jsonify({'success': False, 'message': 'Error deleting campaign'})

@app.route('/api/campaign/current')
def get_current_campaign():
    """Get current campaign data."""
    if game.current_campaign:
        return jsonify({
            'success': True,
            'campaign': game.current_campaign
        })
    else:
        return jsonify({'success': False, 'message': 'No active campaign'})

@app.route('/api/campaign/action', methods=['POST'])
def process_action():
    """Process player action and return DM response."""
    try:
        data = request.get_json()
        player_input = data.get('action', '').strip()
        
        if not player_input:
            return jsonify({'success': False, 'message': 'No action provided'})
        
        # Process the input
        dm_response = game.process_player_input(player_input)
        
        return jsonify({
            'success': True,
            'dm_response': dm_response,
            'character_info': game.active_character
        })
        
    except Exception as e:
        logger.error(f"Error processing action: {e}")
        return jsonify({
            'success': False,
            'message': 'Error processing action'
        })

@app.route('/api/campaign/save', methods=['POST'])
def save_campaign():
    """Save current campaign."""
    success = game.save_campaign()
    return jsonify({'success': success})

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'campaign_active': game.current_campaign is not None
    })

if __name__ == '__main__':
    print("🎲 Starting SoloHeart Main Application...")
    print("Access the game at: http://localhost:5003")
    print("Press Ctrl+C to stop the server")
    app.run(debug=False, host='0.0.0.0', port=5003) 