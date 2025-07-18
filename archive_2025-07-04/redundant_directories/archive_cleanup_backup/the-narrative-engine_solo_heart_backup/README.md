This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

# SoloHeart Game Engine (SRD 5.1-Compliant)

## Project Summary
This is a proof-of-concept demo for the Narrative Engine: an immersive, LLM-powered solo DnD 5E experience. The system enables a single player to create a character using natural language and play through a campaign with an AI Dungeon Master, all in a clean, SRD 5.1-compliant, and legally safe environment.

## Key Features
- **Start Screen**: Begin a new campaign, continue, or delete existing campaigns
- **Vibe Code Character Creation**: Create a character through natural conversation with the LLM (GPT-4o-mini or compatible)
- **SRD-Compliant Character Data**: All character data is saved in a structured, open format
- **Immersive Narrative Gameplay**: Seamless transition into a pure narrative interface, with the LLM acting as DM
- **Persistent Campaigns**: Save, load, and delete campaigns with persistent storage
- **Mobile-Responsive UI**: Clean, thematic, and immersive design

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
3. Set up your OpenAI API key:
   - Copy `.env.template` to `.env` and add your OpenAI API key

## Running the Demo
1. Start the start screen interface (port 5001):
   ```
   python start_screen_interface.py
   ```
2. In a new terminal, start the narrative interface (port 5002):
   ```
   python narrative_focused_interface.py
   ```
3. Open your browser:
   - Start screen: [http://localhost:5001](http://localhost:5001)
   - Narrative gameplay: [http://localhost:5002](http://localhost:5002)

## Demo Instructions
1. **Start a New Campaign**: Click "Start New Campaign" and follow the prompts
2. **Vibe Code Character Creation**: Choose the natural language option and converse with the LLM to create your character
3. **Play**: After character creation, transition directly into immersive narrative gameplay
4. **Continue or Delete**: Return to the start screen to continue or delete campaigns

## Screenshots
> _Add screenshots of the start screen, character creation, and narrative interface here_

## Attribution
See [ATTRIBUTION.md](ATTRIBUTION.md) for full details.
- SRD 5.1 by Wizards of the Coast, licensed under CC BY 4.0
- OpenAI API for LLM-driven gameplay 