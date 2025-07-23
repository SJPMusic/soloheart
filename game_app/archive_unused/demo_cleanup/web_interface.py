#!/usr/bin/env python3
"""
Enhanced Web UI for Dynamic Campaign Orchestrator with Multi-Character Support

Provides a modern web interface for the Solo DnD 5E game with real-time
orchestration, narrative generation, campaign progression tracking,
and multi-character support.
"""

import os
import json
import datetime
import logging
from typing import Dict, List, Any, Optional
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import threading
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add the parent directory to the path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dnd_game.narrative_bridge import NarrativeBridge
from narrative_engine.memory.emotional_memory import EmotionType
from narrative_engine.journaling.player_journal import JournalEntryType
from narrative_engine.narrative_structure.character_arcs import ArcType, ArcStatus
from narrative_engine.narrative_structure.plot_threads import ThreadType, ThreadStatus
from narrative_engine.core.campaign_orchestrator import OrchestrationPriority, OrchestrationEventType

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration from environment variables
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

# CORS configuration
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5001').split(',')
CORS(app, origins=cors_origins)

# Global campaign manager
campaign_manager = {}
active_sessions = {}

class CampaignSession:
    """Manages an active campaign session with real-time updates and multi-character support."""
    
    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        self.bridge = NarrativeBridge(campaign_id)
        self.session_start = datetime.datetime.now()
        self.last_orchestration = datetime.datetime.now()
        self.debug_mode = False
        self.event_history = []
        self.memory_highlights = []
        self.chat_history = []
        self.characters = {}
        self.active_character = None
        
        # Initialize campaign with some content
        self._initialize_campaign()
    
    def _initialize_campaign(self):
        """Initialize the campaign with some starting content."""
        try:
            # Create initial character arc
            self.bridge.create_character_arc(
                character_id="player",
                name="The Hero's Journey",
                arc_type=ArcType.GROWTH,
                description="Your journey from ordinary to extraordinary begins.",
                tags=["hero", "growth", "adventure"],
                emotional_themes=["determination", "curiosity", "courage"]
            )
            
            # Create initial plot thread
            self.bridge.create_plot_thread(
                name="The Mysterious Artifacts",
                thread_type=ThreadType.MYSTERY,
                description="Ancient artifacts have appeared in the world, causing strange phenomena.",
                priority=8,
                assigned_characters=["player"],
                tags=["mystery", "artifacts", "supernatural"]
            )
            
            # Add initial memory
            self.bridge.store_dnd_memory(
                content="You wake up in a strange world, feeling a mysterious connection to ancient artifacts.",
                memory_type="discovery",
                metadata={"location": "Unknown", "phenomenon": "artifacts"},
                tags=["awakening", "artifacts", "mystery"],
                primary_emotion=EmotionType.WONDER,
                emotional_intensity=0.8
            )
            
            # Initialize default character
            self.add_character("player", "Adventurer", "Hero")
            
            logger.info(f"Initialized campaign: {self.campaign_id}")
            
        except Exception as e:
            logger.error(f"Error initializing campaign: {e}")
    
    def add_character(self, character_id: str, name: str, character_class: str = "Adventurer"):
        """Add a new character to the campaign."""
        self.characters[character_id] = {
            "id": character_id,
            "name": name,
            "class": character_class,
            "created": datetime.datetime.now().isoformat(),
            "last_active": datetime.datetime.now().isoformat()
        }
        
        if not self.active_character:
            self.active_character = character_id
    
    def set_active_character(self, character_id: str):
        """Set the active character for the session."""
        if character_id in self.characters:
            self.active_character = character_id
            self.characters[character_id]["last_active"] = datetime.datetime.now().isoformat()
            return True
        return False
    
    def process_player_action(self, action: str, character_id: str = None, context: str = "") -> Dict[str, Any]:
        """Process a player action and generate narrative response."""
        try:
            # Use active character if none specified
            if not character_id:
                character_id = self.active_character or "player"
            
            # Get character info
            character = self.characters.get(character_id, {"name": "Adventurer", "class": "Hero"})
            
            # Store the action as memory
            self.bridge.store_dnd_memory(
                content=f"{character['name']} ({character['class']}): {action}",
                memory_type="action",
                metadata={
                    "character_id": character_id,
                    "character_name": character['name'],
                    "character_class": character['class'],
                    "context": context, 
                    "timestamp": datetime.datetime.now().isoformat()
                },
                tags=["player_action", "interaction", character['class'].lower()],
                primary_emotion=EmotionType.DETERMINATION,
                emotional_intensity=0.6
            )
            
            # Generate DM narration
            narration = self.bridge.generate_dm_narration(
                situation=action,
                player_actions=[action],
                world_context={"context": context, "character": character},
                emotional_context=["determination", "curiosity"]
            )
            
            # Check for orchestration events
            orchestration_events = self._check_orchestration_events()
            
            # Update campaign state
            campaign_state = self.bridge.analyze_campaign_state()
            
            # Get recent memories for highlights
            recent_memories = self.bridge.recall_related_memories(action, max_results=3)
            
            # Create chat entry
            chat_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "character_id": character_id,
                "character_name": character['name'],
                "character_class": character['class'],
                "action": action,
                "narration": narration,
                "orchestration_events": orchestration_events
            }
            
            self.chat_history.append(chat_entry)
            
            response = {
                "success": True,
                "narration": narration,
                "orchestration_events": orchestration_events,
                "campaign_state": campaign_state.to_dict(),
                "recent_memories": recent_memories,
                "character": character,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add to event history
            self.event_history.append({
                "type": "player_action",
                "content": action,
                "response": response,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing player action: {e}")
            return {
                "success": False,
                "error": str(e),
                "narration": "Something unexpected happens...",
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _check_orchestration_events(self) -> List[Dict[str, Any]]:
        """Check for new orchestration events and return them."""
        try:
            # Generate new events if enough time has passed
            time_since_last = datetime.datetime.now() - self.last_orchestration
            if time_since_last.total_seconds() > 30:  # Check every 30 seconds
                events = self.bridge.generate_orchestration_events(max_events=2)
                self.last_orchestration = datetime.datetime.now()
                
                # Convert events to dict format
                event_dicts = []
                for event in events:
                    event_dict = event.to_dict()
                    event_dict["suggested_response"] = self._generate_suggested_response(event)
                    event_dicts.append(event_dict)
                
                return event_dicts
            
            return []
            
        except Exception as e:
            logger.error(f"Error checking orchestration events: {e}")
            return []
    
    def _generate_suggested_response(self, event) -> str:
        """Generate a suggested response for an orchestration event."""
        if event.event_type == OrchestrationEventType.QUEST_SUGGESTION:
            return "Consider investigating this quest opportunity."
        elif event.event_type == OrchestrationEventType.ENCOUNTER_TRIGGER:
            return "Prepare for a potential encounter."
        elif event.event_type == OrchestrationEventType.CHARACTER_DEVELOPMENT:
            return "This could be a moment for character growth."
        elif event.event_type == OrchestrationEventType.PLOT_DEVELOPMENT:
            return "A plot development is unfolding."
        else:
            return "Something interesting is happening."
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """Get a comprehensive campaign summary."""
        try:
            summary = self.bridge.get_campaign_summary()
            progression = self.bridge.get_campaign_progression_suggestions()
            
            # Get character arcs
            arcs = self.bridge.get_character_arcs(status=ArcStatus.ACTIVE)
            
            # Get plot threads
            threads = self.bridge.get_plot_threads(status=ThreadStatus.OPEN)
            
            # Get recent journal entries
            journal_entries = self.bridge.get_journal_entries(max_entries=5)
            
            # Get emotional memory highlights
            emotional_memories = self.bridge.recall_emotional_memories(
                emotion_type=EmotionType.WONDER,  # Use single emotion type
                max_results=3
            )
            
            return {
                "summary": summary,
                "progression": progression,
                "character_arcs": arcs,
                "plot_threads": threads,
                "journal_entries": journal_entries,
                "emotional_memories": emotional_memories,
                "characters": self.characters,
                "active_character": self.active_character,
                "chat_history_count": len(self.chat_history),
                "session_duration": str(datetime.datetime.now() - self.session_start)
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign summary: {e}")
            return {"error": str(e)}
    
    def get_sidebar_data(self, character_id: str = None) -> Dict[str, Any]:
        """Get data for the sidebar display."""
        try:
            if not character_id:
                character_id = self.active_character or "player"
            
            character = self.characters.get(character_id, {})
            
            # Get character's emotional state from recent memories
            recent_memories = self.bridge.recall_related_memories(
                query=character.get('name', 'adventurer'), 
                max_results=5
            )
            
            # Get character's active arcs
            character_arcs = self.bridge.get_character_arcs(
                character_id=character_id,
                status=ArcStatus.ACTIVE
            )
            
            # Get plot threads assigned to this character
            plot_threads = self.bridge.get_plot_threads(
                assigned_characters=[character_id],
                status=ThreadStatus.OPEN
            )
            
            # Get character's recent journal entries
            journal_entries = self.bridge.get_journal_entries(
                character_id=character_id,
                max_entries=3
            )
            
            return {
                "character": character,
                "recent_memories": recent_memories,
                "character_arcs": character_arcs,
                "plot_threads": plot_threads,
                "journal_entries": journal_entries
            }
            
        except Exception as e:
            logger.error(f"Error getting sidebar data: {e}")
            return {"error": str(e)}
    
    def save_campaign_state(self, save_name: str = None) -> Dict[str, Any]:
        """Save the current campaign state."""
        try:
            if not save_name:
                save_name = f"campaign_{self.campaign_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Export campaign data
            campaign_data = {
                "campaign_id": self.campaign_id,
                "save_name": save_name,
                "save_timestamp": datetime.datetime.now().isoformat(),
                "session_data": {
                    "session_start": self.session_start.isoformat(),
                    "last_orchestration": self.last_orchestration.isoformat(),
                    "debug_mode": self.debug_mode,
                    "characters": self.characters,
                    "active_character": self.active_character,
                    "chat_history": self.chat_history[-50:],  # Last 50 entries
                    "event_history": self.event_history[-20:]  # Last 20 events
                }
            }
            
            # Save to file
            save_dir = "campaign_saves"
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f"{save_name}.json")
            
            with open(save_path, 'w') as f:
                json.dump(campaign_data, f, indent=2, default=str)
            
            return {
                "success": True,
                "save_name": save_name,
                "save_path": save_path,
                "message": f"Campaign saved as {save_name}"
            }
            
        except Exception as e:
            logger.error(f"Error saving campaign: {e}")
            return {"success": False, "error": str(e)}
    
    def load_campaign_state(self, save_name: str) -> Dict[str, Any]:
        """Load a campaign state from save."""
        try:
            save_path = os.path.join("campaign_saves", f"{save_name}.json")
            
            if not os.path.exists(save_path):
                return {"success": False, "error": "Save file not found"}
            
            with open(save_path, 'r') as f:
                campaign_data = json.load(f)
            
            # Restore session data
            session_data = campaign_data.get("session_data", {})
            self.characters = session_data.get("characters", {})
            self.active_character = session_data.get("active_character")
            self.chat_history = session_data.get("chat_history", [])
            self.event_history = session_data.get("event_history", [])
            
            # Restore timestamps
            if session_data.get("session_start"):
                self.session_start = datetime.datetime.fromisoformat(session_data["session_start"])
            if session_data.get("last_orchestration"):
                self.last_orchestration = datetime.datetime.fromisoformat(session_data["last_orchestration"])
            
            self.debug_mode = session_data.get("debug_mode", False)
            
            return {
                "success": True,
                "save_name": save_name,
                "message": f"Campaign loaded from {save_name}"
            }
            
        except Exception as e:
            logger.error(f"Error loading campaign: {e}")
            return {"success": False, "error": str(e)}
    
    def get_saved_campaigns(self) -> List[Dict[str, Any]]:
        """Get list of saved campaigns."""
        try:
            save_dir = "campaign_saves"
            if not os.path.exists(save_dir):
                return []
            
            saves = []
            for filename in os.listdir(save_dir):
                if filename.endswith('.json'):
                    save_path = os.path.join(save_dir, filename)
                    try:
                        with open(save_path, 'r') as f:
                            data = json.load(f)
                        
                        saves.append({
                            "save_name": data.get("save_name", filename.replace('.json', '')),
                            "campaign_id": data.get("campaign_id", "unknown"),
                            "save_timestamp": data.get("save_timestamp", ""),
                            "characters": data.get("session_data", {}).get("characters", {}),
                            "chat_history_count": len(data.get("session_data", {}).get("chat_history", []))
                        })
                    except Exception as e:
                        logger.error(f"Error reading save file {filename}: {e}")
                        continue
            
            # Sort by timestamp (newest first)
            saves.sort(key=lambda x: x.get("save_timestamp", ""), reverse=True)
            return saves
            
        except Exception as e:
            logger.error(f"Error getting saved campaigns: {e}")
            return []
    
    def toggle_debug_mode(self):
        """Toggle debug mode on/off."""
        self.debug_mode = not self.debug_mode
        return self.debug_mode
    
    def add_journal_entry(self, title: str, content: str, character_id: str = None, entry_type: str = "player_written") -> bool:
        """Add a journal entry for the current character."""
        try:
            if not character_id:
                character_id = self.active_character or "player"
            
            character = self.characters.get(character_id, {"name": "Adventurer"})
            
            success = self.bridge.add_journal_entry(
                title=title,
                content=content,
                character_id=character_id,
                entry_type=entry_type
            )
            
            if success:
                logger.info(f"Added journal entry for {character['name']}: {title}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding journal entry: {e}")
            return False
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information for the current session."""
        try:
            return {
                "campaign_id": self.campaign_id,
                "session_start": self.session_start.isoformat(),
                "session_duration": str(datetime.datetime.now() - self.session_start),
                "debug_mode": self.debug_mode,
                "characters": self.characters,
                "active_character": self.active_character,
                "chat_history_count": len(self.chat_history),
                "event_history_count": len(self.event_history),
                "last_orchestration": self.last_orchestration.isoformat(),
                "memory_stats": self.bridge.get_memory_statistics(),
                "campaign_state": self.bridge.analyze_campaign_state().to_dict()
            }
        except Exception as e:
            logger.error(f"Error getting debug info: {e}")
            return {"error": str(e)}

def get_or_create_session(campaign_id: str) -> CampaignSession:
    """Get or create a campaign session."""
    if campaign_id not in active_sessions:
        active_sessions[campaign_id] = CampaignSession(campaign_id)
    return active_sessions[campaign_id]

def get_narrative_bridge(campaign_id: str) -> NarrativeBridge:
    """Get the narrative bridge for a campaign."""
    session = get_or_create_session(campaign_id)
    return session.bridge

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/campaign/<campaign_id>/action', methods=['POST'])
def process_action(campaign_id):
    """Process a player action."""
    try:
        data = request.get_json()
        action = data.get('action', '')
        character_id = data.get('character_id')
        context = data.get('context', '')
        
        if not action:
            return jsonify({"error": "No action provided"}), 400
        
        session = get_or_create_session(campaign_id)
        response = session.process_player_action(action, character_id, context)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing action: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/summary')
def get_summary(campaign_id):
    """Get campaign summary."""
    try:
        session = get_or_create_session(campaign_id)
        summary = session.get_campaign_summary()
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/sidebar')
def get_sidebar_data(campaign_id):
    """Get sidebar data for the active character."""
    try:
        data = request.get_json() or {}
        character_id = data.get('character_id')
        
        session = get_or_create_session(campaign_id)
        sidebar_data = session.get_sidebar_data(character_id)
        return jsonify(sidebar_data)
        
    except Exception as e:
        logger.error(f"Error getting sidebar data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/characters', methods=['GET', 'POST'])
def manage_characters(campaign_id):
    """Get characters or add a new character."""
    try:
        session = get_or_create_session(campaign_id)
        
        if request.method == 'GET':
            return jsonify({
                "characters": session.characters,
                "active_character": session.active_character
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            character_id = data.get('character_id')
            name = data.get('name')
            character_class = data.get('class', 'Adventurer')
            
            if not character_id or not name:
                return jsonify({"error": "character_id and name are required"}), 400
            
            session.add_character(character_id, name, character_class)
            return jsonify({
                "success": True,
                "characters": session.characters,
                "active_character": session.active_character
            })
        
    except Exception as e:
        logger.error(f"Error managing characters: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/characters/<character_id>/activate', methods=['POST'])
def activate_character(campaign_id, character_id):
    """Activate a character."""
    try:
        session = get_or_create_session(campaign_id)
        success = session.set_active_character(character_id)
        
        if success:
            return jsonify({
                "success": True,
                "active_character": session.active_character
            })
        else:
            return jsonify({"error": "Character not found"}), 404
        
    except Exception as e:
        logger.error(f"Error activating character: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/chat/history')
def get_chat_history(campaign_id):
    """Get chat history."""
    try:
        session = get_or_create_session(campaign_id)
        return jsonify({
            "chat_history": session.chat_history,
            "total_entries": len(session.chat_history)
        })
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/save', methods=['POST'])
def save_campaign(campaign_id):
    """Save campaign state."""
    try:
        data = request.get_json() or {}
        save_name = data.get('save_name')
        
        session = get_or_create_session(campaign_id)
        result = session.save_campaign_state(save_name)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error saving campaign: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/load', methods=['POST'])
def load_campaign(campaign_id):
    """Load campaign state."""
    try:
        data = request.get_json()
        save_name = data.get('save_name')
        
        if not save_name:
            return jsonify({"error": "save_name is required"}), 400
        
        session = get_or_create_session(campaign_id)
        result = session.load_campaign_state(save_name)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error loading campaign: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/saves')
def get_saved_campaigns(campaign_id):
    """Get list of saved campaigns."""
    try:
        session = get_or_create_session(campaign_id)
        saves = session.get_saved_campaigns()
        return jsonify({"saves": saves})
        
    except Exception as e:
        logger.error(f"Error getting saved campaigns: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/debug/toggle', methods=['POST'])
def toggle_debug(campaign_id):
    """Toggle debug mode."""
    try:
        session = get_or_create_session(campaign_id)
        debug_mode = session.toggle_debug_mode()
        return jsonify({"debug_mode": debug_mode})
        
    except Exception as e:
        logger.error(f"Error toggling debug: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/debug/info')
def get_debug_info(campaign_id):
    """Get debug information."""
    try:
        session = get_or_create_session(campaign_id)
        debug_info = session.get_debug_info()
        return jsonify(debug_info)
        
    except Exception as e:
        logger.error(f"Error getting debug info: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/journal', methods=['POST'])
def add_journal_entry(campaign_id):
    """Add a journal entry."""
    try:
        data = request.get_json()
        title = data.get('title', '')
        content = data.get('content', '')
        character_id = data.get('character_id')
        entry_type = data.get('entry_type', 'player_written')
        
        if not content:
            return jsonify({"error": "Content is required"}), 400
        
        session = get_or_create_session(campaign_id)
        success = session.add_journal_entry(title, content, character_id, entry_type)
        
        if success:
            return jsonify({"success": True, "message": "Journal entry added"})
        else:
            return jsonify({"error": "Failed to add journal entry"}), 500
        
    except Exception as e:
        logger.error(f"Error adding journal entry: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/orchestration/events')
def get_orchestration_events(campaign_id):
    """Get orchestration events."""
    try:
        session = get_or_create_session(campaign_id)
        events = session._check_orchestration_events()
        return jsonify({"events": events})
        
    except Exception as e:
        logger.error(f"Error getting orchestration events: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/orchestration/execute/<event_id>', methods=['POST'])
def execute_orchestration_event(campaign_id, event_id):
    """Execute an orchestration event."""
    try:
        session = get_or_create_session(campaign_id)
        data = request.get_json() or {}
        execution_notes = data.get('notes', '')
        
        success = session.bridge.execute_orchestration_event(event_id, execution_notes)
        
        return jsonify({
            "success": success,
            "event_id": event_id,
            "execution_notes": execution_notes
        })
    except Exception as e:
        logger.error(f"Error executing orchestration event: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/orchestration/triggered-events', methods=['POST'])
def get_triggered_events(campaign_id):
    """Get orchestration events triggered by the last action."""
    try:
        session = get_or_create_session(campaign_id)
        data = request.get_json() or {}
        
        action_context = {
            'action': data.get('action', ''),
            'character': data.get('character', ''),
            'location': data.get('location', ''),
            'emotional_context': data.get('emotional_context', [])
        }
        
        triggered_events = session.bridge.get_triggered_orchestration_events(action_context)
        
        return jsonify({
            "success": True,
            "triggered_events": triggered_events,
            "count": len(triggered_events)
        })
    except Exception as e:
        logger.error(f"Error getting triggered events: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/orchestration/event-history')
def get_event_history(campaign_id):
    """Get recent orchestration event history for timeline display."""
    try:
        session = get_or_create_session(campaign_id)
        limit = request.args.get('limit', 10, type=int)
        
        event_history = session.bridge.get_orchestration_event_history(limit)
        
        return jsonify({
            "success": True,
            "event_history": event_history,
            "count": len(event_history)
        })
    except Exception as e:
        logger.error(f"Error getting event history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/orchestration/active-events')
def get_active_events(campaign_id):
    """Get all currently active orchestration events."""
    try:
        session = get_or_create_session(campaign_id)
        
        active_events = session.bridge.get_active_orchestration_events()
        
        return jsonify({
            "success": True,
            "active_events": active_events,
            "count": len(active_events)
        })
    except Exception as e:
        logger.error(f"Error getting active events: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/orchestration/insights')
def get_orchestration_insights(campaign_id):
    """Get insights about the current orchestration state."""
    try:
        session = get_or_create_session(campaign_id)
        
        insights = session.bridge.get_orchestration_insights()
        
        return jsonify({
            "success": True,
            "insights": insights
        })
    except Exception as e:
        logger.error(f"Error getting orchestration insights: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/narrative-dynamics')
def get_narrative_dynamics(campaign_id):
    """Get real-time narrative dynamics including conflicts."""
    try:
        dynamics = campaign_manager.get_narrative_dynamics(campaign_id)
        return jsonify(dynamics)
    except Exception as e:
        logger.error(f"Error getting narrative dynamics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/conflicts')
def get_conflict_nodes(campaign_id):
    """Get all active conflict nodes for the campaign."""
    try:
        conflicts = campaign_manager.get_conflict_nodes(campaign_id)
        return jsonify(conflicts)
    except Exception as e:
        logger.error(f"Error getting conflict nodes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/conflicts/<conflict_id>/resolve', methods=['POST'])
def resolve_conflict(campaign_id, conflict_id):
    """Resolve a conflict with a specific resolution."""
    try:
        data = request.get_json()
        resolution_id = data.get('resolution_id')
        
        if not resolution_id:
            return jsonify({'error': 'resolution_id is required'}), 400
        
        success = campaign_manager.resolve_conflict(conflict_id, resolution_id, campaign_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Conflict resolved successfully'})
        else:
            return jsonify({'error': 'Failed to resolve conflict'}), 400
            
    except Exception as e:
        logger.error(f"Error resolving conflict: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/conflicts/summary')
def get_conflict_summary(campaign_id):
    """Get a summary of conflict activity for the campaign."""
    try:
        summary = campaign_manager.get_conflict_summary(campaign_id)
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Error getting conflict summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/diagnostics/timeline')
def get_diagnostics_timeline(campaign_id):
    try:
        session = get_or_create_session(campaign_id)
        timeline = session.bridge.get_conflict_timeline(campaign_id)
        return jsonify(timeline)
    except Exception as e:
        logger.error(f"Error getting diagnostics timeline: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/diagnostics/arcs')
def get_diagnostics_arcs(campaign_id):
    try:
        session = get_or_create_session(campaign_id)
        arc_map = session.bridge.get_arc_map(campaign_id)
        return jsonify(arc_map)
    except Exception as e:
        logger.error(f"Error getting diagnostics arcs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/diagnostics/heatmap')
def get_diagnostics_heatmap(campaign_id):
    try:
        session = get_or_create_session(campaign_id)
        heatmap = session.bridge.get_emotion_heatmap(campaign_id)
        return jsonify(heatmap)
    except Exception as e:
        logger.error(f"Error getting diagnostics heatmap: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/diagnostics/report')
def get_diagnostics_report(campaign_id):
    try:
        session = get_or_create_session(campaign_id)
        report = session.bridge.get_diagnostic_report(campaign_id)
        return jsonify(report)
    except Exception as e:
        logger.error(f"Error getting diagnostics report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/lore', methods=['GET'])
def get_lore_entries(campaign_id):
    """Get all lore entries for a campaign"""
    try:
        bridge = get_narrative_bridge(campaign_id)
        lore_data = bridge.get_lore_panel_data()
        return jsonify(lore_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/lore/search', methods=['GET'])
def search_lore_entries(campaign_id):
    """Search lore entries"""
    try:
        query = request.args.get('q', '')
        lore_types = request.args.getlist('type')
        tags = request.args.getlist('tag')
        
        bridge = get_narrative_bridge(campaign_id)
        results = bridge.search_lore_entries(query, lore_types, tags)
        return jsonify({"results": results, "query": query})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/lore/<lore_id>', methods=['GET'])
def get_lore_entry(campaign_id, lore_id):
    """Get a specific lore entry by ID"""
    try:
        bridge = get_narrative_bridge(campaign_id)
        entry = bridge.get_lore_entry_by_id(lore_id)
        if entry:
            return jsonify(entry)
        else:
            return jsonify({"error": "Lore entry not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/lore', methods=['POST'])
def create_lore_entry(campaign_id):
    """Create a new lore entry"""
    try:
        data = request.get_json()
        bridge = get_narrative_bridge(campaign_id)
        
        lore_id = bridge.create_lore_entry(
            title=data.get('title'),
            lore_type=data.get('type'),
            content=data.get('content'),
            tags=data.get('tags', []),
            discovered_by=data.get('discovered_by'),
            discovery_context=data.get('discovery_context'),
            importance_level=data.get('importance_level', 1),
            is_secret=data.get('is_secret', False)
        )
        
        if lore_id:
            return jsonify({"success": True, "lore_id": lore_id})
        else:
            return jsonify({"error": "Failed to create lore entry"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/lore/<lore_id>/link', methods=['POST'])
def link_lore_entry(campaign_id, lore_id):
    """Link a lore entry to another item"""
    try:
        data = request.get_json()
        bridge = get_narrative_bridge(campaign_id)
        
        success = bridge.link_lore_to_item(
            lore_id=lore_id,
            item_type=data.get('item_type'),
            item_id=data.get('item_id')
        )
        
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to link lore entry"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/lore/type/<lore_type>', methods=['GET'])
def get_lore_by_type(campaign_id, lore_type):
    """Get all lore entries of a specific type"""
    try:
        bridge = get_narrative_bridge(campaign_id)
        entries = bridge.get_lore_by_type(lore_type)
        return jsonify({"entries": entries, "type": lore_type})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/campaign/<campaign_id>/lore/tag/<tag>', methods=['GET'])
def get_lore_by_tag(campaign_id, tag):
    """Get lore entries by tag."""
    try:
        bridge = get_narrative_bridge(campaign_id)
        entries = bridge.get_lore_by_tag(tag)
        return jsonify({
            "success": True,
            "entries": entries,
            "tag": tag
        })
    except Exception as e:
        logger.error(f"Error getting lore by tag: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint for connection status."""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "0.1.0"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Create campaign_saves directory if it doesn't exist
    os.makedirs('campaign_saves', exist_ok=True)
    
    print("Starting Enhanced DnD Web Interface...")
    print("Access the game at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 