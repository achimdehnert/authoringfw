"""
authoringfw domain types.

Pydantic v2 frozen models used as inputs and outputs for
BaseContentOrchestrator subclasses. Immutable by design — pass
ContentTask in, get ContentResult out, no side effects.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ContentTask(BaseModel):
    """
    Input for a single orchestration call.

    Attributes:
        action_code: The AIActionType code to dispatch (e.g. 'chapter_writing').
        prompt_variables: Template variables injected into the prompt.
        quality_level: Optional quality tier (1–9). None = use tenant default.
        priority: Optional routing priority ('fast' | 'balanced' | 'quality').
        metadata: Arbitrary caller metadata passed through to ContentResult.
    """

    model_config = ConfigDict(frozen=True)

    action_code: str = Field(description="AIActionType code")
    prompt_variables: dict[str, Any] = Field(
        default_factory=dict,
        description="Variables injected into the prompt template",
    )
    quality_level: int | None = Field(
        default=None,
        ge=1,
        le=9,
        description="Quality tier override (1-9). None = tenant default.",
    )
    priority: str | None = Field(
        default=None,
        description="Routing priority: 'fast' | 'balanced' | 'quality'. None = action default.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Caller metadata passed through unchanged to ContentResult",
    )


class ContentResult(BaseModel):
    """
    Output from a single orchestration call.

    Attributes:
        content: The generated text content.
        action_code: Echo of ContentTask.action_code.
        quality_level: The quality level actually used (resolved from task or default).
        model: The LLM model identifier that produced the content.
        input_tokens: Prompt token count.
        output_tokens: Completion token count.
        latency_ms: End-to-end latency in milliseconds.
        success: True if the LLM call succeeded without errors.
        metadata: Echo of ContentTask.metadata.
    """

    model_config = ConfigDict(frozen=True)

    content: str = Field(description="Generated text content")
    action_code: str = Field(description="AIActionType code used")
    quality_level: int | None = Field(
        default=None,
        description="Quality level used (resolved, not raw input)",
    )
    model: str = Field(default="", description="LLM model identifier")
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)
    success: bool = Field(default=True)
    metadata: dict[str, Any] = Field(default_factory=dict)
