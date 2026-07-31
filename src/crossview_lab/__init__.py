"""Synthetic DLL-injection detection and offline cross-view analysis."""

from .analyzer import analyze, analyze_events
from .simulator import simulate_scenario

__all__ = ["analyze", "analyze_events", "simulate_scenario"]
__version__ = "0.2.0"
