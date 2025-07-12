# 🎲 How to Use The Narrative Engine D&D Demo

## Quick Start (2 minutes)

### 1. **Configure LLM Provider**
- Set up Gemma API access (or use Ollama fallback)
- Configure your `.env` file with `LLM_PROVIDER=gemma`
- Ensure TNB server is running on localhost:3000
- Ensure TNE server is running on localhost:5000

### 2. **Run the Demo**
```bash
python simple_unified_interface.py
```

### 3. **Explore TNE Capabilities!**
- The demo will open in your browser
- Click "Start New Campaign"
- Describe your character concept in natural language
- Watch symbolic processing and memory flow visualization
- Experience TNE's archetype detection and goal inference

## 🎮 What You'll Experience

### **Symbolic Processing Visualization**
- Watch TNE's archetype detection in real-time
- See pattern recognition for transformation, conflict, and resolution cycles
- Observe symbolic reasoning and insight generation
- Experience goal inference and completion tracking

### **Memory Flow Display**
- View episodic memory retrieval and relevance scoring
- See semantic memory integration and concept recall
- Observe emotional memory context and relationship dynamics
- Watch memory impact on narrative generation

### **Bridge Routing Demonstration**
- Experience clean handoff of user input through TNB
- See memory injection and context preservation
- Observe output processing and symbolic integrity
- Watch LLM response enrichment with memory context

## 🔧 Troubleshooting

### **"LLM provider not found"**
- Make sure your `.env` file has `LLM_PROVIDER=gemma` or `LLM_PROVIDER=ollama`
- For Gemma: Ensure Gemma is running at http://localhost:1234/v1
- For Ollama: Start with `brew services start ollama`

### **"TNB/TNE connection failed"**
- Ensure TNB server is running on localhost:3000
- Ensure TNE server is running on localhost:5000
- Check network connectivity and firewall settings

### **"Port already in use"**
- Close other applications that might be using port 5001
- Or restart your computer

### **"Module not found"**
- Run: `pip install Flask Flask-CORS requests python-dotenv jsonschema`

## 💡 Tips

- **Be descriptive** when creating your character concept
- **Watch the symbolic processing** - observe archetype detection
- **Monitor memory flows** - see how context enhances responses
- **Try different character concepts** - each demonstrates unique symbolic patterns

## 🎯 What Makes This Special

- **Symbolic Processing Visualization** - see TNE's archetype detection in action
- **Memory Flow Display** - observe episodic, semantic, and emotional memory
- **Bridge Routing Compliance** - experience clean TNB/TNE integration
- **LLM-Native Integration** - leverage Gemma's autonomous narrative generation
- **Clean Modular Boundaries** - maintain symbolic integrity and domain agnosticism

Explore TNE's capabilities! 🧠✨ 