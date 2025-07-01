#!/usr/bin/env python3
"""
Demo Runner for The Narrative Engine

This script allows users to choose and run different demos showcasing
the capabilities of The Narrative Engine.
"""

import sys
import os

# Add the narrative_engine to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_menu():
    """Display the demo selection menu"""
    print("The Narrative Engine - Demo Suite")
    print("=" * 50)
    print("Choose a demo to run:")
    print()
    print("1. Therapeutic Journaling")
    print("   - Emotional processing with memory continuity")
    print("   - AI-assisted therapeutic writing")
    print()
    print("2. Creative Story Generator")
    print("   - Interactive fiction with persistent memory")
    print("   - Character development and world building")
    print()
    print("3. Exit")
    print()

def main():
    """Main demo runner"""
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '1':
                print("\nStarting Therapeutic Journaling Demo...")
                from therapeutic_journaling import TherapeuticJournalingDemo
                demo = TherapeuticJournalingDemo()
                demo.run()
                
            elif choice == '2':
                print("\nStarting Creative Story Generator Demo...")
                from creative_story_generator import CreativeStoryGeneratorDemo
                demo = CreativeStoryGeneratorDemo()
                demo.run()
                
            elif choice == '3':
                print("\nThank you for exploring The Narrative Engine!")
                break
                
            else:
                print("\nInvalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\nDemo runner stopped. Goodbye!")
            break
        except Exception as e:
            print(f"\nError running demo: {e}")
            print("Please make sure you have the required dependencies installed.")

if __name__ == "__main__":
    main() 