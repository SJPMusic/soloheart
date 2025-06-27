# DnD 5E AI-Powered Campaign Manager

An intelligent campaign management system for Dungeons & Dragons 5th Edition that uses AI to read and understand session logs like AI reads code, maintaining perfect continuity and generating dynamic content.

## 🎯 Overview

This project creates a sophisticated DnD campaign manager that leverages AI to:
- **Read session logs like AI reads code** - Building comprehensive mental models of campaign events
- **Maintain perfect continuity** - Tracking entities, relationships, and story threads across sessions
- **Generate dynamic content** - Creating NPCs, locations, and quests that fit seamlessly into your campaign
- **Support "vibe coding"** - Create characters from natural language descriptions
- **Provide intelligent suggestions** - AI-powered recommendations based on campaign context

## 🚀 Key Features

### 🧠 AI Memory System
- **Entity Extraction**: Automatically identifies and tracks NPCs, locations, items, and events
- **Relationship Mapping**: Builds connections between campaign elements
- **Context Awareness**: Understands how past events influence current situations
- **Continuity Tracking**: Maintains perfect memory across multiple sessions

### 🎭 Character Management
- **Vibe Coding**: Create characters from natural language descriptions
- **5E Compliance**: Full DnD 5th Edition rules integration
- **Custom Flavor**: Add unique traits and abilities
- **Progressive Development**: Track character growth and development

### 📝 Session Logging
- **Real-time Logging**: Capture dialogue, actions, and decisions
- **Automatic Processing**: Extract entities and relationships from session data
- **Comprehensive Summaries**: Generate detailed session reports
- **Export Capabilities**: Save and share session data

### 🤖 AI Content Generation
- **Dynamic NPCs**: Generate characters that fit your campaign world
- **Living Locations**: Create immersive environments with rich descriptions
- **Engaging Quests**: Design adventures that build on campaign history
- **Context-Aware**: All content considers your campaign's established lore

## 🏗️ Architecture

```
DnD Campaign Manager
├── core/
│   ├── memory_system.py      # AI-powered memory and continuity
│   ├── ai_content_generator.py # Dynamic content generation
│   ├── character_manager.py   # Character creation and management
│   └── session_logger.py     # Session capture and processing
├── campaigns/                # Campaign data storage
├── main.py                  # Main application interface
└── requirements.txt         # Dependencies
```

### Core Systems

#### Memory System (`core/memory_system.py`)
The heart of the AI system that reads session logs like AI reads code:

```python
# Example: How the memory system processes session data
memory_system = CampaignMemorySystem("campaign_data")

# Add session log - AI processes it like reading code
memory_system.add_campaign_memory(
    memory_type='dialogue',
    content="Gandalf: 'The ring must be destroyed in Mount Doom'",
    session_id='session_001'
)

# AI builds mental model of entities and relationships
# Gandalf -> knows about ring -> knows about Mount Doom -> understands quest
```

#### AI Content Generator (`core/ai_content_generator.py`)
Generates dynamic content that fits seamlessly into your campaign:

```python
# Generate NPC that fits your campaign context
npc = ai_generator.generate_npc({
    'location_type': 'forest',
    'quest_type': 'magical',
    'player_levels': {'Alice': 3, 'Bob': 3}
})
```

#### Character Manager (`core/character_manager.py`)
Creates characters from "vibe coding" descriptions:

```python
# Create character from natural language
character = character_manager.create_character_from_vibe(
    player_name="Alice",
    vibe_description="A mysterious elven wizard who speaks in riddles",
    preferences={'custom_description': 'Tall with silver hair'}
)
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/dnd-ai-campaign-manager.git
   cd dnd-ai-campaign-manager
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## 📖 Usage Guide

### Creating Your First Campaign

```python
from main import DnDCampaignManager

# Create campaign manager
campaign = DnDCampaignManager("My Epic Campaign")

# Create character using vibe coding
character = campaign.create_character_from_vibe(
    player_name="Alice",
    vibe_description="A brave human fighter who protects the innocent",
    preferences={'custom_description': 'Tall and muscular with a scar on her cheek'}
)

print(f"Created: {character.name} - {character.race.value} {character.character_class.value}")
```

### Running a Session

```python
# Start session
session = campaign.start_session("session_001")

# Log activities
campaign.log_dialogue("Gandalf", "Welcome to Rivendell, young adventurers")
campaign.log_action("Alice", "draws sword", "ready for battle")
campaign.log_exploration("Rivendell", "Elven city with flowing waterfalls", ["ancient library", "healing springs"])

# Generate content
npc = campaign.generate_npc({'location_type': 'elven_city', 'quest_type': 'diplomatic'})
print(f"New NPC: {npc.content}")

# End session
summary = campaign.end_session()
print(f"Session complete! Visited: {summary.locations_visited}")
```

### Using AI Memory

```python
# Search campaign memory
results = campaign.search_campaign_memory("Gandalf")
print(f"Found {len(results)} references to Gandalf")

# Get campaign summary
summary = campaign.get_campaign_summary()
print(f"Campaign has {summary['total_sessions']} sessions and {summary['total_entities']} entities")
```

## 🎮 Advanced Features

### AI-Powered Suggestions

The system provides intelligent suggestions based on your campaign context:

```python
# Get character-specific suggestions
suggestions = campaign.get_character_suggestions("Alice", "facing a locked door")
print("Suggestions:", suggestions)
# Output: ["Consider using your combat abilities", "Your courageous nature suggests a direct approach"]
```

### Dynamic Content Generation

Generate content that adapts to your campaign:

```python
# Generate quest that fits your campaign
quest = campaign.generate_quest({
    'player_levels': {'Alice': 3, 'Bob': 3},
    'location_name': 'Rivendell',
    'active_quests': 2
})
```

### Campaign Continuity

The AI maintains perfect continuity across sessions:

```python
# Session 1: Introduce NPC
campaign.log_dialogue("Gandalf", "I am Gandalf the Grey")

# Session 5: AI remembers and builds on previous interactions
campaign.log_dialogue("Gandalf", "As I mentioned before, the ring is dangerous")
# AI automatically connects this to the previous mention of the ring
```

## 🔧 Configuration

### Campaign Settings

```python
# Customize campaign settings
campaign.campaign_settings.update({
    'world_name': 'Middle-earth',
    'difficulty': 'hard',
    'magic_level': 'high',
    'ai_assistance_level': 'high'
})
campaign._save_campaign_settings(campaign.campaign_settings)
```

### AI Memory Configuration

```python
# Configure memory system
memory_system = CampaignMemorySystem(
    data_dir="custom_campaign_data",
    max_memory_size=10000,
    search_depth=5
)
```

## 📊 Data Management

### Export Campaign Data

```python
# Export all campaign data
export_file = campaign.export_campaign_data("my_campaign_export.json")
print(f"Campaign exported to: {export_file}")
```

### Backup and Restore

```python
# Create backup
backup_file = campaign.backup_campaign()
print(f"Backup created: {backup_file}")

# Restore from backup (implement as needed)
# campaign.restore_from_backup(backup_file)
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=core tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 core/ tests/

# Run type checking
mypy core/

# Format code
black core/ tests/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Dungeons & Dragons 5th Edition** - Wizards of the Coast
- **AI/ML Community** - For inspiration on AI-powered applications
- **DnD Community** - For feedback and testing

## 🚧 Roadmap

### Phase 1: Core Systems ✅
- [x] AI Memory System
- [x] Character Management
- [x] Session Logging
- [x] Basic Content Generation

### Phase 2: Enhanced AI 🤖
- [ ] Advanced NLP for better entity extraction
- [ ] Machine learning for content quality
- [ ] Predictive story suggestions
- [ ] Voice integration for session logging

### Phase 3: Web Interface 🌐
- [ ] Web-based campaign dashboard
- [ ] Real-time session collaboration
- [ ] Mobile app for on-the-go logging
- [ ] Integration with popular VTT platforms

### Phase 4: Advanced Features 🎯
- [ ] Multi-language support
- [ ] Campaign templates and sharing
- [ ] Advanced analytics and insights
- [ ] Integration with DnD Beyond API

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/dnd-ai-campaign-manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/dnd-ai-campaign-manager/discussions)
- **Email**: your.email@example.com

---

**Happy adventuring! May your campaigns be epic and your AI companions wise! 🐉⚔️** 