#!/usr/bin/env python3
"""
SRD 5.2 Compliance Checker for SoloHeart Character Creation

This module ensures that all character data meets SRD 5.2 requirements
before allowing entry into Narrative Mode.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RequirementLevel(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

@dataclass
class Requirement:
    field: str
    level: RequirementLevel
    description: str
    srd_reference: str
    validation_func: callable = None

@dataclass
class PriorityField:
    """Represents a field that needs to be completed with priority information."""
    field: str
    level: RequirementLevel
    description: str
    priority_score: float
    natural_language_prompt: str
    is_urgent: bool = False

class IntelligentPriorityEngine:
    """
    Intelligent prioritization engine that determines the most critical missing fields
    and generates natural language prompts to guide character creation.
    """
    
    def __init__(self):
        self.field_prompts = {
            # Core Identity - Critical
            "name": "What's your character's name?",
            "race": "What race is your character? (Human, Elf, Dwarf, etc.)",
            "class": "What class is your character? (Fighter, Wizard, etc.)",
            
            # Ability Scores - Critical
            "ability_scores": "Let's determine your character's ability scores. What method would you prefer?",
            "strength": "How strong is your character?",
            "dexterity": "How agile and coordinated is your character?",
            "constitution": "How hardy and resilient is your character?",
            "intelligence": "How smart and knowledgeable is your character?",
            "wisdom": "How perceptive and insightful is your character?",
            "charisma": "How charismatic and persuasive is your character?",
            
            # High Priority
            "background": "What's your character's background? (Acolyte, Soldier, etc.)",
            "alignment": "What's your character's moral alignment?",
            "age": "How old is your character?",
            "gender": "What's your character's gender?",
            "skill_proficiencies": "What skills is your character proficient in?",
            "languages": "What languages does your character know?",
            "equipment": "What equipment does your character carry?",
            "weapons": "What weapons does your character use?",
            "armor": "What armor does your character wear?",
            
            # Medium Priority
            "personality_traits": "What are your character's personality traits?",
            "ideals": "What ideals does your character believe in?",
            "bonds": "What bonds connect your character to others?",
            "flaws": "What flaws does your character have?",
            "motivations": "What motivates your character?",
            "backstory": "What's your character's backstory?",
            "combat_approach": "How does your character approach combat?",
            "spells": "What spells does your character know?",
            "class_features": "What special abilities does your character have?",
            
            # Low Priority
            "physical_appearance": "What does your character look like?",
            "emotional_themes": "What emotional themes define your character?",
            "traumas": "What past traumas has your character experienced?",
            "relationships": "What relationships are important to your character?",
            "additional_traits": "What other traits define your character?"
        }
        
        # Field dependencies - some fields depend on others
        self.field_dependencies = {
            "spells": ["class"],  # Spells depend on class
            "class_features": ["class"],  # Class features depend on class
            "racial_features": ["race"],  # Racial features depend on race
            "subrace": ["race"],  # Subrace depends on race
        }
        
        # Priority weights for different levels
        self.level_weights = {
            RequirementLevel.CRITICAL: 1.0,
            RequirementLevel.HIGH: 0.7,
            RequirementLevel.MEDIUM: 0.4,
            RequirementLevel.LOW: 0.1
        }
    
    def get_next_priority_fields(self, character_data: Dict[str, Any], max_fields: int = 2) -> List[PriorityField]:
        """
        Get the next highest priority fields that need to be completed.
        
        Args:
            character_data: Current character data
            max_fields: Maximum number of fields to return
            
        Returns:
            List of PriorityField objects ranked by priority
        """
        try:
            # Get completeness analysis
            completeness_result = srd_checker.check_character_completeness(character_data)
            
            # If character is over 90% complete, focus on clarification
            if completeness_result['completion_percentage'] >= 90:
                return self._get_clarification_fields(character_data, max_fields)
            
            # Build priority fields list
            priority_fields = []
            
            # Process missing fields by level
            for level in RequirementLevel:
                missing_fields = [f for f in completeness_result['missing_fields'] 
                               if f['level'] == level.value]
                
                for field_info in missing_fields:
                    field_name = field_info['field']
                    
                    # Check if field dependencies are met
                    if self._are_dependencies_met(field_name, character_data):
                        priority_score = self._calculate_priority_score(
                            field_name, level, character_data, completeness_result
                        )
                        
                        natural_prompt = self._generate_natural_prompt(
                            field_name, character_data, completeness_result
                        )
                        
                        priority_field = PriorityField(
                            field=field_name,
                            level=level,
                            description=field_info['description'],
                            priority_score=priority_score,
                            natural_language_prompt=natural_prompt,
                            is_urgent=(level == RequirementLevel.CRITICAL)
                        )
                        
                        priority_fields.append(priority_field)
            
            # Sort by priority score (highest first) and return top fields
            priority_fields.sort(key=lambda x: x.priority_score, reverse=True)
            return priority_fields[:max_fields]
            
        except Exception as e:
            logger.error(f"Error getting priority fields: {e}")
            return []
    
    def _are_dependencies_met(self, field_name: str, character_data: Dict[str, Any]) -> bool:
        """Check if field dependencies are met."""
        if field_name not in self.field_dependencies:
            return True
        
        dependencies = self.field_dependencies[field_name]
        for dep in dependencies:
            if not character_data.get(dep):
                return False
        
        return True
    
    def _calculate_priority_score(self, field_name: str, level: RequirementLevel, 
                                character_data: Dict[str, Any], 
                                completeness_result: Dict[str, Any]) -> float:
        """Calculate priority score for a field."""
        base_score = self.level_weights[level]
        
        # Boost score for critical fields
        if level == RequirementLevel.CRITICAL:
            base_score *= 1.5
        
        # Boost score if this is one of the few remaining fields at this level
        level_missing = [f for f in completeness_result['missing_fields'] 
                        if f['level'] == level.value]
        if len(level_missing) <= 2:
            base_score *= 1.2
        
        # Reduce score if field has dependencies that aren't met
        if not self._are_dependencies_met(field_name, character_data):
            base_score *= 0.5
        
        # Boost score for fields that unlock other fields
        if field_name in ["class", "race"]:
            base_score *= 1.3
        
        return base_score
    
    def _generate_natural_prompt(self, field_name: str, character_data: Dict[str, Any], 
                                completeness_result: Dict[str, Any]) -> str:
        """Generate a natural language prompt for a field."""
        base_prompt = self.field_prompts.get(field_name, f"What's your character's {field_name}?")
        
        # Customize prompt based on context
        if field_name == "class":
            if character_data.get('race'):
                base_prompt = f"You're a {character_data['race']}. What class are you becoming?"
            else:
                base_prompt = "What kind of hero are you becoming? (Fighter, Wizard, etc.)"
        
        elif field_name == "race":
            if character_data.get('name'):
                base_prompt = f"What race is {character_data['name']}?"
            else:
                base_prompt = "What race is your character? (Human, Elf, Dwarf, etc.)"
        
        elif field_name == "ability_scores":
            if character_data.get('class'):
                base_prompt = f"As a {character_data['class']}, let's determine your ability scores. What method would you prefer?"
            else:
                base_prompt = "Let's determine your character's ability scores. What method would you prefer?"
        
        elif field_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            if character_data.get('class'):
                base_prompt = f"As a {character_data['class']}, how {field_name.lower()} is your character?"
            else:
                base_prompt = f"How {field_name.lower()} is your character?"
        
        # Add urgency indicator for critical fields
        if field_name in ["name", "race", "class"]:
            base_prompt += " (This is needed to continue)"
        
        return base_prompt
    
    def _get_clarification_fields(self, character_data: Dict[str, Any], max_fields: int) -> List[PriorityField]:
        """Get fields that need clarification when character is mostly complete."""
        clarification_fields = []
        
        # Check for fields that might need clarification
        fields_to_check = [
            ("alignment", "alignment"),
            ("background", "background"),
            ("age", "age"),
            ("gender", "gender")
        ]
        
        for field_name, field_key in fields_to_check:
            value = character_data.get(field_key)
            if value and isinstance(value, str) and len(value.strip()) < 3:
                # Field exists but might need clarification
                clarification_fields.append(PriorityField(
                    field=field_name,
                    level=RequirementLevel.MEDIUM,
                    description=f"Clarify {field_name}",
                    priority_score=0.3,
                    natural_language_prompt=f"Can you tell me more about your character's {field_name}?",
                    is_urgent=False
                ))
        
        return clarification_fields[:max_fields]
    
    def generate_steering_prompt(self, character_data: Dict[str, Any]) -> str:
        """
        Generate a steering prompt that guides the AI to focus on the most critical missing fields.
        
        Returns:
            Natural language prompt for the AI to use in conversation
        """
        try:
            priority_fields = self.get_next_priority_fields(character_data, max_fields=2)
            
            if not priority_fields:
                return "Your character is looking great! Let's continue developing their story."
            
            # Build steering context
            steering_parts = []
            
            for field in priority_fields:
                if field.is_urgent:
                    steering_parts.append(f"URGENT: {field.natural_language_prompt}")
                else:
                    steering_parts.append(field.natural_language_prompt)
            
            # Add context about completion status
            completeness_result = srd_checker.check_character_completeness(character_data)
            completion_percent = completeness_result['completion_percentage']
            
            if completion_percent < 50:
                steering_parts.append("Focus on the most critical information first.")
            elif completion_percent < 80:
                steering_parts.append("We're making good progress. Let's fill in the remaining details.")
            else:
                steering_parts.append("We're almost done! Just a few more details to complete your character.")
            
            return " | ".join(steering_parts)
            
        except Exception as e:
            logger.error(f"Error generating steering prompt: {e}")
            return "Tell me more about your character."

# Global instance of the priority engine
priority_engine = IntelligentPriorityEngine()

class SRDComplianceChecker:
    """Ensures character data meets SRD 5.2 requirements."""
    
    def __init__(self):
        self.requirements = self._initialize_requirements()
        
    def _initialize_requirements(self) -> List[Requirement]:
        """Initialize all SRD 5.2 requirements."""
        return [
            # Core Identity - Critical
            Requirement("name", RequirementLevel.CRITICAL, 
                      "Character name", "SRD 5.2 - Character Creation"),
            Requirement("race", RequirementLevel.CRITICAL, 
                      "Character race (Human, Elf, Dwarf, etc.)", "SRD 5.2 - Races"),
            Requirement("class", RequirementLevel.CRITICAL, 
                      "Character class (Fighter, Wizard, etc.)", "SRD 5.2 - Classes"),
            
            # Ability Scores - Critical
            Requirement("ability_scores", RequirementLevel.CRITICAL,
                      "All six ability scores", "SRD 5.2 - Ability Scores"),
            Requirement("strength", RequirementLevel.CRITICAL,
                      "Strength ability score", "SRD 5.2 - Ability Scores"),
            Requirement("dexterity", RequirementLevel.CRITICAL,
                      "Dexterity ability score", "SRD 5.2 - Ability Scores"),
            Requirement("constitution", RequirementLevel.CRITICAL,
                      "Constitution ability score", "SRD 5.2 - Ability Scores"),
            Requirement("intelligence", RequirementLevel.CRITICAL,
                      "Intelligence ability score", "SRD 5.2 - Ability Scores"),
            Requirement("wisdom", RequirementLevel.CRITICAL,
                      "Wisdom ability score", "SRD 5.2 - Ability Scores"),
            Requirement("charisma", RequirementLevel.CRITICAL,
                      "Charisma ability score", "SRD 5.2 - Ability Scores"),
            
            # High Priority
            Requirement("background", RequirementLevel.HIGH,
                      "Character background", "SRD 5.2 - Backgrounds"),
            Requirement("alignment", RequirementLevel.HIGH,
                      "Character alignment", "SRD 5.2 - Alignment"),
            Requirement("age", RequirementLevel.HIGH,
                      "Character age", "SRD 5.2 - Character Creation"),
            Requirement("gender", RequirementLevel.HIGH,
                      "Character gender", "SRD 5.2 - Character Creation"),
            Requirement("skill_proficiencies", RequirementLevel.HIGH,
                      "Skill and tool proficiencies", "SRD 5.2 - Skills"),
            Requirement("languages", RequirementLevel.HIGH,
                      "Languages known", "SRD 5.2 - Languages"),
            Requirement("equipment", RequirementLevel.HIGH,
                      "Character equipment and gear", "SRD 5.2 - Equipment"),
            Requirement("weapons", RequirementLevel.HIGH,
                      "Weapons carried", "SRD 5.2 - Weapons"),
            Requirement("armor", RequirementLevel.HIGH,
                      "Armor worn", "SRD 5.2 - Armor"),
            
            # Medium Priority
            Requirement("personality_traits", RequirementLevel.MEDIUM,
                      "Character personality traits", "SRD 5.2 - Backgrounds"),
            Requirement("ideals", RequirementLevel.MEDIUM,
                      "Character ideals", "SRD 5.2 - Backgrounds"),
            Requirement("bonds", RequirementLevel.MEDIUM,
                      "Character bonds", "SRD 5.2 - Backgrounds"),
            Requirement("flaws", RequirementLevel.MEDIUM,
                      "Character flaws", "SRD 5.2 - Backgrounds"),
            Requirement("motivations", RequirementLevel.MEDIUM,
                      "Character motivations", "SRD 5.2 - Character Creation"),
            Requirement("backstory", RequirementLevel.MEDIUM,
                      "Character backstory", "SRD 5.2 - Character Creation"),
            Requirement("combat_approach", RequirementLevel.MEDIUM,
                      "Preferred combat approach", "SRD 5.2 - Combat"),
            Requirement("spells", RequirementLevel.MEDIUM,
                      "Spells known/prepared", "SRD 5.2 - Spellcasting"),
            Requirement("class_features", RequirementLevel.MEDIUM,
                      "Class and racial features", "SRD 5.2 - Classes"),
            
            # Low Priority
            Requirement("physical_appearance", RequirementLevel.LOW,
                      "Physical appearance", "SRD 5.2 - Character Creation"),
            Requirement("emotional_themes", RequirementLevel.LOW,
                      "Emotional themes and trauma", "SRD 5.2 - Character Creation"),
            Requirement("traumas", RequirementLevel.LOW,
                      "Past traumas and experiences", "SRD 5.2 - Character Creation"),
            Requirement("relationships", RequirementLevel.LOW,
                      "Relationships and connections", "SRD 5.2 - Character Creation"),
            Requirement("additional_traits", RequirementLevel.LOW,
                      "Additional character traits", "SRD 5.2 - Character Creation"),
        ]
    
    def check_character_completeness(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if character meets SRD 5.2 requirements.
        
        Returns:
            Dict with 'is_complete', 'missing_fields', and 'completion_percentage'
        """
        missing_fields = []
        completion_by_level = {level: [] for level in RequirementLevel}
        
        for req in self.requirements:
            value = character_data.get(req.field)
            
            # Check if field is missing or invalid
            if self._is_field_missing(value, req):
                missing_fields.append({
                    'field': req.field,
                    'level': req.level.value,
                    'description': req.description,
                    'srd_reference': req.srd_reference
                })
                completion_by_level[req.level].append(req.field)
        
        # Calculate completion percentage
        total_fields = len(self.requirements)
        completed_fields = total_fields - len(missing_fields)
        completion_percentage = (completed_fields / total_fields) * 100
        
        # Determine if character is ready for narrative mode
        critical_missing = [f for f in missing_fields if f['level'] == RequirementLevel.CRITICAL.value]
        is_complete = len(critical_missing) == 0
        
        return {
            'is_complete': is_complete,
            'missing_fields': missing_fields,
            'completion_percentage': completion_percentage,
            'completion_by_level': completion_by_level,
            'critical_missing': critical_missing,
            'high_missing': [f for f in missing_fields if f['level'] == RequirementLevel.HIGH.value],
            'medium_missing': [f for f in missing_fields if f['level'] == RequirementLevel.MEDIUM.value],
            'low_missing': [f for f in missing_fields if f['level'] == RequirementLevel.LOW.value]
        }
    
    def get_next_priority_fields(self, character_data: Dict[str, Any], max_fields: int = 2) -> List[PriorityField]:
        """
        Get the next highest priority fields that need to be completed.
        
        Args:
            character_data: Current character data
            max_fields: Maximum number of fields to return
            
        Returns:
            List of PriorityField objects ranked by priority
        """
        # Handle None or invalid character_data
        if character_data is None or not isinstance(character_data, dict):
            return []
        
        return priority_engine.get_next_priority_fields(character_data, max_fields)
    
    def generate_steering_prompt(self, character_data: Dict[str, Any]) -> str:
        """
        Generate a steering prompt that guides the AI to focus on the most critical missing fields.
        
        Returns:
            Natural language prompt for the AI to use in conversation
        """
        # Handle None or invalid character_data
        if character_data is None or not isinstance(character_data, dict):
            return "Tell me more about your character."
        
        return priority_engine.generate_steering_prompt(character_data)
    
    def _is_field_missing(self, value: Any, requirement: Requirement) -> bool:
        """Check if a field is missing or invalid."""
        if value is None:
            return True
        
        # Special handling for different field types
        if requirement.field == "ability_scores":
            return not self._validate_ability_scores(value)
        elif requirement.field in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            return not self._validate_ability_score(value)
        elif requirement.field in ["skill_proficiencies", "languages", "equipment", "weapons", "armor"]:
            return not self._validate_list_field(value)
        elif requirement.field in ["personality_traits", "ideals", "bonds", "flaws", "motivations"]:
            return not self._validate_list_field(value)
        elif requirement.field == "spells":
            return not self._validate_spells_field(value, requirement)
        
        # Default validation
        return value is None or value == ""
    
    def _validate_ability_scores(self, scores: Dict[str, int]) -> bool:
        """Validate that all ability scores are present and valid."""
        if not isinstance(scores, dict):
            return False
        
        required_scores = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for score_name in required_scores:
            if score_name not in scores or not self._validate_ability_score(scores[score_name]):
                return False
        
        return True
    
    def _validate_ability_score(self, score: int) -> bool:
        """Validate that an ability score is within valid range."""
        return isinstance(score, int) and 1 <= score <= 20
    
    def _validate_list_field(self, value: Any) -> bool:
        """Validate that a list field has at least one item."""
        return isinstance(value, list) and len(value) > 0
    
    def _validate_spells_field(self, spells: Any, requirement: Requirement) -> bool:
        """Validate spells field - only required for spellcasting classes."""
        # If character has a spellcasting class, spells should be present
        # This is a simplified check - in practice, you'd check the character's class
        return True  # For now, always return True
    
    def get_missing_fields_summary(self, character_data: Dict[str, Any]) -> str:
        """Get a human-readable summary of missing fields."""
        result = self.check_character_completeness(character_data)
        
        if result['is_complete']:
            return "Character sheet is complete and ready for narrative mode!"
        
        summary_parts = []
        
        for level in RequirementLevel:
            missing = [f for f in result['missing_fields'] if f['level'] == level.value]
            if missing:
                summary_parts.append(f"{level.value}: {', '.join([f['description'] for f in missing])}")
        
        return "; ".join(summary_parts)
    
    def get_completion_priority(self, character_data: Dict[str, Any]) -> List[str]:
        """Get prioritized list of fields to complete."""
        result = self.check_character_completeness(character_data)
        
        priority_fields = []
        
        # Critical fields first
        for field in result['critical_missing']:
            priority_fields.append(f"Critical: {field['description']}")
        
        # High priority fields
        for field in result['high_missing']:
            priority_fields.append(f"High: {field['description']}")
        
        # Medium priority fields
        for field in result['medium_missing']:
            priority_fields.append(f"Medium: {field['description']}")
        
        # Low priority fields
        for field in result['low_missing']:
            priority_fields.append(f"Low: {field['description']}")
        
        return priority_fields
    
    def validate_srd_compliance(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that character data is SRD 5.2 compliant."""
        compliance_issues = []
        
        # Validate race
        if character_data.get('race'):
            if not self._is_valid_srd_race(character_data['race']):
                compliance_issues.append(f"Race '{character_data['race']}' is not SRD 5.2 compliant")
        
        # Validate class
        if character_data.get('class'):
            if not self._is_valid_srd_class(character_data['class']):
                compliance_issues.append(f"Class '{character_data['class']}' is not SRD 5.2 compliant")
        
        # Validate background
        if character_data.get('background'):
            if not self._is_valid_srd_background(character_data['background']):
                compliance_issues.append(f"Background '{character_data['background']}' is not SRD 5.2 compliant")
        
        # Validate ability scores
        if character_data.get('ability_scores'):
            score_issues = self._validate_ability_score_compliance(character_data['ability_scores'])
            compliance_issues.extend(score_issues)
        
        return {
            'is_srd_compliant': len(compliance_issues) == 0,
            'compliance_issues': compliance_issues
        }
    
    def _is_valid_srd_race(self, race: str) -> bool:
        """Check if race is SRD 5.2 compliant."""
        srd_races = [
            "Human", "Elf", "Dwarf", "Halfling", "Dragonborn", 
            "Gnome", "Half-Elf", "Half-Orc", "Tiefling"
        ]
        return race in srd_races
    
    def _is_valid_srd_class(self, class_name: str) -> bool:
        """Check if class is SRD 5.2 compliant."""
        srd_classes = [
            "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
            "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer",
            "Warlock", "Wizard"
        ]
        return class_name in srd_classes
    
    def _is_valid_srd_background(self, background: str) -> bool:
        """Check if background is SRD 5.2 compliant."""
        srd_backgrounds = [
            "Acolyte", "Criminal", "Folk Hero", "Noble", "Sage",
            "Soldier", "Urchin", "Charlatan", "Entertainer", "Guild Artisan",
            "Hermit", "Outlander", "Soldier", "Urchin"
        ]
        return background in srd_backgrounds
    
    def _validate_ability_score_compliance(self, scores: Dict[str, int]) -> List[str]:
        """Validate ability scores meet SRD requirements."""
        issues = []
        
        for score_name, score_value in scores.items():
            if not isinstance(score_value, int):
                issues.append(f"{score_name} must be an integer")
            elif score_value < 1 or score_value > 20:
                issues.append(f"{score_name} must be between 1 and 20")
        
        return issues

# Global instance for easy access
srd_checker = SRDComplianceChecker() 