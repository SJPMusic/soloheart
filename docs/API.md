This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

# The Narrative Engine API Documentation

## Overview

The Narrative Engine provides a comprehensive API for creating, analyzing, and adapting narratives across multiple domains. This document covers the core API components and usage patterns.

## Core Components

### NarrativeEngine

The main orchestrator class that manages narratives, memory, and domain adapters.

```python
from core.narrative_engine import NarrativeEngine

engine = NarrativeEngine()
```

#### Methods

##### `create_narrative(title, description, domain, story_structure)`

Creates a new narrative with the specified parameters.

**Parameters:**
- `title` (str): The narrative title
- `description` (str): Narrative description
- `domain` (NarrativeDomain): The narrative domain (GAMING, THERAPY, EDUCATION, etc.)
- `story_structure` (StoryStructure): The story structure type

**Returns:** `Narrative` object

**Example:**
```python
narrative = engine.create_narrative(
    title="Epic Adventure",
    description="A hero's journey through mystical realms",
    domain=NarrativeDomain.GAMING,
    story_structure=StoryStructure.HERO_JOURNEY
)
```

##### `add_character(narrative_id, character_data)`

Adds a character to a narrative.

**Parameters:**
- `narrative_id` (str): The narrative ID
- `character_data` (dict): Character information

**Returns:** `Character` object

**Example:**
```python
character = engine.add_character(narrative.id, {
    'name': 'Aria',
    'role': CharacterRole.PROTAGONIST,
    'description': 'A brave warrior',
    'traits': ['brave', 'curious'],
    'goals': ['Save the world'],
    'conflicts': ['Internal struggle']
})
```

##### `generate_plot_point(narrative_id, context)`

Generates a plot point for a narrative.

**Parameters:**
- `narrative_id` (str): The narrative ID
- `context` (dict): Plot point context and parameters

**Returns:** `PlotPoint` object

**Example:**
```python
plot_point = engine.generate_plot_point(narrative.id, {
    'type': PlotPointType.INCITING_INCIDENT,
    'title': 'The Call to Adventure',
    'description': 'Hero receives a quest',
    'narrative_significance': 0.9,
    'thematic_elements': ['destiny', 'adventure']
})
```

##### `analyze_narrative(narrative_id)`

Analyzes a narrative for structure, coherence, and themes.

**Parameters:**
- `narrative_id` (str): The narrative ID

**Returns:** `NarrativeAnalysis` object

**Example:**
```python
analysis = engine.analyze_narrative(narrative.id)
print(f"Coherence: {analysis.coherence_score}")
print(f"Themes: {analysis.themes}")
```

##### `adapt_narrative(narrative_id, new_context)`

Adapts a narrative based on new context or requirements.

**Parameters:**
- `narrative_id` (str): The narrative ID
- `new_context` (dict): New context for adaptation

**Returns:** `Narrative` object

**Example:**
```python
adapted_narrative = engine.adapt_narrative(narrative.id, {
    'player_level': 5,
    'world_changes': {'dark_army_defeated': True}
})
```

##### `recall_narrative_context(query, domain, limit)`

Recalls narrative-related memories.

**Parameters:**
- `query` (str, optional): Search query
- `domain` (NarrativeDomain, optional): Domain filter
- `limit` (int): Maximum number of memories to return

**Returns:** List of `MemoryNode` objects

**Example:**
```python
memories = engine.recall_narrative_context(
    query="hero journey",
    domain=NarrativeDomain.GAMING,
    limit=10
)
```

##### `get_narrative_stats()`

Gets comprehensive statistics about all narratives.

**Returns:** Dictionary with statistics

**Example:**
```python
stats = engine.get_narrative_stats()
print(f"Total narratives: {stats['total_narratives']}")
print(f"Narratives by domain: {stats['narratives_by_domain']}")
```

##### `export_narrative(narrative_id)`

Exports a narrative with all its components.

**Parameters:**
- `narrative_id` (str): The narrative ID

**Returns:** Dictionary with export data

