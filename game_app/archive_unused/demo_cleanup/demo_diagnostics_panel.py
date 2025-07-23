#!/usr/bin/env python3
"""
Demo script for Diagnostics UI Panel
Shows the diagnostics panel functionality with sample data and real gameplay
"""

import json
import time
from datetime import datetime, timedelta
import random

def demo_diagnostics_panel():
    """Demonstrate the Diagnostics panel functionality"""
    
    print("📈 Diagnostics Panel Demo")
    print("=" * 60)
    
    # Simulate some gameplay to generate diagnostic data
    print("🎮 Simulating gameplay to generate diagnostic data...")
    
    # Create sample conflicts
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
        },
        {
            "id": "conflict_005",
            "description": "Trust issues with mysterious NPC",
            "type": "interpersonal",
            "urgency": "medium",
            "resolved": False,
            "characters_involved": ["player", "Mysterious Stranger"],
            "resolution_action": None,
            "timestamp": (datetime.now() - timedelta(hours=30)).isoformat()
        }
    ]
    
    print(f"✅ Generated {len(conflicts)} conflicts")
    
    # Create sample character arcs
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
                    },
                    {
                        "title": "Meeting the Mentor",
                        "description": "Encountered wise old mage who offered guidance"
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
                    },
                    {
                        "title": "First Controlled Spell",
                        "description": "Successfully cast a simple light spell"
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
            },
            {
                "arc_id": "arc_004",
                "title": "Finding Purpose",
                "description": "Discovering a new reason to fight",
                "status": "active",
                "milestones": [
                    {
                        "title": "Loss of Faith",
                        "description": "Became disillusioned with previous beliefs"
                    },
                    {
                        "title": "New Ally",
                        "description": "Found unexpected friendship with player character"
                    }
                ]
            }
        ]
    }
    
    print(f"✅ Generated character arcs for {len(arcs)} characters")
    
    # Create emotion heatmap data
    emotions = ["joy", "fear", "anger", "curiosity", "sadness", "wonder", "anxiety", "hope"]
    heatmap = {}
    
    for character in ["player", "Alice"]:
        heatmap[character] = []
        base_time = datetime.now() - timedelta(hours=12)
        
        for i in range(30):
            timestamp = base_time + timedelta(minutes=i * 25)
            emotion = random.choice(emotions)
            intensity = random.uniform(0.1, 1.0)
            
            # Add some narrative context
            contexts = [
                "Explored ancient ruins",
                "Fought bandits",
                "Discovered treasure",
                "Met mysterious NPC",
                "Learned new spell",
                "Made difficult choice",
                "Found hidden passage",
                "Solved puzzle",
                "Rescued villager",
                "Uncovered conspiracy"
            ]
            
            heatmap[character].append({
                "timestamp": timestamp.isoformat(),
                "emotion": emotion,
                "intensity": intensity,
                "context": random.choice(contexts)
            })
    
    print(f"✅ Generated emotion data for {len(heatmap)} characters")
    
    # Create diagnostic report
    report = {
        "total_actions": 47,
        "total_conflicts": 5,
        "resolved_conflicts": 2,
        "unresolved_conflicts": 3,
        "dominant_emotions": {
            "player": "curiosity",
            "Alice": "anxiety"
        },
        "arc_progress_summary": {
            "player": ["active", "active"],
            "Alice": ["stalled", "active"]
        },
        "campaign_health_score": 0.75,
        "narrative_coherence": 0.82,
        "character_engagement": 0.68,
        "conflict_resolution_rate": 0.4,
        "emotional_volatility": 0.65
    }
    
    print(f"✅ Generated comprehensive diagnostic report")
    print()
    
    # Display sample data
    print("📊 Sample Diagnostic Data Preview:")
    print("-" * 40)
    
    print(f"🔍 Conflicts: {len(conflicts)} total")
    resolved = sum(1 for c in conflicts if c['resolved'])
    print(f"   - Resolved: {resolved}")
    print(f"   - Unresolved: {len(conflicts) - resolved}")
    
    print(f"📈 Character Arcs: {sum(len(arcs[char]) for char in arcs)} total")
    for char, char_arcs in arcs.items():
        active = sum(1 for arc in char_arcs if arc['status'] == 'active')
        stalled = sum(1 for arc in char_arcs if arc['status'] == 'stalled')
        print(f"   - {char}: {active} active, {stalled} stalled")
    
    print(f"🔥 Emotion Data: {sum(len(heatmap[char]) for char in heatmap)} data points")
    for char in heatmap:
        print(f"   - {char}: {len(heatmap[char])} emotion records")
    
    print()
    
    # Show what the UI will display
    print("🖥️ UI Panel Features:")
    print("-" * 40)
    
    print("1. 📅 Conflict Timeline")
    print("   - Chronological list of all conflicts")
    print("   - Color-coded by type (internal/interpersonal/external)")
    print("   - Urgency indicators (critical/high/medium/low)")
    print("   - Resolution status with icons")
    print("   - Filters by character, type, and status")
    
    print("\n2. 📊 Character Arc Map")
    print("   - Progress bars for each arc")
    print("   - Milestone trees with descriptions")
    print("   - Status indicators (active/stalled/resolved)")
    print("   - Toggle to show/hide resolved arcs")
    
    print("\n3. 🔥 Emotion Heatmap")
    print("   - Time-series emotion data")
    print("   - Character-specific graphs")
    print("   - Intensity visualization")
    print("   - Export functionality")
    
    print("\n4. 📋 Diagnostic Report")
    print("   - Campaign statistics")
    print("   - Dominant emotions per character")
    print("   - Arc progress summary")
    print("   - Export to JSON")
    print("   - Copy to clipboard")
    
    print()
    
    # Save comprehensive sample data
    sample_data = {
        "timeline": conflicts,
        "arcs": arcs,
        "heatmap": heatmap,
        "report": report
    }
    
    with open("comprehensive_diagnostics_data.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print("💾 Sample data saved to comprehensive_diagnostics_data.json")
    print()
    
    # Instructions for testing
    print("🎯 How to Test the Diagnostics Panel:")
    print("=" * 50)
    print("1. Start the web server: python web_interface.py")
    print("2. Open http://localhost:5001 in your browser")
    print("3. Click the '📈 Diagnostics' button (right side)")
    print("4. Explore each section:")
    print("   - Try the timeline filters")
    print("   - Toggle arc visibility")
    print("   - Switch between character heatmaps")
    print("   - Export the diagnostic report")
    print("5. Test responsive design on mobile/tablet")
    print()
    
    print("✨ Key Features to Verify:")
    print("-" * 30)
    print("✅ Dark theme styling")
    print("✅ Smooth animations")
    print("✅ Real-time data loading")
    print("✅ Interactive filters")
    print("✅ Export functionality")
    print("✅ Mobile responsiveness")
    print("✅ Error handling")
    print()
    
    print("🚀 The Diagnostics Panel is ready for use!")
    print("It provides deep insights into campaign narrative dynamics,")
    print("character development, and emotional progression.")

if __name__ == "__main__":
    demo_diagnostics_panel() 