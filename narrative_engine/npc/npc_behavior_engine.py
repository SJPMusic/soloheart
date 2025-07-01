"""
NPC Behavior Engine - The Narrative Engine
=========================================

Implements adaptive NPC behavior based on emotional memory and context.
Supports the roadmap principle: "Emotional realism matters"

Features:
- Generate responses based on emotional state and memory context
- Integrate with emotional memory system and vector memory
- Memory-driven modifiers for tone, pacing, and cooperation
- JSON-compatible outputs for AI context pipelines
- Campaign-aware behavior for multi-campaign support

Future enhancements:
- Personality trait integration
- Relationship dynamics
- Cultural background influence
- Situational awareness
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import random

logger = logging.getLogger(__name__)

@dataclass
class BehaviorModifier:
    """Modifier for NPC behavior based on emotional state"""
    tone_modifier: str
    pacing_modifier: str
    cooperation_level: float  # 0.0 to 1.0
    detail_level: str  # "minimal", "normal", "detailed"
    trust_level: float  # 0.0 to 1.0
    reasoning: str

@dataclass
class NPCResponse:
    """Structured NPC response with behavioral context"""
    npc_id: str
    response_text: str
    emotional_state: Dict[str, Any]
    behavior_modifiers: BehaviorModifier
    memory_influence: List[Dict[str, Any]]
    response_confidence: float
    timestamp: str

class NPCBehaviorEngine:
    """
    Adaptive NPC behavior engine.
    
    Aligns with roadmap principle: "Emotional realism matters"
    - Generates responses based on emotional memory
    - Integrates with memory systems for context
    - Provides memory-driven behavior modifiers
    - Supports campaign-aware interactions
    """
    
    def __init__(self):
        self.npc_personalities: Dict[str, Dict[str, Any]] = {}
        self.behavior_history: Dict[str, List[NPCResponse]] = {}
        self.response_templates: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default response templates
        self._initialize_response_templates()
        
        logger.info("NPC behavior engine initialized")
    
    def _initialize_response_templates(self):
        """Initialize default response templates for different emotional states"""
        self.response_templates = {
            'joy': {
                'greeting': ['Hello there!', 'Welcome!', 'Great to see you!'],
                'cooperation': ['I\'d be happy to help!', 'Of course, let\'s work together!'],
                'detail_level': 'detailed',
                'tone': 'warm and enthusiastic'
            },
            'sadness': {
                'greeting': ['Hello...', 'Oh, it\'s you...', 'I suppose you\'re here...'],
                'cooperation': ['I\'ll try to help...', 'I suppose I can assist...'],
                'detail_level': 'minimal',
                'tone': 'quiet and withdrawn'
            },
            'anger': {
                'greeting': ['What do you want?', 'You again...', 'Make it quick.'],
                'cooperation': ['Fine, but make it worth my while.', 'I\'ll help, but I don\'t like it.'],
                'detail_level': 'minimal',
                'tone': 'sharp and direct'
            },
            'fear': {
                'greeting': ['Oh! You startled me...', 'Hello... I think...', 'Is everything alright?'],
                'cooperation': ['I\'ll help if I can...', 'I\'m not sure, but I\'ll try...'],
                'detail_level': 'normal',
                'tone': 'nervous and uncertain'
            },
            'trust': {
                'greeting': ['Welcome, friend!', 'Good to see you again!', 'Come in, come in!'],
                'cooperation': ['Absolutely!', 'I trust you completely.', 'Let\'s work together!'],
                'detail_level': 'detailed',
                'tone': 'friendly and open'
            },
            'neutral': {
                'greeting': ['Hello.', 'Greetings.', 'You\'re here.'],
                'cooperation': ['I can help with that.', 'I\'ll assist you.', 'Let\'s proceed.'],
                'detail_level': 'normal',
                'tone': 'calm and measured'
            }
        }
    
    def generate_response(
        self,
        npc_id: str,
        emotion_state: Dict[str, Any],
        memory_context: List[Dict[str, Any]],
        player_input: str,
        campaign_id: Optional[str] = None
    ) -> NPCResponse:
        """
        Generate NPC response based on emotional state and memory context.
        
        Args:
            npc_id: NPC identifier
            emotion_state: Current emotional state from emotional memory system
            memory_context: Relevant memories from vector memory system
            player_input: Player's input/request
            campaign_id: Optional campaign identifier
        
        Returns:
            NPCResponse with behavioral context
        """
        # Get dominant emotion
        dominant_emotion = emotion_state.get('dominant_emotion', 'neutral')
        emotional_intensity = emotion_state.get('emotional_intensity', 0.0)
        
        # Generate behavior modifiers
        behavior_modifiers = self._generate_behavior_modifiers(
            dominant_emotion, emotional_intensity, memory_context
        )
        
        # Generate response text
        response_text = self._generate_response_text(
            npc_id, dominant_emotion, player_input, behavior_modifiers, memory_context
        )
        
        # Calculate response confidence
        response_confidence = self._calculate_response_confidence(
            emotion_state, memory_context, behavior_modifiers
        )
        
        # Create NPC response
        npc_response = NPCResponse(
            npc_id=npc_id,
            response_text=response_text,
            emotional_state=emotion_state,
            behavior_modifiers=behavior_modifiers,
            memory_influence=memory_context,
            response_confidence=response_confidence,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Store in behavior history
        if campaign_id:
            if campaign_id not in self.behavior_history:
                self.behavior_history[campaign_id] = {}
            if npc_id not in self.behavior_history[campaign_id]:
                self.behavior_history[campaign_id][npc_id] = []
            self.behavior_history[campaign_id][npc_id].append(npc_response)
        
        logger.info(f"Generated response for {npc_id} with {dominant_emotion} emotion (confidence: {response_confidence:.2f})")
        
        return npc_response
    
    def _generate_behavior_modifiers(
        self,
        dominant_emotion: str,
        emotional_intensity: float,
        memory_context: List[Dict[str, Any]]
    ) -> BehaviorModifier:
        """Generate behavior modifiers based on emotional state and memories"""
        
        # Base modifiers from emotional state
        base_modifiers = {
            'joy': {
                'tone_modifier': 'warm and enthusiastic',
                'pacing_modifier': 'energetic',
                'cooperation_level': 0.9,
                'detail_level': 'detailed',
                'trust_level': 0.8
            },
            'sadness': {
                'tone_modifier': 'quiet and withdrawn',
                'pacing_modifier': 'slow',
                'cooperation_level': 0.6,
                'detail_level': 'minimal',
                'trust_level': 0.5
            },
            'anger': {
                'tone_modifier': 'sharp and direct',
                'pacing_modifier': 'abrupt',
                'cooperation_level': 0.3,
                'detail_level': 'minimal',
                'trust_level': 0.2
            },
            'fear': {
                'tone_modifier': 'nervous and uncertain',
                'pacing_modifier': 'hesitant',
                'cooperation_level': 0.7,
                'detail_level': 'normal',
                'trust_level': 0.4
            },
            'trust': {
                'tone_modifier': 'friendly and open',
                'pacing_modifier': 'relaxed',
                'cooperation_level': 1.0,
                'detail_level': 'detailed',
                'trust_level': 0.9
            },
            'neutral': {
                'tone_modifier': 'calm and measured',
                'pacing_modifier': 'steady',
                'cooperation_level': 0.7,
                'detail_level': 'normal',
                'trust_level': 0.6
            }
        }
        
        # Get base modifiers
        base = base_modifiers.get(dominant_emotion, base_modifiers['neutral'])
        
        # Apply memory-driven modifications
        memory_modifiers = self._apply_memory_modifiers(memory_context, base)
        
        # Apply emotional intensity scaling
        intensity_scale = min(emotional_intensity / 5.0, 1.0)
        
        # Generate reasoning
        reasoning = self._generate_modifier_reasoning(dominant_emotion, emotional_intensity, memory_context)
        
        return BehaviorModifier(
            tone_modifier=memory_modifiers['tone_modifier'],
            pacing_modifier=memory_modifiers['pacing_modifier'],
            cooperation_level=max(0.0, min(1.0, memory_modifiers['cooperation_level'])),
            detail_level=memory_modifiers['detail_level'],
            trust_level=max(0.0, min(1.0, memory_modifiers['trust_level'])),
            reasoning=reasoning
        )
    
    def _apply_memory_modifiers(
        self,
        memory_context: List[Dict[str, Any]],
        base_modifiers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply memory-driven modifications to behavior"""
        modifiers = base_modifiers.copy()
        
        # Analyze memory context for behavioral influence
        betrayal_count = 0
        kindness_count = 0
        violence_count = 0
        cooperation_count = 0
        
        for memory in memory_context:
            event_type = memory.get('event_type', '')
            if 'betrayal' in event_type.lower():
                betrayal_count += 1
            elif 'kindness' in event_type.lower():
                kindness_count += 1
            elif 'violence' in event_type.lower():
                violence_count += 1
            elif 'cooperation' in event_type.lower():
                cooperation_count += 1
        
        # Apply memory-based adjustments
        if betrayal_count > 0:
            modifiers['cooperation_level'] *= 0.5
            modifiers['trust_level'] *= 0.3
            modifiers['tone_modifier'] = 'guarded and suspicious'
        
        if kindness_count > 0:
            modifiers['cooperation_level'] *= 1.2
            modifiers['trust_level'] *= 1.1
        
        if violence_count > 0:
            modifiers['cooperation_level'] *= 0.7
            modifiers['trust_level'] *= 0.6
            modifiers['tone_modifier'] = 'cautious and defensive'
        
        if cooperation_count > 0:
            modifiers['cooperation_level'] *= 1.1
            modifiers['trust_level'] *= 1.05
        
        return modifiers
    
    def _generate_response_text(
        self,
        npc_id: str,
        dominant_emotion: str,
        player_input: str,
        behavior_modifiers: BehaviorModifier,
        memory_context: List[Dict[str, Any]]
    ) -> str:
        """Generate response text based on emotional state and modifiers"""
        
        # Get response template
        template = self.response_templates.get(dominant_emotion, self.response_templates['neutral'])
        
        # Determine response type based on player input
        if any(word in player_input.lower() for word in ['hello', 'hi', 'greet', 'meet']):
            response_pool = template['greeting']
        elif any(word in player_input.lower() for word in ['help', 'assist', 'support', 'aid']):
            response_pool = template['cooperation']
        else:
            # Generic response based on emotion
            response_pool = template['greeting'] + template['cooperation']
        
        # Select base response
        base_response = random.choice(response_pool)
        
        # Apply behavioral modifications
        response = self._apply_behavioral_modifications(
            base_response, behavior_modifiers, memory_context
        )
        
        return response
    
    def _apply_behavioral_modifications(
        self,
        base_response: str,
        behavior_modifiers: BehaviorModifier,
        memory_context: List[Dict[str, Any]]
    ) -> str:
        """Apply behavioral modifications to response text"""
        response = base_response
        
        # Apply cooperation level modifications
        if behavior_modifiers.cooperation_level < 0.4:
            response += " But I'm not sure about this..."
        elif behavior_modifiers.cooperation_level > 0.8:
            response += " I'm happy to help!"
        
        # Apply detail level modifications
        if behavior_modifiers.detail_level == 'minimal':
            response = response.split('.')[0] + '.'  # Keep only first sentence
        elif behavior_modifiers.detail_level == 'detailed':
            if memory_context:
                memory_ref = f" I remember when {memory_context[0].get('event_type', 'something happened')}."
                response += memory_ref
        
        # Apply trust level modifications
        if behavior_modifiers.trust_level < 0.3:
            response += " I'll need to think about this."
        elif behavior_modifiers.trust_level > 0.8:
            response += " You can count on me."
        
        return response
    
    def _generate_modifier_reasoning(
        self,
        dominant_emotion: str,
        emotional_intensity: float,
        memory_context: List[Dict[str, Any]]
    ) -> str:
        """Generate reasoning for behavior modifiers"""
        reasoning_parts = [f"Dominant emotion: {dominant_emotion}"]
        
        if emotional_intensity > 0.7:
            reasoning_parts.append("High emotional intensity affecting behavior")
        
        if memory_context:
            memory_types = [mem.get('event_type', 'unknown') for mem in memory_context[:2]]
            reasoning_parts.append(f"Recent memories: {', '.join(memory_types)}")
        
        # Count memory types for reasoning
        betrayal_count = sum(1 for mem in memory_context if 'betrayal' in mem.get('event_type', '').lower())
        if betrayal_count > 0:
            reasoning_parts.append(f"Betrayal memories ({betrayal_count}) reducing trust")
        
        kindness_count = sum(1 for mem in memory_context if 'kindness' in mem.get('event_type', '').lower())
        if kindness_count > 0:
            reasoning_parts.append(f"Kindness memories ({kindness_count}) increasing cooperation")
        
        return "; ".join(reasoning_parts)
    
    def _calculate_response_confidence(
        self,
        emotion_state: Dict[str, Any],
        memory_context: List[Dict[str, Any]],
        behavior_modifiers: BehaviorModifier
    ) -> float:
        """Calculate confidence in the generated response"""
        # Base confidence on emotional stability
        emotional_stability = emotion_state.get('emotional_stability', 0.5)
        
        # Adjust based on memory context relevance
        memory_relevance = min(len(memory_context) / 5.0, 1.0)
        
        # Adjust based on behavior modifier consistency
        modifier_consistency = 1.0
        if behavior_modifiers.cooperation_level < 0.3 and behavior_modifiers.trust_level > 0.7:
            modifier_consistency = 0.7  # Inconsistent modifiers
        
        # Calculate final confidence
        confidence = (emotional_stability + memory_relevance + modifier_consistency) / 3.0
        
        return min(confidence, 1.0)
    
    def get_behavior_history(
        self,
        npc_id: str,
        campaign_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get behavior history for an NPC.
        
        Args:
            npc_id: NPC identifier
            campaign_id: Optional campaign filter
            limit: Maximum number of responses to return
        
        Returns:
            List of behavior history entries
        """
        history = []
        
        if campaign_id and campaign_id in self.behavior_history:
            if npc_id in self.behavior_history[campaign_id]:
                history = self.behavior_history[campaign_id][npc_id][-limit:]
        else:
            # Combine all campaign histories
            for campaign_histories in self.behavior_history.values():
                if npc_id in campaign_histories:
                    history.extend(campaign_histories[npc_id])
            history = sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        # Convert to JSON-compatible format
        history_json = []
        for response in history:
            response_dict = asdict(response)
            response_dict['behavior_modifiers'] = asdict(response.behavior_modifiers)
            history_json.append(response_dict)
        
        return history_json
    
    def set_npc_personality(
        self,
        npc_id: str,
        personality_traits: Dict[str, Any],
        campaign_id: Optional[str] = None
    ):
        """
        Set personality traits for an NPC.
        
        Args:
            npc_id: NPC identifier
            personality_traits: Dictionary of personality traits
            campaign_id: Optional campaign identifier
        """
        key = f"{campaign_id}_{npc_id}" if campaign_id else npc_id
        self.npc_personalities[key] = personality_traits
        
        logger.info(f"Set personality for {npc_id}: {list(personality_traits.keys())}")

# Global instance for easy access
npc_behavior_engine = NPCBehaviorEngine() 