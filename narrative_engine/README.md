This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

# The Narrative Engine

A domain-agnostic storytelling framework with layered memory, context modeling, and narrative continuity management.

## Overview

The Narrative Engine is a sophisticated AI-powered storytelling system designed to create immersive, emotionally consistent narratives across multiple domains. Unlike traditional generative AI systems, The Narrative Engine emphasizes interpretive storytelling where the user is a co-author, memory is treated as sacred, and emotional realism shapes character behavior.

## Core Features

- **Layered Memory System**: Multi-tiered memory architecture with semantic, episodic, and procedural layers
- **Emotional Context Tracking**: NPCs remember and respond to emotional contexts
- **Contextual Continuity**: Stories evolve based on established narrative threads and character relationships
- **Multi-Domain Support**: Works for gaming, therapy, education, and creative fiction
- **World State Simulation**: Persistent world state that evolves consistently

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

# Initialize the engine
engine = NarrativeEngine(
    campaign_id="my_story",
    domain="fiction"  # or "therapy", "education", "gaming"
)

# Create a memory system
memory = LayeredMemorySystem(campaign_id="my_story")

# Store a memory with emotional context
memory.store_memory(
    content="The protagonist helped a wounded traveler",
    memory_type="episodic",
    emotional_context={
        "valence": 0.8,  # Positive
        "arousal": 0.6,  # Moderate excitement
        "dominance": 0.7  # Protagonist felt in control
    },
    tags=["helping", "traveler", "kindness"]
)

# Generate narrative content
response = engine.generate_narration(
    situation="The protagonist enters a village",
    context="Previous kindness remembered by villagers"
)

print(response)
```

## Supported Environments

- **Creative Writing**: Interactive storytelling with persistent character development
- **Therapeutic Journaling**: Emotional processing with memory continuity
- **Educational Simulations**: Historical scenarios with adaptive responses
- **Gaming**: AI-driven narrative experiences with emotional depth

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

This is an alpha release. For questions or contributions, please refer to the main project documentation.
