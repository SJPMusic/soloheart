"""
Demo: Enhanced Memory System Integration
=======================================

Demonstrates the enhanced memory system with:
- Layered memory (short/mid/long-term)
- Memory-aware AI DM responses
- Personalization and emotional context
- Memory recall and visualization
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.enhanced_memory_system import LayeredMemorySystem, MemoryType, MemoryLayer, EmotionalContext
from core.enhanced_ai_dm_engine import EnhancedAIDMEngine

def demo_memory_system():
    """Demo the enhanced memory system"""
    print("🧠 Enhanced Memory System Demo")
    print("=" * 50)
    
    # Initialize memory system
    memory_system = LayeredMemorySystem("demo_campaign")
    
    # Add some sample memories
    print("\n📝 Adding sample memories...")
    
    # Short-term memory (recent actions)
    memory_system.add_memory(
        content={'action': 'I cast a fireball at the goblins', 'context': 'Combat encounter'},
        memory_type=MemoryType.EVENT,
        layer=MemoryLayer.SHORT_TERM,
        user_id='player',
        session_id='session_1',
        emotional_weight=0.8,
        emotional_context=[EmotionalContext.ANGER, EmotionalContext.ANTICIPATION],
        thematic_tags=['combat', 'magic']
    )
    
    # Mid-term memory (session-level)
    memory_system.add_memory(
        content={'action': 'I decided to spare the goblin leader', 'context': 'Moral choice'},
        memory_type=MemoryType.DECISION,
        layer=MemoryLayer.MID_TERM,
        user_id='player',
        session_id='session_1',
        emotional_weight=0.9,
        emotional_context=[EmotionalContext.TRUST, EmotionalContext.JOY],
        thematic_tags=['moral_choice', 'mercy']
    )
    
    # Long-term memory (campaign-level)
    memory_system.add_memory(
        content={'action': 'I discovered the ancient temple', 'context': 'World exploration'},
        memory_type=MemoryType.WORLD_STATE,
        layer=MemoryLayer.LONG_TERM,
        user_id='player',
        session_id='session_1',
        emotional_weight=0.7,
        emotional_context=[EmotionalContext.SURPRISE, EmotionalContext.ANTICIPATION],
        thematic_tags=['exploration', 'mystery']
    )
    
    print("✅ Sample memories added!")
    
    # Show memory stats
    print("\n📊 Memory Statistics:")
    stats = memory_system.stats_summary()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Demo memory recall
    print("\n🔍 Memory Recall Demo:")
    
    # Recall by query
    print("\nSearching for 'goblin' related memories:")
    goblin_memories = memory_system.recall(query='goblin', user_id='player')
    for i, memory in enumerate(goblin_memories, 1):
        print(f"  {i}. {memory.content.get('action', 'Unknown action')} (Significance: {memory.get_significance():.2f})")
    
    # Recall by emotional context
    print("\nSearching for memories with 'joy' emotion:")
    joy_memories = memory_system.recall(emotional=EmotionalContext.JOY, user_id='player')
    for i, memory in enumerate(joy_memories, 1):
        print(f"  {i}. {memory.content.get('action', 'Unknown action')} (Significance: {memory.get_significance():.2f})")
    
    # Recall by thematic tags
    print("\nSearching for 'combat' themed memories:")
    combat_memories = memory_system.recall(thematic=['combat'], user_id='player')
    for i, memory in enumerate(combat_memories, 1):
        print(f"  {i}. {memory.content.get('action', 'Unknown action')} (Significance: {memory.get_significance():.2f})")
    
    # Show user profile
    print("\n👤 User Profile:")
    profile = memory_system.get_user_profile('player')
    if 'emotions' in profile:
        print("  Emotional tendencies:")
        for emotion, count in profile['emotions'].items():
            print(f"    {emotion}: {count}")
    
    if 'themes' in profile:
        print("  Thematic interests:")
        for theme, count in profile['themes'].items():
            print(f"    {theme}: {count}")
    
    return memory_system

def demo_ai_dm_integration():
    """Demo the enhanced AI DM with memory integration"""
    print("\n🤖 Enhanced AI DM Integration Demo")
    print("=" * 50)
    
    # Initialize enhanced AI DM
    api_key = os.getenv('OPENAI_API_KEY')
    ai_dm = EnhancedAIDMEngine(api_key, "demo_campaign")
    
    # Sample character info
    character_info = {
        'name': 'Gandalf',
        'race': 'half-elf',
        'class': 'wizard',
        'level': 5,
        'ability_scores': {'STR': 10, 'DEX': 14, 'CON': 12, 'INT': 18, 'WIS': 16, 'CHA': 14},
        'skills': {'Arcana': 7, 'Investigation': 6, 'Perception': 5},
        'equipment': ['Staff of the Magi', 'Spellbook', 'Wizard robes']
    }
    
    # Demo memory-aware responses
    print("\n💬 Memory-Aware AI Responses:")
    
    actions = [
        "I want to explore the ancient temple we discovered earlier",
        "I cast fireball at the enemies",
        "I remember the goblin leader I spared - I want to check on him"
    ]
    
    for i, action in enumerate(actions, 1):
        print(f"\n{i}. Player Action: '{action}'")
        print("   AI Response:")
        
        try:
            response = ai_dm.process_action(
                player_action=action,
                character_info=character_info,
                session_id='demo_session',
                user_id='player'
            )
            print(f"   {response}")
        except Exception as e:
            print(f"   [Fallback response due to API error: {e}]")
            print("   I remember your journey and the choices you've made. Based on our shared history, I'll guide you through this moment with the wisdom of our past adventures together.")
    
    # Show memory stats after AI interaction
    print("\n📊 Memory Stats After AI Interaction:")
    stats = ai_dm.get_memory_stats()
    for key, value in stats.items():
        if key in ['short_term', 'mid_term', 'long_term', 'created', 'reinforced']:
            print(f"  {key}: {value}")
    
    return ai_dm

def demo_memory_persistence():
    """Demo memory state persistence"""
    print("\n💾 Memory Persistence Demo")
    print("=" * 50)
    
    # Create a memory system with some data
    memory_system = LayeredMemorySystem("persistence_demo")
    
    # Add some memories
    memory_system.add_memory(
        content={'action': 'I saved the village from bandits'},
        memory_type=MemoryType.EVENT,
        layer=MemoryLayer.MID_TERM,
        user_id='player',
        session_id='session_1',
        emotional_weight=0.8,
        thematic_tags=['heroism', 'combat']
    )
    
    # Save memory state
    print("Saving memory state...")
    saved_state = memory_system.to_dict()
    
    # Create new memory system and load state
    print("Loading memory state...")
    new_memory_system = LayeredMemorySystem.from_dict(saved_state)
    
    # Verify data was preserved
    print("Verifying data preservation...")
    original_stats = memory_system.stats_summary()
    loaded_stats = new_memory_system.stats_summary()
    
    print(f"Original memories: {original_stats['mid_term']}")
    print(f"Loaded memories: {loaded_stats['mid_term']}")
    
    if original_stats['mid_term'] == loaded_stats['mid_term']:
        print("✅ Memory persistence working correctly!")
    else:
        print("❌ Memory persistence failed!")

def main():
    """Run the complete demo"""
    print("🚀 Enhanced Memory System Integration Demo")
    print("=" * 60)
    print("This demo showcases the enhanced memory system with:")
    print("- Layered memory (short/mid/long-term)")
    print("- Memory-aware AI DM responses")
    print("- Personalization and emotional context")
    print("- Memory recall and visualization")
    print("- Memory persistence")
    print("=" * 60)
    
    try:
        # Demo 1: Basic memory system
        memory_system = demo_memory_system()
        
        # Demo 2: AI DM integration
        ai_dm = demo_ai_dm_integration()
        
        # Demo 3: Memory persistence
        demo_memory_persistence()
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Run the enhanced web interface: python enhanced_web_interface.py")
        print("2. Test memory features in the web UI")
        print("3. Check memory stats and recall functionality")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 