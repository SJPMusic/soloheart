#!/bin/bash

# SoloHeart Launch Script
# Simple one-command launcher for SoloHeart

echo "🎮 Launching SoloHeart..."
echo "================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi

# Run the Python launcher
python3 launch_soloheart.py

# If the launcher exits with an error, show helpful message
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ SoloHeart failed to launch"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Make sure you're in the SoloHeart directory"
    echo "   2. Check that Python 3.8+ is installed"
    echo "   3. Try running: python3 launch_soloheart.py"
    echo "   4. Check the error messages above for specific issues"
    echo ""
    echo "📞 If problems persist, check the documentation or create an issue"
    exit 1
fi 