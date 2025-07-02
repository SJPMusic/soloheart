"""
DnD 5E AI-Powered Game - AI DM Engine
====================================

Flexible AI DM engine that can dynamically interpret DnD 5e rules
"""

import os
import json
import logging
import random
import re
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from dataclasses import asdict

logger = logging.getLogger(__name__)

class AIDMEngine:
    """AI DM Engine that dynamically interprets DnD 5e rules"""
    
    def __init__(self, api_key: str = None):
        try:
            # Import the Ollama service from the solo_heart module
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'solo_heart'))
            from ollama_llm_service import get_ollama_service
            self.ollama_service = get_ollama_service()
            logger.info("Ollama LLM service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama LLM service: {e}")
            self.ollama_service = None
            logger.warning("Using fallback responses due to Ollama service failure")
        
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
        """Get response from Ollama LLM service"""
        if not self.ollama_service:
            # Fallback response without API
            logger.warning("No Ollama service available - using fallback response")
            return self._fallback_response(prompt)
        
        try:
            # Create a system message for the DM role
            system_message = "You are an expert DnD 5e Dungeon Master. Respond as the DM, being helpful, engaging, and mechanically accurate."
            
            response = self.ollama_service.generate_response(
                prompt=prompt,
                system_message=system_message,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return self._fallback_response(prompt)
    
    def _parse_dice_roll(self, message: str) -> Optional[str]:
        """Parse all dice roll expressions and return formatted results"""
        # Regex pattern for DnD dice notation: (number)d(sides)(+/-modifier)
        dice_pattern = r'(\d*)d(\d+)([+-]\d+)?'
        matches = re.findall(dice_pattern, message.lower())
        if not matches:
            return None
        results = []
        for num_dice, dice_sides, modifier in matches:
            dice_sides = int(dice_sides)
            num_dice = int(num_dice) if num_dice else 1
            modifier_value = int(modifier) if modifier else 0
            if num_dice < 1 or num_dice > 100 or dice_sides < 1 or dice_sides > 1000:
                results.append("🎲 Invalid dice expression.")
                continue
            rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
            total = sum(rolls) + modifier_value
            if num_dice == 1:
                if modifier_value == 0:
                    results.append(f"🎲 Rolling 1d{dice_sides}: [{rolls[0]}] = {rolls[0]}")
                else:
                    modifier_str = f"+{modifier_value}" if modifier_value > 0 else str(modifier_value)
                    results.append(f"🎲 Rolling 1d{dice_sides}{modifier_str}: [{rolls[0]}] {modifier_str} = {total}")
            else:
                if modifier_value == 0:
                    results.append(f"🎲 Rolling {num_dice}d{dice_sides}: {rolls} = {total}")
                else:
                    modifier_str = f"+{modifier_value}" if modifier_value > 0 else str(modifier_value)
                    results.append(f"🎲 Rolling {num_dice}d{dice_sides}{modifier_str}: {rolls} {modifier_str} = {total}")
        return "\n".join(results)

    def _fallback_response(self, prompt: str) -> dict:
        """Fallback response when API is not available"""
        dice_result = self._parse_dice_roll(prompt)
        prompt_lower = prompt.lower()
        narrative = None
        # Greeting responses (check these first)
        if any(word in prompt_lower for word in ['hello', 'hi', 'greetings']):
            narrative = "Greetings, brave adventurer! I am your AI Dungeon Master, ready to guide you through epic tales of valor and danger. What adventure shall we embark upon today?"
        elif any(word in prompt_lower for word in ['help', 'what can', 'how do']):
            narrative = "I'm your Dungeon Master! I can help you with character creation, combat, skill checks, spellcasting, and guiding your adventure. What would you like to do? You can ask me to roll dice, create a character, start an adventure, or help with any DnD rules."
        elif any(word in prompt_lower for word in ['initiative']):
            narrative = "Roll initiative! Everyone roll a d20 and add your Dexterity modifier. The highest goes first, then we proceed in order. Let me know your results!"
        elif any(word in prompt_lower for word in ['attack', 'hit', 'damage', 'fight']):
            narrative = "Combat begins! Roll initiative (d20 + your Dexterity modifier) to determine turn order. When you attack, roll a d20 and add your attack bonus. If you hit, roll your weapon's damage dice!"
        elif any(word in prompt_lower for word in ['create', 'character', 'new character']):
            narrative = "Excellent! Let's create your character. What race would you like to play? The classic options are Human, Elf, Dwarf, Halfling, Dragonborn, Tiefling, and many more. Or would you prefer something more exotic?"
        elif any(word in prompt_lower for word in ['wizard', 'sorcerer', 'warlock']):
            narrative = "A spellcaster! Excellent choice. Wizards are masters of arcane magic, Sorcerers have innate magical power, and Warlocks make pacts with powerful beings. Which appeals to you most?"
        elif any(word in prompt_lower for word in ['fighter', 'barbarian', 'paladin']):
            narrative = "A warrior! Fighters are versatile combatants, Barbarians are fierce berserkers, and Paladins are holy warriors. What fighting style interests you?"
        elif any(word in prompt_lower for word in ['rogue', 'ranger', 'monk']):
            narrative = "A skilled specialist! Rogues are masters of stealth and precision, Rangers are wilderness experts, and Monks channel inner power. Which path calls to you?"
        elif any(word in prompt_lower for word in ['cleric', 'druid', 'bard']):
            narrative = "A divine or artistic soul! Clerics channel divine power, Druids commune with nature, and Bards inspire through music and magic. What draws you to this path?"
        elif any(word in prompt_lower for word in ['start', 'adventure', 'begin', 'quest']):
            narrative = "Adventure awaits! You find yourself in a bustling tavern in the town of Neverwinter. A mysterious figure approaches your table with a proposition. 'I have a job that requires someone of your... particular skills,' they whisper. What do you do?"
        elif any(word in prompt_lower for word in ['dungeon', 'cave', 'ruins']):
            narrative = "You stand before ancient stone doors carved with mysterious runes. The air is thick with the scent of earth and something... older. Your torch flickers, casting dancing shadows. What's your next move?"
        elif any(word in prompt_lower for word in ['climb', 'jump', 'swim', 'athletics']):
            narrative = "That's an Athletics check! Roll a d20 and add your Athletics modifier. The DC depends on the difficulty - easy (5), moderate (10), hard (15), very hard (20), or nearly impossible (25)."
        elif any(word in prompt_lower for word in ['sneak', 'hide', 'stealth', 'sneak']):
            narrative = "You attempt to move stealthily. Roll a d20 and add your Stealth modifier. Anyone who might notice you rolls Perception to oppose your roll."
        elif any(word in prompt_lower for word in ['search', 'look', 'investigate', 'perception']):
            narrative = "You search the area carefully. Roll a d20 and add your Investigation or Perception modifier. The higher you roll, the more you'll discover!"
        elif any(word in prompt_lower for word in ['persuade', 'deceive', 'intimidate']):
            narrative = "You attempt to influence someone. Roll a d20 and add your Charisma modifier (Persuasion, Deception, or Intimidation). The target's attitude and the difficulty of the request affect the DC."
        elif any(word in prompt_lower for word in ['spell', 'magic', 'cast']):
            narrative = "You channel magical energy! Tell me which spell you want to cast, and I'll guide you through the process. Remember to check your spell slots and components!"
        elif any(word in prompt_lower for word in ['roll', 'dice', 'd20', 'd6']):
            narrative = "Time to roll the dice! What are you trying to accomplish? I'll tell you which dice to roll and what modifiers to add."
        if dice_result:
            if narrative:
                return {"response": f"{dice_result}\n{narrative}"}
            else:
                return {"response": dice_result}
        if narrative:
            return {"response": narrative}
        return {"response": "I understand you want to do something interesting! As your Dungeon Master, I'm here to help. Could you tell me more specifically what you're trying to accomplish? Are you looking to make an attack, cast a spell, use a skill, or something else entirely?"}

    def generate_response(self, message: str, context: str = None) -> str:
        """Generate a DM response for chat interface"""
        # Build context for the AI
        full_context = self.dnd_context
        
        if context:
            full_context += f"\n\nCurrent Context:\n{context}"
        
        # Create the prompt
        prompt = f"""
{full_context}

Player Message: "{message}"

As the DM, respond to the player's message. Consider:
1. What they're asking or trying to do
2. How to guide them through DnD 5e rules if needed
3. How to maintain narrative flow and engagement
4. Whether any dice rolls or checks are needed

Respond as the DM, being helpful, engaging, and mechanically accurate.
"""
        
        try:
            # Get AI response
            response = self._get_ai_response(prompt)
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I'm having trouble responding right now. Could you try rephrasing your message?"

# Global instance
ai_dm_engine = AIDMEngine() 