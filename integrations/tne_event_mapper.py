"""
TNE Event Mapper: Converts SoloHeart gameplay data into TNE-compatible memory events.
"""

from typing import Literal, Optional, List, Dict
from datetime import datetime, UTC

# Type for supported memory layers
MemoryLayer = Literal["episodic", "semantic", "emotional"]

def map_action_to_event(
    character_id: str,
    action_type: str,
    description: str,
    memory_layer: MemoryLayer = "episodic",
    tags: Optional[List[str]] = None,
    importance: float = 0.5,
    metadata: Optional[Dict] = None,
) -> dict:
    """
    Converts a SoloHeart action into a TNE memory event structure.
    
    Args:
        character_id (str): Unique identifier for the player character.
        action_type (str): High-level action type (e.g., "attack", "dialogue", "explore").
        description (str): Natural language summary of the action.
        memory_layer (Literal): Which memory layer to inject into (episodic, semantic, emotional).
        tags (List[str], optional): Symbolic or narrative tags (e.g., ["courage", "betrayal"]).
        importance (float): Value between 0.0 and 1.0 representing narrative weight.
        metadata (dict, optional): Additional gameplay metadata (e.g., roll outcome, NPC name).
    
    Returns:
        dict: TNE-formatted memory event.
    """
    return {
        "character_id": character_id,
        "timestamp": datetime.now(UTC).isoformat() + "Z",
        "description": description,
        "layer": memory_layer,
        "tags": tags or [],
        "importance": importance,
        "metadata": {
            "action_type": action_type,
            **(metadata or {})
        }
    }

def example_combat_event(character_id: str) -> dict:
    """
    Example function to demonstrate formatting a combat action.
    """
    return map_action_to_event(
        character_id=character_id,
        action_type="attack",
        description="Thalion lunged forward with his longsword, slashing at the ogre's exposed side.",
        memory_layer="episodic",
        tags=["violence", "courage", "aggression"],
        importance=0.8,
        metadata={
            "weapon": "longsword",
            "target": "ogre",
            "roll_result": 17
        }
    ) 