"""
Narrative Structure Management

This module provides character arc and plot thread tracking capabilities for the Narrative Engine,
enabling long-term narrative development and story progression tracking.
"""

from .character_arcs import CharacterArc, ArcStatus, ArcType, CharacterArcManager
from .plot_threads import PlotThread, ThreadStatus, ThreadType, PlotThreadManager

__all__ = [
    'CharacterArc',
    'ArcStatus', 
    'ArcType',
    'CharacterArcManager',
    'PlotThread',
    'ThreadStatus',
    'ThreadType',
    'PlotThreadManager'
] 