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

# Import the actual character generator implementation
try:
    from .simple_unified_interface import SimpleNarrativeBridge
except ImportError:
    from simple_unified_interface import SimpleNarrativeBridge

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
        
        # Import character generator here to avoid module-level import issues
        try:
            from .character_generator import CharacterGenerator
            self.character_generator = CharacterGenerator()
        except ImportError:
            try:
                from character_generator import CharacterGenerator
                self.character_generator = CharacterGenerator()
            except ImportError as e:
                logger.error(f"Failed to import CharacterGenerator: {e}")
                # Fallback to simple character generator
                try:
                    from .simple_unified_interface import SimpleCharacterGenerator
                    self.character_generator = SimpleCharacterGenerator()
                except ImportError:
                    from simple_unified_interface import SimpleCharacterGenerator
                    self.character_generator = SimpleCharacterGenerator()
        
        self.narrative_bridge = SimpleNarrativeBridge()
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
        """Save the current campaign to a file."""
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
        """Load a campaign from file."""
        try:
            filename = f"campaign_saves/{campaign_id}.json"
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    campaign_data = json.load(f)
                
                self.current_campaign = campaign_data
                self.active_character = campaign_data.get('active_character')
                self.conversation_history = campaign_data.get('conversation_history', [])
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error loading campaign: {e}")
            return False
    
    def get_saved_campaigns(self):
        """Get list of saved campaigns."""
        campaigns = []
        try:
            for filename in os.listdir('campaign_saves'):
                if filename.endswith('.json'):
                    campaign_id = filename.replace('.json', '')
                    filepath = os.path.join('campaign_saves', filename)
                    
                    with open(filepath, 'r') as f:
                        campaign_data = json.load(f)
                    
                    campaigns.append({
                        'id': campaign_id,
                        'name': campaign_data.get('name', 'Unknown Campaign'),
                        'created_date': campaign_data.get('created_date'),
                        'character_name': campaign_data.get('active_character', {}).get('name', 'Unknown')
                    })
        except Exception as e:
            logger.error(f"Error getting saved campaigns: {e}")
        
        return campaigns

# Initialize game instance
game = SoloHeartGame()

@app.route('/')
def index():
    """Main index page."""
    return render_template('index.html')

@app.route('/start')
def start_screen():
    """Start screen for new or existing campaigns."""
    return render_template('start_screen.html')

@app.route('/character-creation')
def character_creation():
    """Character creation page."""
    return render_template('character_creation.html')

@app.route('/vibe-code-creation')
def vibe_code_creation():
    """Vibe code character creation page."""
    return render_template('vibe_code_creation.html')

@app.route('/character-creation-select')
def character_creation_select():
    """Character creation mode selector page."""
    return render_template('character_creation_select.html')

@app.route('/step-by-step-creation')
def step_by_step_creation():
    """Step-by-step character creation page."""
    return render_template('step_by_step_creation.html')

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
        
        # Start new campaign
        campaign = game.start_new_campaign(character_data)
        campaign['name'] = campaign_name
        
        # Save campaign
        game.save_campaign()
        
        # Store campaign ID in session
        session['campaign_id'] = campaign['campaign_id']
        
        return jsonify({
            'success': True,
            'campaign': campaign,
            'message': 'Campaign created successfully'
        })
    
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        return jsonify({'success': False, 'message': 'Error creating campaign'})

@app.route('/api/character/create', methods=['POST'])
def create_character():
    """Create a character using the old method."""
    try:
        data = request.get_json()
        character_data = data.get('character_data', {})
        
        # Create character using character manager
        from character_manager import CharacterManager
        char_manager = CharacterManager()
        
        # Ensure required fields
        if not character_data.get('name'):
            character_data['name'] = 'Adventurer'
        if not character_data.get('race'):
            character_data['race'] = 'Human'
        if not character_data.get('class'):
            character_data['class'] = 'Fighter'
        
        # Create character
        character = char_manager.create_character(character_data)
        
        return jsonify({
            'success': True,
            'character': character,
            'message': 'Character created successfully'
        })
    
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        return jsonify({'success': False, 'message': 'Error creating character'})

