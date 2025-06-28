# DnD 5E AI-Powered Solo Game

⚠️ **Disclaimer**: This is an early-stage, private development project exploring original narrative AI frameworks. All content is the intellectual property of the creator. Do not reproduce, copy, or commercialize any part of this project without explicit written permission.

---

An AI-powered Dungeon Master for solo DnD 5E campaigns with persistent memory that never forgets or contradicts itself.

## 🎯 Project Overview

This project creates a conversational AI DM that provides ChatGPT-quality storytelling while maintaining perfect continuity across sessions. It solves the memory issues experienced with ChatGPT by implementing a sophisticated memory system that tracks everything about your character, the world, and your adventures.

## ✨ Key Features

- **ChatGPT-quality storytelling** - Rich, narrative responses powered by OpenAI
- **Persistent memory** - Remembers everything about your character, locations, NPCs, and story
- **Natural conversation** - Just type what you want to do, like "light the flame"
- **DnD 5E compliance** - Proper character creation, rules, and mechanics
- **Perfect continuity** - No more inconsistencies or forgotten details

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (get one at https://platform.openai.com/api-keys)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DnD-Project
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up OpenAI API key**
   ```bash
   python3 setup_openai.py
   ```
   Or manually create a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

5. **Run the game**
   ```bash
   python3 gui_interface.py
   ```

## 🎮 How to Play

### Creating Your Character
Just tell the AI about yourself naturally:
- "I'm a half-elf wizard named Gandalf who specializes in fire magic"
- "My name is Thorin, I'm a dwarf fighter with a mysterious past"

### Playing the Game
Describe what you want to do in natural language:
- "I explore the dark forest"
- "I cast fireball at the goblins"
- "I talk to the innkeeper about rumors"
- "What do I see around me?"

### The AI Remembers Everything
- Your character details and progression
- All locations you've visited
- NPCs you've met and their relationships
- Story events and quest progress
- Your choices and their consequences

## 🏗️ Architecture

### Core Systems
- **Memory System** (`core/memory_system.py`) - Advanced semantic memory with entity extraction
- **AI Content Generator** (`core/ai_content_generator.py`) - OpenAI integration for storytelling
- **Character Manager** (`core/character_manager.py`) - DnD 5E character creation and management
- **Session Logger** (`core/session_logger.py`) - Session tracking and logging
- **Campaign Manager** (`main.py`) - Orchestrates all systems

### Memory Features
- Semantic analysis and entity extraction
- Context-aware memory storage
- Relationship mapping between entities
- Continuity verification
- Advanced search capabilities

## 🧪 Testing

Test the OpenAI integration:
```bash
python3 test_openai_integration.py
```

## 📁 Project Structure

```
DnD Project/
├── core/                    # Core game systems
│   ├── memory_system.py    # Advanced memory system
│   ├── ai_content_generator.py  # OpenAI integration
│   ├── character_manager.py     # Character management
│   └── session_logger.py        # Session tracking
├── data/                   # Game data storage
├── campaigns/              # Campaign data
├── gui_interface.py        # Main GUI
├── main.py                 # Campaign manager
├── setup_openai.py         # API setup script
├── test_openai_integration.py  # Integration tests
└── requirements.txt        # Dependencies
```

## 🔧 Development Status

### ✅ Completed (Phase 1)
- Advanced memory system with semantic analysis
- OpenAI API integration
- DnD 5E character management
- GUI interface
- Session tracking
- Campaign management

### 🚧 In Progress (Phase 2)
- Enhanced AI storytelling
- Improved DnD mechanics
- Combat system
- World generation

### 📋 Planned
- Advanced quest systems
- NPC relationship tracking
- Multi-character support
- Performance optimization

## 💡 Example Interaction

**Player**: "I'm a half-elf wizard named Gandalf who specializes in fire magic"

**AI**: "Welcome, Gandalf! Your elven heritage grants you keen senses and a natural affinity for magic, while your human blood gives you the adaptability to master the arcane arts. As a wizard specializing in fire magic, you carry the warmth of the forge and the destructive power of the inferno. Your spellbook contains ancient knowledge passed down through generations of mages..."

**Player**: "I cast a light spell to illuminate the dark path"

**AI**: "The air in the Mystic Forest is thick with a palpable stillness... As you weave the intricate gestures required for your spell, a warm glow begins to emanate from your fingertips, flickering like a new flame desperately seeking breath..."

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome!

## 📄 License

This project is for personal use and educational purposes.

## 🎯 Roadmap

- **Phase 1**: Foundation ✅
- **Phase 2**: Enhancement (Current)
- **Phase 3**: Polish
- **Phase 4**: Expansion

## 📞 Support

For issues or questions, please refer to the development journal or create an issue in the repository.

---

**Status**: Foundation Complete - Ready for Enhancement Phase  
**Last Updated**: January 2025 