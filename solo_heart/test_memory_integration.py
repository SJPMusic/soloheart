#!/usr/bin/env python3
"""
Test Memory Integration for SoloHeart Phase 6
Tests the new memory context API and prompt system.
"""

import requests
import json
import time

def test_memory_context_api():
    """Test the memory context API endpoint."""
    print("🧪 Testing Memory Context API...")
    
    try:
        # Test the memory context endpoint
        response = requests.get('http://localhost:5001/api/memory/context')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Memory Context API Response:")
            print(f"   Success: {data.get('success')}")
            if data.get('memory_context'):
                memory = data['memory_context']
                print(f"   Total Memories: {memory.get('memory_stats', {}).get('total_memories', 0)}")
                print(f"   Recent Memories: {memory.get('memory_stats', {}).get('recent_memories', 0)}")
                print(f"   Emotional Tags: {len(memory.get('emotional_tags', []))}")
                print(f"   Thematic Tags: {len(memory.get('thematic_tags', []))}")
            else:
                print("   No memory context available")
        else:
            print(f"❌ Memory Context API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure SoloHeart is running on port 5001")
    except Exception as e:
        print(f"❌ Error testing memory context API: {e}")

def test_game_action_with_memory():
    """Test game action with memory integration."""
    print("\n🧪 Testing Game Action with Memory Integration...")
    
    try:
        # Test a simple game action
        action_data = {
            "input": "I want to explore the area around me"
        }
        
        response = requests.post('http://localhost:5001/api/game/action', 
                               json=action_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Game Action Response:")
            print(f"   Success: {data.get('success')}")
            if data.get('dm_response'):
                print(f"   Response Length: {len(data['dm_response'])} characters")
                print(f"   Response Preview: {data['dm_response'][:100]}...")
            else:
                print("   No DM response received")
        else:
            print(f"❌ Game Action failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure SoloHeart is running on port 5001")
    except Exception as e:
        print(f"❌ Error testing game action: {e}")

def test_health_check():
    """Test the health check endpoint."""
    print("\n🧪 Testing Health Check...")
    
    try:
        response = requests.get('http://localhost:5001/api/health')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check Response:")
            print(f"   Status: {data.get('status')}")
            print(f"   LLM Provider: {data.get('llm_provider')}")
            print(f"   LLM Healthy: {data.get('llm_healthy')}")
            print(f"   Demo Healthy: {data.get('demo_healthy')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure SoloHeart is running on port 5001")
    except Exception as e:
        print(f"❌ Error testing health check: {e}")

def main():
    """Run all tests."""
    print("🚀 SoloHeart Phase 6 - Memory Integration Test")
    print("=" * 50)
    
    # Test health first
    test_health_check()
    
    # Test memory context API
    test_memory_context_api()
    
    # Test game action with memory
    test_game_action_with_memory()
    
    print("\n✅ Memory Integration Test Complete!")
    print("\n💡 To test the full interface:")
    print("   1. Start SoloHeart server")
    print("   2. Navigate to http://localhost:5001/game")
    print("   3. Check the sidebar for memory viewer")
    print("   4. Use the developer context toggle")

if __name__ == "__main__":
    main() 