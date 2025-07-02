# 🌿 SoloHeart Branch Strategy

## Overview
This document outlines our Git branch strategy for organizing development work and making it easier for others to evaluate our progress.

## Branch Structure

### 🎯 Main Branch (`main`)
- **Purpose**: Production-ready, stable code
- **Protection**: Requires pull request reviews
- **Deployment**: Auto-deploys to production
- **Content**: Only tested, working features

### 🌿 Feature Branches
Create separate branches for each major feature or improvement:

#### Current Active Branches:
- `feature/bug-fixes-and-improvements` - Current branch for fixing issues
- `feature/character-creation-improvements` - Character creation enhancements
- `feature/ollama-integration` - LLM backend improvements
- `feature/ui-enhancements` - User interface improvements
- `feature/memory-system` - Memory and continuity features

#### Branch Naming Convention:
```
feature/descriptive-name
bugfix/issue-description
hotfix/critical-fix
docs/documentation-update
```

## Workflow

### 1. Starting New Work
```bash
# Create and switch to new feature branch
git checkout -b feature/your-feature-name

# Or create from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### 2. Development Process
```bash
# Make your changes
# Commit frequently with descriptive messages
git add .
git commit -m "feat: add character creation improvements

- Enhanced fact extraction logic
- Added comprehensive debugging
- Fixed file path issues
- Improved natural language handling"

# Push to remote
git push origin feature/your-feature-name
```

### 3. Code Review Process
1. Create Pull Request (PR) from feature branch to main
2. Add detailed description of changes
3. Request reviews from team members
4. Address feedback and make changes
5. Merge when approved

### 4. Merging Strategy
```bash
# Option 1: Merge commit (preserves branch history)
git checkout main
git merge feature/your-feature-name

# Option 2: Squash merge (clean history)
git checkout main
git merge --squash feature/your-feature-name
git commit -m "feat: complete feature description"

# Push to remote
git push origin main
```

## Commit Message Convention

### Format:
```
type(scope): description

[optional body]

[optional footer]
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples:
```
feat(character): add step-by-step character creation flow

fix(ollama): resolve connection timeout issues

docs(readme): update installation instructions

refactor(memory): improve vector memory performance
```

## Branch Organization for Evaluation

### For Investors/Stakeholders:
- **`main`**: Always working, production-ready code
- **`feature/demo-ready`**: Features ready for demonstration
- **`feature/milestone-1`**: First major milestone features

### For Developers:
- **`feature/experimental`**: Experimental features and prototypes
- **`feature/research`**: Research and exploration branches
- **`feature/performance`**: Performance optimization work

### For Testing:
- **`feature/integration-tests`**: Integration testing work
- **`feature/unit-tests`**: Unit testing improvements
- **`feature/e2e-tests`**: End-to-end testing

## Current Project Status

### ✅ Completed Features (in main):
- Basic character creation system
- Ollama LLM integration
- Web interface foundation
- Memory system architecture

### 🔄 In Progress (feature branches):
- Character creation improvements (bug-fixes-and-improvements)
- Enhanced fact extraction
- Better error handling
- Comprehensive debugging

### 📋 Planned Features:
- Advanced memory system
- UI/UX improvements
- Performance optimizations
- Additional game mechanics

## Best Practices

### 1. Keep Branches Focused
- One feature per branch
- Keep branches small and manageable
- Regular commits with clear messages

### 2. Regular Updates
- Pull latest changes from main regularly
- Resolve conflicts early
- Keep feature branches up to date

### 3. Documentation
- Update README.md for major changes
- Document new features
- Keep branch descriptions current

### 4. Testing
- Test features before merging
- Include tests with new features
- Ensure CI/CD pipeline passes

## Quick Reference Commands

```bash
# See all branches
git branch -a

# Switch to main
git checkout main

# Create new feature branch
git checkout -b feature/new-feature

# Update branch with latest main
git checkout main
git pull origin main
git checkout feature/your-branch
git merge main

# Push new branch to remote
git push -u origin feature/new-feature

# Delete local branch after merge
git branch -d feature/completed-feature

# Delete remote branch
git push origin --delete feature/completed-feature
```

## Evaluation Guidelines

### For Code Reviewers:
1. Check the feature branch description
2. Review commit history for logical progression
3. Test the feature if possible
4. Check for proper error handling
5. Verify documentation updates

### For Stakeholders:
1. Check `main` branch for stable features
2. Review `feature/demo-ready` for upcoming features
3. Look at commit frequency and quality
4. Check for proper testing and documentation

This branch strategy ensures organized development, clear progress tracking, and easy evaluation of work quality and progress. 