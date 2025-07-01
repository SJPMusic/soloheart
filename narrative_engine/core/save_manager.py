import json
from typing import Any, Dict

"""
Save Manager for Solo DnD 5E Game Engine
Handles serialization and deserialization of game state.
Initial implementation uses JSON, but design allows for future backend swap (e.g., SQLite).
"""

def save_game(filename: str, state: Dict[str, Any]) -> None:
    """
    Save the entire game state to a JSON file.
    Args:
        filename: Path to the save file.
        state: Dictionary containing all relevant game state.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[SaveManager] Error saving game to {filename}: {e}")
        raise

def load_game(filename: str) -> Dict[str, Any]:
    """
    Load the entire game state from a JSON file.
    Args:
        filename: Path to the save file.
    Returns:
        Dictionary containing the loaded game state.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            state = json.load(f)
        return state
    except Exception as e:
        print(f"[SaveManager] Error loading game from {filename}: {e}")
        raise

# Future: Add backend registry for alternate storage (e.g., SQLite, cloud, etc.) 