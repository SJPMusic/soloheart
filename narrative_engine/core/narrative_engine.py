"""
Narrative Engine Core - The Narrative Engine
===========================================

Main orchestration engine that provides domain-agnostic narrative intelligence.
Implements story structure analysis, character modeling, plot generation, and
thematic analysis across multiple domains.
"""

import json
import datetime
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from ..memory.layered_memory import LayeredMemorySystem, MemoryNode, MemoryType, MemoryLayer, EmotionalContext

logger = logging.getLogger(__name__)

# --- Core Data Structures ---

class NarrativeDomain(Enum):
    GAMING = "gaming"
    THERAPY = "therapy"
    EDUCATION = "education"
    ORGANIZATIONAL = "organizational"
    CREATIVE_WRITING = "creative_writing"
    JOURNALISM = "journalism"
    MARKETING = "marketing"

class StoryStructure(Enum):
    HERO_JOURNEY = "hero_journey"
    THREE_ACT = "three_act"
    FIVE_ACT = "five_act"
    CIRCULAR = "circular"
    EPISODIC = "episodic"
    FRAME = "frame"
    PARALLEL = "parallel"
    IN_MEDIA_RES = "in_media_res"

class CharacterRole(Enum):
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MENTOR = "mentor"
    FOIL = "foil"
    LOVE_INTEREST = "love_interest"
    COMIC_RELIEF = "comic_relief"
    CATALYST = "catalyst"

class PlotPointType(Enum):
    INCITING_INCIDENT = "inciting_incident"
    FIRST_TURNING_POINT = "first_turning_point"
    MIDPOINT = "midpoint"
    SECOND_TURNING_POINT = "second_turning_point"
    CLIMAX = "climax"
    RESOLUTION = "resolution"
    SUBPLOT = "subplot"
    CHARACTER_DEVELOPMENT = "character_development"

@dataclass
class Character:
    """Represents a character in the narrative with development tracking."""
    id: str
    name: str
    role: CharacterRole
    description: str
    traits: List[str]
    goals: List[str]
    conflicts: List[str]
    relationships: Dict[str, str]  # character_id -> relationship_type
    development_arc: List[Dict[str, Any]]
    current_state: Dict[str, Any]
    background: Dict[str, Any]
    personality_matrix: Dict[str, float]  # trait -> strength (0.0 to 1.0)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.traits is None:
            self.traits = []
        if self.goals is None:
            self.goals = []
        if self.conflicts is None:
            self.conflicts = []
        if self.relationships is None:
            self.relationships = {}
        if self.development_arc is None:
            self.development_arc = []
        if self.current_state is None:
            self.current_state = {}
        if self.background is None:
            self.background = {}
        if self.personality_matrix is None:
            self.personality_matrix = {}

    def add_development_moment(self, moment: Dict[str, Any]):
        """Add a character development moment to the arc."""
        moment['timestamp'] = datetime.datetime.utcnow().isoformat()
        self.development_arc.append(moment)

    def update_trait(self, trait: str, strength: float):
        """Update a personality trait strength."""
        self.personality_matrix[trait] = max(0.0, min(1.0, strength))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role.value,
            'description': self.description,
            'traits': self.traits,
            'goals': self.goals,
            'conflicts': self.conflicts,
            'relationships': self.relationships,
            'development_arc': self.development_arc,
            'current_state': self.current_state,
            'background': self.background,
            'personality_matrix': self.personality_matrix
        }

@dataclass
class PlotPoint:
    """Represents a plot point in the narrative."""
    id: str
    plot_point_type: PlotPointType
    title: str
    description: str
    characters_involved: List[str]
    emotional_impact: Dict[str, float]  # character_id -> emotional_change
    narrative_significance: float  # 0.0 to 1.0
    thematic_elements: List[str]
    world_state_changes: Dict[str, Any]
    timestamp: datetime.datetime
    prerequisites: List[str]  # plot_point_ids
    consequences: List[str]   # plot_point_ids
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.characters_involved is None:
            self.characters_involved = []
        if self.emotional_impact is None:
            self.emotional_impact = {}
        if self.thematic_elements is None:
            self.thematic_elements = []
        if self.world_state_changes is None:
            self.world_state_changes = {}
        if self.prerequisites is None:
            self.prerequisites = []
        if self.consequences is None:
            self.consequences = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'plot_point_type': self.plot_point_type.value,
            'title': self.title,
            'description': self.description,
            'characters_involved': self.characters_involved,
            'emotional_impact': self.emotional_impact,
            'narrative_significance': self.narrative_significance,
            'thematic_elements': self.thematic_elements,
            'world_state_changes': self.world_state_changes,
            'timestamp': self.timestamp.isoformat(),
            'prerequisites': self.prerequisites,
            'consequences': self.consequences
        }

