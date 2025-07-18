"""
LLM interface module for The Narrative Engine.
Provides abstraction layer for different LLM providers.
"""

from .ollama_provider import OllamaProvider
from .llm_provider import LLMProvider

__all__ = ['OllamaProvider', 'LLMProvider'] 