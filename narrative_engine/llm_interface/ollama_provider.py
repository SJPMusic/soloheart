"""
Ollama LLM provider for The Narrative Engine.
"""

import requests
import json
import logging
from typing import List, Dict, Any
from .llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    """Ollama LLM provider implementation."""
    
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(model_name, **kwargs)
        self.base_url = base_url.rstrip('/')
        self.is_available = self.test_connection()
    
    def test_connection(self) -> bool:
        """Test if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                if self.model_name in available_models:
                    logger.info(f"Ollama connection successful. Available models: {available_models}")
                    return True
                else:
                    logger.warning(f"Model {self.model_name} not found. Available: {available_models}")
                    return False
            else:
                logger.error(f"Ollama connection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            return False
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat completion using Ollama."""
        if not self.is_available:
            raise Exception("Ollama is not available")
        
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                # Ollama doesn't have system messages, so we'll prepend to the first user message
                continue
            ollama_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # If we have a system message, prepend it to the first user message
        if messages and messages[0]['role'] == 'system':
            if ollama_messages:
                ollama_messages[0]['content'] = f"{messages[0]['content']}\n\n{ollama_messages[0]['content']}"
        
        payload = {
            'model': self.model_name,
            'messages': ollama_messages,
            'stream': False,
            'options': {
                'temperature': self.temperature,
                'num_predict': self.max_tokens
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['message']['content']
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise 