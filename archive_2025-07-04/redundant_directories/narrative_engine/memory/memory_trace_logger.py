"""
Memory Trace Logger - The Narrative Engine
==========================================

Implements memory trace logging for narrative continuity and debug replay.
Supports the roadmap principle: "Narrative continuity is critical"

Features:
- Structured, filterable logging of all memory operations
- Integration with both LayeredMemorySystem and VectorMemoryModule
- JSON-compatible output for frontend/backend integration
- Campaign-aware filtering for all memory traces
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import os

logger = logging.getLogger(__name__)

class TraceLevel(Enum):
    """Trace levels for memory operations"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class MemoryOperation(Enum):
    """Types of memory operations to trace"""
    STORE = "store"
    RETRIEVE = "retrieve"
    DECAY = "decay"
    UPDATE = "update"
    DELETE = "delete"
    SIMILARITY_SEARCH = "similarity_search"

@dataclass
class MemoryTrace:
    """Structured memory trace entry"""
    timestamp: str
    campaign_id: str
    source_module: str
    operation: MemoryOperation
    memory_type: str
    memory_id: Optional[str]
    narrative_tags: List[str]
    emotional_context: Optional[Dict[str, Any]]
    trace_level: TraceLevel
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class MemoryTraceLogger:
    """
    Memory trace logger for narrative continuity and debug replay.
    
    Aligns with roadmap principle: "Narrative continuity is critical"
    - Logs all memory operations with structured metadata
    - Supports filtering by campaign, operation type, and narrative tags
    - Provides JSON-compatible output for integration
    """
    
    def __init__(self, log_file: str = "memory_traces.jsonl", max_traces: int = 10000):
        self.log_file = log_file
        self.max_traces = max_traces
        self.trace_count = 0
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
        
        logger.info(f"Memory trace logger initialized: {log_file}")
    
    def log_memory_operation(
        self,
        campaign_id: str,
        source_module: str,
        operation: MemoryOperation,
        memory_type: str,
        memory_id: Optional[str] = None,
        narrative_tags: List[str] = None,
        emotional_context: Optional[Dict[str, Any]] = None,
        trace_level: TraceLevel = TraceLevel.INFO,
        metadata: Dict[str, Any] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> MemoryTrace:
        """
        Log a memory operation with full context.
        
        Args:
            campaign_id: Campaign identifier (roadmap requirement)
            source_module: Module performing the operation
            operation: Type of memory operation
            memory_type: Type of memory (episodic, semantic, etc.)
            memory_id: Unique memory identifier
            narrative_tags: Tags for narrative context
            emotional_context: Emotional metadata (roadmap: "Emotional realism matters")
            trace_level: Logging level
            metadata: Additional operation metadata
            success: Whether operation succeeded
            error_message: Error details if failed
        
        Returns:
            MemoryTrace: Structured trace entry
        """
        if narrative_tags is None:
            narrative_tags = []
        if metadata is None:
            metadata = {}
        
        trace = MemoryTrace(
            timestamp=datetime.utcnow().isoformat(),
            campaign_id=campaign_id,
            source_module=source_module,
            operation=operation,
            memory_type=memory_type,
            memory_id=memory_id,
            narrative_tags=narrative_tags,
            emotional_context=emotional_context,
            trace_level=trace_level,
            metadata=metadata,
            success=success,
            error_message=error_message
        )
        
        # Write to log file
        self._write_trace(trace)
        
        # Log to standard logger
        log_message = f"Memory {operation.value}: {memory_type} in {campaign_id}"
        if not success:
            log_message += f" - ERROR: {error_message}"
        
        if trace_level == TraceLevel.ERROR:
            logger.error(log_message)
        elif trace_level == TraceLevel.WARNING:
            logger.warning(log_message)
        elif trace_level == TraceLevel.INFO:
            logger.info(log_message)
        else:
            logger.debug(log_message)
        
        return trace
    
    def _write_trace(self, trace: MemoryTrace):
        """Write trace to log file with rotation"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(asdict(trace)) + '\n')
            
            self.trace_count += 1
            
            # Simple rotation: if we exceed max_traces, create a backup
            if self.trace_count >= self.max_traces:
                self._rotate_log()
                
        except Exception as e:
            logger.error(f"Failed to write memory trace: {e}")
    
    def _rotate_log(self):
        """Rotate log file when it gets too large"""
        try:
            backup_file = f"{self.log_file}.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            os.rename(self.log_file, backup_file)
            self.trace_count = 0
            logger.info(f"Memory trace log rotated: {backup_file}")
        except Exception as e:
            logger.error(f"Failed to rotate memory trace log: {e}")
    
    def get_traces(
        self,
        campaign_id: Optional[str] = None,
        operation: Optional[MemoryOperation] = None,
        memory_type: Optional[str] = None,
        narrative_tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[MemoryTrace]:
        """
        Retrieve filtered memory traces.
        
        Args:
            campaign_id: Filter by campaign
            operation: Filter by operation type
            memory_type: Filter by memory type
            narrative_tags: Filter by narrative tags
            limit: Maximum number of traces to return
        
        Returns:
            List[MemoryTrace]: Filtered trace entries
        """
        traces = []
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if len(traces) >= limit:
                        break
                    
                    try:
                        trace_data = json.loads(line.strip())
                        trace = MemoryTrace(**trace_data)
                        
                        # Apply filters
                        if campaign_id and trace.campaign_id != campaign_id:
                            continue
                        if operation and trace.operation != operation:
                            continue
                        if memory_type and trace.memory_type != memory_type:
                            continue
                        if narrative_tags:
                            if not any(tag in trace.narrative_tags for tag in narrative_tags):
                                continue
                        
                        traces.append(trace)
                        
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines
                        
        except FileNotFoundError:
            logger.warning(f"Memory trace log not found: {self.log_file}")
        
        return traces
    
    def get_memory_stats(self, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about memory operations.
        
        Args:
            campaign_id: Optional campaign filter
        
        Returns:
            Dict containing memory operation statistics
        """
        traces = self.get_traces(campaign_id=campaign_id, limit=10000)
        
        stats = {
            'total_operations': len(traces),
            'operations_by_type': {},
            'memory_types': {},
            'success_rate': 0.0,
            'recent_operations': []
        }
        
        if not traces:
            return stats
        
        # Count operations by type
        for trace in traces:
            op_type = trace.operation.value
            if op_type not in stats['operations_by_type']:
                stats['operations_by_type'][op_type] = 0
            stats['operations_by_type'][op_type] += 1
            
            # Count memory types
            mem_type = trace.memory_type
            if mem_type not in stats['memory_types']:
                stats['memory_types'][mem_type] = 0
            stats['memory_types'][mem_type] += 1
        
        # Calculate success rate
        successful = sum(1 for trace in traces if trace.success)
        stats['success_rate'] = successful / len(traces)
        
        # Get recent operations (last 10)
        stats['recent_operations'] = [
            {
                'timestamp': trace.timestamp,
                'operation': trace.operation.value,
                'memory_type': trace.memory_type,
                'success': trace.success
            }
            for trace in sorted(traces, key=lambda x: x.timestamp, reverse=True)[:10]
        ]
        
        return stats
    
    def export_traces_for_narrative_context(
        self,
        campaign_id: str,
        narrative_tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Export traces for narrative context generation.
        
        Aligns with roadmap principle: "Story is interpretive, not just generative"
        - Provides structured context for AI responses
        - Filters by narrative relevance
        - Returns JSON-compatible format
        
        Args:
            campaign_id: Campaign to export traces for
            narrative_tags: Optional narrative tag filters
            limit: Maximum number of traces to export
        
        Returns:
            List of trace dictionaries for narrative context
        """
        traces = self.get_traces(
            campaign_id=campaign_id,
            narrative_tags=narrative_tags,
            limit=limit
        )
        
        # Convert to narrative context format
        context_traces = []
        for trace in traces:
            context_trace = {
                'timestamp': trace.timestamp,
                'operation': trace.operation.value,
                'memory_type': trace.memory_type,
                'narrative_tags': trace.narrative_tags,
                'emotional_context': trace.emotional_context,
                'metadata': trace.metadata,
                'success': trace.success
            }
            context_traces.append(context_trace)
        
        return context_traces

# Global instance for easy access
memory_trace_logger = MemoryTraceLogger() 