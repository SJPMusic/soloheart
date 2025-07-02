#!/usr/bin/env python3
"""
Test Narrative Engine Integration
Simulates the three narrative inputs to test the DnD game integration
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dnd_game.narrative_bridge import create_dnd_bridge, DnDMemoryEntry

def test_narrative_integration():
    """Test the narrative engine integration with three player actions"""
    
    print("🧪 Testing Narrative Engine Integration")
    print("=" * 50)
    
    # Initialize the narrative bridge
    print("1. Initializing Narrative Bridge...")
    try:
        narrative_bridge = create_dnd_bridge(
            campaign_id='Test Campaign',
            api_key=os.getenv('OPENAI_API_KEY')
        )
        print("   ✅ Narrative Bridge initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize Narrative Bridge: {e}")
        return False
    
    # Test 1: Aelric enters the ancient ruins at dusk
    print("\n2. Testing Action 1: Aelric enters the ancient ruins at dusk")
    try:
        response1 = narrative_bridge.generate_dm_narration(
            situation="Aelric, a rogue with exiled noble background, approaches ancient ruins",
            player_actions=["Aelric enters the ancient ruins at dusk"],
            world_context={"location": "ancient_ruins", "time": "dusk"}
        )
        
        # Store memory
        memory1 = DnDMemoryEntry(
            content="Aelric enters the ancient ruins at dusk",
            memory_type="episodic",
            location="ancient_ruins",
            tags=["exploration", "ruins", "dusk"]
        )
        narrative_bridge.store_dnd_memory(memory1)
        
        print(f"   ✅ Response: {str(response1)[:100]}...")
        print("   ✅ Memory stored successfully")
        
    except Exception as e:
        print(f"   ❌ Error in Action 1: {e}")
        return False
    
    # Test 2: He kneels beside a wounded knight and asks what happened
    print("\n3. Testing Action 2: He kneels beside a wounded knight and asks what happened")
    try:
        response2 = narrative_bridge.generate_dm_narration(
            situation="Aelric discovers a wounded knight in the ruins",
            player_actions=["He kneels beside a wounded knight and asks what happened"],
            world_context={"location": "ancient_ruins", "npc": "wounded_knight"}
        )
        
        # Store memory
        memory2 = DnDMemoryEntry(
            content="Aelric kneels beside a wounded knight and asks what happened",
            memory_type="episodic",
            location="ancient_ruins",
            tags=["social", "knight", "wounded", "investigation"]
        )
        narrative_bridge.store_dnd_memory(memory2)
        
        print(f"   ✅ Response: {str(response2)[:100]}...")
        print("   ✅ Memory stored successfully")
        
    except Exception as e:
        print(f"   ❌ Error in Action 2: {e}")
        return False
    
    # Test 3: Suddenly, a goblin attacks—Aelric draws his blade and prepares to fight
    print("\n4. Testing Action 3: Suddenly, a goblin attacks—Aelric draws his blade and prepares to fight")
    try:
        response3 = narrative_bridge.generate_dm_narration(
            situation="Aelric is confronted by a goblin attack in the ruins",
            player_actions=["Suddenly, a goblin attacks—Aelric draws his blade and prepares to fight"],
            world_context={"location": "ancient_ruins", "combat": "goblin_attack"}
        )
        
        # Store memory
        memory3 = DnDMemoryEntry(
            content="Suddenly, a goblin attacks—Aelric draws his blade and prepares to fight",
            memory_type="episodic",
            location="ancient_ruins",
            combat_related=True,
            tags=["combat", "goblin", "attack", "preparation"]
        )
        narrative_bridge.store_dnd_memory(memory3)
        
        print(f"   ✅ Response: {str(response3)[:100]}...")
        print("   ✅ Memory stored successfully")
        
    except Exception as e:
        print(f"   ❌ Error in Action 3: {e}")
        return False
    
    # Test memory recall
    print("\n5. Testing Memory Recall")
    try:
        memories = narrative_bridge.recall_related_memories(
            query="Aelric ruins",
            max_results=5
        )
        
        print(f"   ✅ Retrieved {len(memories)} related memories")
        for i, memory in enumerate(memories[:3], 1):
            print(f"      Memory {i}: {memory.get('content', '')[:50]}...")
            
    except Exception as e:
        print(f"   ❌ Error in memory recall: {e}")
        return False
    
    # Get campaign summary
    print("\n6. Testing Campaign Summary")
    try:
        summary = narrative_bridge.get_campaign_summary()
        print(f"   ✅ Campaign ID: {summary.get('campaign_id', 'Unknown')}")
        print(f"   ✅ Memory Count: {summary.get('memory_stats', {}).get('total_memories', 0)}")
        print(f"   ✅ Session Count: {summary.get('session_count', 0)}")
        
    except Exception as e:
        print(f"   ❌ Error in campaign summary: {e}")
        return False
    
    print("\n🎉 All tests completed successfully!")
    print("=" * 50)
    print("✅ Narrative Engine integration is working")
    print("✅ Memory system is functioning")
    print("✅ DM narration is generating responses")
    print("✅ Memory recall is operational")
    
    return True

if __name__ == "__main__":
    success = test_narrative_integration()
    if not success:
        print("\n❌ Some tests failed. Check the error messages above.")
        sys.exit(1)
    else:
        print("\n✅ All integration tests passed!") 