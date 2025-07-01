#!/usr/bin/env python3
"""
5E-Compatible Web Interface - AI-Powered Solo Adventure Game

This interface provides a web-based version of the CLI adventure game,
integrating with the campaign manager, character creation, and AI DM systems.
Built on 5E-compatible rules and mechanics.
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

# Load environment variables from .env file if it exists
from dotenv import load_dotenv
load_dotenv()

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import 5E-compatible game systems
from dnd_game.enhanced_campaign_manager import EnhancedCampaignManager
from narrative_core.rules import DMNarrationStyle
from narrative_core.conversational_parser import ConversationalParser
from narrative_core.engine_interface import EnhancedNarrativeEngine
from narrative_core.ai_dm_engine import AIDMEngine
from narrative_core.enhanced_memory_system import LayeredMemorySystem, MemoryType, MemoryLayer
from narrative_core.character_creator import CharacterCreator, CharacterCreationStep
from shared.cache_manager import CacheManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dnd_game_secret_key_2024')
CORS(app)

# Initialize 5E-compatible game systems
campaign_manager = EnhancedCampaignManager()
dm_style = DMNarrationStyle()
conversational_parser = ConversationalParser(dm_style)
narrative_engine = EnhancedNarrativeEngine()
ai_dm_engine = AIDMEngine(api_key=os.getenv('OPENAI_API_KEY'))
memory_system = LayeredMemorySystem(campaign_id=campaign_id)
character_creator = CharacterCreator()
cache_manager = CacheManager()

# Global state
current_campaign = None
current_character = None
current_session_id = None


@app.route('/')
def index():
    """Main 5E-compatible game interface"""
    return render_template('dnd_game_index.html')


@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Get all available campaigns"""
    campaigns = campaign_manager.list_campaigns()
    return jsonify({'campaigns': campaigns})


@app.route('/api/campaigns', methods=['POST'])
def create_campaign():
    """Create a new campaign"""
    data = request.json
    campaign_name = data.get('name', 'New Campaign')
    narration_style = data.get('narration_style', 'balanced')
    
    # Create campaign
    campaign = campaign_manager.create_campaign(campaign_name)
    
    # Set narration style
    style_enum = DMNarrationStyle[narration_style.upper()]
    campaign.narration_style = style_enum
    
    # Save campaign
    campaign_manager.save_campaign(campaign)
    
    global current_campaign
    current_campaign = campaign
    
    return jsonify({
        'success': True,
        'campaign_id': campaign.id,
        'campaign_name': campaign.name,
        'message': f'Created campaign: {campaign_name}'
    })


