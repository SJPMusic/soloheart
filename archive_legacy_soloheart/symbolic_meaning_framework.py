#!/usr/bin/env python3
"""
Symbolic Meaning Framework for SoloHeart Narrative Engine

This module implements Jordan Peterson's Maps of Meaning principles for narrative generation,
including archetypal tagging, chaos/order tension tracking, and narrative decay modeling.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from enum import Enum
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ArchetypalTags(Enum):
    """Core archetypal symbols from Maps of Meaning"""
    # Order/Structure
    ORDER = "Order"
    FATHER = "Father"
    MENTOR = "Mentor"
    KING = "King"
    TRADITION = "Tradition"
    
    # Chaos/Transformation
    CHAOS = "Chaos"
    SHADOW = "Shadow"
    THRESHOLD = "Threshold"
    TRANSFORMATION = "Transformation"
    REBIRTH = "Rebirth"
    
    # Heroic Journey
    SACRIFICE = "Sacrifice"
    WOUND = "Wound"
    JOURNEY = "Journey"
    RETURN = "Return"
    REDEMPTION = "Redemption"
    
    # Feminine/Anima
    ANIMA = "Anima"
    MOTHER = "Mother"
    WISDOM = "Wisdom"
    INTUITION = "Intuition"
    
    # Adversarial
    ENEMY = "Enemy"
    BETRAYAL = "Betrayal"
    CORRUPTION = "Corruption"
    DECAY = "Decay"

class ChaosOrderState(Enum):
    """Chaos/Order tension states"""
    PURE_ORDER = "pure_order"      # Rigid, predictable, safe
    ORDER_DOMINANT = "order_dominant"  # Structured with minor chaos
    BALANCED = "balanced"          # Healthy tension
    CHAOS_DOMINANT = "chaos_dominant"  # Unstable with order elements
    PURE_CHAOS = "pure_chaos"      # Complete disorder, danger

class SymbolicMeaningFramework:
    """Core framework for symbolic meaning in narrative"""
    
    def __init__(self):
        self.chaos_order_tension = 0.5  # 0.0 = pure order, 1.0 = pure chaos
        self.narrative_decay = 0.0      # 0.0 = healthy, 1.0 = corrupted
        self.archetypal_history = []
        self.symbolic_coherence_score = 1.0
        
    def tag_fact_with_archetypes(self, fact_type: str, value: Any, source_text: str) -> List[str]:
        """Tag a fact with relevant archetypal symbols"""
        tags = []
        text_lower = source_text.lower()
        
        # Name archetypes
        if fact_type == "name":
            if any(word in text_lower for word in ["king", "lord", "sir", "master"]):
                tags.append(ArchetypalTags.KING.value)
            elif any(word in text_lower for word in ["father", "dad", "papa"]):
                tags.append(ArchetypalTags.FATHER.value)
            elif any(word in text_lower for word in ["mother", "mom", "mama"]):
                tags.append(ArchetypalTags.MOTHER.value)
        
        # Trauma/Wound archetypes
        if fact_type in ["traumas", "emotional_themes"]:
            if any(word in text_lower for word in ["killed", "murdered", "died", "lost", "betrayed"]):
                tags.extend([ArchetypalTags.WOUND.value, ArchetypalTags.SHADOW.value])
            if any(word in text_lower for word in ["revenge", "vengeance", "justice"]):
                tags.append(ArchetypalTags.SACRIFICE.value)
        
        # Motivations archetypes
        if fact_type == "motivations":
            if any(word in text_lower for word in ["revenge", "vengeance"]):
                tags.extend([ArchetypalTags.SHADOW.value, ArchetypalTags.SACRIFICE.value])
            elif any(word in text_lower for word in ["redemption", "forgiveness"]):
                tags.append(ArchetypalTags.REDEMPTION.value)
            elif any(word in text_lower for word in ["adventure", "journey", "quest"]):
                tags.append(ArchetypalTags.JOURNEY.value)
        
        # Combat/Class archetypes
        if fact_type == "class":
            if value == "Fighter":
                tags.append(ArchetypalTags.ORDER.value)
            elif value in ["Barbarian", "Rogue"]:
                tags.append(ArchetypalTags.CHAOS.value)
            elif value in ["Paladin", "Cleric"]:
                tags.append(ArchetypalTags.FATHER.value)
            elif value in ["Druid", "Ranger"]:
                tags.append(ArchetypalTags.ANIMA.value)
        
        # Gear/Items archetypes
        if fact_type == "gear":
            if any(word in text_lower for word in ["sword", "weapon", "armor"]):
                tags.append(ArchetypalTags.ORDER.value)
            elif any(word in text_lower for word in ["pendant", "amulet", "prayer"]):
                tags.append(ArchetypalTags.ANIMA.value)
            elif any(word in text_lower for word in ["father's", "inherited"]):
                tags.append(ArchetypalTags.FATHER.value)
        
        # Background archetypes
        if fact_type == "background":
            if value == "Soldier":
                tags.append(ArchetypalTags.ORDER.value)
            elif value == "Criminal":
                tags.append(ArchetypalTags.SHADOW.value)
            elif value == "Acolyte":
                tags.append(ArchetypalTags.FATHER.value)
            elif value == "Folk Hero":
                tags.append(ArchetypalTags.MENTOR.value)
        
        return list(set(tags))  # Remove duplicates
    
    def assess_chaos_order_impact(self, fact_type: str, value: Any, tags: List[str]) -> float:
        """Assess how a fact impacts chaos/order tension (-1.0 to 1.0)"""
        impact = 0.0
        
        # Order-increasing factors
        if ArchetypalTags.ORDER.value in tags:
            impact -= 0.2
        if ArchetypalTags.FATHER.value in tags:
            impact -= 0.15
        if ArchetypalTags.TRADITION.value in tags:
            impact -= 0.1
        if fact_type == "class" and value in ["Fighter", "Paladin", "Cleric"]:
            impact -= 0.1
        
        # Chaos-increasing factors
        if ArchetypalTags.CHAOS.value in tags:
            impact += 0.2
        if ArchetypalTags.SHADOW.value in tags:
            impact += 0.15
        if ArchetypalTags.THRESHOLD.value in tags:
            impact += 0.1
        if fact_type == "class" and value in ["Barbarian", "Rogue", "Warlock"]:
            impact += 0.1
        if fact_type == "traumas" and value:
            impact += 0.2
        
        return max(-1.0, min(1.0, impact))
    
    def update_chaos_order_tension(self, impact: float):
        """Update the chaos/order tension based on new input"""
        # Weighted average with current tension
        self.chaos_order_tension = (self.chaos_order_tension * 0.8) + (impact * 0.2)
        self.chaos_order_tension = max(0.0, min(1.0, self.chaos_order_tension))
        
        logger.debug(f"🔄 Chaos/Order tension updated: {self.chaos_order_tension:.3f}")
    
    def get_chaos_order_state(self) -> ChaosOrderState:
        """Get current chaos/order state"""
        if self.chaos_order_tension <= 0.1:
            return ChaosOrderState.PURE_ORDER
        elif self.chaos_order_tension <= 0.3:
            return ChaosOrderState.ORDER_DOMINANT
        elif self.chaos_order_tension <= 0.7:
            return ChaosOrderState.BALANCED
        elif self.chaos_order_tension <= 0.9:
            return ChaosOrderState.CHAOS_DOMINANT
        else:
            return ChaosOrderState.PURE_CHAOS
    
    def detect_narrative_decay(self, fact_type: str, value: Any, tags: List[str], 
                             previous_facts: Dict[str, Any]) -> float:
        """Detect narrative decay from contradictions, avoidance, or repeated failures"""
        decay_increase = 0.0
        
        # Contradictions
        if fact_type in previous_facts:
            if previous_facts[fact_type] != value:
                decay_increase += 0.3
                logger.debug(f"⚠️ Contradiction detected in {fact_type}")
        
        # Avoidance patterns
        if fact_type == "motivations" and not value:
            decay_increase += 0.2
        if fact_type == "personality_traits" and not value:
            decay_increase += 0.1
        
        # Shadow/Chaos accumulation
        shadow_count = sum(1 for tag in tags if tag == ArchetypalTags.SHADOW.value)
        if shadow_count > 2:
            decay_increase += 0.2
        
        # Update narrative decay
        self.narrative_decay = min(1.0, self.narrative_decay + decay_increase)
        
        return decay_increase
    
    def assess_symbolic_coherence(self, all_tags: List[str]) -> float:
        """Assess symbolic coherence of all current tags"""
        if not all_tags:
            return 1.0
        
        # Check for conflicting archetypes
        conflicts = 0
        total_pairs = 0
        
        for i, tag1 in enumerate(all_tags):
            for j, tag2 in enumerate(all_tags[i+1:], i+1):
                total_pairs += 1
                if self._are_archetypes_conflicting(tag1, tag2):
                    conflicts += 1
        
        if total_pairs == 0:
            return 1.0
        
        coherence = 1.0 - (conflicts / total_pairs)
        self.symbolic_coherence_score = coherence
        
        return coherence
    
    def _are_archetypes_conflicting(self, tag1: str, tag2: str) -> bool:
        """Check if two archetypal tags are in conflict"""
        conflicts = [
            (ArchetypalTags.ORDER.value, ArchetypalTags.CHAOS.value),
            (ArchetypalTags.FATHER.value, ArchetypalTags.SHADOW.value),
            (ArchetypalTags.MENTOR.value, ArchetypalTags.ENEMY.value),
            (ArchetypalTags.REDEMPTION.value, ArchetypalTags.CORRUPTION.value)
        ]
        
        return (tag1, tag2) in conflicts or (tag2, tag1) in conflicts
    
    def generate_narrative_response(self, chaos_order_state: ChaosOrderState, 
                                  narrative_decay: float) -> str:
        """Generate narrative response based on current symbolic state"""
        if narrative_decay > 0.7:
            return "The world around you seems to distort and decay. Memories blur and shift, as if reality itself is rejecting the contradictions in your story."
        elif narrative_decay > 0.4:
            return "There's a growing sense of unease. The narrative feels strained, as if struggling to maintain coherence."
        
        if chaos_order_state == ChaosOrderState.PURE_ORDER:
            return "The world feels rigid and predictable, but there's a sense of safety in the established order."
        elif chaos_order_state == ChaosOrderState.ORDER_DOMINANT:
            return "Structure and tradition provide a solid foundation, though there are hints of change on the horizon."
        elif chaos_order_state == ChaosOrderState.BALANCED:
            return "There's a healthy tension between order and chaos, creating dynamic potential for growth."
        elif chaos_order_state == ChaosOrderState.CHAOS_DOMINANT:
            return "The world feels unstable and unpredictable, but there's also great potential for transformation."
        else:  # PURE_CHAOS
            return "Complete disorder reigns. This is a place of danger and opportunity, where anything can happen."
    
    def get_symbolic_summary(self) -> Dict[str, Any]:
        """Get a summary of current symbolic state"""
        return {
            "chaos_order_tension": self.chaos_order_tension,
            "chaos_order_state": self.get_chaos_order_state().value,
            "narrative_decay": self.narrative_decay,
            "symbolic_coherence": self.symbolic_coherence_score,
            "archetypal_history": self.archetypal_history[-10:],  # Last 10 entries
            "narrative_response": self.generate_narrative_response(
                self.get_chaos_order_state(), self.narrative_decay
            )
        } 