# Contributing to Solo Narrative Engine Demo

## Project Goals

The Solo Narrative Engine Demo is a proof-of-concept that showcases an immersive, LLM-powered solo DnD 5E experience. Our goal is to demonstrate how AI can create compelling, personalized storytelling experiences while maintaining SRD 5.2 compliance and legal safety.

## Getting Started

### Prerequisites
- Python 3.9+
- OpenAI API key
- Git

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/PianomanSJPM/solo-rp-game-demo.git
   cd solo-rp-game-demo/dnd_game
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.template .env
   # Add your OpenAI API key to .env
   ```

4. Start the demo servers:
   ```bash
   # Terminal 1: Start screen (port 5001)
   python start_screen_interface.py
   
   # Terminal 2: Narrative gameplay (port 5002)
   python narrative_focused_interface.py
   ```

5. Open your browser:
   - Start screen: http://localhost:5001
   - Narrative gameplay: http://localhost:5002

## Contribution Areas

### Frontend & UI
- **Templates**: HTML templates for start screen, character creation, narrative interface
- **Styling**: CSS improvements, mobile responsiveness, thematic design
- **JavaScript**: Interactive features, real-time updates, smooth transitions

### Backend Logic
- **Character System**: Character creation, validation, management
- **Campaign Management**: Save/load, persistence, campaign state
- **Narrative Engine**: LLM integration, story generation, context management

### Memory Systems
- **Emotional Memory**: Character emotional states and memory
- **Campaign Memory**: Persistent story elements and progression
- **Context Management**: Maintaining narrative coherence

### Character Parser Improvements
- **Natural Language Processing**: Better understanding of player input
- **Character Generation**: Enhanced LLM prompts and response parsing
- **Validation**: Improved character data validation and error handling

### Testing & Quality
- **Unit Tests**: Core functionality testing
- **Integration Tests**: End-to-end workflow testing
- **Performance**: Optimization and scalability improvements

## Code Style Guidelines

### Python
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and under 50 lines when possible

### JavaScript
- Use ES6+ features
- Follow consistent naming conventions
- Add comments for complex logic

### HTML/CSS
- Use semantic HTML elements
- Follow BEM methodology for CSS classes
- Ensure accessibility standards are met

## Commit Message Guidelines

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(character): add natural language character creation
fix(ui): resolve mobile responsiveness issues
docs(readme): update installation instructions
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the style guidelines
4. Test your changes thoroughly
5. Commit your changes with clear commit messages
6. Push to your fork and submit a pull request
7. Ensure the PR description clearly describes the problem and solution

## Questions or Need Help?

- Open an issue for bugs or feature requests
- Use GitHub Discussions for questions and ideas
- Join our community discussions about the Narrative Engine

Thank you for contributing to the Solo Narrative Engine Demo! 