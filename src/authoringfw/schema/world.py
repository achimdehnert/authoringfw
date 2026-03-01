"""World context schema for AI-assisted authoring."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Location(BaseModel):
    """A location within a story world."""

    name: str
    description: str = ""
    atmosphere: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorldContext(BaseModel):
    """The story universe — locations, lore, rules, and time period."""

    title: str
    genre: str = ""
    setting: str = ""
    time_period: str = ""
    world_rules: list[str] = Field(default_factory=list)
    locations: list[Location] = Field(default_factory=list)
    lore: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_context_string(self) -> str:
        """Format world context for prompt injection."""
        lines = [f"World: {self.title}"]
        if self.genre:
            lines.append(f"Genre: {self.genre}")
        if self.setting:
            lines.append(f"Setting: {self.setting}")
        if self.time_period:
            lines.append(f"Time period: {self.time_period}")
        if self.world_rules:
            lines.append("Rules: " + "; ".join(self.world_rules))
        return "\n".join(lines)

    def to_yaml(self) -> str:
        """Serialize to YAML string."""
        try:
            import yaml
        except ImportError as e:
            raise ImportError("pyyaml is required. Install with: pip install pyyaml") from e
        return yaml.dump(self.model_dump(), allow_unicode=True, default_flow_style=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "WorldContext":
        """Deserialize from YAML string."""
        try:
            import yaml
        except ImportError as e:
            raise ImportError("pyyaml is required. Install with: pip install pyyaml") from e
        data = yaml.safe_load(yaml_str)
        return cls(**data)
