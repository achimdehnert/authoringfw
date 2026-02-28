"""Style profile schema for AI-assisted authoring."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StyleProfile(BaseModel):
    """Defines the stylistic characteristics of a writing project."""

    tone: str = "neutral"
    pov: str = "third_limited"
    tense: str = "past"
    vocabulary_level: str = "medium"
    sentence_rhythm: str = "varied"
    author_signature: dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": False}

    def to_constraints(self) -> list[str]:
        """Return a list of natural-language style constraints for prompt injection."""
        return [
            f"Tone: {self.tone}",
            f"Point of view: {self.pov}",
            f"Tense: {self.tense}",
            f"Vocabulary level: {self.vocabulary_level}",
            f"Sentence rhythm: {self.sentence_rhythm}",
        ]
