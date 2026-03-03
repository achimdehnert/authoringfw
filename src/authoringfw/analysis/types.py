"""
Analysis sub-domain types.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from authoringfw.types import ContentResult


class AnalysisTask(BaseModel):
    """
    Input for analysis orchestrators.

    Attributes:
        action_code: AIActionType code (e.g. 'style_analysis', 'plot_analysis').
        source_text: The text to analyse.
        analysis_focus: Optional specific focus area for the analysis.
        output_format: 'prose' | 'structured' | 'score' (default: 'structured').
        quality_level: Quality tier override. None = tenant default.
        priority: Routing priority. None = action default.
        metadata: Caller metadata.
    """

    model_config = ConfigDict(frozen=True)

    action_code: str = Field(description="AIActionType code")
    source_text: str = Field(description="Text to analyse")
    analysis_focus: str = Field(
        default="",
        description="Optional specific focus area (e.g. 'pacing', 'dialogue')",
    )
    output_format: str = Field(
        default="structured",
        description="Output format: 'prose' | 'structured' | 'score'",
    )
    quality_level: int | None = Field(default=None, ge=1, le=9)
    priority: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalysisResult(ContentResult):
    """
    Output from analysis orchestrators.

    Adds:
        score: Optional numeric quality score (0.0-1.0), if output_format='score'.
        findings: Key findings as a list of strings (parsed from structured output).
    """

    model_config = ConfigDict(frozen=True)

    score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Quality score (0.0-1.0), present when output_format='score'",
    )
    findings: list[str] = Field(
        default_factory=list,
        description="Key findings extracted from the analysis",
    )
