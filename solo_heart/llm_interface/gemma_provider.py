#!/usr/bin/env python3
"""
Gemma LLM Provider for SoloHeart
Connects to Gemma 3 running locally at http://localhost:1234/v1
"""

import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from .llm_provider_base import LLMProviderBase

logger = logging.getLogger(__name__)

class GemmaProvider(LLMProviderBase):
    """Gemma LLM provider using OpenAI-compatible API."""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1", model_name: str = "gemma"):
        self.chat_endpoint = "/chat/completions"
        self.health_endpoint = "/models"
        super().__init__(base_url, model_name)
    
    def _verify_connection(self) -> None:
        """Verify that Gemma is running and accessible."""
        try:
            response = requests.get(f"{self.base_url}{self.health_endpoint}", timeout=5)
            if response.status_code == 200:
                models = response.json().get('data', [])
                model_names = [model.get('id', '') for model in models]
                if self.model_name in model_names or any('gemma' in name.lower() for name in model_names):
                    logger.info(f"✅ Gemma connection verified at {self.base_url}")
                    logger.info(f"✅ Available models: {model_names}")
                else:
                    logger.warning(f"⚠️  Model '{self.model_name}' not found. Available models: {model_names}")
                    logger.info("💡 Using first available model")
            else:
                raise Exception(f"Gemma health check failed with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"❌ Cannot connect to Gemma at {self.base_url}. Is Gemma running?")
        except Exception as e:
            raise Exception(f"❌ Gemma connection error: {e}")
    
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """
        Send a chat completion request to Gemma.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (optional)
        
        Returns:
            The assistant's response content as a string
        
        Raises:
            Exception: If Gemma is not available or request fails
        """
        try:
            # Prepare the request payload (OpenAI-compatible format)
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            }
            
            # Add max_tokens if specified
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            # Make the request using the base class method
            response_data = self._make_request(self.chat_endpoint, payload)
            
            # Parse the response (OpenAI-compatible format)
            choices = response_data.get('choices', [])
            if not choices:
                raise Exception("Empty response from Gemma")
            
            assistant_message = choices[0].get('message', {})
            content = assistant_message.get('content', '')
            
            if not content:
                raise Exception("Empty response content from Gemma")
            
            # Log token information for debugging
            self._log_token_info(messages, content)
            
            logger.debug(f"Received response from Gemma: {content[:100]}...")
            return content
            
        except Exception as e:
            raise Exception(f"❌ Gemma API error: {e}")
    
    def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """
        Generate text using a simple prompt format.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Controls randomness
        
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat_completion(messages, temperature=temperature)
    
    def generate_conversation_response(self, conversation_history: List[Dict[str, str]], system_prompt: str = "", temperature: float = 0.7) -> str:
        """
        Generate a response in a conversation context.
        
        Args:
            conversation_history: List of message dictionaries
            system_prompt: Optional system prompt
            temperature: Controls randomness
        
        Returns:
            The assistant's response
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend(conversation_history)
        
        return self.chat_completion(messages, temperature=temperature) 