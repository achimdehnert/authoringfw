"""Story profile schema for AI-assisted authoring."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StoryProfile(BaseModel):
    """Represents a story or narrative arc within a world.

    A story contains chapters/scenes and belongs to a world.
    """

    title: str
    genre: str = ""
    logline: str = ""
    synopsis: str = ""
    status: str = ""
    world_title: str = ""
    target_word_count: int | None = None
    actual_word_count: int = 0
    is_public: bool = False
    notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_context_string(self) -> str:
        """Format story for prompt injection."""
        lines = [f"Story: {self.title}"]
        if self.genre:
            lines.append(f"Genre: {self.genre}")
        if self.logline:
            lines.append(f"Logline: {self.logline}")
        if self.synopsis:
            lines.append(f"Synopsis: {self.synopsis}")
        if self.status:
            lines.append(f"Status: {self.status}")
        return "\n".join(lines)

    def to_yaml(self) -> str:
        """Serialize to YAML string."""
        try:
            import yaml
        except ImportError as e:
            raise ImportError(
                "pyyaml is required. Install with: pip install pyyaml"
            ) from e
        return yaml.dump(
            self.model_dump(), allow_unicode=True, default_flow_style=False
        )

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "StoryProfile":
        """Deserialize from YAML string."""
        try:
            import yaml
        except ImportError as e:
            raise ImportError(
                "pyyaml is required. Install with: pip install pyyaml"
            ) from e
        data = yaml.safe_load(yaml_str)
        return cls(**data)
