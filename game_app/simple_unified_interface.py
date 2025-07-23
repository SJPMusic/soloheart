#!/usr/bin/env python3
"""
Simple Unified Interface for SoloHeart
Simplified character generator with step-by-step guided character creation.
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCharacterGenerator:
    """Simple character generator for step-by-step guided character creation with immediate fact commitment."""
    
    def __init__(self, playtest_mode: bool = None):
        self.conversation_history = []
        self.character_data = {
            "name": "Adventurer",
            "race": "Unknown",
            "class": "Unknown",
            "level": 1,
            "background": "Unknown",
            "alignment": "Neutral",
            "personality": "A brave adventurer",
            "ability_scores": {
                "strength": 10, "dexterity": 10, "constitution": 10,
                "intelligence": 10, "wisdom": 10, "charisma": 10
            },
            "hit_points": 10,
            "armor_class": 10,
            "saving_throws": [],
            "skills": [],
            "feats": [],
            "weapons": [],
            "gear": [],
            "spells": [],
            "background_freeform": "",
            "created_date": None
        }
        self.is_complete = False
        self.character_finalized = False
        self.in_review_mode = False
        self.confirmed_facts = set()
        self.narrative_bridge = None
        self.fact_history = []
        
        # Step-by-step creation tracking
        self.creation_steps = [
            "race", "class", "name", "background", "personality", "ability_scores"
        ]
        self.current_step_index = 0
        self.in_ability_score_assignment = False
        
        if playtest_mode is None:
            playtest_mode = os.environ.get('PLAYTEST_LOG', '0') == '1'
        self.playtest_mode = playtest_mode
    
    def _log(self, method, *args, **kwargs):
        # Logging disabled - removed playtest logger
        pass
    
    def _get_current_step(self) -> str:
        """Get the current step in character creation."""
        if self.current_step_index < len(self.creation_steps):
            return self.creation_steps[self.current_step_index]
        return "complete"
    
    def _get_next_step_prompt(self) -> str:
        """Generate the appropriate prompt for the current step."""
        current_step = self._get_current_step()
        
        if current_step == "race":
            return "What race would you like to be? Your options include: Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, and Tiefling. Each race has unique abilities and traits."
        
        elif current_step == "class":
            race = self.character_data.get("race", "Unknown")
            return f"Great! You're a {race}. What class would you like to be? Your options include: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, and Wizard. Each class has different abilities and playstyles."
        
        elif current_step == "name":
            race = self.character_data.get("race", "Unknown")
            char_class = self.character_data.get("class", "Unknown")
            return f"Perfect! You're a {race} {char_class}. What's your character's name?"
        
        elif current_step == "background":
            name = self.character_data.get("name", "Adventurer")
            race = self.character_data.get("race", "Unknown")
            char_class = self.character_data.get("class", "Unknown")
            return f"Excellent! {name} the {race} {char_class}. What background does your character have? Your options include: Acolyte, Criminal, Folk Hero, Noble, Sage, Soldier, or you can describe a custom background."
        
        elif current_step == "personality":
            name = self.character_data.get("name", "Adventurer")
            return f"Great! Now tell me about {name}'s personality. What are they like? Are they brave, cautious, friendly, mysterious, or something else? Describe their character and temperament."
        
        elif current_step == "ability_scores":
            name = self.character_data.get("name", "Adventurer")
            char_class = self.character_data.get("class", "Unknown")
            return f"Perfect! Now let's assign {name}'s ability scores. As a {char_class}, you'll want to focus on certain abilities. I can suggest scores based on your class, or you can choose your own method. Would you like me to suggest optimal scores for a {char_class}, or do you have a preference for how to assign them?"
        
        else:
            return "Character creation is complete! Let's review your character."
    
    def _extract_single_fact(self, user_input: str, step: str) -> Optional[str]:
        """Extract a single fact from user input for the current step."""
        user_input_lower = user_input.lower()
        logger.info(f"Extracting {step} from: '{user_input}'")
        
        if step == "race":
            races = ["human", "elf", "dwarf", "halfling", "dragonborn", "gnome", "half-elf", "half-orc", "tiefling"]
            for race in races:
                if race in user_input_lower:
                    return race.title()
        
        elif step == "class":
            classes = ["barbarian", "bard", "cleric", "druid", "fighter", "monk", "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard"]
            for char_class in classes:
                if char_class in user_input_lower:
                    return char_class.title()
        
        elif step == "name":
            # Extract name from various patterns
            name_patterns = [
                r"my name is ([a-z]+)", r"i'm called ([a-z]+)", r"call me ([a-z]+)",
                r"my character is named ([a-z]+)", r"name me ([a-z]+)",
                r"^i am ([a-z]+)$", r"^i'm ([a-z]+)$",
                r"my name's ([a-z]+)", r"i go by ([a-z]+)",
                r"my character is ([a-z]+)", r"([a-z]+) is my name",
                r"name is ([a-z]+)", r"called ([a-z]+)", r"named ([a-z]+)"
            ]
            for pattern in name_patterns:
                match = re.search(pattern, user_input_lower)
                if match:
                    return match.group(1).title()
        
        elif step == "background":
            backgrounds = ["acolyte", "criminal", "folk hero", "noble", "sage", "soldier"]
            for background in backgrounds:
                if background in user_input_lower:
                    return background.title()
        
        elif step == "personality":
            # For personality, we'll just return a summary of what was said
            return user_input.strip()
        
        return None
    
    def _commit_step_fact(self, step: str, value: str) -> None:
        """Commit a fact for the current step and advance to the next step."""
        # Store old value for undo functionality
        old_value = self.character_data.get(step)
        self.fact_history.append((step, old_value))
        
        # Update character data
        if step == "name":
            self.character_data["name"] = value
        elif step == "race":
            self.character_data["race"] = value
        elif step == "class":
            self.character_data["class"] = value
        elif step == "background":
            self.character_data["background"] = value
        elif step == "personality":
            self.character_data["personality"] = value
        elif step == "ability_scores":
            if isinstance(value, dict):
                self.character_data["ability_scores"] = value
        
        # Mark as confirmed and advance
        self.confirmed_facts.add(step)
        self.current_step_index += 1
        
        logger.info(f"Committed {step}: {value}")
    
    def _generate_ability_score_suggestions(self, char_class: str) -> Dict[str, int]:
        """Generate optimal ability scores for a given class."""
        suggestions = {
            "strength": 10, "dexterity": 10, "constitution": 10,
            "intelligence": 10, "wisdom": 10, "charisma": 10
        }
        
        # Class-specific optimizations
        if char_class.lower() == "fighter":
            suggestions.update({"strength": 15, "constitution": 14, "dexterity": 13})
        elif char_class.lower() == "wizard":
            suggestions.update({"intelligence": 15, "constitution": 14, "dexterity": 13})
        elif char_class.lower() == "rogue":
            suggestions.update({"dexterity": 15, "constitution": 14, "intelligence": 13})
        elif char_class.lower() == "cleric":
            suggestions.update({"wisdom": 15, "constitution": 14, "strength": 13})
        elif char_class.lower() == "barbarian":
            suggestions.update({"strength": 15, "constitution": 14, "dexterity": 13})
        elif char_class.lower() == "bard":
            suggestions.update({"charisma": 15, "dexterity": 14, "constitution": 13})
        elif char_class.lower() == "druid":
            suggestions.update({"wisdom": 15, "constitution": 14, "dexterity": 13})
        elif char_class.lower() == "monk":
            suggestions.update({"dexterity": 15, "wisdom": 14, "constitution": 13})
        elif char_class.lower() == "paladin":
            suggestions.update({"strength": 15, "charisma": 14, "constitution": 13})
        elif char_class.lower() == "ranger":
            suggestions.update({"dexterity": 15, "wisdom": 14, "constitution": 13})
        elif char_class.lower() == "sorcerer":
            suggestions.update({"charisma": 15, "constitution": 14, "dexterity": 13})
        elif char_class.lower() == "warlock":
            suggestions.update({"charisma": 15, "constitution": 14, "dexterity": 13})
        
        return suggestions
    
    def _get_step_confirmation(self, step: str, value: str) -> str:
        """Generate confirmation message for a committed fact."""
        if step == "race":
            return f"Excellent! You are a {value}."
        elif step == "class":
            race = self.character_data.get("race", "Unknown")
            return f"Perfect! You are a {race} {value}."
        elif step == "name":
            race = self.character_data.get("race", "Unknown")
            char_class = self.character_data.get("class", "Unknown")
            return f"Great! {value} the {race} {char_class}."
        elif step == "background":
            name = self.character_data.get("name", "Adventurer")
            return f"Wonderful! {name} has a {value} background."
        elif step == "personality":
            name = self.character_data.get("name", "Adventurer")
            return f"Perfect! {name} is {value}."
        else:
            return f"Great! {step} set to {value}."
    
    def _get_clarification_prompt(self, step: str, user_input: str) -> str:
        """Generate a clarification prompt when fact extraction fails."""
        if step == "race":
            return "I didn't catch that. Could you tell me what race you'd like to be? (Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, or Tiefling)"
        elif step == "class":
            return "I didn't catch that. Could you tell me what class you'd like to be? (Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, or Wizard)"
        elif step == "name":
            return "I didn't catch your character's name. Could you tell me what your character is called?"
        elif step == "background":
            return "I didn't catch that. Could you tell me what background your character has? (Acolyte, Criminal, Folk Hero, Noble, Sage, Soldier, or describe a custom one)"
        elif step == "personality":
            return "I didn't quite understand. Could you tell me more about your character's personality?"
        else:
            return "I didn't catch that. Could you clarify?"
    
    def _handle_ability_score_assignment(self, user_input: str) -> Dict[str, Any]:
        """Handle the ability score assignment step."""
        user_input_lower = user_input.lower()
        char_class = self.character_data.get("class", "Unknown")
        
        # Check if user wants suggestions
        if any(word in user_input_lower for word in ["suggest", "optimal", "recommend", "auto", "automatic"]):
            suggestions = self._generate_ability_score_suggestions(char_class)
            self.character_data["ability_scores"] = suggestions
            self.confirmed_facts.add("ability_scores")
            self.current_step_index += 1
            
            response = f"Perfect! I've assigned optimal ability scores for a {char_class}:\n\n"
            for ability, score in suggestions.items():
                response += f"• {ability.title()}: {score}\n"
            response += f"\n{self.get_character_summary()}\n\n🎯 **Character Creation Complete!**"
            
            return {"success": True, "message": response, "is_complete": True}
        
        # Check if user provided specific scores
        score_patterns = {
            "strength": r"str(?:ength)?[:\s]*(\d+)",
            "dexterity": r"dex(?:terity)?[:\s]*(\d+)",
            "constitution": r"con(?:stitution)?[:\s]*(\d+)",
            "intelligence": r"int(?:elligence)?[:\s]*(\d+)",
            "wisdom": r"wis(?:dom)?[:\s]*(\d+)",
            "charisma": r"cha(?:risma)?[:\s]*(\d+)"
        }
        
        scores = {}
        for ability, pattern in score_patterns.items():
            match = re.search(pattern, user_input_lower)
            if match:
                scores[ability] = int(match.group(1))
        
        if len(scores) >= 3:  # At least 3 scores provided
            # Fill in missing scores with 10s
            for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                if ability not in scores:
                    scores[ability] = 10
            
            self.character_data["ability_scores"] = scores
            self.confirmed_facts.add("ability_scores")
            self.current_step_index += 1
            
            response = f"Great! I've recorded your ability scores:\n\n"
            for ability, score in scores.items():
                response += f"• {ability.title()}: {score}\n"
            response += f"\n{self.get_character_summary()}\n\n🎯 **Character Creation Complete!**"
            
            return {"success": True, "message": response, "is_complete": True}
        
        # If no clear scores provided, ask for clarification
        return {
            "success": True,
            "message": "I can suggest optimal scores for your class, or you can provide specific scores. Would you like me to suggest optimal scores for a " + char_class + "?"
        }
    
    def start_character_creation(self, description: str, campaign_name: str = "") -> Dict[str, Any]:
        """Start character creation with initial description."""
        try:
            logger.info(f"Starting character creation: {description}")
            
            # Reset character data for new creation
            self.character_data = {
                "name": "Adventurer",
                "race": "Unknown",
                "class": "Unknown",
                "level": 1,
                "background": "Unknown",
                "alignment": "Neutral",
                "personality": "A brave adventurer",
                "ability_scores": {
                    "strength": 10, "dexterity": 10, "constitution": 10,
                    "intelligence": 10, "wisdom": 10, "charisma": 10
                },
                "hit_points": 10,
                "armor_class": 10,
                "saving_throws": [],
                "skills": [],
                "feats": [],
                "weapons": [],
                "gear": [],
                "spells": [],
                "background_freeform": "",
                "created_date": datetime.now().isoformat()
            }
            self.is_complete = False
            self.character_finalized = False
            self.in_review_mode = False
            self.confirmed_facts = set()
            self.fact_history = []
            self.current_step_index = 0
            self.conversation_history = []
            
            # Try to extract facts from initial description
            self._extract_initial_facts(description)
            
            # Advance step index based on confirmed facts
            self._advance_step_index()
            
            # Get the next step prompt
            current_step = self._get_current_step()
            if current_step == "complete":
                # All facts were extracted from description
                response = f"Excellent! I've created your character based on your description:\n\n{self.get_character_summary()}\n\n🎯 **Character Creation Complete!**"
                self.is_complete = True
            else:
                response = self._get_next_step_prompt()
            
            return {
                "success": True,
                "message": response,
                "is_complete": self.is_complete
            }
            
        except Exception as e:
            logger.error(f"Error starting character creation: {e}")
            return {
                "success": False,
                "message": f"Error starting character creation: {str(e)}"
            }
    
    def continue_conversation(self, user_input: str) -> Dict[str, Any]:
        """Continue character creation conversation."""
        try:
            logger.info(f"Continuing conversation: {user_input}")
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            current_step = self._get_current_step()
            
            if current_step == "complete":
                # Character is complete, enter review mode
                self.in_review_mode = True
                response = f"Your character is complete! Here's a summary:\n\n{self.get_character_summary()}\n\nWould you like to make any changes or finalize your character?"
                return {
                    "success": True,
                    "message": response,
                    "is_complete": True,
                    "in_review_mode": True
                }
            
            # Handle ability score assignment specially
            if current_step == "ability_scores":
                result = self._handle_ability_score_assignment(user_input)
                if result.get("is_complete"):
                    self.is_complete = True
                return result
            
            # Extract fact for current step
            extracted_value = self._extract_single_fact(user_input, current_step)
            
            if extracted_value:
                # Commit the fact
                self._commit_step_fact(current_step, extracted_value)
                
                # Get confirmation and next step
                confirmation = self._get_step_confirmation(current_step, extracted_value)
                next_step = self._get_current_step()
                
                if next_step == "complete":
                    # All steps completed
                    response = f"{confirmation}\n\n{self.get_character_summary()}\n\n🎯 **Character Creation Complete!**"
                    self.is_complete = True
                else:
                    next_prompt = self._get_next_step_prompt()
                    response = f"{confirmation}\n\n{next_prompt}"
                
                return {
                    "success": True,
                    "message": response,
                    "is_complete": self.is_complete
                }
            else:
                # Fact extraction failed, ask for clarification
                clarification = self._get_clarification_prompt(current_step, user_input)
                return {
                    "success": True,
                    "message": clarification,
                    "is_complete": False
                }
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return {
                "success": False,
                "message": f"Error continuing conversation: {str(e)}"
            }
    
    def _extract_initial_facts(self, user_input: str) -> None:
        """Extract facts from initial description without advancing step index."""
        user_input_lower = user_input.lower()
        
        # Check for race
        if "race" not in self.confirmed_facts:
            race_patterns = {
                "human": ["human"],
                "elf": ["elf", "elven", "elvish"],
                "dwarf": ["dwarf", "dwarven", "dwarvish"],
                "halfling": ["halfling", "hobbit"],
                "dragonborn": ["dragonborn", "dragon"],
                "gnome": ["gnome", "gnomish"],
                "half-elf": ["half-elf", "half elf"],
                "half-orc": ["half-orc", "half orc"],
                "tiefling": ["tiefling"]
            }
            
            for race, patterns in race_patterns.items():
                for pattern in patterns:
                    if pattern in user_input_lower:
                        self._commit_fact("race", race.title())
                        break
                if "race" in self.confirmed_facts:
                    break
        
        # Check for class
        if "class" not in self.confirmed_facts:
            classes = ["barbarian", "bard", "cleric", "druid", "fighter", "monk", "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard"]
            for char_class in classes:
                if char_class in user_input_lower:
                    self._commit_fact("class", char_class.title())
                    break
        
        # Check for name
        if "name" not in self.confirmed_facts:
            name_patterns = [
                r"my name is ([a-z]+)", r"i'm called ([a-z]+)", r"call me ([a-z]+)",
                r"my character is named ([a-z]+)", r"name me ([a-z]+)",
                r"^i am ([a-z]+)$", r"^i'm ([a-z]+)$",
                r"my name's ([a-z]+)", r"i go by ([a-z]+)",
                r"my character is ([a-z]+)", r"([a-z]+) is my name",
                r"name is ([a-z]+)", r"called ([a-z]+)", r"named ([a-z]+)"
            ]
            for pattern in name_patterns:
                match = re.search(pattern, user_input_lower)
                if match:
                    self._commit_fact("name", match.group(1).title())
                    break
        
        # Check for background
        if "background" not in self.confirmed_facts:
            backgrounds = ["acolyte", "criminal", "folk hero", "noble", "sage", "soldier"]
            for background in backgrounds:
                if background in user_input_lower:
                    self._commit_fact("background", background.title())
                    break
    
    def _detect_and_commit_facts(self, user_input: str, ai_response: str) -> None:
        """Detect and commit facts from user input during conversation."""
        user_input_lower = user_input.lower()
        
        # Define patterns for fact detection
        def match_patterns(fact_type, values, extra_patterns=None):
            patterns = []
            for value in values:
                patterns.append(rf"\b{value}\b")
            if extra_patterns:
                patterns.extend(extra_patterns)
            
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return True
            return False
        
        # Check for race
        if "race" not in self.confirmed_facts:
            race_patterns = {
                "human": ["human"],
                "elf": ["elf", "elven", "elvish"],
                "dwarf": ["dwarf", "dwarven", "dwarvish"],
                "halfling": ["halfling", "hobbit"],
                "dragonborn": ["dragonborn", "dragon"],
                "gnome": ["gnome", "gnomish"],
                "half-elf": ["half-elf", "half elf"],
                "half-orc": ["half-orc", "half orc"],
                "tiefling": ["tiefling"]
            }
            
            for race, patterns in race_patterns.items():
                for pattern in patterns:
                    if pattern in user_input_lower:
                        self._commit_step_fact("race", race.title())
                        break
                if race in self.confirmed_facts:
                    break
        
        # Check for class
        if "class" not in self.confirmed_facts:
            classes = ["barbarian", "bard", "cleric", "druid", "fighter", "monk", "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard"]
            if match_patterns("class", classes):
                for char_class in classes:
                    if char_class in user_input_lower:
                        self._commit_step_fact("class", char_class.title())
                        break
        
        # Check for name
        if "name" not in self.confirmed_facts:
            name_patterns = [
                r"my name is ([a-z]+)", r"i'm called ([a-z]+)", r"call me ([a-z]+)",
                r"my character is named ([a-z]+)", r"name me ([a-z]+)",
                r"^i am ([a-z]+)$", r"^i'm ([a-z]+)$",
                r"my name's ([a-z]+)", r"i go by ([a-z]+)",
                r"my character is ([a-z]+)", r"([a-z]+) is my name",
                r"name is ([a-z]+)", r"called ([a-z]+)", r"named ([a-z]+)"
            ]
            for pattern in name_patterns:
                match = re.search(pattern, user_input_lower)
                if match:
                    self._commit_step_fact("name", match.group(1).title())
                    break
        
        # Check for background
        if "background" not in self.confirmed_facts:
            backgrounds = ["acolyte", "criminal", "folk hero", "noble", "sage", "soldier"]
            if match_patterns("background", backgrounds):
                for background in backgrounds:
                    if background in user_input_lower:
                        self._commit_step_fact("background", background.title())
                        break
    
    def _commit_fact(self, fact_type: str, value: str, source: str = "player", allow_overwrite: bool = False) -> None:
        """Commit a fact to character data."""
        if fact_type in self.confirmed_facts and not allow_overwrite:
            logger.info(f"Fact {fact_type} already confirmed, skipping")
            return
        
        # Store old value for undo
        old_value = self.character_data.get(fact_type)
        self.fact_history.append((fact_type, old_value))
        
        # Update character data
        if fact_type == "name":
            self.character_data["name"] = value
        elif fact_type == "race":
            self.character_data["race"] = value
        elif fact_type == "class":
            self.character_data["class"] = value
        elif fact_type == "background":
            self.character_data["background"] = value
        elif fact_type == "personality":
            self.character_data["personality"] = value
        elif fact_type == "ability_scores":
            if isinstance(value, dict):
                self.character_data["ability_scores"] = value
        
        # Mark as confirmed
        self.confirmed_facts.add(fact_type)
        
        logger.info(f"Committed {fact_type}: {value} (source: {source})")
    
    def undo_last_fact(self) -> Optional[Tuple[str, str]]:
        """Undo the last committed fact."""
        if not self.fact_history:
            return None
        
        fact_type, old_value = self.fact_history.pop()
        
        # Restore old value
        if fact_type == "name":
            self.character_data["name"] = old_value
        elif fact_type == "race":
            self.character_data["race"] = old_value
        elif fact_type == "class":
            self.character_data["class"] = old_value
        elif fact_type == "background":
            self.character_data["background"] = old_value
        elif fact_type == "personality":
            self.character_data["personality"] = old_value
        elif fact_type == "ability_scores":
            if isinstance(old_value, dict):
                self.character_data["ability_scores"] = old_value
        
        # Remove from confirmed facts
        self.confirmed_facts.discard(fact_type)
        
        logger.info(f"Undid {fact_type}: {old_value}")
        return (fact_type, old_value)
    
    def _get_current_character_state(self, bullet_points: bool = False) -> str:
        """Get current character state as string."""
        if bullet_points:
            state = []
            for key, value in self.character_data.items():
                if key not in ["ability_scores", "saving_throws", "skills", "feats", "weapons", "gear", "spells"]:
                    state.append(f"• {key.title()}: {value}")
            
            # Add ability scores
            scores = self.character_data.get("ability_scores", {})
            if scores:
                score_str = ", ".join([f"{k.title()}: {v}" for k, v in scores.items()])
                state.append(f"• Ability Scores: {score_str}")
            
            return "\n".join(state)
        else:
            return json.dumps(self.character_data, indent=2)
    
    def _advance_step_index(self):
        """Advance step index based on confirmed facts."""
        while self.current_step_index < len(self.creation_steps):
            current_step = self.creation_steps[self.current_step_index]
            if current_step in self.confirmed_facts:
                self.current_step_index += 1
            else:
                break
    
    def _get_unknown_facts_list(self):
        """Get list of facts that still need to be determined."""
        all_facts = {"name", "race", "class", "background", "personality", "ability_scores"}
        return all_facts - self.confirmed_facts
    
    def is_character_complete(self) -> bool:
        """Check if character has all required information."""
        required_facts = {"name", "race", "class", "background", "personality", "ability_scores"}
        return required_facts.issubset(self.confirmed_facts)
    
    def get_character_summary(self) -> str:
        """Get a formatted summary of the character."""
        name = self.character_data.get("name", "Adventurer")
        race = self.character_data.get("race", "Unknown")
        char_class = self.character_data.get("class", "Unknown")
        background = self.character_data.get("background", "Unknown")
        personality = self.character_data.get("personality", "A brave adventurer")
        
        summary = f"**{name}**\n"
        summary += f"**{race} {char_class}**\n"
        summary += f"**Background:** {background}\n"
        summary += f"**Personality:** {personality}\n\n"
        
        # Add ability scores
        scores = self.character_data.get("ability_scores", {})
        if scores:
            summary += "**Ability Scores:**\n"
            for ability, score in scores.items():
                modifier = (score - 10) // 2
                modifier_str = f" (+{modifier})" if modifier >= 0 else f" ({modifier})"
                summary += f"• {ability.title()}: {score}{modifier_str}\n"
        
        return summary
    
    def apply_character_edit(self, message: str) -> Dict[str, Any]:
        """Apply edits to character in review mode."""
        try:
            if not self.in_review_mode:
                return {
                    "success": False,
                    "message": "Character is not in review mode"
                }
            
            message_lower = message.lower()
            
            # Check for specific edit patterns
            if "change name" in message_lower or "rename" in message_lower:
                # Extract new name
                name_match = re.search(r"(?:to|as) ([a-z]+)", message_lower)
                if name_match:
                    new_name = name_match.group(1).title()
                    old_name = self.character_data["name"]
                    self.character_data["name"] = new_name
                    return {
                        "success": True,
                        "message": f"Changed name from {old_name} to {new_name}",
                        "character_summary": self.get_character_summary()
                    }
            
            elif "change class" in message_lower or "change to" in message_lower:
                # Extract new class
                classes = ["barbarian", "bard", "cleric", "druid", "fighter", "monk", "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard"]
                for char_class in classes:
                    if char_class in message_lower:
                        old_class = self.character_data["class"]
                        self.character_data["class"] = char_class.title()
                        return {
                            "success": True,
                            "message": f"Changed class from {old_class} to {char_class.title()}",
                            "character_summary": self.get_character_summary()
                        }
            
            elif "change race" in message_lower:
                # Extract new race
                races = ["human", "elf", "dwarf", "halfling", "dragonborn", "gnome", "half-elf", "half-orc", "tiefling"]
                for race in races:
                    if race in message_lower:
                        old_race = self.character_data["race"]
                        self.character_data["race"] = race.title()
                        return {
                            "success": True,
                            "message": f"Changed race from {old_race} to {race.title()}",
                            "character_summary": self.get_character_summary()
                        }
            
            return {
                "success": False,
                "message": "I didn't understand that edit. Please be more specific about what you'd like to change."
            }
            
        except Exception as e:
            logger.error(f"Error applying character edit: {e}")
            return {
                "success": False,
                "message": f"Error applying edit: {str(e)}"
            }
    
    def finalize_character(self) -> Dict[str, Any]:
        """Finalize the character creation."""
        try:
            if not self.is_character_complete():
                return {
                    "success": False,
                    "message": "Character is not complete. Please finish character creation first."
                }
            
            self.character_finalized = True
            self.in_review_mode = False
            
            return {
                "success": True,
                "message": "Character finalized successfully!",
                "character_finalized": True,
                "character_data": self.character_data
            }
            
        except Exception as e:
            logger.error(f"Error finalizing character: {e}")
            return {
                "success": False,
                "message": f"Error finalizing character: {str(e)}"
            }
    
    def get_character_data(self) -> Dict[str, Any]:
        """Get the current character data."""
        return self.character_data.copy()
    
    def save_character(self, campaign_id: str):
        """Save character data to file."""
        try:
            filename = f"character_saves/{campaign_id}_character.json"
            with open(filename, 'w') as f:
                json.dump(self.character_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving character: {e}")
            return False

class SimpleNarrativeBridge:
    """Simple narrative bridge for campaign management."""
    
    def __init__(self):
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure necessary directories exist."""
        directories = ['campaign_saves', 'character_saves', 'logs']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def initialize_campaign(self, character_data: Dict[str, Any], campaign_name: str = None) -> Optional[Dict[str, Any]]:
        """Initialize a new campaign with character data."""
        try:
            campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            campaign_data = {
                'id': campaign_id,
                'name': campaign_name or 'New Campaign',
                'created_date': datetime.now().isoformat(),
                'character': character_data,
                'conversation_history': [],
                'world_state': {},
                'session_memory': []
            }
            
            # Save campaign
            filename = f"campaign_saves/{campaign_id}.json"
            with open(filename, 'w') as f:
                json.dump(campaign_data, f, indent=2)
            
            logger.info(f"Campaign initialized: {campaign_id}")
            return campaign_data
            
        except Exception as e:
            logger.error(f"Error initializing campaign: {e}")
            return None
    
    def generate_setting_introduction(self, character_data: Dict[str, Any], campaign_name: str) -> str:
        """Generate setting introduction for the campaign."""
        name = character_data.get("name", "Adventurer")
        race = character_data.get("race", "Unknown")
        char_class = character_data.get("class", "Unknown")
        background = character_data.get("background", "Unknown")
        
        introduction = f"Welcome to your adventure, {name}!\n\n"
        introduction += f"You are {name}, a {race} {char_class} with a {background} background. "
        introduction += f"Your journey begins in the mystical realm of Eldoria, a land of ancient magic and untold dangers.\n\n"
        introduction += f"As you step into this world, you feel the weight of destiny upon your shoulders. "
        introduction += f"Your skills and abilities will be tested, and your choices will shape the fate of this realm.\n\n"
        introduction += f"What would you like to do first?"
        
        return introduction
    
    def load_campaign(self, campaign_id: str) -> bool:
        """Load a campaign from file."""
        try:
            filename = f"campaign_saves/{campaign_id}.json"
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    campaign_data = json.load(f)
                return campaign_data
            else:
                return None
        except Exception as e:
            logger.error(f"Error loading campaign: {e}")
            return None
    
    def process_player_input(self, player_input: str, campaign_id: str) -> str:
        """Process player input and return DM response."""
        # Simple placeholder response
        return f"You say: '{player_input}'. As your Dungeon Master, I acknowledge your action and will respond accordingly."
    
    def save_campaign(self, campaign_id: str) -> bool:
        """Save campaign data to file."""
        try:
            # This would save the current campaign state
            return True
        except Exception as e:
            logger.error(f"Error saving campaign: {e}")
            return False
    
    def get_campaign_data(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign data."""
        return self.load_campaign(campaign_id) 