@dataclass
class Narrative:
    """Represents a complete narrative with all its components."""
    id: str
    title: str
    description: str
    domain: NarrativeDomain
    story_structure: StoryStructure
    characters: Dict[str, Character]
    plot_points: Dict[str, PlotPoint]
    themes: List[str]
    world_state: Dict[str, Any]
    narrative_arc: List[str]  # plot_point_ids in order
    metadata: Dict[str, Any]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.characters is None:
            self.characters = {}
        if self.plot_points is None:
            self.plot_points = {}
        if self.themes is None:
            self.themes = []
        if self.world_state is None:
            self.world_state = {}
        if self.narrative_arc is None:
            self.narrative_arc = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = self.created_at

    def add_character(self, character: Character):
        """Add a character to the narrative."""
        self.characters[character.id] = character
        self.updated_at = datetime.datetime.utcnow()

    def add_plot_point(self, plot_point: PlotPoint):
        """Add a plot point to the narrative."""
        self.plot_points[plot_point.id] = plot_point
        self.narrative_arc.append(plot_point.id)
        self.updated_at = datetime.datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'domain': self.domain.value,
            'story_structure': self.story_structure.value,
            'characters': {k: v.to_dict() for k, v in self.characters.items()},
            'plot_points': {k: v.to_dict() for k, v in self.plot_points.items()},
            'themes': self.themes,
            'world_state': self.world_state,
            'narrative_arc': self.narrative_arc,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class NarrativeAnalysis:
    """Results of narrative analysis."""
    coherence_score: float
    thematic_consistency: float
    character_development: Dict[str, float]
    plot_complexity: float
    emotional_arc: Dict[str, List[float]]
    pacing_analysis: Dict[str, Any]
    structural_integrity: float
    themes: List[str]
    motifs: List[str]
    conflicts: List[Dict[str, Any]]
    recommendations: List[str]

# --- Domain Adapters ---

class DomainAdapter:
    """Base class for domain-specific narrative adapters."""
    
    def __init__(self, domain: NarrativeDomain):
        self.domain = domain
    
    def analyze_narrative(self, narrative: Narrative) -> NarrativeAnalysis:
        """Analyze narrative from domain-specific perspective."""
        raise NotImplementedError
    
    def generate_plot_point(self, narrative: Narrative, context: Dict[str, Any]) -> PlotPoint:
        """Generate domain-appropriate plot point."""
        raise NotImplementedError
    
    def adapt_narrative(self, narrative: Narrative, new_context: Dict[str, Any]) -> Narrative:
        """Adapt narrative for domain-specific requirements."""
        raise NotImplementedError

# --- Main Narrative Engine ---

