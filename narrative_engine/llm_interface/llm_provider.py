"""
Base LLM provider interface for The Narrative Engine.
Following Cursor's LLMProvider pattern but adapted for storytelling.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model_name: str = "llama3", temperature: float = 0.7, max_tokens: int = 500):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.is_available = False
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat completion response."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the LLM provider is available."""
        pass
    
    def generate_narrative_response(self, 
                                  user_input: str, 
                                  context: str = "", 
                                  memory_context: str = "") -> str:
        """Generate a narrative response with context and memory."""
        system_prompt = self._build_system_prompt(context, memory_context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = self.chat_completion(messages)
            logger.info(f"Generated narrative response: {response[:100]}...")
            return response
        except Exception as e:
            logger.error(f"Error generating narrative response: {e}")
            return self._fallback_response(user_input)
    
    def _build_system_prompt(self, context: str, memory_context: str) -> str:
        """Build the system prompt with context and memory."""
        prompt = """You are The Narrative Engine, a sophisticated AI that helps understand and work with narratives in any context.

Your role is to:
1. Help users understand the stories and patterns in their lives, work, relationships, or any domain
2. Track historical context and identify meaningful patterns over time
3. Interpret the deeper meaning in relationships, events, and changes
4. Suggest next actions that align with the established narrative and goals
5. Maintain continuity and coherence in understanding across conversations

You work with narratives broadly defined - the stories we tell ourselves and others to interpret our world. This includes:
- Business narratives (company evolution, value propositions, market positioning)
- Therapeutic narratives (client progress, relationship dynamics, personal growth)
- Personal narratives (life stories, identity, goals, relationships)
- Organizational narratives (culture, change, leadership, strategy)
- Any other context where understanding patterns and meaning is valuable

You are NOT limited to fiction or entertainment. You are a tool for understanding, interpreting, and working with real-world narratives.
"""
        
        if context:
            prompt += f"Current Context: {context}\n\n"
        
        if memory_context:
            prompt += f"Relevant Historical Context: {memory_context}\n\n"
        
        prompt += "Respond by helping the user understand patterns, interpret meaning, and consider aligned next steps based on the historical narrative context."
        
        return prompt
    
    def _fallback_response(self, user_input: str) -> str:
        """Provide a fallback response when LLM is unavailable."""
        fallback_responses = [
            "I understand. Please continue with your story.",
            "That's interesting. Tell me more about that.",
            "I see. How does this affect your journey?",
            "That's a significant development. What happens next?",
            "I'm processing that information. Please continue."
        ]
        
        import random
        return random.choice(fallback_responses) 