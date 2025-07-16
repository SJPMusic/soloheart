This work includes material from the System Reference Document 5.2 and is licensed under the Creative Commons Attribution 4.0 International License.

# SoloHeart Game Engine (SRD 5.2-Compliant)

## Project Summary
This is an enhanced demo for the Narrative Engine: an immersive, LLM-powered solo DnD 5E experience with advanced character creation and symbolic meaning integration. The system enables a single player to create a character using natural language and play through a campaign with an AI Dungeon Master, all in a clean, SRD 5.2-compliant, and legally safe environment.

## Key Features

### 🎯 Enhanced Character Creation
- **LLM-Powered Extraction**: Uses Ollama's llama3 model for semantic understanding of character descriptions
- **Immediate Fact Commitment**: Extract and commit character facts immediately from natural language input
- **Live Character Sheet**: Real-time updates as player describes character with visual feedback
- **No Linear Questioning**: Describe your character naturally without being prompted for specific details
- **Robust Fallback System**: Pattern matching when LLM extraction fails for reliability
- **Multi-Fact Extraction**: Extracts name, race, class, background, age, gender, alignment, personality, motivations, trauma, gear, combat style simultaneously
- **Confidence Scoring**: Only commits high-confidence facts with configurable thresholds
- **Context Awareness**: Uses surrounding text to infer missing information
- **Ambiguity Detection**: Only requests confirmation when facts are truly ambiguous
- **DnD 5E Compliance**: Automatically tracks missing required fields and validates character data

### 🧠 Symbolic Meaning Framework
- **Archetypal Tagging**: Facts tagged with Jungian archetypes (Father, Shadow, Journey, etc.)
- **Chaos/Order Tension**: Dynamic tracking of narrative stability and character development
- **Narrative Decay Detection**: Identifies contradictions and avoidance patterns
- **Symbolic Coherence**: Ensures meaningful character development and story progression
- **Psychological Depth**: Inspired by Jordan B. Peterson's *Maps of Meaning* principles

### 💬 Natural Language Interface
- **Freeform Character Creation**: Describe your character concept in detail without constraints
- **AI-Driven Conversation**: LLM guides character development through natural dialogue
- **Real-Time Validation**: Character data validated against SRD 5.2 schema
- **Structured Output**: Character data saved in standardized JSON format with symbolic metadata
- **Error Handling**: Graceful handling of invalid inputs and edge cases

### 📋 SRD 5.2 Compliant Character System
- **Complete Character Schema**: All standard DnD 5E character fields included
- **Legal Compliance**: Uses only open-source SRD content
- **Validation System**: Ensures all character data meets game requirements
- **Character Sheet Rendering**: Beautiful, mobile-responsive character display
- **Character Management**: Save, load, and update character data with symbolic state

### 📖 Immersive Narrative Gameplay
- **AI Dungeon Master**: LLM generates dynamic, contextual storytelling
- **Natural Language Interaction**: Players respond naturally to story prompts
- **Context Awareness**: AI remembers campaign history and character development
- **Emotional Memory**: Tracks character emotional states and relationships
- **Symbolic Influence**: Chaos/order tension and archetypal state affect narrative direction
- **Campaign Progression**: Story evolves based on player choices and actions

### 💾 Persistent Campaign System
- **Automatic Saving**: All game state automatically persisted
- **Campaign State Management**: Tracks story progress, character development, and world state
- **Session Continuity**: Seamless experience across multiple play sessions
- **Symbolic Persistence**: Chaos/order tension and archetypal state maintained across sessions
- **Data Integrity**: Robust error handling and data validation

