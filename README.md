# SoloHeart - Enhanced Natural Language DnD 5E Character Creation

> **A solo tabletop RPG featuring enhanced natural language character creation that extracts and commits facts immediately from freeform player input, powered by Ollama LLM integration and a domain-agnostic Narrative Engine.**

![Demo Status](https://img.shields.io/badge/status-Enhanced%20Character%20Creation%20%E2%80%93%20Actively%20Developing-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![LLM](https://img.shields.io/badge/LLM-Ollama%20llama3-orange)

## What is SoloHeart?

SoloHeart is a solo tabletop RPG that demonstrates advanced natural language character creation and a domain-agnostic Narrative Engine. Unlike traditional character creation systems that ask linear questions, SoloHeart extracts multiple character facts from freeform player input without requiring explicit prompts or default values.

**Key Innovations:**
- **Immediate Fact Commitment**: Facts are committed to character sheet immediately, avoiding staging states
- **LLM-Powered Extraction**: Uses Ollama's llama3 model for semantic understanding of character descriptions
- **Natural Language Processing**: Robust pattern-matching with LLM fallback for complex extractions
- **DnD 5E Compliance**: Tracks all required character sheet fields automatically
- **Live Character Sheet**: Real-time character sheet updates as you describe your character
- **Guided Completion**: Intelligent fallback to guided questions only when truly ambiguous
- **Domain-Agnostic Narrative Engine**: Modular memory and context system for narrative continuity
- **Game-Specific Features**: Support for inspiration points and saving throws in integration layer

## Enhanced Character Creation System

### How It Works

```
Player Input → LLM Extraction → Pattern Matching → Immediate Commitment → Live Character Sheet
     ↓              ↓                ↓                    ↓                ↓
Natural Language → Semantic Analysis → Regex Patterns → Character State → Real-time Updates
     ↓              ↓                ↓                    ↓                ↓
Freeform Description → Context Understanding → Fact Extraction → No Staging → Instant Feedback
```

### Example Character Creation

**Player Input:**
> "My character is Kaelen Thorne. He's a 35-year-old former blacksmith who lost everything when his forge was burned down in a raid. He has a badly scarred left arm and a deep distrust of authority. Kaelen carries a massive hammer—his own creation—and wears a leather apron like armor. He doesn't call himself a warrior, but when things go bad, he's the first to step in. He's loyal to those who earn it, and he's searching for the raiders who destroyed his home, hoping for justice… or revenge."

**System Extracts:**
- **Name**: Kaelen Thorne
- **Age**: 35
- **Race**: Human
- **Class**: Fighter
- **Background**: Soldier
- **Gender**: Male
- **Combat Style**: Massive hammer, leather apron armor
- **Personality**: Loyal, distrustful of authority
- **Motivations**: Justice, revenge
- **Trauma**: Lost forge in raid, scarred arm
- **Gear**: Massive hammer, leather apron

### Core Features

#### 1. LLM-Powered Semantic Extraction
- **Primary Method**: Uses Ollama's llama3 model for semantic understanding
- **Structured Output**: LLM extracts facts into JSON format
- **Context Awareness**: Understands relationships between facts
- **Ambiguity Detection**: Identifies when facts need confirmation

#### 2. Robust Pattern Matching
- **Fallback System**: Pattern-matching when LLM extraction fails
- **Confidence Scoring**: Only commits high-confidence facts
- **Multiple Fact Types**: Extracts race, class, background, gear, motivations, trauma
- **Context Clues**: Uses surrounding text to infer missing information

#### 3. Immediate Fact Commitment
- **No Staging**: Facts committed directly to character sheet
- **Live Updates**: Character sheet updates in real-time
- **Ambiguity Handling**: Only asks for confirmation when truly ambiguous
- **Confidence Thresholds**: Configurable confidence levels for different fact types

#### 4. Live Character Sheet
- **Real-time Display**: Character sheet updates as you type
- **Visual Feedback**: See what facts have been captured
- **Missing Fields**: Clear indication of what's still needed
- **Responsive Design**: Works on desktop and mobile

#### 5. Guided Completion System
- **Intelligent Fallback**: Only transitions to guided questions when necessary
- **Context Preservation**: Maintains all extracted facts during guided completion
- **Natural Flow**: Seamless transition from natural language to guided questions
- **Completion Tracking**: Automatically tracks required DnD 5E fields

#### 6. Domain-Agnostic Narrative Engine
- **Modular Design**: Core engine independent of game mechanics
- **Layered Memory**: Episodic, semantic, procedural, and emotional memory layers
- **Context Surfacing**: Provides relevant narrative context to LLM
- **Memory Management**: Intelligent memory storage and retrieval
- **Integration Layer**: Clean separation between core engine and game-specific features

#### 7. Game-Specific Features
- **Inspiration Points**: Track and manage character inspiration
- **Saving Throws**: Store and retrieve saving throw modifiers
- **Domain Encapsulation**: All game-specific data stored in `current_state`
- **Clean Integration**: Game features don't affect core Narrative Engine

## Technology Stack

- **Backend**: Python, Flask, Ollama (local LLM)
- **Character Creation**: Enhanced fact extraction with immediate commitment
- **LLM Integration**: Ollama llama3 model for semantic understanding
- **Pattern Matching**: Robust regex patterns for fallback extraction
- **Frontend**: HTML5, CSS3, JavaScript (mobile-responsive)
- **Narrative Engine**: Domain-agnostic memory and context system
- **Compliance**: SRD 5.2 compliant, fully rebranded as SoloHeart

## Quick Start

### Prerequisites
- Python 3.9+
- Ollama with llama3 model (local LLM)

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

3. **Set up Ollama**:
   ```bash
   # Install Ollama (macOS)
   brew install ollama
   
   # Start Ollama service
   brew services start ollama
   
   # Pull the llama3 model
   ollama pull llama3
   ```

### Running SoloHeart
```bash
python simple_unified_interface.py
```

Access the game at: [http://localhost:5001](http://localhost:5001)

## Character Creation Walkthrough

### 1. Natural Language Input
- Describe your character concept in detail using natural language
- Include race, class, background, personality, motivations, gear, trauma
- No need to follow specific prompts or answer linear questions
- System extracts multiple facts simultaneously

### 2. Immediate Fact Commitment
- Facts are committed to character sheet immediately
- No staging or pending states
- Live character sheet shows what's been captured
- Only requests confirmation for truly ambiguous facts

### 3. LLM-Powered Understanding
- Primary extraction uses Ollama's llama3 model
- Semantic understanding of character descriptions
- Context-aware fact extraction
- Handles complex, multi-sentence descriptions

### 4. Pattern Matching Fallback
- Robust regex patterns when LLM extraction fails
- Confidence scoring for all extracted facts
- Context clues for inferring missing information
- Multiple extraction strategies for different fact types

### 5. Guided Completion
- Intelligent transition to guided questions only when needed
- Preserves all extracted facts during guided completion
- Tracks missing DnD 5E required fields
- Natural flow from freeform to guided input

## Key Innovations

### Enhanced Fact Extraction
- **LLM Primary**: Semantic understanding with Ollama llama3
- **Pattern Fallback**: Robust regex patterns for reliability
- **Multi-Fact Extraction**: Extracts multiple facts simultaneously
- **Context Awareness**: Uses surrounding text for inference
- **Confidence Scoring**: Only commits high-confidence facts

### Immediate Commitment System
- **No Staging**: Facts committed directly to character sheet
- **Live Updates**: Real-time character sheet updates
- **Ambiguity Detection**: Only asks for confirmation when truly ambiguous
- **Confidence Thresholds**: Configurable for different fact types

### Live Character Sheet
- **Real-time Display**: Updates as you describe your character
- **Visual Feedback**: Clear indication of captured facts
- **Missing Fields**: Shows what's still needed
- **Responsive Design**: Works on all devices

### Guided Completion
- **Intelligent Transition**: Only when truly ambiguous
- **Context Preservation**: Maintains all extracted facts
- **Natural Flow**: Seamless from freeform to guided
- **Completion Tracking**: Tracks DnD 5E required fields

### Domain-Agnostic Narrative Engine
- **Modular Design**: Core engine independent of game mechanics
- **Layered Memory**: Episodic, semantic, procedural, emotional layers
- **Context Surfacing**: Provides relevant narrative context to LLM
- **Memory Management**: Intelligent storage and retrieval
- **Integration Layer**: Clean separation between core and game-specific features

### Game-Specific Features
- **Inspiration Points**: Track and manage character inspiration
- **Saving Throws**: Store and retrieve saving throw modifiers
- **Domain Encapsulation**: All game-specific data in `current_state`
- **Clean Integration**: Game features don't affect core engine

## Project Structure

```
SoloHeart Project/
├── solo_heart/                      # Main application
│   ├── simple_unified_interface.py  # Main Flask application
│   ├── templates/                   # UI templates
│   ├── utils/                       # Utility functions
│   │   ├── character_fact_extraction.py  # Fact extraction
│   │   ├── guided_character_completion.py # Guided completion
│   │   └── ollama_llm_service.py   # LLM integration
│   ├── narrative_engine_integration.py # SoloHeart integration layer
│   └── character_generator.py       # Character generation
├── narrative_core/                  # Domain-agnostic Narrative Engine
│   └── narrative_engine.py         # Core memory and context system
├── docs/                           # Documentation
├── tests/                          # Test suite
├── requirements.txt                 # Dependencies
├── README.md                       # This file
└── archive_2025-07-04/            # Archived redundant files
```

## Recent Improvements

### Narrative Engine Domain-Agnostic Integrity (2025-07-05)
- **Core Engine Cleanup**: Removed all domain-specific logic from Narrative Engine core
- **Integration Layer**: Proper separation of universal vs game-specific fields
- **Memory Layers**: Established episodic, semantic, procedural, and emotional memory layers
- **Game Features**: Added inspiration points and saving throws support in integration layer
- **Architectural Integrity**: Maintained clean separation between core engine and game features

### Project Cleanup (2025-07-04)
- **Archived Redundant Files**: 50+ files and 4 duplicate directories
- **Simplified Structure**: Cleaner project hierarchy
- **Preserved History**: All files safely archived for recovery
- **Better Maintainability**: Clear separation of active vs archived code

### Enhanced Character Creation
- **LLM Integration**: Ollama llama3 for semantic understanding
- **Immediate Commitment**: No staging states, direct character sheet updates
- **Live Character Sheet**: Real-time visual feedback
- **Robust Fallback**: Pattern matching when LLM extraction fails

### UI Improvements
- **Simplified Flow**: Removed "Vibe Code" terminology from user interface
- **Campaign Start**: Only asks for campaign name and character creation
- **Live Updates**: Character sheet updates in real-time
- **Responsive Design**: Works on desktop and mobile

## Contributing

We welcome contributors interested in:
- **Enhanced Character Creation**: LLM integration, fact extraction, guided completion
- **UI/UX Improvements**: Web interface, mobile responsiveness, user experience
- **DnD 5E Integration**: Game mechanics, character sheets, compliance
- **LLM Integration**: Ollama optimization, prompt engineering, semantic understanding
- **Narrative Engine**: Memory systems, context management, domain-agnostic design

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Documentation

- [How to Play](HOW_TO_PLAY.md) - Game instructions and character creation guide
- [Compliance Summary](COMPLIANCE_SUMMARY.md) - Legal and branding compliance
- [Cleanup Summary](CLEANUP_SUMMARY.md) - Project cleanup and archive details
- [Development Log](DEVELOPMENT_LOG.md) - Comprehensive development history
- [Character Fact Extraction](solo_heart/utils/character_fact_extraction.py) - Fact extraction implementation
- [Narrative Engine](narrative_core/narrative_engine.py) - Domain-agnostic memory and context system

## Vision & Future

SoloHeart represents a new approach to character creation and narrative systems—one that prioritizes natural language understanding, immediate feedback, and domain-agnostic design over rigid form-filling. The enhanced character creation system with LLM integration and the modular Narrative Engine demonstrate the potential for more intuitive and engaging game experiences.

**Interested in collaborating or contributing?**  
We're actively seeking contributors to enhance the character creation system, improve the UI/UX, expand the game mechanics, and develop the domain-agnostic Narrative Engine for broader applications.

## Attribution

This project uses content from the Systems Reference Document 5.2 (SRD 5.2) by Wizards of the Coast LLC, available under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

- SRD 5.2: https://dnd.wizards.com/resources/systems-reference-document
- License: https://creativecommons.org/licenses/by/4.0/

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
