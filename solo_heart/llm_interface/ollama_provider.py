#!/usr/bin/env python3
"""
Ollama LLM Provider for SoloHeart
Connects to Ollama running locally at http://localhost:11434
"""

import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from .llm_provider_base import LLMProviderBase

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProviderBase):
    """Ollama LLM provider using Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3"):
        super().__init__(base_url, model_name)
        self.chat_endpoint = "/api/chat"
        self.health_endpoint = "/api/tags"
    
    def _verify_connection(self) -> None:
        """Verify that Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.base_url}{self.health_endpoint}", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                if self.model_name in model_names:
                    logger.info(f"✅ Ollama connection verified at {self.base_url}")
                    logger.info(f"✅ Model '{self.model_name}' is available")
                else:
                    logger.warning(f"⚠️  Model '{self.model_name}' not found. Available models: {model_names}")
                    logger.info("💡 You may need to pull the model: ollama pull llama3")
            else:
                raise Exception(f"Ollama health check failed with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"❌ Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
        except Exception as e:
            raise Exception(f"❌ Ollama connection error: {e}")
    
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """
        Send a chat completion request to Ollama.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (optional)
        
        Returns:
            The assistant's response content as a string
        
        Raises:
            Exception: If Ollama is not available or request fails
        """
        try:
            # Prepare the request payload (Ollama format)
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            # Add max_tokens if specified (Ollama uses num_predict)
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            # Make the request using the base class method
            response_data = self._make_request(self.chat_endpoint, payload)
            
            # Parse the response (Ollama format)
            assistant_message = response_data.get('message', {})
            content = assistant_message.get('content', '')
            
            if not content:
                raise Exception("Empty response from Ollama")
            
            logger.debug(f"Received response from Ollama: {content[:100]}...")
            return content
            
        except Exception as e:
            raise Exception(f"❌ Ollama API error: {e}")
    
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