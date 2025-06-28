"""
DnD 5E AI-Powered Game - Web Interface
=====================================

A ChatGPT-style web interface for interactive DnD gameplay
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import os
import sys
import threading
import time
from datetime import datetime

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import DnDCampaignManager
from core.character_manager import Character

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dnd-game-secret-key-2025')  # Use environment variable
CORS(app)

# Global game state
game_manager = None
current_campaign = "Default Campaign"

def initialize_game():
    """Initialize the game manager"""
    global game_manager
    if game_manager is None:
        game_manager = DnDCampaignManager(current_campaign)
    return game_manager

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Initialize game if needed
        manager = initialize_game()
        
        # Process the message through the game manager
        response = manager.process_player_action(message)
        
        # Return the response in the expected format
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': f'An error occurred while processing your message: {str(e)}'
        }), 500

@app.route('/api/status')
def status():
    """Get current game status"""
    try:
        manager = initialize_game()
        
        # Get character info if available
        characters = {}
        for name, char in manager.player_characters.items():
            characters[name] = {
                'name': char.name,
                'race': char.race.value,
                'class': char.character_class.value,
                'level': char.level
            }
        
        return jsonify({
            'campaign': current_campaign,
            'characters': characters,
            'session_active': manager.current_session is not None,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/new-campaign', methods=['POST'])
def new_campaign():
    """Start a new campaign"""
    try:
        data = request.get_json()
        campaign_name = data.get('campaign_name', 'New Campaign')
        
        global game_manager, current_campaign
        current_campaign = campaign_name
        game_manager = DnDCampaignManager(campaign_name)
        
        return jsonify({
            'message': f'New campaign "{campaign_name}" created successfully',
            'campaign': campaign_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-session', methods=['POST'])
def start_session():
    """Start a new game session"""
    try:
        manager = initialize_game()
        session_summary = manager.start_session()
        
        return jsonify({
            'message': 'Session started successfully',
            'session_id': session_summary.session_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/end-session', methods=['POST'])
def end_session():
    """End the current game session"""
    try:
        manager = initialize_game()
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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("Starting DnD Web Interface...")
    print("Open your browser to: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001) 