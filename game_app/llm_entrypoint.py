#!/usr/bin/env python3
"""
LLM Entrypoint for SoloHeart

Centralized LLM interface using the pluggable adapter system.
Replaces direct Ollama/OpenAI calls with unified adapter interface.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional

# Add the parent directory to the path to import from llm_adapters
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    from llm_adapters.llm_adapters import get_llm_client
    from llm_adapters.llm_adapters.config_loader import load_llm_config
    ADAPTER_AVAILABLE = True
except ImportError as e:
    ADAPTER_AVAILABLE = False
    logging.warning(f"LLM adapters not available: {e}")

logger = logging.getLogger(__name__)

# Global LLM client instance
_llm_client = None

def get_llm_client_instance():
    """
    Get the global LLM client instance.
    
    Returns:
        LLM client instance from the adapter system
    """
    global _llm_client
    
    if _llm_client is not None:
        return _llm_client
    
    if not ADAPTER_AVAILABLE:
        raise ImportError(
            "LLM adapters not available. "
            "Please ensure the llm_adapters package is installed."
        )
    
    try:
        # Load configuration
        config = load_llm_config()
        
        # Create LLM client
        _llm_client = get_llm_client(
            config["llm_backend"], 
            endpoint=config["llm_endpoint"]
        )
        
        logger.info(f"✅ Initialized SoloHeart LLM client: {config['llm_backend']} at {config['llm_endpoint']}")
        
        # Perform health check
        if _llm_client.health_check():
            logger.info("✅ SoloHeart LLM service health check passed")
        else:
            logger.warning("⚠️ SoloHeart LLM service health check failed - service may not be available")
        
        return _llm_client
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize SoloHeart LLM client: {e}")
        raise

def chat_completion(messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
    """
    Send a chat completion request using the adapter system.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum tokens to generate (optional)
    
    Returns:
        The assistant's response content as a string
    
    Raises:
        Exception: If LLM service is not available or request fails
    """
    try:
        client = get_llm_client_instance()
        
        # Prepare parameters
        params = {"temperature": temperature}
        if max_tokens:
            params["max_tokens"] = max_tokens
        
        # Make the request
        response = client.chat(messages, **params)
        
        logger.debug(f"✅ LLM response received: {response[:100]}...")
        return response
        
    except Exception as e:
        logger.error(f"❌ LLM chat completion failed: {e}")
        raise

def generate_text(prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
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
    
    return chat_completion(messages, temperature=temperature)

def generate_conversation_response(conversation_history: List[Dict[str, str]], system_prompt: str = "", temperature: float = 0.7) -> str:
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
    
    return chat_completion(messages, temperature=temperature)

def get_llm_metadata() -> Dict[str, Any]:
    """
    Get metadata about the current LLM client.
    
    Returns:
        Dictionary containing LLM client metadata
    """
    try:
        client = get_llm_client_instance()
        return client.get_metadata()
    except Exception as e:
        logger.error(f"❌ Failed to get LLM metadata: {e}")
        return {"error": str(e)}

def health_check() -> bool:
    """
    Check if the LLM service is healthy.
    
    Returns:
        True if healthy, False otherwise
    """
    try:
        client = get_llm_client_instance()
        return client.health_check()
    except Exception as e:
        logger.error(f"❌ LLM health check failed: {e}")
        return False

# Backward compatibility functions
def get_ollama_service():
    """
    Backward compatibility function for existing code.
    Returns the LLM client instance.
    """
    logger.warning("get_ollama_service() is deprecated - use get_llm_client_instance() instead")
    return get_llm_client_instance()

# Export the main functions
__all__ = [
    'get_llm_client_instance',
    'chat_completion',
    'generate_text',
    'generate_conversation_response',
    'get_llm_metadata',
    'health_check',
    'get_ollama_service'  # For backward compatibility
] 