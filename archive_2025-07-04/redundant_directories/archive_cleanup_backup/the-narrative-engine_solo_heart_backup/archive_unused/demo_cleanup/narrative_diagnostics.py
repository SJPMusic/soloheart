import datetime
from typing import List, Dict, Any
from narrative_engine.core.campaign_orchestrator import DynamicCampaignOrchestrator
from dnd_game.narrative_bridge import NarrativeBridge

# --- Conflict Timeline ---
def generate_conflict_timeline(campaign_id: str) -> List[Dict[str, Any]]:
    """Return a chronological list of conflicts for the campaign."""
    bridge = NarrativeBridge(campaign_id)
    orchestrator = bridge.campaign_orchestrator
    timeline = []
    for conflict in sorted(orchestrator.conflicts.values(), key=lambda c: c.created_timestamp):
        timeline.append({
            'id': conflict.conflict_id,
            'type': conflict.conflict_type.value,
            'description': conflict.description,
            'timestamp': conflict.created_timestamp.isoformat(),
            'urgency': conflict.urgency.value,
            'resolved': conflict.resolved_timestamp is not None,
            'resolution_action': conflict.resolution_chosen or '',
            'characters_involved': conflict.characters_involved
        })
    return timeline

# --- Arc Resolution Map ---
def generate_arc_map(campaign_id: str) -> Dict[str, Any]:
    """Return a map of each character's arcs, milestones, and status."""
    bridge = NarrativeBridge(campaign_id)
    arc_map = {}
    arcs = bridge.get_character_arcs()
    for arc in arcs:
        char_id = arc.get('character_id', 'player')
        if char_id not in arc_map:
            arc_map[char_id] = []
        arc_map[char_id].append({
            'arc_type': arc.get('arc_type'),
            'milestones': arc.get('milestones', []),
            'status': arc.get('status'),
            'arc_id': arc.get('id'),
            'title': arc.get('title'),
            'description': arc.get('description')
        })
    return arc_map

# --- Emotion Heatmap ---
def generate_emotion_heatmap(campaign_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """Return a time series of emotion intensity per character."""
    bridge = NarrativeBridge(campaign_id)
    # Assume bridge exposes a method to get all memories with emotion info
    memories = bridge.get_all_memories() if hasattr(bridge, 'get_all_memories') else []
    heatmap = {}
    for mem in memories:
        char_id = mem.get('character_id', 'player')
        timestamp = mem.get('timestamp') or mem.get('created_at')
        emotions = mem.get('metadata', {}).get('emotional_context', [])
        intensity = mem.get('metadata', {}).get('emotional_intensity', 0.0)
        for emotion in emotions:
            if char_id not in heatmap:
                heatmap[char_id] = []
            heatmap[char_id].append({
                'character_id': char_id,
                'emotion': emotion,
                'timestamp': timestamp,
                'intensity': intensity
            })
    return heatmap

# --- Diagnostic Report ---
def generate_diagnostic_report(campaign_id: str) -> Dict[str, Any]:
    """Return a summary diagnostic report for the campaign."""
    bridge = NarrativeBridge(campaign_id)
    timeline = generate_conflict_timeline(campaign_id)
    arc_map = generate_arc_map(campaign_id)
    heatmap = generate_emotion_heatmap(campaign_id)
    # For total actions/events, assume bridge exposes logs or counts
    total_actions = getattr(bridge, 'get_total_actions', lambda: 0)()
    total_conflicts = len(timeline)
    resolved_conflicts = sum(1 for c in timeline if c['resolved'])
    unresolved_conflicts = total_conflicts - resolved_conflicts
    # Dominant emotions: most frequent per character
    dominant_emotions = {}
    for char_id, entries in heatmap.items():
        freq = {}
        for entry in entries:
            e = entry['emotion']
            freq[e] = freq.get(e, 0) + 1
        if freq:
            dominant_emotions[char_id] = max(freq, key=freq.get)
    # Arc progress summary
    arc_progress_summary = {}
    for char_id, arcs in arc_map.items():
        arc_progress_summary[char_id] = [arc['status'] for arc in arcs]
    return {
        'campaign_id': campaign_id,
        'total_actions': total_actions,
        'total_conflicts': total_conflicts,
        'resolved_conflicts': resolved_conflicts,
        'unresolved_conflicts': unresolved_conflicts,
        'dominant_emotions': dominant_emotions,
        'arc_progress_summary': arc_progress_summary
    } 