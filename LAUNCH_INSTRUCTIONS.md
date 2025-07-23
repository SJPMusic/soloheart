# 🎮 SoloHeart Launch Instructions

## Quick Start

### Option 1: One-Command Launch (Recommended)
```bash
./launch.sh
```

### Option 2: Python Launcher
```bash
python3 launch_soloheart.py
```

## What the Launcher Does

The SoloHeart launcher automatically handles:

✅ **Python Version Check** - Ensures Python 3.8+ is installed  
✅ **Virtual Environment** - Creates and activates the virtual environment  
✅ **Dependencies** - Installs all required packages  
✅ **Port Check** - Ensures port 5002 is available  
✅ **Server Startup** - Starts the SoloHeart server  
✅ **Browser Launch** - Opens the character creation page  
✅ **Status Display** - Shows server URLs and next steps  

## Expected Experience

1. **Launch**: Run `./launch.sh` or `python3 launch_soloheart.py`
2. **Setup**: Watch the launcher handle all setup automatically
3. **Browser**: Your browser opens to the character creation page
4. **Create**: Describe your character in natural language
5. **Play**: Start your D&D adventure!

## Example Character Creation

Try this in the character creation interface:

> "My name is Elira. I'm an elven druid who survived a forest fire and now protects nature. I'm brave and mysterious, having learned ancient druidic secrets."

The AI will guide you through the rest of the character creation process.

## Troubleshooting

### Port Already in Use
If you see "Port 5002 is in use":
```bash
# Find what's using the port
lsof -i :5002

# Kill the process (replace PID with actual process ID)
kill -9 PID
```

### Virtual Environment Issues
If the virtual environment is corrupted:
```bash
# Remove and recreate
rm -rf venv
python3 launch_soloheart.py
```

### Dependencies Issues
If packages fail to install:
```bash
# Update pip
python3 -m pip install --upgrade pip

# Try again
python3 launch_soloheart.py
```

## Server URLs

Once launched, SoloHeart is available at:

- **Character Creation**: http://localhost:5002/vibe-code-creation
- **Main Page**: http://localhost:5002/
- **Health Check**: http://localhost:5002/health

## Stopping SoloHeart

Press `Ctrl+C` in the terminal where you launched SoloHeart to stop the server.

## Support

If you encounter issues:

1. Check the error messages in the terminal
2. Ensure Python 3.8+ is installed
3. Make sure you're in the SoloHeart directory
4. Try the troubleshooting steps above

The launcher provides clear feedback at each step to help identify and resolve any issues. 