@app.route('/api/character/vibe-code/start', methods=['POST'])
def start_vibe_code_creation():
    """Start the vibe code character creation process."""
    try:
        data = request.get_json()
        description = data.get('description', '')
        campaign_name = data.get('campaign_name', '')
        
        if not description:
            return jsonify({'success': False, 'message': 'Character description is required'})
        
        # Initialize Vibe Code character creator
        try:
            from character_creator.vibe_code_creator import VibeCodeCharacterCreator
        except ImportError:
            from .character_creator.vibe_code_creator import VibeCodeCharacterCreator
        
        vibe_creator = VibeCodeCharacterCreator()
        
        # Start character creation conversation
        result = vibe_creator.start_character_creation(description, campaign_name)
        
        if result['success']:
            # Store the vibe creator in session
            session['vibe_creator'] = {
                'conversation_history': vibe_creator.conversation_history,
                'current_character_data': vibe_creator.current_character_data,
                'is_complete': vibe_creator.is_complete
            }
            session['character_creation_active'] = True
            session['campaign_name'] = campaign_name
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'is_complete': result['is_complete'],
                'character_data': result['character_data']
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
        user_input = data.get('input', '')
        
        if not user_input:
            return jsonify({'success': False, 'message': 'User input is required'})
        
        # Get vibe creator from session
        vibe_creator_data = session.get('vibe_creator')
        if not vibe_creator_data:
            return jsonify({'success': False, 'message': 'No active character creation session'})
        
        # Recreate Vibe Code character creator
        try:
            from character_creator.vibe_code_creator import VibeCodeCharacterCreator
        except ImportError:
            from .character_creator.vibe_code_creator import VibeCodeCharacterCreator
        
        vibe_creator = VibeCodeCharacterCreator()
        vibe_creator.conversation_history = vibe_creator_data['conversation_history']
        vibe_creator.current_character_data = vibe_creator_data['current_character_data']
        vibe_creator.is_complete = vibe_creator_data['is_complete']
        
        # Continue character creation conversation
        result = vibe_creator.continue_conversation(user_input)
        
        # Update session with new state
        session['vibe_creator'] = {
            'conversation_history': vibe_creator.conversation_history,
            'current_character_data': vibe_creator.current_character_data,
            'is_complete': vibe_creator.is_complete
        }
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'is_complete': result.get('is_complete', False),
            'character_data': result.get('character_data', {})
        })
    
    except Exception as e:
        logger.error(f"Error continuing vibe code creation: {e}")
        return jsonify({'success': False, 'message': 'Error continuing character creation'})

@app.route('/api/character/vibe-code/undo', methods=['POST'])
def undo_last_character_fact():
    """Undo the last committed character fact."""
    try:
        result = game.character_generator.undo_last_fact()
        
        if result:
            fact_type, old_value = result
            return jsonify({
                'success': True,
                'message': f'Undid {fact_type}: {old_value}',
                'undone_fact': fact_type,
                'old_value': old_value
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No facts to undo'
            })
    
    except Exception as e:
        logger.error(f"Error undoing character fact: {e}")
        return jsonify({'success': False, 'message': 'Error undoing character fact'})

@app.route('/api/character/vibe-code/edit', methods=['POST'])
def edit_character():
    """Apply edits to character in review mode."""
    try:
        data = request.get_json()
        edit_message = data.get('edit_message', '')
        
        if not edit_message:
            return jsonify({'success': False, 'message': 'Edit message is required'})
        
        result = game.character_generator.apply_character_edit(edit_message)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error editing character: {e}")
        return jsonify({'success': False, 'message': 'Error editing character'})

