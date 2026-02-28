"""Base format profile and workflow phase definitions."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowPhase(str, Enum):
    IDEATION = "ideation"
    CONCEPT = "concept"
    OUTLINE = "outline"
    FIRST_DRAFT = "first_draft"
    REVISION = "revision"
    CONSISTENCY = "consistency"
    PRODUCTION = "production"


class StepConfig(BaseModel):
    """Configuration for a single workflow step."""

    name: str
    phase: WorkflowPhase
    prompt_template_id: str
    max_tokens: int = 2000
    temperature: float = 0.7
    requires_human_approval: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class FormatProfile(BaseModel):
    """Defines the writing format and its workflow phases."""

    format_type: str
    display_name: str
    description: str = ""
    phases: list[WorkflowPhase] = Field(
        default_factory=lambda: list(WorkflowPhase)
    )
    steps: list[StepConfig] = Field(default_factory=list)
    style_constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def steps_for_phase(self, phase: WorkflowPhase) -> list[StepConfig]:
        return [s for s in self.steps if s.phase == phase]


ROMAN = FormatProfile(
    format_type="roman",
    display_name="Novel",
    description="Long-form fiction with chapters, characters, and story arcs.",
    style_constraints=["Show don't tell", "Consistent POV", "Scene & sequel structure"],
)

ESSAY = FormatProfile(
    format_type="essay",
    display_name="Essay",
    description="Argumentative or descriptive non-fiction prose.",
    style_constraints=["Clear thesis", "Logical argumentation", "Evidence-based claims"],
)

SERIE = FormatProfile(
    format_type="serie",
    display_name="Series",
    description="Multi-volume fiction with shared universe and recurring characters.",
    style_constraints=["Series-wide consistency", "Character continuity", "World-building coherence"],
)

SCIENTIFIC = FormatProfile(
    format_type="scientific",
    display_name="Scientific Paper",
    description="Academic writing with citations, methodology, and structured sections.",
    style_constraints=["Objective tone", "Precise terminology", "Citation required"],
)

FORMAT_REGISTRY: dict[str, FormatProfile] = {
    "roman": ROMAN,
    "essay": ESSAY,
    "serie": SERIE,
    "scientific": SCIENTIFIC,
}


def get_format(format_type: str) -> FormatProfile:
    """Get a built-in format profile by type string."""
    if format_type not in FORMAT_REGISTRY:
        raise KeyError(f"Unknown format type '{format_type}'. Available: {list(FORMAT_REGISTRY)}")
    return FORMAT_REGISTRY[format_type]