### 📱 Modern, Responsive UI
- **Mobile-First Design**: Optimized for mobile and desktop experiences
- **Thematic Styling**: Immersive, fantasy-themed interface design
- **Real-Time Updates**: Dynamic UI updates without page refreshes
- **Live Character Sheet**: Real-time character sheet updates as you type
- **Accessibility**: Clean, readable design with good contrast and navigation

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/PianomanSJPM/solo-rp-game-demo.git
   cd solo-rp-game-demo/solo_heart
   ```
2. Install dependencies (Python 3.9+ recommended):
   ```
   pip install -r requirements.txt
   ```
3. Set up Ollama (local LLM):
   ```bash
   # Install Ollama (macOS)
   brew install ollama
   
   # Start Ollama service
   brew services start ollama
   
   # Pull the llama3 model
   ollama pull llama3
   ```

## Running the Demo
1. Start the unified interface (port 5001):
   ```
   python simple_unified_interface.py
   ```
2. Open your browser:
   - Landing page: [http://localhost:5001](http://localhost:5001)
   - Game interface: [http://localhost:5001/game](http://localhost:5001/game)

## Demo Instructions

### Landing Page Options
1. **Start New Game**: Begin a new adventure with optional campaign ID
2. **Resume Game**: Continue an existing session from the dropdown list
3. **Demo Mode**: Try SoloHeart instantly with a pre-configured demo character

### Session Management
- **Session List**: View all available sessions with creation dates and campaign IDs
- **Load Sessions**: Resume any previous session with one click
- **Rename Sessions**: Customize session names for better organization
- **Delete Sessions**: Remove old sessions to keep your list clean
- **Auto-Cleanup**: Demo sessions are automatically cleaned up after 24 hours

### Demo Mode Features
- **Instant Start**: No character creation required - jump straight into gameplay
- **Pre-configured Character**: Demo character with balanced stats and equipment
- **Temporary Sessions**: Demo sessions are tagged and auto-deleted after timeout
- **Full Feature Access**: All gameplay features available in demo mode
- **Session Timeout**: Configurable timeout (default: 24 hours) in settings.json

### Enhanced Character Creation
1. **Natural Language**: Describe your character in detail without constraints
2. **Live Character Sheet**: Watch as your character sheet updates in real-time
3. **Symbolic Analysis**: Facts tagged with archetypal symbols and chaos/order tension
4. **SRD Compliance**: All character data validated against D&D 5E rules
5. **Immersive Gameplay**: Transition directly into narrative storytelling

## Configuration

### Demo Mode Settings
Edit `settings.json` to customize demo behavior:
```json
{
  "demo_mode": {
    "enable_demo_mode": true,
    "demo_session_timeout_hours": 24,
    "auto_resume_latest": false,
    "max_sessions_visible": 10
  }
}
```

### Session Management
- **Auto-cleanup**: Demo sessions automatically deleted after timeout
- **Session retention**: Regular sessions kept for 7 days by default
- **Max sessions**: Limit visible sessions to prevent UI clutter

## Technical Architecture

### Enhanced Character Creation
- **LLM Integration**: Ollama llama3 model for semantic understanding
- **Fact Extraction Engine**: Robust pattern matching and confidence scoring with LLM fallback
- **Immediate Commitment**: Facts committed to character sheet without staging
- **Live Updates**: Real-time character sheet updates with visual feedback
- **Ambiguity Detection**: Intelligent detection of unclear or contradictory information
- **Symbolic Integration**: Archetypal tagging and chaos/order impact assessment

### LLM Integration
- **Primary Method**: Ollama llama3 model for semantic understanding
- **Structured Output**: LLM extracts facts into JSON format
- **Fallback System**: Pattern matching when LLM extraction fails
- **Error Handling**: Graceful degradation to pattern matching
- **Context Awareness**: Uses surrounding text to infer missing information

### Symbolic Meaning Framework
- **Archetypal Analysis**: Jungian archetype detection and tagging
- **Chaos/Order Modeling**: Dynamic tension tracking and state management
- **Narrative Decay**: Contradiction and avoidance pattern detection
- **Symbolic Coherence**: Archetypal conflict resolution and coherence scoring

### Backend Systems
- **Flask Web Framework**: Lightweight, scalable Python web application
- **Ollama Integration**: Local LLM for natural language processing
- **JSON Schema Validation**: Ensures data integrity and compliance
- **File-Based Storage**: Simple, reliable persistence system
- **Error Handling**: Comprehensive error catching and user feedback

### Frontend Systems
- **HTML5 Templates**: Semantic, accessible markup
- **CSS3 Styling**: Modern, responsive design with animations
- **JavaScript Interactivity**: Dynamic UI updates and real-time features
- **Mobile Responsiveness**: Optimized for all screen sizes
- **Live Character Sheet**: Real-time character sheet updates

## Project Cleanup (2025-07-04)
- **Archived Redundant Files**: 50+ files and 4 duplicate directories
- **Simplified Structure**: Cleaner project hierarchy with clear active vs archived separation
- **Preserved History**: All files safely archived with detailed recovery instructions
- **Better Maintainability**: Clear separation of active vs archived code

## Development Statistics
- **Files Archived**: 50+ files and 4 directories
- **Archive Size**: ~100MB of redundant content
- **Development Time**: ~3 hours for cleanup and enhancements
- **Lines of Code**: ~2000 lines of enhanced character creation
- **Test Coverage**: Comprehensive testing of new features
- **Documentation**: Updated README and project documentation

## Screenshots
> _Add screenshots of the start screen, character creation, and narrative interface here_

## Attribution
See [ATTRIBUTION.md](ATTRIBUTION.md) for full details.
- SRD 5.2 by Wizards of the Coast, licensed under CC BY 4.0
- Ollama for local LLM-driven gameplay
- Symbolic Meaning Framework inspired by Jordan B. Peterson's *Maps of Meaning* 