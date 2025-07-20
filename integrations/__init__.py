"""
SoloHeart Integration Layer

This package contains integration modules for connecting SoloHeart
with external systems like The Narrative Engine (TNE).
"""

from .tne_bridge import send_event_to_tne, fetch_goal_alignment, TNE_API_URL
from .tne_event_mapper import map_action_to_event, example_combat_event, MemoryLayer
from .tne_client import TNEClient

__all__ = [
    'send_event_to_tne', 
    'fetch_goal_alignment', 
    'TNE_API_URL',
    'map_action_to_event',
    'example_combat_event',
    'MemoryLayer',
    'TNEClient'
] 