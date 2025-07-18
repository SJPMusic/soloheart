"""
Gaming Domain Adapter - The Narrative Engine
===========================================

Specialized adapter for gaming narratives, providing:
- Quest system integration
- Character progression tracking
- Combat and conflict resolution
- World-building and lore management
- Player agency and choice modeling
"""

from typing import Dict, List, Any
from core.narrative_engine import DomainAdapter, NarrativeDomain, Narrative, NarrativeAnalysis, PlotPoint, PlotPointType
from core.memory_system import MemoryType, MemoryLayer, EmotionalContext
import logging

logger = logging.getLogger(__name__)

class GamingAdapter(DomainAdapter):
    """Domain adapter for gaming narratives with specialized gaming features."""
    
    def __init__(self):
        super().__init__(NarrativeDomain.GAMING)
        self.quest_templates = self._load_quest_templates()
        self.combat_patterns = self._load_combat_patterns()
        self.world_building_elements = self._load_world_building_elements()
    
    def analyze_narrative(self, narrative: Narrative) -> NarrativeAnalysis:
        """Analyze gaming narrative with domain-specific metrics."""
        # Calculate gaming-specific coherence
        coherence_score = self._calculate_gaming_coherence(narrative)
        
        # Analyze character progression
        character_development = self._analyze_character_progression(narrative)
        
        # Calculate quest complexity
        quest_complexity = self._calculate_quest_complexity(narrative)
        
        # Analyze combat and conflict patterns
        conflict_analysis = self._analyze_conflict_patterns(narrative)
        
        # Extract gaming themes
        gaming_themes = self._extract_gaming_themes(narrative)
        
        # Analyze player agency
        player_agency_score = self._analyze_player_agency(narrative)
        
        analysis = NarrativeAnalysis(
            coherence_score=coherence_score,
            thematic_consistency=self._calculate_thematic_consistency(narrative),
            character_development=character_development,
            plot_complexity=quest_complexity,
            emotional_arc=self._analyze_emotional_arcs(narrative),
            pacing_analysis=self._analyze_gaming_pacing(narrative),
            structural_integrity=self._calculate_structural_integrity(narrative),
            themes=gaming_themes,
            motifs=self._extract_gaming_motifs(narrative),
            conflicts=conflict_analysis,
            recommendations=self._generate_gaming_recommendations(narrative, player_agency_score)
        )
        
        return analysis
    
    def generate_plot_point(self, narrative: Narrative, context: Dict[str, Any]) -> PlotPoint:
        """Generate gaming-appropriate plot point."""
        plot_type = context.get('type', PlotPointType.SUBPLOT)
        
        if plot_type == PlotPointType.INCITING_INCIDENT:
            return self._generate_quest_hook(narrative, context)
        elif plot_type == PlotPointType.CLIMAX:
            return self._generate_boss_battle(narrative, context)
        elif plot_type == PlotPointType.CHARACTER_DEVELOPMENT:
            return self._generate_character_moment(narrative, context)
        else:
            return self._generate_general_plot_point(narrative, context)
    
    def adapt_narrative(self, narrative: Narrative, new_context: Dict[str, Any]) -> Narrative:
        """Adapt gaming narrative based on player choices or game state."""
        adapted_narrative = narrative
        
        # Adapt based on player level/experience
        if 'player_level' in new_context:
            adapted_narrative = self._adapt_for_player_level(adapted_narrative, new_context['player_level'])
        
        # Adapt based on player choices
        if 'player_choices' in new_context:
            adapted_narrative = self._adapt_for_player_choices(adapted_narrative, new_context['player_choices'])
        
        # Adapt based on world state changes
        if 'world_changes' in new_context:
            adapted_narrative.world_state.update(new_context['world_changes'])
        
        return adapted_narrative
    
    def _calculate_gaming_coherence(self, narrative: Narrative) -> float:
        """Calculate coherence specific to gaming narratives."""
        coherence_factors = []
        
        # Quest chain coherence
        quest_coherence = self._analyze_quest_chain_coherence(narrative)
        coherence_factors.append(quest_coherence)
        
        # Character motivation coherence
        motivation_coherence = self._analyze_character_motivations(narrative)
        coherence_factors.append(motivation_coherence)
        
        # World consistency
        world_coherence = self._analyze_world_consistency(narrative)
        coherence_factors.append(world_coherence)
        
        return sum(coherence_factors) / len(coherence_factors)
    
    def _analyze_character_progression(self, narrative: Narrative) -> Dict[str, float]:
        """Analyze character progression in gaming context."""
        progression_scores = {}
        
        for character in narrative.characters.values():
            # Calculate progression based on development arc length
            arc_length = len(character.development_arc)
            
            # Calculate progression based on goal completion
            goal_progress = self._calculate_goal_progress(character, narrative)
            
            # Calculate progression based on relationship development
            relationship_progress = len(character.relationships) / max(len(narrative.characters) - 1, 1)
            
            # Combine factors
            progression_score = (arc_length * 0.3 + goal_progress * 0.4 + relationship_progress * 0.3)
            progression_scores[character.id] = min(progression_score, 1.0)
        
        return progression_scores
    
    def _calculate_quest_complexity(self, narrative: Narrative) -> float:
        """Calculate quest complexity for gaming narratives."""
        if not narrative.plot_points:
            return 0.0
        
        complexity_factors = []
        
        for plot_point in narrative.plot_points.values():
            # Factor in narrative significance
            complexity_factors.append(plot_point.narrative_significance)
            
            # Factor in number of characters involved
            char_complexity = len(plot_point.characters_involved) / max(len(narrative.characters), 1)
            complexity_factors.append(char_complexity)
            
            # Factor in world state changes
            world_complexity = len(plot_point.world_state_changes) / 10.0  # Normalize
            complexity_factors.append(world_complexity)
        
        return sum(complexity_factors) / len(complexity_factors)
    
    def _analyze_conflict_patterns(self, narrative: Narrative) -> List[Dict[str, Any]]:
        """Analyze conflict patterns in gaming narrative."""
        conflicts = []
        
        for plot_point in narrative.plot_points.values():
            if plot_point.plot_point_type in [PlotPointType.CLIMAX, PlotPointType.FIRST_TURNING_POINT]:
                conflict = {
                    'type': 'major_conflict',
                    'plot_point_id': plot_point.id,
                    'characters_involved': plot_point.characters_involved,
                    'thematic_elements': plot_point.thematic_elements,
                    'resolution_status': 'unresolved' if plot_point.plot_point_type == PlotPointType.CLIMAX else 'resolved'
                }
                conflicts.append(conflict)
        
        return conflicts
    
    def _extract_gaming_themes(self, narrative: Narrative) -> List[str]:
        """Extract gaming-specific themes."""
        gaming_themes = set()
        
        # Common gaming themes
        common_gaming_themes = [
            'heroism', 'quest', 'adventure', 'power', 'destiny', 'choice',
            'sacrifice', 'redemption', 'betrayal', 'loyalty', 'growth',
            'challenge', 'overcoming_obstacles', 'friendship', 'love'
        ]
        
        # Check plot points for these themes
        for plot_point in narrative.plot_points.values():
            for theme in plot_point.thematic_elements:
                if theme in common_gaming_themes:
                    gaming_themes.add(theme)
        
        # Add themes from character goals
        for character in narrative.characters.values():
            for goal in character.goals:
                if any(theme in goal.lower() for theme in common_gaming_themes):
                    for theme in common_gaming_themes:
                        if theme in goal.lower():
                            gaming_themes.add(theme)
        
        return list(gaming_themes)
    
    def _analyze_player_agency(self, narrative: Narrative) -> float:
        """Analyze player agency in the narrative."""
        agency_factors = []
        
        # Check for multiple plot paths
        plot_paths = self._count_plot_paths(narrative)
        agency_factors.append(min(plot_paths / 5.0, 1.0))  # Normalize to 0-1
        
        # Check for character choice moments
        choice_moments = self._count_choice_moments(narrative)
        agency_factors.append(min(choice_moments / 10.0, 1.0))
        
        # Check for branching consequences
        branching_factor = self._calculate_branching_factor(narrative)
        agency_factors.append(branching_factor)
        
        return sum(agency_factors) / len(agency_factors)
    
    def _generate_quest_hook(self, narrative: Narrative, context: Dict[str, Any]) -> PlotPoint:
        """Generate a quest hook plot point."""
        return PlotPoint(
            id=None,
            plot_point_type=PlotPointType.INCITING_INCIDENT,
            title=context.get('title', 'The Call to Adventure'),
            description=context.get('description', 'A mysterious quest appears that will change everything'),
            characters_involved=context.get('characters_involved', []),
            emotional_impact=context.get('emotional_impact', {}),
            narrative_significance=0.9,
            thematic_elements=['quest', 'adventure', 'destiny'],
            world_state_changes={'quest_active': True},
            timestamp=None,
            prerequisites=[],
            consequences=[]
        )
    
    def _generate_boss_battle(self, narrative: Narrative, context: Dict[str, Any]) -> PlotPoint:
        """Generate a boss battle plot point."""
        return PlotPoint(
            id=None,
            plot_point_type=PlotPointType.CLIMAX,
            title=context.get('title', 'The Final Battle'),
            description=context.get('description', 'The ultimate confrontation with the main antagonist'),
            characters_involved=context.get('characters_involved', []),
            emotional_impact=context.get('emotional_impact', {}),
            narrative_significance=1.0,
            thematic_elements=['conflict', 'resolution', 'victory'],
            world_state_changes={'final_battle_complete': True},
            timestamp=None,
            prerequisites=[],
            consequences=[]
        )
    
    def _generate_character_moment(self, narrative: Narrative, context: Dict[str, Any]) -> PlotPoint:
        """Generate a character development moment."""
        return PlotPoint(
            id=None,
            plot_point_type=PlotPointType.CHARACTER_DEVELOPMENT,
            title=context.get('title', 'Character Growth'),
            description=context.get('description', 'A moment of significant character development'),
            characters_involved=context.get('characters_involved', []),
            emotional_impact=context.get('emotional_impact', {}),
            narrative_significance=0.7,
            thematic_elements=['growth', 'development', 'change'],
            world_state_changes={},
            timestamp=None,
            prerequisites=[],
            consequences=[]
        )
    
    def _generate_general_plot_point(self, narrative: Narrative, context: Dict[str, Any]) -> PlotPoint:
        """Generate a general gaming plot point."""
        return PlotPoint(
            id=None,
            plot_point_type=context.get('type', PlotPointType.SUBPLOT),
            title=context.get('title', 'Gaming Event'),
            description=context.get('description', 'A significant event in the gaming narrative'),
            characters_involved=context.get('characters_involved', []),
            emotional_impact=context.get('emotional_impact', {}),
            narrative_significance=context.get('narrative_significance', 0.5),
            thematic_elements=context.get('thematic_elements', []),
            world_state_changes=context.get('world_state_changes', {}),
            timestamp=None,
            prerequisites=context.get('prerequisites', []),
            consequences=context.get('consequences', [])
        )
    
    def _load_quest_templates(self) -> Dict[str, Any]:
        """Load quest templates for gaming narratives."""
        return {
            'rescue_quest': {
                'title': 'Rescue Mission',
                'description': 'Save someone in danger',
                'themes': ['heroism', 'sacrifice', 'urgency']
            },
            'collection_quest': {
                'title': 'Gather Artifacts',
                'description': 'Collect important items',
                'themes': ['exploration', 'discovery', 'persistence']
            },
            'elimination_quest': {
                'title': 'Defeat Enemies',
                'description': 'Eliminate threats',
                'themes': ['conflict', 'power', 'justice']
            }
        }
    
    def _load_combat_patterns(self) -> Dict[str, Any]:
        """Load combat patterns for gaming narratives."""
        return {
            'boss_battle': {
                'structure': ['setup', 'confrontation', 'climax', 'resolution'],
                'themes': ['power', 'strategy', 'determination']
            },
            'group_combat': {
                'structure': ['formation', 'engagement', 'coordination', 'victory'],
                'themes': ['teamwork', 'cooperation', 'unity']
            }
        }
    
    def _load_world_building_elements(self) -> Dict[str, Any]:
        """Load world building elements for gaming narratives."""
        return {
            'locations': ['dungeon', 'castle', 'forest', 'village', 'city'],
            'factions': ['nobles', 'merchants', 'wizards', 'warriors', 'rogues'],
            'conflicts': ['political', 'religious', 'economic', 'personal']
        }
    
    # Helper methods for analysis
    def _analyze_quest_chain_coherence(self, narrative: Narrative) -> float:
        """Analyze coherence of quest chains."""
        # Simplified implementation
        return 0.8
    
    def _analyze_character_motivations(self, narrative: Narrative) -> float:
        """Analyze character motivation coherence."""
        # Simplified implementation
        return 0.7
    
    def _analyze_world_consistency(self, narrative: Narrative) -> float:
        """Analyze world consistency."""
        # Simplified implementation
        return 0.9
    
    def _calculate_goal_progress(self, character, narrative: Narrative) -> float:
        """Calculate character goal progress."""
        # Simplified implementation
        return 0.6
    
    def _analyze_emotional_arcs(self, narrative: Narrative) -> Dict[str, List[float]]:
        """Analyze emotional arcs for characters."""
        emotional_arcs = {}
        for character in narrative.characters.values():
            emotional_arcs[character.id] = [0.5] * len(narrative.plot_points)
        return emotional_arcs
    
    def _analyze_gaming_pacing(self, narrative: Narrative) -> Dict[str, Any]:
        """Analyze gaming-specific pacing."""
        return {
            'overall_pacing': 'moderate',
            'action_sequences': len([p for p in narrative.plot_points.values() if p.plot_point_type == PlotPointType.CLIMAX]),
            'downtime_moments': len([p for p in narrative.plot_points.values() if p.plot_point_type == PlotPointType.CHARACTER_DEVELOPMENT])
        }
    
    def _calculate_structural_integrity(self, narrative: Narrative) -> float:
        """Calculate structural integrity for gaming narratives."""
        # Simplified implementation
        return 0.8
    
    def _extract_gaming_motifs(self, narrative: Narrative) -> List[str]:
        """Extract gaming-specific motifs."""
        return ['quest', 'adventure', 'power']
    
    def _generate_gaming_recommendations(self, narrative: Narrative, player_agency_score: float) -> List[str]:
        """Generate gaming-specific recommendations."""
        recommendations = []
        
        if player_agency_score < 0.5:
            recommendations.append("Consider adding more player choice moments")
        
        if len(narrative.plot_points) < 3:
            recommendations.append("Add more plot points to create a richer narrative")
        
        if len(narrative.characters) < 2:
            recommendations.append("Consider adding supporting characters for richer interactions")
        
        return recommendations
    
    def _count_plot_paths(self, narrative: Narrative) -> int:
        """Count available plot paths."""
        # Simplified implementation
        return len(narrative.plot_points)
    
    def _count_choice_moments(self, narrative: Narrative) -> int:
        """Count character choice moments."""
        # Simplified implementation
        return len([p for p in narrative.plot_points.values() if p.plot_point_type == PlotPointType.CHARACTER_DEVELOPMENT])
    
    def _calculate_branching_factor(self, narrative: Narrative) -> float:
        """Calculate narrative branching factor."""
        # Simplified implementation
        return 0.6
    
    def _calculate_thematic_consistency(self, narrative: Narrative) -> float:
        """Calculate thematic consistency."""
        # Simplified implementation
        return 0.7
    
    def _adapt_for_player_level(self, narrative: Narrative, player_level: int) -> Narrative:
        """Adapt narrative for player level."""
        # Simplified implementation
        return narrative
    
    def _adapt_for_player_choices(self, narrative: Narrative, player_choices: List[str]) -> Narrative:
        """Adapt narrative for player choices."""
        # Simplified implementation
        return narrative 