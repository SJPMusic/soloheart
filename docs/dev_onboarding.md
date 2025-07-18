# 🧠 Developer Onboarding Guide

Welcome to SoloHeart!

This project integrates a solo RPG frontend with a symbolic memory + goal inference backend. To get started:

## 🎯 Project Overview

SoloHeart is a solo roleplaying engine that:
- **Tracks player actions** and injects them into The Narrative Engine (TNE)
- **Infers narrative goals** using AI-powered analysis
- **Generates session journals** in multiple formats
- **Provides fallback behavior** when TNE is unavailable
- **Offers a React dashboard** for real-time goal visualization

## 🔧 Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SoloHeart
```

### 2. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
OPENROUTER_API_KEY=your_api_key_here
TNE_BASE_URL=http://localhost:5001
```

## 🚀 Running the Application

### Option 1: Mock Mode (Recommended for Development)
```bash
# Run the integration test suite in mock mode
python tests/full_mvp_integration_test.py --mode mock

# Start the frontend dashboard
cd frontend && npm run dev
```

### Option 2: Live Mode (Full TNE Integration)
```bash
# Terminal 1: Start TNE API
cd ../TNE
source venv/bin/activate
uvicorn api.narrative_api:app --reload --port 5001

# Terminal 2: Run SoloHeart tests
cd ../SoloHeart
python tests/full_mvp_integration_test.py --mode live

# Terminal 3: Start frontend
cd frontend && npm run dev
```

## 🧪 Testing

### Run All Tests
```bash
python tests/full_mvp_integration_test.py --mode mock
```

### Run Specific Test Categories
```bash
# Test memory injection
python tests/full_mvp_integration_test.py --mode mock --category memory

# Test goal inference
python tests/full_mvp_integration_test.py --mode mock --category goals

# Test journal export
python tests/full_mvp_integration_test.py --mode mock --category journal
```

### Test Modes
- **`--mode mock`**: Uses mock data, no external dependencies
- **`--mode live`**: Requires TNE backend running on port 5001

## 📁 Project Structure

```
SoloHeart/
├── integrations/           # TNE integration modules
│   ├── tne_bridge.py      # Event sending and goal fetching
│   └── tne_event_mapper.py # Game action to memory mapping
├── tests/                  # Test suites
│   ├── full_mvp_integration_test.py
│   └── test_narrative_loop_mvp.py
├── scripts/                # Utility scripts
│   └── finalize_mvp_release.py
├── docs/                   # Documentation
├── frontend/               # React dashboard
└── requirements.txt        # Python dependencies
```

## 🔄 Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python tests/full_mvp_integration_test.py --mode mock

# Commit with conventional format
git commit -m "feat(scope): description of changes"
```

### 2. Testing Before Commit
```bash
# Run full test suite
python tests/full_mvp_integration_test.py --mode mock

# Check for compliance violations
python -c "import tests.full_mvp_integration_test as test; test.run_compliance_check()"
```

### 3. Pull Request Process
- Ensure all tests pass
- Update documentation if needed
- Follow conventional commit format
- Request review from maintainers

## ✅ Contribution Guidelines

### Code Standards
- **Write tests** with every feature
- **Use feature branches**: `feature/your-feature-name`
- **Follow conventional commits**: `type(scope): description`
- **All commits must pass** compliance scan
- **Document new features** in appropriate docs

### Testing Requirements
- **Unit tests** for new modules
- **Integration tests** for TNE interactions
- **Mock mode tests** for CI compatibility
- **Compliance validation** for all code

### Architecture Principles
- **Modular design**: Clear separation of concerns
- **Fallback behavior**: Graceful degradation
- **Test coverage**: Comprehensive validation
- **Documentation**: Clear usage examples

## 🐛 Debugging

### Common Issues

#### TNE Connection Problems
```bash
# Check if TNE is running
curl http://localhost:5001/health

# Restart TNE if needed
cd ../TNE && uvicorn api.narrative_api:app --reload --port 5001
```

#### Frontend Issues
```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Test Failures
```bash
# Run with verbose output
python tests/full_mvp_integration_test.py --mode mock --verbose

# Check specific test category
python tests/full_mvp_integration_test.py --mode mock --category system
```

## 📚 Additional Resources

- **README.md**: Project overview and quick start
- **RELEASE_NOTES.md**: Latest features and changes
- **docs/release_checklist_mvp.md**: Release validation checklist
- **tests/coverage_mvp_report.md**: Test coverage details

## 🤝 Getting Help

- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the docs/ directory for detailed guides

---

**Welcome to SoloHeart development! Let's build something amazing together.** 