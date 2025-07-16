# SoloHeart Phase 7: Symbolic Processing + GoalEngine Integration

## 🎯 Implementation Summary

Phase 7 has been successfully implemented, bringing advanced symbolic processing and goal inference to SoloHeart. The system now provides deep narrative intelligence with archetypal analysis, metaphorical detection, and dynamic goal tracking.

## ✅ Step 1: Symbolic Tagging

### Enhanced Symbolic Processing
- **Archetype Detection**: Identifies Hero, Mentor, Shadow, Trickster, Rebirth, Labyrinth, Monster, Threshold, Sacred, Profane patterns
- **Theme Recognition**: Detects narrative themes like Redemption, Betrayal, Sacrifice, Transformation, Power, Justice, Love, Death, Rebirth, Chaos
- **Metaphor Analysis**: Recognizes metaphorical patterns like Light vs Dark, Journey, Battle, Growth, Decay, Water, Fire, Earth
- **Contradiction Detection**: Identifies conflicting elements like Good vs Evil, Life vs Death, Hope vs Despair

### New API Endpoint: `POST /api/symbolic/tags`
- **Input**: narrative text, memory context, character stats
- **Output**: structured symbolic tags with confidence scores, colors, and tooltips
- **Fallback Support**: Comprehensive fallback system when TNE integration unavailable

### Symbolic Features:
- **Color-coded Tags**: Archetypes (yellow), themes (blue), metaphors (green), contradictions (red)
- **Confidence Scoring**: Each tag includes confidence level (0.0-1.0)
- **Tooltip Explanations**: Hover tooltips explain symbolic meaning
- **Real-time Analysis**: Tags update automatically with narrative progression

## ✅ Step 2: GoalEngine Integration

### Advanced Goal Inference
- **Goal Types**: Escape, Discover, Change, Protect, Destroy, Connect, Survive, Achieve
- **Confidence Scoring**: Dynamic confidence calculation based on keyword frequency and context
- **Progress Tracking**: Visual progress bars for goal completion
- **Narrative Justification**: Each goal includes contextual explanation

### New API Endpoint: `POST /api/goal/infer`
- **Input**: session history, memory context, current turn
- **Output**: top 3 inferred goals with confidence scores and justifications
- **Memory Integration**: Goals influenced by memory context and emotional state

### Goal Features:
- **Dynamic Detection**: Goals inferred from conversation patterns
- **Confidence Meters**: Visual progress bars showing goal strength
- **Color-coded Goals**: Each goal type has distinct color for easy identification
- **Contextual Justification**: Brief narrative explanation for each goal

## ✅ Step 3: Backend Prompt Enhancement

### Enhanced Structured Prompts
- **New Sections**: Added `[Symbolism]` and `[Goals]` to prompt structure
- **Auto-refresh**: Both sections update automatically after each player input
- **Context Integration**: Symbolic and goal context included in LLM prompts
- **Memory Awareness**: Prompts now include symbolic and goal context

### Prompt Structure:
```
[System] - Core instructions and character context
[Context] - Campaign and session information
[Memory] - Recent memories and experiences
[Stats] - Character statistics and abilities
[Symbolism] - Active symbolic elements and archetypes
[Goals] - Inferred narrative goals and motivations
[Input] - Player's current action
```

### Integration Features:
- **Seamless Integration**: Symbolic and goal analysis integrated into existing flow
- **Performance Optimized**: Limited to 5 most relevant symbols and 3 top goals
- **Error Handling**: Graceful fallbacks for all analysis components
- **Session Persistence**: All symbolic and goal data saved with campaign

## ✅ Step 4: Dev Toggle + Visuals

### Enhanced Developer Tools
- **Context Block Expansion**: Now shows symbolism and goals sections
- **Auto-hide Timer**: Context blocks fade after 10 seconds
- **Structured Display**: JSON formatting for developer readability
- **Real-time Updates**: All context sections update with narrative progression

### Visual Enhancements:
- **Symbolic Tag Animations**: Smooth fade/slide effects for tag entry
- **Hover Tooltips**: Explanations for archetypes and narrative concepts
- **Color-coded Interface**: Distinct colors for different symbolic types
- **Progress Bars**: Animated goal progress indicators

### Sidebar Integration:
- **Symbolic Tags Section**: Real-time display of detected symbols
- **Goal Engine Section**: Active goals with confidence meters
- **Refresh Buttons**: Manual refresh for both symbolic and goal analysis
- **Responsive Design**: Mobile-friendly interface with proper scaling

## 📁 Files Updated

### Backend Files:
- `simple_unified_interface.py`:
  - New `/api/symbolic/tags` endpoint
  - New `/api/goal/infer` endpoint
  - Enhanced `_build_enhanced_prompt()` with symbolism and goals
  - Added `_get_symbolic_context_for_prompt()` method
  - Added `_get_goals_context_for_prompt()` method
  - Comprehensive fallback systems for both APIs

### Frontend Files:
- `templates/gameplay.html`:
  - Symbolic Tags sidebar section with real-time display
  - Goal Engine sidebar section with progress bars
  - Enhanced JavaScript for symbolic and goal integration
  - Improved CSS for animations and visual feedback
  - Updated context block with symbolism and goals

### Integration Files:
- `narrative_engine_integration.py`:
  - Added `extract_symbolic_tags()` method
  - Added `infer_narrative_goals()` method
  - Added `_detect_archetypes()` method
  - Added `_detect_metaphors()` method
  - Added `_generate_goal_justification()` method

