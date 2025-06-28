"""
DnD 5E AI-Powered Game - Simple AI Interface
===========================================

Simple web interface that uses dynamic AI interpretation like ChatGPT
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
import sys
import logging
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ai_dm_engine import AIDMEngine
from core.character_manager import Character, Race, CharacterClass, AbilityScore

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dnd-ai-game-2025')
CORS(app)

# Global game state
ai_dm = AIDMEngine()
current_character = None
campaign_context = "You are in a fantasy tavern in a small town. The air is thick with the smell of ale and wood smoke. Various adventurers and locals mingle about."

def create_sample_character():
    """Create a sample character for testing"""
    character = Character(
        name="Aria",
        race=Race.ELF,
        character_class=CharacterClass.ROGUE,
        level=3,
        background="Criminal",
        personality_traits=["Sneaky", "Quick", "Loyal to friends"],
        ability_scores={
            AbilityScore.STRENGTH: 10,
            AbilityScore.DEXTERITY: 16,
            AbilityScore.CONSTITUTION: 12,
            AbilityScore.INTELLIGENCE: 14,
            AbilityScore.WISDOM: 12,
            AbilityScore.CHARISMA: 14
        }
    )
    return character

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('simple_index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with dynamic AI interpretation"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        global current_character, campaign_context
        
        # Create character if not exists
        if not current_character:
            current_character = create_sample_character()
        
        # Convert character to dict for AI context
        character_info = {
            'name': current_character.name,
            'race': current_character.race.value,
            'class': current_character.character_class.value,
            'level': current_character.level,
            'ability_scores': {k.value: v for k, v in current_character.ability_scores.items()},
            'background': current_character.background,
            'personality_traits': current_character.personality_traits
        }
        
        # Process with AI DM engine
        response = ai_dm.process_action(message, character_info, campaign_context)
        
        # Update campaign context based on the interaction
        campaign_context = f"Recent action: {message}. {campaign_context}"
        if len(campaign_context) > 500:
            campaign_context = campaign_context[-500:]  # Keep it manageable
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'character': character_info
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/api/status')
def status():
    """Get current game status"""
    try:
        global current_character, campaign_context
        
        character_info = None
        if current_character:
            character_info = {
                'name': current_character.name,
                'race': current_character.race.value,
                'class': current_character.character_class.value,
                'level': current_character.level
            }
        
        return jsonify({
            'character': character_info,
            'campaign_context': campaign_context[:200] + "..." if len(campaign_context) > 200 else campaign_context,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in status endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/character', methods=['GET', 'POST'])
def character():
    """Get or update character information"""
    try:
        global current_character
        
        if request.method == 'GET':
            if not current_character:
                return jsonify({'error': 'No character created'}), 404
            
            character_info = {
                'name': current_character.name,
                'race': current_character.race.value,
                'class': current_character.character_class.value,
                'level': current_character.level,
                'ability_scores': {k.value: v for k, v in current_character.ability_scores.items()},
                'background': current_character.background,
                'personality_traits': current_character.personality_traits
            }
            
            return jsonify(character_info)
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Create new character from data
            current_character = Character(
                name=data.get('name', 'Adventurer'),
                race=Race(data.get('race', 'HUMAN')),
                character_class=CharacterClass(data.get('class', 'FIGHTER')),
                level=data.get('level', 1),
                background=data.get('background', 'Soldier'),
                personality_traits=data.get('personality_traits', []),
                ability_scores={
                    AbilityScore(k.upper()): v 
                    for k, v in data.get('ability_scores', {}).items()
                }
            )
            
            return jsonify({
                'message': f'Character {current_character.name} created successfully',
                'character': {
                    'name': current_character.name,
                    'race': current_character.race.value,
                    'class': current_character.character_class.value,
                    'level': current_character.level
                }
            })
        
    except Exception as e:
        logger.error(f"Error in character endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ruling', methods=['POST'])
def make_ruling():
    """Ask the AI DM for a ruling on a complex situation"""
    try:
        data = request.get_json()
        situation = data.get('situation', '').strip()
        question = data.get('question', '').strip()
        
        if not situation:
            return jsonify({'error': 'Situation description is required'}), 400
        
        # Get AI ruling
        ruling = ai_dm.make_ruling(situation, question)
        
        return jsonify({
            'ruling': ruling,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in ruling endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/combat', methods=['POST'])
def handle_combat():
    """Handle combat actions dynamically"""
    try:
        data = request.get_json()
        action = data.get('action', '').strip()
        combat_state = data.get('combat_state', {})
        
        if not action:
            return jsonify({'error': 'Combat action is required'}), 400
        
        # Get AI combat response
        response = ai_dm.handle_combat_action(action, combat_state)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in combat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Reset the game state"""
    try:
        global current_character, campaign_context
        
        current_character = None
        campaign_context = "You are in a fantasy tavern in a small town. The air is thick with the smell of ale and wood smoke. Various adventurers and locals mingle about."
        
        return jsonify({
            'message': 'Game reset successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in reset endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("Starting Simple AI DnD Interface...")
    print("Open your browser to: http://localhost:5002")
    print("This interface uses dynamic AI interpretation like ChatGPT!")
    
    app.run(debug=True, host='0.0.0.0', port=5002) 