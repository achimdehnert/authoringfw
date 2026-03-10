"""Scene profile schema for AI-assisted authoring."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SceneProfile(BaseModel):
    """Represents a single scene in a story.

    A scene is the smallest narrative unit: one location, one time,
    one set of characters, one dramatic purpose.
    """

    title: str
    summary: str = ""
    goal: str = ""
    disaster: str = ""
    pov_character: str = ""
    location: str = ""
    mood: str = ""
    order: int = 0
    beat_sheet: list[str] = Field(default_factory=list)
    characters_present: list[str] = Field(default_factory=list)
    notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_context_string(self) -> str:
        """Format scene for prompt injection."""
        lines = [f"Scene: {self.title}"]
        if self.pov_character:
            lines.append(f"POV: {self.pov_character}")
        if self.location:
            lines.append(f"Location: {self.location}")
        if self.mood:
            lines.append(f"Mood: {self.mood}")
        if self.goal:
            lines.append(f"Goal: {self.goal}")
        if self.disaster:
            lines.append(f"Disaster: {self.disaster}")
        if self.summary:
            lines.append(f"Summary: {self.summary}")
        if self.beat_sheet:
            lines.append("Beats:\n" + "\n".join(f"  - {b}" for b in self.beat_sheet))
        return "\n".join(lines)

    def to_yaml(self) -> str:
        """Serialize to YAML string."""
        try:
            import yaml
        except ImportError as e:
            raise ImportError(
                "pyyaml is required. Install with: pip install pyyaml"
            ) from e
        return yaml.dump(self.model_dump(), allow_unicode=True, default_flow_style=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "SceneProfile":
        """Deserialize from YAML string."""
        try:
            import yaml
        except ImportError as e:
            raise ImportError(
                "pyyaml is required. Install with: pip install pyyaml"
            ) from e
        data = yaml.safe_load(yaml_str)
        return cls(**data)
