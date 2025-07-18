#!/usr/bin/env python3
"""
Unified SoloHeart Narrative Interface
A single Flask server that provides the complete immersive solo DnD experience.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from character_generator import CharacterGenerator
from character_manager import CharacterManager
from narrative_bridge import NarrativeBridge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'unified-narrative-key')

class UnifiedNarrativeGame:
    """Unified game manager that handles the complete SoloHeart experience."""
    
    def __init__(self):
        self.character_generator = CharacterGenerator()
        self.character_manager = CharacterManager()
        self.narrative_bridge = NarrativeBridge()
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure necessary directories exist."""
        directories = ['campaign_saves', 'character_saves', 'templates']
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
            
            # Initialize the narrative bridge with the character
            campaign_data = self.narrative_bridge.initialize_campaign(character_data, campaign_name)
            
            if campaign_data:
                return campaign_data
            else:
                return None
        except Exception as e:
            logger.error(f"Error creating new campaign: {e}")
            return None
    
    def generate_setting_introduction(self, character_data, campaign_name):
        """Generate LLM-created setting introduction as per design guide."""
        try:
            # Use the narrative bridge to generate the setting introduction
            introduction = self.narrative_bridge.generate_setting_introduction(character_data, campaign_name)
            return introduction
        except Exception as e:
            logger.error(f"Error generating setting introduction: {e}")
            return "You find yourself in a mysterious land, ready to begin your adventure..."

# Initialize game manager
game = UnifiedNarrativeGame()

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
        campaign_data = game.create_new_campaign(character_data, campaign_name)
        
        if campaign_data:
            # Generate LLM-created setting introduction
            setting_introduction = game.generate_setting_introduction(character_data, campaign_name)
            
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
            campaign_data = game.create_new_campaign(character_data, campaign_name)
            
            if campaign_data:
                # Generate setting introduction
                setting_introduction = game.generate_setting_introduction(character_data, campaign_name)
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
    print("🎲 Starting Unified SoloHeart Narrative Interface...")
    print("Access the game at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5001)
