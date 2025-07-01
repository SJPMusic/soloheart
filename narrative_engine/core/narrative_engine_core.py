"""
Narrative Engine Core - Domain-Agnostic Narrative Intelligence

This module provides the foundational architecture for a Narrative Engine that can
work across different domains including gaming, therapy, education, organizational
narratives, and more.

Key Features:
- Story structure analysis and generation
- Narrative coherence and consistency
- Thematic analysis and development
- Modular architecture for domain-specific extensions
- Character and relationship modeling
- Plot progression and conflict resolution
- Emotional arc tracking
- World-building and setting management
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NarrativeDomain(Enum):
    """Supported narrative domains"""
    GAMING = "gaming"
    THERAPY = "therapy"
    EDUCATION = "education"
    ORGANIZATIONAL = "organizational"
    CREATIVE_WRITING = "creative_writing"
    JOURNALISM = "journalism"
    MARKETING = "marketing"


class StoryStructure(Enum):
    """Common story structure patterns"""
    HERO_JOURNEY = "hero_journey"
    THREE_ACT = "three_act"
    FIVE_ACT = "five_act"
    FREYTAG_PYRAMID = "freytag_pyramid"
    SAVE_THE_CAT = "save_the_cat"
    CUSTOM = "custom"


class EmotionalValence(Enum):
    """Emotional valence for tracking emotional arcs"""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2


@dataclass
class NarrativeElement:
    """Base class for narrative elements"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Character(NarrativeElement):
    """Character representation in the narrative"""
    personality_traits: List[str] = field(default_factory=list)
    motivations: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)  # character_id -> relationship_type
    emotional_state: EmotionalValence = EmotionalValence.NEUTRAL
    arc_progression: float = 0.0  # 0.0 to 1.0
    role: str = ""  # protagonist, antagonist, supporting, etc.


@dataclass
class Setting(NarrativeElement):
    """Setting/world representation"""
    location_type: str = ""  # city, forest, space, etc.
    atmosphere: str = ""
    rules: List[str] = field(default_factory=list)  # world rules, physics, etc.
    history: str = ""
    current_state: str = ""


@dataclass
class PlotPoint(NarrativeElement):
    """Individual plot point or event"""
    story_structure_position: float = 0.0  # 0.0 to 1.0 in story progression
    emotional_impact: EmotionalValence = EmotionalValence.NEUTRAL
    characters_involved: List[str] = field(default_factory=list)
    conflict_type: str = ""
    resolution: str = ""
    consequences: List[str] = field(default_factory=list)


@dataclass
class Theme(NarrativeElement):
    """Thematic element"""
    motif: str = ""
    development_arc: List[float] = field(default_factory=list)  # progression over time
    symbols: List[str] = field(default_factory=list)
    message: str = ""


