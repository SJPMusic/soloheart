import random
from typing import Tuple, List, Dict

def roll_dice(sides: int, count: int = 1) -> List[int]:
    """Rolls a dice with the given number of sides, count times."""
    return [random.randint(1, sides) for _ in range(count)]

def roll_d20(advantage: bool = False, disadvantage: bool = False) -> Tuple[int, List[int]]:
    """
    Rolls a d20, with optional advantage/disadvantage.
    Returns (final_result, [all_rolls])
    """
    rolls = roll_dice(20, 2 if advantage or disadvantage else 1)
    if advantage:
        return max(rolls), rolls
    elif disadvantage:
        return min(rolls), rolls
    else:
        return rolls[0], rolls

def roll_multiple(dice_spec: str) -> Dict[str, List[int]]:
    """
    Rolls multiple dice based on a dice spec string, e.g. '2d6+1d8'.
    Returns a dict of {dice_type: [results]}.
    """
    import re
    result = {}
    for part in dice_spec.split('+'):
        match = re.match(r'(\d*)d(\d+)', part.strip())
        if match:
            count = int(match.group(1)) if match.group(1) else 1
            sides = int(match.group(2))
            key = f"{count}d{sides}"
            result[key] = roll_dice(sides, count)
    return result

def roll_with_modifier(sides: int, count: int = 1, modifier: int = 0) -> Tuple[int, List[int]]:
    """
    Rolls dice and adds a modifier to the total.
    Returns (total_with_modifier, [all_rolls])
    """
    rolls = roll_dice(sides, count)
    total = sum(rolls) + modifier
    return total, rolls 