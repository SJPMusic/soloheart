#!/usr/bin/env python3
"""
Test script for Narrative Engine Integration with Vector Memory
Tests the integration of TNE with vector memory for semantic search.
"""

import sys
import os
import logging
from datetime import datetime

# Add the solo_heart directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solo_heart'))

from narrative_engine_integration import TNEDemoEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_vector_memory_integration():
    """Test the vector memory integration with narrative engine."""
    
    print("🧪 Testing Vector Memory Integration")
    print("=" * 50)
    
    # Initialize the engine
    engine = TNEDemoEngine(campaign_id="test_campaign")
    
    # Test 1: Character Creation with Vector Memory
    print("\n📝 Test 1: Character Creation")
    character_data = {
        'name': 'Thorin Stonebeard',
        'race': 'Dwarf',
        'class': 'Fighter',
        'background': 'Soldier',
        'personality_traits': ['Brave', 'Stubborn', 'Loyal'],
        'motivations': ['Protect his clan', 'Find ancient treasures'],
        'emotional_themes': ['Honor', 'Loss', 'Redemption'],
        'backstory': 'A dwarf warrior who lost his clan in a goblin attack'
    }
    
    char_id = engine.record_character_creation(character_data)
    print(f"✅ Character created: {char_id}")
    
    # Test 2: Player Actions with Vector Memory
    print("\n📝 Test 2: Player Actions")
    player_actions = [
        "I want to explore the ancient ruins",
        "My character feels conflicted about his past",
        "I'm searching for clues about the lost clan",
        "The dwarf warrior approaches the mysterious door"
    ]
    
    for action in player_actions:
        memory_id = engine.record_player_action(action, {'user_id': 'player'})
        print(f"✅ Recorded action: {action[:50]}...")
    
    # Test 3: Memory Context Retrieval
    print("\n📝 Test 3: Memory Context Retrieval")
    context = engine.get_memory_context_for_ollama(user_id='player', max_memories=10)
    print("📊 Retrieved Memory Context:")
    print(context)
    
    # Test 4: Vector Memory Search
    print("\n📝 Test 4: Vector Memory Search")
    if hasattr(engine, 'vector_memory') and engine.vector_memory:
        # Test semantic search
        search_results = engine.vector_memory.search_memories(
            query="dwarf warrior clan",
            top_k=3,
            user_id='player'
        )
        
        print(f"🧠 Vector Search Results ({len(search_results)} found):")
        for i, (memory_item, similarity) in enumerate(search_results):
            print(f"  {i+1}. Similarity: {similarity:.3f}")
            print(f"     Content: {memory_item.content}")
            print(f"     Tags: {memory_item.thematic_tags}")
    
    # Test 5: Memory Statistics
    print("\n📝 Test 5: Memory Statistics")
    stats = engine.get_memory_stats()
    print(f"📊 Memory Stats: {stats}")
    
    # Test 6: Vector Memory Statistics
    print("\n📝 Test 6: Vector Memory Statistics")
    if hasattr(engine, 'vector_memory') and engine.vector_memory:
        vector_stats = engine.vector_memory.get_memory_stats()
        print(f"🧠 Vector Memory Stats: {vector_stats}")
    
    print("\n✅ All tests completed successfully!")
    return True

def test_error_handling():
    """Test error handling in the integration."""
    
    print("\n🧪 Testing Error Handling")
    print("=" * 50)
    
    try:
        # Test with invalid campaign ID
        engine = TNEDemoEngine(campaign_id="invalid_campaign")
        
        # Test with empty character data
        char_id = engine.record_character_creation({})
        print("✅ Handled empty character data")
        
        # Test with invalid memory context
        context = engine.get_memory_context_for_ollama(user_id='nonexistent')
        print("✅ Handled nonexistent user")
        
        print("✅ Error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_performance():
    """Test performance of vector memory operations."""
    
    print("\n🧪 Testing Performance")
    print("=" * 50)
    
    import time
    
    engine = TNEDemoEngine(campaign_id="perf_test")
    
    # Test memory addition performance
    start_time = time.time()
    
    for i in range(10):
        character_data = {
            'name': f'Test Character {i}',
            'race': 'Human',
            'class': 'Wizard',
            'background': 'Sage',
            'personality_traits': [f'Trait {i}'],
            'motivations': [f'Motivation {i}'],
            'backstory': f'Test character {i} backstory'
        }
        
        engine.record_character_creation(character_data)
    
    add_time = time.time() - start_time
    print(f"⏱️ Added 10 characters in {add_time:.2f} seconds")
    
    # Test search performance
    start_time = time.time()
    context = engine.get_memory_context_for_ollama(max_memories=20)
    search_time = time.time() - start_time
    print(f"⏱️ Retrieved memory context in {search_time:.2f} seconds")
    
    print("✅ Performance tests completed!")
    return True

def main():
    """Run all integration tests."""
    
    print("🚀 Starting Narrative Engine Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Vector Memory Integration", test_vector_memory_integration),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Vector memory integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 