@app.route('/api/campaigns/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id: str):
    """Get campaign details"""
    campaign = campaign_manager.load_campaign(campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404
    
    return jsonify({
        'id': campaign.id,
        'name': campaign.name,
        'narration_style': campaign.narration_style.name.lower(),
        'character': campaign.character.to_dict() if campaign.character else None,
        'backstory': campaign.backstory,
        'created_at': campaign.created_at.isoformat(),
        'last_played': campaign.last_played.isoformat() if campaign.last_played else None
    })


@app.route('/api/campaigns/<campaign_id>/load', methods=['POST'])
def load_campaign(campaign_id: str):
    """Load a campaign for play"""
    campaign = campaign_manager.load_campaign(campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404
    
    global current_campaign, current_character
    current_campaign = campaign
    current_character = campaign.character
    
    # Initialize memory system for this campaign
    memory_system = LayeredMemorySystem(campaign_id)
    
    return jsonify({
        'success': True,
        'campaign': {
            'id': campaign.id,
            'name': campaign.name,
            'narration_style': campaign.narration_style.name.lower(),
            'character': campaign.character.to_dict() if campaign.character else None,
            'backstory': campaign.backstory
        },
        'message': f'Loaded campaign: {campaign.name}'
    })


@app.route('/api/character/create', methods=['POST'])
def start_character_creation():
    """Start character creation process"""
    data = request.json
    creation_type = data.get('type', 'step_by_step')  # 'step_by_step' or 'vibe_based'
    
    # Reset character creator to start
    character_creator.current_step = CharacterCreationStep.START
    character_creator.character_data = {}
    
    # Get first step
    step = character_creator.get_current_step()
    instructions = character_creator.get_step_instructions()
    options = character_creator.get_available_options()
    
    return jsonify({
        'success': True,
        'step': step.value,
        'instructions': instructions,
        'options': options,
        'creation_type': creation_type
    })


@app.route('/api/character/step', methods=['GET'])
def get_character_step():
    """Get current character creation step"""
    step = character_creator.get_current_step()
    if not step:
        return jsonify({'error': 'No active character creation'}), 400
    
    instructions = character_creator.get_step_instructions()
    options = character_creator.get_available_options()
    summary = character_creator.get_character_summary()
    
    return jsonify({
        'step': step.value,
        'instructions': instructions,
        'options': options,
        'summary': summary
    })


@app.route('/api/character/choice', methods=['POST'])
def make_character_choice():
    """Make a choice in character creation"""
    data = request.json
    choice = data.get('choice')
    
    if not choice:
        return jsonify({'error': 'No choice provided'}), 400
    
    # Make choice
    result = character_creator.make_choice(choice)
    
    if character_creator.get_current_step() == CharacterCreationStep.COMPLETE:
        # Character creation complete
        character_data = character_creator.get_complete_character()
        return jsonify({
            'success': True,
            'completed': True,
            'character': character_data,
            'message': 'Character creation complete!'
        })
    else:
        # Get next step
        step = character_creator.get_current_step()
        instructions = character_creator.get_step_instructions()
        options = character_creator.get_available_options()
        summary = character_creator.get_character_summary()
        
        return jsonify({
            'success': True,
            'completed': False,
            'step': step.value,
            'instructions': instructions,
            'options': options,
            'summary': summary,
            'message': result
        })


@app.route('/api/character/save', methods=['POST'])
def save_character():
    """Save the created character to current campaign"""
    if not current_campaign:
        return jsonify({'error': 'No active campaign'}), 400
    
    character_data = character_creator.get_complete_character()
    if not character_data or 'error' in character_data:
        return jsonify({'error': 'No character to save'}), 400
    
    # Convert character data to Character object (simplified for now)
    # In a full implementation, you'd want to create a proper Character object
    character = character_data
    
    # Save character to campaign
    current_campaign.character = character
    campaign_manager.save_campaign(current_campaign)
    
    global current_character
    current_character = character
    
    return jsonify({
        'success': True,
        'character': character,
        'message': f'Character saved to campaign {current_campaign.name}'
    })


@app.route('/api/backstory', methods=['POST'])
def set_backstory():
    """Set campaign backstory"""
    if not current_campaign:
        return jsonify({'error': 'No active campaign'}), 400
    
    data = request.json
    backstory = data.get('backstory', '')
    
    current_campaign.backstory = backstory
    campaign_manager.save_campaign(current_campaign)
    
    return jsonify({
        'success': True,
        'backstory': backstory,
        'message': 'Backstory saved'
    })


@app.route('/api/game/chat', methods=['POST'])
def game_chat():
    """Main game chat endpoint"""
    if not current_campaign:
        return jsonify({'error': 'No active campaign'}), 400
    
    data = request.json
    message = data.get('message', '')
    
    # Parse for style changes
    parsed = conversational_parser.parse_input(message)
    
    if parsed.get('type') == 'style_change':
        # Handle style change
        new_style = parsed.get('style')
        style_enum = DMNarrationStyle[new_style.upper()]
        current_campaign.narration_style = style_enum
        campaign_manager.save_campaign(current_campaign)
        
        return jsonify({
            'type': 'style_change',
            'style': new_style,
            'message': f'Switched to {new_style} narration style!'
        })
    
    # Process game message
    try:
        # Get AI response with current narration style
        response = narrative_engine.generate_dm_response(
            message=message,
            character=current_character,
            narration_style=current_campaign.narration_style.name.lower(),
            campaign_context=current_campaign.backstory
        )
        
        # Update campaign last played
        current_campaign.last_played = datetime.now()
        campaign_manager.save_campaign(current_campaign)
        
        return jsonify({
            'type': 'game_response',
            'response': response,
            'narration_style': current_campaign.narration_style.name.lower()
        })
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return jsonify({
            'type': 'error',
            'response': 'Sorry, I encountered an error. Please try again.'
        })


@app.route('/api/game/roll', methods=['POST'])
def roll_dice():
    """Roll dice with modifiers"""
    data = request.json
    dice_notation = data.get('dice', 'd20')
    modifier = data.get('modifier', 0)
    description = data.get('description', '')
    
    try:
        result = narrative_engine.roll_dice(dice_notation, modifier)
        return jsonify({
            'success': True,
            'dice': dice_notation,
            'modifier': modifier,
            'result': result,
            'description': description
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/game/quests', methods=['GET'])
def get_quests():
    """Get current quests"""
    if not current_campaign:
        return jsonify({'error': 'No active campaign'}), 400
    
    quests = narrative_engine.get_active_quests()
    return jsonify({'quests': quests})


@app.route('/api/game/quests', methods=['POST'])
def add_quest():
    """Add a new quest"""
    if not current_campaign:
        return jsonify({'error': 'No active campaign'}), 400
    
    data = request.json
    title = data.get('title', '')
    description = data.get('description', '')
    objectives = data.get('objectives', [])
    
    quest_id = narrative_engine.add_quest(title, description, objectives)
    
    return jsonify({
        'success': True,
        'quest_id': quest_id,
        'message': f'Quest "{title}" added!'
    })


@app.route('/api/game/quests/<quest_id>/update', methods=['POST'])
def update_quest(quest_id: str):
    """Update quest progress"""
    if not current_campaign:
        return jsonify({'error': 'No active campaign'}), 400
    
    data = request.json
    objective_id = data.get('objective_id')
    completed = data.get('completed', False)
    
    result = narrative_engine.update_quest_objective(quest_id, objective_id, completed)
    
    return jsonify({
        'success': True,
        'result': result
    })


@app.route('/api/game/save', methods=['POST'])
def save_game():
    """Save current game state"""
    if not current_campaign:
        return jsonify({'error': 'No active campaign'}), 400
    
    # Save campaign
    campaign_manager.save_campaign(current_campaign)
    
    # Save game state
    narrative_engine.save_game_state(current_campaign.id)
    
    return jsonify({
        'success': True,
        'message': 'Game saved successfully!'
    })


@app.route('/api/game/load', methods=['POST'])
def load_game():
    """Load game state"""
    if not current_campaign:
        return jsonify({'error': 'No active campaign'}), 400
    
    # Load game state
    narrative_engine.load_game_state(current_campaign.id)
    
    return jsonify({
        'success': True,
        'message': 'Game loaded successfully!'
    })


@app.route('/api/game/status', methods=['GET'])
def get_game_status():
    """Get current game status"""
    if not current_campaign:
        return jsonify({'error': 'No active campaign'}), 404
    
    return jsonify({
        'campaign': {
            'id': current_campaign.id,
            'name': current_campaign.name,
            'narration_style': current_campaign.narration_style.name.lower(),
            'backstory': current_campaign.backstory
        },
        'character': current_character.to_dict() if current_character else None,
        'quests': narrative_engine.get_active_quests(),
        'completed_quests': narrative_engine.get_completed_quests()
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'systems': {
            'campaign_manager': '✅',
            'narrative_engine': '✅',
            'ai_dm_engine': '✅',
            'character_creator': '✅'
        }
    })


if __name__ == '__main__':
    print("🎲 Starting DnD Web Interface...")
    print("   - Campaign Manager: ✅")
    print("   - Narrative Engine: ✅")
    print("   - AI DM Engine: ✅")
    print("   - Character Creator: ✅")
    print("   - Conversational Style Switching: ✅")
    print("\n🌐 Web interface available at: http://localhost:5002")
    print("📖 Open your browser and navigate to the URL above to start playing!")
    
    app.run(debug=True, host='0.0.0.0', port=5002) 