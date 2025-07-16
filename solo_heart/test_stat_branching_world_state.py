#!/usr/bin/env python3
"""
Test Stat-Based Branching + World State for SoloHeart Phase 8
Tests the new stat triggers and world state management systems.
"""

import requests
import json
import time

def test_stat_triggers():
    """Test stat-based branching triggers."""
    print("🧪 Testing Stat-Based Branching...")
    
    # Test different character stat scenarios
    test_scenarios = [
        {
            "name": "Critical Health",
            "character_stats": {
                "hit_points": 2,
                "ability_scores": {"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
                "level": 1
            },
            "expected_triggers": ["critical_health"]
        },
        {
            "name": "High Intelligence",
            "character_stats": {
                "hit_points": 10,
                "ability_scores": {"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 18, "wisdom": 10, "charisma": 10},
                "level": 1
            },
            "expected_triggers": ["exceptional_intelligence"]
        },
        {
            "name": "Experienced Warrior",
            "character_stats": {
                "hit_points": 15,
                "ability_scores": {"strength": 16, "dexterity": 14, "constitution": 16, "intelligence": 10, "wisdom": 12, "charisma": 10},
                "level": 5
            },
            "expected_triggers": ["high_strength", "high_constitution", "experienced_warrior"]
        },
        {
            "name": "Multiple High Stats",
            "character_stats": {
                "hit_points": 20,
                "ability_scores": {"strength": 18, "dexterity": 18, "constitution": 16, "intelligence": 16, "wisdom": 14, "charisma": 18},
                "level": 3
            },
            "expected_triggers": ["exceptional_strength", "exceptional_dexterity", "high_constitution", "high_intelligence", "exceptional_charisma", "seasoned_adventurer"]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📊 Testing: {scenario['name']}")
        
        try:
            # Test a game action with the character stats
            action_data = {
                "input": "I want to explore the area"
            }
            
            response = requests.post('http://localhost:5001/api/game/action', 
                               json=action_data,
                               headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Game Action Response:")
                print(f"   Success: {data.get('success')}")
                if data.get('dm_response'):
                    print(f"   Response Length: {len(data['dm_response'])} characters")
                    print(f"   Response Preview: {data['dm_response'][:150]}...")
                    
                    # Check for stat-based narrative elements
                    response_lower = data['dm_response'].lower()
                    stat_indicators = ['vision blur', 'wounds', 'injured', 'arcane', 'symbols', 'charm', 'intimidate', 'reflexes', 'grace', 'intuition', 'endurance', 'experience']
                    found_indicators = [indicator for indicator in stat_indicators if indicator in response_lower]
                    print(f"   Stat-based indicators found: {found_indicators}")
                else:
                    print("   No DM response received")
            else:
                print(f"❌ Game action failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure SoloHeart is running on port 5001")
        except Exception as e:
            print(f"❌ Error testing stat triggers: {e}")

def test_world_state_api():
    """Test world state API endpoints."""
    print("\n🧪 Testing World State API...")
    
    # Test getting world state
    print("📖 Testing GET /api/world/state...")
    try:
        response = requests.get('http://localhost:5001/api/world/state')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ World State Response:")
            print(f"   Success: {data.get('success')}")
            if data.get('world_state'):
                world_state = data['world_state']
                print(f"   Current Location: {world_state.get('current_location', 'Unknown')}")
                print(f"   Items: {world_state.get('items', [])}")
                print(f"   NPCs: {world_state.get('npc_flags', {})}")
                print(f"   Story Flags: {world_state.get('story_flags', {})}")
            else:
                print("   No world state available")
        else:
            print(f"❌ World state API failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure SoloHeart is running on port 5001")
    except Exception as e:
        print(f"❌ Error testing world state API: {e}")

def test_world_state_updates():
    """Test world state update functionality."""
    print("\n🧪 Testing World State Updates...")
    
    # Test different world state updates
    test_updates = [
        {
            "name": "Location Update",
            "updates": {
                "current_location": "Ancient Crypt of the Forgotten Stars"
            }
        },
        {
            "name": "Item Acquisition",
            "updates": {
                "add_item": "Mystical Key of the Ancients"
            }
        },
        {
            "name": "NPC Meeting",
            "updates": {
                "npc_flag": {"npc": "Elandra the Wise", "status": "Friendly"}
            }
        },
        {
            "name": "Story Flag",
            "updates": {
                "story_flag": {"flag": "gate_opened", "value": True}
            }
        },
        {
            "name": "Complex Update",
            "updates": {
                "current_location": "Inner Sanctum",
                "add_item": "Sacred Amulet",
                "npc_flag": {"npc": "Guardian Spirit", "status": "Hostile"},
                "story_flag": {"flag": "ritual_completed", "value": True}
            }
        }
    ]
    
    for test_update in test_updates:
        print(f"\n🌍 Testing: {test_update['name']}")
        
        try:
            response = requests.post('http://localhost:5001/api/world/update', 
                                   json={'updates': test_update['updates']},
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ World State Update Response:")
                print(f"   Success: {data.get('success')}")
                print(f"   Message: {data.get('message')}")
                
                if data.get('world_state'):
                    world_state = data['world_state']
                    print(f"   Updated Location: {world_state.get('current_location', 'Unknown')}")
                    print(f"   Updated Items: {world_state.get('items', [])}")
                    print(f"   Updated NPCs: {world_state.get('npc_flags', {})}")
                    print(f"   Updated Story Flags: {world_state.get('story_flags', {})}")
                else:
                    print("   No world state in response")
            else:
                print(f"❌ World state update failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure SoloHeart is running on port 5001")
        except Exception as e:
            print(f"❌ Error testing world state updates: {e}")

def test_enhanced_prompt_integration():
    """Test the enhanced prompt system with stat triggers and world state."""
    print("\n🧪 Testing Enhanced Prompt Integration...")
    
    try:
        # Test a game action that should trigger stat-based and world state responses
        action_data = {
            "input": "I want to use my intelligence to examine the ancient runes on the wall"
        }
        
        response = requests.post('http://localhost:5001/api/game/action', 
                               json=action_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced Game Action Response:")
            print(f"   Success: {data.get('success')}")
            if data.get('dm_response'):
                print(f"   Response Length: {len(data['dm_response'])} characters")
                print(f"   Response Preview: {data['dm_response'][:200]}...")
                
                # Check for enhanced narrative elements
                response_lower = data['dm_response'].lower()
                enhanced_indicators = ['intelligence', 'runes', 'ancient', 'symbols', 'arcane', 'recognize', 'notice', 'details']
                found_indicators = [indicator for indicator in enhanced_indicators if indicator in response_lower]
                print(f"   Enhanced indicators found: {found_indicators}")
                
                # Check for stat-based narrative
                stat_indicators = ['vision blur', 'wounds', 'injured', 'arcane', 'symbols', 'charm', 'intimidate', 'reflexes', 'grace', 'intuition', 'endurance', 'experience']
                found_stat_indicators = [indicator for indicator in stat_indicators if indicator in response_lower]
                print(f"   Stat-based narrative found: {found_stat_indicators}")
            else:
                print("   No DM response received")
        else:
            print(f"❌ Enhanced game action failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure SoloHeart is running on port 5001")
    except Exception as e:
        print(f"❌ Error testing enhanced prompt integration: {e}")

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
    print("🚀 SoloHeart Phase 8 - Stat-Based Branching + World State Test")
    print("=" * 70)
    
    # Test health first
    test_health_check()
    
    # Test stat triggers
    test_stat_triggers()
    
    # Test world state API
    test_world_state_api()
    
    # Test world state updates
    test_world_state_updates()
    
    # Test enhanced prompt integration
    test_enhanced_prompt_integration()
    
    print("\n✅ Stat-Based Branching + World State Test Complete!")
    print("\n💡 To test the full interface:")
    print("   1. Start SoloHeart server")
    print("   2. Navigate to http://localhost:5001/game")
    print("   3. Check the sidebar for World State panel")
    print("   4. Use the developer context toggle to see stat triggers")
    print("   5. Try different actions to see stat-based narrative branching")
    print("   6. Watch world state update as you explore and interact")

if __name__ == "__main__":
    main() 