"""
The Narrative Engine - Core Architecture
=======================================

A story-centric framework for narrative intelligence, not just game mechanics.
Built on the principle that narratives are data structures encoding intentions,
conflicts, contextual memory, world-state, character arcs, and consequences.
"""

import json
import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Types of narrative memory"""
    EVENT = "event"
    CHARACTER_ARC = "character_arc"
    THEME = "theme"
    CONFLICT = "conflict"
    DECISION = "decision"
    CONSEQUENCE = "consequence"
    WORLD_STATE = "world_state"

class NarrativeRole(Enum):
    """Narrative function roles"""
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    GUIDE = "guide"
    BETRAYER = "betrayer"
    REDEEMER = "redeemer"
    WITNESS = "witness"
    CATALYST = "catalyst"

class MemorySlot:
    """A slot in the narrative memory system"""
    
    def __init__(self, memory_type: MemoryType, content: Dict[str, Any], 
                 timestamp: datetime.datetime = None, emotional_weight: float = 1.0,
                 thematic_tags: List[str] = None):
        self.memory_type = memory_type
        self.content = content
        self.timestamp = timestamp or datetime.datetime.utcnow()
        self.emotional_weight = emotional_weight  # 0.0 to 1.0
        self.thematic_tags = thematic_tags or []
        self.associations = []  # Links to other memories
        self.decay_rate = 0.1  # How quickly this memory fades
        self.reinforcement_count = 0
    
    def reinforce(self):
        """Reinforce this memory, making it less likely to decay"""
        self.reinforcement_count += 1
        self.decay_rate = max(0.01, self.decay_rate * 0.9)
    
    def get_significance(self) -> float:
        """Calculate current significance based on weight, age, and reinforcement"""
        age_hours = (datetime.datetime.utcnow() - self.timestamp).total_seconds() / 3600
        decay_factor = max(0.1, 1.0 - (age_hours * self.decay_rate))
        reinforcement_bonus = min(0.5, self.reinforcement_count * 0.1)
        return (self.emotional_weight * decay_factor) + reinforcement_bonus
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'memory_type': self.memory_type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'emotional_weight': self.emotional_weight,
            'thematic_tags': self.thematic_tags,
            'associations': self.associations,
            'decay_rate': self.decay_rate,
            'reinforcement_count': self.reinforcement_count,
            'significance': self.get_significance()
        }

class MemoryCore:
    """Module 1: Persistent structured memory system"""
    
    def __init__(self):
        self.memories: List[MemorySlot] = []
        self.character_memories: Dict[str, List[MemorySlot]] = defaultdict(list)
        self.thematic_index: Dict[str, List[MemorySlot]] = defaultdict(list)
        self.temporal_index: Dict[str, List[MemorySlot]] = defaultdict(list)
    
    def add_memory(self, memory: MemorySlot, character_id: str = None):
        """Add a memory to the core system"""
        self.memories.append(memory)
        
        # Index by character
        if character_id:
            self.character_memories[character_id].append(memory)
        
        # Index by thematic tags
        for tag in memory.thematic_tags:
            self.thematic_index[tag].append(memory)
        
        # Index by temporal period (day, week, month)
        day_key = memory.timestamp.strftime('%Y-%m-%d')
        self.temporal_index[day_key].append(memory)
        
        logger.info(f"Added {memory.memory_type.value} memory with significance {memory.get_significance():.2f}")
    
    def search_memories(self, query: str = None, memory_type: MemoryType = None, 
                       character_id: str = None, thematic_tags: List[str] = None,
                       min_significance: float = 0.0) -> List[MemorySlot]:
        """Search memories based on various criteria"""
        results = []
        
        for memory in self.memories:
            # Filter by significance
            if memory.get_significance() < min_significance:
                continue
            
            # Filter by type
            if memory_type and memory.memory_type != memory_type:
                continue
            
            # Filter by character
            if character_id and memory not in self.character_memories[character_id]:
                continue
            
            # Filter by thematic tags
            if thematic_tags and not any(tag in memory.thematic_tags for tag in thematic_tags):
                continue
            
            # Text search in content
            if query:
                content_str = json.dumps(memory.content).lower()
                if query.lower() not in content_str:
                    continue
            
            results.append(memory)
        
        # Sort by significance
        results.sort(key=lambda m: m.get_significance(), reverse=True)
        return results
    
    def get_evolving_themes(self) -> Dict[str, float]:
        """Identify evolving themes based on memory patterns"""
        theme_strengths = defaultdict(float)
        
        for memory in self.memories:
            for tag in memory.thematic_tags:
                theme_strengths[tag] += memory.get_significance()
        
        return dict(theme_strengths)
    
    def get_unresolved_tensions(self) -> List[Dict[str, Any]]:
        """Identify unresolved narrative tensions"""
        tensions = []
        
        # Look for conflicts without resolutions
        conflicts = self.search_memories(memory_type=MemoryType.CONFLICT)
        resolutions = self.search_memories(memory_type=MemoryType.CONSEQUENCE)
        
        for conflict in conflicts:
            # Check if this conflict has been resolved
            resolved = any(
                res.content.get('resolves_conflict_id') == conflict.content.get('conflict_id')
                for res in resolutions
            )
            
            if not resolved and conflict.get_significance() > 0.3:
                tensions.append({
                    'conflict': conflict.content,
                    'significance': conflict.get_significance(),
                    'age_hours': (datetime.datetime.utcnow() - conflict.timestamp).total_seconds() / 3600
                })
        
        return tensions

class NarrativeInterpreter:
    """Module 2: Natural language processing and narrative function detection"""
    
    def __init__(self, memory_core: MemoryCore):
        self.memory_core = memory_core
        self.narrative_functions = {
            'choice': self._detect_choice,
            'conflict': self._detect_conflict,
            'character_development': self._detect_character_development,
            'world_interaction': self._detect_world_interaction,
            'thematic_moment': self._detect_thematic_moment
        }
    
    def process_input(self, user_input: str, character_id: str = None) -> Dict[str, Any]:
        """Process user input and extract narrative functions"""
        result = {
            'raw_input': user_input,
            'narrative_functions': [],
            'detected_roles': [],
            'thematic_elements': [],
            'narrative_weight': 0.0
        }
        
        # Detect narrative functions
        for function_name, detector in self.narrative_functions.items():
            detection = detector(user_input, character_id)
            if detection:
                result['narrative_functions'].append(detection)
                result['narrative_weight'] += detection.get('weight', 0.0)
        
        # Detect narrative roles
        result['detected_roles'] = self._detect_narrative_roles(user_input)
        
        # Extract thematic elements
        result['thematic_elements'] = self._extract_themes(user_input)
        
        return result
    
    def _detect_choice(self, text: str, character_id: str) -> Optional[Dict[str, Any]]:
        """Detect if input represents a meaningful choice"""
        choice_indicators = ['choose', 'decide', 'pick', 'select', 'want to', 'try to', 'attempt']
        
        if any(indicator in text.lower() for indicator in choice_indicators):
            return {
                'type': 'choice',
                'weight': 0.8,
                'content': {'choice_text': text}
            }
        return None
    
    def _detect_conflict(self, text: str, character_id: str) -> Optional[Dict[str, Any]]:
        """Detect if input represents or creates conflict"""
        conflict_indicators = ['attack', 'fight', 'argue', 'disagree', 'resist', 'defy', 'challenge']
        
        if any(indicator in text.lower() for indicator in conflict_indicators):
            return {
                'type': 'conflict',
                'weight': 0.9,
                'content': {'conflict_text': text}
            }
        return None
    
    def _detect_character_development(self, text: str, character_id: str) -> Optional[Dict[str, Any]]:
        """Detect character development moments"""
        development_indicators = ['learn', 'grow', 'change', 'realize', 'understand', 'feel']
        
        if any(indicator in text.lower() for indicator in development_indicators):
            return {
                'type': 'character_development',
                'weight': 0.7,
                'content': {'development_text': text}
            }
        return None
    
    def _detect_world_interaction(self, text: str, character_id: str) -> Optional[Dict[str, Any]]:
        """Detect world interaction"""
        world_indicators = ['go to', 'visit', 'explore', 'search', 'examine', 'open', 'use']
        
        if any(indicator in text.lower() for indicator in world_indicators):
            return {
                'type': 'world_interaction',
                'weight': 0.5,
                'content': {'interaction_text': text}
            }
        return None
    
    def _detect_thematic_moment(self, text: str, character_id: str) -> Optional[Dict[str, Any]]:
        """Detect thematically significant moments"""
        # Check against evolving themes
        themes = self.memory_core.get_evolving_themes()
        text_lower = text.lower()
        
        for theme, strength in themes.items():
            if theme.lower() in text_lower and strength > 0.5:
                return {
                    'type': 'thematic_moment',
                    'weight': min(1.0, strength),
                    'content': {'theme': theme, 'thematic_text': text}
                }
        return None
    
    def _detect_narrative_roles(self, text: str) -> List[str]:
        """Detect narrative roles in the input"""
        roles = []
        text_lower = text.lower()
        
        role_indicators = {
            'protagonist': ['i', 'my', 'me', 'myself'],
            'antagonist': ['enemy', 'opponent', 'villain', 'threat'],
            'guide': ['help', 'teach', 'show', 'guide'],
            'witness': ['see', 'observe', 'watch', 'notice']
        }
        
        for role, indicators in role_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                roles.append(role)
        
        return roles
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract thematic elements from text"""
        themes = []
        text_lower = text.lower()
        
        # Simple theme detection - could be enhanced with NLP
        theme_keywords = {
            'justice': ['justice', 'fair', 'unfair', 'right', 'wrong'],
            'redemption': ['redemption', 'forgive', 'second chance', 'change'],
            'power': ['power', 'control', 'authority', 'strength'],
            'love': ['love', 'care', 'protect', 'relationship'],
            'fear': ['fear', 'afraid', 'scared', 'terrified'],
            'hope': ['hope', 'dream', 'believe', 'future']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes

class WorldStateSimulator:
    """Module 3: World logic simulation engine"""
    
    def __init__(self):
        self.world_state = {
            'political_systems': {},
            'economies': {},
            'geography': {},
            'social_relations': {},
            'current_events': []
        }
        self.simulation_rules = {}
        self.causality_chains = []
    
    def update_world_state(self, action: Dict[str, Any], consequences: List[Dict[str, Any]]):
        """Update world state based on actions and consequences"""
        # Apply immediate consequences
        for consequence in consequences:
            self._apply_consequence(consequence)
        
        # Trigger causal chains
        self._trigger_causality_chains(action)
        
        # Update current events
        self.world_state['current_events'].append({
            'action': action,
            'consequences': consequences,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })
        
        # Keep only recent events
        if len(self.world_state['current_events']) > 50:
            self.world_state['current_events'] = self.world_state['current_events'][-50:]
    
    def _apply_consequence(self, consequence: Dict[str, Any]):
        """Apply a single consequence to world state"""
        consequence_type = consequence.get('type')
        
        if consequence_type == 'political_change':
            self._apply_political_change(consequence)
        elif consequence_type == 'economic_change':
            self._apply_economic_change(consequence)
        elif consequence_type == 'social_change':
            self._apply_social_change(consequence)
        elif consequence_type == 'geographic_change':
            self._apply_geographic_change(consequence)
    
    def _apply_political_change(self, consequence: Dict[str, Any]):
        """Apply political system changes"""
        target = consequence.get('target', 'default')
        if target not in self.world_state['political_systems']:
            self.world_state['political_systems'][target] = {}
        
        self.world_state['political_systems'][target].update(consequence.get('changes', {}))
    
    def _apply_economic_change(self, consequence: Dict[str, Any]):
        """Apply economic system changes"""
        target = consequence.get('target', 'default')
        if target not in self.world_state['economies']:
            self.world_state['economies'][target] = {}
        
        self.world_state['economies'][target].update(consequence.get('changes', {}))
    
    def _apply_social_change(self, consequence: Dict[str, Any]):
        """Apply social relation changes"""
        target = consequence.get('target', 'default')
        if target not in self.world_state['social_relations']:
            self.world_state['social_relations'][target] = {}
        
        self.world_state['social_relations'][target].update(consequence.get('changes', {}))
    
    def _apply_geographic_change(self, consequence: Dict[str, Any]):
        """Apply geographic changes"""
        target = consequence.get('target', 'default')
        if target not in self.world_state['geography']:
            self.world_state['geography'][target] = {}
        
        self.world_state['geography'][target].update(consequence.get('changes', {}))
    
    def _trigger_causality_chains(self, action: Dict[str, Any]):
        """Trigger causal chains based on actions"""
        # This would implement complex causality logic
        # For now, a simple implementation
        pass
    
    def get_world_context(self) -> Dict[str, Any]:
        """Get current world context for narrative generation"""
        return {
            'current_state': self.world_state,
            'active_events': self.world_state['current_events'][-10:],  # Last 10 events
            'political_climate': self._summarize_political_climate(),
            'economic_conditions': self._summarize_economic_conditions(),
            'social_tensions': self._summarize_social_tensions()
        }
    
    def _summarize_political_climate(self) -> str:
        """Summarize current political climate"""
        if not self.world_state['political_systems']:
            return "Political systems are stable and established."
        
        # Simple summary - could be much more sophisticated
        return f"Political landscape involves {len(self.world_state['political_systems'])} major systems."
    
    def _summarize_economic_conditions(self) -> str:
        """Summarize current economic conditions"""
        if not self.world_state['economies']:
            return "Economic conditions are stable."
        
        return f"Economic activity spans {len(self.world_state['economies'])} regions."
    
    def _summarize_social_tensions(self) -> str:
        """Summarize current social tensions"""
        if not self.world_state['social_relations']:
            return "Social relations are harmonious."
        
        return f"Social dynamics involve {len(self.world_state['social_relations'])} key relationships."

class AIActor:
    """Individual AI actor with beliefs, goals, and adaptive memory"""
    
    def __init__(self, actor_id: str, name: str, role: NarrativeRole, 
                 beliefs: Dict[str, Any], goals: List[str]):
        self.actor_id = actor_id
        self.name = name
        self.role = role
        self.beliefs = beliefs
        self.goals = goals
        self.memory = []  # Personal memory
        self.motivations = self._derive_motivations()
        self.relationships = {}
    
    def _derive_motivations(self) -> List[str]:
        """Derive motivations from beliefs and goals"""
        motivations = []
        
        # Convert goals to motivations
        for goal in self.goals:
            motivations.append(f"achieve_{goal}")
        
        # Add role-based motivations
        if self.role == NarrativeRole.PROTAGONIST:
            motivations.extend(['grow', 'overcome_challenges', 'find_meaning'])
        elif self.role == NarrativeRole.ANTAGONIST:
            motivations.extend(['maintain_control', 'prevent_change', 'assert_dominance'])
        elif self.role == NarrativeRole.GUIDE:
            motivations.extend(['help_others', 'share_wisdom', 'facilitate_growth'])
        
        return motivations
    
    def update_beliefs(self, new_information: Dict[str, Any]):
        """Update beliefs based on new information"""
        for key, value in new_information.items():
            if key in self.beliefs:
                # Beliefs can change but with resistance
                self.beliefs[key] = self._blend_beliefs(self.beliefs[key], value)
            else:
                self.beliefs[key] = value
    
    def _blend_beliefs(self, old_belief: Any, new_belief: Any) -> Any:
        """Blend old and new beliefs (simplified)"""
        # Simple blending - could be much more sophisticated
        if isinstance(old_belief, (int, float)) and isinstance(new_belief, (int, float)):
            return (old_belief * 0.7) + (new_belief * 0.3)
        return new_belief
    
    def get_response(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actor response to a situation"""
        response = {
            'actor_id': self.actor_id,
            'name': self.name,
            'role': self.role.value,
            'response_type': self._determine_response_type(situation),
            'motivation': self._select_primary_motivation(situation),
            'action': self._generate_action(situation)
        }
        
        return response
    
    def _determine_response_type(self, situation: Dict[str, Any]) -> str:
        """Determine type of response based on situation and role"""
        if self.role == NarrativeRole.PROTAGONIST:
            return 'proactive'
        elif self.role == NarrativeRole.ANTAGONIST:
            return 'oppositional'
        elif self.role == NarrativeRole.GUIDE:
            return 'supportive'
        else:
            return 'reactive'
    
    def _select_primary_motivation(self, situation: Dict[str, Any]) -> str:
        """Select primary motivation for this situation"""
        # Simple selection - could be much more sophisticated
        return self.motivations[0] if self.motivations else 'survive'
    
    def _generate_action(self, situation: Dict[str, Any]) -> str:
        """Generate specific action based on motivation and situation"""
        motivation = self._select_primary_motivation(situation)
        
        action_templates = {
            'achieve_goal': f"{self.name} works toward their goal.",
            'grow': f"{self.name} seeks to learn and improve.",
            'overcome_challenges': f"{self.name} faces the challenge head-on.",
            'maintain_control': f"{self.name} attempts to maintain their position.",
            'help_others': f"{self.name} offers assistance and guidance.",
            'survive': f"{self.name} takes defensive action."
        }
        
        return action_templates.get(motivation, f"{self.name} responds to the situation.")

class AIActorFramework:
    """Module 4: Framework for managing AI actors"""
    
    def __init__(self):
        self.actors: Dict[str, AIActor] = {}
        self.actor_relationships = defaultdict(dict)
    
    def add_actor(self, actor: AIActor):
        """Add an actor to the framework"""
        self.actors[actor.actor_id] = actor
    
    def get_actor(self, actor_id: str) -> Optional[AIActor]:
        """Get actor by ID"""
        return self.actors.get(actor_id)
    
    def update_actor_relationships(self, actor1_id: str, actor2_id: str, 
                                 relationship_type: str, strength: float):
        """Update relationship between two actors"""
        self.actor_relationships[actor1_id][actor2_id] = {
            'type': relationship_type,
            'strength': strength,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
    
    def get_actor_response(self, actor_id: str, situation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get response from specific actor"""
        actor = self.get_actor(actor_id)
        if actor:
            return actor.get_response(situation)
        return None
    
    def get_all_actor_responses(self, situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get responses from all actors"""
        responses = []
        for actor in self.actors.values():
            response = actor.get_response(situation)
            if response:
                responses.append(response)
        return responses

class OutputLayer:
    """Module 5: Interface layer for narrative presentation"""
    
    def __init__(self, memory_core: MemoryCore, world_simulator: WorldStateSimulator, 
                 actor_framework: AIActorFramework):
        self.memory_core = memory_core
        self.world_simulator = world_simulator
        self.actor_framework = actor_framework
        self.conversation_history = []
    
    def generate_response(self, user_input: str, character_id: str = None) -> str:
        """Generate narrative response to user input"""
        # Get world context
        world_context = self.world_simulator.get_world_context()
        
        # Get relevant memories
        relevant_memories = self.memory_core.search_memories(
            query=user_input, 
            character_id=character_id,
            min_significance=0.3
        )
        
        # Get actor responses
        situation = {
            'user_input': user_input,
            'world_context': world_context,
            'relevant_memories': [m.to_dict() for m in relevant_memories]
        }
        
        actor_responses = self.actor_framework.get_all_actor_responses(situation)
        
        # Generate narrative response
        response = self._compose_narrative_response(
            user_input, world_context, relevant_memories, actor_responses
        )
        
        # Store in conversation history
        self.conversation_history.append({
            'user_input': user_input,
            'response': response,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })
        
        return response
    
    def _compose_narrative_response(self, user_input: str, world_context: Dict[str, Any],
                                  memories: List[MemorySlot], 
                                  actor_responses: List[Dict[str, Any]]) -> str:
        """Compose the actual narrative response"""
        
        # Start with world context
        response_parts = []
        
        # Add world state information
        if world_context['current_events']:
            recent_event = world_context['current_events'][-1]
            response_parts.append(f"The world around you reflects recent changes: {recent_event['action'].get('description', 'Something has shifted.')}")
        
        # Add relevant memories
        if memories:
            most_significant = max(memories, key=lambda m: m.get_significance())
            response_parts.append(f"You remember: {most_significant.content.get('description', 'A significant moment.')}")
        
        # Add actor responses
        if actor_responses:
            for actor_response in actor_responses[:3]:  # Limit to 3 most relevant
                response_parts.append(f"{actor_response['name']}: {actor_response['action']}")
        
        # Compose final response
        if response_parts:
            response = " ".join(response_parts)
        else:
            response = "The world responds to your actions, though the full consequences are not yet clear."
        
        return response

class NarrativeEngine:
    """Main Narrative Engine that coordinates all modules"""
    
    def __init__(self):
        # Initialize core modules
        self.memory_core = MemoryCore()
        self.narrative_interpreter = NarrativeInterpreter(self.memory_core)
        self.world_simulator = WorldStateSimulator()
        self.actor_framework = AIActorFramework()
        self.output_layer = OutputLayer(self.memory_core, self.world_simulator, self.actor_framework)
        
        # Initialize default actors
        self._initialize_default_actors()
    
    def _initialize_default_actors(self):
        """Initialize default narrative actors"""
        # Player character (protagonist)
        player = AIActor(
            actor_id="player",
            name="You",
            role=NarrativeRole.PROTAGONIST,
            beliefs={"freedom": 0.8, "justice": 0.7, "growth": 0.9},
            goals=["find_purpose", "overcome_challenges", "help_others"]
        )
        self.actor_framework.add_actor(player)
        
        # Guide character
        guide = AIActor(
            actor_id="guide",
            name="The Mentor",
            role=NarrativeRole.GUIDE,
            beliefs={"wisdom": 0.9, "teaching": 0.8, "patience": 0.7},
            goals=["guide_player", "share_knowledge", "maintain_balance"]
        )
        self.actor_framework.add_actor(guide)
    
    def process_input(self, user_input: str, character_id: str = "player") -> str:
        """Process user input and generate narrative response"""
        
        # Step 1: Interpret the input
        interpretation = self.narrative_interpreter.process_input(user_input, character_id)
        
        # Step 2: Create memory of this interaction
        memory = MemorySlot(
            memory_type=MemoryType.EVENT,
            content={
                'user_input': user_input,
                'interpretation': interpretation,
                'character_id': character_id
            },
            emotional_weight=interpretation['narrative_weight'],
            thematic_tags=interpretation['thematic_elements']
        )
        self.memory_core.add_memory(memory, character_id)
        
        # Step 3: Update world state
        self.world_simulator.update_world_state(
            action={'type': 'user_action', 'description': user_input},
            consequences=[{'type': 'narrative_progression', 'description': 'Story advances'}]
        )
        
        # Step 4: Generate response
        response = self.output_layer.generate_response(user_input, character_id)
        
        return response
    
    def get_narrative_state(self) -> Dict[str, Any]:
        """Get current state of the narrative engine"""
        return {
            'memory_count': len(self.memory_core.memories),
            'evolving_themes': self.memory_core.get_evolving_themes(),
            'unresolved_tensions': self.memory_core.get_unresolved_tensions(),
            'world_context': self.world_simulator.get_world_context(),
            'actor_count': len(self.actor_framework.actors),
            'conversation_history_length': len(self.output_layer.conversation_history)
        }

# Global instance
narrative_engine = NarrativeEngine() 