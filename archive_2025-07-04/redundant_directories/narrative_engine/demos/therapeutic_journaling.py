#!/usr/bin/env python3
"""
Therapeutic Journaling Demo for The Narrative Engine

This demo shows how the narrative engine can be used for therapeutic journaling
with emotional processing and memory continuity.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Add the narrative_engine to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from narrative_engine.core.narrative_engine import NarrativeEngine
from narrative_engine.memory.layered_memory import LayeredMemorySystem
from narrative_engine.core.character_manager import Character

class TherapeuticJournalingDemo:
    """Demo for therapeutic journaling using The Narrative Engine"""
    
    def __init__(self):
        self.engine = NarrativeEngine(
            campaign_id="therapeutic_journaling",
            domain="therapy"
        )
        self.memory = LayeredMemorySystem(campaign_id="therapeutic_journaling")
        self.session_count = 0
        
    def start_session(self):
        """Start a new journaling session"""
        self.session_count += 1
        print(f"\n🧠 Therapeutic Journaling Session #{self.session_count}")
        print("=" * 50)
        print("Welcome to your therapeutic journaling session.")
        print("The system will remember your emotional journey and help you process experiences.")
        print("Type 'quit' to end the session, 'memories' to see your emotional history.")
        print()
        
    def process_entry(self, entry: str) -> str:
        """Process a journal entry and return therapeutic response"""
        # Store the entry with emotional analysis
        emotional_context = self._analyze_emotion(entry)
        
        memory_entry = {
            "content": entry,
            "memory_type": "episodic",
            "emotional_context": emotional_context,
            "tags": ["journaling", "therapy", "personal"],
            "timestamp": datetime.now().isoformat()
        }
        
        self.memory.store_memory(**memory_entry)
        
        # Generate therapeutic response
        response = self.engine.generate_narration(
            situation="Processing a journal entry",
            context=f"Entry: {entry[:100]}...",
            emotional_context=emotional_context
        )
        
        return response
    
    def _analyze_emotion(self, text: str) -> Dict[str, float]:
        """Simple emotion analysis (in a real system, this would use NLP)"""
        text_lower = text.lower()
        
        # Simple keyword-based emotion detection
        positive_words = ["happy", "joy", "excited", "grateful", "peaceful", "content"]
        negative_words = ["sad", "angry", "frustrated", "anxious", "worried", "stressed"]
        high_arousal_words = ["excited", "angry", "frustrated", "anxious", "stressed"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        high_arousal_count = sum(1 for word in high_arousal_words if word in text_lower)
        
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
        """Show emotional memory history"""
        memories = self.memory.recall_memories(
            query="journaling therapy personal",
            max_results=10
        )
        
        if not memories:
            print("No memories found yet. Start journaling to build your emotional history.")
            return
        
        print("\n📚 Your Emotional Journey:")
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
        """Run the interactive demo"""
        self.start_session()
        
        while True:
            try:
                entry = input("\n📝 Journal Entry: ").strip()
                
                if entry.lower() == 'quit':
                    print("\nThank you for your session. Your emotional journey is preserved.")
                    break
                elif entry.lower() == 'memories':
                    self.show_memories()
                    continue
                elif not entry:
                    continue
                
                # Process the entry
                response = self.process_entry(entry)
                
                print(f"\n🤖 Therapeutic Response:")
                print(f"{response}")
                
            except KeyboardInterrupt:
                print("\n\nSession ended. Take care!")
                break
            except Exception as e:
                print(f"\nError processing entry: {e}")

def main():
    """Main entry point for the demo"""
    print("Therapeutic Journaling Demo - The Narrative Engine")
    print("=" * 60)
    print("This demo shows how AI can support therapeutic journaling")
    print("with emotional memory and continuity.")
    print()
    
    demo = TherapeuticJournalingDemo()
    demo.run()

if __name__ == "__main__":
    main() 