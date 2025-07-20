# 🎲 SoloHeart Game Engine

[![CI](https://github.com/SJPMusic/soloheart/workflows/SoloHeart%20CI/badge.svg)](https://github.com/SJPMusic/soloheart/actions/workflows/test.yml)

> **Transform solo tabletop gaming with AI-powered storytelling that adapts to your choices and creates truly personalized adventures.**

![Demo Status](https://img.shields.io/badge/status-Demo%20Stage%20%E2%80%93%20Actively%20Developing-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9+-blue)

![Demo Screenshot](demo_screenshot.txt)

## Project Summary

This is a proof-of-concept demo for the **Narrative Engine**: an immersive, LLM-powered solo DnD 5E experience. The system enables a single player to create a character using natural language and play through a campaign with an AI Dungeon Master, all in a clean, SRD 5.1-compliant, and legally safe environment.

## How It Works

```
Player Input → LLM Processing → Narrative Response → Campaign State Update
     ↓              ↓                ↓                    ↓
Natural Language → Context Analysis → Story Generation → Persistent Save
     ↓              ↓                ↓                    ↓
Character Creation → Memory Systems → Emotional Tracking → Campaign Progression
```

### Core Flow
1. **Start Screen** → Choose to begin new campaign or continue existing
2. **Vibe Code Creation** → Natural conversation with AI to build your character
3. **Narrative Gameplay** → Immersive storytelling with persistent campaign state
4. **Save & Continue** → Seamless persistence across sessions

## Key Features

- **🎯 Start Screen**: Begin a new campaign, continue, or delete existing campaigns
- **💬 Vibe Code Character Creation**: Create a character through natural conversation with the LLM (GPT-4o-mini or compatible)
- **📋 SRD-Compliant Character Data**: All character data is saved in a structured, open format
- **📖 Immersive Narrative Gameplay**: Seamless transition into a pure narrative interface, with the LLM acting as DM
- **💾 Persistent Campaigns**: Save, load, and delete campaigns with persistent storage
- **📱 Mobile-Responsive UI**: Clean, thematic, and immersive design

## Quick Start

### Prerequisites
- Python 3.9+ (3.13 recommended)
- Optional: Local LLM service for AI features

### Installation & Launch

#### **Option 1: One-Command Setup (Recommended)**
```bash
# On macOS/Linux:
./install_and_launch.sh

# On Windows:
install_and_launch.bat
```

#### **Option 2: Manual Setup**
1. **Clone the repository**:
   ```bash
   git clone https://github.com/PianomanSJPM/solo-rp-game-demo.git
   cd solo-rp-game-demo/SoloHeart
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch SoloHeart**:
   ```bash
   python launch_soloheart.py
   ```

### LLM Setup (Optional)
SoloHeart works completely offline, but you can enhance it with AI features:

```bash
# Option 1: Use Gemma3 via LM Studio (recommended)
# 1. Install LM Studio from https://lmstudio.ai
# 2. Download and load a Gemma 3 model
# 3. Start LM Studio server at http://localhost:1234/v1

# Option 2: Use Ollama (alternative)
# 1. Install Ollama from https://ollama.ai
# 2. Run: ollama pull llama3
# 3. The game will auto-detect and use Ollama
```

### Access the Game
- **Game URL**: [http://localhost:5003](http://localhost:5003)
- **Health Check**: [http://localhost:5003/health](http://localhost:5003/health)

## Demo Walkthrough

### 1. Start a New Campaign
- Click "Start New Campaign" and follow the prompts
- Choose your preferred character creation method

### 2. Vibe Code Character Creation
- Select the natural language option
- Converse with the AI to describe your character concept
- The LLM will ask clarifying questions and build your character sheet

### 3. Immersive Gameplay
- After character creation, transition directly into narrative gameplay
- Respond naturally to the AI DM's storytelling
- Your choices and character development are tracked and remembered

### 4. Campaign Management
- Return to the start screen to continue or delete campaigns
- All progress is automatically saved and persistent

## Screenshots

![Demo Screenshot](demo_screenshot.txt)

*Screenshot showing the start screen, character creation flow, and narrative gameplay interface*

> _Replace with actual screenshots of the start screen, character creation, and narrative interface_

## LLM Configuration

SoloHeart uses a pluggable LLM adapter system that supports multiple local LLM backends:

### Supported Backends
- **Gemma3 (LM Studio)** - Default, recommended for best performance
- **Ollama** - Alternative with LLaMA 3 support
- **llama.cpp** - Coming soon

### Configuration
The LLM backend is configured in `settings.json`:

```json
{
  "llm": {
    "backend": "gemma",
    "endpoint": "http://localhost:1234/v1",
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

### Switching Backends
To use a different LLM backend:

1. **Update settings.json**:
   ```json
   {
     "llm": {
       "backend": "ollama",
       "endpoint": "http://localhost:11434"
     }
   }
   ```

2. **Or use environment variables**:
   ```bash
   export LLM_BACKEND=ollama
   export LLM_ENDPOINT=http://localhost:11434
   ```

3. **Restart the game** to apply changes

## Technology Stack

- **Backend**: Python, Flask, Narrative Engine LLM adapters
- **Frontend**: HTML5, CSS3, JavaScript
- **Character System**: SRD 5.1-compliant JSON schema
- **AI Integration**: Pluggable LLM adapter system (Gemma3, Ollama, etc.)
- **Storage**: Local file-based persistence

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

### Compliance Notes
The compliance checker has been updated to allow professional terminology related to memory testing and UI polish. Please ensure new contributions follow WCAG guidelines and avoid SRD-restricted language, but false positives may be reviewed and approved.

## Governance

This repository follows strict governance principles to maintain game development standards, SRD compliance, and architectural integrity:

- **[IMPLEMENTATION_GOVERNANCE.md](IMPLEMENTATION_GOVERNANCE.md)** - Complete governance documentation and constraints
- **[docs/GOVERNANCE.md](docs/GOVERNANCE.md)** - Summary of governance expectations
- **[docs/dev_onboarding.md](docs/dev_onboarding.md)** - Developer onboarding guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

All contributions must pass governance enforcement tests and comply with SRD 5.1 requirements.

## Documentation

- [Investor Documentation](investor_docs/) - Project overview, features, and future vision
- [Attribution](solo_heart/ATTRIBUTION.md) - Legal compliance and attributions

## Attribution

This project uses content from the Systems Reference Document 5.1 (SRD 5.1) by Wizards of the Coast LLC, available under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

- SRD 5.1: https://dnd.wizards.com/resources/systems-reference-document
- License: https://creativecommons.org/licenses/by/4.0/

This project uses the OpenAI API for natural language processing and LLM-driven gameplay.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 🚀 MVP Pitch: Why This Integration Matters

SoloHeart now integrates fully with The Narrative Engine (TNE), enabling longform storytelling with memory injection, symbolic goal inference, session journaling, and graceful fallback logic.

All 8 MVP criteria have been met and validated with automated tests.

This confirms readiness for public deployment, collaborator onboarding, and external stakeholder review.

**Key wins:**
- ✅ Modular, testable architecture
- ✅ Memory + goal alignment loop complete
- ✅ Full support for mock and live TNE modes
- ✅ Ready for CI/CD and Render deployment

**Technical Achievements:**
- **Memory Injection**: Real-time event streaming to TNE
- **Goal Inference**: AI-powered narrative goal suggestions
- **Session Journaling**: Automated campaign documentation
- **Fallback Logic**: Graceful degradation when TNE unavailable
- **Dashboard Sync**: Live goal alignment visualization
- **Compliance**: Production-ready code standards

**Integration Status:** Production-ready as of 2025-07-17
