"""
Enhanced AI DM Engine with Memory Integration
============================================

Integrates the layered memory system with AI DM responses for:
- Memory-aware storytelling
- Contextual recall and relevancy pings
- Personalization based on player history
- Emotional continuity and thematic callbacks
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from .enhanced_memory_system import LayeredMemorySystem, MemoryType, MemoryLayer, EmotionalContext

logger = logging.getLogger(__name__)

class EnhancedAIDMEngine:
    """AI DM Engine enhanced with layered memory system integration"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", campaign_id: str = "default"):
        self.ollama_url = ollama_url
        self.model = "llama3"
        
        # Initialize memory system
        self.memory_system = LayeredMemorySystem(campaign_id)
        
        # Core DnD 5e knowledge base
        self.dnd_context = """
        You are an expert Dungeon Master for DnD 5e with a sophisticated memory system.
        You remember everything about the player's journey, choices, and the world.
        
        Your capabilities include:
        - Dynamic rule interpretation and DC calculation
        - Memory-aware storytelling with callbacks and continuity
        - Emotional and thematic consistency
        - Personalized responses based on player history
        - Contextual recall of relevant past events
        
        Always maintain narrative coherence and emotional continuity.
        """
    
    def process_action(self, player_action: str, character_info: Dict[str, Any] = None, 
                      session_id: str = None, user_id: str = "player") -> str:
        """Process player action with memory integration"""
        
        # Add action to short-term memory
        self._add_action_memory(player_action, character_info, session_id, user_id)
        
        # Get relevant memories for context
        relevant_memories = self._get_relevant_memories(player_action, user_id)
        
        # Get player profile for personalization
        player_profile = self.memory_system.get_user_profile(user_id)
        
        # Build enhanced context
        context = self._build_enhanced_context(
            player_action, character_info, relevant_memories, player_profile
        )
        
        # Generate memory-aware response
        response = self._get_memory_aware_response(context, user_id, session_id)
        
        # Add response to memory
        self._add_response_memory(response, player_action, session_id, user_id)
        
        return response
    
    def _add_action_memory(self, action: str, character_info: Dict[str, Any], 
                          session_id: str, user_id: str):
        """Add player action to memory system"""
        content = {
            'action': action,
            'character_info': character_info,
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': session_id
        }
        
        # Determine memory type and emotional context
        memory_type = self._classify_action(action)
        emotional_context = self._extract_emotional_context(action)
        thematic_tags = self._extract_thematic_tags(action)
        
        # Add to short-term memory
        self.memory_system.add_memory(
            content=content,
            memory_type=memory_type,
            layer=MemoryLayer.SHORT_TERM,
            user_id=user_id,
            session_id=session_id,
            emotional_weight=0.6,
            emotional_context=emotional_context,
            thematic_tags=thematic_tags
        )
    
    def _get_relevant_memories(self, action: str, user_id: str) -> List[Dict[str, Any]]:
        """Get memories relevant to current action"""
        # Search for memories by action keywords
        relevant = self.memory_system.recall(
            query=action,
            user_id=user_id,
            min_significance=0.3
        )
        
        # Also get recent emotional context
        emotional_memories = self.memory_system.recall(
            user_id=user_id,
            min_significance=0.4
        )[:3]  # Last 3 significant memories
        
        # Combine and format for AI context
        all_relevant = relevant + emotional_memories
        return [self._format_memory_for_context(m) for m in all_relevant[:5]]
    
    def _format_memory_for_context(self, memory) -> Dict[str, Any]:
        """Format memory for AI context"""
        return {
            'content': memory.content,
            'type': memory.memory_type.value,
            'significance': memory.get_significance(),
            'age_hours': (datetime.utcnow() - memory.timestamp).total_seconds() / 3600,
            'emotional_context': [e.value for e in memory.emotional_context],
            'thematic_tags': memory.thematic_tags
        }
    
    def _build_enhanced_context(self, action: str, character_info: Dict[str, Any],
                               relevant_memories: List[Dict[str, Any]], 
                               player_profile: Dict[str, Any]) -> str:
        """Build enhanced context with memory integration"""
        
        context_parts = [self.dnd_context]
        
        # Character information
        if character_info:
            context_parts.append(f"Player Character:\n{self._format_character_info(character_info)}")
        
        # Relevant memories
        if relevant_memories:
            memory_context = "Relevant Memories:\n"
            for i, memory in enumerate(relevant_memories, 1):
                memory_context += f"{i}. {memory['content'].get('action', 'Previous event')} "
                memory_context += f"(Significance: {memory['significance']:.2f}, "
                memory_context += f"Age: {memory['age_hours']:.1f}h)\n"
            context_parts.append(memory_context)
        
        # Player profile insights
        if player_profile:
            profile_context = "Player Profile:\n"
            if 'emotions' in player_profile:
                emotions = dict(player_profile['emotions'])
                if emotions:
                    profile_context += f"Emotional tendencies: {', '.join(emotions.keys())}\n"
            if 'themes' in player_profile:
                themes = dict(player_profile['themes'])
                if themes:
                    profile_context += f"Thematic interests: {', '.join(themes.keys())}\n"
            context_parts.append(profile_context)
        
        # Current action
        context_parts.append(f"Current Action: \"{action}\"")
        
        # Instructions for memory-aware response
        context_parts.append("""
As the DM, respond with:
1. Memory-aware storytelling that references relevant past events
2. Emotional continuity with the player's journey
3. Thematic callbacks when appropriate
4. Proper DnD 5e mechanics and rulings
5. Personalized touches based on the player's history

Make your response engaging, narrative-focused, and mechanically accurate while maintaining perfect continuity.
""")
        
        return "\n".join(context_parts)
    
    def _get_memory_aware_response(self, context: str, user_id: str, session_id: str) -> str:
        """Get AI response with memory awareness using Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"You are a memory-aware DnD 5e Dungeon Master. Respond to the following context:\n\n{context}",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 600
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._fallback_response(context)
                
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return self._fallback_response(context)
    
    def _add_response_memory(self, response: str, original_action: str, 
                           session_id: str, user_id: str):
        """Add DM response to memory system"""
        content = {
            'response': response,
            'original_action': original_action,
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': session_id
        }
        
        # Add to mid-term memory for session continuity
        self.memory_system.add_memory(
            content=content,
            memory_type=MemoryType.EVENT,
            layer=MemoryLayer.MID_TERM,
            user_id=user_id,
            session_id=session_id,
            emotional_weight=0.5,
            thematic_tags=self._extract_thematic_tags(response)
        )
    
    def _classify_action(self, action: str) -> MemoryType:
        """Classify the type of action for memory storage"""
        action_lower = action.lower()
        
        if any(word in action_lower for word in ['attack', 'fight', 'combat', 'hit']):
            return MemoryType.EVENT
        elif any(word in action_lower for word in ['decide', 'choose', 'opt', 'select']):
            return MemoryType.DECISION
        elif any(word in action_lower for word in ['talk', 'speak', 'conversation', 'ask']):
            return MemoryType.RELATIONSHIP
        elif any(word in action_lower for word in ['explore', 'search', 'investigate', 'discover']):
            return MemoryType.WORLD_STATE
        elif any(word in action_lower for word in ['cast', 'spell', 'magic', 'ritual']):
            return MemoryType.EVENT
        else:
            return MemoryType.EVENT
    
    def _extract_emotional_context(self, text: str) -> List[EmotionalContext]:
        """Extract emotional context from text"""
        text_lower = text.lower()
        emotions = []
        
        if any(word in text_lower for word in ['happy', 'joy', 'excited', 'thrilled']):
            emotions.append(EmotionalContext.JOY)
        if any(word in text_lower for word in ['afraid', 'scared', 'fear', 'terrified']):
            emotions.append(EmotionalContext.FEAR)
        if any(word in text_lower for word in ['angry', 'rage', 'fury', 'mad']):
            emotions.append(EmotionalContext.ANGER)
        if any(word in text_lower for word in ['sad', 'depressed', 'melancholy', 'grief']):
            emotions.append(EmotionalContext.SADNESS)
        if any(word in text_lower for word in ['surprised', 'shocked', 'amazed', 'astonished']):
            emotions.append(EmotionalContext.SURPRISE)
        if any(word in text_lower for word in ['trust', 'believe', 'faith', 'confidence']):
            emotions.append(EmotionalContext.TRUST)
        if any(word in text_lower for word in ['anticipate', 'expect', 'hope', 'look forward']):
            emotions.append(EmotionalContext.ANTICIPATION)
        
        return emotions
    
    def _extract_thematic_tags(self, text: str) -> List[str]:
        """Extract thematic tags from text"""
        text_lower = text.lower()
        themes = []
        
        # DnD-specific themes
        if any(word in text_lower for word in ['combat', 'fight', 'battle', 'war']):
            themes.append('combat')
        if any(word in text_lower for word in ['magic', 'spell', 'arcane', 'mystical']):
            themes.append('magic')
        if any(word in text_lower for word in ['exploration', 'discovery', 'adventure']):
            themes.append('exploration')
        if any(word in text_lower for word in ['social', 'conversation', 'diplomacy']):
            themes.append('social')
        if any(word in text_lower for word in ['mystery', 'investigation', 'clue']):
            themes.append('mystery')
        if any(word in text_lower for word in ['moral', 'ethical', 'choice', 'dilemma']):
            themes.append('moral_choice')
        
        return themes
    
    def _format_character_info(self, character_info: Dict[str, Any]) -> str:
        """Format character information for AI context"""
        if not character_info:
            return "Generic adventurer"
        
        parts = []
        
        # Basic info
        if 'name' in character_info:
            parts.append(f"Name: {character_info['name']}")
        if 'race' in character_info:
            parts.append(f"Race: {character_info['race']}")
        if 'class' in character_info:
            parts.append(f"Class: {character_info['class']}")
        if 'level' in character_info:
            parts.append(f"Level: {character_info['level']}")
        
        # Ability scores
        if 'ability_scores' in character_info:
            abilities = character_info['ability_scores']
            ability_str = ", ".join([f"{k}: {v}" for k, v in abilities.items()])
            parts.append(f"Ability Scores: {ability_str}")
        
        # Skills
        if 'skills' in character_info:
            skills = character_info['skills']
            skill_str = ", ".join([f"{k}: +{v}" for k, v in skills.items()])
            parts.append(f"Skills: {skill_str}")
        
        # Equipment
        if 'equipment' in character_info:
            parts.append(f"Equipment: {', '.join(character_info['equipment'])}")
        
        return "\n".join(parts)
    
    def _fallback_response(self, context: str) -> str:
        """Fallback response when API is not available"""
        return "I remember your journey and the choices you've made. Based on our shared history, I'll guide you through this moment with the wisdom of our past adventures together."
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return self.memory_system.stats_summary()
    
    def save_memory_state(self) -> Dict[str, Any]:
        """Save current memory state"""
        return self.memory_system.to_dict()
    
    def load_memory_state(self, state: Dict[str, Any]):
        """Load memory state from saved data"""
        self.memory_system = LayeredMemorySystem.from_dict(state)

# Global instance
enhanced_ai_dm_engine = EnhancedAIDMEngine() 