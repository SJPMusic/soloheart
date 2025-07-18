#!/usr/bin/env python3
"""
Expanded Playtest Demo: Dynamic Campaign Orchestrator

Simulates a rich solo DnD session with multiple characters, decision points, and full narrative logging.
"""

import sys
import os
import time
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dnd_game.narrative_bridge import NarrativeBridge
from narrative_engine.memory.emotional_memory import EmotionType
from narrative_engine.journaling.player_journal import JournalEntryType
from narrative_engine.narrative_structure.character_arcs import ArcType, ArcStatus
from narrative_engine.narrative_structure.plot_threads import ThreadType, ThreadStatus

# --- CONFIG ---
CAMPAIGN_ID = "playtest-demo-campaign"
PLAYER_1 = {"id": "Aelric", "class": "Rogue", "bg": "Exiled Noble"}
PLAYER_2 = {"id": "Seraphine", "class": "Cleric", "bg": "Haunted Healer"}

PLAYER_ACTIONS = [
    (PLAYER_1["id"], "Aelric lights a torch and enters the forgotten crypt."),
    (PLAYER_2["id"], "Seraphine whispers a prayer and follows, her holy symbol glowing faintly."),
    (PLAYER_1["id"], "He inspects the mural on the wall and tries to decipher it."),
    (PLAYER_2["id"], "She senses a lingering sorrow in the air and tries to comfort any spirits present."),
    (PLAYER_1["id"], "He hears footsteps and hides in the shadows."),
    (PLAYER_2["id"], "Seraphine stands her ground, ready to protect her companion."),
    (PLAYER_1["id"], "Aelric prepares for combat as a figure emerges."),
    (PLAYER_2["id"], "She calls out, demanding the figure reveal itself in the name of the Light."),
    # Decision point: who confronts the figure?
    ("DECISION", "The figure offers a cursed artifact. Who will accept it: Aelric (risking corruption) or Seraphine (risking her faith)?"),
    (PLAYER_1["id"], "Aelric hesitates, then reaches for the artifact, determined to protect Seraphine."),
    (PLAYER_2["id"], "Seraphine prays for Aelric's soul, vowing to help him resist the curse."),
    (PLAYER_1["id"], "He questions the figure about their purpose here."),
    (PLAYER_2["id"], "She records the encounter in her journal, noting the emotional toll.")
]

# --- DEMO LOGIC ---
def print_section(title):
    print("\n" + "=" * 60)
    print(f"{title.upper()}")
    print("=" * 60)

def log_action(char_id, action):
    print_section(f"{char_id} Action: {action}")

def log_narration(narration):
    print("\n[Narration]")
    print(narration)

def log_memory(memories):
    print("\n[Memory Trace]")
    if not memories:
        print("No related memories found.")
        return
    for m in memories:
        emotion = m.get('emotion', 'Neutral')
        summary = m.get('content', m.get('summary', ''))
        print(f"- Emotion: {emotion} | {summary}")

def log_journal(journal_entries):
    print("\n[Journal Entry]")
    if not journal_entries:
        print("No new journal entries.")
        return
    for entry in journal_entries:
        print(f"- {entry.get('title', 'Untitled')}: {entry.get('content', '')[:100]}...")

def log_arcs(arcs):
    print("\n[Character Arcs]")
    if not arcs:
        print("No active arcs.")
        return
    for arc in arcs:
        print(f"- {arc.get('name', 'Unnamed')} ({arc.get('arc_type', '')}, {arc.get('status', '')}): {arc.get('description', '')}")
        if arc.get('completion_percentage'):
            print(f"  Progress: {arc['completion_percentage']*100:.1f}%")

def log_threads(threads):
    print("\n[Plot Threads]")
    if not threads:
        print("No open threads.")
        return
    for thread in threads:
        print(f"- {thread.get('name', 'Unnamed')} (Priority {thread.get('priority', 0)}): {thread.get('description', '')}")

def log_events(events):
    print("\n[Orchestrator Events]")
    if not events:
        print("No orchestration events triggered.")
        return
    for event in events:
        print(f"- {event.get('event_type', 'Unknown')} (Priority {event.get('priority', 0)}): {event.get('description', '')}")
        if event.get('suggested_response'):
            print(f"  Suggestion: {event['suggested_response']}")

def get_emotion_for_action(char_id, action):
    action_lower = action.lower()
    if char_id == PLAYER_2["id"] and ("sorrow" in action_lower or "comfort" in action_lower):
        return EmotionType.SADNESS
    if "crypt" in action_lower or "enter" in action_lower:
        return EmotionType.WONDER
    elif "inspect" in action_lower or "decipher" in action_lower:
        return EmotionType.CURIOSITY
    elif "footsteps" in action_lower or "hide" in action_lower:
        return EmotionType.FEAR
    elif "combat" in action_lower or "prepare" in action_lower:
        return EmotionType.ANTICIPATION
    elif "question" in action_lower or "figure" in action_lower:
        return EmotionType.DETERMINATION
    elif "prayer" in action_lower or "faith" in action_lower:
        return EmotionType.TRUST
    elif "artifact" in action_lower and "curse" in action_lower:
        return EmotionType.FEAR
    else:
        return EmotionType.DETERMINATION

