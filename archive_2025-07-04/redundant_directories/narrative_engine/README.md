This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

# The Narrative Engine

A domain-agnostic storytelling framework with layered memory, context modeling, symbolic meaning analysis, and narrative continuity management.

## Overview

The Narrative Engine is a sophisticated AI-powered storytelling system designed to create immersive, emotionally consistent narratives across multiple domains. Unlike traditional generative AI systems, The Narrative Engine emphasizes interpretive storytelling where the user is a co-author, memory is treated as sacred, emotional realism shapes character behavior, and symbolic meaning adds psychological depth.

## Core Features

- **Layered Memory System**: Multi-tiered memory architecture with semantic, episodic, and procedural layers
- **Emotional Context Tracking**: NPCs remember and respond to emotional contexts
- **Symbolic Meaning Framework**: Archetypal analysis and chaos/order tension tracking inspired by Jordan B. Peterson's *Maps of Meaning*
- **Contextual Continuity**: Stories evolve based on established narrative threads and character relationships
- **Multi-Domain Support**: Works for gaming, therapy, education, and creative fiction
- **World State Simulation**: Persistent world state that evolves consistently
- **Enhanced Character Creation**: Immediate fact commitment with robust extraction and symbolic tagging

## Installation

```bash
# Install from the narrative_engine directory
cd narrative_engine
pip install -e .

# Or install with optional dependencies
pip install -e .[vector,web,cache]

# For development
pip install -e .[dev]
```

## Quick Start

```python
from narrative_engine.core.narrative_engine import NarrativeEngine
from narrative_engine.memory.layered_memory import LayeredMemorySystem
from narrative_engine.utils.symbolic_meaning_framework import SymbolicMeaningFramework

# Initialize the engine
engine = NarrativeEngine(
    campaign_id="my_story",
    domain="fiction"  # or "therapy", "education", "gaming"
)

# Create a memory system
memory = LayeredMemorySystem(campaign_id="my_story")

# Initialize symbolic meaning framework
symbolic_framework = SymbolicMeaningFramework()

# Store a memory with emotional and symbolic context
memory.store_memory(
    content="The protagonist helped a wounded traveler",
    memory_type="episodic",
    emotional_context={
        "valence": 0.8,  # Positive
        "arousal": 0.6,  # Moderate excitement
        "dominance": 0.7  # Protagonist felt in control
    },
    symbolic_context={
        "archetypal_tags": ["MENTOR", "SACRIFICE"],
        "chaos_order_impact": -0.2,  # Order-increasing
        "symbolic_coherence": 0.9
    },
    tags=["helping", "traveler", "kindness"]
)

# Generate narrative content with symbolic analysis
response = engine.generate_narration(
    situation="The protagonist enters a village",
    context="Previous kindness remembered by villagers",
    symbolic_state=symbolic_framework.get_symbolic_summary()
)

print(response)
```

## Enhanced Character Creation

```python
from narrative_engine.utils.character_fact_extraction import extract_all_facts_from_text
from narrative_engine.utils.symbolic_meaning_framework import SymbolicMeaningFramework

# Initialize symbolic framework
symbolic_framework = SymbolicMeaningFramework()

# Extract facts from natural language description
character_description = "John is a 19-year-old human fighter seeking revenge for his parents' murder"
facts = extract_all_facts_from_text(character_description, symbolic_framework)

# Facts are immediately committed with symbolic analysis
print(f"Extracted facts: {facts}")
print(f"Symbolic state: {symbolic_framework.get_symbolic_summary()}")
```

## Supported Environments

- **Creative Writing**: Interactive storytelling with persistent character development and symbolic meaning
- **Therapeutic Journaling**: Emotional processing with memory continuity and archetypal analysis
- **Educational Simulations**: Historical scenarios with adaptive responses and psychological depth
- **Gaming**: AI-driven narrative experiences with emotional depth and symbolic coherence

## Symbolic Meaning Framework

The Narrative Engine includes a sophisticated symbolic meaning framework inspired by Jordan B. Peterson's *Maps of Meaning*:

- **Archetypal Tagging**: 20+ Jungian archetypes (Father, Shadow, Journey, etc.)
- **Chaos/Order Tension**: Dynamic tracking of narrative stability
- **Narrative Decay**: Detection of contradictions and avoidance patterns
- **Symbolic Coherence**: Ensures meaningful character development
- **Psychological Profiling**: Deep analysis of character psychology and motivations

## Dependencies

### Required
- `openai>=1.0.0` - OpenAI API integration
- `numpy>=1.21.0` - Numerical computations
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=0.19.0` - Environment management

### Optional
- `faiss-cpu>=1.7.0` - Vector similarity search (for enhanced memory)
- `flask>=2.0.0` - Web interface support
- `redis>=4.0.0` - Caching and session storage

## License

MIT License - See LICENSE file for details.

## Contributing

This is an enhanced alpha release with symbolic meaning framework. For questions or contributions, please refer to the main project documentation.