### Test Files:
- `test_symbolic_goal_integration.py`:
  - Comprehensive test suite for symbolic tags API
  - Goal inference testing with various scenarios
  - Enhanced prompt integration testing
  - Health check validation

## 🎨 Visual Enhancements

### Symbolic Tags Display:
- **Color-coded Tags**: Archetypes (yellow), themes (blue), metaphors (green), contradictions (red)
- **Hover Effects**: Tags scale and brighten on hover
- **Tooltip Explanations**: Detailed explanations for each symbolic element
- **Smooth Animations**: Fade-in effects for new tags

### Goal Engine Display:
- **Progress Bars**: Animated progress indicators for each goal
- **Confidence Meters**: Visual representation of goal strength
- **Color-coded Goals**: Each goal type has distinct color
- **Contextual Justification**: Brief narrative explanation for each goal

### Developer Context:
- **Expanded Sections**: Now includes symbolism and goals data
- **JSON Formatting**: Structured display for developer readability
- **Auto-hide Timer**: Context blocks fade after 10 seconds
- **Real-time Updates**: All sections update with narrative progression

## 🔧 Technical Implementation

### Symbolic Processing:
```python
# Symbolic tag extraction
symbolic_tags = tne_engine.extract_symbolic_tags(
    narrative_text=narrative_text,
    memory_context=memory_context,
    character_stats=character_stats
)

# Archetype detection
archetypes = self._detect_archetypes(narrative_text)
themes = self._extract_narrative_themes(narrative_text)
metaphors = self._detect_metaphors(narrative_text)
```

### Goal Inference:
```python
# Goal inference with TNE context
inferred_goals = tne_engine.infer_narrative_goals(
    session_history=session_history,
    memory_context=memory_context,
    current_turn=current_turn
)

# Confidence calculation
confidence = min(0.95, base_confidence + (keyword_count * 0.05) + memory_boost)
```

### Frontend Integration:
```javascript
// Symbolic tags refresh
async function refreshSymbolicTags() {
    const response = await fetch('/api/symbolic/tags', {
        method: 'POST',
        body: JSON.stringify({
            narrative_text: narrativeText,
            memory_context: lastMemoryContext,
            character_stats: {}
        })
    });
}

// Goal engine refresh
async function refreshGoalEngine() {
    const response = await fetch('/api/goal/infer', {
        method: 'POST',
        body: JSON.stringify({
            session_history: sessionHistory,
            memory_context: lastMemoryContext,
            current_turn: {input: ''}
        })
    });
}
```

## 🚀 Ready for Next Phase

The implementation is now ready for:
1. **Stat-based Branching**: Dynamic narrative paths based on character stats
2. **Dynamic World State**: Evolving world influenced by symbolic and goal analysis
3. **Transformation Detection**: Monitor character and world transformations
4. **Resolution Monitoring**: Track goal completion and narrative resolution

## 🧪 Testing

Run the comprehensive test suite:
```bash
cd "SoloHeart Project/solo_heart"
python test_symbolic_goal_integration.py
```

## 📊 Performance Notes

- **Symbolic Analysis**: Limited to 5 most relevant symbols for performance
- **Goal Inference**: Top 3 goals with confidence scoring
- **Auto-refresh**: Both systems update after each player action
- **Fallback Support**: Comprehensive fallbacks when TNE unavailable
- **Memory Integration**: All symbolic and goal data saved with campaign

## 🎯 Success Criteria Met

✅ **Symbolic Tagging**: Comprehensive archetype, theme, metaphor, and contradiction detection
✅ **GoalEngine Integration**: Dynamic goal inference with confidence scoring and progress tracking
✅ **Backend Enhancement**: Enhanced prompt system with symbolism and goals sections
✅ **Visual Feedback**: Animated tags, progress bars, and developer context display
✅ **Dev Tools**: Enhanced context toggle with symbolism and goals sections
✅ **Responsive Design**: Mobile-friendly interface with proper scaling

## 🔮 Advanced Features Implemented

### Symbolic Intelligence:
- **Archetypal Analysis**: Hero, Mentor, Shadow, Trickster, Rebirth patterns
- **Thematic Recognition**: Redemption, Betrayal, Sacrifice, Transformation themes
- **Metaphorical Detection**: Light vs Dark, Journey, Battle, Growth metaphors
- **Contradiction Analysis**: Good vs Evil, Life vs Death, Hope vs Despair conflicts

### Goal Intelligence:
- **Dynamic Inference**: Goals inferred from conversation patterns
- **Confidence Scoring**: Mathematical confidence calculation with context boosting
- **Progress Tracking**: Visual progress bars for goal completion
- **Narrative Justification**: Contextual explanations for each goal

### Integration Intelligence:
- **Seamless Flow**: Symbolic and goal analysis integrated into narrative flow
- **Memory Awareness**: All analysis influenced by memory context
- **Real-time Updates**: Automatic refresh after each player action
- **Developer Tools**: Comprehensive debugging and analysis tools

**Status**: ✅ **COMPLETE** - Ready for Phase 8: Stat-based Branching and Dynamic World State

The system now provides **full narrative intelligence** with symbolic processing, goal inference, and comprehensive visual feedback. SoloHeart has evolved into a sophisticated narrative AI with deep understanding of archetypal patterns, thematic elements, and character motivations. 