class NarrativeEngine:
    """
    Main narrative engine that provides domain-agnostic narrative intelligence.
    Orchestrates memory, analysis, generation, and adaptation across domains.
    """
    
    def __init__(self):
        self.memory_system = LayeredMemorySystem(campaign_id='Default Campaign')
        self.domain_adapters: Dict[NarrativeDomain, DomainAdapter] = {}
        self.narratives: Dict[str, Narrative] = {}
        self.analysis_cache: Dict[str, NarrativeAnalysis] = {}
        
        # Register default domain adapters
        self._register_default_adapters()
        
        logger.info("Narrative Engine initialized successfully")
    
    def register_domain_adapter(self, domain: NarrativeDomain, adapter: DomainAdapter):
        """Register a domain-specific adapter."""
        self.domain_adapters[domain] = adapter
        logger.info(f"Registered adapter for domain: {domain.value}")
    
    def create_narrative(self, title: str, description: str, domain: NarrativeDomain,
                        story_structure: StoryStructure = StoryStructure.THREE_ACT) -> Narrative:
        """Create a new narrative."""
        narrative = Narrative(
            id=None,
            title=title,
            description=description,
            domain=domain,
            story_structure=story_structure,
            characters={},
            plot_points={},
            themes=[],
            world_state={},
            narrative_arc=[],
            metadata={},
            created_at=None,
            updated_at=None
        )
        
        self.narratives[narrative.id] = narrative
        
        # Store in memory
        self.memory_system.add_memory(
            content={'action': 'narrative_created', 'narrative_id': narrative.id},
            memory_type=MemoryType.EVENT,
            layer=MemoryLayer.LONG_TERM,
            user_id='system',
            session_id='narrative_creation',
            emotional_weight=0.3,
            thematic_tags=['narrative_creation', domain.value],
            narrative_context={'domain': domain.value, 'structure': story_structure.value}
        )
        
        logger.info(f"Created narrative: {title} ({domain.value})")
        return narrative
    
    def add_character(self, narrative_id: str, character_data: Dict[str, Any]) -> Character:
        """Add a character to a narrative."""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        narrative = self.narratives[narrative_id]
        
        character = Character(
            id=None,
            name=character_data['name'],
            role=CharacterRole(character_data['role']),
            description=character_data.get('description', ''),
            traits=character_data.get('traits', []),
            goals=character_data.get('goals', []),
            conflicts=character_data.get('conflicts', []),
            relationships=character_data.get('relationships', {}),
            development_arc=character_data.get('development_arc', []),
            current_state=character_data.get('current_state', {}),
            background=character_data.get('background', {}),
            personality_matrix=character_data.get('personality_matrix', {})
        )
        
        narrative.add_character(character)
        
        # Store character in memory
        self.memory_system.add_memory(
            content={'action': 'character_added', 'character_id': character.id, 'narrative_id': narrative_id},
            memory_type=MemoryType.CHARACTER_DEVELOPMENT,
            layer=MemoryLayer.MID_TERM,
            user_id='system',
            session_id='character_creation',
            emotional_weight=0.5,
            thematic_tags=['character_creation', character.role.value],
            narrative_context={'narrative_id': narrative_id, 'character_name': character.name}
        )
        
        logger.info(f"Added character {character.name} to narrative {narrative.title}")
        return character
    
    def generate_plot_point(self, narrative_id: str, context: Dict[str, Any]) -> PlotPoint:
        """Generate a plot point for a narrative."""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        narrative = self.narratives[narrative_id]
        
        # Use domain adapter if available
        if narrative.domain in self.domain_adapters:
            plot_point = self.domain_adapters[narrative.domain].generate_plot_point(narrative, context)
        else:
            # Default plot point generation
            plot_point = self._generate_default_plot_point(narrative, context)
        
        narrative.add_plot_point(plot_point)
        
        # Store plot point in memory
        self.memory_system.add_memory(
            content={'action': 'plot_point_generated', 'plot_point_id': plot_point.id, 'narrative_id': narrative_id},
            memory_type=MemoryType.PLOT_POINT,
            layer=MemoryLayer.MID_TERM,
            user_id='system',
            session_id='plot_generation',
            emotional_weight=plot_point.narrative_significance,
            thematic_tags=plot_point.thematic_elements,
            narrative_context={'narrative_id': narrative_id, 'plot_type': plot_point.plot_point_type.value}
        )
        
        logger.info(f"Generated plot point: {plot_point.title}")
        return plot_point
    
    def analyze_narrative(self, narrative_id: str) -> NarrativeAnalysis:
        """Analyze a narrative for structure, coherence, and themes."""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        narrative = self.narratives[narrative_id]
        
        # Check cache first
        if narrative_id in self.analysis_cache:
            return self.analysis_cache[narrative_id]
        
        # Use domain adapter if available
        if narrative.domain in self.domain_adapters:
            analysis = self.domain_adapters[narrative.domain].analyze_narrative(narrative)
        else:
            # Default analysis
            analysis = self._analyze_narrative_default(narrative)
        
        # Cache the analysis
        self.analysis_cache[narrative_id] = analysis
        
        # Store analysis in memory
        self.memory_system.add_memory(
            content={'action': 'narrative_analyzed', 'narrative_id': narrative_id, 'coherence_score': analysis.coherence_score},
            memory_type=MemoryType.THEME,
            layer=MemoryLayer.MID_TERM,
            user_id='system',
            session_id='narrative_analysis',
            emotional_weight=0.4,
            thematic_tags=['analysis', 'coherence', 'themes'],
            narrative_context={'narrative_id': narrative_id, 'domain': narrative.domain.value}
        )
        
        logger.info(f"Analyzed narrative: {narrative.title}")
        return analysis
    
    def adapt_narrative(self, narrative_id: str, new_context: Dict[str, Any]) -> Narrative:
        """Adapt a narrative based on new context or requirements."""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        narrative = self.narratives[narrative_id]
        
        # Use domain adapter if available
        if narrative.domain in self.domain_adapters:
            adapted_narrative = self.domain_adapters[narrative.domain].adapt_narrative(narrative, new_context)
        else:
            # Default adaptation
            adapted_narrative = self._adapt_narrative_default(narrative, new_context)
        
        # Update the narrative
        self.narratives[narrative_id] = adapted_narrative
        
        # Store adaptation in memory
        self.memory_system.add_memory(
            content={'action': 'narrative_adapted', 'narrative_id': narrative_id, 'adaptation_context': new_context},
            memory_type=MemoryType.DECISION,
            layer=MemoryLayer.MID_TERM,
            user_id='system',
            session_id='narrative_adaptation',
            emotional_weight=0.6,
            thematic_tags=['adaptation', 'context_change'],
            narrative_context={'narrative_id': narrative_id, 'adaptation_type': new_context.get('type', 'general')}
        )
        
        logger.info(f"Adapted narrative: {narrative.title}")
        return adapted_narrative
    
    def recall_narrative_context(self, query: str = None, domain: NarrativeDomain = None, 
                                limit: int = 10) -> List[MemoryNode]:
        """Recall narrative-related memories."""
        thematic_tags = []
        if domain:
            thematic_tags.append(domain.value)
        
        return self.memory_system.recall(
            query=query,
            thematic=thematic_tags,
            limit=limit
        )
    
    def get_narrative_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about all narratives."""
        stats = {
            'total_narratives': len(self.narratives),
            'narratives_by_domain': {},
            'total_characters': 0,
            'total_plot_points': 0,
            'memory_stats': self.memory_system.get_memory_stats()
        }
        
        for narrative in self.narratives.values():
            domain = narrative.domain.value
            if domain not in stats['narratives_by_domain']:
                stats['narratives_by_domain'][domain] = 0
            stats['narratives_by_domain'][domain] += 1
            stats['total_characters'] += len(narrative.characters)
            stats['total_plot_points'] += len(narrative.plot_points)
        
        return stats
    
    def export_narrative(self, narrative_id: str) -> Dict[str, Any]:
        """Export a narrative with all its components."""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        narrative = self.narratives[narrative_id]
        analysis = self.analyze_narrative(narrative_id)
        
        export_data = {
            'narrative': narrative.to_dict(),
            'analysis': asdict(analysis),
            'memory_context': [m.to_dict() for m in self.recall_narrative_context(narrative_id=narrative_id, limit=20)],
            'export_metadata': {
                'exported_at': datetime.datetime.utcnow().isoformat(),
                'engine_version': '1.0.0',
                'domain': narrative.domain.value
            }
        }
        
        return export_data
    
    def import_narrative(self, export_data: Dict[str, Any]) -> str:
        """Import a narrative from export data."""
        narrative_data = export_data['narrative']
        
        # Reconstruct narrative
        narrative = Narrative(
            id=narrative_data['id'],
            title=narrative_data['title'],
            description=narrative_data['description'],
            domain=NarrativeDomain(narrative_data['domain']),
            story_structure=StoryStructure(narrative_data['story_structure']),
            characters={},
            plot_points={},
            themes=narrative_data['themes'],
            world_state=narrative_data['world_state'],
            narrative_arc=narrative_data['narrative_arc'],
            metadata=narrative_data['metadata'],
            created_at=datetime.datetime.fromisoformat(narrative_data['created_at']),
            updated_at=datetime.datetime.fromisoformat(narrative_data['updated_at'])
        )
        
        # Reconstruct characters
        for char_data in narrative_data['characters'].values():
            character = Character(
                id=char_data['id'],
                name=char_data['name'],
                role=CharacterRole(char_data['role']),
                description=char_data['description'],
                traits=char_data['traits'],
                goals=char_data['goals'],
                conflicts=char_data['conflicts'],
                relationships=char_data['relationships'],
                development_arc=char_data['development_arc'],
                current_state=char_data['current_state'],
                background=char_data['background'],
                personality_matrix=char_data['personality_matrix']
            )
            narrative.characters[character.id] = character
        
        # Reconstruct plot points
        for plot_data in narrative_data['plot_points'].values():
            plot_point = PlotPoint(
                id=plot_data['id'],
                plot_point_type=PlotPointType(plot_data['plot_point_type']),
                title=plot_data['title'],
                description=plot_data['description'],
                characters_involved=plot_data['characters_involved'],
                emotional_impact=plot_data['emotional_impact'],
                narrative_significance=plot_data['narrative_significance'],
                thematic_elements=plot_data['thematic_elements'],
                world_state_changes=plot_data['world_state_changes'],
                timestamp=datetime.datetime.fromisoformat(plot_data['timestamp']),
                prerequisites=plot_data['prerequisites'],
                consequences=plot_data['consequences']
            )
            narrative.plot_points[plot_point.id] = plot_point
        
        self.narratives[narrative.id] = narrative
        
        # Import analysis if available
        if 'analysis' in export_data:
            self.analysis_cache[narrative.id] = NarrativeAnalysis(**export_data['analysis'])
        
        logger.info(f"Imported narrative: {narrative.title}")
        return narrative.id
    
    def _register_default_adapters(self):
        """Register default domain adapters."""
        # This will be implemented when domain adapters are created
        pass
    
    def _generate_default_plot_point(self, narrative: Narrative, context: Dict[str, Any]) -> PlotPoint:
        """Generate a default plot point when no domain adapter is available."""
        plot_point_type = PlotPointType(context.get('type', PlotPointType.SUBPLOT))
        
        plot_point = PlotPoint(
            id=None,
            plot_point_type=plot_point_type,
            title=context.get('title', f"{plot_point_type.value.replace('_', ' ').title()}"),
            description=context.get('description', 'A plot point in the narrative'),
            characters_involved=context.get('characters_involved', []),
            emotional_impact=context.get('emotional_impact', {}),
            narrative_significance=context.get('narrative_significance', 0.5),
            thematic_elements=context.get('thematic_elements', []),
            world_state_changes=context.get('world_state_changes', {}),
            timestamp=datetime.datetime.utcnow(),
            prerequisites=context.get('prerequisites', []),
            consequences=context.get('consequences', [])
        )
        
        return plot_point
    
    def _analyze_narrative_default(self, narrative: Narrative) -> NarrativeAnalysis:
        """Perform default narrative analysis when no domain adapter is available."""
        # Calculate coherence based on plot point connections
        coherence_score = self._calculate_coherence(narrative)
        
        # Analyze character development
        character_development = {}
        for character in narrative.characters.values():
            development_score = len(character.development_arc) / max(len(narrative.plot_points), 1)
            character_development[character.id] = min(development_score, 1.0)
        
        # Calculate plot complexity
        plot_complexity = len(narrative.plot_points) / max(len(narrative.characters), 1)
        
        # Analyze emotional arcs
        emotional_arc = {}
        for character in narrative.characters.values():
            emotional_arc[character.id] = [0.5] * len(narrative.plot_points)  # Default emotional state
        
        # Extract themes from plot points
        themes = set()
        for plot_point in narrative.plot_points.values():
            themes.update(plot_point.thematic_elements)
        
        analysis = NarrativeAnalysis(
            coherence_score=coherence_score,
            thematic_consistency=0.7,  # Default value
            character_development=character_development,
            plot_complexity=plot_complexity,
            emotional_arc=emotional_arc,
            pacing_analysis={'overall_pacing': 'moderate'},
            structural_integrity=0.8,  # Default value
            themes=list(themes),
            motifs=list(themes),  # Simplified for default analysis
            conflicts=[],  # Would need more sophisticated analysis
            recommendations=['Consider adding more character development moments']
        )
        
        return analysis
    
    def _adapt_narrative_default(self, narrative: Narrative, new_context: Dict[str, Any]) -> Narrative:
        """Perform default narrative adaptation when no domain adapter is available."""
        # Create a copy of the narrative
        adapted_narrative = Narrative(
            id=narrative.id,
            title=narrative.title,
            description=narrative.description,
            domain=narrative.domain,
            story_structure=narrative.story_structure,
            characters=narrative.characters.copy(),
            plot_points=narrative.plot_points.copy(),
            themes=narrative.themes.copy(),
            world_state=narrative.world_state.copy(),
            narrative_arc=narrative.narrative_arc.copy(),
            metadata=narrative.metadata.copy(),
            created_at=narrative.created_at,
            updated_at=datetime.datetime.utcnow()
        )
        
        # Apply context changes
        if 'world_state_changes' in new_context:
            adapted_narrative.world_state.update(new_context['world_state_changes'])
        
        if 'new_themes' in new_context:
            adapted_narrative.themes.extend(new_context['new_themes'])
        
        return adapted_narrative
    
    def _calculate_coherence(self, narrative: Narrative) -> float:
        """Calculate narrative coherence based on plot point connections."""
        if not narrative.plot_points:
            return 1.0
        
        total_connections = 0
        max_possible_connections = len(narrative.plot_points) * (len(narrative.plot_points) - 1)
        
        for plot_point in narrative.plot_points.values():
            total_connections += len(plot_point.prerequisites) + len(plot_point.consequences)
        
        if max_possible_connections == 0:
            return 1.0
        
        return min(total_connections / max_possible_connections, 1.0)

# Global instance
narrative_engine = NarrativeEngine() 