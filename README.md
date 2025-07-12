# The Narrative Engine D&D Demo

> **A demonstration application showcasing The Narrative Engine's symbolic processing capabilities through interactive character creation and narrative development workflows, featuring clean input/output routing and symbolic state visualization.**

![Demo Status](https://img.shields.io/badge/status-TNE%20Demo%20Layer%20%E2%80%93%20Active-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![LLM](https://img.shields.io/badge/LLM-Gemma%20Integration-orange)

## What is The Narrative Engine D&D Demo?

The Narrative Engine D&D Demo is a lightweight orchestration layer that demonstrates The Narrative Engine's symbolic processing capabilities through interactive character creation and narrative development workflows. It serves as a reference implementation for symbolic bridge input routing, goal inference monitoring, episodic and semantic memory integration, and LLM-assisted narrative decision modeling.

**Key Demonstration Features:**
- **Symbolic Bridge Routing**: Clean handoff of user input through TNB to TNE
- **Memory State Visualization**: Display of episodic, semantic, and emotional memory flows
- **Goal Inference Monitoring**: Real-time tracking of narrative goal completion
- **Symbolic Pattern Recognition**: Visualization of archetype detection and symbolic reasoning
- **LLM Response Enrichment**: Display of memory-enhanced narrative outputs

**Key Innovations:**
- **Symbolic Processing Demonstration**: Showcases TNE's archetype detection and symbolic reasoning
- **Memory Flow Visualization**: Displays episodic, semantic, and emotional memory retrieval
- **Goal State Tracking**: Real-time visualization of narrative goal completion and inference
- **Bridge Routing Compliance**: Follows TNB's input/output patterns exactly
- **LLM-Native Integration**: Leverages Gemma's autonomous narrative generation capabilities
- **Clean Modular Boundaries**: Maintains strict separation from core TNE/TNB architecture
- **Symbolic State Display**: Visualizes symbolic patterns, transformations, and insights
- **Memory Context Enrichment**: Shows how retrieved memories enhance LLM responses

## TNE Demonstration System

### How It Works

```
User Input → TNB Bridge → TNE Processing → Symbolic Analysis → Response Display
     ↓              ↓                ↓                    ↓                ↓
Narrative Input → Memory Retrieval → Symbolic Processing → Pattern Detection → Enriched Output
     ↓              ↓                ↓                    ↓                ↓
Character Creation → Context Injection → Archetype Recognition → Goal Tracking → Memory Visualization
```

### Example TNE Demonstration

**User Input:**
> "My character is Kaelen Thorne. He's a 35-year-old former blacksmith who lost everything when his forge was burned down in a raid. He has a badly scarred left arm and a deep distrust of authority. Kaelen carries a massive hammer—his own creation—and wears a leather apron like armor. He doesn't call himself a warrior, but when things go bad, he's the first to step in. He's loyal to those who earn it, and he's searching for the raiders who destroyed his home, hoping for justice… or revenge."

**TNE Symbolic Analysis:**
- **Archetype Detection**: Hero's Journey pattern (transformation, quest for justice)
- **Symbolic Patterns**: Rebirth cycle (loss → transformation → quest)
- **Memory Integration**: Episodic (raid trauma), Semantic (blacksmith skills), Emotional (distrust, loyalty)
- **Goal Inference**: Justice/revenge quest, protection of allies, personal transformation
- **Symbolic Reasoning**: Transformation from craftsman to protector, loss as catalyst for growth

### Core Features

#### 1. Symbolic Bridge Routing
- **TNB Integration**: Clean handoff of user input through Narrative Bridge
- **Memory Retrieval**: Demonstrates episodic, semantic, and emotional memory flows
- **Context Injection**: Shows how relevant memories enhance LLM prompts
- **Output Processing**: Visualizes extraction of narrative-relevant information

#### 2. Symbolic State Visualization
- **Archetype Detection**: Displays recognition of universal narrative patterns
- **Pattern Recognition**: Shows transformation, conflict, and resolution cycles
- **Symbolic Reasoning**: Visualizes computational analysis of symbolic relationships
- **Insight Generation**: Displays meaningful interpretations of symbolic patterns

#### 3. Memory Flow Display
- **Episodic Memory**: Shows retrieval of past interactions and events
- **Semantic Memory**: Demonstrates concept and knowledge recall capabilities
- **Emotional Memory**: Visualizes emotional context and relationship dynamics
- **Memory Relevance**: Displays relevance scores and contextual weighting

#### 4. Goal State Tracking
- **Goal Inference**: Shows automatic detection of narrative objectives
- **Progress Visualization**: Displays completion status of narrative goals
- **Goal Evolution**: Tracks how goals change and develop over time
- **Completion Indicators**: Highlights achieved narrative milestones

#### 5. LLM Response Enrichment
- **Memory Context**: Shows how retrieved memories enhance LLM responses
- **Symbolic Insights**: Displays symbolic analysis of narrative content
- **Response Analysis**: Visualizes the impact of memory on narrative generation
- **Enrichment Display**: Highlights memory-influenced narrative elements

#### 6. Clean Modular Boundaries
- **Demo Layer Only**: Focuses exclusively on demonstration and visualization
- **No Core Logic**: All narrative processing delegated to TNE/TNB systems
- **UI/UX Focus**: Emphasizes user experience and interface design
- **Integration Testing**: Validates proper communication with core systems

#### 7. LLM Provider Orchestration
- **Gemma Integration**: Primary provider for autonomous narrative generation
- **Provider Abstraction**: Uses llm_provider_base.py pattern for clean routing
- **Environment Configuration**: .env-based control of active LLM backend
- **Fallback Support**: Maintains Ollama fallback for testing and validation

## Technology Stack

- **Backend**: Python, Flask, Gemma API integration
- **Demo Layer**: Lightweight orchestration and visualization
- **LLM Integration**: Gemma for autonomous narrative generation
- **Bridge Routing**: TNB integration for memory retrieval and prompt construction
- **Frontend**: HTML5, CSS3, JavaScript (mobile-responsive)
- **Symbolic Processing**: TNE integration for archetype detection and reasoning
- **Memory Visualization**: Display of episodic, semantic, and emotional memory flows

## Quick Start

### Prerequisites
- Python 3.9+
- Gemma API access (or Ollama fallback for testing)
- TNB server running on localhost:3000
- TNE server running on localhost:5000

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/PianomanSJPM/solo-rp-game-demo.git
   cd solo-rp-game-demo/solo_heart
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   # Copy environment template
   cp env.template .env
   
   # Set LLM provider (gemma or ollama)
   echo "LLM_PROVIDER=gemma" >> .env
   ```

### Running The Narrative Engine D&D Demo
```bash
python simple_unified_interface.py
```

Access the demo at: [http://localhost:5001](http://localhost:5001)

## TNE Demonstration Walkthrough

### 1. Narrative Input Capture
- Describe your character concept using natural language
- Include background, personality, motivations, and story elements
- System routes input through TNB for memory retrieval
- No manual prompt construction or staging required

### 2. Symbolic Bridge Routing
- Input automatically routed through TNB bridge
- Memory retrieval from TNE (episodic, semantic, emotional)
- Context injection into LLM prompts
- Clean handoff to TNE for symbolic processing

### 3. Symbolic State Visualization
- Archetype detection and pattern recognition displayed
- Symbolic reasoning and insight generation shown
- Goal inference and completion tracking visualized
- Real-time updates of symbolic processing results

### 4. Memory Flow Display
- Episodic memory retrieval and relevance scoring
- Semantic memory integration and concept recall
- Emotional memory context and relationship dynamics
- Memory impact on narrative generation highlighted

### 5. Enriched Response Display
- LLM responses enhanced with memory context
- Symbolic insights and pattern analysis included
- Goal progress and completion indicators shown
- Memory-influenced narrative elements highlighted

## Key Innovations

### Symbolic Processing Demonstration
- **Archetype Detection**: Recognition of universal narrative patterns
- **Pattern Recognition**: Transformation, conflict, and resolution cycles
- **Symbolic Reasoning**: Computational analysis of symbolic relationships
- **Insight Generation**: Meaningful interpretations of symbolic patterns
- **Goal Inference**: Automatic detection of narrative objectives

### Memory Flow Visualization
- **Episodic Memory**: Retrieval of past interactions and events
- **Semantic Memory**: Concept and knowledge recall capabilities
- **Emotional Memory**: Emotional context and relationship dynamics
- **Memory Relevance**: Relevance scoring and contextual weighting
- **Memory Impact**: Visualization of memory influence on responses

### Bridge Routing Compliance
- **TNB Integration**: Clean handoff of user input through Narrative Bridge
- **Memory Injection**: Shows how relevant memories enhance LLM prompts
- **Context Preservation**: Demonstrates narrative continuity across sessions
- **Output Processing**: Visualizes extraction of narrative-relevant information
- **Symbolic Integrity**: Maintains TNE's cross-domain applicability

### LLM-Native Integration
- **Gemma Integration**: Autonomous narrative generation capabilities
- **Provider Abstraction**: Clean routing through llm_provider_base.py pattern
- **Environment Configuration**: .env-based control of active LLM backend
- **Fallback Support**: Ollama fallback for testing and validation
- **Token Management**: Optimized for each model's capabilities

### Clean Modular Boundaries
- **Demo Layer Only**: Focuses exclusively on demonstration and visualization
- **No Core Logic**: All narrative processing delegated to TNE/TNB systems
- **UI/UX Focus**: Emphasizes user experience and interface design
- **Integration Testing**: Validates proper communication with core systems
- **Symbolic Integrity**: Full compliance with symbolic processing models

## Project Structure

```
SoloHeart Project/
├── solo_heart/                      # TNE Demo Layer
│   ├── simple_unified_interface.py  # Main demo application
│   ├── templates/                   # UI templates
│   ├── demo_layer/                  # Demonstration components
│   │   ├── input_capture.py        # User input interfaces
│   │   ├── output_display.py       # Response visualization
│   │   ├── memory_visualizer.py    # Memory state display
│   │   ├── goal_tracker.py         # Goal progress visualization
│   │   └── symbolic_display.py     # Symbolic pattern visualization
│   ├── routing/                     # Bridge routing components
│   │   ├── tnb_bridge.py           # TNB integration
│   │   ├── tne_connector.py        # TNE integration
│   │   └── llm_orchestrator.py     # LLM provider management
│   ├── config/                      # Configuration
│   │   ├── provider_factory.py     # LLM provider selection
│   │   └── environment.py          # Environment configuration
│   └── utils/                       # Utility functions
│       ├── json_renderer.py        # JSON response formatting
│       ├── markdown_processor.py   # Markdown output processing
│       └── symbolic_tags.py        # Symbolic tag visualization
├── docs/                           # Documentation
├── tests/                          # Test suite
├── requirements.txt                 # Dependencies
├── README.md                       # This file
└── archive_2025-07-04/            # Archived redundant files
```

## Recent Improvements

### TNE Demo Layer Pivot (2025-07-10)
- **Architectural Pivot**: Transformed from standalone game to TNE demonstration layer
- **Symbolic Processing Integration**: Clean integration with TNE's archetype detection and reasoning
- **Bridge Routing Compliance**: Proper adherence to TNB's input/output patterns
- **Memory Flow Visualization**: Display of episodic, semantic, and emotional memory flows
- **Goal State Tracking**: Real-time visualization of narrative goal completion and inference

### LLM Provider Migration (2025-07-09)
- **Gemma Integration**: Migrated from Ollama to Gemma for autonomous narrative generation
- **Provider Abstraction**: Implemented clean llm_provider_base.py pattern
- **Environment Configuration**: .env-based control of active LLM backend
- **Fallback Support**: Maintained Ollama fallback for testing and validation
- **Timeout Optimization**: Increased timeout to 180 seconds for long prompts

### Symbolic State Visualization
- **Archetype Detection**: Display of universal narrative pattern recognition
- **Pattern Recognition**: Visualization of transformation, conflict, and resolution cycles
- **Symbolic Reasoning**: Real-time display of computational symbolic analysis
- **Insight Generation**: Meaningful interpretations of symbolic patterns
- **Goal Inference**: Automatic detection and tracking of narrative objectives

### Clean Modular Boundaries
- **Demo Layer Only**: Focuses exclusively on demonstration and visualization
- **No Core Logic**: All narrative processing delegated to TNE/TNB systems
- **UI/UX Focus**: Emphasizes user experience and interface design
- **Integration Testing**: Validates proper communication with core systems
- **Symbolic Integrity**: Full compliance with symbolic processing models

## Contributing

We welcome contributors interested in:
- **TNE Demo Layer**: Symbolic processing visualization, memory flow display
- **UI/UX Improvements**: Web interface, mobile responsiveness, user experience
- **Bridge Routing**: TNB integration, memory retrieval, prompt construction
- **LLM Integration**: Gemma optimization, provider abstraction, symbolic analysis
- **Symbolic Processing**: Archetype detection, pattern recognition, goal inference

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Documentation

- [How to Play](HOW_TO_PLAY.md) - Demo instructions and character creation guide
- [Compliance Summary](COMPLIANCE_SUMMARY.md) - Legal and branding compliance
- [Cleanup Summary](CLEANUP_SUMMARY.md) - Project cleanup and archive details
- [Development Log](DEVELOPMENT_LOG.md) - Comprehensive development history
- [TNE Integration](solo_heart/narrative_engine_integration.py) - TNE integration implementation
- [Symbolic Processing](../The Narrative Engine/docs/symbolic_processor.md) - TNE symbolic processing documentation

## Vision & Future

The Narrative Engine D&D Demo represents a new approach to symbolic processing visualization and narrative system demonstration—one that prioritizes clean modular boundaries, symbolic integrity, and LLM-native integration over embedded logic. The demonstration layer showcases TNE's capabilities through interactive character creation and narrative development workflows.

**Interested in collaborating or contributing?**  
We're actively seeking contributors to enhance the demo layer visualization, improve the UI/UX, expand the symbolic processing display, and develop the bridge routing capabilities for broader TNE/TNB integration validation.

## Attribution

This project uses content from the Systems Reference Document 5.2 (SRD 5.2) by Wizards of the Coast LLC, available under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

- SRD 5.2: https://dnd.wizards.com/resources/systems-reference-document
- License: https://creativecommons.org/licenses/by/4.0/

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