**Example:**
```python
export_data = engine.export_narrative(narrative.id)
# Save to file
with open('narrative_export.json', 'w') as f:
    json.dump(export_data, f, indent=2)
```

##### `import_narrative(export_data)`

Imports a narrative from export data.

**Parameters:**
- `export_data` (dict): Export data from `export_narrative`

**Returns:** Narrative ID

**Example:**
```python
with open('narrative_export.json', 'r') as f:
    export_data = json.load(f)
narrative_id = engine.import_narrative(export_data)
```

##### `register_domain_adapter(domain, adapter)`

Registers a domain-specific adapter.

**Parameters:**
- `domain` (NarrativeDomain): The domain
- `adapter` (DomainAdapter): The domain adapter

**Example:**
```python
from domains.gaming import GamingAdapter
gaming_adapter = GamingAdapter()
engine.register_domain_adapter(NarrativeDomain.GAMING, gaming_adapter)
```

## Data Structures

### Narrative

Represents a complete narrative with all its components.

**Attributes:**
- `id` (str): Unique identifier
- `title` (str): Narrative title
- `description` (str): Narrative description
- `domain` (NarrativeDomain): Narrative domain
- `story_structure` (StoryStructure): Story structure type
- `characters` (dict): Character dictionary
- `plot_points` (dict): Plot point dictionary
- `themes` (list): Narrative themes
- `world_state` (dict): World state information
- `narrative_arc` (list): Plot point IDs in order
- `metadata` (dict): Additional metadata
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

### Character

Represents a character in the narrative.

**Attributes:**
- `id` (str): Unique identifier
- `name` (str): Character name
- `role` (CharacterRole): Character role
- `description` (str): Character description
- `traits` (list): Character traits
- `goals` (list): Character goals
- `conflicts` (list): Character conflicts
- `relationships` (dict): Character relationships
- `development_arc` (list): Development moments
- `current_state` (dict): Current character state
- `background` (dict): Character background
- `personality_matrix` (dict): Personality traits

### PlotPoint

Represents a plot point in the narrative.

**Attributes:**
- `id` (str): Unique identifier
- `plot_point_type` (PlotPointType): Type of plot point
- `title` (str): Plot point title
- `description` (str): Plot point description
- `characters_involved` (list): Involved character IDs
- `emotional_impact` (dict): Emotional impact on characters
- `narrative_significance` (float): Significance score (0.0-1.0)
- `thematic_elements` (list): Thematic elements
- `world_state_changes` (dict): World state changes
- `timestamp` (datetime): Creation timestamp
- `prerequisites` (list): Prerequisite plot point IDs
- `consequences` (list): Consequent plot point IDs

### NarrativeAnalysis

Results of narrative analysis.

**Attributes:**
- `coherence_score` (float): Narrative coherence (0.0-1.0)
- `thematic_consistency` (float): Thematic consistency (0.0-1.0)
- `character_development` (dict): Character development scores
- `plot_complexity` (float): Plot complexity score
- `emotional_arc` (dict): Emotional arcs for characters
- `pacing_analysis` (dict): Pacing analysis results
- `structural_integrity` (float): Structural integrity score
- `themes` (list): Identified themes
- `motifs` (list): Identified motifs
- `conflicts` (list): Conflict analysis
- `recommendations` (list): Improvement recommendations

## Enums

### NarrativeDomain

Available narrative domains:
- `GAMING`: Gaming narratives
- `THERAPY`: Therapeutic narratives
- `EDUCATION`: Educational narratives
- `ORGANIZATIONAL`: Organizational narratives
- `CREATIVE_WRITING`: Creative writing
- `JOURNALISM`: Journalistic narratives
- `MARKETING`: Marketing narratives

### StoryStructure

Available story structures:
- `HERO_JOURNEY`: Hero's journey structure
- `THREE_ACT`: Three-act structure
- `FIVE_ACT`: Five-act structure
- `CIRCULAR`: Circular structure
- `EPISODIC`: Episodic structure
- `FRAME`: Frame narrative
- `PARALLEL`: Parallel narratives
- `IN_MEDIA_RES`: In medias res

