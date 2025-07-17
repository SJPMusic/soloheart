#!/usr/bin/env python3
"""
TNE Memory Injection Test Harness

Standalone CLI test for validating SoloHeart → TNE integration.
Tests the full path from game actions to memory events.

CRITICAL TEST TOOL: Use this for all future TNE↔SoloHeart development.
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Import our integration modules
try:
    from integrations.tne_event_mapper import map_action_to_event
    from integrations.tne_bridge import send_event_to_tne
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the SoloHeart directory")
    sys.exit(1)


async def test_combat_action():
    """Test combat action mapping and injection."""
    print("\n" + "="*60)
    print("🗡️  TESTING COMBAT ACTION")
    print("="*60)
    
    # Simulate combat action
    combat_action = {
        "action_type": "combat",
        "character_name": "Thalion",
        "target": "ogre",
        "weapon": "sword",
        "damage": 12,
        "hit": True,
        "critical": False,
        "location": "Dark Forest",
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"🎯 COMBAT ACTION: {combat_action['character_name']} attacks {combat_action['target']}")
    
    # MAPPING: Convert to TNE event
    print("\n📝 MAPPING: Converting to TNE memory event...")
    try:
        tne_event = map_action_to_event(
            character_id=combat_action['character_name'],
            action_type=combat_action['action_type'],
            description=f"{combat_action['character_name']} attacks {combat_action['target']} with {combat_action['weapon']} for {combat_action['damage']} damage",
            memory_layer="episodic",
            tags=["combat", "violence", "aggression"],
            importance=0.8,
            metadata={
                "weapon": combat_action['weapon'],
                "target": combat_action['target'],
                "damage": combat_action['damage'],
                "hit": combat_action['hit'],
                "critical": combat_action['critical'],
                "location": combat_action['location']
            }
        )
        print("✅ Mapping successful")
        print(f"📋 Generated event type: {tne_event.get('metadata', {}).get('action_type', 'unknown')}")
        print(f"📋 Event description length: {len(tne_event.get('description', ''))} chars")
    except Exception as e:
        print(f"❌ Mapping failed: {e}")
        return False
    
    # SENDING: Send to TNE
    print("\n🚀 SENDING: Transmitting to TNE...")
    try:
        response = await send_event_to_tne(tne_event)
        print("✅ Transmission successful")
        return response
    except Exception as e:
        print(f"❌ Transmission failed: {e}")
        return False


async def test_dialogue_action():
    """Test dialogue action mapping and injection."""
    print("\n" + "="*60)
    print("💬 TESTING DIALOGUE ACTION")
    print("="*60)
    
    # Simulate dialogue action
    dialogue_action = {
        "action_type": "dialogue",
        "character_name": "Thalion",
        "npc_name": "Village Elder",
        "dialogue_type": "negotiation",
        "topic": "quest information",
        "success": True,
        "location": "Village Square",
        "timestamp": datetime.now().isoformat(),
        "dialogue_summary": "Successfully negotiated for information about the ancient ruins"
    }
    
    print(f"💬 DIALOGUE ACTION: {dialogue_action['character_name']} negotiates with {dialogue_action['npc_name']}")
    
    # MAPPING: Convert to TNE event
    print("\n📝 MAPPING: Converting to TNE memory event...")
    try:
        tne_event = map_action_to_event(
            character_id=dialogue_action['character_name'],
            action_type=dialogue_action['action_type'],
            description=f"{dialogue_action['character_name']} negotiates with {dialogue_action['npc_name']} about {dialogue_action['topic']}",
            memory_layer="episodic",
            tags=["dialogue", "negotiation", "social"],
            importance=0.6,
            metadata={
                "npc_name": dialogue_action['npc_name'],
                "dialogue_type": dialogue_action['dialogue_type'],
                "topic": dialogue_action['topic'],
                "success": dialogue_action['success'],
                "location": dialogue_action['location'],
                "dialogue_summary": dialogue_action['dialogue_summary']
            }
        )
        print("✅ Mapping successful")
        print(f"📋 Generated event type: {tne_event.get('metadata', {}).get('action_type', 'unknown')}")
        print(f"📋 Event description length: {len(tne_event.get('description', ''))} chars")
    except Exception as e:
        print(f"❌ Mapping failed: {e}")
        return False
    
    # SENDING: Send to TNE
    print("\n🚀 SENDING: Transmitting to TNE...")
    try:
        response = await send_event_to_tne(tne_event)
        print("✅ Transmission successful")
        return response
    except Exception as e:
        print(f"❌ Transmission failed: {e}")
        return False


async def test_invalid_action():
    """Test handling of invalid action types."""
    print("\n" + "="*60)
    print("⚠️  TESTING INVALID ACTION")
    print("="*60)
    
    # Simulate invalid action
    invalid_action = {
        "action_type": "invalid_type",
        "character_name": "Thalion",
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"⚠️  INVALID ACTION: Unknown action type '{invalid_action['action_type']}'")
    
    # MAPPING: Should handle gracefully
    print("\n📝 MAPPING: Attempting to convert invalid action...")
    try:
        tne_event = map_action_to_event(
            character_id=invalid_action['character_name'],
            action_type=invalid_action['action_type'],
            description=f"Unknown action type: {invalid_action['action_type']}",
            memory_layer="episodic",
            tags=["unknown", "error"],
            importance=0.1,
            metadata={"error": "Unknown action type"}
        )
        print("✅ Mapping handled gracefully")
        print(f"📋 Generated event type: {tne_event.get('metadata', {}).get('action_type', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ Mapping failed (expected): {e}")
        return False


def print_response_summary(test_name: str, response: Any):
    """Print formatted response summary."""
    print(f"\n📊 RESPONSE SUMMARY: {test_name}")
    print("-" * 40)
    
    if response is False:
        print("❌ Test failed - no response received")
        return
    
    if isinstance(response, dict):
        print("✅ Response received successfully")
        print(f"📋 Response keys: {list(response.keys())}")
        
        # Pretty print the response
        print("\n📄 Full Response JSON:")
        print(json.dumps(response, indent=2, default=str))
    else:
        print(f"⚠️  Unexpected response type: {type(response)}")
        print(f"📄 Response: {response}")


async def run_all_tests():
    """Run all test scenarios."""
    print("🧪 TNE MEMORY INJECTION TEST HARNESS")
    print("=" * 60)
    print(f"🕐 Test started at: {datetime.now().isoformat()}")
    print("🎯 Testing SoloHeart → TNE integration pipeline")
    
    results = {}
    
    # Test 1: Combat Action
    combat_response = await test_combat_action()
    print_response_summary("Combat Action", combat_response)
    results['combat'] = combat_response is not False
    
    # Test 2: Dialogue Action
    dialogue_response = await test_dialogue_action()
    print_response_summary("Dialogue Action", dialogue_response)
    results['dialogue'] = dialogue_response is not False
    
    # Test 3: Invalid Action
    invalid_response = await test_invalid_action()
    print_response_summary("Invalid Action", invalid_response)
    results['invalid'] = invalid_response is not False
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name.title()} Action")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! TNE integration is working.")
        return True
    else:
        print("⚠️  Some tests failed. Check the integration.")
        return False


if __name__ == "__main__":
    """Main entry point for standalone CLI execution."""
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 