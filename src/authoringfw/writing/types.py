"""
Writing sub-domain types.

Pydantic v2 frozen models for chapter and summary generation tasks.
Extend ContentTask / ContentResult with writing-specific fields.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from authoringfw.types import ContentResult


class ChapterTask(BaseModel):
    """
    Input for ChapterOrchestrator.

    Attributes:
        action_code: AIActionType code (default: 'chapter_writing').
        chapter_title: Title or heading for the chapter.
        chapter_outline: Beat sheet / outline for this chapter.
        previous_summary: Brief recap of preceding narrative (for continuity).
        style_notes: Free-form style guidance (tone, POV, tense).
        character_context: Serialised character info (from CharacterProfile.to_context_string()).
        world_context: Serialised world info (from WorldContext.to_context_string()).
        target_word_count: Approximate target length in words.
        quality_level: Quality tier override (1-9). None = tenant default.
        priority: Routing priority. None = action default.
        metadata: Caller metadata passed through to ChapterResult.
    """

    model_config = ConfigDict(frozen=True)

    action_code: str = Field(default="chapter_writing", description="AIActionType code")
    chapter_title: str = Field(description="Chapter title or heading")
    chapter_outline: str = Field(description="Beat sheet or outline for this chapter")
    previous_summary: str = Field(
        default="",
        description="Brief recap of preceding narrative for continuity",
    )
    style_notes: str = Field(
        default="",
        description="Free-form style guidance: tone, POV, tense, etc.",
    )
    character_context: str = Field(
        default="",
        description="Serialised character context (CharacterProfile.to_context_string())",
    )
    world_context: str = Field(
        default="",
        description="Serialised world context (WorldContext.to_context_string())",
    )
    target_word_count: int = Field(
        default=2000,
        ge=100,
        le=20000,
        description="Approximate target word count",
    )
    quality_level: int | None = Field(default=None, ge=1, le=9)
    priority: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChapterResult(ContentResult):
    """
    Output from ChapterOrchestrator.

    Inherits all ContentResult fields and adds writing-specific metadata.
    """

    model_config = ConfigDict(frozen=True)

    chapter_title: str = Field(default="", description="Echo of ChapterTask.chapter_title")
    estimated_word_count: int = Field(default=0, ge=0, description="Word count of generated content")


class SummaryTask(BaseModel):
    """
    Input for SummaryOrchestrator.

    Attributes:
        action_code: AIActionType code (default: 'summary_writing').
        source_text: The text to summarise.
        summary_style: 'brief' | 'detailed' | 'narrative' (default: 'brief').
        max_words: Maximum summary word count.
        quality_level: Quality tier override. None = tenant default.
        priority: Routing priority. None = action default.
        metadata: Caller metadata.
    """

    model_config = ConfigDict(frozen=True)

    action_code: str = Field(default="summary_writing", description="AIActionType code")
    source_text: str = Field(description="Text to summarise")
    summary_style: str = Field(
        default="brief",
        description="Summary style: 'brief' | 'detailed' | 'narrative'",
    )
    max_words: int = Field(default=150, ge=30, le=1000)
    quality_level: int | None = Field(default=None, ge=1, le=9)
    priority: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SummaryResult(ContentResult):
    """
    Output from SummaryOrchestrator.

    Inherits all ContentResult fields.
    """

    model_config = ConfigDict(frozen=True)
