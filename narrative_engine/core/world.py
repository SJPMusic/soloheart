from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Location:
    name: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)

@dataclass
class WorldState:
    locations: Dict[str, Location] = field(default_factory=dict)
    time_of_day: str = "morning"
    day: int = 1
    weather: str = "clear"
    global_flags: Dict[str, bool] = field(default_factory=dict)
    def add_location(self, location: Location):
        self.locations[location.name] = location
    def get_location(self, name: str) -> Optional[Location]:
        return self.locations.get(name)
    def advance_time(self, hours: int = 1):
        # Simple time logic
        tod = ["morning", "afternoon", "evening", "night"]
        idx = tod.index(self.time_of_day)
        idx = (idx + hours) % len(tod)
        self.time_of_day = tod[idx]
        if self.time_of_day == "morning":
            self.day += 1
