This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

# 🎲 How to Play Solo DnD 5E Demo

## Quick Start (2 minutes)

### 1. **Get an OpenAI API Key**
- Go to https://platform.openai.com/api-keys
- Sign up or log in
- Click "Create new secret key"
- Copy the key (it starts with `sk-`)

### 2. **Run the Game**
```bash
python consumer_launcher.py
```

### 3. **Play!**
- The game will open in your browser
- Click "Start New Campaign"
- Choose "Natural Language" for character creation
- Describe your character concept
- Start your adventure!

## 🎮 What You'll Experience

### **Character Creation**
- Tell the AI about your character concept in plain English
- Example: "I want to be a mysterious elven wizard who was exiled from their homeland"
- The AI will ask clarifying questions and build your character

### **Gameplay**
- Pure narrative storytelling with an AI Dungeon Master
- Respond naturally to the story
- Your choices and progress are automatically saved
- Return anytime to continue your campaign

## 🔧 Troubleshooting

### **"API key not found"**
- Make sure you entered your OpenAI API key correctly
- It should start with `sk-`

### **"Port already in use"**
- Close other applications that might be using ports 5001 or 5002
- Or restart your computer

### **"Module not found"**
- Run: `pip install Flask Flask-CORS openai python-dotenv jsonschema`

### **Character creation asks the same questions twice**
- This was a bug that has been fixed in the latest version
- Make sure you're using the `consumer_launcher.py` script

## 💡 Tips

- **Be descriptive** when creating your character
- **Respond naturally** to the AI's storytelling
- **Save often** - your progress is automatic
- **Try different character concepts** - each creates a unique story

## 🎯 What Makes This Special

- **No dice rolling** - pure storytelling
- **AI remembers everything** - your choices matter
- **Natural language** - no complex rules to learn
- **Immersive experience** - like having a personal DM

Enjoy your adventure! 🗡️✨
