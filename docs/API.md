This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

# The Narrative Engine API Documentation

## Overview

The Narrative Engine provides a domain-agnostic memory and context system for narrative continuity across multiple applications. This document covers the core API components and usage patterns for the current implementation.

## Core Components

### NarrativeEngine

The main orchestrator class that manages characters, memory, and context without domain-specific logic.

```python
from narrative_core.narrative_engine import NarrativeEngine

engine = NarrativeEngine(campaign_name="test_campaign")
```

#### Methods

##### `add_character(character_data)`

Adds a character to the narrative without domain-specific filtering.

**Parameters:**
- `character_data` (dict): Character information (any structure accepted)

**Returns:** Character ID (str)

**Example:**
```python
character_id = engine.add_character({
    'id': 'char_123',
    'name': 'Aria',
    'description': 'A brave warrior',
    'traits': ['brave', 'curious'],
    'goals': ['Save the world'],
    'conflicts': ['Internal struggle'],
    'current_state': {
        'race': 'Human',
        'class': 'Fighter',
        'level': 5,
        'hit_points': 45
    }
})
```

##### `get_character_by_name(name)`

Retrieves a character by name.

**Parameters:**
- `name` (str): Character name

**Returns:** Character object or None

**Example:**
```python
character = engine.get_character_by_name("Aria")
if character:
    print(f"Found character: {character.name}")
```

##### `update_character_state(name, new_state)`

Updates a character's current state.

**Parameters:**
- `name` (str): Character name
- `new_state` (dict): New state data

**Example:**
```python
engine.update_character_state("Aria", {
    'hit_points': 40,
    'inspiration_points': 2,
    'saving_throws': {'dexterity': 2, 'wisdom': 1}
})
```

##### `get_context_for_llm(character_name)`

Provides narrative context to LLM for character interactions.

**Parameters:**
- `character_name` (str): Character name

**Returns:** Context string for LLM

**Example:**
```python
context = engine.get_context_for_llm("Aria")
# Use context in LLM prompt
```

##### `add_memory(memory_data)`

Adds a memory to the narrative system.

**Parameters:**
- `memory_data` (dict): Memory information

**Returns:** Memory ID (str)

**Example:**
```python
memory_id = engine.add_memory({
    'type': 'episodic',
    'content': 'Aria defeated the dragon',
    'emotional_weight': 0.8,
    'character_connections': ['Aria']
})
```

##### `get_memories(query=None, limit=10)`

Retrieves memories based on query.

**Parameters:**
- `query` (str, optional): Search query
- `limit` (int): Maximum number of memories

**Returns:** List of memory objects

**Example:**
```python
memories = engine.get_memories(query="dragon", limit=5)
```

##### `save_campaign()`

Saves the current campaign state.

**Example:**
```python
engine.save_campaign()
```

##### `load_campaign(campaign_name)`

Loads a campaign state.

**Parameters:**
- `campaign_name` (str): Campaign name

**Example:**
```python
engine.load_campaign("test_campaign")
```

## SoloHeart Integration Layer

### SoloHeartNarrativeEngine

The integration layer that provides game-specific features while maintaining domain-agnostic core.

```python
from solo_heart.narrative_engine_integration import SoloHeartNarrativeEngine

integration = SoloHeartNarrativeEngine(campaign_name="test_campaign")
```

#### Methods

##### `record_character_creation(character_data)`

Records character creation with proper field separation.

**Parameters:**
- `character_data` (dict): Character data from character creation

**Returns:** Character ID (str)

**Example:**
```python
char_id = integration.record_character_creation({
    'name': 'Thorin',
    'race': 'Human',
    'class': 'Fighter',
    'level': 1,
    'hit_points': 12,
    'inspiration_points': 0
})
```

##### `record_character_facts(facts, character_name)`

Records additional character facts.

**Parameters:**
- `facts` (dict): Character facts
- `character_name` (str): Character name

**Returns:** Success status

**Example:**
```python
integration.record_character_facts({
    'combat_style': 'Sword and shield',
    'motivations': ['Revenge', 'Justice']
}, "Thorin")
```

##### `set_inspiration_points(character_name, points)`

Sets inspiration points for a character.

**Parameters:**
- `character_name` (str): Character name
- `points` (int): Number of inspiration points

**Example:**
```python
integration.set_inspiration_points("Thorin", 2)
```

##### `get_inspiration_points(character_name)`

Gets inspiration points for a character.

**Parameters:**
- `character_name` (str): Character name

**Returns:** Number of inspiration points (int)

**Example:**
```python
points = integration.get_inspiration_points("Thorin")
print(f"Thorin has {points} inspiration points")
```

##### `set_saving_throws(character_name, saving_throws)`

Sets saving throw modifiers for a character.

