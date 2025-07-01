from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from .core import Character

@dataclass
class Encounter:
    type: str  # 'combat', 'social', 'exploration', etc.
    participants: List[Character]
    description: str = ""
    state: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    outcome: Optional[str] = None

    def resolve(self, rules_engine=None):
        # Placeholder: actual resolution logic depends on type
        if self.type == 'combat':
            self.outcome = 'combat_resolved'  # Placeholder
        elif self.type == 'social':
            self.outcome = 'social_resolved'
        else:
            self.outcome = 'resolved'
        self.resolved = True
        return self.outcome

# --- Encounter Generation ---
def generate_encounter(encounter_type: str, participants: List[Character], description: str = "") -> Encounter:
    return Encounter(type=encounter_type, participants=participants, description=description)