def main():
    print("\n🎲 Expanded Playtest Demo: Dynamic Campaign Orchestrator\n" + "=" * 60)
    print(f"Initializing campaign '{CAMPAIGN_ID}' for players '{PLAYER_1['id']}' and '{PLAYER_2['id']}'...")

    bridge = NarrativeBridge(CAMPAIGN_ID)

    # Set up initial arcs and threads for both characters
    try:
        bridge.create_character_arc(
            character_id=PLAYER_1["id"],
            name="Redemption of the Exile",
            arc_type=ArcType.REDEMPTION,
            description="Aelric seeks to reclaim his lost honor and uncover the truth behind his exile.",
            tags=["redemption", "nobility", "mystery"],
            emotional_themes=["regret", "hope", "determination"]
        )
        bridge.create_character_arc(
            character_id=PLAYER_2["id"],
            name="Healing the Haunted",
            arc_type=ArcType.GROWTH,
            description="Seraphine must overcome her own trauma to heal others and herself.",
            tags=["healing", "trauma", "growth"],
            emotional_themes=["compassion", "sorrow", "hope"]
        )
        print("✅ Created initial character arcs")
    except Exception as e:
        print(f"⚠️ Could not create character arcs: {e}")
    try:
        bridge.create_plot_thread(
            name="Secrets of the Forgotten Crypt",
            thread_type=ThreadType.MYSTERY,
            description="Strange happenings and ancient secrets lie buried in the crypt.",
            priority=8,
            assigned_characters=[PLAYER_1["id"], PLAYER_2["id"]],
            tags=["crypt", "secrets", "supernatural"]
        )
        print("✅ Created initial plot thread")
    except Exception as e:
        print(f"⚠️ Could not create plot thread: {e}")

    # Simulate player actions
    for idx, (char_id, action) in enumerate(PLAYER_ACTIONS):
        if char_id == "DECISION":
            print_section("Decision Point")
            print(action)
            # Simulate a decision: Aelric accepts the artifact
            continue
        log_action(char_id, action)
        emotion = get_emotion_for_action(char_id, action)
        bridge.store_dnd_memory(
            content=f"{char_id} action: {action}",
            memory_type="action",
            metadata={"step": idx+1, "character": char_id},
            tags=["player_action", "playtest", char_id],
            primary_emotion=emotion,
            emotional_intensity=0.7
        )
        narration = bridge.generate_dm_narration(
            situation=action,
            player_actions=[action],
            world_context={"step": idx+1, "character": char_id},
            emotional_context=[emotion.name.lower()]
        )
        log_narration(narration)
        memories = bridge.recall_related_memories(action, max_results=3)
        log_memory(memories)
        # Journal entry for major actions or decision aftermath
        if idx == 0 or "artifact" in action or "curse" in action or "decision" in action:
            try:
                bridge.add_journal_entry(
                    character_id=char_id,
                    entry_type=JournalEntryType.PLAYER_WRITTEN,
                    title=f"Step {idx+1}: {action[:30]}...",
                    content=f"{char_id}: {action}\nNarration: {narration}",
                    tags=["playtest", "auto-journal", char_id],
                    emotional_context=[emotion.name.lower()]
                )
            except Exception as e:
                print(f"⚠️ Could not add journal entry: {e}")
        journal_entries = bridge.get_journal_entries(character_id=char_id, limit=2)
        log_journal(journal_entries)
        # Arc and thread progression
        try:
            arcs = bridge.get_character_arcs(character_id=char_id, status=ArcStatus.ACTIVE)
            log_arcs(arcs)
        except Exception as e:
            print(f"⚠️ Could not get character arcs: {e}")
            log_arcs([])
        try:
            threads = bridge.get_plot_threads(status=ThreadStatus.OPEN)
            log_threads(threads)
        except Exception as e:
            print(f"⚠️ Could not get plot threads: {e}")
            log_threads([])
        # Orchestrator events
        try:
            events = bridge.generate_orchestration_events(max_events=2)
            event_dicts = []
            for event in events:
                if hasattr(event, 'to_dict'):
                    event_dict = event.to_dict()
                else:
                    event_dict = event
                if 'event_type' in event_dict:
                    if event_dict['event_type'] == 'QUEST_SUGGESTION':
                        event_dict['suggested_response'] = "Consider investigating this quest."
                    elif event_dict['event_type'] == 'ENCOUNTER_TRIGGER':
                        event_dict['suggested_response'] = "Prepare for a potential encounter."
                    elif event_dict['event_type'] == 'CHARACTER_DEVELOPMENT':
                        event_dict['suggested_response'] = "This could be a moment for character growth."
                    elif event_dict['event_type'] == 'PLOT_DEVELOPMENT':
                        event_dict['suggested_response'] = "A plot development is unfolding."
                    else:
                        event_dict['suggested_response'] = "Something interesting is happening."
                event_dicts.append(event_dict)
            log_events(event_dicts)
        except Exception as e:
            print(f"⚠️ Could not generate orchestration events: {e}")
            log_events([])
        print("\n--- End of Step ---\n")
        time.sleep(1)
    print("\n🎲 Playtest complete. Review the above log for emergent narrative and orchestration quality.\n")

if __name__ == "__main__":
    main() 