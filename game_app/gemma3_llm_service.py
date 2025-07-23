#!/usr/bin/env python3
"""
Gemma3 LLM Service for SoloHeart
Centralized service for all LLM interactions using Gemma3 via LM Studio.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import the GemmaClient from the llm_adapters package
try:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from llm_adapters.llm_adapters import GemmaClient
except ImportError as e:
    logging.error(f"Failed to import GemmaClient: {e}")
    raise

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Gemma3LLMService:
    """Centralized service for Gemma3 LLM interactions via LM Studio."""
    
    def __init__(self, endpoint: str = "http://localhost:1234/v1"):
        self.endpoint = endpoint
        self.client = GemmaClient(endpoint=endpoint)
        
        # Verify Gemma3 is running
        self._verify_gemma3_connection()
    
    def _verify_gemma3_connection(self):
        """Verify that Gemma3 is running and accessible via LM Studio."""
        try:
            if self.client.health_check():
                logger.info(f"✅ Gemma3 connection verified at {self.endpoint}")
            else:
                raise Exception("Gemma3 health check failed")
        except Exception as e:
            raise Exception(f"❌ Cannot connect to Gemma3 at {self.endpoint}. Is LM Studio running with Gemma3 loaded? Error: {e}")
    
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """
        Send a chat completion request to Gemma3.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (optional)
        
        Returns:
            The assistant's response content as a string
        
        Raises:
            Exception: If Gemma3 is not available or request fails
        """
        try:
            # Prepare parameters
            params = {
                'temperature': temperature
            }
            if max_tokens:
                params['max_tokens'] = max_tokens
            
            logger.debug(f"Sending chat completion request to Gemma3: {len(messages)} messages")
            
            # Use the GemmaClient
            response = self.client.chat(messages, **params)
            
            if not response:
                raise Exception("Empty response from Gemma3")
            
            return response
            
        except Exception as e:
            logger.error(f"Gemma3 chat completion error: {e}")
            raise
    
    def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """
        Generate text using Gemma3 with a simple prompt.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Controls randomness (0.0 to 1.0)
        
        Returns:
            Generated text as a string
        """
        try:
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            logger.debug(f"Generating text with Gemma3: prompt length={len(prompt)}")
            
            # Use chat completion
            response = self.chat_completion(messages, temperature=temperature)
            
            return response
            
        except Exception as e:
            logger.error(f"Gemma3 text generation error: {e}")
            raise
    
    def generate_conversation_response(self, conversation_history: List[Dict[str, str]], system_prompt: str = "", temperature: float = 0.7) -> str:
        """
        Generate a response in a conversation context.
        
        Args:
            conversation_history: List of previous messages
            system_prompt: Optional system prompt
            temperature: Controls randomness (0.0 to 1.0)
        
        Returns:
            Generated response as a string
        """
        try:
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(conversation_history)
            
            logger.debug(f"Generating conversation response with Gemma3: {len(conversation_history)} history messages")
            
            # Use chat completion
            response = self.chat_completion(messages, temperature=temperature)
            
            return response
            
        except Exception as e:
            logger.error(f"Gemma3 conversation response error: {e}")
            raise

# Global service instance
_gemma3_service = None

def get_gemma3_service() -> Gemma3LLMService:
    """Get or create the global Gemma3 service instance."""
    global _gemma3_service
    if _gemma3_service is None:
        _gemma3_service = Gemma3LLMService()
    return _gemma3_service

# Convenience functions for backward compatibility
def chat_completion(messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
    """Convenience function for chat completion."""
    service = get_gemma3_service()
    return service.chat_completion(messages, temperature, max_tokens)

def generate_text(prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
    """Convenience function for text generation."""
    service = get_gemma3_service()
    return service.generate_text(prompt, system_prompt, temperature)

def generate_conversation_response(conversation_history: List[Dict[str, str]], system_prompt: str = "", temperature: float = 0.7) -> str:
    """Convenience function for conversation response generation."""
    service = get_gemma3_service()
    return service.generate_conversation_response(conversation_history, system_prompt, temperature) 