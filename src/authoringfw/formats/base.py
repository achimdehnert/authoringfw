"""Base format profile and workflow phase definitions."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from authoringfw.planning import PlanningFieldConfig


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

    model_config = {"arbitrary_types_allowed": True}

    def steps_for_phase(self, phase: WorkflowPhase) -> list[StepConfig]:
        return [s for s in self.steps if s.phase == phase]

    @property
    def planning_fields(self) -> "PlanningFieldConfig":
        """Return the PlanningFieldConfig for this format.

        Lazy import to avoid circular dependency.
        """
        from authoringfw.planning import get_planning_config
        return get_planning_config(self.format_type)


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

NONFICTION = FormatProfile(
    format_type="nonfiction",
    display_name="Non-Fiction",
    description="Informational or instructional book for a general or specialist audience.",
    style_constraints=["Clear structure", "Evidence-based", "Reader-focused"],
)

ACADEMIC = FormatProfile(
    format_type="academic",
    display_name="Academic Monograph",
    description="Scholarly long-form work (monograph, dissertation, Habilitation).",
    style_constraints=["Objective tone", "Citation required", "Structured argumentation"],
)

SCREENPLAY = FormatProfile(
    format_type="screenplay",
    display_name="Screenplay",
    description="Film or TV script with scene headings, action lines, and dialogue.",
    style_constraints=["INT./EXT. scene headings", "Present tense", "Show don't tell", "Dialogue-driven"],
)

SHORT_STORY = FormatProfile(
    format_type="short_story",
    display_name="Short Story",
    description="Compact fiction up to ~10,000 words with single narrative arc.",
    style_constraints=["Single POV", "Tight focus", "Strong opening hook", "Resonant ending"],
)

BLOG_POST = FormatProfile(
    format_type="blog_post",
    display_name="Blog Post",
    description="Informative or opinion web article with SEO-friendly structure.",
    style_constraints=["Conversational tone", "H2/H3 headings", "Short paragraphs", "Call to action"],
)

PODCAST_SCRIPT = FormatProfile(
    format_type="podcast_script",
    display_name="Podcast Script",
    description="Spoken-word audio script with host/guest dialogue and show notes.",
    style_constraints=["Spoken language", "No complex punctuation", "Natural transitions", "Listener-friendly summaries"],
)

FORMAT_REGISTRY: dict[str, FormatProfile] = {
    "roman": ROMAN,
    "novel": ROMAN,
    "essay": ESSAY,
    "serie": SERIE,
    "scientific": SCIENTIFIC,
    "nonfiction": NONFICTION,
    "academic": ACADEMIC,
    "screenplay": SCREENPLAY,
    "short_story": SHORT_STORY,
    "blog_post": BLOG_POST,
    "podcast_script": PODCAST_SCRIPT,
}


def get_format(format_type: str) -> FormatProfile:
    """Get a built-in format profile by type string.

    Raises:
        KeyError: If format_type is not registered in FORMAT_REGISTRY.
    """
    return FORMAT_REGISTRY[format_type]
