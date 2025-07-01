#!/usr/bin/env python3
"""
Test OpenAI Integration for DnD 5E AI-Powered Game
=================================================

This script tests the OpenAI integration with the memory system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from narrative_engine.memory.layered_memory import LayeredMemorySystem
from narrative_engine.core.ai_content_generator import AIContentGenerator

def test_openai_integration():
    """Test the OpenAI integration"""
    print("🧪 Testing OpenAI Integration")
    print("=" * 40)
    
    # Initialize memory system
    memory_system = LayeredMemorySystem("test_campaign")
    
    # Initialize AI generator
    ai_generator = AIContentGenerator(memory_system)
    
    # Check if OpenAI is available
    if not ai_generator.openai_client:
        print("❌ OpenAI client not available")
        print("Run 'python3 setup_openai.py' to set up your API key")
        return False
    
    print("✅ OpenAI client initialized")
    
    # Add some test memory
    memory_system.add_campaign_memory(
        memory_type='character',
        content={
            'name': 'Gandalf',
            'race': 'half-elf',
            'class': 'wizard',
            'level': 3,
            'background': 'sage'
        },
        session_id='test_session'
    )
    
    memory_system.add_campaign_memory(
        memory_type='location',
        content={
            'name': 'Mystic Forest',
            'description': 'A dark, ancient forest with glowing mushrooms',
            'atmosphere': 'mysterious and foreboding'
        },
        session_id='test_session'
    )
    
    print("✅ Test memory added")
    
    # Test conversational response
    context = {
        'player_message': 'I cast a light spell to illuminate the dark path',
        'character': {
            'name': 'Gandalf',
            'race': 'half-elf',
            'character_class': 'wizard',
            'level': 3
        },
        'campaign_memory': {
            'current_location': 'Mystic Forest'
        }
    }
    
    print("\n🎭 Testing AI response...")
    print(f"Player: {context['player_message']}")
    
    try:
        response = ai_generator.generate_conversational_response(context)
        
        print("\n🤖 AI Response:")
        print("-" * 40)
        print(response.content)
        print("-" * 40)
        
        print(f"\n📊 Response Details:")
        print(f"- Type: {response.content_type}")
        print(f"- Entities: {response.entities_involved}")
        print(f"- Confidence: {response.confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_integration()
    if success:
        print("\n🎉 OpenAI integration test successful!")
        print("You can now run the full game with ChatGPT-quality responses!")
    else:
        print("\n❌ Test failed. Please check your setup.") 