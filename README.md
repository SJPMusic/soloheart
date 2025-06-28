# The Narrative Engine

A domain-agnostic narrative intelligence system that understands, generates, and adapts stories across multiple contexts.

## Overview

The Narrative Engine is a sophisticated system designed to work with narratives across various domains including gaming, therapy, education, organizational storytelling, creative writing, journalism, and marketing. It provides deep narrative understanding, generation capabilities, and adaptive storytelling.

## Core Features

### 1. **Layered Memory System**
- **Short-term memory**: Immediate context and recent interactions
- **Mid-term memory**: Session-level goals, arcs, and unresolved threads  
- **Long-term memory**: Campaign/world-level lore, history, and relationships
- **Memory decay and reinforcement**: Natural forgetting and strengthening mechanisms
- **Emotional context**: Memory tagging with emotional weights and contexts
- **Nonlinear recall**: Associative and contextual memory retrieval

### 2. **Domain-Agnostic Architecture**
- **Modular domain adapters**: Specialized handlers for different narrative contexts
- **Universal narrative analysis**: Story structure, coherence, and thematic analysis
- **Cross-domain learning**: Knowledge transfer between different narrative types
- **Extensible framework**: Easy addition of new domains and capabilities

### 3. **Narrative Intelligence**
- **Story structure analysis**: Understanding narrative arcs, pacing, and structure
- **Character modeling**: Dynamic character development and relationship tracking
- **Plot generation**: Contextual plot point creation and adaptation
- **Thematic analysis**: Identifying and developing themes and motifs
- **Coherence maintenance**: Ensuring narrative consistency and flow

### 4. **Adaptive Capabilities**
- **Real-time adaptation**: Dynamic story adjustment based on user input
- **Personalization**: Tailored experiences based on user preferences and history
- **Context awareness**: Situational understanding and appropriate responses
- **Multi-modal support**: Text, dialogue, and structured narrative formats

## Architecture

```
The Narrative Engine/
├── core/
│   ├── memory_system.py          # Layered memory implementation
│   ├── narrative_engine.py       # Main engine orchestration
│   ├── domain_adapters.py        # Domain-specific handlers
│   ├── story_analyzer.py         # Narrative analysis tools
│   ├── character_model.py        # Character development system
│   └── plot_generator.py         # Plot creation and adaptation
├── domains/
│   ├── gaming.py                 # Gaming narrative adapter
│   ├── therapy.py                # Therapeutic narrative adapter
│   ├── education.py              # Educational narrative adapter
│   ├── organizational.py         # Business narrative adapter
│   ├── creative_writing.py       # Creative writing adapter
│   ├── journalism.py             # Journalistic narrative adapter
│   └── marketing.py              # Marketing narrative adapter
├── utils/
│   ├── text_processing.py        # NLP and text analysis
│   ├── coherence_checker.py      # Narrative consistency tools
│   └── export_import.py          # Data serialization
├── examples/
│   ├── demo.py                   # Basic usage examples
│   ├── gaming_example.py         # Gaming narrative demo
│   ├── therapy_example.py        # Therapeutic narrative demo
│   └── education_example.py      # Educational narrative demo
├── tests/
│   ├── test_memory_system.py     # Memory system tests
│   ├── test_narrative_engine.py  # Engine functionality tests
│   └── test_domain_adapters.py   # Domain adapter tests
├── docs/
│   ├── API.md                    # API documentation
│   ├── DOMAINS.md                # Domain-specific guides
│   └── MEMORY_SYSTEM.md          # Memory system documentation
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Installation

```bash
# Clone or create the project directory
cd "The Narrative Engine"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```python
from core.narrative_engine import NarrativeEngine
from domains.gaming import GamingAdapter

# Initialize the engine
engine = NarrativeEngine()

# Register a domain adapter
engine.register_domain('gaming', GamingAdapter())

# Create a narrative
narrative = engine.create_narrative(
    domain='gaming',
    title='Epic Adventure',
    description='A hero\'s journey through a mystical realm'
)

# Add characters
engine.add_character(narrative.id, {
    'name': 'Aria',
    'role': 'protagonist',
    'traits': ['brave', 'curious', 'determined']
})

# Generate plot points
plot_point = engine.generate_plot_point(narrative.id, {
    'context': 'The hero discovers an ancient map',
    'tension': 'high',
    'character_focus': 'Aria'
})

# Analyze narrative
analysis = engine.analyze_narrative(narrative.id)
print(f"Coherence: {analysis.coherence_score}")
print(f"Themes: {analysis.themes}")
```

## Core Concepts

### Memory as Narrative Context
The engine uses a sophisticated memory system that treats memories as narrative building blocks:
- **Emotional weighting**: Memories are tagged with emotional significance
- **Associative linking**: Memories connect through themes, characters, and events
- **Temporal layering**: Different time scales for different narrative needs
- **Decay and reinforcement**: Natural memory processes that affect narrative flow

### Domain Adaptability
Each domain has specialized knowledge and capabilities:
- **Gaming**: Character progression, quest systems, world-building
- **Therapy**: Emotional processing, personal growth, healing narratives
- **Education**: Learning objectives, knowledge retention, skill development
- **Organizational**: Brand storytelling, corporate narratives, change management
- **Creative Writing**: Literary techniques, genre conventions, artistic expression
- **Journalism**: Fact-based storytelling, ethical reporting, audience engagement
- **Marketing**: Brand narratives, customer journeys, conversion optimization

### Narrative Intelligence
The engine understands narrative at multiple levels:
- **Structural**: Plot arcs, pacing, scene construction
- **Character**: Development, relationships, motivations
- **Thematic**: Symbolism, motifs, deeper meanings
- **Emotional**: Emotional arcs, tension, catharsis
- **Contextual**: Cultural, historical, situational awareness

## API Reference

### Core Engine
- `NarrativeEngine()`: Main engine class
- `create_narrative()`: Create new narrative
- `analyze_narrative()`: Analyze narrative structure and themes
- `generate_plot_point()`: Generate contextual plot points
- `adapt_narrative()`: Adapt narrative based on new information

### Memory System
- `add_memory()`: Store new memory
- `recall()`: Retrieve relevant memories
- `reinforce()`: Strengthen memory connections
- `forget()`: Natural memory decay

### Domain Adapters
- `register_domain()`: Add new domain support
- `get_domain_adapter()`: Access domain-specific functionality
- `cross_domain_analysis()`: Apply insights across domains

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

Creative Commons Attribution-NonCommercial 4.0 International License

## Contact

For questions, suggestions, or collaboration opportunities, please contact the development team.

---

*The Narrative Engine represents a new paradigm in computational storytelling, bridging the gap between human creativity and artificial intelligence to create truly adaptive, intelligent narrative experiences.* 