#!/usr/bin/env python3
"""
Base LLM Provider Interface for SoloHeart
Defines the interface that all LLM providers must implement.
"""

import os
import json
import logging
import requests
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMProviderBase(ABC):
    """Base class for all LLM providers in SoloHeart."""
    
    def __init__(self, base_url: str, model_name: str = None):
        self.base_url = base_url
        self.model_name = model_name
        self.provider_name = self.__class__.__name__.replace('Provider', '').lower()
        
        # Get timeout from environment or use default
        self.timeout = int(os.environ.get('LLM_TIMEOUT_SECONDS', '180'))
        
        # Verify connection on initialization
        self._verify_connection()
        
        logger.info(f"[LLM] Using {self.provider_name.title()} provider at {self.base_url} (timeout: {self.timeout}s)")
    
    @abstractmethod
    def _verify_connection(self) -> None:
        """Verify that the LLM provider is accessible."""
        pass
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """
        Send a chat completion request to the LLM provider.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (optional)
        
        Returns:
            The assistant's response content as a string
        
        Raises:
            Exception: If the provider is not available or request fails
        """
        pass
    
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
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for a given text.
        This is a rough approximation (1 token ≈ 4 characters for English text).
        
        Args:
            text: The text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters for English text
        return len(text) // 4
    
    def _log_token_info(self, messages: List[Dict[str, str]], response: str = "") -> None:
        """
        Log token information for debugging.
        
        Args:
            messages: The messages sent to the LLM
            response: The response from the LLM
        """
        if os.environ.get('DEBUG_LLM', 'false').lower() == 'true':
            total_input = sum(len(msg.get('content', '')) for msg in messages)
            input_tokens = self._estimate_tokens(total_input)
            output_tokens = self._estimate_tokens(response)
            
            logger.info(f"[DEBUG] Token estimation:")
            logger.info(f"[DEBUG] Input tokens: ~{input_tokens}")
            logger.info(f"[DEBUG] Output tokens: ~{output_tokens}")
            logger.info(f"[DEBUG] Total tokens: ~{input_tokens + output_tokens}")
            
            # Warn if approaching Gemma's limit (8192 tokens)
            if input_tokens + output_tokens > 7000:
                logger.warning(f"[DEBUG] ⚠️ Approaching token limit! Total: ~{input_tokens + output_tokens}")
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any], timeout: int = None) -> Dict[str, Any]:
        """
        Make a request to the LLM provider with error handling.
        
        Args:
            endpoint: The API endpoint to call
            payload: The request payload
            timeout: Request timeout in seconds (uses self.timeout if None)
        
        Returns:
            The response data as a dictionary
        
        Raises:
            Exception: If the request fails
        """
        if timeout is None:
            timeout = self.timeout
            
        try:
            url = f"{self.base_url}{endpoint}"
            
            # Debug logging if enabled
            if os.environ.get('DEBUG_LLM', 'false').lower() == 'true':
                logger.info(f"[DEBUG] Sending request to {self.provider_name}:")
                logger.info(f"[DEBUG] URL: {url}")
                logger.info(f"[DEBUG] Timeout: {timeout}s")
                logger.info(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")
            
            start_time = time.time()
            
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            
            response_time = time.time() - start_time
            
            if os.environ.get('DEBUG_LLM', 'false').lower() == 'true':
                logger.info(f"[DEBUG] Response time: {response_time:.2f}s")
                logger.info(f"[DEBUG] Status code: {response.status_code}")
            
            if response.status_code != 200:
                raise Exception(f"{self.provider_name.title()} API error: {response.status_code} - {response.text}")
            
            response_data = response.json()
            
            if os.environ.get('DEBUG_LLM', 'false').lower() == 'true':
                logger.info(f"[DEBUG] Response data: {str(response_data)[:200]}...")
            
            return response_data
            
        except requests.exceptions.ConnectionError:
            raise Exception(f"❌ Cannot connect to {self.provider_name.title()} at {self.base_url}. Is it running?")
        except requests.exceptions.Timeout:
            raise Exception(f"⏰ {self.provider_name.title()} request timed out after {timeout} seconds. The model may be too slow or the prompt too long.")
        except Exception as e:
            raise Exception(f"❌ {self.provider_name.title()} API error: {e}") 