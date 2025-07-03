#!/usr/bin/env python3
"""
Interactive CLI for testing The Narrative Engine.
Allows real-time testing of memory, recall, and narrative continuity.
"""

import sys
import os
from typing import List

# Add the narrative_engine directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import MemoryType, EngineConfig
from llm_interface.ollama_provider import OllamaProvider
from memory.memory_manager import MemoryManager
from engine.core_loop import NarrativeEngineCore

def print_banner():
    """Print the CLI banner."""
    print("🎭 The Narrative Engine - Interactive CLI")
    print("=" * 50)
    print("Type your narrative input and see how the engine responds.")
    print("Commands:")
    print("  /help     - Show this help")
    print("  /status   - Show engine status")
    print("  /search   - Search memories")
    print("  /add      - Manually add memory")
    print("  /clear    - Clear all memories")
    print("  /quit     - Exit")
    print("=" * 50)

def initialize_engine():
    """Initialize the narrative engine."""
    print("🚀 Initializing The Narrative Engine...")
    
    try:
        # Initialize LLM Provider
        llm_provider = OllamaProvider(model_name="llama3:latest")
        if not llm_provider.is_available:
            print("⚠️  Ollama not available. Engine will use fallback responses.")
        
        # Initialize Engine
        config = EngineConfig(
            model_name="llama3:latest",
            temperature=0.7,
            max_tokens=500,
            memory_retrieval_limit=5
        )
        engine = NarrativeEngineCore(llm_provider, config, "cli_memory.json")
        
        print("✅ Engine initialized successfully!")
        return engine
        
    except Exception as e:
        print(f"❌ Failed to initialize engine: {e}")
        return None

def show_status(engine: NarrativeEngineCore):
    """Show engine status."""
    summary = engine.get_conversation_summary()
    
    print("\n📊 Engine Status:")
    print(f"  Conversation turns: {summary['total_turns']}")
    print(f"  Total memories: {summary['total_memories']}")
    print(f"  LLM available: {summary['llm_available']}")
    
    print("\n  Memory breakdown:")
    for memory_type, count in summary['memory_types'].items():
        print(f"    {memory_type}: {count}")
    
    if summary['recent_memories']:
        print("\n  Recent memories:")
        for memory in summary['recent_memories'][:3]:
            print(f"    - {memory['content']} ({memory['type']})")

def search_memories(engine: NarrativeEngineCore):
    """Search memories interactively."""
    query = input("\n🔍 Enter search query: ").strip()
    if not query:
        return
    
    memories = engine.search_memories(query, limit=10)
    
    if memories:
        print(f"\n📚 Found {len(memories)} memories:")
        for i, memory in enumerate(memories, 1):
            print(f"  {i}. {memory['content']} ({memory['type']})")
            print(f"     Tags: {', '.join(memory['tags'])}")
    else:
        print("❌ No memories found for that query.")

def add_memory_manually(engine: NarrativeEngineCore):
    """Manually add a memory entry."""
    print("\n➕ Add Memory Manually")
    
    content = input("Content: ").strip()
    if not content:
        return
    
    print("\nMemory types:")
    for i, memory_type in enumerate(MemoryType, 1):
        print(f"  {i}. {memory_type.value}")
    
    try:
        type_choice = int(input("Choose type (1-5): ")) - 1
        memory_type = list(MemoryType)[type_choice]
    except (ValueError, IndexError):
        print("❌ Invalid choice. Using EVENT type.")
        memory_type = MemoryType.EVENT
    
    tags_input = input("Tags (comma-separated): ").strip()
    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
    
    memory_id = engine.add_memory_manually(content, memory_type, tags)
    print(f"✅ Memory added with ID: {memory_id}")

def main():
    """Main CLI loop."""
    print_banner()
    
    # Initialize engine
    engine = initialize_engine()
    if not engine:
        print("❌ Cannot start CLI without engine.")
        return
    
    print("\n🎯 Ready for narrative input!")
    
    while True:
        try:
            # Get user input
            user_input = input("\n🎭 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()
                
                if command == "/help":
                    print_banner()
                elif command == "/status":
                    show_status(engine)
                elif command == "/search":
                    search_memories(engine)
                elif command == "/add":
                    add_memory_manually(engine)
                elif command == "/clear":
                    confirm = input("⚠️  Clear all memories? (y/N): ").strip().lower()
                    if confirm == 'y':
                        engine.clear_memories()
                        print("✅ All memories cleared.")
                elif command == "/quit":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Unknown command. Type /help for available commands.")
                continue
            
            # Process narrative input
            print("🤖 Engine: ", end="", flush=True)
            response = engine.process_input(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 