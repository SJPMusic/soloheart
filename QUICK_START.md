# 🎮 SoloHeart Quick Start Guide

## For Testers

### Option 1: Simple Start (Recommended)
```bash
cd SoloHeart
python3 launch_server.py
```

That's it! The server will start on **http://localhost:5001**

### Option 2: Manual Start
If the simple start doesn't work:

1. **Navigate to SoloHeart directory:**
   ```bash
   cd SoloHeart
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # macOS/Linux
   # OR
   venv\Scripts\activate     # Windows
   ```

3. **Start the server:**
   ```bash
   cd game_app
   python main_app.py
   ```

4. **Open your browser to:** http://localhost:5001

### Option 3: Debug Mode
If you're having issues, try the debug launcher:
```bash
cd SoloHeart
python3 launch_server.py
```
This will show detailed startup information and handle process management automatically.

## Troubleshooting

### "Virtual environment not found"
```bash
cd SoloHeart
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Kill any existing processes
pkill -f "python.*main_app.py"
# Then try starting again
```

### "Module not found"
```bash
cd SoloHeart
source venv/bin/activate
pip install -r requirements.txt
```

## What You Should See

1. **Server starts** with messages like:
   ```
   🚀 Starting SoloHeart Server...
   ✅ Found Python: /path/to/venv/bin/python
   ✅ Found main app: /path/to/game_app/main_app.py
   🌐 Starting server on http://localhost:5001
   ✅ Server is running successfully!
   ```

2. **Browser opens** to http://localhost:5001

3. **Character creation interface** loads

## Need Help?

If you're still having issues, please:
1. Check that you're in the `SoloHeart` directory
2. Make sure the virtual environment exists (`venv` folder)
3. Try the simple start first: `python start_server.py` 