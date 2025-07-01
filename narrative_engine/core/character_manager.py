"""
Character Management System for DnD 5E
======================================

Handles character creation, "vibe coding", and 5E rules compliance
"""

import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class AbilityScore(Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"

class CharacterClass(Enum):
    BARBARIAN = "barbarian"
    BARD = "bard"
    CLERIC = "cleric"
    DRUID = "druid"
    FIGHTER = "fighter"
    MONK = "monk"
    PALADIN = "paladin"
    RANGER = "ranger"
    ROGUE = "rogue"
    SORCERER = "sorcerer"
    WARLOCK = "warlock"
    WIZARD = "wizard"

class Race(Enum):
    DRAGONBORN = "dragonborn"
    DWARF = "dwarf"
    ELF = "elf"
    GNOME = "gnome"
    HALF_ELF = "half-elf"
    HALF_ORC = "half-orc"
    HALFLING = "halfling"
    HUMAN = "human"
    TIEFLING = "tiefling"

@dataclass
class Character:
    """DnD 5E Character with all attributes"""
    name: str
    race: Race
    character_class: CharacterClass
    level: int = 1
    ability_scores: Dict[AbilityScore, int] = None
    hit_points: int = 0
    armor_class: int = 10
    background: str = ""
    personality_traits: List[str] = None
    ideals: List[str] = None
    bonds: List[str] = None
    flaws: List[str] = None
    proficiencies: List[str] = None
    equipment: List[str] = None
    spells: List[str] = None
    features: List[str] = None
    custom_flavor: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.ability_scores is None:
            self.ability_scores = {}
        if self.personality_traits is None:
            self.personality_traits = []
        if self.ideals is None:
            self.ideals = []
        if self.bonds is None:
            self.bonds = []
        if self.flaws is None:
            self.flaws = []
        if self.proficiencies is None:
            self.proficiencies = []
        if self.equipment is None:
            self.equipment = []
        if self.spells is None:
            self.spells = []
        if self.features is None:
            self.features = []
        if self.custom_flavor is None:
            self.custom_flavor = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary for serialization"""
        return asdict(self)

class CharacterManager:
    """Manages character creation and customization"""
    
    def __init__(self):
        self.races_data = self._load_races_data()
        self.classes_data = self._load_classes_data()
        self.backgrounds_data = self._load_backgrounds_data()
        self.spells_data = self._load_spells_data()
        self.characters: Dict[str, Character] = {}  # Store characters by name
    
    def create_character_from_vibe(self, vibe_description: str, player_preferences: Dict[str, Any]) -> Character:
        """
        Create a character based on "vibe coding" description
        Analyzes the vibe and creates a 5E compliant character
        """
        
        # Parse vibe description
        vibe_analysis = self._analyze_vibe(vibe_description)
        
        # Select race based on vibe
        race = self._select_race_from_vibe(vibe_analysis)
        
        # Select class based on vibe
        character_class = self._select_class_from_vibe(vibe_analysis)
        
        # Generate ability scores
        ability_scores = self._generate_ability_scores(character_class, race)
        
        # Generate name
        name = self._generate_character_name(race, vibe_analysis)
        
        # Create character
        character = Character(
            name=name,
            race=race,
            character_class=character_class,
            ability_scores=ability_scores
        )
        
        # Apply race and class features
        self._apply_race_features(character)
        self._apply_class_features(character)
        
        # Generate background and personality
        self._generate_background(character, vibe_analysis)
        self._generate_personality(character, vibe_analysis)
        
        # Apply custom flavor
        self._apply_custom_flavor(character, player_preferences)
        
        # Calculate derived stats
        self._calculate_derived_stats(character)
        
        return character
    
    def create_character_from_info(self, character_info: Dict[str, Any]) -> Character:
        """
        Create a character from parsed information
        """
        # Extract basic info
        name = character_info.get('name', 'Adventurer')
        race_name = character_info.get('race', 'human')
        class_name = character_info.get('character_class', 'fighter')
        level = character_info.get('level', 1)
        background = character_info.get('background', 'folk hero')
        personality_traits = character_info.get('personality_traits', ['brave'])
        
        # Convert string values to enums
        try:
            race = Race(race_name)
        except ValueError:
            race = Race.HUMAN  # Default fallback
        
        try:
            character_class = CharacterClass(class_name)
        except ValueError:
            character_class = CharacterClass.FIGHTER  # Default fallback
        
        # Generate ability scores based on class
        ability_scores = self._generate_ability_scores(character_class, race)
        
        # Create character
        character = Character(
            name=name,
            race=race,
            character_class=character_class,
            level=level,
            ability_scores=ability_scores,
            background=background,
            personality_traits=personality_traits
        )
        
        # Apply race and class features
        self._apply_race_features(character)
        self._apply_class_features(character)
        
        # Calculate derived stats
        self._calculate_derived_stats(character)
        
        return character
    
    def _analyze_vibe(self, vibe_description: str) -> Dict[str, Any]:
        """Analyze vibe description to extract character concepts"""
        vibe_lower = vibe_description.lower()
        
        analysis = {
            'combat_style': self._detect_combat_style(vibe_lower),
            'personality_type': self._detect_personality(vibe_lower),
            'magical_affinity': self._detect_magic_affinity(vibe_lower),
            'social_style': self._detect_social_style(vibe_lower),
            'background_hints': self._extract_background_hints(vibe_lower),
            'themes': self._extract_themes(vibe_lower)
        }
        
        return analysis
    
    def _detect_combat_style(self, vibe: str) -> str:
        """Detect preferred combat style from vibe"""
        if any(word in vibe for word in ['sword', 'weapon', 'fighter', 'warrior', 'battle']):
            return 'melee'
        elif any(word in vibe for word in ['bow', 'arrow', 'ranged', 'sniper', 'hunter']):
            return 'ranged'
        elif any(word in vibe for word in ['magic', 'spell', 'wizard', 'sorcerer', 'magical']):
            return 'magical'
        elif any(word in vibe for word in ['stealth', 'sneak', 'assassin', 'thief', 'rogue']):
            return 'stealth'
        else:
            return 'balanced'
    
    def _detect_personality(self, vibe: str) -> str:
        """Detect personality type from vibe"""
        if any(word in vibe for word in ['brave', 'bold', 'courageous', 'heroic']):
            return 'heroic'
        elif any(word in vibe for word in ['mysterious', 'dark', 'shadow', 'secretive']):
            return 'mysterious'
        elif any(word in vibe for word in ['wise', 'knowledge', 'scholar', 'learned']):
            return 'scholarly'
        elif any(word in vibe for word in ['wild', 'nature', 'primal', 'feral']):
            return 'primal'
        elif any(word in vibe for word in ['noble', 'honorable', 'chivalrous', 'knight']):
            return 'noble'
        else:
            return 'balanced'
    
    def _detect_magic_affinity(self, vibe: str) -> str:
        """Detect magic affinity from vibe"""
        if any(word in vibe for word in ['fire', 'flame', 'burning', 'inferno']):
            return 'fire'
        elif any(word in vibe for word in ['ice', 'frost', 'cold', 'winter']):
            return 'ice'
        elif any(word in vibe for word in ['nature', 'earth', 'plant', 'growth']):
            return 'nature'
        elif any(word in vibe for word in ['light', 'holy', 'divine', 'sacred']):
            return 'divine'
        elif any(word in vibe for word in ['shadow', 'dark', 'void', 'death']):
            return 'shadow'
        else:
            return 'general'
    
    def _detect_social_style(self, vibe: str) -> str:
        """Detect social style from vibe"""
        if any(word in vibe for word in ['leader', 'charismatic', 'inspiring', 'commanding']):
            return 'leader'
        elif any(word in vibe for word in ['lone', 'solitary', 'independent', 'reclusive']):
            return 'lone_wolf'
        elif any(word in vibe for word in ['friendly', 'social', 'outgoing', 'gregarious']):
            return 'social'
        elif any(word in vibe for word in ['mysterious', 'quiet', 'reserved', 'shy']):
            return 'reserved'
        else:
            return 'balanced'
    
    def _extract_background_hints(self, vibe: str) -> List[str]:
        """Extract background hints from vibe"""
        hints = []
        
        backgrounds = [
            'soldier', 'noble', 'sage', 'criminal', 'acolyte', 'folk_hero',
            'guild_artisan', 'hermit', 'outlander', 'urchin', 'entertainer'
        ]
        
        for background in backgrounds:
            if background.replace('_', ' ') in vibe:
                hints.append(background)
        
        return hints
    
    def _extract_themes(self, vibe: str) -> List[str]:
        """Extract thematic elements from vibe"""
        themes = []
        
        theme_keywords = {
            'nature': ['forest', 'wild', 'animal', 'plant', 'earth'],
            'mystery': ['secret', 'hidden', 'unknown', 'mysterious'],
            'power': ['strong', 'mighty', 'powerful', 'dominant'],
            'wisdom': ['wise', 'knowledge', 'learned', 'scholar'],
            'adventure': ['explorer', 'wanderer', 'traveler', 'journey'],
            'protection': ['guardian', 'protector', 'defender', 'shield']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in vibe for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _select_race_from_vibe(self, vibe_analysis: Dict[str, Any]) -> Race:
        """Select race based on vibe analysis"""
        race_vibe_mapping = {
            'heroic': [Race.HUMAN, Race.DRAGONBORN, Race.HALF_ORC],
            'mysterious': [Race.TIEFLING, Race.ELF, Race.HALF_ELF],
            'scholarly': [Race.ELF, Race.GNOME, Race.HUMAN],
            'primal': [Race.HALF_ORC, Race.DRAGONBORN, Race.HUMAN],
            'noble': [Race.ELF, Race.HUMAN, Race.HALF_ELF],
            'balanced': [Race.HUMAN, Race.HALF_ELF, Race.HALFLING]
        }
        
        personality = vibe_analysis.get('personality_type', 'balanced')
        available_races = race_vibe_mapping.get(personality, race_vibe_mapping['balanced'])
        
        return random.choice(available_races)
    
    def _select_class_from_vibe(self, vibe_analysis: Dict[str, Any]) -> CharacterClass:
        """Select class based on vibe analysis"""
        class_vibe_mapping = {
            'melee': [CharacterClass.FIGHTER, CharacterClass.BARBARIAN, CharacterClass.PALADIN],
            'ranged': [CharacterClass.RANGER, CharacterClass.ROGUE, CharacterClass.FIGHTER],
            'magical': [CharacterClass.WIZARD, CharacterClass.SORCERER, CharacterClass.WARLOCK],
            'stealth': [CharacterClass.ROGUE, CharacterClass.RANGER, CharacterClass.MONK],
            'balanced': [CharacterClass.FIGHTER, CharacterClass.CLERIC, CharacterClass.BARD]
        }
        
        combat_style = vibe_analysis.get('combat_style', 'balanced')
        available_classes = class_vibe_mapping.get(combat_style, class_vibe_mapping['balanced'])
        
        return random.choice(available_classes)
    
    def _generate_ability_scores(self, character_class: CharacterClass, race: Race) -> Dict[AbilityScore, int]:
        """Generate ability scores optimized for class and race"""
        # Standard array: 15, 14, 13, 12, 10, 8
        scores = [15, 14, 13, 12, 10, 8]
        random.shuffle(scores)
        
        ability_scores = {}
        
        # Assign scores based on class priority
        class_priorities = {
            CharacterClass.BARBARIAN: [AbilityScore.STRENGTH, AbilityScore.CONSTITUTION, AbilityScore.DEXTERITY],
            CharacterClass.BARD: [AbilityScore.CHARISMA, AbilityScore.DEXTERITY, AbilityScore.CONSTITUTION],
            CharacterClass.CLERIC: [AbilityScore.WISDOM, AbilityScore.CONSTITUTION, AbilityScore.STRENGTH],
            CharacterClass.DRUID: [AbilityScore.WISDOM, AbilityScore.CONSTITUTION, AbilityScore.DEXTERITY],
            CharacterClass.FIGHTER: [AbilityScore.STRENGTH, AbilityScore.CONSTITUTION, AbilityScore.DEXTERITY],
            CharacterClass.MONK: [AbilityScore.DEXTERITY, AbilityScore.WISDOM, AbilityScore.CONSTITUTION],
            CharacterClass.PALADIN: [AbilityScore.STRENGTH, AbilityScore.CHARISMA, AbilityScore.CONSTITUTION],
            CharacterClass.RANGER: [AbilityScore.DEXTERITY, AbilityScore.WISDOM, AbilityScore.CONSTITUTION],
            CharacterClass.ROGUE: [AbilityScore.DEXTERITY, AbilityScore.INTELLIGENCE, AbilityScore.CONSTITUTION],
            CharacterClass.SORCERER: [AbilityScore.CHARISMA, AbilityScore.CONSTITUTION, AbilityScore.DEXTERITY],
            CharacterClass.WARLOCK: [AbilityScore.CHARISMA, AbilityScore.CONSTITUTION, AbilityScore.DEXTERITY],
            CharacterClass.WIZARD: [AbilityScore.INTELLIGENCE, AbilityScore.CONSTITUTION, AbilityScore.DEXTERITY]
        }
        
        priorities = class_priorities.get(character_class, [AbilityScore.STRENGTH, AbilityScore.DEXTERITY, AbilityScore.CONSTITUTION])
        
        # Assign high scores to priority abilities
        for i, ability in enumerate(priorities):
            ability_scores[ability] = scores[i]
        
        # Assign remaining scores
        remaining_abilities = [a for a in AbilityScore if a not in priorities]
        remaining_scores = scores[len(priorities):]
        
        for ability, score in zip(remaining_abilities, remaining_scores):
            ability_scores[ability] = score
        
        # Apply race bonuses
        race_bonuses = self.races_data.get(race.value, {}).get('ability_bonuses', {})
        for ability, bonus in race_bonuses.items():
            if ability in ability_scores:
                ability_scores[ability] += bonus
        
        return ability_scores
    
    def _generate_character_name(self, race: Race, vibe_analysis: Dict[str, Any]) -> str:
        """Generate character name based on race and vibe"""
        # This would ideally use a more sophisticated name generator
        # For now, using simple templates
        name_templates = {
            Race.HUMAN: ["{first} {last}", "{first} the {title}"],
            Race.ELF: ["{first} {last}", "{first} of the {place}"],
            Race.DWARF: ["{first} {last}", "{first} {clan}"],
            Race.HALFLING: ["{first} {last}", "{first} {nickname}"],
            Race.GNOME: ["{first} {last}", "{first} the {adjective}"],
            Race.DRAGONBORN: ["{first} {last}", "{first} {clan}"],
            Race.TIEFLING: ["{first} {last}", "{first} the {title}"],
            Race.HALF_ELF: ["{first} {last}", "{first} of {heritage}"],
            Race.HALF_ORC: ["{first} {last}", "{first} {clan}"]
        }
        
        template = random.choice(name_templates.get(race, name_templates[Race.HUMAN]))
        
        # Generate name components based on race and vibe
        first_names = self._get_race_first_names(race)
        last_names = self._get_race_last_names(race)
        
        name_data = {
            'first': random.choice(first_names),
            'last': random.choice(last_names),
            'title': self._generate_title(vibe_analysis),
            'place': self._generate_place_name(),
            'clan': self._generate_clan_name(race),
            'nickname': self._generate_nickname(vibe_analysis),
            'adjective': self._generate_adjective(vibe_analysis),
            'heritage': self._generate_heritage()
        }
        
        return template.format(**name_data)
    
    def _get_race_first_names(self, race: Race) -> List[str]:
        """Get first names for a race"""
        race_names = {
            Race.HUMAN: ['Aldric', 'Branwen', 'Cedric', 'Dwyn', 'Eira', 'Faelan'],
            Race.ELF: ['Aelar', 'Baelor', 'Caelan', 'Daelin', 'Elenwe', 'Faelar'],
            Race.DWARF: ['Balin', 'Dwalin', 'Gimli', 'Thorin', 'Bifur', 'Bofur'],
            Race.HALFLING: ['Bilbo', 'Frodo', 'Samwise', 'Pippin', 'Merry', 'Rosie'],
            Race.GNOME: ['Alston', 'Boddynock', 'Brocc', 'Burgell', 'Dimble', 'Eldon'],
            Race.DRAGONBORN: ['Arjhan', 'Balasar', 'Bharash', 'Donaar', 'Ghesh', 'Heskan'],
            Race.TIEFLING: ['Akmenos', 'Amnon', 'Barakas', 'Damakos', 'Ekemon', 'Iados'],
            Race.HALF_ELF: ['Adran', 'Aelar', 'Aramil', 'Arannis', 'Aust', 'Beiro'],
            Race.HALF_ORC: ['Dench', 'Feng', 'Gell', 'Henk', 'Holg', 'Imsh']
        }
        
        return race_names.get(race, ['Unknown'])
    
    def _get_race_last_names(self, race: Race) -> List[str]:
        """Get last names for a race"""
        race_names = {
            Race.HUMAN: ['Blackwood', 'Stormwind', 'Ironheart', 'Silverleaf'],
            Race.ELF: ['Amakiir', 'Amastacia', 'Galanodel', 'Holimion'],
            Race.DWARF: ['Balderk', 'Battlehammer', 'Brawnanvil', 'Dankil'],
            Race.HALFLING: ['Brushgather', 'Goodbarrel', 'Greenbottle', 'High-hill'],
            Race.GNOME: ['Beren', 'Daergel', 'Folkor', 'Garrick', 'Nackle'],
            Race.DRAGONBORN: ['Clethtinthiallor', 'Daardendrian', 'Delmirev', 'Drachedandion'],
            Race.TIEFLING: ['Crius', 'Kaen', 'Mordai', 'Naeth', 'Oriax', 'Shakos'],
            Race.HALF_ELF: ['Amakiir', 'Galanodel', 'Holimion', 'Liadon', 'Siannodel'],
            Race.HALF_ORC: ['Dankil', 'Guhm', 'Henk', 'Lum', 'Ronk', 'Susk']
        }
        
        return race_names.get(race, ['Unknown'])
    
    def _generate_title(self, vibe_analysis: Dict[str, Any]) -> str:
        """Generate title based on vibe"""
        titles = {
            'heroic': ['the Brave', 'the Valiant', 'the Hero', 'the Champion'],
            'mysterious': ['the Shadow', 'the Unknown', 'the Mysterious', 'the Enigma'],
            'scholarly': ['the Wise', 'the Learned', 'the Scholar', 'the Sage'],
            'primal': ['the Wild', 'the Feral', 'the Primal', 'the Untamed'],
            'noble': ['the Noble', 'the Honorable', 'the Just', 'the Righteous']
        }
        
        personality = vibe_analysis.get('personality_type', 'balanced')
        available_titles = titles.get(personality, ['the Adventurer'])
        
        return random.choice(available_titles)
    
    def _generate_place_name(self) -> str:
        """Generate a place name"""
        places = ['Mystwood', 'Stormhaven', 'Ironforge', 'Silvermoon', 'Shadowfell']
        return random.choice(places)
    
    def _generate_clan_name(self, race: Race) -> str:
        """Generate clan name for race"""
        clan_templates = {
            Race.DWARF: ['Iron', 'Stone', 'Gold', 'Silver', 'Bronze'],
            Race.DRAGONBORN: ['Fire', 'Storm', 'Iron', 'Gold', 'Silver'],
            Race.HALF_ORC: ['Blood', 'Iron', 'Stone', 'Wolf', 'Bear']
        }
        
        if race in clan_templates:
            prefix = random.choice(clan_templates[race])
            suffixes = ['fist', 'heart', 'claw', 'fang', 'hide']
            suffix = random.choice(suffixes)
            return f"{prefix}{suffix}"
        
        return "Unknown"
    
    def _generate_nickname(self, vibe_analysis: Dict[str, Any]) -> str:
        """Generate nickname based on vibe"""
        nicknames = {
            'heroic': ['Braveheart', 'Lionheart', 'Ironwill', 'Stormbringer'],
            'mysterious': ['Shadow', 'Ghost', 'Raven', 'Whisper'],
            'scholarly': ['Sage', 'Wise', 'Scholar', 'Thinker'],
            'primal': ['Wild', 'Feral', 'Beast', 'Hunter'],
            'noble': ['Noble', 'Just', 'Honorable', 'Righteous']
        }
        
        personality = vibe_analysis.get('personality_type', 'balanced')
        available_nicknames = nicknames.get(personality, ['Adventurer'])
        
        return random.choice(available_nicknames)
    
    def _generate_adjective(self, vibe_analysis: Dict[str, Any]) -> str:
        """Generate adjective based on vibe"""
        adjectives = {
            'heroic': ['Brave', 'Valiant', 'Courageous', 'Bold'],
            'mysterious': ['Mysterious', 'Enigmatic', 'Cryptic', 'Obscure'],
            'scholarly': ['Wise', 'Learned', 'Intelligent', 'Knowledgeable'],
            'primal': ['Wild', 'Feral', 'Untamed', 'Natural'],
            'noble': ['Noble', 'Honorable', 'Just', 'Righteous']
        }
        
        personality = vibe_analysis.get('personality_type', 'balanced')
        available_adjectives = adjectives.get(personality, ['Adventurous'])
        
        return random.choice(available_adjectives)
    
    def _generate_heritage(self) -> str:
        """Generate heritage for half-elf"""
        heritages = ['Elven Kingdom', 'Human City', 'Mixed Heritage', 'Unknown Origins']
        return random.choice(heritages)
    
    def _apply_race_features(self, character: Character):
        """Apply race-specific features to character"""
        race_data = self.races_data.get(character.race.value, {})
        
        # Apply racial traits
        if 'traits' in race_data:
            character.features.extend(race_data['traits'])
        
        # Apply racial proficiencies
        if 'proficiencies' in race_data:
            character.proficiencies.extend(race_data['proficiencies'])
    
    def _apply_class_features(self, character: Character):
        """Apply class-specific features to character"""
        class_data = self.classes_data.get(character.character_class.value, {})
        
        # Apply class features
        if 'features' in class_data:
            character.features.extend(class_data['features'])
        
        # Apply class proficiencies
        if 'proficiencies' in class_data:
            character.proficiencies.extend(class_data['proficiencies'])
        
        # Apply starting equipment
        if 'starting_equipment' in class_data:
            character.equipment.extend(class_data['starting_equipment'])
    
    def _generate_background(self, character: Character, vibe_analysis: Dict[str, Any]):
        """Generate background based on vibe"""
        background_hints = vibe_analysis.get('background_hints', [])
        
        if background_hints:
            background_name = random.choice(background_hints)
        else:
            # Select background based on personality
            background_mapping = {
                'heroic': ['folk_hero', 'soldier'],
                'mysterious': ['criminal', 'hermit'],
                'scholarly': ['sage', 'acolyte'],
                'noble': ['noble', 'guild_artisan'],
                'primal': ['outlander', 'hermit']
            }
            
            personality = vibe_analysis.get('personality_type', 'balanced')
            available_backgrounds = background_mapping.get(personality, ['folk_hero'])
            background_name = random.choice(available_backgrounds)
        
        background_data = self.backgrounds_data.get(background_name, {})
        character.background = background_name
        
        # Apply background features
        if 'features' in background_data:
            character.features.extend(background_data['features'])
        
        # Apply background proficiencies
        if 'proficiencies' in background_data:
            character.proficiencies.extend(background_data['proficiencies'])
    
    def _generate_personality(self, character: Character, vibe_analysis: Dict[str, Any]):
        """Generate personality traits based on vibe"""
        personality_type = vibe_analysis.get('personality_type', 'balanced')
        
        # Generate personality traits
        trait_options = {
            'heroic': ['I face problems head-on. A simple, direct solution is the best path to success.', 'I protect those who cannot protect themselves.'],
            'mysterious': ['I am quiet around strangers, but I am not shy.', 'I keep my thoughts and observations to myself.'],
            'scholarly': ['I use polysyllabic words that convey the impression of great erudition.', 'I\'ve read every book in the world\'s greatest libraries.'],
            'primal': ['I feel far more comfortable around animals than people.', 'I place no stock in wealthy or well-mannered folk.'],
            'noble': ['I am always polite and respectful.', 'I am a snob who looks down on those who can\'t appreciate fine art.']
        }
        
        available_traits = trait_options.get(personality_type, trait_options['heroic'])
        character.personality_traits = random.sample(available_traits, min(2, len(available_traits)))
    
    def _apply_custom_flavor(self, character: Character, player_preferences: Dict[str, Any]):
        """Apply custom flavor based on player preferences"""
        if 'custom_description' in player_preferences:
            character.custom_flavor['description'] = player_preferences['custom_description']
        
        if 'special_abilities' in player_preferences:
            character.custom_flavor['special_abilities'] = player_preferences['special_abilities']
        
        if 'unique_features' in player_preferences:
            character.custom_flavor['unique_features'] = player_preferences['unique_features']
    
    def _calculate_derived_stats(self, character: Character):
        """Calculate derived statistics"""
        # Calculate hit points
        con_modifier = (character.ability_scores[AbilityScore.CONSTITUTION] - 10) // 2
        class_hp = self.classes_data.get(character.character_class.value, {}).get('hit_die', 8)
        character.hit_points = class_hp + con_modifier
        
        # Calculate armor class
        dex_modifier = (character.ability_scores[AbilityScore.DEXTERITY] - 10) // 2
        character.armor_class = 10 + dex_modifier
    
    def _load_races_data(self) -> Dict[str, Any]:
        """Load race data from JSON"""
        # This would load from a JSON file
        # For now, returning basic structure
        return {
            'human': {
                'ability_bonuses': {'strength': 1, 'dexterity': 1, 'constitution': 1, 'intelligence': 1, 'wisdom': 1, 'charisma': 1},
                'traits': ['Extra Language'],
                'proficiencies': []
            },
            'elf': {
                'ability_bonuses': {'dexterity': 2},
                'traits': ['Darkvision', 'Keen Senses', 'Fey Ancestry', 'Trance'],
                'proficiencies': ['Perception']
            }
            # Add more races as needed
        }
    
    def _load_classes_data(self) -> Dict[str, Any]:
        """Load class data from JSON"""
        return {
            'fighter': {
                'hit_die': 10,
                'features': ['Fighting Style', 'Second Wind'],
                'proficiencies': ['All armor', 'Shields', 'Simple weapons', 'Martial weapons'],
                'starting_equipment': ['Chain mail', 'Martial weapon', 'Shield', 'Crossbow', '20 bolts']
            },
            'wizard': {
                'hit_die': 6,
                'features': ['Spellcasting', 'Arcane Recovery'],
                'proficiencies': ['Daggers', 'Quarterstaffs', 'Light crossbows'],
                'starting_equipment': ['Spellbook', 'Arcane focus', 'Scholar\'s pack', 'Writing kit']
            }
            # Add more classes as needed
        }
    
    def _load_backgrounds_data(self) -> Dict[str, Any]:
        """Load background data from JSON"""
        return {
            'folk_hero': {
                'features': ['Rustic Hospitality'],
                'proficiencies': ['Animal Handling', 'Survival']
            },
            'sage': {
                'features': ['Researcher'],
                'proficiencies': ['Arcana', 'History']
            }
            # Add more backgrounds as needed
        }
    
    def _load_spells_data(self) -> Dict[str, Any]:
        """Load spells data from JSON"""
        return {
            'fireball': {
                'level': 3,
                'school': 'evocation',
                'casting_time': '1 action',
                'range': '150 feet',
                'components': ['V', 'S', 'M'],
                'duration': 'Instantaneous'
            }
            # Add more spells as needed
        }

    def get_character(self, name: str) -> Optional[Character]:
        """Get a character by name."""
        return self.characters.get(name)

    def add_character(self, character: Character):
        """Add a character to the manager."""
        self.characters[character.name] = character

    def get_all_characters(self) -> List[Character]:
        """Get all characters in the manager."""
        return list(self.characters.values()) 