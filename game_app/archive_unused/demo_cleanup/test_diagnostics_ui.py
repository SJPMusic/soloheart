#!/usr/bin/env python3
"""
Test script for Diagnostics UI Panel
Generates sample diagnostic data and tests the web interface
"""

import json
import time
from datetime import datetime, timedelta
import random

def generate_sample_diagnostics_data():
    """Generate comprehensive sample data for testing diagnostics panel"""
    
    # Sample conflict timeline
    conflicts = [
        {
            "id": "conflict_001",
            "description": "Internal struggle with newfound magical abilities",
            "type": "internal",
            "urgency": "high",
            "resolved": False,
            "characters_involved": ["player"],
            "resolution_action": None,
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
        },
        {
            "id": "conflict_002", 
            "description": "Disagreement with party member about treasure distribution",
            "type": "interpersonal",
            "urgency": "medium",
            "resolved": True,
            "characters_involved": ["player", "Alice"],
            "resolution_action": "Compromised on 60/40 split",
            "timestamp": (datetime.now() - timedelta(hours=4)).isoformat()
        },
        {
            "id": "conflict_003",
            "description": "Confrontation with local bandit leader",
            "type": "external",
            "urgency": "critical",
            "resolved": False,
            "characters_involved": ["player", "Alice"],
            "resolution_action": None,
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()
        },
        {
            "id": "conflict_004",
            "description": "Moral dilemma about using dark magic",
            "type": "internal",
            "urgency": "high",
            "resolved": True,
            "characters_involved": ["player"],
            "resolution_action": "Chose to resist temptation",
            "timestamp": (datetime.now() - timedelta(hours=6)).isoformat()
        }
    ]
    
    # Sample character arcs
    arcs = {
        "player": [
            {
                "arc_id": "arc_001",
                "title": "The Hero's Journey",
                "description": "Transformation from ordinary person to legendary hero",
                "status": "active",
                "milestones": [
                    {
                        "title": "Call to Adventure",
                        "description": "Discovered mysterious artifact in the forest"
                    },
                    {
                        "title": "Crossing the Threshold", 
                        "description": "Left home village for the first time"
                    },
                    {
                        "title": "First Trial",
                        "description": "Survived encounter with bandits"
                    }
                ]
            },
            {
                "arc_id": "arc_002",
                "title": "Magic Awakening",
                "description": "Learning to control newfound magical abilities",
                "status": "active",
                "milestones": [
                    {
                        "title": "Power Discovery",
                        "description": "First magical outburst during stress"
                    },
                    {
                        "title": "Training Begins",
                        "description": "Started studying with local mage"
                    }
                ]
            }
        ],
        "Alice": [
            {
                "arc_id": "arc_003",
                "title": "Redemption Quest",
                "description": "Seeking to atone for past mistakes",
                "status": "stalled",
                "milestones": [
                    {
                        "title": "Recognition of Guilt",
                        "description": "Realized the consequences of past actions"
                    }
                ]
            }
        ]
    }
    
    # Sample emotion heatmap data
    emotions = ["joy", "fear", "anger", "curiosity", "sadness", "wonder", "anxiety"]
    heatmap = {}
    
    for character in ["player", "Alice"]:
        heatmap[character] = []
        base_time = datetime.now() - timedelta(hours=8)
        
        for i in range(20):
            timestamp = base_time + timedelta(minutes=i * 30)
            heatmap[character].append({
                "timestamp": timestamp.isoformat(),
                "emotion": random.choice(emotions),
                "intensity": random.uniform(0.1, 1.0),
                "context": f"Event {i+1} for {character}"
            })
    
    # Sample diagnostic report
    report = {
        "total_actions": 47,
        "total_conflicts": 4,
        "resolved_conflicts": 2,
        "unresolved_conflicts": 2,
        "dominant_emotions": {
            "player": "curiosity",
            "Alice": "anxiety"
        },
        "arc_progress_summary": {
            "player": ["active", "active"],
            "Alice": ["stalled"]
        },
        "campaign_health_score": 0.75,
        "narrative_coherence": 0.82,
        "character_engagement": 0.68
    }
    
    return {
        "timeline": conflicts,
        "arcs": arcs,
        "heatmap": heatmap,
        "report": report
    }

def test_diagnostics_endpoints():
    """Test the diagnostics API endpoints"""
    import requests
    
    base_url = "http://localhost:5001"
    campaign_id = "demo-campaign"
    
    endpoints = [
        f"/api/campaign/{campaign_id}/diagnostics/timeline",
        f"/api/campaign/{campaign_id}/diagnostics/arcs", 
        f"/api/campaign/{campaign_id}/diagnostics/heatmap",
        f"/api/campaign/{campaign_id}/diagnostics/report"
    ]
    
    print("🔍 Testing Diagnostics API Endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}")
                print(f"   Status: {response.status_code}")
                print(f"   Data type: {type(data)}")
                if isinstance(data, list):
                    print(f"   Items: {len(data)}")
                elif isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())}")
                print()
            else:
                print(f"❌ {endpoint}")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {response.text}")
                print()
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}")
            print("   Error: Could not connect to server")
            print("   Make sure the web server is running on port 5001")
            print()
        except Exception as e:
            print(f"❌ {endpoint}")
            print(f"   Error: {str(e)}")
            print()

def main():
    """Main test function"""
    print("📈 Diagnostics UI Panel Test")
    print("=" * 50)
    
    # Generate sample data
    print("📊 Generating sample diagnostics data...")
    sample_data = generate_sample_diagnostics_data()
    
    # Save sample data for reference
    with open("sample_diagnostics_data.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    print("✅ Sample data saved to sample_diagnostics_data.json")
    print()
    
    # Test API endpoints
    test_diagnostics_endpoints()
    
    print("🎯 Next Steps:")
    print("1. Start the web server: python web_interface.py")
    print("2. Open http://localhost:5001 in your browser")
    print("3. Click the '📈 Diagnostics' button to open the panel")
    print("4. Verify all sections load and display correctly")
    print("5. Test filtering, export, and interaction features")
    print()
    
    print("📋 Expected Features:")
    print("✅ Conflict Timeline with filters")
    print("✅ Character Arc visualization")
    print("✅ Emotion Heatmap (placeholder)")
    print("✅ Diagnostic Report with export")
    print("✅ Responsive design")
    print("✅ Dark theme styling")

if __name__ == "__main__":
    main() 