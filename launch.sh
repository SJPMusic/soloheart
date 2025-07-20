#!/bin/bash
# SoloHeart Launch Script
# This script launches SoloHeart from anywhere

set -e  # Exit on any error

echo "🎲 SoloHeart Launcher"
echo "===================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📍 SoloHeart directory: $SCRIPT_DIR"

# Change to SoloHeart directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "💡 Please run: ./install.sh"
    exit 1
fi

# Check if Python exists in venv
if [ ! -f "venv/bin/python" ]; then
    echo "❌ Python not found in virtual environment"
    echo "💡 Please run: ./install.sh"
    exit 1
fi

echo "✅ Virtual environment found"
echo "🚀 Starting SoloHeart..."

# Launch SoloHeart
venv/bin/python run.py 