"""
DnD 5E AI-Powered Game - AI DM Engine
====================================

Flexible AI DM engine that can dynamically interpret DnD 5e rules
"""

import openai
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import asdict

logger = logging.getLogger(__name__)

class AIDMEngine:
    """AI DM Engine that dynamically interprets DnD 5e rules"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key
        
        # Core DnD 5e knowledge base for context
        self.dnd_context = """
        You are an expert Dungeon Master for DnD 5e. You have deep knowledge of:
        - All official DnD 5e rules and mechanics
        - Monster Manual creatures and their stats
        - Player's Handbook classes, races, and abilities
        - Dungeon Master's Guide guidelines
        - Xanathar's Guide and other supplements
        
        You can dynamically:
        - Calculate appropriate DCs for any situation
        - Determine which skills apply to actions
        - Handle combat mechanics on the fly
        - Make rulings for edge cases
        - Adapt rules to fit the narrative
        
        Always explain your reasoning and show dice rolls when appropriate.
        """
    
    def process_action(self, player_action: str, character_info: Dict[str, Any] = None, 
                      campaign_context: str = None) -> str:
        """Process a player action with dynamic rule interpretation"""
        
        # Build context for the AI
        context = self._build_context(player_action, character_info, campaign_context)
        
        # Create the prompt
        prompt = f"""
{self.dnd_context}

Current Situation:
{campaign_context or "A typical DnD adventure"}

Player Character:
{self._format_character_info(character_info) if character_info else "Generic adventurer"}

Player Action: "{player_action}"

As the DM, interpret this action according to DnD 5e rules. Consider:
1. What skill checks or ability checks might be needed?
2. What's an appropriate DC for this situation?
3. Are there any special circumstances (advantage/disadvantage)?
4. What are the consequences of success or failure?

Respond as the DM, describing what happens and showing any necessary dice rolls.
Make your response engaging and narrative-focused while being mechanically accurate.
"""
        
        try:
            # Get AI response
            response = self._get_ai_response(prompt)
            return response
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return f"I'm having trouble processing that action right now. Could you try rephrasing?"
    
    def handle_combat_action(self, action: str, combat_state: Dict[str, Any] = None) -> str:
        """Handle combat actions dynamically"""
        
        context = f"""
{self.dnd_context}

Combat Situation:
{self._format_combat_state(combat_state) if combat_state else "Combat encounter in progress"}

Combat Action: "{action}"

As the DM, handle this combat action according to DnD 5e rules. Consider:
1. What type of action is this (attack, spell, movement, etc.)?
2. What are the appropriate mechanics?
3. What dice need to be rolled?
4. What are the results and consequences?

Show all dice rolls and explain the outcomes clearly.
"""
        
        try:
            response = self._get_ai_response(context)
            return response
        except Exception as e:
            logger.error(f"Error handling combat action: {e}")
            return f"I'm having trouble with that combat action. Could you clarify?"
    
    def make_ruling(self, situation: str, player_question: str = None) -> str:
        """Make a DM ruling on a complex situation"""
        
        prompt = f"""
{self.dnd_context}

Situation: {situation}

Player Question: {player_question or "How should this be handled?"}

As the DM, make a ruling on this situation. Consider:
1. What do the official rules say about this?
2. How can we adapt the rules to fit this specific situation?
3. What would be fair and fun for the players?
4. How can we keep the game moving?

Explain your reasoning and provide a clear ruling.
"""
        
        try:
            response = self._get_ai_response(prompt)
            return response
        except Exception as e:
            logger.error(f"Error making ruling: {e}")
            return f"I need to think about that ruling. Could you give me a moment?"
    
    def _build_context(self, action: str, character_info: Dict[str, Any], campaign_context: str) -> str:
        """Build context for AI processing"""
        context_parts = []
        
        if campaign_context:
            context_parts.append(f"Campaign Context: {campaign_context}")
        
        if character_info:
            context_parts.append(f"Character: {self._format_character_info(character_info)}")
        
        context_parts.append(f"Action: {action}")
        
        return "\n".join(context_parts)
    
    def _format_character_info(self, character_info: Dict[str, Any]) -> str:
        """Format character information for AI context"""
        if not character_info:
            return "Generic adventurer"
        
        parts = []
        
        # Basic info
        if 'name' in character_info:
            parts.append(f"Name: {character_info['name']}")
        if 'race' in character_info:
            parts.append(f"Race: {character_info['race']}")
        if 'class' in character_info:
            parts.append(f"Class: {character_info['class']}")
        if 'level' in character_info:
            parts.append(f"Level: {character_info['level']}")
        
        # Ability scores
        if 'ability_scores' in character_info:
            abilities = character_info['ability_scores']
            ability_str = ", ".join([f"{k}: {v}" for k, v in abilities.items()])
            parts.append(f"Ability Scores: {ability_str}")
        
        # Skills
        if 'skills' in character_info:
            skills = character_info['skills']
            skill_str = ", ".join([f"{k}: +{v}" for k, v in skills.items()])
            parts.append(f"Skills: {skill_str}")
        
        # Equipment
        if 'equipment' in character_info:
            parts.append(f"Equipment: {', '.join(character_info['equipment'])}")
        
        return "\n".join(parts)
    
    def _format_combat_state(self, combat_state: Dict[str, Any]) -> str:
        """Format combat state for AI context"""
        if not combat_state:
            return "Combat encounter in progress"
        
        parts = []
        
        if 'round' in combat_state:
            parts.append(f"Round: {combat_state['round']}")
        
        if 'current_turn' in combat_state:
            parts.append(f"Current Turn: {combat_state['current_turn']}")
        
        if 'combatants' in combat_state:
            combatants = []
            for name, data in combat_state['combatants'].items():
                hp = data.get('current_hit_points', '?')
                max_hp = data.get('max_hit_points', '?')
                ac = data.get('armor_class', '?')
                combatants.append(f"{name} (HP: {hp}/{max_hp}, AC: {ac})")
            parts.append(f"Combatants: {', '.join(combatants)}")
        
        return "\n".join(parts)
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get response from OpenAI API"""
        if not self.api_key:
            # Fallback response without API
            return self._fallback_response(prompt)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert DnD 5e Dungeon Master."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when API is not available"""
        # Simple keyword-based responses for testing
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['attack', 'hit', 'damage']):
            return "You make an attack! Roll a d20 and add your attack bonus. If you hit, roll damage dice."
        
        if any(word in prompt_lower for word in ['climb', 'jump', 'swim']):
            return "That's an Athletics check! Roll a d20 and add your Athletics modifier. The DC depends on the difficulty."
        
        if any(word in prompt_lower for word in ['sneak', 'hide', 'stealth']):
            return "You attempt to move stealthily. Roll a d20 and add your Stealth modifier. Others roll Perception to notice you."
        
        if any(word in prompt_lower for word in ['search', 'look', 'investigate']):
            return "You search the area. Roll a d20 and add your Investigation or Perception modifier."
        
        return "I understand your action. As the DM, I'll need to make a ruling on how to handle this according to DnD 5e rules."

# Global instance
ai_dm_engine = AIDMEngine() 