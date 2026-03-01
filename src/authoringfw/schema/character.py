"""Character profile schema for AI-assisted authoring."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CharacterProfile(BaseModel):
    """Represents a character in a story universe."""

    name: str
    role: str = "supporting"
    description: str = ""
    personality_traits: list[str] = Field(default_factory=list)
    backstory: str = ""
    relationships: dict[str, str] = Field(default_factory=dict)
    arc: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_context_string(self) -> str:
        """Format character for prompt injection."""
        lines = [f"**{self.name}** ({self.role})"]
        if self.description:
            lines.append(self.description)
        if self.personality_traits:
            lines.append(f"Traits: {', '.join(self.personality_traits)}")
        if self.arc:
            lines.append(f"Arc: {self.arc}")
        return "\n".join(lines)

    def relationships_graph(self) -> dict[str, list[str]]:
        """
        Return relationships as a directed adjacency dict.

        Example: {"Alice": ["is sister of Bob", "loves Charlie"]}
        """
        return {self.name: list(self.relationships.values())}

    def to_yaml(self) -> str:
        """Serialize to YAML string."""
        try:
            import yaml
        except ImportError as e:
            raise ImportError("pyyaml is required. Install with: pip install pyyaml") from e
        return yaml.dump(self.model_dump(), allow_unicode=True, default_flow_style=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "CharacterProfile":
        """Deserialize from YAML string."""
        try:
            import yaml
        except ImportError as e:
            raise ImportError("pyyaml is required. Install with: pip install pyyaml") from e
        data = yaml.safe_load(yaml_str)
        return cls(**data)
