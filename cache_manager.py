"""
DnD 5E AI-Powered Game - Redis Cache Manager
===========================================

Redis caching for AI responses and session memory optimization
"""

import redis
import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis cache manager for DnD game optimization"""
    
    def __init__(self, redis_url: str = None):
        """Initialize Redis connection"""
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.redis_client = None
        self.connected = False
        self._connect()
    
    def _connect(self):
        """Connect to Redis with error handling"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.connected = True
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.connected = False
            self.redis_client = None
    
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix"""
        return f"dnd:{prefix}:{identifier}"
    
    def _hash_content(self, content: str) -> str:
        """Generate hash for content"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def cache_ai_response(self, prompt: str, response: str, session_id: str, ttl: int = 3600) -> bool:
        """
        Cache AI response for a given prompt
        
        Args:
            prompt: The user's input prompt
            response: The AI's response
            session_id: Current session ID
            ttl: Time to live in seconds (default 1 hour)
        
        Returns:
            bool: True if cached successfully, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            prompt_hash = self._hash_content(prompt)
            cache_key = self._get_cache_key("ai_response", prompt_hash)
            
            cache_data = {
                'prompt': prompt,
                'response': response,
                'session_id': session_id,
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': ttl
            }
            
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
            # Also store in session-specific cache
            session_key = self._get_cache_key("session_responses", session_id)
            self.redis_client.sadd(session_key, prompt_hash)
            self.redis_client.expire(session_key, ttl)
            
            logger.debug(f"Cached AI response for prompt hash: {prompt_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching AI response: {e}")
            return False
    
    def get_cached_response(self, prompt: str) -> Optional[str]:
        """
        Get cached AI response for a prompt
        
        Args:
            prompt: The user's input prompt
        
        Returns:
            str: Cached response if found, None otherwise
        """
        if not self.connected:
            return None
        
        try:
            prompt_hash = self._hash_content(prompt)
            cache_key = self._get_cache_key("ai_response", prompt_hash)
            
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                logger.debug(f"Cache hit for prompt hash: {prompt_hash}")
                return data['response']
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached response: {e}")
            return None
    
    def cache_session_memory(self, session_id: str, memory_data: Dict[str, Any], ttl: int = 7200) -> bool:
        """
        Cache session memory data
        
        Args:
            session_id: Current session ID
            memory_data: Memory data to cache
            ttl: Time to live in seconds (default 2 hours)
        
        Returns:
            bool: True if cached successfully, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            cache_key = self._get_cache_key("session_memory", session_id)
            
            cache_data = {
                'memory_data': memory_data,
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': ttl
            }
            
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
            logger.debug(f"Cached session memory for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching session memory: {e}")
            return False
    
    def get_session_memory(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached session memory
        
        Args:
            session_id: Current session ID
        
        Returns:
            dict: Cached memory data if found, None otherwise
        """
        if not self.connected:
            return None
        
        try:
            cache_key = self._get_cache_key("session_memory", session_id)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.debug(f"Cache hit for session memory: {session_id}")
                return data['memory_data']
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving session memory: {e}")
            return None
    
    def cache_world_state(self, campaign_id: str, world_state: Dict[str, Any], ttl: int = 86400) -> bool:
        """
        Cache world state for a campaign
        
        Args:
            campaign_id: Campaign ID
            world_state: World state data
            ttl: Time to live in seconds (default 24 hours)
        
        Returns:
            bool: True if cached successfully, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            cache_key = self._get_cache_key("world_state", campaign_id)
            
            cache_data = {
                'world_state': world_state,
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': ttl
            }
            
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
            logger.debug(f"Cached world state for campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching world state: {e}")
            return False
    
    def get_world_state(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached world state
        
        Args:
            campaign_id: Campaign ID
        
        Returns:
            dict: Cached world state if found, None otherwise
        """
        if not self.connected:
            return None
        
        try:
            cache_key = self._get_cache_key("world_state", campaign_id)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.debug(f"Cache hit for world state: {campaign_id}")
                return data['world_state']
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving world state: {e}")
            return None
    
    def clear_session_cache(self, session_id: str) -> bool:
        """
        Clear all cache entries for a session
        
        Args:
            session_id: Session ID to clear
        
        Returns:
            bool: True if cleared successfully, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            # Clear session responses
            session_key = self._get_cache_key("session_responses", session_id)
            response_hashes = self.redis_client.smembers(session_key)
            
            for prompt_hash in response_hashes:
                cache_key = self._get_cache_key("ai_response", prompt_hash)
                self.redis_client.delete(cache_key)
            
            # Clear session-specific keys
            self.redis_client.delete(session_key)
            self.redis_client.delete(self._get_cache_key("session_memory", session_id))
            
            logger.debug(f"Cleared cache for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing session cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            dict: Cache statistics
        """
        if not self.connected:
            return {'connected': False}
        
        try:
            info = self.redis_client.info()
            return {
                'connected': True,
                'used_memory': info.get('used_memory_human', 'Unknown'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'connected': False, 'error': str(e)}
    
    def health_check(self) -> bool:
        """
        Check if Redis is healthy
        
        Returns:
            bool: True if healthy, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except Exception:
            self.connected = False
            return False

# Global cache manager instance
cache_manager = CacheManager() 