@app.route('/api/character/vibe-code/complete', methods=['POST'])
def complete_vibe_code_creation():
    """Complete the vibe code character creation and start the game."""
    try:
        # Get vibe creator from session
        vibe_creator_data = session.get('vibe_creator')
        if not vibe_creator_data:
            return jsonify({'success': False, 'message': 'No active character creation session'})
        
        if not vibe_creator_data['is_complete']:
            return jsonify({'success': False, 'message': 'Character creation is not complete'})
        
        # Get the completed character data
        character_data = vibe_creator_data['current_character_data']
        campaign_name = session.get('campaign_name', 'New Campaign')
        
        # Create a new campaign with the character
        campaign_data = game.start_new_campaign(character_data)
        
        if campaign_data:
            # Save the character data
            try:
                from character_creator.vibe_code_creator import VibeCodeCharacterCreator
            except ImportError:
                from .character_creator.vibe_code_creator import VibeCodeCharacterCreator
            
            vibe_creator = VibeCodeCharacterCreator()
            vibe_creator.current_character_data = character_data
            vibe_creator.is_complete = True
            vibe_creator.save_character(campaign_data['campaign_id'])
            
            # Set session and redirect
            session['campaign_id'] = campaign_data['campaign_id']
            session.pop('character_creation_active', None)
            session.pop('campaign_name', None)
            session.pop('vibe_creator', None)
            
            return jsonify({
                'success': True,
                'redirect': '/game',
                'character': character_data
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to create campaign'})
    
    except Exception as e:
        logger.error(f"Error completing vibe code creation: {e}")
        return jsonify({'success': False, 'message': 'Error completing character creation'})

@app.route('/api/character/vibe-code/finalize', methods=['POST'])
def finalize_character():
    """Finalize the character creation."""
    try:
        result = game.character_generator.finalize_character()
        
        if result['success']:
            # Get character data and campaign name
            character_data = game.character_generator.get_character_data()
            campaign_name = session.get('campaign_name', 'New Campaign')
            
            # Initialize campaign
            campaign_data = game.narrative_bridge.initialize_campaign(character_data, campaign_name)
            
            if campaign_data:
                # Clear session data
                session.pop('character_creation_active', None)
                session.pop('campaign_name', None)
                session['campaign_id'] = campaign_data['id']
                
                result['redirect'] = '/game'
                result['campaign_data'] = campaign_data
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error finalizing character: {e}")
        return jsonify({'success': False, 'message': 'Error finalizing character'})

@app.route('/api/character/step-by-step/start', methods=['POST'])
def start_step_by_step_creation():
    """Start the step-by-step character creation process."""
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        
        # Initialize step-by-step character creator
        try:
            from character_creator.enhanced_step_by_step_creator import EnhancedStepByStepCreator
        except ImportError:
            from .character_creator.enhanced_step_by_step_creator import EnhancedStepByStepCreator
        
        # Initialize LLM service for the enhanced step-by-step creator
        try:
            from gemma3_llm_service import chat_completion
            llm_service = type('LLMService', (), {
                'get_completion': lambda prompt: chat_completion(prompt)
            })()
        except ImportError:
            llm_service = None
        
        step_creator = EnhancedStepByStepCreator(llm_service=llm_service)
        
        # Store only the serializable state in session
        session['step_by_step_state'] = {
            'state': step_creator.state,
            'current_field_index': step_creator.current_field_index,
            'is_active': True  # Always set to True when starting
        }
        
        # Start the process (ignore user_input for start)
        result = step_creator.start()
        
        return jsonify({
            'success': True,
            'message': result,
            'progress': 0
        })
    
    except Exception as e:
        logger.error(f"Error starting step-by-step creation: {e}")
        return jsonify({'success': False, 'message': 'Error starting character creation'})

@app.route('/api/character/step-by-step/continue', methods=['POST'])
def continue_step_by_step_creation():
    """Continue the step-by-step character creation process."""
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        
        # Get the step-by-step state from session and recreate the creator
        step_state = session.get('step_by_step_state')
        logger.info(f"Retrieved step state from session: {step_state}")
        if not step_state:
            return jsonify({'success': False, 'message': 'No active character creation session'})
        
        # Recreate the enhanced step-by-step creator with the saved state
        try:
            from character_creator.enhanced_step_by_step_creator import EnhancedStepByStepCreator
        except ImportError:
            from .character_creator.enhanced_step_by_step_creator import EnhancedStepByStepCreator
        
        # Initialize LLM service for the enhanced step-by-step creator
        try:
            from gemma3_llm_service import chat_completion
            llm_service = type('LLMService', (), {
                'get_completion': lambda prompt: chat_completion(prompt)
            })()
        except ImportError:
            llm_service = None
        
        step_creator = EnhancedStepByStepCreator(llm_service=llm_service)
        step_creator.restore_state(
            step_state['state'],
            step_state['current_field_index'],
            step_state['is_active']
        )
        logger.info(f"Restored creator state: active={step_creator.is_active}, field_index={step_creator.current_field_index}")
        logger.info(f"Current field: {step_creator.fields[step_creator.current_field_index] if step_creator.current_field_index < len(step_creator.fields) else 'COMPLETE'}")
        logger.info(f"State: {step_creator.state}")
        
        # Process the response
        result = step_creator.process_response(user_input)
        
        # IMMEDIATELY update session with current state after processing
        session['step_by_step_state'] = {
            'state': step_creator.state,
            'current_field_index': step_creator.current_field_index,
            'is_active': True  # Keep active during the process
        }
        logger.info(f"Updated session state: field_index={step_creator.current_field_index}, state={step_creator.state}")
        
        # Get current progress and character data
        progress_data = step_creator.get_current_progress()
        progress = len([v for v in progress_data['state'].values() if v is not None])
        
        # Check if complete
        is_complete = step_creator.is_active and step_creator.current_field_index >= len(step_creator.fields)
        
        response_data = {
            'success': True,
            'message': result,
            'progress': progress,
            'is_complete': is_complete
        }
        
        # Add character data if available
        if progress > 0:
            response_data['character_data'] = progress_data['state']
        
        # If complete, create the character and start campaign
        if is_complete:
            character_data = step_creator._create_character_data()
            response_data['character_data'] = character_data
            
            # Start a new campaign with the created character
            try:
                campaign = game.start_new_campaign(character_data)
                session['campaign_id'] = campaign['campaign_id']
                response_data['campaign_started'] = True
                response_data['campaign_id'] = campaign['campaign_id']
                logger.info(f"Started campaign {campaign['campaign_id']} with character {character_data.get('basic_info', {}).get('name', 'Unknown')}")
            except Exception as e:
                logger.error(f"Error starting campaign: {e}")
                response_data['campaign_started'] = False
            
            # Clear session
            session.pop('step_by_step_state', None)
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error continuing step-by-step creation: {e}")
        return jsonify({'success': False, 'message': 'Error processing response'})

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
            'response': dm_response,
            'campaign': game.current_campaign
        })
    
    except Exception as e:
        logger.error(f"Error processing action: {e}")
        return jsonify({'success': False, 'message': 'Error processing action'})

@app.route('/api/campaign/save', methods=['POST'])
def save_campaign():
    """Save the current campaign."""
    success = game.save_campaign()
    if success:
        return jsonify({'success': True, 'message': 'Campaign saved successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to save campaign'})

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 