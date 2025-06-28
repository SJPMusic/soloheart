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

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from narrative_engine_core import (
    NarrativeEngineCore, NarrativeDomain, StoryStructure, EmotionalValence,
    Character, Setting, PlotPoint, Theme, BasicNarrativeAnalyzer,
    BasicNarrativeGenerator, BasicDomainAdapter
)

# Import existing components
from enhanced_campaign_manager import EnhancedCampaignManager
from core.enhanced_memory_system import LayeredMemorySystem, MemoryType, MemoryLayer
from ai_dm_engine import AIDMEngine
from character_creator import CharacterCreator, CharacterCreationStep
from cache_manager import CacheManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'narrative_engine_secret_key_2024')
CORS(app)

# Initialize systems
narrative_engine = NarrativeEngineCore()
ai_dm_engine = AIDMEngine(api_key=os.getenv('OPENAI_API_KEY'))
memory_system = LayeredMemorySystem('Default Campaign')
campaign_manager = EnhancedCampaignManager()
character_creator = CharacterCreator()
cache_manager = CacheManager()

# Register basic implementations for all domains
basic_analyzer = BasicNarrativeAnalyzer()
basic_generator = BasicNarrativeGenerator()
basic_adapter = BasicDomainAdapter()

for domain in NarrativeDomain:
    narrative_engine.register_analyzer(domain, basic_analyzer)
    narrative_engine.register_generator(domain, basic_generator)
    narrative_engine.register_adapter(domain, basic_adapter)

# Global state
current_narrative_id = None
current_domain = NarrativeDomain.GAMING
current_campaign_id = None


@app.route('/')
def index():
    """Main interface page"""
    return render_template('enhanced_narrative_index.html')


@app.route('/api/domains', methods=['GET'])
def get_domains():
    """Get available narrative domains"""
    domains = [
        {
            'value': domain.value,
            'name': domain.value.replace('_', ' ').title(),
            'description': get_domain_description(domain)
        }
        for domain in NarrativeDomain
    ]
    return jsonify({'domains': domains})


def get_domain_description(domain: NarrativeDomain) -> str:
    """Get description for a narrative domain"""
    descriptions = {
        NarrativeDomain.GAMING: "Interactive storytelling for games and adventures",
        NarrativeDomain.THERAPY: "Narrative therapy and personal development",
        NarrativeDomain.EDUCATION: "Educational storytelling and learning",
        NarrativeDomain.ORGANIZATIONAL: "Organizational change and business narratives",
        NarrativeDomain.CREATIVE_WRITING: "Creative writing and story development",
        NarrativeDomain.JOURNALISM: "Journalistic storytelling and reporting",
        NarrativeDomain.MARKETING: "Marketing narratives and brand storytelling"
    }
    return descriptions.get(domain, "Narrative development and analysis")


@app.route('/api/narratives', methods=['GET'])
def get_narratives():
    """Get all narratives"""
    narratives = []
    for narrative_id, narrative in narrative_engine.narratives.items():
        summary = narrative_engine.get_narrative_summary(narrative_id)
        narratives.append({
            'id': narrative_id,
            'name': summary['name'],
            'domain': get_narrative_domain(narrative_id),
            'structure_type': summary['structure_type'],
            'character_count': summary['character_count'],
            'plot_point_count': summary['plot_point_count'],
            'coherence_score': summary['coherence_score'],
            'created_at': summary['created_at'],
            'updated_at': summary['updated_at']
        })
    return jsonify({'narratives': narratives})


def get_narrative_domain(narrative_id: str) -> str:
    """Get the domain for a narrative (stored in metadata)"""
    narrative = narrative_engine.narratives.get(narrative_id)
    if narrative and narrative.characters:
        # Check first character's tags for domain
        for tag in narrative.characters[0].tags:
            if tag.startswith('domain:'):
                return tag.split(':')[1]
    return 'gaming'  # Default


@app.route('/api/narratives', methods=['POST'])
def create_narrative():
    """Create a new narrative"""
    data = request.json
    name = data.get('name', 'New Narrative')
    domain = NarrativeDomain(data.get('domain', 'gaming'))
    structure_type = StoryStructure(data.get('structure_type', 'three_act'))
    
    # Create narrative
    narrative_id = narrative_engine.create_narrative(name, structure_type)
    
    # Add domain tag to first character (if any are added later)
    global current_narrative_id, current_domain
    current_narrative_id = narrative_id
    current_domain = domain
    
    # Create initial character with domain tag
    initial_character = Character(
        name="Narrator",
        description="The narrative voice",
        tags={f"domain:{domain.value}"},
        role="narrator"
    )
    narrative_engine.add_character(narrative_id, initial_character)
    
    return jsonify({
        'success': True,
        'narrative_id': narrative_id,
        'message': f'Created narrative: {name}'
    })


