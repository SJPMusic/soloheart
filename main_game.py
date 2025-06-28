#!/usr/bin/env python3
"""
Main Game Launcher for Solo DnD 5E

This is the main entry point for the solo DnD game engine.
It provides a structured game flow with:
- Campaign selection (new or continue)
- Character creation (step-by-step or vibe-based)
- Backstory integration
- Campaign launching
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from narrative_core.campaign_manager import CampaignManager

def print_banner():
    """Print the game banner."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    🎲 SOLO DnD 5E 🎲                        ║
    ║                                                              ║
    ║              AI-Powered Solo Adventure Engine                ║
    ║                                                              ║
    ║              Created by Stephen Miller                       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def print_menu():
    """Print the main menu."""
    print("\n🎮 MAIN MENU")
    print("=" * 50)
    print("1. Start New Campaign")
    print("2. Continue Existing Campaign")
    print("3. View Campaign List")
    print("4. Demo Quest Journal System")
    print("5. Exit")
    print("=" * 50)

def handle_new_campaign(campaign_manager: CampaignManager):
    """Handle new campaign creation."""
    print("\n🎲 NEW CAMPAIGN")
    print("=" * 50)
    
    try:
        campaign = campaign_manager.start_new_campaign()
        
        print(f"\n✅ Campaign '{campaign.name}' created successfully!")
        print(f"   Character: {campaign.character.name} the {campaign.character.character_class}")
        print(f"   Level: {campaign.character.level}")
        
        # Ask if they want to start playing immediately
        choice = input("\nWould you like to start playing now? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            campaign_manager.run_game_loop()
        
    except KeyboardInterrupt:
        print("\n❌ Campaign creation cancelled.")
    except Exception as e:
        print(f"\n❌ Error creating campaign: {e}")

def handle_continue_campaign(campaign_manager: CampaignManager):
    """Handle continuing an existing campaign."""
    print("\n📂 CONTINUE CAMPAIGN")
    print("=" * 50)
    
    # List available campaigns
    campaigns = campaign_manager.list_campaigns()
    
    if not campaigns:
        print("❌ No saved campaigns found.")
        print("   Please start a new campaign first.")
        return
    
    print("Available campaigns:")
    for i, campaign in enumerate(campaigns, 1):
        print(f"   {i}. {campaign['name']}")
        print(f"      Character: {campaign['character_name']} the {campaign['character_class']}")
        print(f"      Created: {campaign['created_date']}")
        print(f"      Last played: {campaign['last_played']}")
        print()
    
    try:
        choice = input("Enter campaign number to load: ").strip()
        campaign_index = int(choice) - 1
        
        if 0 <= campaign_index < len(campaigns):
            campaign_id = campaigns[campaign_index]['id']
            campaign = campaign_manager.load_campaign(campaign_id)
            
            if campaign:
                print(f"\n✅ Loaded campaign: {campaign.name}")
                choice = input("Would you like to start playing? (y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    campaign_manager.run_game_loop()
        else:
            print("❌ Invalid campaign number.")
    
    except ValueError:
        print("❌ Please enter a valid number.")
    except KeyboardInterrupt:
        print("\n❌ Campaign loading cancelled.")
    except Exception as e:
        print(f"\n❌ Error loading campaign: {e}")

def handle_view_campaigns(campaign_manager: CampaignManager):
    """Handle viewing campaign list."""
    print("\n📋 CAMPAIGN LIST")
    print("=" * 50)
    
    campaigns = campaign_manager.list_campaigns()
    
    if not campaigns:
        print("❌ No saved campaigns found.")
        return
    
    print(f"Found {len(campaigns)} campaign(s):")
    print()
    
    for i, campaign in enumerate(campaigns, 1):
        print(f"📁 Campaign {i}: {campaign['name']}")
        print(f"   🎭 Character: {campaign['character_name']} the {campaign['character_class']}")
        print(f"   📅 Created: {campaign['created_date']}")
        print(f"   🕒 Last played: {campaign['last_played']}")
        print()

def handle_demo_quest_journal(campaign_manager: CampaignManager):
    """Handle quest journal demo."""
    print("\n🎯 QUEST JOURNAL DEMO")
    print("=" * 50)
    
    try:
        # Import and run the demo
        from demo_quest_journal import main as run_demo
        run_demo()
    except ImportError:
        print("❌ Quest journal demo not found.")
        print("   Make sure demo_quest_journal.py exists in the project directory.")
    except Exception as e:
        print(f"❌ Error running demo: {e}")

def main():
    """Main game loop."""
    print_banner()
    
    # Initialize campaign manager
    print("🚀 Initializing game systems...")
    campaign_manager = CampaignManager()
    print("✅ Game systems ready!")
    
    while True:
        try:
            print_menu()
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                handle_new_campaign(campaign_manager)
            
            elif choice == "2":
                handle_continue_campaign(campaign_manager)
            
            elif choice == "3":
                handle_view_campaigns(campaign_manager)
            
            elif choice == "4":
                handle_demo_quest_journal(campaign_manager)
            
            elif choice == "5":
                print("\n👋 Thanks for playing Solo DnD 5E!")
                print("   May your adventures be epic and your rolls be natural 20s!")
                break
            
            else:
                print("❌ Invalid choice. Please enter a number between 1-5.")
            
            # Ask if they want to return to main menu
            if choice in ["1", "2", "4"]:
                input("\nPress Enter to return to main menu...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for playing Solo DnD 5E!")
            print("   May your adventures be epic and your rolls be natural 20s!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("   Please try again or contact support if the problem persists.")

if __name__ == "__main__":
    main() 