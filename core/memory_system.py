"""
AI-Powered DnD 5E Campaign Memory System
========================================

This system reads and understands session logs the way AI assistants read code:
- Analyzes entire context simultaneously
- Extracts relationships and patterns
- Builds comprehensive mental models
- Maintains perfect continuity across sessions
- Understands implicit connections and context
- Uses semantic analysis and categorization
"""

import json
import sqlite3
import os
import re
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
import spacy

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')

class EntityType(Enum):
    """Types of entities that can be tracked in the campaign"""
    NPC = "npc"
    LOCATION = "location"
    ITEM = "item"
    EVENT = "event"
    RELATIONSHIP = "relationship"
    QUEST = "quest"
    FACT = "fact"
    CHARACTER = "character"
    ORGANIZATION = "organization"
    CREATURE = "creature"
    SPELL = "spell"
    ABILITY = "ability"

class SemanticCategory(Enum):
    """Semantic categories for better understanding"""
    COMBAT = "combat"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    MAGIC = "magic"
    ECONOMIC = "economic"
    POLITICAL = "political"
    RELIGIOUS = "religious"
    PERSONAL = "personal"
    ENVIRONMENTAL = "environmental"

class ContextLevel(Enum):
    """Context levels for understanding importance"""
    CRITICAL = "critical"      # Essential for campaign continuity
    IMPORTANT = "important"    # Significant but not critical
    MODERATE = "moderate"      # Useful background information
    MINOR = "minor"           # Flavor text, less important

@dataclass
class SemanticTag:
    """Semantic tag for categorization"""
    category: SemanticCategory
    confidence: float
    context: str
    keywords: List[str]

@dataclass
class ContextualReference:
    """Reference to another entity with context"""
    entity_id: str
    relationship_type: str
    context: str
    strength: float  # 0.0 to 1.0
    timestamp: datetime

@dataclass
class CampaignEntity:
    """Represents any entity in the campaign with full context"""
    id: str
    name: str
    entity_type: EntityType
    description: str
    attributes: Dict[str, Any]
    relationships: Dict[str, List[str]]  # entity_id -> relationship_type
    first_mentioned: str  # session_id
    last_updated: str  # session_id
    confidence: float  # 0.0 to 1.0, how certain we are about this entity
    context_snippets: List[str]  # Key quotes/mentions from sessions
    semantic_tags: List[SemanticTag]  # Categorization tags
    context_level: ContextLevel  # Importance level
    aliases: List[str]  # Alternative names/descriptions
    core_attributes: Dict[str, Any]  # Essential, unchanging attributes
    variable_attributes: Dict[str, Any]  # Attributes that can change
    references: List[ContextualReference]  # References to other entities
    
    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()
        if self.semantic_tags is None:
            self.semantic_tags = []
        if self.aliases is None:
            self.aliases = []
        if self.core_attributes is None:
            self.core_attributes = {}
        if self.variable_attributes is None:
            self.variable_attributes = {}
        if self.references is None:
            self.references = []
    
    def _generate_id(self) -> str:
        """Generate unique ID based on name and type"""
        content = f"{self.name}_{self.entity_type.value}_{self.first_mentioned}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

@dataclass
class SessionLog:
    """Represents a complete session with parsed information"""
    session_id: str
    timestamp: datetime
    raw_text: str
    parsed_entities: List[CampaignEntity]
    key_events: List[Dict[str, Any]]
    player_actions: List[str]
    dm_responses: List[str]
    session_summary: str
    continuity_checks: List[str]
    semantic_analysis: Dict[str, Any]  # Overall session categorization
    context_map: Dict[str, Any]  # Context relationships within session

@dataclass
class ParsedSegment:
    """A parsed segment of text with semantic understanding"""
    text: str
    entity_mentions: List[str]
    semantic_category: SemanticCategory
    context_level: ContextLevel
    relationships: List[Dict[str, str]]
    confidence: float

