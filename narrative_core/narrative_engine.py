from narrative_core.enhanced_memory_system import LayeredMemorySystem, MemoryType, MemoryLayer

class NarrativeEngine:
    def __init__(self):
        self.memory_system = LayeredMemorySystem(campaign_id='Default Campaign') 