"""
DnD 5E AI-Powered Game - Enhanced Web Interface
==============================================

Enhanced web interface with database persistence and Redis caching
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import os
import sys
import threading
import time
from datetime import datetime
import logging

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_campaign_manager import EnhancedCampaignManager
from models import create_database, get_session, Campaign, CampaignSession
from cache_manager import cache_manager
from core.character_manager import Character

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'dnd-game-secret-key-2025'  # Change this in production
CORS(app)

# Global game state
game_manager = None
current_campaign = "Default Campaign"

def initialize_database():
    """Initialize database on startup"""
    try:
        create_database()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def initialize_game():
    """Initialize the enhanced game manager"""
    global game_manager
    if game_manager is None:
        try:
            game_manager = EnhancedCampaignManager(current_campaign)
            logger.info("Enhanced campaign manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize game manager: {e}")
            return None
    return game_manager

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with caching"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Initialize game if needed
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Failed to initialize game manager'}), 500
        
        # Process the message through the enhanced game manager
        response = manager.process_player_action(message)
        
        # Return the response
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'cached': False  # Enhanced manager handles caching internally
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': f'An error occurred while processing your message: {str(e)}'
        }), 500

@app.route('/api/status')
def status():
    """Get current game status with enhanced info"""
    try:
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        # Get character info if available
        characters = {}
        for name, char in manager.player_characters.items():
            characters[name] = {
                'name': char.name,
                'race': char.race.value,
                'class': char.character_class.value,
                'level': char.level
            }
        
        # Get enhanced campaign summary
        campaign_summary = manager.get_campaign_summary()
        
        return jsonify({
            'campaign': current_campaign,
            'characters': characters,
            'session_active': manager.current_session is not None,
            'timestamp': datetime.now().isoformat(),
            'campaign_summary': campaign_summary,
            'cache_status': cache_manager.get_cache_stats()
        })
        
    except Exception as e:
        logger.error(f"Error in status endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/new-campaign', methods=['POST'])
def new_campaign():
    """Start a new campaign with database persistence"""
    try:
        data = request.get_json()
        campaign_name = data.get('campaign_name', 'New Campaign')
        
        global game_manager, current_campaign
        current_campaign = campaign_name
        
        # Create new enhanced campaign manager
        game_manager = EnhancedCampaignManager(campaign_name)
        
        return jsonify({
            'message': f'New campaign "{campaign_name}" created successfully',
            'campaign': campaign_name,
            'campaign_id': game_manager.campaign_db.id
        })
        
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-session', methods=['POST'])
def start_session():
    """Start a new game session with database persistence"""
    try:
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        session_summary = manager.start_session()
        
        return jsonify({
            'message': 'Session started successfully',
            'session_id': session_summary.session_id,
            'session_db_id': manager.current_session_db.id if manager.current_session_db else None
        })
        
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/end-session', methods=['POST'])
def end_session():
    """End the current game session with database persistence"""
    try:
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        session_summary = manager.end_session()
        
        return jsonify({
            'message': 'Session ended successfully',
            'session_summary': {
                'session_id': session_summary.session_id,
                'duration': session_summary.duration,
                'message_count': session_summary.message_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-campaign', methods=['POST'])
def save_campaign():
    """Save current campaign state"""
    try:
        data = request.get_json()
        save_name = data.get('save_name', None)
        
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        save_result = manager.save_campaign_state(save_name)
        
        return jsonify({
            'message': f'Campaign saved successfully as "{save_result["save_name"]}"',
            'save_data': save_result
        })
        
    except Exception as e:
        logger.error(f"Error saving campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/load-campaign', methods=['POST'])
def load_campaign():
    """Load a saved campaign state"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        success = manager.load_campaign_state(session_id)
        
        if success:
            return jsonify({
                'message': 'Campaign loaded successfully',
                'session_id': session_id
            })
        else:
            return jsonify({'error': 'Failed to load campaign state'}), 500
        
    except Exception as e:
        logger.error(f"Error loading campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/saved-sessions')
def get_saved_sessions():
    """Get list of saved sessions"""
    try:
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        saved_sessions = manager.get_saved_sessions()
        
        return jsonify({
            'saved_sessions': saved_sessions,
            'count': len(saved_sessions)
        })
        
    except Exception as e:
        logger.error(f"Error getting saved sessions: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Combat API endpoints
@app.route('/api/combat/start', methods=['POST'])
def start_combat():
    """Start a combat encounter"""
    try:
        data = request.get_json()
        enemies = data.get('enemies', [])
        
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        combat_status = manager.start_combat(enemies)
        
        return jsonify({
            'message': 'Combat started successfully',
            'combat_status': combat_status
        })
        
    except Exception as e:
        logger.error(f"Error starting combat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/combat/attack', methods=['POST'])
def make_attack():
    """Make an attack in combat"""
    try:
        data = request.get_json()
        attacker = data.get('attacker')
        target = data.get('target')
        
        if not attacker or not target:
            return jsonify({'error': 'Attacker and target are required'}), 400
        
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        attack_result = manager.make_attack(attacker, target)
        
        return jsonify({
            'message': 'Attack completed',
            'attack_result': attack_result
        })
        
    except Exception as e:
        logger.error(f"Error making attack: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/combat/next-turn', methods=['POST'])
def next_combat_turn():
    """Advance to the next turn in combat"""
    try:
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        next_combatant = manager.next_combat_turn()
        
        return jsonify({
            'message': 'Turn advanced',
            'next_combatant': next_combatant,
            'combat_status': manager.get_combat_status()
        })
        
    except Exception as e:
        logger.error(f"Error advancing turn: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/combat/end', methods=['POST'])
def end_combat():
    """End the current combat encounter"""
    try:
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        combat_status = manager.end_combat()
        
        return jsonify({
            'message': 'Combat ended successfully',
            'combat_status': combat_status
        })
        
    except Exception as e:
        logger.error(f"Error ending combat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/combat/status')
def get_combat_status():
    """Get current combat status"""
    try:
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        combat_status = manager.get_combat_status()
        
        return jsonify({
            'combat_status': combat_status
        })
        
    except Exception as e:
        logger.error(f"Error getting combat status: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Skill check API endpoint
@app.route('/api/skill-check', methods=['POST'])
def make_skill_check():
    """Make a skill check"""
    try:
        data = request.get_json()
        skill_name = data.get('skill_name')
        difficulty_class = data.get('difficulty_class')
        character_name = data.get('character_name')
        advantage = data.get('advantage', False)
        disadvantage = data.get('disadvantage', False)
        
        if not skill_name or not difficulty_class or not character_name:
            return jsonify({'error': 'Skill name, difficulty class, and character name are required'}), 400
        
        manager = initialize_game()
        if not manager:
            return jsonify({'error': 'Game manager not available'}), 500
        
        # Get character
        character = manager.player_characters.get(character_name)
        if not character:
            return jsonify({'error': f'Character {character_name} not found'}), 404
        
        # Convert to combatant
        combatant = manager._character_to_combatant(character)
        
        # Make skill check
        from core.combat_system import skill_check_system
        result = skill_check_system.make_skill_check(
            combatant, skill_name, difficulty_class, advantage, disadvantage
        )
        
        # Log the skill check
        manager.memory_system.add_campaign_memory(
            memory_type='skill_check',
            content={
                'skill': skill_name,
                'result': result.__dict__,
                'character': character_name
            },
            session_id=manager.current_session.session_id if manager.current_session else None
        )
        
        return jsonify({
            'message': 'Skill check completed',
            'skill_check_result': {
                'skill_name': result.skill_name,
                'dice_roll': result.dice_roll,
                'modifier': result.modifier,
                'total': result.total,
                'difficulty_class': result.difficulty_class,
                'success': result.success,
                'critical_success': result.critical_success,
                'critical_failure': result.critical_failure,
                'formatted_result': skill_check_system.format_skill_check_result(result)
            }
        })
        
    except Exception as e:
        logger.error(f"Error making skill check: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache-stats')
def get_cache_stats():
    """Get Redis cache statistics"""
    try:
        stats = cache_manager.get_cache_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check database
        db_session = get_session()
        db_session.execute("SELECT 1")
        db_session.close()
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False
    
    # Check Redis
    redis_healthy = cache_manager.health_check()
    
    return jsonify({
        'status': 'healthy' if db_healthy and redis_healthy else 'unhealthy',
        'database': 'connected' if db_healthy else 'disconnected',
        'redis': 'connected' if redis_healthy else 'disconnected',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Initialize database
    if not initialize_database():
        print("Warning: Database initialization failed")
    
    print("Starting Enhanced DnD Web Interface...")
    print("Open your browser to: http://localhost:5001")
    print(f"Database: {'Connected' if initialize_database() else 'Failed'}")
    print(f"Redis: {'Connected' if cache_manager.connected else 'Not available'}")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 