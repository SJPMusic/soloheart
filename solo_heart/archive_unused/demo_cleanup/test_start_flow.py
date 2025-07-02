#!/usr/bin/env python3
"""
Test script for the start screen flow
"""

import json
import os
from start_screen_interface import StartScreenManager

def test_start_screen_flow():
    """Test the start screen flow functionality."""
    print("🧪 Testing Start Screen Flow...")
    
    # Initialize the manager
    manager = StartScreenManager()
    
    # Test 1: Get saved campaigns
    print("\n1. Testing campaign listing...")
    campaigns = manager.get_saved_campaigns()
    print(f"   Found {len(campaigns)} saved campaigns")
    
    # Test 2: Create a test character
    print("\n2. Testing character creation...")
    test_character = {
        'name': 'Test Character',
        'class': 'Fighter',
        'race': 'Human',
        'level': 1,
        'stats': {
            'strength': 15,
            'dexterity': 14,
            'constitution': 13,
            'intelligence': 10,
            'wisdom': 12,
            'charisma': 8
        }
    }
    
    # Test 3: Create a new campaign
    print("\n3. Testing campaign creation...")
    campaign_data = manager.create_new_campaign(test_character, "Test Campaign")
    if campaign_data:
        print(f"   ✅ Campaign created: {campaign_data['campaign_id']}")
        print(f"   Character: {campaign_data['active_character']['name']}")
        
        # Test 4: Verify campaign appears in list
        print("\n4. Testing campaign listing after creation...")
        updated_campaigns = manager.get_saved_campaigns()
        print(f"   Now found {len(updated_campaigns)} campaigns")
        
        # Test 5: Test campaign deletion
        print("\n5. Testing campaign deletion...")
        success = manager.delete_campaign(campaign_data['campaign_id'])
        if success:
            print("   ✅ Campaign deleted successfully")
        else:
            print("   ❌ Failed to delete campaign")
        
        # Test 6: Verify campaign is gone
        print("\n6. Testing campaign listing after deletion...")
        final_campaigns = manager.get_saved_campaigns()
        print(f"   Final count: {len(final_campaigns)} campaigns")
        
    else:
        print("   ❌ Failed to create campaign")
    
    print("\n✅ Start screen flow test completed!")

if __name__ == '__main__':
    test_start_screen_flow() 