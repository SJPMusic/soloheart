#!/usr/bin/env python3
"""
Test Symbolic Processing + GoalEngine Integration for SoloHeart Phase 7
Tests the new symbolic tagging and goal inference systems.
"""

import requests
import json
import time

def test_symbolic_tags_api():
    """Test the symbolic tags API endpoint."""
    print("🧪 Testing Symbolic Tags API...")
    
    # Test narrative text with various symbolic elements
    test_narratives = [
        {
            "name": "Hero's Journey",
            "text": "The brave warrior embarks on a dangerous quest to find the ancient sword of light. Along the way, they meet a wise mentor who guides them through the dark labyrinth of the underworld.",
            "expected_symbols": ["Hero", "Mentor", "Labyrinth", "Journey", "Light vs Dark"]
        },
        {
            "name": "Transformation Story",
            "text": "The young apprentice undergoes a profound transformation, shedding their old identity like a snake shedding its skin. They emerge reborn with new powers and understanding.",
            "expected_symbols": ["Transformation", "Rebirth", "Change", "Growth"]
        },
        {
            "name": "Battle for Survival",
            "text": "The desperate survivors fight against the monstrous creatures that threaten to destroy their sacred homeland. They must protect the innocent and eliminate the evil forces.",
            "expected_symbols": ["Monster", "Protect", "Destroy", "Sacred", "Battle"]
        }
    ]
    
    for test_case in test_narratives:
        print(f"\n📖 Testing: {test_case['name']}")
        
        try:
            response = requests.post('http://localhost:5001/api/symbolic/tags', 
                                   json={
                                       'narrative_text': test_case['text'],
                                       'memory_context': {},
                                       'character_stats': {}
                                   },
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received:")
                print(f"   Success: {data.get('success')}")
                
                if data.get('symbolic_tags'):
                    symbols = [tag['symbol'] for tag in data['symbolic_tags']]
                    print(f"   Detected symbols: {symbols}")
                    
                    # Check for expected symbols
                    found_expected = []
                    for expected in test_case['expected_symbols']:
                        if any(expected.lower() in symbol.lower() for symbol in symbols):
                            found_expected.append(expected)
                    
                    print(f"   Expected symbols found: {found_expected}")
                    print(f"   Coverage: {len(found_expected)}/{len(test_case['expected_symbols'])}")
                else:
                    print("   No symbolic tags detected")
            else:
                print(f"❌ API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure SoloHeart is running on port 5001")
        except Exception as e:
            print(f"❌ Error testing symbolic tags: {e}")

def test_goal_inference_api():
    """Test the goal inference API endpoint."""
    print("\n🧪 Testing Goal Inference API...")
    
    # Test session histories with different goal patterns
    test_sessions = [
        {
            "name": "Escape Scenario",
            "history": [
                {"role": "user", "content": "I need to get out of here quickly"},
                {"role": "assistant", "content": "You find yourself trapped in a dark dungeon. The walls are closing in."},
                {"role": "user", "content": "I'm trying to escape before it's too late"},
                {"role": "assistant", "content": "You spot a narrow passage that might lead to freedom."}
            ],
            "expected_goals": ["Escape", "Survive"]
        },
        {
            "name": "Discovery Quest",
            "history": [
                {"role": "user", "content": "I want to explore this ancient temple"},
                {"role": "assistant", "content": "You enter the mysterious ruins, eager to uncover its secrets."},
                {"role": "user", "content": "I'm searching for hidden knowledge and treasures"},
                {"role": "assistant", "content": "Ancient inscriptions hint at forgotten wisdom within."}
            ],
            "expected_goals": ["Discover", "Achieve"]
        },
        {
            "name": "Protection Mission",
            "history": [
                {"role": "user", "content": "I must protect the village from the approaching army"},
                {"role": "assistant", "content": "The innocent villagers look to you for salvation."},
                {"role": "user", "content": "I'll defend them with my life"},
                {"role": "assistant", "content": "Your courage inspires others to stand with you."}
            ],
            "expected_goals": ["Protect", "Achieve"]
        }
    ]
    
    for test_case in test_sessions:
        print(f"\n🎯 Testing: {test_case['name']}")
        
        try:
            response = requests.post('http://localhost:5001/api/goal/infer', 
                                   json={
                                       'session_history': test_case['history'],
                                       'memory_context': {},
                                       'current_turn': {'input': 'continue the story'}
                                   },
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received:")
                print(f"   Success: {data.get('success')}")
                
                if data.get('inferred_goals'):
                    goals = [goal['type'] for goal in data['inferred_goals']]
                    print(f"   Inferred goals: {goals}")
                    
                    # Check for expected goals
                    found_expected = []
                    for expected in test_case['expected_goals']:
                        if expected in goals:
                            found_expected.append(expected)
                    
                    print(f"   Expected goals found: {found_expected}")
                    print(f"   Coverage: {len(found_expected)}/{len(test_case['expected_goals'])}")
                    
                    # Show goal details
                    for goal in data['inferred_goals']:
                        print(f"   - {goal['type']}: {goal['justification']} (Confidence: {goal['confidence']:.1%})")
                else:
                    print("   No goals inferred")
            else:
                print(f"❌ API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure SoloHeart is running on port 5001")
        except Exception as e:
            print(f"❌ Error testing goal inference: {e}")

def test_enhanced_prompt_integration():
    """Test the enhanced prompt system with symbolism and goals."""
    print("\n🧪 Testing Enhanced Prompt Integration...")
    
    try:
        # Test a game action that should trigger symbolic and goal analysis
        action_data = {
            "input": "I want to explore the ancient ruins and discover their secrets"
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
                print(f"   Response Preview: {data['dm_response'][:150]}...")
                
                # Check if response shows enhanced understanding
                response_lower = data['dm_response'].lower()
                enhanced_indicators = ['explore', 'discover', 'ancient', 'secrets', 'ruins']
                found_indicators = [indicator for indicator in enhanced_indicators if indicator in response_lower]
                print(f"   Enhanced indicators found: {found_indicators}")
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
    print("🚀 SoloHeart Phase 7 - Symbolic Processing + GoalEngine Integration Test")
    print("=" * 70)
    
    # Test health first
    test_health_check()
    
    # Test symbolic tags API
    test_symbolic_tags_api()
    
    # Test goal inference API
    test_goal_inference_api()
    
    # Test enhanced prompt integration
    test_enhanced_prompt_integration()
    
    print("\n✅ Symbolic Processing + GoalEngine Integration Test Complete!")
    print("\n💡 To test the full interface:")
    print("   1. Start SoloHeart server")
    print("   2. Navigate to http://localhost:5001/game")
    print("   3. Check the sidebar for Symbolic Tags and Goal Engine")
    print("   4. Use the developer context toggle to see all sections")
    print("   5. Try different narrative actions to see symbolic analysis")

if __name__ == "__main__":
    main() 