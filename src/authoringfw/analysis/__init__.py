"""
authoringfw.analysis — Analysis sub-domain.

Provides orchestrators for text analysis tasks:
  - StyleAnalysisOrchestrator: analyses style, tone, POV consistency
  - PlotAnalysisOrchestrator: analyses plot structure, pacing, arc
"""

from authoringfw.analysis.analysis import PlotAnalysisOrchestrator, StyleAnalysisOrchestrator
from authoringfw.analysis.types import AnalysisResult, AnalysisTask

__all__ = [
    "StyleAnalysisOrchestrator",
    "PlotAnalysisOrchestrator",
    "AnalysisTask",
    "AnalysisResult",
]