@dataclass
class NarrativeArc:
    """Complete narrative arc tracking"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    structure_type: StoryStructure = StoryStructure.THREE_ACT
    plot_points: List[PlotPoint] = field(default_factory=list)
    characters: List[Character] = field(default_factory=list)
    themes: List[Theme] = field(default_factory=list)
    setting: Optional[Setting] = None
    emotional_progression: List[Tuple[float, EmotionalValence]] = field(default_factory=list)
    coherence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class NarrativeAnalyzer(ABC):
    """Abstract base class for narrative analysis"""
    
    @abstractmethod
    def analyze_coherence(self, narrative: NarrativeArc) -> float:
        """Analyze narrative coherence and return a score (0.0 to 1.0)"""
        pass
    
    @abstractmethod
    def identify_themes(self, narrative: NarrativeArc) -> List[Theme]:
        """Identify themes in the narrative"""
        pass
    
    @abstractmethod
    def analyze_character_arcs(self, narrative: NarrativeArc) -> Dict[str, float]:
        """Analyze character development arcs"""
        pass
    
    @abstractmethod
    def detect_conflicts(self, narrative: NarrativeArc) -> List[Dict[str, Any]]:
        """Detect and analyze conflicts in the narrative"""
        pass


class NarrativeGenerator(ABC):
    """Abstract base class for narrative generation"""
    
    @abstractmethod
    def generate_plot_point(self, context: Dict[str, Any]) -> PlotPoint:
        """Generate a new plot point based on context"""
        pass
    
    @abstractmethod
    def develop_character(self, character: Character, context: Dict[str, Any]) -> Character:
        """Develop a character based on narrative context"""
        pass
    
    @abstractmethod
    def create_conflict(self, characters: List[Character], setting: Setting) -> PlotPoint:
        """Create a conflict involving the given characters"""
        pass
    
    @abstractmethod
    def resolve_conflict(self, conflict: PlotPoint, context: Dict[str, Any]) -> PlotPoint:
        """Resolve a conflict based on context"""
        pass


class DomainAdapter(ABC):
    """Abstract base class for domain-specific adaptations"""
    
    @abstractmethod
    def adapt_narrative_element(self, element: NarrativeElement, domain: NarrativeDomain) -> NarrativeElement:
        """Adapt a narrative element for a specific domain"""
        pass
    
    @abstractmethod
    def get_domain_rules(self, domain: NarrativeDomain) -> Dict[str, Any]:
        """Get domain-specific rules and constraints"""
        pass
    
    @abstractmethod
    def validate_narrative(self, narrative: NarrativeArc, domain: NarrativeDomain) -> bool:
        """Validate narrative for domain-specific requirements"""
        pass


class NarrativeEngineCore:
    """Core Narrative Engine that orchestrates all components"""
    
    def __init__(self):
        self.analyzers: Dict[NarrativeDomain, NarrativeAnalyzer] = {}
        self.generators: Dict[NarrativeDomain, NarrativeGenerator] = {}
        self.adapters: Dict[NarrativeDomain, DomainAdapter] = {}
        self.narratives: Dict[str, NarrativeArc] = {}
        self.active_narrative: Optional[str] = None
        
    def register_analyzer(self, domain: NarrativeDomain, analyzer: NarrativeAnalyzer):
        """Register a narrative analyzer for a specific domain"""
        self.analyzers[domain] = analyzer
        logger.info(f"Registered analyzer for domain: {domain.value}")
    
    def register_generator(self, domain: NarrativeDomain, generator: NarrativeGenerator):
        """Register a narrative generator for a specific domain"""
        self.generators[domain] = generator
        logger.info(f"Registered generator for domain: {domain.value}")
    
    def register_adapter(self, domain: NarrativeDomain, adapter: DomainAdapter):
        """Register a domain adapter"""
        self.adapters[domain] = adapter
        logger.info(f"Registered adapter for domain: {domain.value}")
    
    def create_narrative(self, name: str, structure_type: StoryStructure = StoryStructure.THREE_ACT) -> str:
        """Create a new narrative arc"""
        narrative = NarrativeArc(name=name, structure_type=structure_type)
        self.narratives[narrative.id] = narrative
        if not self.active_narrative:
            self.active_narrative = narrative.id
        logger.info(f"Created narrative: {name} (ID: {narrative.id})")
        return narrative.id
    
    def add_character(self, narrative_id: str, character: Character) -> str:
        """Add a character to a narrative"""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        self.narratives[narrative_id].characters.append(character)
        logger.info(f"Added character {character.name} to narrative {narrative_id}")
        return character.id
    
    def add_plot_point(self, narrative_id: str, plot_point: PlotPoint) -> str:
        """Add a plot point to a narrative"""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        self.narratives[narrative_id].plot_points.append(plot_point)
        self.narratives[narrative_id].updated_at = datetime.now()
        logger.info(f"Added plot point {plot_point.name} to narrative {narrative_id}")
        return plot_point.id
    
    def analyze_narrative(self, narrative_id: str, domain: NarrativeDomain) -> Dict[str, Any]:
        """Analyze a narrative using domain-specific analyzer"""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        if domain not in self.analyzers:
            raise ValueError(f"No analyzer registered for domain {domain.value}")
        
        narrative = self.narratives[narrative_id]
        analyzer = self.analyzers[domain]
        
        analysis = {
            'coherence_score': analyzer.analyze_coherence(narrative),
            'themes': analyzer.identify_themes(narrative),
            'character_arcs': analyzer.analyze_character_arcs(narrative),
            'conflicts': analyzer.detect_conflicts(narrative),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Analyzed narrative {narrative_id} for domain {domain.value}")
        return analysis
    
    def generate_next_plot_point(self, narrative_id: str, domain: NarrativeDomain, context: Dict[str, Any]) -> PlotPoint:
        """Generate the next plot point for a narrative"""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        if domain not in self.generators:
            raise ValueError(f"No generator registered for domain {domain.value}")
        
        narrative = self.narratives[narrative_id]
        generator = self.generators[domain]
        
        # Add narrative context to the generation context
        context.update({
            'narrative': narrative,
            'current_plot_points': narrative.plot_points,
            'characters': narrative.characters,
            'themes': narrative.themes
        })
        
        plot_point = generator.generate_plot_point(context)
        logger.info(f"Generated plot point {plot_point.name} for narrative {narrative_id}")
        return plot_point
    
    def adapt_for_domain(self, narrative_id: str, target_domain: NarrativeDomain) -> NarrativeArc:
        """Adapt a narrative for a specific domain"""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        if target_domain not in self.adapters:
            raise ValueError(f"No adapter registered for domain {target_domain.value}")
        
        narrative = self.narratives[narrative_id]
        adapter = self.adapters[target_domain]
        
        # Create a copy of the narrative for adaptation
        adapted_narrative = NarrativeArc(
            name=f"{narrative.name} ({target_domain.value})",
            structure_type=narrative.structure_type
        )
        
        # Adapt all elements
        for character in narrative.characters:
            adapted_character = adapter.adapt_narrative_element(character, target_domain)
            adapted_narrative.characters.append(adapted_character)
        
        for plot_point in narrative.plot_points:
            adapted_plot_point = adapter.adapt_narrative_element(plot_point, target_domain)
            adapted_narrative.plot_points.append(adapted_plot_point)
        
        for theme in narrative.themes:
            adapted_theme = adapter.adapt_narrative_element(theme, target_domain)
            adapted_narrative.themes.append(adapted_theme)
        
        if narrative.setting:
            adapted_setting = adapter.adapt_narrative_element(narrative.setting, target_domain)
            adapted_narrative.setting = adapted_setting
        
        logger.info(f"Adapted narrative {narrative_id} for domain {target_domain.value}")
        return adapted_narrative
    
    def get_narrative_summary(self, narrative_id: str) -> Dict[str, Any]:
        """Get a summary of a narrative"""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        narrative = self.narratives[narrative_id]
        
        summary = {
            'id': narrative.id,
            'name': narrative.name,
            'structure_type': narrative.structure_type.value,
            'character_count': len(narrative.characters),
            'plot_point_count': len(narrative.plot_points),
            'theme_count': len(narrative.themes),
            'coherence_score': narrative.coherence_score,
            'created_at': narrative.created_at.isoformat(),
            'updated_at': narrative.updated_at.isoformat(),
            'characters': [{'id': c.id, 'name': c.name, 'role': c.role} for c in narrative.characters],
            'plot_points': [{'id': p.id, 'name': p.name, 'position': p.story_structure_position} for p in narrative.plot_points]
        }
        
        return summary
    
    def export_narrative(self, narrative_id: str) -> str:
        """Export a narrative to JSON"""
        if narrative_id not in self.narratives:
            raise ValueError(f"Narrative {narrative_id} not found")
        
        narrative = self.narratives[narrative_id]
        
        # Convert to dict for JSON serialization
        export_data = {
            'id': narrative.id,
            'name': narrative.name,
            'structure_type': narrative.structure_type.value,
            'plot_points': [],
            'characters': [],
            'themes': [],
            'setting': None,
            'emotional_progression': narrative.emotional_progression,
            'coherence_score': narrative.coherence_score,
            'created_at': narrative.created_at.isoformat(),
            'updated_at': narrative.updated_at.isoformat()
        }
        
        # Convert plot points
        for plot_point in narrative.plot_points:
            export_data['plot_points'].append({
                'id': plot_point.id,
                'name': plot_point.name,
                'description': plot_point.description,
                'story_structure_position': plot_point.story_structure_position,
                'emotional_impact': plot_point.emotional_impact.value,
                'characters_involved': plot_point.characters_involved,
                'conflict_type': plot_point.conflict_type,
                'resolution': plot_point.resolution,
                'consequences': plot_point.consequences,
                'tags': list(plot_point.tags),
                'metadata': plot_point.metadata
            })
        
        # Convert characters
        for character in narrative.characters:
            export_data['characters'].append({
                'id': character.id,
                'name': character.name,
                'description': character.description,
                'personality_traits': character.personality_traits,
                'motivations': character.motivations,
                'relationships': character.relationships,
                'emotional_state': character.emotional_state.value,
                'arc_progression': character.arc_progression,
                'role': character.role,
                'tags': list(character.tags),
                'metadata': character.metadata
            })
        
        # Convert themes
        for theme in narrative.themes:
            export_data['themes'].append({
                'id': theme.id,
                'name': theme.name,
                'description': theme.description,
                'motif': theme.motif,
                'development_arc': theme.development_arc,
                'symbols': theme.symbols,
                'message': theme.message,
                'tags': list(theme.tags),
                'metadata': theme.metadata
            })
        
        # Convert setting
        if narrative.setting:
            export_data['setting'] = {
                'id': narrative.setting.id,
                'name': narrative.setting.name,
                'description': narrative.setting.description,
                'location_type': narrative.setting.location_type,
                'atmosphere': narrative.setting.atmosphere,
                'rules': narrative.setting.rules,
                'history': narrative.setting.history,
                'current_state': narrative.setting.current_state,
                'tags': list(narrative.setting.tags),
                'metadata': narrative.setting.metadata
            }
        
        return json.dumps(export_data, indent=2)
    
    def import_narrative(self, json_data: str) -> str:
        """Import a narrative from JSON"""
        data = json.loads(json_data)
        
        # Create narrative
        narrative = NarrativeArc(
            id=data['id'],
            name=data['name'],
            structure_type=StoryStructure(data['structure_type']),
            emotional_progression=[(float(pos), EmotionalValence(val)) for pos, val in data['emotional_progression']],
            coherence_score=data['coherence_score'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )
        
        # Import plot points
        for plot_data in data['plot_points']:
            plot_point = PlotPoint(
                id=plot_data['id'],
                name=plot_data['name'],
                description=plot_data['description'],
                story_structure_position=plot_data['story_structure_position'],
                emotional_impact=EmotionalValence(plot_data['emotional_impact']),
                characters_involved=plot_data['characters_involved'],
                conflict_type=plot_data['conflict_type'],
                resolution=plot_data['resolution'],
                consequences=plot_data['consequences'],
                tags=set(plot_data['tags']),
                metadata=plot_data['metadata']
            )
            narrative.plot_points.append(plot_point)
        
        # Import characters
        for char_data in data['characters']:
            character = Character(
                id=char_data['id'],
                name=char_data['name'],
                description=char_data['description'],
                personality_traits=char_data['personality_traits'],
                motivations=char_data['motivations'],
                relationships=char_data['relationships'],
                emotional_state=EmotionalValence(char_data['emotional_state']),
                arc_progression=char_data['arc_progression'],
                role=char_data['role'],
                tags=set(char_data['tags']),
                metadata=char_data['metadata']
            )
            narrative.characters.append(character)
        
        # Import themes
        for theme_data in data['themes']:
            theme = Theme(
                id=theme_data['id'],
                name=theme_data['name'],
                description=theme_data['description'],
                motif=theme_data['motif'],
                development_arc=theme_data['development_arc'],
                symbols=theme_data['symbols'],
                message=theme_data['message'],
                tags=set(theme_data['tags']),
                metadata=theme_data['metadata']
            )
            narrative.themes.append(theme)
        
        # Import setting
        if data['setting']:
            setting_data = data['setting']
            setting = Setting(
                id=setting_data['id'],
                name=setting_data['name'],
                description=setting_data['description'],
                location_type=setting_data['location_type'],
                atmosphere=setting_data['atmosphere'],
                rules=setting_data['rules'],
                history=setting_data['history'],
                current_state=setting_data['current_state'],
                tags=set(setting_data['tags']),
                metadata=setting_data['metadata']
            )
            narrative.setting = setting
        
        self.narratives[narrative.id] = narrative
        logger.info(f"Imported narrative: {narrative.name} (ID: {narrative.id})")
        return narrative.id


# Example implementations for demonstration
class BasicNarrativeAnalyzer(NarrativeAnalyzer):
    """Basic implementation of narrative analyzer"""
    
    def analyze_coherence(self, narrative: NarrativeArc) -> float:
        """Simple coherence analysis based on plot point connections"""
        if not narrative.plot_points:
            return 0.0
        
        # Check for character consistency across plot points
        character_consistency = 0.0
        if narrative.characters:
            character_appearances = {}
            for plot_point in narrative.plot_points:
                for char_id in plot_point.characters_involved:
                    character_appearances[char_id] = character_appearances.get(char_id, 0) + 1
            
            # Calculate consistency based on character usage
            total_plot_points = len(narrative.plot_points)
            character_consistency = min(1.0, sum(character_appearances.values()) / (total_plot_points * len(narrative.characters)))
        
        # Check for emotional progression
        emotional_coherence = 0.0
        if len(narrative.emotional_progression) > 1:
            # Simple check for emotional progression
            emotional_coherence = 0.5  # Placeholder
        
        return (character_consistency + emotional_coherence) / 2
    
    def identify_themes(self, narrative: NarrativeArc) -> List[Theme]:
        """Identify themes based on plot points and character motivations"""
        themes = []
        
        # Analyze character motivations for themes
        motivation_themes = {}
        for character in narrative.characters:
            for motivation in character.motivations:
                if motivation not in motivation_themes:
                    motivation_themes[motivation] = Theme(
                        name=f"Theme: {motivation}",
                        motif=motivation,
                        message=f"Exploration of {motivation}"
                    )
                themes.append(motivation_themes[motivation])
        
        return themes
    
    def analyze_character_arcs(self, narrative: NarrativeArc) -> Dict[str, float]:
        """Analyze character development progression"""
        arcs = {}
        for character in narrative.characters:
            arcs[character.id] = character.arc_progression
        return arcs
    
    def detect_conflicts(self, narrative: NarrativeArc) -> List[Dict[str, Any]]:
        """Detect conflicts in the narrative"""
        conflicts = []
        for plot_point in narrative.plot_points:
            if plot_point.conflict_type:
                conflicts.append({
                    'plot_point_id': plot_point.id,
                    'conflict_type': plot_point.conflict_type,
                    'characters_involved': plot_point.characters_involved,
                    'resolution': plot_point.resolution
                })
        return conflicts


class BasicNarrativeGenerator(NarrativeGenerator):
    """Basic implementation of narrative generator"""
    
    def generate_plot_point(self, context: Dict[str, Any]) -> PlotPoint:
        """Generate a basic plot point"""
        narrative = context.get('narrative')
        current_points = context.get('current_plot_points', [])
        
        # Calculate next position in story structure
        next_position = len(current_points) / max(1, len(current_points) + 1)
        
        plot_point = PlotPoint(
            name=f"Plot Point {len(current_points) + 1}",
            description="Generated plot point",
            story_structure_position=next_position,
            emotional_impact=EmotionalValence.NEUTRAL
        )
        
        return plot_point
    
    def develop_character(self, character: Character, context: Dict[str, Any]) -> Character:
        """Develop a character based on context"""
        # Simple character development
        character.arc_progression = min(1.0, character.arc_progression + 0.1)
        character.updated_at = datetime.now()
        return character
    
    def create_conflict(self, characters: List[Character], setting: Setting) -> PlotPoint:
        """Create a conflict between characters"""
        if len(characters) < 2:
            raise ValueError("Need at least 2 characters for conflict")
        
        plot_point = PlotPoint(
            name="Conflict",
            description=f"Conflict between {characters[0].name} and {characters[1].name}",
            conflict_type="interpersonal",
            characters_involved=[c.id for c in characters[:2]],
            emotional_impact=EmotionalValence.NEGATIVE
        )
        
        return plot_point
    
    def resolve_conflict(self, conflict: PlotPoint, context: Dict[str, Any]) -> PlotPoint:
        """Resolve a conflict"""
        conflict.resolution = "Conflict resolved through dialogue"
        conflict.emotional_impact = EmotionalValence.POSITIVE
        conflict.updated_at = datetime.now()
        return conflict


class BasicDomainAdapter(DomainAdapter):
    """Basic implementation of domain adapter"""
    
    def adapt_narrative_element(self, element: NarrativeElement, domain: NarrativeDomain) -> NarrativeElement:
        """Basic adaptation of narrative elements"""
        # Create a copy of the element
        adapted_element = type(element)(
            id=element.id,
            name=element.name,
            description=element.description,
            tags=element.tags.copy(),
            metadata=element.metadata.copy()
        )
        
        # Add domain-specific tag
        adapted_element.tags.add(f"domain:{domain.value}")
        
        return adapted_element
    
    def get_domain_rules(self, domain: NarrativeDomain) -> Dict[str, Any]:
        """Get basic domain rules"""
        rules = {
            NarrativeDomain.GAMING: {
                "requires_conflict": True,
                "character_development": True,
                "world_building": True
            },
            NarrativeDomain.THERAPY: {
                "requires_conflict": False,
                "character_development": True,
                "emotional_safety": True
            },
            NarrativeDomain.EDUCATION: {
                "requires_conflict": False,
                "character_development": True,
                "learning_objectives": True
            }
        }
        
        return rules.get(domain, {})
    
    def validate_narrative(self, narrative: NarrativeArc, domain: NarrativeDomain) -> bool:
        """Basic narrative validation"""
        rules = self.get_domain_rules(domain)
        
        if rules.get("requires_conflict", False):
            has_conflicts = any(p.conflict_type for p in narrative.plot_points)
            if not has_conflicts:
                return False
        
        return True 