**Parameters:**
- `character_name` (str): Character name
- `saving_throws` (dict): Saving throw modifiers

**Example:**
```python
saving_throws = {
    'dexterity': 2,
    'wisdom': 1,
    'constitution': 3
}
integration.set_saving_throws("Thorin", saving_throws)
```

##### `get_saving_throws(character_name)`

Gets saving throw modifiers for a character.

**Parameters:**
- `character_name` (str): Character name

**Returns:** Dictionary of saving throw modifiers

**Example:**
```python
throws = integration.get_saving_throws("Thorin")
print(f"Thorin's saving throws: {throws}")
```

## Character Data Structure

### Universal Fields (Top Level)

These fields are stored at the top level of the Character dataclass:

```python
CHARACTER_FIELDS = {
    'id', 'name', 'description', 'traits', 'goals', 'conflicts', 
    'relationships', 'development_arc', 'current_state', 'background',
    'personality_matrix', 'emotional_state', 'memory_ids', 'last_updated'
}
```

### Domain-Specific Fields (current_state)

These fields are stored in the `current_state` dictionary:

```python
domain_specific_fields = [
    'race', 'class', 'background', 'alignment', 'age', 'gender',
    'level', 'hit_points', 'armor_class', 'initiative', 'experience',
    'combat_style', 'gear', 'spells', 'abilities', 'skills',
    'personality_traits', 'motivations', 'emotional_themes', 'traumas',
    'relational_history', 'backstory', 'inspiration_points', 'saving_throws'
]
```

## Memory System

### Memory Types

The Narrative Engine supports multiple memory layers:

1. **Episodic Memory**: Specific events and experiences
2. **Semantic Memory**: Facts and knowledge
3. **Procedural Memory**: Skills and procedures
4. **Emotional Memory**: Emotional context and reactions

### Memory Structure

```python
{
    'id': 'mem_123',
    'type': 'episodic',  # episodic, semantic, procedural, emotional
    'content': 'Memory content',
    'emotional_weight': 0.8,
    'character_connections': ['character_name'],
    'timestamp': '2025-07-05T10:30:00',
    'tags': ['combat', 'victory']
}
```

## Usage Examples

### Basic Character Creation

```python
from solo_heart.narrative_engine_integration import SoloHeartNarrativeEngine

# Initialize integration
integration = SoloHeartNarrativeEngine("test_campaign")

# Create character
char_data = {
    'name': 'Thorin',
    'race': 'Human',
    'class': 'Fighter',
    'level': 1,
    'hit_points': 12,
    'inspiration_points': 0,
    'motivations': ['Revenge', 'Justice'],
    'traits': ['Brave', 'Loyal']
}

char_id = integration.record_character_creation(char_data)
```

### Managing Game State

```python
# Set inspiration points
integration.set_inspiration_points("Thorin", 2)

# Set saving throws
saving_throws = {
    'dexterity': 2,
    'wisdom': 1,
    'constitution': 3
}
integration.set_saving_throws("Thorin", saving_throws)

# Get current state
points = integration.get_inspiration_points("Thorin")
throws = integration.get_saving_throws("Thorin")
```

### Memory Management

```python
from narrative_core.narrative_engine import NarrativeEngine

engine = NarrativeEngine("test_campaign")

# Add memory
memory_data = {
    'type': 'episodic',
    'content': 'Thorin defeated the bandit leader',
    'emotional_weight': 0.9,
    'character_connections': ['Thorin'],
    'tags': ['combat', 'victory', 'revenge']
}

memory_id = engine.add_memory(memory_data)

# Retrieve memories
memories = engine.get_memories(query="combat", limit=5)
```

## Error Handling

### Common Errors

1. **Character Not Found**
```python
try:
    points = integration.get_inspiration_points("Unknown")
except Exception as e:
    print(f"Character not found: {e}")
```

2. **Invalid Data Structure**
```python
try:
    char_id = engine.add_character(invalid_data)
except Exception as e:
    print(f"Invalid data: {e}")
```

## Best Practices

1. **Domain Separation**: Always use the integration layer for game-specific features
2. **Memory Management**: Use appropriate memory types for different information
3. **Error Handling**: Always handle potential errors gracefully
4. **State Consistency**: Ensure character state is updated atomically
5. **Context Provision**: Use `get_context_for_llm()` for LLM interactions

## Architecture Notes

- **Domain-Agnostic Core**: The Narrative Engine core contains no game-specific logic
- **Integration Layer**: Game-specific features are implemented in the integration layer
- **Memory Layers**: Multiple memory types support rich narrative context
- **State Encapsulation**: All game-specific data is stored in `current_state`
- **Clean Separation**: Universal metadata vs domain-specific state properly separated 