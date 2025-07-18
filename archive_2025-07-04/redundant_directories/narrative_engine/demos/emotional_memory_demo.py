#!/usr/bin/env python3
"""
Emotional Memory System Demo

Demonstrates the emotional tagging and recall capabilities of the memory system.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path to import the memory module
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.emotional_memory import (
    EmotionalMemoryEnhancer, 
    EmotionalMemoryFilter,
    EmotionType,
    EmotionalContext
)
from memory.layered_memory import LayeredMemorySystem, MemoryType, MemoryLayer


class DemoMemory:
    """Simple memory class for demonstration purposes."""
    
    def __init__(self, content, memory_type, emotional_context=None, metadata=None):
        self.content = content
        self.memory_type = memory_type
        self.emotional_context = emotional_context or []
        self.metadata = metadata or {}


def demo_emotional_memory_system():
    """Demonstrate the emotional memory system functionality."""
    print("💭 Emotional Memory System Demo")
    print("=" * 50)
    
    # Initialize the memory system and emotional components
    memory_system = LayeredMemorySystem()
    emotional_enhancer = EmotionalMemoryEnhancer()
    emotional_filter = EmotionalMemoryFilter()
    
    # Demo 1: Create memories with emotional context
    print("\n1. Creating Memories with Emotional Context")
    print("-" * 45)
    
    # Create some demo memories
    memories = []
    
    # Memory 1: Joyful discovery
    memory1 = DemoMemory(
        content="I found a beautiful ancient sword in the ruins! The blade gleams with magical energy and feels warm to the touch. This could be the legendary weapon I've been searching for.",
        memory_type=MemoryType.EVENT
    )
    emotional_enhancer.add_emotional_context(
        memory1,
        primary_emotion=EmotionType.JOY,
        intensity=0.9,
        secondary_emotions=[EmotionType.EXCITEMENT, EmotionType.WONDER],
        emotional_triggers=["discovery", "magical item", "achievement"],
        emotional_outcome="Feeling of accomplishment and wonder"
    )
    memories.append(memory1)
    print(f"✅ Created joyful memory: {memory1.content[:50]}...")
    
    # Memory 2: Fearful encounter
    memory2 = DemoMemory(
        content="A massive shadow emerged from the darkness. I could hear its heavy breathing and see glowing red eyes. My heart was pounding as I realized I was face to face with a creature of pure darkness.",
        memory_type=MemoryType.EVENT
    )
    emotional_enhancer.add_emotional_context(
        memory2,
        primary_emotion=EmotionType.FEAR,
        intensity=0.8,
        secondary_emotions=[EmotionType.ANXIETY, EmotionType.SURPRISE],
        emotional_triggers=["darkness", "unknown creature", "danger"],
        emotional_outcome="Heightened alertness and caution"
    )
    memories.append(memory2)
    print(f"✅ Created fearful memory: {memory2.content[:50]}...")
    
    # Memory 3: Sad loss
    memory3 = DemoMemory(
        content="My companion fell in battle today. We had traveled together for months, and now they're gone. I feel a deep emptiness inside, like a part of me has been lost forever.",
        memory_type=MemoryType.EVENT
    )
    emotional_enhancer.add_emotional_context(
        memory3,
        primary_emotion=EmotionType.SADNESS,
        intensity=0.95,
        secondary_emotions=[EmotionType.GRIEF, EmotionType.LOSS],
        emotional_triggers=["death", "companion", "loss"],
        emotional_outcome="Deep mourning and reflection"
    )
    memories.append(memory3)
    print(f"✅ Created sad memory: {memory3.content[:50]}...")
    
    # Memory 4: Angry betrayal
    memory4 = DemoMemory(
        content="I discovered that my trusted advisor has been working with the enemy all along. All those years of friendship, all those secrets shared, and it was all a lie. I feel betrayed and furious.",
        memory_type=MemoryType.EVENT
    )
    emotional_enhancer.add_emotional_context(
        memory4,
        primary_emotion=EmotionType.ANGER,
        intensity=0.85,
        secondary_emotions=[EmotionType.BETRAYAL, EmotionType.FRUSTRATION],
        emotional_triggers=["betrayal", "deception", "broken trust"],
        emotional_outcome="Vengeful determination"
    )
    memories.append(memory4)
    print(f"✅ Created angry memory: {memory4.content[:50]}...")
    
    # Memory 5: Hopeful moment
    memory5 = DemoMemory(
        content="The villagers finally agreed to work together to rebuild their homes. After weeks of conflict and division, seeing them united gives me hope that peace is possible.",
        memory_type=MemoryType.EVENT
    )
    emotional_enhancer.add_emotional_context(
        memory5,
        primary_emotion=EmotionType.HOPE,
        intensity=0.7,
        secondary_emotions=[EmotionType.INSPIRATION, EmotionType.SATISFACTION],
        emotional_triggers=["unity", "cooperation", "rebuilding"],
        emotional_outcome="Renewed optimism and determination"
    )
    memories.append(memory5)
    print(f"✅ Created hopeful memory: {memory5.content[:50]}...")
    
    # Demo 2: Filter memories by emotion
    print("\n2. Filtering Memories by Emotion")
    print("-" * 35)
    
    # Filter by specific emotion
    joyful_memories = emotional_filter.filter_by_emotion(memories, EmotionType.JOY, min_intensity=0.5)
    print(f"😊 Joyful memories (intensity >= 0.5): {len(joyful_memories)}")
    for memory in joyful_memories:
        print(f"  - {memory.content[:60]}...")
    
    fearful_memories = emotional_filter.filter_by_emotion(memories, EmotionType.FEAR, min_intensity=0.5)
    print(f"😨 Fearful memories (intensity >= 0.5): {len(fearful_memories)}")
    for memory in fearful_memories:
        print(f"  - {memory.content[:60]}...")
    
    # Filter by emotion group
    positive_memories = emotional_filter.filter_by_emotion_group(memories, "positive", min_intensity=0.5)
    print(f"😊 Positive emotion memories: {len(positive_memories)}")
    for memory in positive_memories:
        print(f"  - {memory.content[:60]}...")
    
    negative_memories = emotional_filter.filter_by_emotion_group(memories, "negative", min_intensity=0.5)
    print(f"😔 Negative emotion memories: {len(negative_memories)}")
    for memory in negative_memories:
        print(f"  - {memory.content[:60]}...")
    
    # Demo 3: Filter by intensity range
    print("\n3. Filtering by Emotional Intensity")
    print("-" * 35)
    
    # High intensity memories (0.8+)
    high_intensity = emotional_filter.filter_by_intensity_range(memories, min_intensity=0.8, max_intensity=1.0)
    print(f"🔥 High intensity memories (0.8-1.0): {len(high_intensity)}")
    for memory in high_intensity:
        primary_emotion = memory.emotional_context[0].primary_emotion.value if memory.emotional_context else "Unknown"
        intensity = memory.emotional_context[0].intensity if memory.emotional_context else 0.0
        print(f"  - {primary_emotion} (intensity: {intensity:.2f}): {memory.content[:50]}...")
    
    # Medium intensity memories (0.5-0.8)
    medium_intensity = emotional_filter.filter_by_intensity_range(memories, min_intensity=0.5, max_intensity=0.8)
    print(f"⚡ Medium intensity memories (0.5-0.8): {len(medium_intensity)}")
    for memory in medium_intensity:
        primary_emotion = memory.emotional_context[0].primary_emotion.value if memory.emotional_context else "Unknown"
        intensity = memory.emotional_context[0].intensity if memory.emotional_context else 0.0
        print(f"  - {primary_emotion} (intensity: {intensity:.2f}): {memory.content[:50]}...")
    
    # Demo 4: Emotional content analysis
    print("\n4. Automatic Emotional Content Analysis")
    print("-" * 40)
    
    # Test texts for emotional analysis
    test_texts = [
        "I am so happy to see you again! This is the best day ever!",
        "I'm terrified of what might be lurking in the shadows.",
        "I feel so sad and lonely without my friends around.",
        "I'm absolutely furious about what happened yesterday!",
        "I have hope that things will get better soon."
    ]
    
    for i, text in enumerate(test_texts, 1):
        analysis = emotional_enhancer.analyze_emotional_content(text)
        print(f"Text {i}: {text}")
        if analysis['emotional_content_detected']:
            print(f"  Primary emotion: {analysis['primary_emotion']}")
            print(f"  Intensity: {analysis['max_intensity']:.2f}")
            print(f"  Emotions found: {list(analysis['emotions_found'].keys())}")
        else:
            print("  No strong emotional content detected")
        print()
    
    # Demo 5: Memory statistics
    print("\n5. Emotional Memory Statistics")
    print("-" * 35)
    
    stats = emotional_filter.get_emotion_statistics(memories)
    print(f"📊 Emotional Memory Statistics:")
    print(f"  Total emotionally tagged memories: {stats['total_emotionally_tagged']}")
    print(f"  Average intensity: {stats['average_intensity']:.2f}")
    print(f"  Emotion groups available: {', '.join(stats['emotion_groups'])}")
    
    print("\n  Emotion breakdown:")
    for emotion, count in stats['emotion_counts'].items():
        print(f"    {emotion}: {count}")
    
    print("\n  Group breakdown:")
    for group, count in stats['group_counts'].items():
        print(f"    {group}: {count}")
    
    print("\n🎉 Emotional Memory System Demo Complete!")
    print("\nKey features demonstrated:")
    print("  ✅ Emotional context tagging")
    print("  ✅ Emotion-based filtering")
    print("  ✅ Intensity-based filtering")
    print("  ✅ Automatic emotional content analysis")
    print("  ✅ Emotional memory statistics")


if __name__ == "__main__":
    demo_emotional_memory_system() 