### CharacterRole

Available character roles:
- `PROTAGONIST`: Main character
- `ANTAGONIST`: Opposing character
- `SUPPORTING`: Supporting character
- `MENTOR`: Mentor character
- `FOIL`: Foil character
- `LOVE_INTEREST`: Love interest
- `COMIC_RELIEF`: Comic relief
- `CATALYST`: Catalyst character

### PlotPointType

Available plot point types:
- `INCITING_INCIDENT`: Inciting incident
- `FIRST_TURNING_POINT`: First turning point
- `MIDPOINT`: Midpoint
- `SECOND_TURNING_POINT`: Second turning point
- `CLIMAX`: Climax
- `RESOLUTION`: Resolution
- `SUBPLOT`: Subplot
- `CHARACTER_DEVELOPMENT`: Character development

## Memory System

### LayeredMemorySystem

The memory system provides layered memory storage with emotional context.

**Methods:**

##### `add_memory(content, memory_type, layer, user_id, session_id, ...)`

Adds a memory to the system.

**Example:**
```python
memory_id = engine.memory_system.add_memory(
    content={'event': 'Character creation', 'character': 'Aria'},
    memory_type=MemoryType.CHARACTER_DEVELOPMENT,
    layer=MemoryLayer.MID_TERM,
    user_id='user123',
    session_id='session456',
    emotional_weight=0.7,
    emotional_context=[EmotionalContext.JOY],
    thematic_tags=['character_creation', 'gaming']
)
```

##### `recall(query, emotional, thematic, user_id, layer, min_significance, limit)`

Recalls memories based on various criteria.

**Example:**
```python
memories = engine.memory_system.recall(
    query="hero journey",
    emotional=EmotionalContext.JOY,
    thematic=['gaming'],
    limit=10
)
```

##### `get_memory_stats()`

Gets memory system statistics.

**Example:**
```python
stats = engine.memory_system.get_memory_stats()
print(f"Total memories: {stats['created']}")
print(f"Short-term: {stats['short_term_count']}")
print(f"Mid-term: {stats['mid_term_count']}")
print(f"Long-term: {stats['long_term_count']}")
```

## Domain Adapters

### Creating Custom Domain Adapters

To create a custom domain adapter, inherit from `DomainAdapter`:

```python
from core.narrative_engine import DomainAdapter, NarrativeDomain, Narrative, NarrativeAnalysis

class CustomAdapter(DomainAdapter):
    def __init__(self):
        super().__init__(NarrativeDomain.CUSTOM)
    
    def analyze_narrative(self, narrative: Narrative) -> NarrativeAnalysis:
        # Implement domain-specific analysis
        pass
    
    def generate_plot_point(self, narrative: Narrative, context: Dict[str, Any]) -> PlotPoint:
        # Implement domain-specific plot point generation
        pass
    
    def adapt_narrative(self, narrative: Narrative, new_context: Dict[str, Any]) -> Narrative:
        # Implement domain-specific adaptation
        pass
```

## Error Handling

The Narrative Engine uses standard Python exceptions:

- `ValueError`: Invalid parameters or data
- `KeyError`: Missing keys in dictionaries
- `TypeError`: Incorrect data types

**Example:**
```python
try:
    narrative = engine.create_narrative(
        title="Test",
        description="Test narrative",
        domain=NarrativeDomain.GAMING
    )
except ValueError as e:
    print(f"Error creating narrative: {e}")
```

## Best Practices

1. **Always check return values** for None or empty results
2. **Use appropriate memory layers** for different types of information
3. **Provide rich context** when generating plot points
4. **Regularly analyze narratives** to maintain quality
5. **Export important narratives** for backup and sharing
6. **Use domain adapters** for specialized functionality
7. **Monitor memory statistics** to prevent memory bloat

## Performance Considerations

- Large narratives may impact analysis performance
- Memory system can grow large over time; use `forget()` method
- Export/import operations can be memory-intensive
- Consider caching analysis results for frequently accessed narratives 