import unittest
import json
from datetime import datetime
from narrative_engine.memory.emotional_memory import EmotionalContext, EmotionalTone, EmotionalIntensity, EventType, emotional_memory_system
from narrative_engine.memory.memory_trace_logger import memory_trace_logger, MemoryOperation, TraceLevel
from dataclasses import asdict

def enum_to_value(obj):
    if isinstance(obj, list):
        return [enum_to_value(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: enum_to_value(v) for k, v in obj.items()}
    elif hasattr(obj, 'value'):
        return obj.value
    else:
        return obj

class TestEmotionalMemorySimulation(unittest.TestCase):
    """
    Simulate a solo gameplay interaction:
    - Player returns to a town where an NPC remembers a betrayal
    - NPC's response is emotionally shaped by memory recall (tone: bitter, memory: betrayal event, campaign-aware)
    - Demonstrates: emotional memory tagging, narrative interpretation, memory trace logging, co-authoring impact
    References: NarrativeEngine_Roadmap.txt (Emotional realism, narrative continuity, memory as sacred)
    """
    def test_npc_betrayal_memory(self):
        campaign_id = "DemoCampaign"
        npc_name = "Mayor Elric"
        player_name = "Aria"
        town = "Ravenwood"
        # Step 1: Tag the betrayal event in emotional memory
        betrayal_ctx = EmotionalContext(
            primary_tone=EmotionalTone.ANGER,
            intensity=EmotionalIntensity.INTENSE,
            event_type=EventType.BETRAYAL,
            character_name=npc_name,
            target_character=player_name,
            location=town,
            triggers=["Aria sided with bandits"],
            consequences=["Town suffered losses"]
        )
        mem_id = emotional_memory_system.add_emotional_memory(campaign_id, npc_name, betrayal_ctx)
        # Step 2: Log the memory operation
        trace = memory_trace_logger.log_memory_operation(
            campaign_id=campaign_id,
            source_module="emotional_memory_system",
            operation=MemoryOperation.STORE,
            memory_type="emotional",
            memory_id=mem_id,
            narrative_tags=["betrayal", "npc", "anger"],
            emotional_context=asdict(betrayal_ctx),
            trace_level=TraceLevel.INFO,
            metadata={"player": player_name, "location": town},
            success=True
        )
        # Step 3: Simulate player returning to town
        situation = f"{player_name} returns to {town} after the betrayal."
        response = emotional_memory_system.generate_emotional_response(
            character_name=npc_name,
            situation=situation,
            target_character=player_name,
            campaign_id=campaign_id
        )
        # Step 4: Output all as JSON-compatible data
        # Convert enums in trace_log to their .value for JSON compatibility
        trace_log_dict = asdict(trace)
        for k, v in trace_log_dict.items():
            if hasattr(v, 'value'):
                trace_log_dict[k] = v.value
        # Also convert enums in relevant_memories
        for mem in response["relevant_memories"]:
            for k, v in mem.items():
                if hasattr(v, 'value'):
                    mem[k] = v.value
        output = {
            "scenario": situation,
            "npc": npc_name,
            "emotional_state": response["emotional_state"],
            "emotional_response": response["emotional_response"],
            "relevant_memories": response["relevant_memories"],
            "trace_log": trace_log_dict,
            "narrative_interpretation": (
                f"{npc_name} greets {player_name} with a bitter tone, recalling the betrayal. "
                f"Their response is shaped by anger and the memory of {betrayal_ctx.triggers[0]}."
            )
        }
        print(json.dumps(enum_to_value(output), indent=2))
        # Assertions for test validity
        self.assertEqual(response["emotional_response"]["dominant_emotion"], EmotionalTone.ANGER.value)
        self.assertTrue(any(m["event_type"] == EventType.BETRAYAL.value for m in response["relevant_memories"]))
        self.assertIn("betrayal", trace.narrative_tags)
        self.assertEqual(output["emotional_response"]["tone_modifier"], "sharp and direct")

if __name__ == "__main__":
    unittest.main() 