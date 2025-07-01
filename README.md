# 🎲 Solo Narrative Engine Demo

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
- Python 3.9+
- OpenAI API key

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/PianomanSJPM/solo-rp-game-demo.git
   cd solo-rp-game-demo/dnd_game
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**:
   ```bash
   cp .env.template .env
   # Add your OpenAI API key to .env
   ```

### Running the Demo
1. **Start the start screen interface** (port 5001):
   ```bash
   python start_screen_interface.py
   ```

2. **In a new terminal, start the narrative interface** (port 5002):
   ```bash
   python narrative_focused_interface.py
   ```

3. **Open your browser**:
   - Start screen: [http://localhost:5001](http://localhost:5001)
   - Narrative gameplay: [http://localhost:5002](http://localhost:5002)

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

## Technology Stack

- **Backend**: Python, Flask, OpenAI API
- **Frontend**: HTML5, CSS3, JavaScript
- **Character System**: SRD 5.1-compliant JSON schema
- **AI Integration**: GPT-4o-mini for natural language processing
- **Storage**: Local file-based persistence

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## Documentation

- [Investor Documentation](investor_docs/) - Project overview, features, and future vision
- [Attribution](dnd_game/ATTRIBUTION.md) - Legal compliance and attributions

## Attribution

This project uses content from the Systems Reference Document 5.1 (SRD 5.1) by Wizards of the Coast LLC, available under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

- SRD 5.1: https://dnd.wizards.com/resources/systems-reference-document
- License: https://creativecommons.org/licenses/by/4.0/

This project uses the OpenAI API for natural language processing and LLM-driven gameplay.
- https://openai.com/

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
