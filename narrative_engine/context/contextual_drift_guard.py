"""
Contextual Drift Prevention System - The Narrative Engine
========================================================

Implements contextual drift prevention to maintain narrative coherence.
Supports the roadmap principle: "Narrative continuity matters"

Features:
- Check memory relevance to current context
- Filter out irrelevant memories to prevent drift
- Provide explanations for filtering decisions
- JSON-compatible outputs for AI context pipelines
- Campaign-aware filtering for multi-campaign support

Future enhancements:
- Sentiment analysis for emotional relevance
- Topic modeling for thematic coherence
- Event causality trees for plot continuity
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re

logger = logging.getLogger(__name__)

@dataclass
class FilteringDecision:
    """Record of a filtering decision for transparency"""
    memory_id: str
    memory_content: str
    relevance_score: float
    threshold: float
    filtered_out: bool
    reasoning: str
    timestamp: str

@dataclass
class DriftAnalysis:
    """Analysis of potential narrative drift"""
    campaign_id: str
    context_keywords: List[str]
    memory_count_before: int
    memory_count_after: int
    average_relevance: float
    filtering_decisions: List[FilteringDecision]
    drift_risk_score: float
    recommendations: List[str]

class ContextualDriftGuard:
    """
    Contextual drift prevention system.
    
    Aligns with roadmap principle: "Narrative continuity matters"
    - Filters irrelevant memories to prevent narrative drift
    - Maintains coherent storylines across sessions
    - Provides transparent filtering decisions
    - Supports campaign-aware context management
    """
    
    def __init__(self, default_threshold: float = 0.4):
        self.default_threshold = default_threshold
        self.filtering_history: Dict[str, List[FilteringDecision]] = {}
        self.context_cache: Dict[str, Dict[str, float]] = {}
        
        logger.info(f"Contextual drift guard initialized with threshold {default_threshold}")
    
    def check_relevance(
        self, 
        context: List[str], 
        memory: List[str],
        campaign_id: Optional[str] = None
    ) -> float:
        """
        Check relevance of memories to current context.
        
        Args:
            context: Current narrative context keywords/phrases
            memory: Memory content to evaluate
            campaign_id: Optional campaign identifier for caching
        
        Returns:
            float: Relevance score between 0.0 and 1.0
        """
        if not context or not memory:
            return 0.0
        
        # Normalize context and memory to lowercase for comparison
        context_normalized = [phrase.lower().strip() for phrase in context]
        memory_normalized = [phrase.lower().strip() for phrase in memory]
        
        # Calculate keyword overlap
        context_keywords = set()
        for phrase in context_normalized:
            context_keywords.update(phrase.split())
        
        memory_keywords = set()
        for phrase in memory_normalized:
            memory_keywords.update(phrase.split())
        
        # Calculate weighted relevance score
        intersection = context_keywords.intersection(memory_keywords)
        union = context_keywords.union(memory_keywords)
        
        if len(union) == 0:
            return 0.0
        
        # Use intersection/union ratio but with a boost for partial matches
        base_score = len(intersection) / len(union)
        
        # Boost score based on intersection size relative to context
        if len(intersection) > 0:
            context_coverage = len(intersection) / len(context_keywords)
            memory_coverage = len(intersection) / len(memory_keywords)
            coverage_boost = (context_coverage + memory_coverage) / 2.0
            base_score = max(base_score, coverage_boost * 0.5)
        
        # Apply semantic similarity boost for related concepts
        relevance_score = self._apply_semantic_boost(base_score, context_normalized, memory_normalized)
        
        # Cache result if campaign_id provided
        if campaign_id:
            cache_key = f"{campaign_id}_{hash(tuple(context))}_{hash(tuple(memory))}"
            self.context_cache[cache_key] = relevance_score
        
        return min(relevance_score, 1.0)
    
    def _apply_semantic_boost(
        self, 
        base_score: float, 
        context: List[str], 
        memory: List[str]
    ) -> float:
        """Apply semantic similarity boost for related concepts"""
        # Define semantic relationships (simplified - could use embeddings)
        semantic_groups = {
            'combat': ['fight', 'battle', 'attack', 'defend', 'weapon', 'armor', 'damage'],
            'social': ['talk', 'conversation', 'diplomacy', 'negotiate', 'persuade', 'intimidate'],
            'exploration': ['travel', 'explore', 'discover', 'map', 'location', 'terrain'],
            'magic': ['spell', 'magic', 'enchantment', 'ritual', 'arcane', 'divine'],
            'emotion': ['anger', 'fear', 'joy', 'sadness', 'trust', 'surprise'],
            'time': ['morning', 'afternoon', 'evening', 'night', 'dawn', 'dusk']
        }
        
        # Check for semantic group matches
        context_groups = set()
        memory_groups = set()
        
        for group_name, keywords in semantic_groups.items():
            for phrase in context:
                if any(keyword in phrase for keyword in keywords):
                    context_groups.add(group_name)
            for phrase in memory:
                if any(keyword in phrase for keyword in keywords):
                    memory_groups.add(group_name)
        
        # Apply boost for matching semantic groups
        if context_groups.intersection(memory_groups):
            boost = 0.2  # 20% boost for semantic similarity
            return min(base_score + boost, 1.0)
        
        return base_score
    
    def filter_irrelevant_memories(
        self,
        context: List[str],
        memories: List[Dict[str, Any]],
        threshold: Optional[float] = None,
        campaign_id: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], DriftAnalysis]:
        """
        Filter out memories that are irrelevant to current context.
        
        Args:
            context: Current narrative context
            memories: List of memory dictionaries to filter
            threshold: Relevance threshold (uses default if None)
            campaign_id: Optional campaign identifier
        
        Returns:
            Tuple of (filtered_memories, drift_analysis)
        """
        if threshold is None:
            threshold = self.default_threshold
        
        filtering_decisions = []
        filtered_memories = []
        
        for memory in memories:
            # Extract memory content for relevance checking
            memory_content = self._extract_memory_content(memory)
            
            # Calculate relevance
            relevance_score = self.check_relevance(context, [memory_content], campaign_id)
            
            # Make filtering decision
            filtered_out = relevance_score < threshold
            reasoning = self._generate_filtering_reasoning(relevance_score, threshold, memory_content, context)
            
            decision = FilteringDecision(
                memory_id=memory.get('id', 'unknown'),
                memory_content=memory_content,
                relevance_score=relevance_score,
                threshold=threshold,
                filtered_out=filtered_out,
                reasoning=reasoning,
                timestamp=datetime.utcnow().isoformat()
            )
            
            filtering_decisions.append(decision)
            
            if not filtered_out:
                filtered_memories.append(memory)
        
        # Generate drift analysis
        drift_analysis = self._generate_drift_analysis(
            context, memories, filtered_memories, filtering_decisions, campaign_id
        )
        
        # Store filtering history
        if campaign_id:
            if campaign_id not in self.filtering_history:
                self.filtering_history[campaign_id] = []
            self.filtering_history[campaign_id].extend(filtering_decisions)
        
        logger.info(f"Filtered {len(memories) - len(filtered_memories)} irrelevant memories from {len(memories)} total")
        
        return filtered_memories, drift_analysis
    
    def _extract_memory_content(self, memory: Dict[str, Any]) -> str:
        """Extract text content from memory for relevance checking"""
        content_parts = []
        
        # Extract from common memory fields
        for field in ['content', 'description', 'summary', 'text', 'narrative']:
            if field in memory and memory[field]:
                content_parts.append(str(memory[field]))
        
        # Extract from emotional context if present
        if 'emotional_context' in memory and memory['emotional_context']:
            emotional = memory['emotional_context']
            if isinstance(emotional, dict):
                for field in ['primary_tone', 'event_type', 'triggers', 'consequences']:
                    if field in emotional and emotional[field]:
                        content_parts.append(str(emotional[field]))
        
        # Extract from metadata if present
        if 'metadata' in memory and memory['metadata']:
            metadata = memory['metadata']
            if isinstance(metadata, dict):
                for value in metadata.values():
                    if value:
                        content_parts.append(str(value))
        
        return ' '.join(content_parts)
    
    def _generate_filtering_reasoning(
        self, 
        relevance_score: float, 
        threshold: float, 
        memory_content: str, 
        context: List[str]
    ) -> str:
        """Generate human-readable reasoning for filtering decision"""
        if relevance_score >= threshold:
            return f"Memory retained: relevance score {relevance_score:.2f} >= threshold {threshold}"
        
        # Identify why memory was filtered
        context_keywords = set()
        for phrase in context:
            context_keywords.update(phrase.lower().split())
        
        memory_keywords = set(memory_content.lower().split())
        
        # Find missing keywords
        missing_keywords = context_keywords - memory_keywords
        if missing_keywords:
            missing_str = ', '.join(list(missing_keywords)[:3])  # Show first 3
            return f"Filtered: low relevance ({relevance_score:.2f}) - missing context keywords: {missing_str}"
        
        return f"Filtered: low relevance score {relevance_score:.2f} < threshold {threshold}"
    
    def _generate_drift_analysis(
        self,
        context: List[str],
        original_memories: List[Dict[str, Any]],
        filtered_memories: List[Dict[str, Any]],
        filtering_decisions: List[FilteringDecision],
        campaign_id: Optional[str] = None
    ) -> DriftAnalysis:
        """Generate comprehensive drift analysis"""
        memory_count_before = len(original_memories)
        memory_count_after = len(filtered_memories)
        
        # Calculate average relevance
        if filtering_decisions:
            average_relevance = sum(d.relevance_score for d in filtering_decisions) / len(filtering_decisions)
        else:
            average_relevance = 0.0
        
        # Calculate drift risk score
        filtered_ratio = (memory_count_before - memory_count_after) / max(memory_count_before, 1)
        drift_risk_score = filtered_ratio * (1.0 - average_relevance)
        
        # Generate recommendations
        recommendations = []
        if drift_risk_score > 0.7:
            recommendations.append("High drift risk detected - consider expanding context keywords")
        if average_relevance < 0.3:
            recommendations.append("Low average relevance - review context specificity")
        if memory_count_after < 3:
            recommendations.append("Very few memories retained - may need broader context")
        
        return DriftAnalysis(
            campaign_id=campaign_id or "unknown",
            context_keywords=context,
            memory_count_before=memory_count_before,
            memory_count_after=memory_count_after,
            average_relevance=average_relevance,
            filtering_decisions=filtering_decisions,
            drift_risk_score=drift_risk_score,
            recommendations=recommendations
        )
    
    def explain_filtering(
        self,
        campaign_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Explain recent filtering decisions.
        
        Args:
            campaign_id: Optional campaign filter
            limit: Maximum number of decisions to include
        
        Returns:
            Dict containing filtering explanation
        """
        if campaign_id and campaign_id in self.filtering_history:
            decisions = self.filtering_history[campaign_id][-limit:]
        else:
            # Combine all campaign decisions
            all_decisions = []
            for campaign_decisions in self.filtering_history.values():
                all_decisions.extend(campaign_decisions)
            decisions = sorted(all_decisions, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        # Convert to JSON-compatible format
        decisions_json = []
        for decision in decisions:
            decisions_json.append(asdict(decision))
        
        # Calculate statistics
        total_decisions = len(decisions)
        filtered_count = sum(1 for d in decisions if d.filtered_out)
        avg_relevance = sum(d.relevance_score for d in decisions) / max(total_decisions, 1)
        
        return {
            'campaign_id': campaign_id,
            'total_decisions': total_decisions,
            'filtered_count': filtered_count,
            'retained_count': total_decisions - filtered_count,
            'average_relevance': avg_relevance,
            'recent_decisions': decisions_json,
            'explanation': f"Filtered {filtered_count} out of {total_decisions} memories (avg relevance: {avg_relevance:.2f})"
        }
    
    def get_context_suggestions(
        self,
        current_context: List[str],
        campaign_id: Optional[str] = None
    ) -> List[str]:
        """Get suggestions for context keywords based on current context."""
        suggestions = []
        
        # Extract keywords from current context
        keywords = set()
        for phrase in current_context:
            keywords.update(phrase.lower().split())
        
        # Add semantic suggestions based on keywords
        semantic_groups = {
            'combat': ['fight', 'battle', 'attack', 'defend', 'weapon', 'armor', 'damage'],
            'social': ['talk', 'conversation', 'diplomacy', 'negotiate', 'persuade', 'intimidate'],
            'exploration': ['travel', 'explore', 'discover', 'map', 'location', 'terrain'],
            'magic': ['spell', 'magic', 'enchantment', 'ritual', 'arcane', 'divine'],
            'emotion': ['anger', 'fear', 'joy', 'sadness', 'trust', 'surprise'],
            'time': ['morning', 'afternoon', 'evening', 'night', 'dawn', 'dusk']
        }
        
        for group_name, group_keywords in semantic_groups.items():
            if any(keyword in keywords for keyword in group_keywords):
                suggestions.extend(group_keywords[:3])  # Add first 3 keywords from matching group
        
        return list(set(suggestions))[:10]  # Return unique suggestions, max 10

    def validate_narration(self, narration: str, context: Dict[str, Any]) -> str:
        """
        Validate and potentially adjust narration to maintain contextual coherence.
        
        Args:
            narration: The generated narration text
            context: Current context information
            
        Returns:
            str: Validated/adjusted narration
        """
        # For now, return the narration as-is
        # This is a placeholder for future contextual validation logic
        # Could include:
        # - Character consistency checks
        # - Location coherence validation
        # - Tone and style consistency
        # - Plot continuity verification
        
        logger.debug(f"Validating narration for context: {context.get('campaign_id', 'unknown')}")
        return narration

# Global instance for easy access
contextual_drift_guard = ContextualDriftGuard() 