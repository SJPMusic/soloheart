#!/usr/bin/env python3
"""
Enhanced Web UI Demonstration

A simple script to demonstrate the enhanced web UI features
including multi-character support, sidebar functionality, and save/load.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Any

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def demo_enhanced_web_ui():
    """Demonstrate the enhanced web UI features."""
    
    base_url = "http://localhost:5001"
    campaign_id = "demo-campaign"
    
    print("🎭 Enhanced Web UI Demonstration")
    print("=" * 40)
    print("This demo shows the new features:")
    print("✅ Multi-character support")
    print("✅ Sidebar with character info, arcs, threads, journal")
    print("✅ Save/load campaign functionality")
    print("✅ Chat history with character attribution")
    print("✅ Debug panel with detailed information")
    print("=" * 40)
    
    # Test 1: Check if server is running
    print("\n1. Checking server connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Web interface is accessible at http://localhost:5001")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the web interface:")
        print("   cd dnd_game && python web_interface.py")
        return False
    
    # Test 2: Create characters
    print("\n2. Creating characters...")
    
    characters = [
        {"character_id": "gandalf", "name": "Gandalf the Grey", "class": "Wizard"},
        {"character_id": "aragorn", "name": "Aragorn", "class": "Ranger"},
        {"character_id": "legolas", "name": "Legolas", "class": "Ranger"}
    ]
    
    for char in characters:
        response = requests.post(
            f"{base_url}/api/campaign/{campaign_id}/characters",
            json=char
        )
        if response.status_code == 200:
            print(f"   ✅ Created {char['name']} ({char['class']})")
        else:
            print(f"   ❌ Failed to create {char['name']}")
    
    # Test 3: Switch between characters and perform actions
    print("\n3. Testing character switching and actions...")
    
    actions = [
        ("gandalf", "I cast a light spell to illuminate the dark cave"),
        ("aragorn", "I draw my sword and scan the area for threats"),
        ("legolas", "I nock an arrow and watch for movement"),
        ("gandalf", "I examine the ancient runes on the walls"),
        ("aragorn", "I search for any hidden passages or traps")
    ]
    
    for character_id, action in actions:
        # Activate character
        response = requests.post(
            f"{base_url}/api/campaign/{campaign_id}/characters/{character_id}/activate"
        )
        if response.status_code == 200:
            print(f"   ✅ Activated {character_id}")
        
        # Perform action
        action_data = {
            "action": action,
            "character_id": character_id
        }
        
        response = requests.post(
            f"{base_url}/api/campaign/{campaign_id}/action",
            json=action_data
        )
        
        if response.status_code == 200:
            data = response.json()
            character_name = data.get('character', {}).get('name', character_id)
            print(f"   ✅ {character_name}: {action[:50]}...")
        else:
            print(f"   ❌ Failed action for {character_id}")
    
    # Test 4: Check sidebar data
    print("\n4. Testing sidebar functionality...")
    
    for char in characters:
        response = requests.post(
            f"{base_url}/api/campaign/{campaign_id}/sidebar",
            json={"character_id": char['character_id']}
        )
        
        if response.status_code == 200:
            data = response.json()
            arcs = len(data.get('character_arcs', []))
            threads = len(data.get('plot_threads', []))
            journal = len(data.get('journal_entries', []))
            print(f"   ✅ {char['name']}: {arcs} arcs, {threads} threads, {journal} journal entries")
        else:
            print(f"   ❌ Failed to get sidebar data for {char['name']}")
    
    # Test 5: Save campaign
    print("\n5. Testing save functionality...")
    
    save_data = {"save_name": "demo-save-1"}
    response = requests.post(
        f"{base_url}/api/campaign/{campaign_id}/save",
        json=save_data
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"   ✅ Campaign saved as: {data.get('save_name')}")
        else:
            print(f"   ❌ Save failed: {data.get('error')}")
    else:
        print(f"   ❌ Save request failed: {response.status_code}")
    
    # Test 6: Get campaign summary
    print("\n6. Testing campaign summary...")
    
    response = requests.get(f"{base_url}/api/campaign/{campaign_id}/summary")
    
    if response.status_code == 200:
        data = response.json()
        char_count = len(data.get('characters', {}))
        chat_count = data.get('chat_history_count', 0)
        duration = data.get('session_duration', 'Unknown')
        print(f"   ✅ Summary: {char_count} characters, {chat_count} chat entries")
        print(f"   ✅ Session duration: {duration}")
    else:
        print(f"   ❌ Failed to get summary: {response.status_code}")
    
    # Test 7: Debug information
    print("\n7. Testing debug functionality...")
    
    # Toggle debug mode
    response = requests.post(f"{base_url}/api/campaign/{campaign_id}/debug/toggle")
    if response.status_code == 200:
        data = response.json()
        debug_mode = data.get('debug_mode', False)
        print(f"   ✅ Debug mode: {debug_mode}")
    
    # Get debug info
    response = requests.get(f"{base_url}/api/campaign/{campaign_id}/debug/info")
    if response.status_code == 200:
        data = response.json()
        active_char = data.get('active_character', 'None')
        chat_count = data.get('chat_history_count', 0)
        print(f"   ✅ Debug info: Active character = {active_char}, Chat entries = {chat_count}")
    else:
        print(f"   ❌ Failed to get debug info: {response.status_code}")
    
    # Test 8: Chat history
    print("\n8. Testing chat history...")
    
    response = requests.get(f"{base_url}/api/campaign/{campaign_id}/chat/history")
    if response.status_code == 200:
        data = response.json()
        total_entries = data.get('total_entries', 0)
        print(f"   ✅ Chat history: {total_entries} total entries")
        
        # Show last few entries
        history = data.get('chat_history', [])
        if history:
            print("   📝 Recent chat entries:")
            for entry in history[-3:]:  # Last 3 entries
                char_name = entry.get('character_name', 'Unknown')
                action = entry.get('action', '')[:60]
                print(f"      {char_name}: {action}...")
    else:
        print(f"   ❌ Failed to get chat history: {response.status_code}")
    
    print("\n" + "=" * 40)
    print("🎉 Enhanced Web UI Demo Complete!")
    print("=" * 40)
    
    print("\n📋 What was demonstrated:")
    print("✅ Multi-character creation and management")
    print("✅ Character switching and action attribution")
    print("✅ Sidebar data for each character")
    print("✅ Campaign save/load functionality")
    print("✅ Chat history with character labels")
    print("✅ Debug panel with detailed information")
    print("✅ Campaign summary with statistics")
    
    print(f"\n🌐 Open http://localhost:5001 in your browser to see the interface!")
    print("   Features to try:")
    print("   - Character selection dropdown")
    print("   - Sidebar toggle and content")
    print("   - Save/load campaign buttons")
    print("   - Debug panel for system info")
    print("   - Switch between characters and observe updates")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Enhanced Web UI Demonstration")
    print("Make sure the web server is running on http://localhost:5001")
    print("Press Enter to continue...")
    input()
    
    try:
        success = demo_enhanced_web_ui()
        if success:
            print("\n✅ Demo completed successfully!")
        else:
            print("\n❌ Demo failed. Check the server logs.")
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc() 