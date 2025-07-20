#!/bin/bash
# SoloHeart Installation Script
# This script sets up SoloHeart for first-time use

set -e  # Exit on any error

echo "🎲 SoloHeart Installation"
echo "========================"

# Check if Python 3.9+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "   Please install Python 3.9 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ SoloHeart installation complete!"
echo ""
echo "🚀 To start SoloHeart, run:"
echo "   python run.py"
echo ""
echo "💡 Or if you prefer:"
echo "   ./venv/bin/python run.py"
echo "" 