@app.route('/api/narratives/<narrative_id>', methods=['GET'])
def get_narrative(narrative_id: str):
    """Get detailed narrative information"""
    try:
        summary = narrative_engine.get_narrative_summary(narrative_id)
        narrative = narrative_engine.narratives[narrative_id]
        
        # Get detailed character information
        characters = []
        for char in narrative.characters:
            characters.append({
                'id': char.id,
                'name': char.name,
                'description': char.description,
                'personality_traits': char.personality_traits,
                'motivations': char.motivations,
                'relationships': char.relationships,
                'emotional_state': char.emotional_state.value,
                'arc_progression': char.arc_progression,
                'role': char.role,
                'tags': list(char.tags)
            })
        
        # Get detailed plot point information
        plot_points = []
        for plot in narrative.plot_points:
            plot_points.append({
                'id': plot.id,
                'name': plot.name,
                'description': plot.description,
                'story_structure_position': plot.story_structure_position,
                'emotional_impact': plot.emotional_impact.value,
                'characters_involved': plot.characters_involved,
                'conflict_type': plot.conflict_type,
                'resolution': plot.resolution,
                'consequences': plot.consequences,
                'tags': list(plot.tags)
            })
        
        # Get themes
        themes = []
        for theme in narrative.themes:
            themes.append({
                'id': theme.id,
                'name': theme.name,
                'description': theme.description,
                'motif': theme.motif,
                'development_arc': theme.development_arc,
                'symbols': theme.symbols,
                'message': theme.message,
                'tags': list(theme.tags)
            })
        
        # Get setting
        setting = None
        if narrative.setting:
            setting = {
                'id': narrative.setting.id,
                'name': narrative.setting.name,
                'description': narrative.setting.description,
                'location_type': narrative.setting.location_type,
                'atmosphere': narrative.setting.atmosphere,
                'rules': narrative.setting.rules,
                'history': narrative.setting.history,
                'current_state': narrative.setting.current_state,
                'tags': list(narrative.setting.tags)
            }
        
        return jsonify({
            'summary': summary,
            'characters': characters,
            'plot_points': plot_points,
            'themes': themes,
            'setting': setting,
            'emotional_progression': narrative.emotional_progression
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/narratives/<narrative_id>/characters', methods=['POST'])
def add_character(narrative_id: str):
    """Add a character to a narrative"""
    data = request.json
    
    character = Character(
        name=data.get('name', 'New Character'),
        description=data.get('description', ''),
        personality_traits=data.get('personality_traits', []),
        motivations=data.get('motivations', []),
        role=data.get('role', 'supporting'),
        emotional_state=EmotionalValence(data.get('emotional_state', 0)),
        tags=set(data.get('tags', []))
    )
    
    character_id = narrative_engine.add_character(narrative_id, character)
    
    return jsonify({
        'success': True,
        'character_id': character_id,
        'message': f'Added character: {character.name}'
    })


@app.route('/api/narratives/<narrative_id>/plot-points', methods=['POST'])
def add_plot_point(narrative_id: str):
    """Add a plot point to a narrative"""
    data = request.json
    
    plot_point = PlotPoint(
        name=data.get('name', 'New Plot Point'),
        description=data.get('description', ''),
        story_structure_position=data.get('story_structure_position', 0.0),
        emotional_impact=EmotionalValence(data.get('emotional_impact', 0)),
        characters_involved=data.get('characters_involved', []),
        conflict_type=data.get('conflict_type', ''),
        resolution=data.get('resolution', ''),
        consequences=data.get('consequences', []),
        tags=set(data.get('tags', []))
    )
    
    plot_id = narrative_engine.add_plot_point(narrative_id, plot_point)
    
    return jsonify({
        'success': True,
        'plot_id': plot_id,
        'message': f'Added plot point: {plot_point.name}'
    })


@app.route('/api/narratives/<narrative_id>/analyze', methods=['POST'])
def analyze_narrative(narrative_id: str):
    """Analyze a narrative"""
    data = request.json
    domain = NarrativeDomain(data.get('domain', 'gaming'))
    
    try:
        analysis = narrative_engine.analyze_narrative(narrative_id, domain)
        
        # Convert themes to serializable format
        themes = []
        for theme in analysis['themes']:
            themes.append({
                'name': theme.name,
                'description': theme.description,
                'motif': theme.motif,
                'message': theme.message
            })
        
        return jsonify({
            'success': True,
            'analysis': {
                'coherence_score': analysis['coherence_score'],
                'themes': themes,
                'character_arcs': analysis['character_arcs'],
                'conflicts': analysis['conflicts'],
                'timestamp': analysis['timestamp']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/narratives/<narrative_id>/generate', methods=['POST'])
def generate_plot_point(narrative_id: str):
    """Generate the next plot point for a narrative"""
    data = request.json
    domain = NarrativeDomain(data.get('domain', 'gaming'))
    context = data.get('context', {})
    
    try:
        plot_point = narrative_engine.generate_next_plot_point(narrative_id, domain, context)
        
        # Add the generated plot point to the narrative
        plot_id = narrative_engine.add_plot_point(narrative_id, plot_point)
        
        return jsonify({
            'success': True,
            'plot_point': {
                'id': plot_point.id,
                'name': plot_point.name,
                'description': plot_point.description,
                'story_structure_position': plot_point.story_structure_position,
                'emotional_impact': plot_point.emotional_impact.value,
                'characters_involved': plot_point.characters_involved,
                'conflict_type': plot_point.conflict_type,
                'resolution': plot_point.resolution,
                'consequences': plot_point.consequences
            },
            'message': f'Generated plot point: {plot_point.name}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/narratives/<narrative_id>/adapt', methods=['POST'])
def adapt_narrative(narrative_id: str):
    """Adapt a narrative for a different domain"""
    data = request.json
    target_domain = NarrativeDomain(data.get('target_domain', 'education'))
    
    try:
        adapted_narrative = narrative_engine.adapt_for_domain(narrative_id, target_domain)
        
        return jsonify({
            'success': True,
            'adapted_narrative': {
                'id': adapted_narrative.id,
                'name': adapted_narrative.name,
                'character_count': len(adapted_narrative.characters),
                'plot_point_count': len(adapted_narrative.plot_points),
                'theme_count': len(adapted_narrative.themes)
            },
            'message': f'Adapted narrative for {target_domain.value} domain'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/narratives/<narrative_id>/export', methods=['GET'])
def export_narrative(narrative_id: str):
    """Export a narrative to JSON"""
    try:
        export_data = narrative_engine.export_narrative(narrative_id)
        
        # Create filename
        narrative = narrative_engine.narratives[narrative_id]
        filename = f"{narrative.name.replace(' ', '_')}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return jsonify({
            'success': True,
            'export_data': export_data,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/narratives/import', methods=['POST'])
def import_narrative():
    """Import a narrative from JSON"""
    data = request.json
    json_data = data.get('json_data', '')
    
    try:
        narrative_id = narrative_engine.import_narrative(json_data)
        
        return jsonify({
            'success': True,
            'narrative_id': narrative_id,
            'message': 'Narrative imported successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint that integrates Narrative Engine with AI DM"""
    data = request.json
    message = data.get('message', '')
    narrative_id = data.get('narrative_id')
    domain = NarrativeDomain(data.get('domain', 'gaming'))
    
    try:
        # Get narrative context if available
        narrative_context = ""
        if narrative_id and narrative_id in narrative_engine.narratives:
            narrative = narrative_engine.narratives[narrative_id]
            summary = narrative_engine.get_narrative_summary(narrative_id)
            
            narrative_context = f"""
            Current Narrative: {summary['name']}
            Characters: {', '.join([c.name for c in narrative.characters])}
            Plot Points: {len(narrative.plot_points)}
            Structure: {summary['structure_type']}
            """
        
        # Generate AI response using the appropriate engine
        if domain == NarrativeDomain.GAMING:
            # Use AI DM engine for gaming
            response = ai_dm_engine.generate_response(message, narrative_context)
        else:
            # Use narrative engine for other domains
            context = {
                'user_input': message,
                'narrative_context': narrative_context,
                'domain': domain.value
            }
            
            if narrative_id:
                # Generate next plot point
                plot_point = narrative_engine.generate_next_plot_point(narrative_id, domain, context)
                response = f"Based on your input, I've generated a new plot point: {plot_point.name}. {plot_point.description}"
            else:
                response = f"I'm here to help you with {domain.value} narratives. What would you like to explore?"
        
        # Store in memory system
        memory_system.add_memory(
            content={"user": message, "ai": response},
            memory_type=MemoryType.EVENT,
            layer=MemoryLayer.SHORT_TERM,
            user_id="player",
            session_id="default",
            emotional_weight=0.7,
            thematic_tags=[domain.value, "narrative_engine"]
        )
        
        return jsonify({
            'response': response,
            'narrative_context': narrative_context.strip() if narrative_context else None
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/memory/stats', methods=['GET'])
def get_memory_stats():
    """Get memory system statistics"""
    try:
        stats = memory_system.get_memory_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/memory/recall', methods=['POST'])
def recall_memory():
    """Recall memories based on query"""
    data = request.json
    query = data.get('query', '')
    limit = data.get('limit', 5)
    
    try:
        memories = memory_system.recall(query=query)
        # Convert MemoryNode objects to dicts and limit results
        memory_dicts = [memory.to_dict() for memory in memories[:limit]]
        return jsonify({'memories': memory_dicts})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        # Get campaign count from database
        from models import Campaign
        from database import get_session
        session = get_session()
        campaigns_count = session.query(Campaign).count()
        session.close()
        
        return jsonify({
            'narrative_engine': {
                'narratives_count': len(narrative_engine.narratives),
                'domains_supported': len(NarrativeDomain),
                'active_narrative': current_narrative_id
            },
            'memory_system': {
                'total_memories': memory_system.get_memory_stats().get('total_memories', 0),
                'memory_types': memory_system.get_memory_stats().get('memory_types', {})
            },
            'campaign_manager': {
                'campaigns_count': campaigns_count,
                'active_campaign': current_campaign_id
            }
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'narrative_engine': 'running',
            'ai_dm_engine': 'running',
            'memory_system': 'running',
            'campaign_manager': 'running',
            'character_creator': 'running'
        }
    })


# Character Creation Endpoints
@app.route('/api/character/start', methods=['POST'])
def start_character_creation():
    """Start character creation process"""
    try:
        # Reset character creator to start
        character_creator.current_step = CharacterCreationStep.START
        character_creator.character_data = {}
        
        return jsonify({
            'success': True,
            'step': character_creator.get_current_step().value,
            'instructions': character_creator.get_step_instructions(),
            'options': character_creator.get_available_options()
        })
    except Exception as e:
        logger.error(f"Error starting character creation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/character/step', methods=['GET'])
def get_character_step():
    """Get current character creation step"""
    try:
        return jsonify({
            'step': character_creator.get_current_step().value,
            'instructions': character_creator.get_step_instructions(),
            'options': character_creator.get_available_options(),
            'summary': character_creator.get_character_summary()
        })
    except Exception as e:
        logger.error(f"Error getting character step: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/character/choice', methods=['POST'])
def make_character_choice():
    """Make a choice in character creation"""
    try:
        data = request.get_json()
        choice = data.get('choice', '')
        details = data.get('details', {})
        
        response = character_creator.make_choice(choice, details)
        
        return jsonify({
            'success': True,
            'response': response,
            'step': character_creator.get_current_step().value,
            'instructions': character_creator.get_step_instructions(),
            'options': character_creator.get_available_options(),
            'summary': character_creator.get_character_summary(),
            'complete': character_creator.get_current_step() == CharacterCreationStep.COMPLETE
        })
    except Exception as e:
        logger.error(f"Error making character choice: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/character/complete', methods=['GET'])
def get_complete_character():
    """Get the complete character data"""
    try:
        character_data = character_creator.get_complete_character()
        
        if 'error' in character_data:
            return jsonify({'error': character_data['error']}), 400
            
        return jsonify({
            'success': True,
            'character': character_data
        })
    except Exception as e:
        logger.error(f"Error getting complete character: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/character/save', methods=['POST'])
def save_character():
    """Save the completed character to the campaign"""
    try:
        data = request.get_json()
        character_name = data.get('name', 'Player Character')
        
        character_data = character_creator.get_complete_character()
        
        if 'error' in character_data:
            return jsonify({'error': character_data['error']}), 400
        
        # Add character name and save to campaign
        character_data['name'] = character_name
        character_data['created_at'] = datetime.now().isoformat()
        
        # Save to campaign manager
        campaign_manager.save_character(character_name, character_data)
        
        return jsonify({
            'success': True,
            'message': f'Character {character_name} saved successfully!',
            'character': character_data
        })
    except Exception as e:
        logger.error(f"Error saving character: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Narrative Web Interface...")
    print("   - Narrative Engine Core: ✅")
    print("   - AI DM Engine: ✅")
    print("   - Memory System: ✅")
    print("   - Campaign Manager: ✅")
    print("   - Multi-domain support: ✅")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 