class CampaignMemorySystem:
    """
    Advanced memory system that reads session logs like AI reads code:
    - Simultaneous context analysis
    - Relationship extraction
    - Pattern recognition
    - Continuity verification
    - Semantic understanding
    - Context-aware categorization
    """
    
    def __init__(self, campaign_id: str, db_path: str = "data/campaigns/campaign_memory.db"):
        self.campaign_id = campaign_id
        self.db_path = db_path
        self.entities: Dict[str, CampaignEntity] = {}
        self.sessions: Dict[str, SessionLog] = {}
        self.relationship_graph: Dict[str, Set[str]] = defaultdict(set)
        self.fact_index: Dict[str, List[str]] = defaultdict(list)  # fact -> entity_ids
        self.context_cache: Dict[str, Any] = {}
        self.semantic_index: Dict[SemanticCategory, List[str]] = defaultdict(list)
        
        # Initialize NLP components
        self._init_nlp()
        self._init_database()
        self._load_existing_data()
    
    def _init_nlp(self):
        """Initialize NLP components for semantic analysis"""
        # Load spaCy model for better entity recognition
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If spaCy model not available, use basic NLTK
            self.nlp = None
            print("Warning: spaCy model not available. Using basic NLTK for entity recognition.")
    
    def _init_database(self):
        """Initialize the database with enhanced schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Enhanced entities table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    campaign_id TEXT,
                    name TEXT,
                    entity_type TEXT,
                    description TEXT,
                    attributes TEXT,
                    relationships TEXT,
                    first_mentioned TEXT,
                    last_updated TEXT,
                    confidence REAL,
                    context_snippets TEXT,
                    semantic_tags TEXT,
                    context_level TEXT,
                    aliases TEXT,
                    core_attributes TEXT,
                    variable_attributes TEXT,
                    references TEXT
                )
            """)
            
            # Enhanced sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    campaign_id TEXT,
                    timestamp TEXT,
                    raw_text TEXT,
                    parsed_entities TEXT,
                    key_events TEXT,
                    player_actions TEXT,
                    dm_responses TEXT,
                    session_summary TEXT,
                    continuity_checks TEXT,
                    semantic_analysis TEXT,
                    context_map TEXT
                )
            """)
            
            # Enhanced relationships table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    entity1_id TEXT,
                    entity2_id TEXT,
                    relationship_type TEXT,
                    strength REAL,
                    context TEXT,
                    semantic_category TEXT,
                    timestamp TEXT,
                    PRIMARY KEY (entity1_id, entity2_id, relationship_type)
                )
            """)
            
            # Enhanced facts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    fact_id TEXT PRIMARY KEY,
                    campaign_id TEXT,
                    fact_text TEXT,
                    entity_ids TEXT,
                    confidence REAL,
                    source_session TEXT,
                    timestamp TEXT,
                    semantic_category TEXT,
                    context_level TEXT
                )
            """)
            
            # New semantic index table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS semantic_index (
                    category TEXT,
                    entity_id TEXT,
                    confidence REAL,
                    context TEXT,
                    PRIMARY KEY (category, entity_id)
                )
            """)
    
    def process_session_log(self, session_id: str, raw_text: str) -> SessionLog:
        """
        Process a new session log using AI-like reading approach:
        1. Simultaneous analysis of entire text
        2. Entity extraction and relationship mapping
        3. Context understanding and pattern recognition
        4. Continuity verification with existing knowledge
        5. Semantic categorization and tagging
        """
        
        # Step 1: Simultaneous analysis of entire text
        analysis = self._analyze_session_simultaneously(raw_text)
        
        # Step 2: Extract entities with semantic understanding
        entities = self._extract_entities_with_semantics(raw_text, session_id, analysis)
        
        # Step 3: Build relationship graph
        self._build_enhanced_relationship_graph(entities, analysis)
        
        # Step 4: Verify continuity
        continuity_checks = self._verify_enhanced_continuity(entities, session_id)
        
        # Step 5: Generate semantic analysis
        semantic_analysis = self._generate_semantic_analysis(raw_text, entities, analysis)
        
        # Step 6: Create context map
        context_map = self._create_context_map(entities, analysis)
        
        # Create session log
        session = SessionLog(
            session_id=session_id,
            timestamp=datetime.now(),
            raw_text=raw_text,
            parsed_entities=entities,
            key_events=analysis.get('key_events', []),
            player_actions=analysis.get('player_actions', []),
            dm_responses=analysis.get('dm_responses', []),
            session_summary=self._generate_enhanced_summary(raw_text, entities, analysis),
            continuity_checks=continuity_checks,
            semantic_analysis=semantic_analysis,
            context_map=context_map
        )
        
        # Update entities and save
        self._update_entities_enhanced(entities, session_id)
        self._save_session_to_database_enhanced(session)
        
        return session
    
    def _analyze_session_simultaneously(self, raw_text: str) -> Dict[str, Any]:
        """
        Analyze entire session text simultaneously, like AI reading code
        """
        # Tokenize and parse
        sentences = sent_tokenize(raw_text)
        words = word_tokenize(raw_text)
        
        # POS tagging for better understanding
        pos_tags = pos_tag(words)
        
        # Named entity recognition
        if self.nlp:
            doc = self.nlp(raw_text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
        else:
            # Basic NLTK named entity recognition
            entities = []
            ne_tree = ne_chunk(pos_tags)
            for subtree in ne_tree:
                if hasattr(subtree, 'label'):
                    entities.append((' '.join([leaf[0] for leaf in subtree.leaves()]), subtree.label()))
        
        # Semantic analysis
        semantic_categories = self._categorize_text_semantically(raw_text)
        
        # Context level analysis
        context_levels = self._analyze_context_levels(raw_text)
        
        # Extract key information
        key_events = self._extract_key_events_enhanced(raw_text)
        player_actions = self._extract_player_actions_enhanced(raw_text)
        dm_responses = self._extract_dm_responses_enhanced(raw_text)
        
        return {
            'sentences': sentences,
            'words': words,
            'pos_tags': pos_tags,
            'entities': entities,
            'semantic_categories': semantic_categories,
            'context_levels': context_levels,
            'key_events': key_events,
            'player_actions': player_actions,
            'dm_responses': dm_responses
        }
    
    def _categorize_text_semantically(self, text: str) -> List[SemanticTag]:
        """Categorize text into semantic categories"""
        text_lower = text.lower()
        categories = []
        
        # Combat category
        combat_keywords = ['attack', 'fight', 'battle', 'combat', 'weapon', 'damage', 'hp', 'initiative']
        if any(keyword in text_lower for keyword in combat_keywords):
            confidence = sum(1 for keyword in combat_keywords if keyword in text_lower) / len(combat_keywords)
            categories.append(SemanticTag(
                category=SemanticCategory.COMBAT,
                confidence=min(confidence, 1.0),
                context="Combat-related content detected",
                keywords=[kw for kw in combat_keywords if kw in text_lower]
            ))
        
        # Social category
        social_keywords = ['talk', 'conversation', 'dialogue', 'speak', 'persuade', 'intimidate', 'deception']
        if any(keyword in text_lower for keyword in social_keywords):
            confidence = sum(1 for keyword in social_keywords if keyword in text_lower) / len(social_keywords)
            categories.append(SemanticTag(
                category=SemanticCategory.SOCIAL,
                confidence=min(confidence, 1.0),
                context="Social interaction content detected",
                keywords=[kw for kw in social_keywords if kw in text_lower]
            ))
        
        # Magic category
        magic_keywords = ['spell', 'magic', 'cast', 'wizard', 'sorcerer', 'magical', 'enchantment']
        if any(keyword in text_lower for keyword in magic_keywords):
            confidence = sum(1 for keyword in magic_keywords if keyword in text_lower) / len(magic_keywords)
            categories.append(SemanticTag(
                category=SemanticCategory.MAGIC,
                confidence=min(confidence, 1.0),
                context="Magic-related content detected",
                keywords=[kw for kw in magic_keywords if kw in text_lower]
            ))
        
        # Exploration category
        exploration_keywords = ['explore', 'search', 'investigate', 'travel', 'journey', 'discover']
        if any(keyword in text_lower for keyword in exploration_keywords):
            confidence = sum(1 for keyword in exploration_keywords if keyword in text_lower) / len(exploration_keywords)
            categories.append(SemanticTag(
                category=SemanticCategory.EXPLORATION,
                confidence=min(confidence, 1.0),
                context="Exploration content detected",
                keywords=[kw for kw in exploration_keywords if kw in text_lower]
            ))
        
        return categories
    
    def _analyze_context_levels(self, text: str) -> List[ContextLevel]:
        """Analyze the context level (importance) of different parts of text"""
        context_levels = []
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Critical indicators
            critical_keywords = ['death', 'kill', 'destroy', 'save', 'critical', 'essential', 'must', 'vital']
            if any(keyword in sentence_lower for keyword in critical_keywords):
                context_levels.append(ContextLevel.CRITICAL)
                continue
            
            # Important indicators
            important_keywords = ['quest', 'mission', 'goal', 'objective', 'key', 'main', 'primary']
            if any(keyword in sentence_lower for keyword in important_keywords):
                context_levels.append(ContextLevel.IMPORTANT)
                continue
            
            # Moderate indicators
            moderate_keywords = ['help', 'assist', 'support', 'guide', 'inform', 'tell']
            if any(keyword in sentence_lower for keyword in moderate_keywords):
                context_levels.append(ContextLevel.MODERATE)
                continue
            
            # Default to minor
            context_levels.append(ContextLevel.MINOR)
        
        return context_levels
    
    def _extract_entities_with_semantics(self, text: str, session_id: str, analysis: Dict[str, Any]) -> List[CampaignEntity]:
        """Extract entities with enhanced semantic understanding"""
        entities = []
        
        # Extract named entities using NLP
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                # Map spaCy entity types to our types
                entity_type = self._map_spacy_entity_type(ent.label_)
                
                # Create entity with semantic understanding
                entity = CampaignEntity(
                    id="",
                    name=ent.text,
                    entity_type=entity_type,
                    description=f"Detected {entity_type.value}: {ent.text}",
                    attributes={},
                    relationships={},
                    first_mentioned=session_id,
                    last_updated=session_id,
                    confidence=0.8,  # High confidence for NLP-detected entities
                    context_snippets=[ent.text],
                    semantic_tags=self._get_semantic_tags_for_entity(ent.text, text),
                    context_level=self._determine_entity_context_level(ent.text, text),
                    aliases=[],
                    core_attributes={},
                    variable_attributes={},
                    references=[]
                )
                entities.append(entity)
        
        # Extract additional entities using pattern matching
        additional_entities = self._extract_entities_by_patterns(text, session_id)
        entities.extend(additional_entities)
        
        return entities
    
    def _map_spacy_entity_type(self, spacy_label: str) -> EntityType:
        """Map spaCy entity labels to our entity types"""
        mapping = {
            'PERSON': EntityType.NPC,
            'ORG': EntityType.ORGANIZATION,
            'GPE': EntityType.LOCATION,
            'LOC': EntityType.LOCATION,
            'FAC': EntityType.LOCATION,
            'PRODUCT': EntityType.ITEM,
            'EVENT': EntityType.EVENT,
            'WORK_OF_ART': EntityType.ITEM,
            'LAW': EntityType.FACT,
            'LANGUAGE': EntityType.FACT
        }
        return mapping.get(spacy_label, EntityType.FACT)
    
    def _get_semantic_tags_for_entity(self, entity_name: str, context: str) -> List[SemanticTag]:
        """Get semantic tags for a specific entity"""
        tags = []
        
        # Analyze context around entity mention
        entity_lower = entity_name.lower()
        context_lower = context.lower()
        
        # Check for combat context
        if any(word in context_lower for word in ['attack', 'fight', 'battle', 'enemy']):
            tags.append(SemanticTag(
                category=SemanticCategory.COMBAT,
                confidence=0.7,
                context=f"{entity_name} mentioned in combat context",
                keywords=['combat', 'battle', 'fight']
            ))
        
        # Check for social context
        if any(word in context_lower for word in ['talk', 'speak', 'conversation', 'dialogue']):
            tags.append(SemanticTag(
                category=SemanticCategory.SOCIAL,
                confidence=0.7,
                context=f"{entity_name} mentioned in social context",
                keywords=['social', 'conversation', 'dialogue']
            ))
        
        return tags
    
    def _determine_entity_context_level(self, entity_name: str, context: str) -> ContextLevel:
        """Determine the context level (importance) of an entity"""
        context_lower = context.lower()
        entity_lower = entity_name.lower()
        
        # Critical indicators
        critical_indicators = ['boss', 'final', 'main villain', 'key', 'essential', 'vital']
        if any(indicator in context_lower for indicator in critical_indicators):
            return ContextLevel.CRITICAL
        
        # Important indicators
        important_indicators = ['quest', 'mission', 'objective', 'goal', 'primary']
        if any(indicator in context_lower for indicator in important_indicators):
            return ContextLevel.IMPORTANT
        
        # Moderate indicators
        moderate_indicators = ['help', 'assist', 'guide', 'inform']
        if any(indicator in context_lower for indicator in moderate_indicators):
            return ContextLevel.MODERATE
        
        return ContextLevel.MINOR
    
    def _extract_entities_by_patterns(self, text: str, session_id: str) -> List[CampaignEntity]:
        """Extract entities using pattern matching for DnD-specific content"""
        entities = []
        
        # Extract NPCs (proper nouns followed by titles or descriptions)
        npc_patterns = [
            r'\b([A-Z][a-z]+ [A-Z][a-z]+)\s+(?:the|a|an)\s+([a-z\s]+)',
            r'\b([A-Z][a-z]+)\s+(?:says|asks|tells|shouts|whispers)',
            r'\b([A-Z][a-z]+)\s+(?:merchant|guard|noble|wizard|priest|rogue)'
        ]
        
        for pattern in npc_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1)
                description = match.group(2) if len(match.groups()) > 1 else "NPC"
                
                entity = CampaignEntity(
                    id="",
                    name=name,
                    entity_type=EntityType.NPC,
                    description=description,
                    attributes={},
                    relationships={},
                    first_mentioned=session_id,
                    last_updated=session_id,
                    confidence=0.6,
                    context_snippets=[match.group(0)],
                    semantic_tags=[],
                    context_level=ContextLevel.MODERATE,
                    aliases=[],
                    core_attributes={},
                    variable_attributes={},
                    references=[]
                )
                entities.append(entity)
        
        # Extract locations
        location_patterns = [
            r'\b([A-Z][a-z]+)\s+(?:tavern|inn|shop|temple|castle|tower|cave|forest|mountain)',
            r'\b(?:in|at|to|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\b([A-Z][a-z]+)\s+(?:village|town|city|kingdom|empire)'
        ]
        
        for pattern in location_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1)
                
                entity = CampaignEntity(
                    id="",
                    name=name,
                    entity_type=EntityType.LOCATION,
                    description=f"Location: {name}",
                    attributes={},
                    relationships={},
                    first_mentioned=session_id,
                    last_updated=session_id,
                    confidence=0.6,
                    context_snippets=[match.group(0)],
                    semantic_tags=[],
                    context_level=ContextLevel.MODERATE,
                    aliases=[],
                    core_attributes={},
                    variable_attributes={},
                    references=[]
                )
                entities.append(entity)
        
        return entities
    
    def _build_enhanced_relationship_graph(self, entities: List[CampaignEntity], analysis: Dict[str, Any]):
        """Build enhanced relationship graph with semantic understanding"""
        for entity in entities:
            # Find relationships in the text
            relationships = self._extract_relationships_for_entity(entity, analysis)
            
            for rel in relationships:
                target_entity = self._find_entity_by_name(rel['target'])
                if target_entity:
                    # Add bidirectional relationship
                    if entity.id not in target_entity.relationships:
                        target_entity.relationships[entity.id] = []
                    target_entity.relationships[entity.id].append(rel['type'])
                    
                    if target_entity.id not in entity.relationships:
                        entity.relationships[target_entity.id] = []
                    entity.relationships[target_entity.id].append(rel['type'])
    
    def _extract_relationships_for_entity(self, entity: CampaignEntity, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract relationships for a specific entity"""
        relationships = []
        entity_name = entity.name
        
        # Look for relationship patterns in the text
        relationship_patterns = [
            (r'\b' + re.escape(entity_name) + r'\s+(?:is|was|has|owns|leads|commands|serves|works for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 'is_a'),
            (r'\b' + re.escape(entity_name) + r'\s+(?:lives in|resides in|comes from|travels to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 'location'),
            (r'\b' + re.escape(entity_name) + r'\s+(?:wields|carries|owns|uses)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 'possesses'),
            (r'\b' + re.escape(entity_name) + r'\s+(?:fights|battles|attacks|defends against)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 'opposes'),
            (r'\b' + re.escape(entity_name) + r'\s+(?:helps|assists|supports|works with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 'allies')
        ]
        
        for pattern, rel_type in relationship_patterns:
            matches = re.finditer(pattern, analysis.get('raw_text', ''), re.IGNORECASE)
            for match in matches:
                target = match.group(1)
                relationships.append({
                    'target': target,
                    'type': rel_type,
                    'context': match.group(0)
                })
        
        return relationships
    
    def _verify_enhanced_continuity(self, new_entities: List[CampaignEntity], session_id: str) -> List[str]:
        """Verify continuity with enhanced semantic understanding"""
        continuity_checks = []
        
        for entity in new_entities:
            # Check if entity already exists
            existing_entity = self._find_entity_by_name(entity.name)
            
            if existing_entity:
                # Check for inconsistencies
                inconsistencies = self._check_entity_consistency(existing_entity, entity)
                if inconsistencies:
                    continuity_checks.extend(inconsistencies)
                
                # Update existing entity
                self._merge_entity_information(existing_entity, entity, session_id)
            else:
                # New entity, add to memory
                self.entities[entity.id] = entity
                continuity_checks.append(f"New entity discovered: {entity.name} ({entity.entity_type.value})")
        
        return continuity_checks
    
    def _check_entity_consistency(self, existing: CampaignEntity, new: CampaignEntity) -> List[str]:
        """Check for inconsistencies between existing and new entity information"""
        inconsistencies = []
        
        # Check for type inconsistencies
        if existing.entity_type != new.entity_type:
            inconsistencies.append(f"Entity type mismatch for {existing.name}: {existing.entity_type.value} vs {new.entity_type.value}")
        
        # Check for attribute inconsistencies
        for attr, value in new.core_attributes.items():
            if attr in existing.core_attributes and existing.core_attributes[attr] != value:
                inconsistencies.append(f"Core attribute mismatch for {existing.name}.{attr}: {existing.core_attributes[attr]} vs {value}")
        
        return inconsistencies
    
    def _merge_entity_information(self, existing: CampaignEntity, new: CampaignEntity, session_id: str):
        """Merge new information into existing entity"""
        # Update last mentioned
        existing.last_updated = session_id
        
        # Merge context snippets
        existing.context_snippets.extend(new.context_snippets)
        
        # Merge semantic tags
        for tag in new.semantic_tags:
            if not any(existing_tag.category == tag.category for existing_tag in existing.semantic_tags):
                existing.semantic_tags.append(tag)
        
        # Merge variable attributes
        existing.variable_attributes.update(new.variable_attributes)
        
        # Merge references
        existing.references.extend(new.references)
    
    def _generate_semantic_analysis(self, text: str, entities: List[CampaignEntity], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive semantic analysis of the session"""
        return {
            'primary_categories': [tag.category.value for tag in analysis.get('semantic_categories', [])],
            'context_distribution': self._get_context_distribution(analysis.get('context_levels', [])),
            'entity_types': [entity.entity_type.value for entity in entities],
            'relationship_density': len(analysis.get('relationships', [])) / max(len(entities), 1),
            'semantic_coherence': self._calculate_semantic_coherence(text, entities),
            'session_focus': self._determine_session_focus(analysis)
        }
    
    def _get_context_distribution(self, context_levels: List[ContextLevel]) -> Dict[str, int]:
        """Get distribution of context levels"""
        distribution = defaultdict(int)
        for level in context_levels:
            distribution[level.value] += 1
        return dict(distribution)
    
    def _calculate_semantic_coherence(self, text: str, entities: List[CampaignEntity]) -> float:
        """Calculate semantic coherence of the session"""
        # Simple coherence calculation based on entity relationships
        total_relationships = sum(len(entity.relationships) for entity in entities)
        total_entities = len(entities)
        
        if total_entities == 0:
            return 0.0
        
        # Coherence is higher when entities are well-connected
        return min(total_relationships / (total_entities * (total_entities - 1)), 1.0)
    
    def _determine_session_focus(self, analysis: Dict[str, Any]) -> str:
        """Determine the primary focus of the session"""
        categories = analysis.get('semantic_categories', [])
        if not categories:
            return "general"
        
        # Find the category with highest confidence
        primary_category = max(categories, key=lambda x: x.confidence)
        return primary_category.category.value
    
    def _create_context_map(self, entities: List[CampaignEntity], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a context map showing relationships and flow"""
        context_map = {
            'entities': [entity.name for entity in entities],
            'relationships': [],
            'flow': [],
            'key_moments': []
        }
        
        # Extract relationships
        for entity in entities:
            for target_id, rel_types in entity.relationships.items():
                target_entity = self.entities.get(target_id)
                if target_entity:
                    context_map['relationships'].append({
                        'from': entity.name,
                        'to': target_entity.name,
                        'type': rel_types[0] if rel_types else 'related'
                    })
        
        # Extract flow from player actions
        for action in analysis.get('player_actions', []):
            context_map['flow'].append({
                'type': 'player_action',
                'content': action
            })
        
        # Extract key moments from events
        for event in analysis.get('key_events', []):
            context_map['key_moments'].append({
                'type': event.get('type', 'event'),
                'description': event.get('description', ''),
                'entities': event.get('entities', [])
            })
        
        return context_map
    
    def _generate_enhanced_summary(self, text: str, entities: List[CampaignEntity], analysis: Dict[str, Any]) -> str:
        """Generate enhanced session summary with semantic understanding"""
        summary_parts = []
        
        # Session focus
        focus = self._determine_session_focus(analysis)
        summary_parts.append(f"Session focused on {focus} activities.")
        
        # Key entities
        if entities:
            entity_names = [entity.name for entity in entities[:3]]  # Top 3 entities
            summary_parts.append(f"Key entities: {', '.join(entity_names)}.")
        
        # Key events
        events = analysis.get('key_events', [])
        if events:
            event_descriptions = [event.get('description', '') for event in events[:2]]  # Top 2 events
            summary_parts.append(f"Key events: {'; '.join(event_descriptions)}.")
        
        # Player actions
        actions = analysis.get('player_actions', [])
        if actions:
            action_count = len(actions)
            summary_parts.append(f"Player performed {action_count} actions.")
        
        return ' '.join(summary_parts)
    
    def _update_entities_enhanced(self, entities: List[CampaignEntity], session_id: str):
        """Update entities with enhanced information"""
        for entity in entities:
            if entity.id in self.entities:
                # Update existing entity
                existing = self.entities[entity.id]
                self._merge_entity_information(existing, entity, session_id)
            else:
                # Add new entity
                self.entities[entity.id] = entity
                
                # Add to semantic index
                for tag in entity.semantic_tags:
                    self.semantic_index[tag.category].append(entity.id)
    
    def _save_session_to_database_enhanced(self, session: SessionLog):
        """Save enhanced session to database"""
        with sqlite3.connect(self.db_path) as conn:
            # Save session
            conn.execute("""
                INSERT OR REPLACE INTO sessions 
                (session_id, campaign_id, timestamp, raw_text, parsed_entities, key_events, 
                 player_actions, dm_responses, session_summary, continuity_checks, 
                 semantic_analysis, context_map)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                self.campaign_id,
                session.timestamp.isoformat(),
                session.raw_text,
                json.dumps([asdict(entity) for entity in session.parsed_entities]),
                json.dumps(session.key_events),
                json.dumps(session.player_actions),
                json.dumps(session.dm_responses),
                session.session_summary,
                json.dumps(session.continuity_checks),
                json.dumps(session.semantic_analysis),
                json.dumps(session.context_map)
            ))
            
            # Save entities
            for entity in session.parsed_entities:
                conn.execute("""
                    INSERT OR REPLACE INTO entities 
                    (id, campaign_id, name, entity_type, description, attributes, relationships,
                     first_mentioned, last_updated, confidence, context_snippets, semantic_tags,
                     context_level, aliases, core_attributes, variable_attributes, references)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entity.id,
                    self.campaign_id,
                    entity.name,
                    entity.entity_type.value,
                    entity.description,
                    json.dumps(entity.attributes),
                    json.dumps(entity.relationships),
                    entity.first_mentioned,
                    entity.last_updated,
                    entity.confidence,
                    json.dumps(entity.context_snippets),
                    json.dumps([asdict(tag) for tag in entity.semantic_tags]),
                    entity.context_level.value,
                    json.dumps(entity.aliases),
                    json.dumps(entity.core_attributes),
                    json.dumps(entity.variable_attributes),
                    json.dumps([asdict(ref) for ref in entity.references])
                ))
            
            conn.commit()
    
    def search_campaign_memory_enhanced(self, query: str, semantic_category: Optional[SemanticCategory] = None) -> List[Dict[str, Any]]:
        """Enhanced search with semantic understanding"""
        results = []
        
        # Search in entities
        for entity in self.entities.values():
            relevance = self._calculate_enhanced_relevance(entity, query, semantic_category)
            if relevance > 0.3:  # Threshold for relevance
                results.append({
                    'type': 'entity',
                    'content': entity,
                    'relevance': relevance,
                    'match_type': 'entity_search'
                })
        
        # Search in session content
        for session in self.sessions.values():
            if query.lower() in session.raw_text.lower():
                results.append({
                    'type': 'session',
                    'content': session,
                    'relevance': 0.8,
                    'match_type': 'text_search'
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results
    
    def _calculate_enhanced_relevance(self, entity: CampaignEntity, query: str, semantic_category: Optional[SemanticCategory] = None) -> float:
        """Calculate enhanced relevance score"""
        query_lower = query.lower()
        relevance = 0.0
        
        # Name matching
        if query_lower in entity.name.lower():
            relevance += 0.8
        
        # Description matching
        if query_lower in entity.description.lower():
            relevance += 0.6
        
        # Semantic category matching
        if semantic_category:
            for tag in entity.semantic_tags:
                if tag.category == semantic_category:
                    relevance += 0.4
        
        # Context snippet matching
        for snippet in entity.context_snippets:
            if query_lower in snippet.lower():
                relevance += 0.3
        
        return min(relevance, 1.0)
    
    def get_campaign_summary_enhanced(self) -> Dict[str, Any]:
        """Get enhanced campaign summary with semantic analysis"""
        summary = {
            'total_entities': len(self.entities),
            'total_sessions': len(self.sessions),
            'entity_types': self._count_entity_types(),
            'semantic_distribution': self._get_semantic_distribution(),
            'key_entities': self._get_key_entities_enhanced(),
            'recent_activity': self._get_recent_activity(),
            'campaign_timeline': self._get_campaign_timeline(),
            'relationship_network': self._get_relationship_network()
        }
        
        return summary
    
    def _get_semantic_distribution(self) -> Dict[str, int]:
        """Get distribution of semantic categories"""
        distribution = defaultdict(int)
        for entity in self.entities.values():
            for tag in entity.semantic_tags:
                distribution[tag.category.value] += 1
        return dict(distribution)
    
    def _get_key_entities_enhanced(self) -> List[Dict[str, Any]]:
        """Get key entities with enhanced information"""
        key_entities = []
        
        for entity in self.entities.values():
            # Calculate importance score
            importance = 0.0
            
            # Critical entities are more important
            if entity.context_level == ContextLevel.CRITICAL:
                importance += 0.5
            
            # Entities with many relationships are more important
            importance += len(entity.relationships) * 0.1
            
            # Entities mentioned in many sessions are more important
            mention_count = len(entity.context_snippets)
            importance += mention_count * 0.05
            
            if importance > 0.3:  # Threshold for key entities
                key_entities.append({
                    'name': entity.name,
                    'type': entity.entity_type.value,
                    'importance': importance,
                    'context_level': entity.context_level.value,
                    'relationship_count': len(entity.relationships)
                })
        
        # Sort by importance
        key_entities.sort(key=lambda x: x['importance'], reverse=True)
        return key_entities[:10]  # Top 10 entities
    
    def _get_relationship_network(self) -> Dict[str, Any]:
        """Get relationship network for visualization"""
        network = {
            'nodes': [],
            'edges': []
        }
        
        # Add nodes (entities)
        for entity in self.entities.values():
            network['nodes'].append({
                'id': entity.id,
                'name': entity.name,
                'type': entity.entity_type.value,
                'importance': len(entity.relationships)
            })
        
        # Add edges (relationships)
        for entity in self.entities.values():
            for target_id, rel_types in entity.relationships.items():
                if target_id in self.entities:
                    network['edges'].append({
                        'source': entity.id,
                        'target': target_id,
                        'type': rel_types[0] if rel_types else 'related',
                        'strength': len(rel_types)
                    })
        
        return network
    
    def _count_entity_types(self) -> Dict[str, int]:
        """Count entities by type"""
        counts = defaultdict(int)
        for entity in self.entities.values():
            counts[entity.entity_type.value] += 1
        return dict(counts)
    
    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent campaign activity"""
        recent_sessions = sorted(
            self.sessions.values(), 
            key=lambda s: s.timestamp, 
            reverse=True
        )[:5]
        
        return [{
            'session_id': session.session_id,
            'timestamp': session.timestamp,
            'summary': session.session_summary,
            'entities_mentioned': len(session.parsed_entities)
        } for session in recent_sessions]
    
    def _get_campaign_timeline(self) -> List[Dict[str, Any]]:
        """Get campaign timeline"""
        timeline = []
        
        for session in sorted(self.sessions.values(), key=lambda s: s.timestamp):
            timeline.append({
                'session_id': session.session_id,
                'timestamp': session.timestamp,
                'summary': session.session_summary,
                'key_events': session.key_events[:3]  # Top 3 events
            })
        
        return timeline
    
    def _find_entity_by_name(self, name: str) -> Optional[CampaignEntity]:
        """Find entity by name"""
        for entity in self.entities.values():
            if entity.name.lower() == name.lower():
                return entity
        return None
    
    def _extract_key_events_enhanced(self, text: str) -> List[Dict[str, Any]]:
        """Extract key events with enhanced understanding"""
        events = []
        
        # Look for action verbs and significant events
        event_patterns = [
            r'(\w+ (?:attacked|cast|moved|found|discovered|met|talked to|bought|sold|killed|saved))',
            r'(?:The party|You|They) (?:entered|left|arrived at|departed from) (\w+)',
            r'(?:A|An) (\w+) (?:appeared|emerged|approached|spoke)',
            r'(?:Quest|Mission|Objective) (?:completed|failed|started)',
            r'(?:Level|Experience|XP) (?:gained|increased)',
            r'(?:Item|Weapon|Armor) (?:found|acquired|equipped)'
        ]
        
        for pattern in event_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                events.append({
                    'event': match.group(),
                    'position': match.start(),
                    'type': 'action',
                    'description': match.group()
                })
        
        return events
    
    def _extract_player_actions_enhanced(self, text: str) -> List[str]:
        """Extract player actions with enhanced understanding"""
        actions = []
        
        # Look for player input patterns
        player_patterns = [
            r'Player: (.+)',
            r'You: (.+)',
            r'\[Player\] (.+)',
            r'I (?:attack|cast|move|search|talk|use|equip|drink|read)',
            r'(?:I want to|I will|I am going to) (.+)'
        ]
        
        for pattern in player_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                actions.append(match.group(1) if len(match.groups()) > 0 else match.group(0))
        
        return actions
    
    def _extract_dm_responses_enhanced(self, text: str) -> List[str]:
        """Extract DM responses with enhanced understanding"""
        responses = []
        
        # Look for DM response patterns
        dm_patterns = [
            r'DM: (.+)',
            r'Game Master: (.+)',
            r'\[DM\] (.+)',
            r'(?:The|A|An) (.+) (?:says|asks|tells|shouts|whispers)',
            r'(?:You see|You notice|You find|You discover) (.+)',
            r'(?:Roll|Make) (?:a|an) (.+) (?:check|save)'
        ]
        
        for pattern in dm_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                responses.append(match.group(1) if len(match.groups()) > 0 else match.group(0))
        
        return responses
    
    def _load_existing_data(self):
        """Load existing campaign data from enhanced database"""
        with sqlite3.connect(self.db_path) as conn:
            # Load entities
            cursor = conn.execute(
                "SELECT * FROM entities WHERE campaign_id = ?", 
                (self.campaign_id,)
            )
            for row in cursor.fetchall():
                # Parse semantic tags
                semantic_tags = []
                if row[11]:  # semantic_tags column
                    tag_data = json.loads(row[11])
                    for tag_dict in tag_data:
                        semantic_tags.append(SemanticTag(
                            category=SemanticCategory(tag_dict['category']),
                            confidence=tag_dict['confidence'],
                            context=tag_dict['context'],
                            keywords=tag_dict['keywords']
                        ))
                
                # Parse references
                references = []
                if row[16]:  # references column
                    ref_data = json.loads(row[16])
                    for ref_dict in ref_data:
                        references.append(ContextualReference(
                            entity_id=ref_dict['entity_id'],
                            relationship_type=ref_dict['relationship_type'],
                            context=ref_dict['context'],
                            strength=ref_dict['strength'],
                            timestamp=datetime.fromisoformat(ref_dict['timestamp'])
                        ))
                
                entity = CampaignEntity(
                    id=row[0],
                    name=row[2],
                    entity_type=EntityType(row[3]),
                    description=row[4],
                    attributes=json.loads(row[5]),
                    relationships=json.loads(row[6]),
                    first_mentioned=row[7],
                    last_updated=row[8],
                    confidence=row[9],
                    context_snippets=json.loads(row[10]),
                    semantic_tags=semantic_tags,
                    context_level=ContextLevel(row[12]) if row[12] else ContextLevel.MINOR,
                    aliases=json.loads(row[13]) if row[13] else [],
                    core_attributes=json.loads(row[14]) if row[14] else {},
                    variable_attributes=json.loads(row[15]) if row[15] else {},
                    references=references
                )
                self.entities[entity.id] = entity
            
            # Load sessions
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE campaign_id = ?", 
                (self.campaign_id,)
            )
            for row in cursor.fetchall():
                # Parse entities for session
                parsed_entities = []
                if row[4]:  # parsed_entities column
                    entity_data = json.loads(row[4])
                    for entity_dict in entity_data:
                        # Reconstruct entity objects (simplified)
                        parsed_entities.append(CampaignEntity(
                            id=entity_dict['id'],
                            name=entity_dict['name'],
                            entity_type=EntityType(entity_dict['entity_type']),
                            description=entity_dict['description'],
                            attributes=entity_dict['attributes'],
                            relationships=entity_dict['relationships'],
                            first_mentioned=entity_dict['first_mentioned'],
                            last_updated=entity_dict['last_updated'],
                            confidence=entity_dict['confidence'],
                            context_snippets=entity_dict['context_snippets'],
                            semantic_tags=[],  # Simplified for session loading
                            context_level=ContextLevel.MINOR,
                            aliases=[],
                            core_attributes={},
                            variable_attributes={},
                            references=[]
                        ))
                
                session = SessionLog(
                    session_id=row[0],
                    timestamp=datetime.fromisoformat(row[2]),
                    raw_text=row[3],
                    parsed_entities=parsed_entities,
                    key_events=json.loads(row[5]),
                    player_actions=json.loads(row[6]),
                    dm_responses=json.loads(row[7]),
                    session_summary=row[8],
                    continuity_checks=json.loads(row[9]),
                    semantic_analysis=json.loads(row[10]) if row[10] else {},
                    context_map=json.loads(row[11]) if row[11] else {}
                )
                self.sessions[session.session_id] = session
    
    def add_campaign_memory(self, memory_type: str, content: Dict[str, Any], session_id: str):
        """Add a memory entry to the campaign"""
        # Create a fact entry
        fact_id = f"fact_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO facts 
                (fact_id, campaign_id, fact_text, entity_ids, confidence, source_session, timestamp, semantic_category, context_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fact_id,
                self.campaign_id,
                json.dumps(content),
                json.dumps([]),  # entity_ids will be extracted later
                0.8,  # default confidence
                session_id,
                datetime.now().isoformat(),
                'general',  # default semantic category
                'moderate'  # default context level
            ))
            conn.commit()
    
    def get_campaign_memories(self, session_id: str) -> List[Dict[str, Any]]:
        """Get memories for a specific session"""
        memories = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM facts WHERE source_session = ? ORDER BY timestamp DESC",
                (session_id,)
            )
            
            for row in cursor.fetchall():
                memories.append({
                    'memory_type': 'fact',
                    'content': json.loads(row[2]),
                    'timestamp': row[6]
                })
        
        return memories
    
    def search_campaign_memories(self, session_id: str, query: str) -> List[Dict[str, Any]]:
        """Search memories for a specific session"""
        return self.search_campaign_memory_enhanced(query)
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """Get campaign summary (legacy method)"""
        return self.get_campaign_summary_enhanced() 