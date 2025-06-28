"""
DnD 5E AI-Powered Game - Enhanced Campaign Manager
=================================================

Enhanced campaign manager with SQLAlchemy persistence and Redis caching
"""

import json
import os
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import logging

from models import get_session, Campaign, CampaignSession, Character, ChatMessage, create_database
from cache_manager import cache_manager
from main import DnDCampaignManager
from core.character_manager import Character as CoreCharacter
from core.combat_system import combat_system, skill_check_system, Combatant, SkillCheckResult
from core.memory_system import MemoryType, MemoryLayer, EmotionalContext

logger = logging.getLogger(__name__)

class EnhancedCampaignManager(DnDCampaignManager):
    """Enhanced campaign manager with database persistence and caching"""
    
    def __init__(self, campaign_name: str = "Default Campaign"):
        super().__init__(campaign_name)
        
        # Initialize database
        self.db_session = get_session()
        self.campaign_db = self._get_or_create_campaign(campaign_name)
        self.current_session_db = None
        
        # Cache integration
        self.cache_enabled = cache_manager.connected
        if self.cache_enabled:
            logger.info("Redis cache enabled")
        else:
            logger.warning("Redis cache not available - running without caching")
        
        # Combat system integration
        self.combat_system = combat_system
        self.skill_check_system = skill_check_system
    
    def _get_or_create_campaign(self, campaign_name: str) -> Campaign:
        """Get existing campaign or create new one"""
        campaign = self.db_session.query(Campaign).filter_by(name=campaign_name).first()
        
        if not campaign:
            campaign = Campaign(
                name=campaign_name,
                world_name=self.campaign_settings.get('world_name', 'Forgotten Realms'),
                difficulty=self.campaign_settings.get('difficulty', 'medium'),
                magic_level=self.campaign_settings.get('magic_level', 'standard')
            )
            self.db_session.add(campaign)
            self.db_session.commit()
            logger.info(f"Created new campaign: {campaign_name}")
        else:
            logger.info(f"Loaded existing campaign: {campaign_name}")
        
        return campaign
    
    def start_session(self, session_id: str = None) -> Any:
        """Start a new session with database persistence"""
        # Start session using parent class
        session_summary = super().start_session(session_id)
        
        # Create database session record
        self.current_session_db = CampaignSession(
            campaign_id=self.campaign_db.id,
            session_id=session_summary.session_id,
            name=f"Session {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            started_at=session_summary.start_time,
            is_active=True
        )
        self.db_session.add(self.current_session_db)
        self.db_session.commit()
        
        # Cache session memory
        if self.cache_enabled:
            memory_data = self.memory_system.to_dict()
            cache_manager.cache_session_memory(session_summary.session_id, memory_data)
        
        logger.info(f"Started session: {session_summary.session_id}")
        return session_summary
    
    def end_session(self) -> Any:
        """End the current session with database persistence"""
        if not self.current_session:
            raise ValueError("No active session to end")
        
        # End session using parent class
        session_summary = super().end_session()
        
        # Update database session record
        if self.current_session_db:
            self.current_session_db.ended_at = session_summary.end_time
            self.current_session_db.duration_minutes = session_summary.duration
            self.current_session_db.message_count = session_summary.message_count
            self.current_session_db.is_active = False
            self.current_session_db.current_location = self._get_current_location()
            self.current_session_db.active_quests = self.active_quests
            self.current_session_db.world_state = self._get_world_state()
            
            self.db_session.commit()
        
        # Clear session cache
        if self.cache_enabled:
            cache_manager.clear_session_cache(session_summary.session_id)
        
        self.current_session_db = None
        logger.info(f"Ended session: {session_summary.session_id}")
        return session_summary
    
    def save_campaign_state(self, save_name: str = None) -> Dict[str, Any]:
        """Save current campaign state to database"""
        if not save_name:
            save_name = f"Save {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Create a new session record for the save
        save_session = CampaignSession(
            campaign_id=self.campaign_db.id,
            session_id=f"save_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=save_name,
            started_at=datetime.datetime.utcnow(),
            ended_at=datetime.datetime.utcnow(),
            is_active=False,
            current_location=self._get_current_location(),
            active_quests=self.active_quests,
            world_state=self._get_world_state()
        )
        self.db_session.add(save_session)
        
        # Save current chat messages
        if self.current_session:
            for message in self.session_logger.get_current_messages():
                chat_message = ChatMessage(
                    session_id=save_session.id,
                    message_type=message.get('type', 'user'),
                    content=message.get('content', ''),
                    timestamp=message.get('timestamp', datetime.datetime.utcnow()),
                    msg_metadata=message.get('metadata', {})
                )
                self.db_session.add(chat_message)
        
        # Save characters
        for player_name, character in self.player_characters.items():
            char_record = Character(
                campaign_id=self.campaign_db.id,
                player_name=player_name,
                character_name=character.name,
                race=character.race.value,
                character_class=character.character_class.value,
                level=character.level,
                background=character.background,
                personality_traits=character.personality_traits,
                ability_scores={k.value: v for k, v in character.ability_scores.items()},
                inventory=character.inventory if hasattr(character, 'inventory') else [],
                experience_points=character.experience_points if hasattr(character, 'experience_points') else 0,
                hit_points=character.hit_points if hasattr(character, 'hit_points') else None,
                max_hit_points=character.max_hit_points if hasattr(character, 'max_hit_points') else None
            )
            self.db_session.add(char_record)
        
        self.db_session.commit()
        
        # Cache world state
        if self.cache_enabled:
            world_state = self._get_world_state()
            cache_manager.cache_world_state(str(self.campaign_db.id), world_state)
        
        logger.info(f"Saved campaign state: {save_name}")
        return {
            'save_name': save_name,
            'session_id': save_session.session_id,
            'timestamp': save_session.started_at.isoformat()
        }
    
    def load_campaign_state(self, session_id: str) -> bool:
        """Load campaign state from database"""
        try:
            # Find the save session
            save_session = self.db_session.query(CampaignSession).filter_by(
                session_id=session_id,
                campaign_id=self.campaign_db.id
            ).first()
            
            if not save_session:
                logger.error(f"Save session not found: {session_id}")
                return False
            
            # Load world state
            if save_session.world_state:
                self.active_quests = save_session.world_state.get('active_quests', [])
                # Restore other world state as needed
            
            # Load characters
            characters = self.db_session.query(Character).filter_by(
                campaign_id=self.campaign_db.id
            ).all()
            
            self.player_characters.clear()
            for char_record in characters:
                # Convert back to core character object
                from core.character_manager import Race, CharacterClass, AbilityScore
                
                ability_scores = {}
                for key, value in char_record.ability_scores.items():
                    ability_scores[AbilityScore(key)] = value
                
                character = CoreCharacter(
                    name=char_record.character_name,
                    race=Race(char_record.race),
                    character_class=CharacterClass(char_record.character_class),
                    level=char_record.level,
                    background=char_record.background,
                    personality_traits=char_record.personality_traits or [],
                    ability_scores=ability_scores
                )
                
                # Restore additional character data
                if hasattr(character, 'inventory'):
                    character.inventory = char_record.inventory or []
                if hasattr(character, 'experience_points'):
                    character.experience_points = char_record.experience_points
                if hasattr(character, 'hit_points'):
                    character.hit_points = char_record.hit_points
                if hasattr(character, 'max_hit_points'):
                    character.max_hit_points = char_record.max_hit_points
                
                self.player_characters[char_record.player_name] = character
            
            # Load chat history
            messages = self.db_session.query(ChatMessage).filter_by(
                session_id=save_session.id
            ).order_by(ChatMessage.timestamp).all()
            
            # Restore chat history to memory system
            for message in messages:
                self.memory_system.add_memory(
                    content={
                        'type': message.message_type,
                        'content': message.content,
                        'timestamp': message.timestamp.isoformat()
                    },
                    memory_type=MemoryType.EVENT,
                    layer=MemoryLayer.SHORT_TERM,
                    user_id='system',
                    session_id=save_session.session_id,
                    emotional_weight=0.3,
                    thematic_tags=['chat_message', 'session_history']
                )
            
            logger.info(f"Loaded campaign state from: {save_session.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading campaign state: {e}")
            return False
    
    def get_saved_sessions(self) -> List[Dict[str, Any]]:
        """Get list of saved sessions"""
        sessions = self.db_session.query(CampaignSession).filter_by(
            campaign_id=self.campaign_db.id,
            is_active=False
        ).order_by(CampaignSession.started_at.desc()).all()
        
        return [session.to_dict() for session in sessions]
    
    def process_player_action(self, message: str, character: CoreCharacter = None) -> str:
        """Process player action with caching and skill check integration"""
        # Check cache first
        if self.cache_enabled and self.current_session:
            cached_response = cache_manager.get_cached_response(message)
            if cached_response:
                logger.info("Using cached response")
                return cached_response
        
        # Check if this action requires a skill check
        skill_check_result = self._check_for_skill_check(message, character)
        
        # Process normally
        response = super().process_player_action(message, character)
        
        # If a skill check was made, include it in the response
        if skill_check_result:
            response = f"{response}\n\n{skill_check_system.format_skill_check_result(skill_check_result)}"
        
        # Cache the response
        if self.cache_enabled and self.current_session:
            cache_manager.cache_ai_response(
                message, 
                response, 
                self.current_session.session_id
            )
        
        # Save message to database
        if self.current_session_db:
            chat_message = ChatMessage(
                session_id=self.current_session_db.id,
                message_type='user',
                content=message,
                timestamp=datetime.datetime.utcnow()
            )
            self.db_session.add(chat_message)
            
            # Add AI response
            ai_message = ChatMessage(
                session_id=self.current_session_db.id,
                message_type='ai',
                content=response,
                timestamp=datetime.datetime.utcnow()
            )
            self.db_session.add(ai_message)
            
            self.current_session_db.message_count += 2
            self.db_session.commit()
        
        return response
    
    def _check_for_skill_check(self, message: str, character: CoreCharacter = None) -> Optional[SkillCheckResult]:
        """Check if a player action requires a skill check"""
        if not character:
            return None
        
        # Convert character to Combatant for skill check system
        combatant = self._character_to_combatant(character)
        
        # Simple skill check detection based on keywords
        message_lower = message.lower()
        
        # Define skill check triggers
        skill_triggers = {
            'athletics': ['climb', 'jump', 'swim', 'push', 'pull', 'lift', 'break'],
            'acrobatics': ['balance', 'tumble', 'dodge', 'escape', 'squeeze'],
            'stealth': ['sneak', 'hide', 'conceal', 'move quietly'],
            'perception': ['look', 'search', 'examine', 'investigate', 'notice'],
            'insight': ['read', 'sense', 'detect lie', 'understand motive'],
            'persuasion': ['convince', 'persuade', 'negotiate', 'bargain'],
            'intimidation': ['threaten', 'intimidate', 'scare', 'bully'],
            'deception': ['lie', 'deceive', 'bluff', 'mislead'],
            'sleight_of_hand': ['pick pocket', 'steal', 'sleight', 'trick'],
            'arcana': ['magic', 'spell', 'arcane', 'enchantment'],
            'nature': ['survival', 'track', 'hunt', 'wilderness'],
            'religion': ['divine', 'holy', 'sacred', 'religious'],
            'medicine': ['heal', 'treat', 'diagnose', 'medical'],
            'history': ['remember', 'recall', 'historical', 'ancient'],
            'investigation': ['search', 'examine', 'analyze', 'deduce']
        }
        
        # Check for skill check triggers
        for skill, triggers in skill_triggers.items():
            if any(trigger in message_lower for trigger in triggers):
                # Determine DC based on task description
                dc = skill_check_system.determine_dc(message, character.level)
                
                # Make the skill check
                result = skill_check_system.make_skill_check(combatant, skill, dc)
                
                # Log the skill check
                self.memory_system.add_memory(
                    content={
                        'skill': skill,
                        'result': asdict(result),
                        'trigger': message
                    },
                    memory_type=MemoryType.EVENT,
                    layer=MemoryLayer.SHORT_TERM,
                    user_id=character.name if character else 'unknown',
                    session_id=self.current_session.session_id if self.current_session else 'skill_check',
                    emotional_weight=0.6,
                    thematic_tags=['skill_check', 'gameplay']
                )
                
                return result
        
        return None
    
    def _character_to_combatant(self, character: CoreCharacter) -> Combatant:
        """Convert a core character to a combatant for the combat system"""
        # Convert ability scores
        abilities = {}
        for ability, score in character.ability_scores.items():
            abilities[ability.value.lower()] = score
        
        # Calculate skill modifiers (simplified - you might want to enhance this)
        skills = {}
        for ability_name, score in abilities.items():
            modifier = skill_check_system.calculate_modifier(score)
            # Map ability to relevant skills
            for skill, ability in skill_check_system.SKILL_ABILITY_MAP.items():
                if ability == ability_name:
                    skills[skill] = modifier
        
        # Set default combat stats if not present
        armor_class = getattr(character, 'armor_class', 10)
        max_hp = getattr(character, 'max_hit_points', 10)
        current_hp = getattr(character, 'hit_points', max_hp)
        attack_bonus = getattr(character, 'attack_bonus', 0)
        damage_dice = getattr(character, 'damage_dice', '1d6')
        
        return Combatant(
            name=character.name,
            character_type='player',
            armor_class=armor_class,
            max_hit_points=max_hp,
            current_hit_points=current_hp,
            initiative_modifier=skill_check_system.calculate_modifier(abilities.get('dexterity', 10)),
            attack_bonus=attack_bonus,
            damage_dice=damage_dice,
            abilities=abilities,
            skills=skills
        )
    
    def start_combat(self, enemies: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start a combat encounter"""
        # Clear existing combat
        self.combat_system.combatants.clear()
        self.combat_system.initiative_order.clear()
        
        # Add player characters
        for player_name, character in self.player_characters.items():
            combatant = self._character_to_combatant(character)
            self.combat_system.add_combatant(combatant)
        
        # Add enemies if provided
        if enemies:
            for enemy_data in enemies:
                enemy = Combatant(
                    name=enemy_data['name'],
                    character_type='monster',
                    armor_class=enemy_data.get('armor_class', 10),
                    max_hit_points=enemy_data.get('hit_points', 10),
                    current_hit_points=enemy_data.get('hit_points', 10),
                    initiative_modifier=enemy_data.get('initiative_modifier', 0),
                    attack_bonus=enemy_data.get('attack_bonus', 0),
                    damage_dice=enemy_data.get('damage_dice', '1d6'),
                    abilities=enemy_data.get('abilities', {}),
                    skills=enemy_data.get('skills', {})
                )
                self.combat_system.add_combatant(enemy)
        
        # Roll initiative
        initiative_order = self.combat_system.roll_initiative()
        
        # Log combat start
        self.memory_system.add_memory(
            content={
                'initiative_order': [asdict(entry) for entry in initiative_order],
                'combatants': [combatant.name for combatant in self.combat_system.combatants.values()]
            },
            memory_type=MemoryType.EVENT,
            layer=MemoryLayer.SHORT_TERM,
            user_id='dm',
            session_id=self.current_session.session_id if self.current_session else 'combat',
            emotional_weight=0.8,
            thematic_tags=['combat_start', 'gameplay']
        )
        
        return self.combat_system.get_combat_status()
    
    def make_attack(self, attacker_name: str, target_name: str) -> Dict[str, Any]:
        """Make an attack in combat"""
        try:
            result = self.combat_system.make_attack(attacker_name, target_name)
            
            # Log the attack
            self.memory_system.add_memory(
                content=asdict(result),
                memory_type=MemoryType.EVENT,
                layer=MemoryLayer.SHORT_TERM,
                user_id=attacker_name,
                session_id=self.current_session.session_id if self.current_session else 'combat',
                emotional_weight=0.7,
                thematic_tags=['combat_attack', 'gameplay']
            )
            
            return asdict(result)
        except ValueError as e:
            logger.error(f"Attack error: {e}")
            return {'error': str(e)}
    
    def next_combat_turn(self) -> Optional[str]:
        """Advance to the next turn in combat"""
        next_combatant = self.combat_system.next_turn()
        if next_combatant:
            return next_combatant.name
        return None
    
    def end_combat(self) -> Dict[str, Any]:
        """End the current combat encounter"""
        self.combat_system.end_combat()
        
        # Log combat end
        self.memory_system.add_memory(
            content={
                'survivors': [name for name, combatant in self.combat_system.combatants.items() if combatant.is_alive()]
            },
            memory_type=MemoryType.EVENT,
            layer=MemoryLayer.MID_TERM,
            user_id='dm',
            session_id=self.current_session.session_id if self.current_session else 'combat',
            emotional_weight=0.9,
            thematic_tags=['combat_end', 'gameplay']
        )
        
        return self.combat_system.get_combat_status()
    
    def get_combat_status(self) -> Dict[str, Any]:
        """Get current combat status"""
        return self.combat_system.get_combat_status()
    
    def _get_current_location(self) -> str:
        """Get current location from memory system"""
        try:
            location_memories = self.memory_system.recall(query="current location", limit=1)
            if location_memories:
                return location_memories[0].content.get('location', 'Unknown')
            return 'Unknown'
        except:
            return 'Unknown'
    
    def _get_world_state(self) -> Dict[str, Any]:
        """Get current world state"""
        return {
            'active_quests': self.active_quests,
            'campaign_settings': self.campaign_settings,
            'character_count': len(self.player_characters),
            'session_active': self.current_session is not None,
            'combat_state': self.combat_system.get_state() if self.combat_system.in_combat else None
        }
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """Get enhanced campaign summary with database info"""
        summary = super().get_campaign_summary()
        
        # Add database info
        summary['campaign_id'] = self.campaign_db.id
        summary['total_sessions'] = len(self.campaign_db.sessions)
        summary['total_characters'] = len(self.campaign_db.characters)
        summary['cache_enabled'] = self.cache_enabled
        
        # Add combat info
        summary['in_combat'] = self.combat_system.in_combat
        if self.combat_system.in_combat:
            summary['combat_round'] = self.combat_system.round
            summary['current_combatant'] = self.combat_system.get_current_combatant().name if self.combat_system.get_current_combatant() else None
        
        if self.cache_enabled:
            summary['cache_stats'] = cache_manager.get_cache_stats()
        
        return summary
    
    def __del__(self):
        """Cleanup database session"""
        if hasattr(self, 'db_session'):
            self.db_session.close()

# Initialize database on import
if __name__ == '__main__':
    create_database()
    print("Database initialized successfully!") 