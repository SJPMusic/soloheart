"""
DnD 5E AI-Powered Game - Database Models
=======================================

SQLAlchemy models for campaign persistence and chat history
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
import os

Base = declarative_base()

class Campaign(Base):
    """Campaign model for storing campaign metadata"""
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    world_name = Column(String(255), default='fantasy campaign setting')
    difficulty = Column(String(50), default='medium')
    magic_level = Column(String(50), default='standard')
    is_active = Column(Boolean, default=True)
    
    # Relationships
    sessions = relationship("CampaignSession", back_populates="campaign", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="campaign", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert campaign to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'world_name': self.world_name,
            'difficulty': self.difficulty,
            'magic_level': self.magic_level,
            'is_active': self.is_active,
            'session_count': len(self.sessions),
            'character_count': len(self.characters)
        }

class CampaignSession(Base):
    """Session model for storing individual game sessions"""
    __tablename__ = 'campaign_sessions'
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    session_id = Column(String(255), nullable=False, unique=True)
    name = Column(String(255))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    duration_minutes = Column(Integer)
    message_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Session state
    current_location = Column(Text)
    active_quests = Column(JSON)  # Store as JSON
    world_state = Column(JSON)    # Store as JSON
    
    # Relationships
    campaign = relationship("Campaign", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'session_id': self.session_id,
            'name': self.name,
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration_minutes': self.duration_minutes,
            'message_count': self.message_count,
            'is_active': self.is_active,
            'current_location': self.current_location,
            'active_quests': self.active_quests or [],
            'world_state': self.world_state or {}
        }

class Character(Base):
    """Character model for storing player characters"""
    __tablename__ = 'characters'
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    player_name = Column(String(255), nullable=False)
    character_name = Column(String(255), nullable=False)
    race = Column(String(100), nullable=False)
    character_class = Column(String(100), nullable=False)
    level = Column(Integer, default=1)
    background = Column(String(255))
    personality_traits = Column(JSON)
    ability_scores = Column(JSON)
    inventory = Column(JSON)
    experience_points = Column(Integer, default=0)
    hit_points = Column(Integer)
    max_hit_points = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="characters")
    
    def to_dict(self):
        """Convert character to dictionary"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'player_name': self.player_name,
            'character_name': self.character_name,
            'race': self.race,
            'character_class': self.character_class,
            'level': self.level,
            'background': self.background,
            'personality_traits': self.personality_traits or [],
            'ability_scores': self.ability_scores or {},
            'inventory': self.inventory or [],
            'experience_points': self.experience_points,
            'hit_points': self.hit_points,
            'max_hit_points': self.max_hit_points,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ChatMessage(Base):
    """Chat message model for storing conversation history"""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('campaign_sessions.id'), nullable=False)
    message_type = Column(String(50), nullable=False)  # 'user', 'ai', 'system', 'error'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    msg_metadata = Column(JSON)  # Store additional context like character actions, dice rolls, etc.
    
    # Relationships
    session = relationship("CampaignSession", back_populates="messages")
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message_type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.msg_metadata or {}
        }

# Database setup
def get_database_url():
    """Get database URL from environment or use default SQLite"""
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url
    
    # Default to SQLite in the project directory
    db_path = os.path.join(os.path.dirname(__file__), 'dnd_game.db')
    return f'sqlite:///{db_path}'

def create_database():
    """Create database and tables"""
    engine = create_engine(get_database_url())
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get database session"""
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    return Session()

# Initialize database on import
if __name__ == '__main__':
    create_database()
    print("Database created successfully!") 