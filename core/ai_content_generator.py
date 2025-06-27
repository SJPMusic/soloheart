"""
AI Content Generator for DnD 5E Campaign
========================================

Generates dynamic content using campaign memory and AI integration
"""

import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .memory_system import CampaignMemorySystem, CampaignEntity

@dataclass
class ContentRequest:
    """Request for AI-generated content"""
    content_type: str  # 'npc', 'location', 'quest', 'dialogue', 'description'
    context: Dict[str, Any]
    player_preferences: Dict[str, Any]
    campaign_state: Dict[str, Any]

@dataclass
class GeneratedContent:
    """Generated content with metadata"""
    content: str
    content_type: str
    entities_involved: List[str]
    continuity_notes: List[str]
    confidence: float

class AIContentGenerator:
    """Generates dynamic DnD content using memory system"""
    
    def __init__(self, memory_system: CampaignMemorySystem):
        self.memory = memory_system
        self.templates = self._load_templates()
        self.name_generators = self._load_name_generators()
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load content templates"""
        return {
            'npc_description': [
                "{name} is a {race} {class} who {personality_trait}. They {appearance} and {mannerism}.",
                "You encounter {name}, a {race} {class} with {appearance}. They {personality_trait} and {mannerism}.",
                "{name} appears before you - a {race} {class} who {appearance}. They {personality_trait}."
            ],
            'location_description': [
                "You find yourself in {location_name}, a {location_type} where {description}. {atmosphere}.",
                "{location_name} stretches before you - a {location_type} with {description}. {atmosphere}.",
                "The {location_type} of {location_name} surrounds you. {description} {atmosphere}."
            ],
            'quest_introduction': [
                "{npc_name} approaches you with a troubled expression. '{quest_hook}' they say.",
                "As you enter {location_name}, {npc_name} rushes over. '{quest_hook}' they plead.",
                "{npc_name} gestures you closer. 'I have need of brave adventurers,' they begin. '{quest_hook}'"
            ]
        }
    
    def _load_name_generators(self) -> Dict[str, List[str]]:
        """Load name generation components"""
        return {
            'first_names': [
                'Aldric', 'Branwen', 'Cedric', 'Dwyn', 'Eira', 'Faelan', 'Gareth', 'Helena',
                'Ivor', 'Jocelyn', 'Kael', 'Lysandra', 'Mael', 'Niamh', 'Orion', 'Phaedra',
                'Quinn', 'Rhiannon', 'Soren', 'Thalia', 'Ulfric', 'Vesper', 'Wren', 'Xander'
            ],
            'last_names': [
                'Blackwood', 'Stormwind', 'Ironheart', 'Silverleaf', 'Darkwater', 'Brightforge',
                'Shadowborn', 'Lightweaver', 'Frostborn', 'Fireheart', 'Earthshaker', 'Windwalker'
            ],
            'titles': [
                'the Wise', 'the Brave', 'the Cunning', 'the Mysterious', 'the Noble',
                'the Wanderer', 'the Guardian', 'the Seeker', 'the Protector', 'the Ancient'
            ]
        }
    
    def generate_npc(self, context: Dict[str, Any]) -> GeneratedContent:
        """Generate a new NPC with full context"""
        # Get relevant campaign context
        campaign_context = self._get_campaign_context(context)
        
        # Generate NPC details
        name = self._generate_name()
        race = self._select_race(context.get('location_type', 'general'))
        character_class = self._select_class(context.get('quest_type', 'general'))
        personality = self._generate_personality(campaign_context)
        appearance = self._generate_appearance(race)
        mannerism = self._generate_mannerism(personality)
        
        # Create NPC description
        template = random.choice(self.templates['npc_description'])
        description = template.format(
            name=name,
            race=race,
            class=character_class,
            personality_trait=personality,
            appearance=appearance,
            mannerism=mannerism
        )
        
        # Create NPC entity for memory system
        npc_entity = CampaignEntity(
            id="",
            name=name,
            entity_type="npc",
            description=description,
            attributes={
                'race': race,
                'class': character_class,
                'personality': personality,
                'appearance': appearance,
                'mannerism': mannerism
            },
            relationships={},
            first_mentioned=context.get('session_id', 'current'),
            last_updated=context.get('session_id', 'current'),
            confidence=0.9,
            context_snippets=[description]
        )
        
        return GeneratedContent(
            content=description,
            content_type='npc',
            entities_involved=[name],
            continuity_notes=[f"New NPC {name} created in {context.get('location_name', 'unknown location')}"],
            confidence=0.9
        )
    
    def generate_location(self, context: Dict[str, Any]) -> GeneratedContent:
        """Generate a new location description"""
        campaign_context = self._get_campaign_context(context)
        
        location_name = self._generate_location_name()
        location_type = self._select_location_type(context.get('biome', 'general'))
        description = self._generate_location_description(location_type, campaign_context)
        atmosphere = self._generate_atmosphere(location_type, context.get('time_of_day', 'day'))
        
        template = random.choice(self.templates['location_description'])
        full_description = template.format(
            location_name=location_name,
            location_type=location_type,
            description=description,
            atmosphere=atmosphere
        )
        
        return GeneratedContent(
            content=full_description,
            content_type='location',
            entities_involved=[location_name],
            continuity_notes=[f"New location {location_name} discovered"],
            confidence=0.85
        )
    
    def generate_quest(self, context: Dict[str, Any]) -> GeneratedContent:
        """Generate a quest with continuity"""
        campaign_context = self._get_campaign_context(context)
        
        # Find relevant NPCs or create one
        npc_name = self._find_relevant_npc(campaign_context) or self._generate_name()
        quest_type = self._select_quest_type(context.get('player_level', 1))
        quest_hook = self._generate_quest_hook(quest_type, campaign_context)
        
        template = random.choice(self.templates['quest_introduction'])
        quest_intro = template.format(
            npc_name=npc_name,
            location_name=context.get('location_name', 'the area'),
            quest_hook=quest_hook
        )
        
        return GeneratedContent(
            content=quest_intro,
            content_type='quest',
            entities_involved=[npc_name],
            continuity_notes=[f"Quest offered by {npc_name} in {context.get('location_name', 'current location')}"],
            confidence=0.8
        )
    
    def _get_campaign_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant campaign context from memory"""
        relevant_entities = []
        
        # Search for relevant entities
        if 'location_name' in context:
            search_results = self.memory.search_campaign_memory(context['location_name'])
            relevant_entities.extend([r['data'] for r in search_results if r['type'] == 'entity'])
        
        if 'quest_type' in context:
            search_results = self.memory.search_campaign_memory(context['quest_type'])
            relevant_entities.extend([r['data'] for r in search_results if r['type'] == 'entity'])
        
        return {
            'relevant_entities': relevant_entities,
            'campaign_summary': self.memory.get_campaign_summary(),
            'recent_events': self._get_recent_events()
        }
    
    def _generate_name(self) -> str:
        """Generate a fantasy name"""
        first_name = random.choice(self.name_generators['first_names'])
        last_name = random.choice(self.name_generators['last_names'])
        title = random.choice(self.name_generators['titles'])
        
        return f"{first_name} {last_name}, {title}"
    
    def _generate_location_name(self) -> str:
        """Generate a location name"""
        prefixes = ['The', 'Fort', 'Castle', 'Tower', 'Village', 'Town', 'City', 'Keep']
        names = ['Raven', 'Storm', 'Iron', 'Silver', 'Shadow', 'Light', 'Frost', 'Fire']
        suffixes = ['hold', 'crest', 'spire', 'haven', 'watch', 'gate', 'bridge', 'crossing']
        
        prefix = random.choice(prefixes)
        name = random.choice(names)
        suffix = random.choice(suffixes)
        
        return f"{prefix} {name}{suffix}"
    
    def _select_race(self, location_type: str) -> str:
        """Select appropriate race for location"""
        race_locations = {
            'forest': ['elf', 'druid', 'ranger'],
            'mountain': ['dwarf', 'goliath', 'dragonborn'],
            'city': ['human', 'halfling', 'gnome'],
            'underground': ['dwarf', 'drow', 'duergar'],
            'general': ['human', 'elf', 'dwarf', 'halfling', 'gnome', 'dragonborn']
        }
        
        races = race_locations.get(location_type, race_locations['general'])
        return random.choice(races)
    
    def _select_class(self, quest_type: str) -> str:
        """Select appropriate class for quest"""
        class_quests = {
            'combat': ['fighter', 'barbarian', 'paladin'],
            'stealth': ['rogue', 'ranger', 'monk'],
            'magic': ['wizard', 'sorcerer', 'warlock'],
            'healing': ['cleric', 'druid', 'paladin'],
            'general': ['fighter', 'rogue', 'wizard', 'cleric', 'ranger', 'barbarian']
        }
        
        classes = class_quests.get(quest_type, class_quests['general'])
        return random.choice(classes)
    
    def _generate_personality(self, campaign_context: Dict[str, Any]) -> str:
        """Generate personality based on campaign context"""
        personalities = [
            "speaks in riddles and ancient proverbs",
            "is direct and to the point",
            "seems nervous and constantly looks over their shoulder",
            "radiates confidence and authority",
            "appears wise beyond their years",
            "has a mysterious air about them",
            "is friendly and welcoming",
            "seems guarded and suspicious"
        ]
        
        return random.choice(personalities)
    
    def _generate_appearance(self, race: str) -> str:
        """Generate appearance based on race"""
        race_appearances = {
            'elf': ['tall and graceful with pointed ears', 'ethereal beauty with silver hair'],
            'dwarf': ['stout and strong with a thick beard', 'broad-shouldered with braided hair'],
            'human': ['average height with weathered features', 'tall and well-built'],
            'halfling': ['small and cheerful with curly hair', 'diminutive with bright eyes'],
            'gnome': ['tiny with twinkling eyes', 'small stature with wild hair'],
            'dragonborn': ['scaled and imposing with draconic features', 'tall with reptilian eyes']
        }
        
        appearances = race_appearances.get(race, ['has distinctive features'])
        return random.choice(appearances)
    
    def _generate_mannerism(self, personality: str) -> str:
        """Generate mannerism based on personality"""
        mannerisms = [
            "fidgets with their hands while speaking",
            "maintains steady eye contact",
            "speaks with measured, deliberate words",
            "gestures animatedly while talking",
            "keeps their distance and speaks softly",
            "leans forward with intense interest",
            "crosses their arms defensively",
            "nods frequently in agreement"
        ]
        
        return random.choice(mannerisms)
    
    def _select_location_type(self, biome: str) -> str:
        """Select location type based on biome"""
        biome_locations = {
            'forest': ['ancient grove', 'mystical clearing', 'dense thicket'],
            'mountain': ['rocky outcropping', 'mountain pass', 'cave entrance'],
            'desert': ['oasis', 'sand dune', 'rocky canyon'],
            'swamp': ['marsh clearing', 'bog island', 'misty fen'],
            'general': ['clearing', 'path', 'ruins', 'settlement']
        }
        
        locations = biome_locations.get(biome, biome_locations['general'])
        return random.choice(locations)
    
    def _generate_location_description(self, location_type: str, campaign_context: Dict[str, Any]) -> str:
        """Generate location description"""
        descriptions = [
            "trees tower overhead like ancient sentinels",
            "stones are worn smooth by countless years",
            "mist swirls around your feet",
            "the air crackles with magical energy",
            "shadows dance in the flickering light",
            "the ground is covered in strange markings",
            "wind whispers through the branches",
            "the atmosphere feels heavy with history"
        ]
        
        return random.choice(descriptions)
    
    def _generate_atmosphere(self, location_type: str, time_of_day: str) -> str:
        """Generate atmospheric description"""
        atmospheres = [
            "The air feels charged with anticipation.",
            "A sense of ancient power lingers here.",
            "The silence is almost deafening.",
            "You feel as though you're being watched.",
            "The place seems to breathe with its own life.",
            "An aura of mystery surrounds everything.",
            "The atmosphere is thick with tension.",
            "A peaceful calm settles over the area."
        ]
        
        return random.choice(atmospheres)
    
    def _find_relevant_npc(self, campaign_context: Dict[str, Any]) -> Optional[str]:
        """Find an existing NPC from campaign memory"""
        entities = campaign_context.get('relevant_entities', [])
        npcs = [e for e in entities if e.get('entity_type') == 'npc']
        
        if npcs:
            return random.choice(npcs)['name']
        return None
    
    def _select_quest_type(self, player_level: int) -> str:
        """Select quest type based on player level"""
        if player_level <= 3:
            return 'general'
        elif player_level <= 7:
            return random.choice(['combat', 'stealth', 'general'])
        else:
            return random.choice(['combat', 'stealth', 'magic', 'healing'])
    
    def _generate_quest_hook(self, quest_type: str, campaign_context: Dict[str, Any]) -> str:
        """Generate quest hook based on type"""
        hooks = {
            'combat': [
                "There are bandits terrorizing the local villages. We need someone to deal with them.",
                "A dangerous beast has been spotted in the area. Can you hunt it down?",
                "The guards are overwhelmed. We need help defending the town."
            ],
            'stealth': [
                "Something valuable was stolen. We need someone to retrieve it quietly.",
                "There's a spy in our midst. Can you help us find them?",
                "We need information from a heavily guarded location."
            ],
            'magic': [
                "Strange magical disturbances have been reported. Can you investigate?",
                "An ancient artifact has awakened. We need someone to study it.",
                "Magical creatures have been appearing. We need to understand why."
            ],
            'healing': [
                "People are falling ill with a mysterious sickness. Can you help?",
                "The healing supplies are running low. We need someone to gather more.",
                "There's been an accident. We need healing magic immediately."
            ],
            'general': [
                "We have a problem that needs solving. Are you up for the challenge?",
                "Something strange is happening. Can you investigate?",
                "We need help with a delicate situation."
            ]
        }
        
        quest_hooks = hooks.get(quest_type, hooks['general'])
        return random.choice(quest_hooks)
    
    def _get_recent_events(self) -> List[Dict[str, Any]]:
        """Get recent campaign events"""
        summary = self.memory.get_campaign_summary()
        return summary.get('recent_activity', []) 