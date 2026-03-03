"""
authoringfw.research — Research sub-domain.

Provides orchestrators for research and context-gathering tasks:
  - ResearchOrchestrator: extracts structured research from a topic/query

Typical pipeline (ADR-096 §4.5)::

    research = ResearchOrchestrator().execute(ResearchTask(topic="..."))
    chapter = ChapterOrchestrator().execute(ChapterTask(
        chapter_outline="...",
        world_context=research.structured_findings,
    ))
"""

from authoringfw.research.research import ResearchOrchestrator
from authoringfw.research.types import ResearchResult, ResearchTask

__all__ = [
    "ResearchOrchestrator",
    "ResearchTask",
    "ResearchResult",
]
