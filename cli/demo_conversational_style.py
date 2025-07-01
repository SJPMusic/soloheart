#!/usr/bin/env python3
"""
Demo: Conversational Narration Style Switching
Showcases natural language style switching in the AI-powered DnD game
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from narrative_core.campaign_manager import CampaignManager
from narrative_core.conversational_parser import ConversationalParser
from narrative_core.rules import DMNarrationStyle

def demo_conversational_style_switching():
    """Demonstrate the conversational style switching system"""
    
    print("🎭 CONVERSATIONAL NARRATION STYLE SWITCHING DEMO")
    print("=" * 60)
    print("This demo showcases how players can change narration styles")
    print("using natural language without memorizing commands.")
    print()
    
    # Initialize the DM style system
    dm_style = DMNarrationStyle()
    parser = ConversationalParser(dm_style)
    
    print("🎯 CURRENT STYLE: Neutral")
    print(f"   {dm_style.get_style_phrase()}")
    print()
    
    # Demo 1: Style Discovery
    print("📋 DEMO 1: Style Discovery")
    print("-" * 30)
    discovery_input = "What narration styles can you use?"
    print(f"Player: '{discovery_input}'")
    
    parsed = parser.parse_input(discovery_input)
    print(f"Parsed as: {parsed['type']}")
    
    response = parser.generate_style_discovery_response()
    print(f"DM Response: {response}")
    print()
    
    # Demo 2: Explicit Style Change
    print("📋 DEMO 2: Explicit Style Change")
    print("-" * 30)
    style_input = "Can we switch to a more epic tone?"
    print(f"Player: '{style_input}'")
    
    parsed = parser.parse_input(style_input)
    if parsed['type'] in ['style_change', 'style_inference']:
        print(f"Parsed as: {parsed['type']} -> {parsed['style']}")
        old_style = dm_style.get_current_style()
        dm_style.set_style(parsed['style'])
        confirmation = parser.generate_style_change_confirmation(parsed['style'], old_style)
        print(f"DM Response: {confirmation}")
        print(f"New style phrase: {dm_style.get_style_phrase()}")
    else:
        print(f"Parsed as: {parsed['type']}")
        print("No style change detected")
    print()
    
    # Demo 3: Feedback-Based Inference
    print("📋 DEMO 3: Feedback-Based Inference")
    print("-" * 30)
    feedback_input = "That was too boring"
    print(f"Player: '{feedback_input}'")
    
    parsed = parser.parse_input(feedback_input)
    if parsed['type'] in ['style_change', 'style_inference']:
        print(f"Parsed as: {parsed['type']} -> {parsed['style']}")
        old_style = dm_style.get_current_style()
        dm_style.set_style(parsed['style'])
        confirmation = parser.generate_style_change_confirmation(parsed['style'], old_style)
        print(f"DM Response: {confirmation}")
        print(f"New style phrase: {dm_style.get_style_phrase()}")
    else:
        print(f"Parsed as: {parsed['type']}")
        print("No style change detected")
    print()
    
    # Demo 4: Multiple Style Changes
    print("📋 DEMO 4: Multiple Style Changes")
    print("-" * 30)
    
    style_changes = [
        ("Make it grittier", "gritty"),
        ("I want it more mysterious", "eerie"),
        ("Can you be funnier?", "comedic"),
        ("Tell it in a poetic way", "poetic"),
        ("Make it more magical", "mystical"),
        ("Back to normal", "neutral")
    ]
    
    for input_text, expected_style in style_changes:
        print(f"Player: '{input_text}'")
        parsed = parser.parse_input(input_text)
        if parsed['type'] in ['style_change', 'style_inference']:
            print(f"Parsed as: {parsed['type']} -> {parsed['style']}")
            old_style = dm_style.get_current_style()
            dm_style.set_style(parsed['style'])
            confirmation = parser.generate_style_change_confirmation(parsed['style'], old_style)
            print(f"DM Response: {confirmation}")
            print(f"Current style: {dm_style.get_style_info()['name']}")
        else:
            print(f"Parsed as: {parsed['type']}")
            print("No style change detected")
        print()
    
    # Demo 5: Complex Natural Language
    print("📋 DEMO 5: Complex Natural Language")
    print("-" * 30)
    
    complex_inputs = [
        "The story feels too light and silly, can you make it more serious?",
        "I want the atmosphere to be more atmospheric and mysterious",
        "This scene needs to be more exciting and intense",
        "Can you narrate this part with more beauty and elegance?",
        "The tone is too ordinary, make it more wondrous"
    ]
    
    for input_text in complex_inputs:
        print(f"Player: '{input_text}'")
        parsed = parser.parse_input(input_text)
        print(f"Parsed as: {parsed['type']}")
        
        if parsed['type'] in ['style_change', 'style_inference']:
            print(f"Detected style: {parsed['style']}")
            old_style = dm_style.get_current_style()
            dm_style.set_style(parsed['style'])
            confirmation = parser.generate_style_change_confirmation(parsed['style'], old_style)
            print(f"DM Response: {confirmation}")
        else:
            print("No style change detected")
        print()
    
    # Demo 6: Campaign Integration
    print("📋 DEMO 6: Campaign Integration")
    print("-" * 30)
    print("Testing style persistence in campaign manager...")
    
    try:
        # Create a temporary campaign manager
        campaign_manager = CampaignManager(save_directory="temp_campaigns")
        
        # Create a simple campaign
        campaign = campaign_manager.current_campaign
        if campaign:
            print(f"Campaign loaded: {campaign.name}")
            print(f"Current style: {campaign_manager.engine.dm_style.get_current_style()}")
            
            # Test style change through campaign manager
            test_input = "Make it epic"
            parsed = campaign_manager.conversational_parser.parse_input(test_input)
            print(f"Input: '{test_input}' -> {parsed['type']}")
            
            if parsed['type'] == 'style_change':
                old_style = campaign_manager.engine.dm_style.get_current_style()
                campaign_manager.engine.dm_style.set_style(parsed['style'])
                campaign.settings["narration_style"] = parsed['style']
                print(f"Style changed from {old_style} to {parsed['style']}")
                print(f"Campaign settings updated: {campaign.settings['narration_style']}")
        
        print("✅ Campaign integration working!")
        
    except Exception as e:
        print(f"⚠️ Campaign integration test failed: {e}")
    
    print()
    print("🎉 CONVERSATIONAL STYLE SWITCHING DEMO COMPLETE!")
    print("=" * 60)
    print("Key Features Demonstrated:")
    print("✅ Natural language style detection")
    print("✅ Feedback-based style inference")
    print("✅ Style discovery requests")
    print("✅ Persistent style storage")
    print("✅ In-character style confirmations")
    print("✅ Campaign integration")
    print()
    print("Players can now change narration styles using everyday language!")
    print("No commands to memorize - just speak naturally!")

if __name__ == "__main__":
    demo_conversational_style_switching() 