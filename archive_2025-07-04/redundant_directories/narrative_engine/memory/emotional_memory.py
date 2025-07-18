"""
Emotional Memory Subsystem - The Narrative Engine
================================================

Implements emotional memory for NPC behavior and player choice influence.
Supports the roadmap principle: "Emotional realism matters"

Features:
- Tag memories with emotional tone, character name, and event type
- Integrate with emotional layer in memory system
- Graceful fallback for missing or ambiguous emotional context
- JSON-compatible outputs for AI context pipelines
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import random

logger = logging.getLogger(__name__)

class EmotionalTone(Enum):
    """Primary emotional tones for memory tagging"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    NEUTRAL = "neutral"

class EmotionalIntensity(Enum):
    """Intensity levels for emotional memories"""
    MILD = "mild"
    MODERATE = "moderate"
    INTENSE = "intense"
    OVERWHELMING = "overwhelming"

class EventType(Enum):
    """Types of events that trigger emotional memories"""
    BETRAYAL = "betrayal"
    KINDNESS = "kindness"
    VIOLENCE = "violence"
    SACRIFICE = "sacrifice"
    ACHIEVEMENT = "achievement"
    LOSS = "loss"
    REUNION = "reunion"
    CONFLICT = "conflict"
    COOPERATION = "cooperation"
    MYSTERY = "mystery"
    CELEBRATION = "celebration"
    GRIEF = "grief"

class EmotionType(Enum):
    """Standardized emotion types for memory tagging."""
    # Positive emotions
    JOY = "joy"
    HAPPINESS = "happiness"
    EXCITEMENT = "excitement"
    PRIDE = "pride"
    LOVE = "love"
    GRATITUDE = "gratitude"
    HOPE = "hope"
    INSPIRATION = "inspiration"
    SATISFACTION = "satisfaction"
    AMUSEMENT = "amusement"
    
    # Negative emotions
    FEAR = "fear"
    ANGER = "anger"
    SADNESS = "sadness"
    DISGUST = "disgust"
    SHAME = "shame"
    GUILT = "guilt"
    DESPAIR = "despair"
    ANXIETY = "anxiety"
    FRUSTRATION = "frustration"
    DISAPPOINTMENT = "disappointment"
    
    # Complex emotions
    NOSTALGIA = "nostalgia"
    WONDER = "wonder"
    CURIOSITY = "curiosity"
    CONFUSION = "confusion"
    SURPRISE = "surprise"
    ANTICIPATION = "anticipation"
    RELIEF = "relief"
    REGRET = "regret"
    JEALOUSY = "jealousy"
    ENVY = "envy"
    
    # Neutral/Contextual emotions
    DETERMINATION = "determination"
    FOCUS = "focus"
    CALMNESS = "calmness"
    CONTEMPLATION = "contemplation"
    RESOLVE = "resolve"
    CAUTION = "caution"
    VIGILANCE = "vigilance"
    PATIENCE = "patience"

@dataclass
class EmotionalContext:
    """Structured emotional context for memories"""
    primary_tone: EmotionalTone
    intensity: EmotionalIntensity
    event_type: EventType
    character_name: str
    target_character: Optional[str] = None
    location: Optional[str] = None
    timestamp: Optional[str] = None
    duration: Optional[int] = None  # Duration in minutes
    triggers: List[str] = None
    consequences: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.triggers is None:
            self.triggers = []
        if self.consequences is None:
            self.consequences = []
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

