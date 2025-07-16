#!/usr/bin/env python3
"""
LLM Provider Factory for SoloHeart
Dynamically loads the correct LLM provider based on environment configuration.
Standardized on Google Gemma 3 for all AI operations.
"""

import os
import logging
from typing import Optional
from .llm_provider_base import LLMProviderBase
from .gemma_provider import GemmaProvider

logger = logging.getLogger(__name__)

# Global provider instance
_llm_provider = None

def get_llm_provider() -> LLMProviderBase:
    """
    Get the configured LLM provider instance.
    
    Returns:
        An instance of the configured LLM provider (Gemma 3)
        
    Raises:
        Exception: If the provider cannot be loaded or configured
    """
    global _llm_provider
    
    if _llm_provider is None:
        _llm_provider = _create_provider()
    
    return _llm_provider

def _create_provider() -> LLMProviderBase:
    """
    Create the appropriate LLM provider based on environment configuration.
    Currently standardized on Google Gemma 3.
    
    Returns:
        An instance of the configured LLM provider
        
    Raises:
        Exception: If the provider cannot be created
    """
    # Get provider type from environment (default to gemma)
    provider_type = os.environ.get('LLM_PROVIDER', 'gemma').lower()
    
    logger.info(f"[LLM] Loading provider: {provider_type}")
    
    if provider_type == 'gemma':
        return _create_gemma_provider()
    else:
        raise Exception(f"Unknown LLM provider: {provider_type}. Supported providers: gemma")

def _create_gemma_provider() -> GemmaProvider:
    """Create a Gemma 3 provider instance."""
    base_url = os.environ.get('GEMMA_API_URL', 'http://localhost:1234/v1')
    model_name = os.environ.get('GEMMA_MODEL', 'google/gemma-3-12b')
    
    logger.info(f"[LLM] Creating Gemma 3 provider at {base_url} with model {model_name}")
    
    return GemmaProvider(base_url=base_url, model_name=model_name)

# Convenience functions for backward compatibility
def chat_completion(messages, temperature: float = 0.7, max_tokens=None) -> str:
    """Convenience function for chat completion."""
    provider = get_llm_provider()
    return provider.chat_completion(messages, temperature, max_tokens)

def generate_text(prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
    """Convenience function for text generation."""
    provider = get_llm_provider()
    return provider.generate_text(prompt, system_prompt, temperature)

def generate_conversation_response(conversation_history, system_prompt: str = "", temperature: float = 0.7) -> str:
    """Convenience function for conversation responses."""
    provider = get_llm_provider()
    return provider.generate_conversation_response(conversation_history, system_prompt, temperature) 