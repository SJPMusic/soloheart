# 🌍 Welcome to SoloHeart

## 🧠 AI Meets Storytelling

SoloHeart is a solo RPG engine powered by The Narrative Engine (TNE). It tracks your actions, interprets your goals, and builds a persistent story as you play.

### 🎯 What Makes SoloHeart Special

**Memory-Aware AI**: Every action you take is remembered and analyzed by an intelligent memory system that understands narrative context.

**Goal-Driven Storytelling**: The AI suggests meaningful narrative goals based on your character's journey, creating a dynamic story that evolves with your choices.

**Persistent World**: Your campaign world persists across sessions, with detailed journals and character development tracking.

**Graceful Fallback**: When AI services are unavailable, SoloHeart continues to function with intelligent fallback behavior.

## 🚀 Features

### Core Capabilities
- **Symbolic Goal Modeling**: AI-powered narrative goal suggestions
- **Memory-Aware Interactions**: Persistent memory of campaign events
- **Narrative Journaling**: Automated session documentation in multiple formats
- **Mock and Live Modes**: Full testing capabilities with or without external services
- **Real-time Dashboard**: Live goal visualization and campaign tracking

### Technical Excellence
- **Full Test Coverage**: Comprehensive automated testing suite
- **Modular Architecture**: Clean separation of concerns
- **CI/CD Ready**: Automated deployment and testing
- **Open Source**: Transparent, community-driven development

## 🧪 Try It Out

### Quick Start
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SoloHeart
   ```

2. **Run the integration test suite**
   ```bash
   python tests/full_mvp_integration_test.py --mode mock
   ```

3. **Start the frontend dashboard**
   ```bash
   cd frontend && npm install && npm run dev
   ```

4. **Visit the dashboard**
   Open `http://localhost:5173` in your browser

### Live Mode (Full AI Integration)
For the complete experience with AI-powered goal suggestions:

1. **Start TNE backend**
   ```bash
   cd ../TNE
   source venv/bin/activate
   uvicorn api.narrative_api:app --reload --port 5001
   ```

2. **Run tests with live integration**
   ```bash
   cd ../SoloHeart
   python tests/full_mvp_integration_test.py --mode live
   ```

## 🎮 Use Cases

### For Writers
- **Generate narrative goals** based on character actions
- **Maintain consistent story arcs** across multiple sessions
- **Export campaign journals** in JSON and Markdown formats
- **Track character development** over time

### For Solo Gamers
- **AI-powered goal suggestions** during gameplay
- **Persistent memory** of campaign events and decisions
- **Automated session documentation** for campaign continuity
- **Dynamic story evolution** based on player choices

### For Developers
- **Modular, testable architecture** for easy extension
- **Clear separation of concerns** between components
- **Comprehensive test coverage** for reliable development
- **CI/CD ready deployment** with Render configuration

## 🏗️ Architecture

### System Components
```
SoloHeart Frontend (React) 
    ↓
SoloHeart Backend (Python)
    ↓
TNE Bridge (Memory Injection)
    ↓
The Narrative Engine (Goal Inference)
```

### Key Modules
- **`integrations/tne_bridge.py`**: Handles communication with TNE
- **`integrations/tne_event_mapper.py`**: Maps game actions to memory events
- **`tests/full_mvp_integration_test.py`**: Comprehensive test suite
- **`scripts/finalize_mvp_release.py`**: Release automation

## 📊 Test Coverage

All critical integration areas have automated test coverage:

- ✅ **System Readiness**: Module imports, environment setup, data validation
- ✅ **Memory Injection**: Event streaming, TNE API integration, error handling
- ✅ **Goal Inference**: AI-powered suggestions, pattern analysis, confidence scoring
- ✅ **Session Journal Export**: JSON and Markdown formats, campaign persistence
- ✅ **Bridge Integration**: Complete SoloHeart → TNE event mapping cycle
- ✅ **Fallback Behavior**: Graceful degradation when TNE unavailable
- ✅ **Goal Dashboard Sync**: Real-time UI updates, polling, data formatting
- ✅ **Compliance Validation**: Code standards, restricted term filtering

## 🔧 Technical Requirements

- **Python 3.11+** for backend services
- **Node.js 18+** for frontend development
- **FastAPI** for TNE backend communication
- **React + TypeScript** for frontend dashboard
- **OpenRouter API** for AI inference (optional)

## 🚀 Deployment

SoloHeart includes complete deployment configuration:

- **Render Deployment**: Automatic deployment with environment variable management
- **GitHub Actions**: CI/CD pipeline with automated testing
- **Docker Support**: Containerized deployment options
- **Environment Management**: Secure secret handling

## 💡 Built For

### Writers and Storytellers
Create dynamic narratives with AI-powered goal suggestions and persistent world-building.

### Solo Roleplayers
Experience rich, evolving campaigns with intelligent story progression and detailed session tracking.

### Narrative Theorists
Study AI-driven storytelling and symbolic goal modeling in action.

### AI Developers
Explore modular architecture patterns and memory-aware AI integration techniques.

### Open Source Contributors
Join a community-driven project with comprehensive testing and clear contribution guidelines.

## 🤝 Contributing

We welcome contributions! SoloHeart is built on:

- **Comprehensive Testing**: Write tests for all new features
- **Clear Documentation**: Document your changes and additions
- **Modular Design**: Follow established architectural patterns
- **Community Standards**: Respect our code of conduct and contribution guidelines

## 📚 Documentation

- **[Developer Onboarding](docs/dev_onboarding.md)**: Complete setup and development guide
- **[Release Notes](RELEASE_NOTES.md)**: Latest features and changes
- **[Test Coverage](tests/coverage_mvp_report.md)**: Detailed testing information
- **[Security Guide](docs/repo_hardening.md)**: Repository security best practices

## 🎬 See It In Action

Watch our [launch trailer script](docs/launch_trailer_script.md) to see SoloHeart's capabilities in action, or dive right in with the quick start guide above.

---

## Ready to tell your story?

**SoloHeart starts here.**

*Your imagination. Our engine. Infinite possibilities.* 