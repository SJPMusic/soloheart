#!/bin/bash

# SoloHeart GitHub Setup Script
# This script helps you push SoloHeart to your new GitHub account

echo "🎲 SoloHeart GitHub Setup Script"
echo "=================================="

# Check if new GitHub username is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your new GitHub username"
    echo "Usage: ./setup-new-github.sh YOUR_NEW_USERNAME"
    echo ""
    echo "Example: ./setup-new-github.sh mynewaccount"
    exit 1
fi

NEW_USERNAME=$1
REPO_NAME="soloheart"

echo "✅ Setting up SoloHeart for GitHub account: $NEW_USERNAME"
echo "📦 Repository name: $REPO_NAME"
echo ""

# Remove old remotes that are suspended
echo "🧹 Cleaning up old suspended remotes..."
git remote remove newrepo 2>/dev/null || true
git remote remove demo 2>/dev/null || true
git remote remove mainrepo 2>/dev/null || true
git remote remove origin 2>/dev/null || true

# Add new remote
echo "🔗 Adding new GitHub remote..."
git remote add origin https://github.com/$NEW_USERNAME/$REPO_NAME.git

# Show current status
echo ""
echo "📊 Current Git Status:"
git status

echo ""
echo "🌐 Remote Configuration:"
git remote -v

echo ""
echo "📝 Next Steps:"
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: $REPO_NAME"
echo "   - Make it public or private as needed"
echo "   - DO NOT initialize with README (we'll push our own)"
echo ""
echo "2. Push to your new repository:"
echo "   git push -u origin feature/ollama-connection-improvements"
echo ""
echo "3. Or push to main branch:"
echo "   git push -u origin feature/ollama-connection-improvements:main"
echo ""
echo "✅ Setup complete! Your SoloHeart project is ready to push to your new GitHub account." 