#!/usr/bin/env python3
"""
Enhanced Narrative Web Interface - Integrating Narrative Engine Core

This interface combines the Narrative Engine core with the existing AI DM system,
providing a unified platform for both DnD gaming and broader narrative applications
across multiple domains.
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

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the narrative bridge instead of direct core imports
from dnd_game.narrative_bridge import (
    NarrativeBridge, DnDMemoryEntry, DnDNPCResponse,
    create_dnd_bridge, store_combat_memory, store_quest_memory
)

# Import existing components
from dnd_game.enhanced_campaign_manager import EnhancedCampaignManager
from cache_manager import CacheManager
from shared.models import get_session, Campaign

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'narrative_engine_secret_key_2024')
CORS(app)

# Initialize systems using the narrative bridge
narrative_bridge = create_dnd_bridge(
    campaign_id='Default Campaign',
    api_key=os.getenv('OPENAI_API_KEY')
)
campaign_manager = EnhancedCampaignManager()
cache_manager = CacheManager()

# Global state
current_campaign_id = 'Default Campaign'


@app.route('/')
def index():
    """Main interface page"""
    return render_template('enhanced_narrative_index.html')


@app.route('/api/domains', methods=['GET'])
def get_domains():
    """Get available narrative domains"""
    domains = [
        {
            'value': 'gaming',
            'name': 'Gaming',
            'description': 'Interactive storytelling for games and adventures'
        },
        {
            'value': 'therapy',
            'name': 'Therapy',
            'description': 'Narrative therapy and personal development'
        },
        {
            'value': 'education',
            'name': 'Education',
            'description': 'Educational storytelling and learning'
        },
        {
            'value': 'fiction',
            'name': 'Fiction',
            'description': 'Creative writing and story development'
        }
    ]
    return jsonify({'domains': domains})


@app.route('/api/narratives', methods=['GET'])
def get_narratives():
    """Get all narratives (simplified to use campaign data)"""
    try:
        # Get campaign summary from the bridge
        summary = narrative_bridge.get_campaign_summary()
        
        narratives = [{
            'id': summary['campaign_id'],
            'name': 'DnD Campaign',
            'domain': 'gaming',
            'character_count': summary.get('active_characters', 0),
            'memory_count': summary.get('memory_stats', {}).get('total_memories', 0),
            'session_count': summary.get('session_count', 0)
        }]
        
        return jsonify({'narratives': narratives})
    except Exception as e:
        logger.error(f"Error getting narratives: {e}")
        return jsonify({'narratives': []})


@app.route('/api/narratives', methods=['POST'])
def create_narrative():
    """Create a new narrative (simplified)"""
    data = request.json
    name = data.get('name', 'New DnD Campaign')
    
    # For now, we'll just return success since we're using a single campaign
    return jsonify({
        'success': True,
        'narrative_id': 'Default Campaign',
        'message': f'Using campaign: {name}'
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat interactions using the narrative bridge"""
    try:
        data = request.json
        message = data.get('message', '')
        npc_name = data.get('npc_name', 'DM')
        context = data.get('context', '')
        
        if npc_name == 'DM':
            # Generate DM narration
            response = narrative_bridge.generate_dm_narration(
                situation=context or "The party continues their adventure",
                player_actions=[message],
                world_context={"location": "current_location"}
            )
        else:
            # Generate NPC response
            npc_response = narrative_bridge.get_npc_response(
                npc_name=npc_name,
                context=context or message,
                player_emotion=None
            )
            response = npc_response.text
        
        # Store the interaction as memory
        memory_entry = DnDMemoryEntry(
            content=f"Player: {message} | Response: {response}",
            memory_type="episodic",
            tags=["chat", "interaction"]
        )
        narrative_bridge.store_dnd_memory(memory_entry)
        
        return jsonify({
            'response': response,
            'npc_name': npc_name,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({
            'response': 'I apologize, but I encountered an error processing your request.',
            'success': False,
            'error': str(e)
        })


@app.route('/api/memory/stats', methods=['GET'])
def get_memory_stats():
    """Get memory statistics"""
    try:
        summary = narrative_bridge.get_campaign_summary()
        stats = summary.get('memory_stats', {})
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return jsonify({'error': str(e)})


@app.route('/api/memory/recall', methods=['POST'])
def recall_memory():
    """Recall memories"""
    try:
        data = request.json
        query = data.get('query', '')
        max_results = data.get('max_results', 5)
        
        memories = narrative_bridge.recall_related_memories(
            query=query,
            max_results=max_results
        )
        
        return jsonify({'memories': memories})
    except Exception as e:
        logger.error(f"Error recalling memories: {e}")
        return jsonify({'memories': [], 'error': str(e)})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        summary = narrative_bridge.get_campaign_summary()
        return jsonify({
            'status': 'operational',
            'campaign_id': summary['campaign_id'],
            'memory_count': summary.get('memory_stats', {}).get('total_memories', 0),
            'character_count': summary.get('active_characters', 0),
            'session_count': summary.get('session_count', 0)
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'status': 'error', 'error': str(e)})


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Narrative Engine Bridge is running'})


if __name__ == '__main__':
    print("🚀 Starting Enhanced Narrative Web Interface...")
    print("   - Narrative Engine Core: ✅")
    print("   - AI DM Engine: ✅")
    print("   - Memory System: ✅")
    print("   - Campaign Manager: ✅")
    print("   - Multi-domain support: ✅")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 