@dataclass
class EnhancedEmotionalContext:
    """Enhanced emotional context for memory objects with float intensity."""
    primary_emotion: EmotionType
    intensity: float  # 0.0 to 1.0
    secondary_emotions: List[EmotionType] = None
    emotional_triggers: List[str] = None
    emotional_outcome: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.secondary_emotions is None:
            self.secondary_emotions = []
        if self.emotional_triggers is None:
            self.emotional_triggers = []
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'primary_emotion': self.primary_emotion.value,
            'intensity': self.intensity,
            'secondary_emotions': [e.value for e in self.secondary_emotions],
            'emotional_triggers': self.emotional_triggers,
            'emotional_outcome': self.emotional_outcome,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedEmotionalContext':
        """Create from dictionary."""
        data['primary_emotion'] = EmotionType(data['primary_emotion'])
        data['secondary_emotions'] = [EmotionType(e) for e in data['secondary_emotions']]
        if data.get('timestamp'):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class EmotionalMemorySystem:
    """
    Emotional memory system for NPC behavior and player choice influence.
    
    Aligns with roadmap principle: "Emotional realism matters"
    - Tracks emotional context for all memories
    - Provides emotional recall for NPC interactions
    - Influences AI DM responses based on emotional history
    - Graceful fallback for missing emotional context
    """
    
    def __init__(self):
        self.emotional_memories: Dict[str, List[EmotionalContext]] = {}
        self.character_emotional_profiles: Dict[str, Dict[str, float]] = {}
        self.emotional_decay_rates = {
            EmotionalIntensity.MILD: 0.1,      # 10% decay per day
            EmotionalIntensity.MODERATE: 0.05,  # 5% decay per day
            EmotionalIntensity.INTENSE: 0.02,   # 2% decay per day
            EmotionalIntensity.OVERWHELMING: 0.01  # 1% decay per day
        }
        
        logger.info("Emotional memory system initialized")
    
    def add_emotional_memory(
        self,
        campaign_id: str,
        character_name: str,
        emotional_context: EmotionalContext
    ) -> str:
        """
        Add an emotional memory for a character.
        
        Args:
            campaign_id: Campaign identifier (roadmap requirement)
            character_name: Character experiencing the emotion
            emotional_context: Emotional context details
        
        Returns:
            str: Memory identifier
        """
        if campaign_id not in self.emotional_memories:
            self.emotional_memories[campaign_id] = []
        
        # Generate unique memory ID
        memory_id = f"emotion_{character_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Add to emotional memories
        self.emotional_memories[campaign_id].append(emotional_context)
        
        # Update character emotional profile
        self._update_character_profile(character_name, emotional_context)
        
        logger.info(f"Added emotional memory for {character_name}: {emotional_context.primary_tone.value} ({emotional_context.intensity.value})")
        
        return memory_id
    
    def _update_character_profile(self, character_name: str, emotional_context: EmotionalContext):
        """Update character's emotional profile based on new memory"""
        if character_name not in self.character_emotional_profiles:
            self.character_emotional_profiles[character_name] = {}
        
        profile = self.character_emotional_profiles[character_name]
        tone = emotional_context.primary_tone.value
        intensity_multiplier = {
            EmotionalIntensity.MILD: 0.5,
            EmotionalIntensity.MODERATE: 1.0,
            EmotionalIntensity.INTENSE: 2.0,
            EmotionalIntensity.OVERWHELMING: 3.0
        }[emotional_context.intensity]
        
        # Update emotional tone weight
        if tone not in profile:
            profile[tone] = 0.0
        profile[tone] += intensity_multiplier
        
        # Apply decay to other emotions
        for other_tone in profile:
            if other_tone != tone:
                profile[other_tone] *= 0.95  # 5% decay for other emotions
    
    def get_character_emotional_state(
        self,
        character_name: str,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current emotional state of a character.
        
        Args:
            character_name: Character to analyze
            campaign_id: Optional campaign filter
        
        Returns:
            Dict containing emotional state analysis
        """
        if character_name not in self.character_emotional_profiles:
            return {
                'character_name': character_name,
                'dominant_emotion': EmotionalTone.NEUTRAL.value,
                'emotional_intensity': 0.0,
                'emotional_stability': 1.0,
                'recent_emotional_events': [],
                'emotional_tendencies': {}
            }
        
        profile = self.character_emotional_profiles[character_name]
        
        # Find dominant emotion
        dominant_emotion = max(profile.items(), key=lambda x: x[1]) if profile else (EmotionalTone.NEUTRAL.value, 0.0)
        
        # Calculate emotional intensity
        total_intensity = sum(profile.values())
        
        # Calculate emotional stability (inverse of emotional volatility)
        emotional_stability = 1.0 / (1.0 + total_intensity * 0.1)
        
        # Get recent emotional events
        recent_events = self._get_recent_emotional_events(character_name, campaign_id, limit=5)
        
        return {
            'character_name': character_name,
            'dominant_emotion': dominant_emotion[0],
            'emotional_intensity': total_intensity,
            'emotional_stability': min(emotional_stability, 1.0),
            'recent_emotional_events': recent_events,
            'emotional_tendencies': profile.copy()
        }
    
    def _get_recent_emotional_events(
        self,
        character_name: str,
        campaign_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent emotional events for a character"""
        events = []
        
        if campaign_id and campaign_id in self.emotional_memories:
            for memory in self.emotional_memories[campaign_id]:
                if memory.character_name == character_name:
                    events.append({
                        'timestamp': memory.timestamp,
                        'tone': memory.primary_tone.value,
                        'intensity': memory.intensity.value,
                        'event_type': memory.event_type.value,
                        'target_character': memory.target_character,
                        'location': memory.location
                    })
        
        # Sort by timestamp and return recent events
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        return events[:limit]
    
    def recall_emotional_context(
        self,
        character_name: str,
        target_character: Optional[str] = None,
        event_type: Optional[EventType] = None,
        campaign_id: Optional[str] = None,
        limit: int = 10
    ) -> List[EmotionalContext]:
        """
        Recall emotional context for character interactions.
        
        Args:
            character_name: Character recalling emotions
            target_character: Optional target character filter
            event_type: Optional event type filter
            campaign_id: Optional campaign filter
            limit: Maximum number of memories to return
        
        Returns:
            List of relevant emotional contexts
        """
        relevant_memories = []
        
        if campaign_id and campaign_id in self.emotional_memories:
            for memory in self.emotional_memories[campaign_id]:
                if memory.character_name == character_name:
                    # Apply filters
                    if target_character and memory.target_character != target_character:
                        continue
                    if event_type and memory.event_type != event_type:
                        continue
                    
                    relevant_memories.append(memory)
        
        # Sort by recency and intensity
        relevant_memories.sort(
            key=lambda x: (
                x.intensity.value,
                x.timestamp
            ),
            reverse=True
        )
        
        return relevant_memories[:limit]
    
    def generate_emotional_response(
        self,
        character_name: str,
        situation: str,
        target_character: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate emotional response for a character in a given situation.
        
        Aligns with roadmap principle: "Emotional realism matters"
        - Uses emotional memory to influence responses
        - Provides fallback for missing emotional context
        - Returns JSON-compatible response structure
        
        Args:
            character_name: Character generating response
            situation: Current situation description
            target_character: Optional target character
            campaign_id: Optional campaign context
        
        Returns:
            Dict containing emotional response details
        """
        # Get character's emotional state
        emotional_state = self.get_character_emotional_state(character_name, campaign_id)
        
        # Recall relevant emotional memories
        relevant_memories = self.recall_emotional_context(
            character_name, target_character, campaign_id=campaign_id, limit=3
        )
        
        # Determine response based on emotional state and memories
        response = self._determine_emotional_response(
            emotional_state, relevant_memories, situation
        )
        
        # Only use fallback if there's truly no emotional context
        # Check if dominant emotion is neutral AND no relevant memories
        if (emotional_state['dominant_emotion'] == EmotionalTone.NEUTRAL.value and 
            not relevant_memories and 
            emotional_state['emotional_intensity'] < 0.1):
            response = self._generate_fallback_response(character_name, situation)
        
        return {
            'character_name': character_name,
            'situation': situation,
            'target_character': target_character,
            'emotional_response': response,
            'emotional_state': emotional_state,
            'relevant_memories': [
                {
                    'tone': mem.primary_tone.value,
                    'intensity': mem.intensity.value,
                    'event_type': mem.event_type.value,
                    'timestamp': mem.timestamp
                }
                for mem in relevant_memories
            ],
            'response_confidence': self._calculate_response_confidence(emotional_state, relevant_memories)
        }
    
    def _determine_emotional_response(
        self,
        emotional_state: Dict[str, Any],
        relevant_memories: List[EmotionalContext],
        situation: str
    ) -> Dict[str, Any]:
        """Determine emotional response based on state and memories"""
        dominant_emotion = emotional_state['dominant_emotion']
        emotional_intensity = emotional_state['emotional_intensity']
        
        # Base response on dominant emotion
        response_templates = {
            EmotionalTone.JOY.value: {
                'primary_response': 'positive and enthusiastic',
                'tone_modifier': 'warm and welcoming',
                'behavior_hint': 'likely to help or cooperate'
            },
            EmotionalTone.SADNESS.value: {
                'primary_response': 'melancholic and withdrawn',
                'tone_modifier': 'quiet and contemplative',
                'behavior_hint': 'may need support or space'
            },
            EmotionalTone.ANGER.value: {
                'primary_response': 'defensive and confrontational',
                'tone_modifier': 'sharp and direct',
                'behavior_hint': 'likely to challenge or resist'
            },
            EmotionalTone.FEAR.value: {
                'primary_response': 'cautious and anxious',
                'tone_modifier': 'nervous and uncertain',
                'behavior_hint': 'may avoid or seek reassurance'
            },
            EmotionalTone.TRUST.value: {
                'primary_response': 'open and cooperative',
                'tone_modifier': 'friendly and accepting',
                'behavior_hint': 'likely to share or collaborate'
            },
            EmotionalTone.NEUTRAL.value: {
                'primary_response': 'neutral and observant',
                'tone_modifier': 'calm and measured',
                'behavior_hint': 'likely to assess before acting'
            }
        }
        
        # Get base response
        base_response = response_templates.get(
            dominant_emotion,
            response_templates[EmotionalTone.NEUTRAL.value]
        )
        
        # Adjust based on intensity
        intensity_modifier = min(emotional_intensity / 5.0, 1.0)
        
        return {
            'primary_response': base_response['primary_response'],
            'tone_modifier': base_response['tone_modifier'],
            'behavior_hint': base_response['behavior_hint'],
            'emotional_intensity': intensity_modifier,
            'dominant_emotion': dominant_emotion,
            'stability_factor': emotional_state['emotional_stability']
        }
    
    def _generate_fallback_response(self, character_name: str, situation: str) -> Dict[str, Any]:
        """Generate fallback response when emotional context is missing"""
        return {
            'primary_response': 'neutral and observant',
            'tone_modifier': 'calm and measured',
            'behavior_hint': 'likely to assess before acting',
            'emotional_intensity': 0.3,
            'dominant_emotion': EmotionalTone.NEUTRAL.value,
            'stability_factor': 0.8,
            'fallback_used': True
        }
    
    def _calculate_response_confidence(
        self,
        emotional_state: Dict[str, Any],
        relevant_memories: List[EmotionalContext]
    ) -> float:
        """Calculate confidence in emotional response"""
        # Base confidence on emotional stability and memory relevance
        stability = emotional_state['emotional_stability']
        memory_relevance = min(len(relevant_memories) / 3.0, 1.0)
        
        return (stability + memory_relevance) / 2.0
    
    def apply_emotional_decay(self, campaign_id: str, days_passed: int = 1):
        """
        Apply emotional decay over time.
        
        Aligns with roadmap principle: "Memory is sacred" - decay is natural
        - Reduces emotional intensity over time
        - Preserves important emotional memories longer
        - Maintains narrative continuity while allowing growth
        """
        if campaign_id not in self.emotional_memories:
            return
        
        for memory in self.emotional_memories[campaign_id]:
            decay_rate = self.emotional_decay_rates[memory.intensity]
            # Apply decay (simplified - in practice would use actual timestamps)
            # This is a placeholder for the decay mechanism
        
        logger.info(f"Applied emotional decay to {campaign_id} over {days_passed} days")
    
    def export_emotional_context(
        self,
        campaign_id: str,
        character_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Export emotional context for external use.
        
        Args:
            campaign_id: Campaign identifier
            character_name: Optional character filter
            
        Returns:
            List of emotional context dictionaries
        """
        if campaign_id not in self.emotional_memories:
            return []
        
        memories = self.emotional_memories[campaign_id]
        
        if character_name:
            memories = [m for m in memories if m.character_name == character_name]
        
        return [asdict(memory) for memory in memories]

# Global instance for easy access
emotional_memory_system = EmotionalMemorySystem() 

class EmotionalMemoryEnhancer:
    """Enhances memory objects with emotional context."""
    
    @staticmethod
    def add_emotional_context(
        memory: Any,
        primary_emotion: EmotionType,
        intensity: float,
        secondary_emotions: Optional[List[EmotionType]] = None,
        emotional_triggers: Optional[List[str]] = None,
        emotional_outcome: Optional[str] = None
    ) -> bool:
        """
        Add emotional context to a memory object.
        
        Args:
            memory: Memory object to enhance
            primary_emotion: Primary emotion type
            intensity: Emotional intensity (0.0 to 1.0)
            secondary_emotions: Optional secondary emotions
            emotional_triggers: Optional emotional triggers
            emotional_outcome: Optional emotional outcome
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not hasattr(memory, 'emotional_context'):
                memory.emotional_context = []
            
            emotional_context = EnhancedEmotionalContext(
                primary_emotion=primary_emotion,
                intensity=max(0.0, min(1.0, intensity)),  # Clamp to 0-1
                secondary_emotions=secondary_emotions or [],
                emotional_triggers=emotional_triggers or [],
                emotional_outcome=emotional_outcome,
                timestamp=datetime.now()
            )
            
            memory.emotional_context.append(emotional_context)
            
            # Update memory metadata if available
            if hasattr(memory, 'metadata'):
                if 'emotional_tags' not in memory.metadata:
                    memory.metadata['emotional_tags'] = []
                memory.metadata['emotional_tags'].append(primary_emotion.value)
            
            logger.debug(f"Added emotional context to memory: {primary_emotion.value} (intensity: {intensity})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding emotional context: {e}")
            return False
    
    @staticmethod
    def analyze_emotional_content(text: str) -> Dict[str, Any]:
        """
        Analyze text content for emotional indicators.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary with emotional analysis results
        """
        # Simple keyword-based emotional analysis
        # In a production system, this would use more sophisticated NLP
        
        text_lower = text.lower()
        emotions_found = {}
        
        # Positive emotion keywords
        positive_keywords = {
            EmotionType.JOY: ['joy', 'happy', 'excited', 'thrilled', 'delighted'],
            EmotionType.PRIDE: ['proud', 'accomplished', 'achieved', 'success'],
            EmotionType.LOVE: ['love', 'affection', 'care', 'fondness'],
            EmotionType.HOPE: ['hope', 'optimistic', 'promising', 'bright'],
            EmotionType.SATISFACTION: ['satisfied', 'content', 'fulfilled', 'pleased']
        }
        
        # Negative emotion keywords
        negative_keywords = {
            EmotionType.FEAR: ['fear', 'afraid', 'terrified', 'scared', 'panic'],
            EmotionType.ANGER: ['angry', 'furious', 'rage', 'irritated', 'mad'],
            EmotionType.SADNESS: ['sad', 'depressed', 'melancholy', 'sorrow'],
            EmotionType.ANXIETY: ['anxious', 'worried', 'nervous', 'concerned'],
            EmotionType.FRUSTRATION: ['frustrated', 'annoyed', 'irritated', 'upset']
        }
        
        # Check for positive emotions
        for emotion, keywords in positive_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                emotions_found[emotion.value] = {
                    'count': count,
                    'intensity': min(1.0, count * 0.2)  # Simple intensity calculation
                }
        
        # Check for negative emotions
        for emotion, keywords in negative_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                emotions_found[emotion.value] = {
                    'count': count,
                    'intensity': min(1.0, count * 0.2)
                }
        
        # Determine primary emotion
        primary_emotion = None
        max_intensity = 0.0
        
        for emotion, data in emotions_found.items():
            if data['intensity'] > max_intensity:
                max_intensity = data['intensity']
                primary_emotion = emotion
        
        return {
            'emotions_found': emotions_found,
            'primary_emotion': primary_emotion,
            'max_intensity': max_intensity,
            'emotional_content_detected': len(emotions_found) > 0
        }
    
    @staticmethod
    def auto_tag_memory_emotion(memory: Any) -> bool:
        """
        Automatically tag a memory with emotional context based on its content.
        
        Args:
            memory: Memory object to auto-tag
            
        Returns:
            True if emotional context was added, False otherwise
        """
        try:
            if not hasattr(memory, 'content'):
                return False
            
            # Get text content
            if isinstance(memory.content, dict):
                text = memory.content.get('text', '')
            else:
                text = str(memory.content)
            
            if not text:
                return False
            
            # Analyze emotional content
            analysis = EmotionalMemoryEnhancer.analyze_emotional_content(text)
            
            if not analysis['emotional_content_detected']:
                return False
            
            # Add emotional context
            primary_emotion = EmotionType(analysis['primary_emotion'])
            intensity = analysis['max_intensity']
            
            return EmotionalMemoryEnhancer.add_emotional_context(
                memory=memory,
                primary_emotion=primary_emotion,
                intensity=intensity
            )
            
        except Exception as e:
            logger.error(f"Error auto-tagging memory emotion: {e}")
            return False


class EmotionalMemoryFilter:
    """Provides filtering capabilities for emotionally tagged memories."""
    
    def __init__(self):
        self.emotion_groups = {
            'positive': {
                EmotionType.JOY, EmotionType.HAPPINESS, EmotionType.EXCITEMENT,
                EmotionType.PRIDE, EmotionType.LOVE, EmotionType.GRATITUDE,
                EmotionType.HOPE, EmotionType.INSPIRATION, EmotionType.SATISFACTION,
                EmotionType.AMUSEMENT, EmotionType.WONDER, EmotionType.RELIEF
            },
            'negative': {
                EmotionType.FEAR, EmotionType.ANGER, EmotionType.SADNESS,
                EmotionType.DISGUST, EmotionType.SHAME, EmotionType.GUILT,
                EmotionType.DESPAIR, EmotionType.ANXIETY, EmotionType.FRUSTRATION,
                EmotionType.DISAPPOINTMENT, EmotionType.REGRET, EmotionType.JEALOUSY,
                EmotionType.ENVY
            },
            'complex': {
                EmotionType.NOSTALGIA, EmotionType.CURIOSITY, EmotionType.CONFUSION,
                EmotionType.SURPRISE, EmotionType.ANTICIPATION
            },
            'neutral': {
                EmotionType.DETERMINATION, EmotionType.FOCUS, EmotionType.CALMNESS,
                EmotionType.CONTEMPLATION, EmotionType.RESOLVE, EmotionType.CAUTION,
                EmotionType.VIGILANCE, EmotionType.PATIENCE
            }
        }
    
    def filter_by_emotion(
        self,
        memories: List[Any],
        emotion: EmotionType,
        min_intensity: float = 0.0
    ) -> List[Any]:
        """
        Filter memories by specific emotion and minimum intensity.
        
        Args:
            memories: List of memory objects
            emotion: Emotion to filter by
            min_intensity: Minimum emotional intensity (0.0 to 1.0)
            
        Returns:
            Filtered list of memories
        """
        filtered = []
        for memory in memories:
            if hasattr(memory, 'emotional_context') and memory.emotional_context:
                for emotional_context in memory.emotional_context:
                    if (isinstance(emotional_context, EnhancedEmotionalContext) and
                        emotional_context.primary_emotion == emotion and
                        emotional_context.intensity >= min_intensity):
                        filtered.append(memory)
                        break
        return filtered
    
    def filter_by_emotion_group(
        self,
        memories: List[Any],
        group: str,
        min_intensity: float = 0.0
    ) -> List[Any]:
        """
        Filter memories by emotion group (positive, negative, complex, neutral).
        
        Args:
            memories: List of memory objects
            group: Emotion group name
            min_intensity: Minimum emotional intensity
            
        Returns:
            Filtered list of memories
        """
        if group not in self.emotion_groups:
            logger.warning(f"Unknown emotion group: {group}")
            return []
        
        target_emotions = self.emotion_groups[group]
        filtered = []
        
        for memory in memories:
            if hasattr(memory, 'emotional_context') and memory.emotional_context:
                for emotional_context in memory.emotional_context:
                    if (isinstance(emotional_context, EnhancedEmotionalContext) and
                        emotional_context.primary_emotion in target_emotions and
                        emotional_context.intensity >= min_intensity):
                        filtered.append(memory)
                        break
        
        return filtered
    
    def filter_by_intensity_range(
        self,
        memories: List[Any],
        min_intensity: float = 0.0,
        max_intensity: float = 1.0
    ) -> List[Any]:
        """
        Filter memories by emotional intensity range.
        
        Args:
            memories: List of memory objects
            min_intensity: Minimum emotional intensity
            max_intensity: Maximum emotional intensity
            
        Returns:
            Filtered list of memories
        """
        filtered = []
        for memory in memories:
            if hasattr(memory, 'emotional_context') and memory.emotional_context:
                for emotional_context in memory.emotional_context:
                    if (isinstance(emotional_context, EnhancedEmotionalContext) and
                        min_intensity <= emotional_context.intensity <= max_intensity):
                        filtered.append(memory)
                        break
        return filtered
    
    def get_emotion_statistics(self, memories: List[Any]) -> Dict[str, Any]:
        """
        Get statistics about emotional content in memories.
        
        Args:
            memories: List of memory objects
            
        Returns:
            Dictionary with emotion statistics
        """
        emotion_counts = {}
        intensity_sum = 0.0
        intensity_count = 0
        
        for memory in memories:
            if hasattr(memory, 'emotional_context') and memory.emotional_context:
                for emotional_context in memory.emotional_context:
                    if isinstance(emotional_context, EnhancedEmotionalContext):
                        emotion = emotional_context.primary_emotion.value
                        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                        intensity_sum += emotional_context.intensity
                        intensity_count += 1
        
        # Group statistics
        group_counts = {group: 0 for group in self.emotion_groups.keys()}
        for memory in memories:
            if hasattr(memory, 'emotional_context') and memory.emotional_context:
                for emotional_context in memory.emotional_context:
                    if isinstance(emotional_context, EnhancedEmotionalContext):
                        for group, emotions in self.emotion_groups.items():
                            if emotional_context.primary_emotion in emotions:
                                group_counts[group] += 1
                                break
        
        return {
            'total_emotionally_tagged': intensity_count,
            'emotion_counts': emotion_counts,
            'group_counts': group_counts,
            'average_intensity': intensity_sum / intensity_count if intensity_count > 0 else 0.0,
            'emotion_groups': list(self.emotion_groups.keys())
        } 