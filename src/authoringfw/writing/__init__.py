"""
authoringfw.writing — Writing sub-domain.

Provides concrete orchestrators for text generation tasks:
  - ChapterOrchestrator: generates a chapter from outline + context
  - SummaryOrchestrator: generates a chapter/section summary

Usage::

    from authoringfw.writing import ChapterOrchestrator, ChapterTask

    orchestrator = ChapterOrchestrator()
    result = orchestrator.execute(ChapterTask(
        action_code="chapter_writing",
        chapter_title="Der erste Schritt",
        chapter_outline="Protagonist trifft den Mentor...",
        previous_summary="In Kapitel 1 erwachte...",
    ))
    print(result.content)
"""

from authoringfw.writing.chapter import ChapterOrchestrator
from authoringfw.writing.summary import SummaryOrchestrator
from authoringfw.writing.types import (
    ChapterResult,
    ChapterTask,
    SummaryResult,
    SummaryTask,
)

__all__ = [
    "ChapterOrchestrator",
    "SummaryOrchestrator",
    "ChapterTask",
    "ChapterResult",
    "SummaryTask",
    "SummaryResult",
]
