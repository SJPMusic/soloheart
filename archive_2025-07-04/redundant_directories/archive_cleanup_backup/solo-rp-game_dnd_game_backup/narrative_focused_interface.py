#!/usr/bin/env python3
"""
Narrative-Focused Solo DnD 5E Interface
A simplified, conversation-driven interface that aligns with the original vision
of a pure narrative experience with minimal gamification.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'narrative-focused-key')

class NarrativeFocusedInterface:
    """Simplified interface focused purely on narrative conversation."""
    
    def __init__(self):
        self.current_campaign = None
        self.active_character = None
        self.conversation_history = []
        
    def start_new_campaign(self, character_data=None):
        """Start a new campaign with minimal setup."""
        campaign_id = f"narrative-campaign-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create basic campaign structure
        campaign_data = {
            'campaign_id': campaign_id,
            'name': 'Narrative Adventure',
            'created_date': datetime.now().isoformat(),
            'active_character': character_data or self._create_default_character(),
            'conversation_history': [],
            'world_state': {},
            'session_memory': []
        }
        
        self.current_campaign = campaign_data
        self.active_character = campaign_data['active_character']
        
        return campaign_data
    
    def _create_default_character(self):
        """Create a simple default character."""
        return {
            'id': 'player',
            'name': 'Adventurer',
            'class': 'Fighter',
            'level': 1,
            'stats': {
                'strength': 15,
                'dexterity': 14,
                'constitution': 13,
                'intelligence': 10,
                'wisdom': 12,
                'charisma': 8
            }
        }
    
    def process_player_input(self, player_input):
        """Process natural language player input and return DM response."""
        if not self.current_campaign:
            return "I'm sorry, but no campaign is currently active. Please start a new game."
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'speaker': 'player',
            'content': player_input
        })
        
        # For now, return a simple response
        # In the full implementation, this would use the narrative engine
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
            # Save to file
            filename = f"campaign_saves/{self.current_campaign['campaign_id']}.json"
            os.makedirs('campaign_saves', exist_ok=True)
            
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

# Initialize interface
interface = NarrativeFocusedInterface()

@app.route('/')
def index():
    """Main narrative interface."""
    # Check if there's an active campaign in session
    campaign_id = session.get('campaign_id')
    if not campaign_id:
        # Redirect to start screen if no campaign is active
        return redirect('/start')
    
    # Load the campaign if it exists
    if not interface.current_campaign or interface.current_campaign.get('campaign_id') != campaign_id:
        success = interface.load_campaign(campaign_id)
        if not success:
            # If campaign can't be loaded, redirect to start screen
            session.pop('campaign_id', None)
            return redirect('/start')
    
    return render_template('narrative_focused.html')

@app.route('/start')
def start_screen():
    """Start screen - redirect to main start screen interface."""
    return redirect('http://localhost:5001/')

@app.route('/new-game')
def new_game():
    """Start a new game."""
    campaign_data = interface.start_new_campaign()
    session['campaign_id'] = campaign_data['campaign_id']
    return jsonify({'success': True, 'campaign': campaign_data})

@app.route('/api/campaign/current')
def get_current_campaign():
    """Get current campaign data."""
    if interface.current_campaign:
        return jsonify({
            'success': True,
            'campaign': interface.current_campaign
        })
    else:
        return jsonify({'success': False, 'message': 'No active campaign'})

@app.route('/api/campaign/current/action', methods=['POST'])
def process_action():
    """Process player action and return DM response."""
    try:
        data = request.get_json()
        player_input = data.get('action', '').strip()
        
        if not player_input:
            return jsonify({'success': False, 'message': 'No action provided'})
        
        # Process the input
        dm_response = interface.process_player_input(player_input)
        
        return jsonify({
            'success': True,
            'dm_response': dm_response,
            'character_info': interface.active_character
        })
        
    except Exception as e:
        logger.error(f"Error processing action: {e}")
        return jsonify({
            'success': False,
            'message': 'Error processing action'
        })

@app.route('/api/campaign/current/save', methods=['POST'])
def save_campaign():
    """Save current campaign."""
    success = interface.save_campaign()
    return jsonify({'success': success})

@app.route('/api/campaigns')
def list_campaigns():
    """List available campaigns."""
    try:
        campaigns = []
        if os.path.exists('campaign_saves'):
            for filename in os.listdir('campaign_saves'):
                if filename.endswith('.json'):
                    campaign_id = filename.replace('.json', '')
                    campaigns.append({
                        'id': campaign_id,
                        'name': f'Campaign {campaign_id}'
                    })
        
        return jsonify({'success': True, 'campaigns': campaigns})
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        return jsonify({'success': False, 'campaigns': []})

@app.route('/api/campaign/<campaign_id>/load', methods=['POST'])
def load_campaign(campaign_id):
    """Load a specific campaign."""
    success = interface.load_campaign(campaign_id)
    if success:
        session['campaign_id'] = campaign_id
    return jsonify({'success': success})

if __name__ == '__main__':
    print("🎲 Starting Narrative-Focused Solo DnD 5E Interface...")
    print("Access the game at: http://localhost:5002")
    print("Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
