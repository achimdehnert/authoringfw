"""
Research sub-domain types.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from authoringfw.types import ContentResult


class ResearchTask(BaseModel):
    """
    Input for ResearchOrchestrator.

    Attributes:
        action_code: AIActionType code (default: 'research_query').
        topic: The research topic or question.
        context: Optional background context (e.g. existing world notes).
        output_format: 'prose' | 'bullets' | 'structured' (default: 'structured').
        max_words: Maximum response length in words.
        quality_level: Quality tier override (1-9). None = tenant default.
        priority: Routing priority. None = action default.
        metadata: Caller metadata.
    """

    model_config = ConfigDict(frozen=True)

    action_code: str = Field(default="research_query", description="AIActionType code")
    topic: str = Field(description="Research topic or question")
    context: str = Field(default="", description="Background context or existing notes")
    output_format: str = Field(
        default="structured",
        description="Output format: 'prose' | 'bullets' | 'structured'",
    )
    max_words: int = Field(default=500, ge=50, le=3000)
    quality_level: int | None = Field(default=None, ge=1, le=9)
    priority: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResearchResult(ContentResult):
    """
    Output from ResearchOrchestrator.

    Inherits all ContentResult fields and adds:
        structured_findings: Cleaned, ready-to-use research text for
                             injection into ChapterTask.world_context.
    """

    model_config = ConfigDict(frozen=True)

    structured_findings: str = Field(
        default="",
        description="Cleaned research output suitable for ChapterTask.world_context",
    )
    topic: str = Field(default="", description="Echo of ResearchTask.topic")
