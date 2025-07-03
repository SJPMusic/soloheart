# The Narrative Engine

> **A memory-driven, context-aware storytelling framework that simulates and evolves complex narratives across domains like games, therapy, education, and strategic planning.**

![Demo Status](https://img.shields.io/badge/status-Proof%20of%20Concept%20%E2%80%93%20Actively%20Developing-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9+-blue)

## What is The Narrative Engine?

The Narrative Engine treats narrative as a simulation of memory, emotion, decision history, and real-time contextual input—rather than just linear storytelling. It's designed to create AI co-architects that understand context, remember choices, and evolve stories based on layered memory systems.

**Current Proof-of-Concept: SoloHeart**  
SoloHeart is a solo tabletop RPG that demonstrates The Narrative Engine's capabilities in a gaming context. It features:

- **Context-aware memory retrieval** that recalls past choices and their emotional weight
- **Emotionally responsive narratives** that adapt to player decisions and character development
- **Persistent character and campaign state** that maintains continuity across sessions
- **Natural language character creation** through "Vibe Code" conversations with the AI

## Beyond Gaming: The Broader Vision

While SoloHeart showcases the system in entertainment, The Narrative Engine is designed for much broader applications:

- **Therapy & Mental Health**: AI companions that remember therapeutic progress and adapt interventions
- **Education**: Personalized learning narratives that evolve based on student engagement and comprehension
- **Leadership Development**: Simulation environments that track decision patterns and leadership growth
- **Strategic Planning**: Scenario modeling that maintains context across complex, multi-session planning

The core innovation is treating narrative as a **simulation of human memory and reasoning**—not just story generation, but a system that understands context, learns from interactions, and maintains coherent continuity across time.

## How It Works

```
User Input → Context Analysis → Memory Retrieval → Narrative Response → State Update
     ↓              ↓                ↓                    ↓                ↓
Natural Language → Emotional Tagging → Layered Recall → Adaptive Story → Persistent Save
     ↓              ↓                ↓                    ↓                ↓
Character Creation → Memory Systems → Contextual Reasoning → Campaign Progression → Continuity
```

### Core Architecture
- **Layered Memory System**: Short-term, mid-term, and long-term memory with emotional tagging
- **Contextual Drift Prevention**: Advanced algorithms that maintain narrative coherence
- **Emotional Intelligence**: AI that understands and responds to emotional context
- **Domain-Agnostic Design**: Modular architecture that can be adapted to any narrative domain

## Quick Start: SoloHeart Demo

### Prerequisites
- Python 3.9+
- OpenAI API key or Ollama (local LLM)

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

3. **Set up your API key**:
   ```bash
   cp env.template .env
   # Add your OpenAI API key to .env
   ```

### Running SoloHeart
```bash
python simple_unified_interface.py
```

Access the game at: [http://localhost:5001](http://localhost:5001)

## Demo Walkthrough

### 1. Character Creation
- Use "Vibe Code" to describe your character concept in natural language
- The AI asks clarifying questions and builds your character sheet
- All data is SRD 5.1 compliant and legally safe

### 2. Narrative Gameplay
- Seamless transition into immersive storytelling
- Your choices are remembered and influence future encounters
- Emotional context is tracked and affects narrative responses

### 3. Persistent Continuity
- Campaign state is automatically saved
- Return to continue your story with full context preserved
- Memory systems ensure the AI remembers your journey

## Technology Stack

- **Backend**: Python, Flask, OpenAI API/Ollama
- **Memory System**: Vector-based similarity search with emotional tagging
- **Frontend**: HTML5, CSS3, JavaScript (mobile-responsive)
- **Compliance**: SRD 5.1 compliant, fully rebranded as SoloHeart

## Contributing

We welcome contributors interested in:
- **The Narrative Engine**: Core memory systems, contextual reasoning, domain adaptation
- **SoloHeart**: Game mechanics, UI/UX, character systems
- **New Domains**: Therapy, education, leadership, or other narrative applications

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Documentation

- [The Narrative Engine Roadmap](NarrativeEngine_Roadmap.txt) - Development phases and vision
- [Investor Documentation](investor_docs/) - Project overview and future potential
- [Compliance Summary](COMPLIANCE_SUMMARY.md) - Legal and branding compliance

## Vision & Future

The Narrative Engine represents a new approach to AI interaction—one that prioritizes memory, context, and emotional intelligence over simple response generation. SoloHeart is just the beginning.

**Interested in collaborating or investing?**  
We're actively seeking partners to explore applications in therapy, education, leadership development, and beyond. The technology is real, demonstrable, and ready for broader deployment.

## Attribution

This project uses content from the Systems Reference Document 5.1 (SRD 5.1) by Wizards of the Coast LLC, available under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

- SRD 5.1: https://dnd.wizards.com/resources/systems-reference-document
- License: https://creativecommons.org/licenses/by/4.0/

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
