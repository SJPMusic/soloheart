#!/usr/bin/env python3
"""
Creative Story Generator Demo for The Narrative Engine

This demo shows how the narrative engine can be used for interactive fiction
with persistent memory and character development.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

# Add the narrative_engine to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from narrative_engine.core.narrative_engine import NarrativeEngine
from narrative_engine.memory.layered_memory import LayeredMemorySystem
from narrative_engine.core.character_manager import Character, CharacterManager

class CreativeStoryGeneratorDemo:
    """Demo for creative story generation using The Narrative Engine"""
    
    def __init__(self):
        self.engine = NarrativeEngine(
            campaign_id="creative_story",
            domain="fiction"
        )
        self.memory = LayeredMemorySystem(campaign_id="creative_story")
        self.character_manager = CharacterManager()
        self.story_state = {
            "location": "A mysterious forest",
            "time": "dawn",
            "atmosphere": "mysterious",
            "characters": []
        }
        
    def start_story(self):
        """Start a new interactive story"""
        print(f"\n📚 Creative Story Generator")
        print("=" * 50)
        print("Welcome to your interactive story!")
        print("The system will remember your choices and develop the narrative accordingly.")
        print("Commands:")
        print("  'character <name> <description>' - Create a character")
        print("  'location <description>' - Change location")
        print("  'action <description>' - Describe an action")
        print("  'memories' - See story memory")
        print("  'quit' - End the story")
        print()
        
        # Initialize story
        self.memory.store_memory(
            content="The story begins in a mysterious forest at dawn",
            memory_type="episodic",
            emotional_context={"valence": 0.5, "arousal": 0.4, "dominance": 0.3},
            tags=["story_start", "forest", "dawn"]
        )
        
    def create_character(self, name: str, description: str):
        """Create a new character in the story"""
        character = Character(
            name=name,
            personality=description,
            current_emotion="curious"
        )
        
        self.story_state["characters"].append(character)
        
        # Store character creation in memory
        self.memory.store_memory(
            content=f"Character {name} enters the story: {description}",
            memory_type="episodic",
            emotional_context={"valence": 0.6, "arousal": 0.5, "dominance": 0.4},
            tags=["character_creation", name.lower()]
        )
        
        print(f"✨ {name} has joined your story!")
        
    def change_location(self, description: str):
        """Change the story location"""
        old_location = self.story_state["location"]
        self.story_state["location"] = description
        
        # Store location change in memory
        self.memory.store_memory(
            content=f"The story moves from {old_location} to {description}",
            memory_type="episodic",
            emotional_context={"valence": 0.5, "arousal": 0.6, "dominance": 0.4},
            tags=["location_change", "travel"]
        )
        
        print(f"📍 Location changed to: {description}")
        
    def process_action(self, action: str) -> str:
        """Process a story action and generate narrative response"""
        # Store the action in memory
        emotional_context = self._analyze_action_emotion(action)
        
        memory_entry = {
            "content": f"Action: {action}",
            "memory_type": "episodic",
            "emotional_context": emotional_context,
            "tags": ["action", "story_progression"],
            "timestamp": datetime.now().isoformat()
        }
        
        self.memory.store_memory(**memory_entry)
        
        # Generate narrative response
        context = f"Location: {self.story_state['location']}, Time: {self.story_state['time']}"
        if self.story_state["characters"]:
            context += f", Characters: {', '.join([c.name for c in self.story_state['characters']])}"
        
        response = self.engine.generate_narration(
            situation=f"Action: {action}",
            context=context,
            emotional_context=emotional_context
        )
        
        return response
    
    def _analyze_action_emotion(self, action: str) -> Dict[str, float]:
        """Analyze the emotional content of an action"""
        action_lower = action.lower()
        
        # Simple keyword-based emotion detection
        positive_words = ["help", "save", "find", "discover", "win", "achieve"]
        negative_words = ["fight", "lose", "fail", "hurt", "destroy", "kill"]
        high_arousal_words = ["run", "fight", "escape", "chase", "attack", "defend"]
        
        positive_count = sum(1 for word in positive_words if word in action_lower)
        negative_count = sum(1 for word in negative_words if word in action_lower)
        high_arousal_count = sum(1 for word in high_arousal_words if word in action_lower)
        
        # Calculate emotional dimensions
        valence = 0.5 + (positive_count - negative_count) * 0.1
        valence = max(0.0, min(1.0, valence))
        
        arousal = 0.3 + high_arousal_count * 0.15
        arousal = max(0.0, min(1.0, arousal))
        
        dominance = 0.5  # Neutral dominance
        
        return {
            "valence": valence,
            "arousal": arousal,
            "dominance": dominance
        }
    
    def show_memories(self):
        """Show story memory history"""
        memories = self.memory.recall_memories(
            query="story action character location",
            max_results=10
        )
        
        if not memories:
            print("No story memories yet. Start creating your narrative!")
            return
        
        print("\n📖 Story Memory:")
        print("-" * 40)
        
        for i, memory in enumerate(memories[:5], 1):
            content = memory.get("content", "")[:80] + "..." if len(memory.get("content", "")) > 80 else memory.get("content", "")
            emotion = memory.get("emotional_context", {})
            
            # Simple emotion label
            valence = emotion.get("valence", 0.5)
            if valence > 0.6:
                emotion_label = "😊 Positive"
            elif valence < 0.4:
                emotion_label = "😔 Negative"
            else:
                emotion_label = "😐 Neutral"
            
            print(f"{i}. {emotion_label} - {content}")
    
    def run(self):
        """Run the interactive story demo"""
        self.start_story()
        
        while True:
            try:
                command = input("\n🎭 Story Command: ").strip()
                
                if command.lower() == 'quit':
                    print("\nThe story ends here. Your narrative journey is preserved.")
                    break
                elif command.lower() == 'memories':
                    self.show_memories()
                    continue
                elif not command:
                    continue
                
                # Parse commands
                parts = command.split(' ', 1)
                if len(parts) < 2:
                    print("Please provide more details for your command.")
                    continue
                
                cmd_type, details = parts
                
                if cmd_type.lower() == 'character':
                    # Parse character creation: "character <name> <description>"
                    char_parts = details.split(' ', 1)
                    if len(char_parts) < 2:
                        print("Please provide both name and description for the character.")
                        continue
                    name, description = char_parts
                    self.create_character(name, description)
                    
                elif cmd_type.lower() == 'location':
                    self.change_location(details)
                    
                elif cmd_type.lower() == 'action':
                    response = self.process_action(details)
                    print(f"\n📖 Story Response:")
                    print(f"{response}")
                    
                else:
                    # Treat as an action
                    response = self.process_action(command)
                    print(f"\n📖 Story Response:")
                    print(f"{response}")
                
            except KeyboardInterrupt:
                print("\n\nStory ended. Thanks for creating with us!")
                break
            except Exception as e:
                print(f"\nError processing command: {e}")

def main():
    """Main entry point for the demo"""
    print("Creative Story Generator Demo - The Narrative Engine")
    print("=" * 60)
    print("This demo shows how AI can create interactive fiction")
    print("with persistent memory and character development.")
    print()
    
    demo = CreativeStoryGeneratorDemo()
    demo.run()

if __name__ == "__main__":
    main() 