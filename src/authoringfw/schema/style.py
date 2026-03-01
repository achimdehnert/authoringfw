"""
Style profile schema for AI-assisted authoring.

New in 0.2.0:
- to_yaml() / from_yaml() serialization
- from_text() async factory: analyze sample text → StyleProfile via LLM
"""

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

    def to_yaml(self) -> str:
        """Serialize to YAML string."""
        try:
            import yaml
        except ImportError as e:
            raise ImportError("pyyaml is required. Install with: pip install pyyaml") from e
        return yaml.dump(self.model_dump(), allow_unicode=True, default_flow_style=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "StyleProfile":
        """Deserialize from YAML string."""
        try:
            import yaml
        except ImportError as e:
            raise ImportError("pyyaml is required. Install with: pip install pyyaml") from e
        data = yaml.safe_load(yaml_str)
        return cls(**data)

    @classmethod
    async def from_text(
        cls,
        text: str,
        action_code: str = "style_analysis",
        llm_completion_fn=None,
    ) -> "StyleProfile":
        """
        Async factory: analyze sample text and return a StyleProfile.

        Requires ``aifw`` for the default LLM call, or pass a custom
        ``llm_completion_fn(action_code, messages) -> LLMResult``.

        Usage with aifw::

            from aifw import completion
            profile = await StyleProfile.from_text(sample_text)

        Usage with custom fn::

            profile = await StyleProfile.from_text(text, llm_completion_fn=my_fn)
        """
        import json

        prompt = (
            "Analyze the writing style of the following text and return a JSON object "
            "with these exact keys: tone, pov, tense, vocabulary_level, sentence_rhythm.\n"
            "Valid values:\n"
            "  tone: neutral|dark|melancholic|optimistic|humorous|tense|lyrical\n"
            "  pov: first_person|second_person|third_limited|third_omniscient\n"
            "  tense: past|present|future\n"
            "  vocabulary_level: simple|medium|advanced|academic\n"
            "  sentence_rhythm: short|varied|long|fragmented\n"
            f"\nText:\n{text[:3000]}\n\nReturn ONLY the JSON object, no explanation."
        )
        messages = [{"role": "user", "content": prompt}]

        if llm_completion_fn is None:
            try:
                from aifw.service import completion as aifw_completion
                llm_completion_fn = aifw_completion
            except ImportError as e:
                raise ImportError(
                    "aifw is required for StyleProfile.from_text(). "
                    "Install with: pip install aifw"
                ) from e

        result = await llm_completion_fn(action_code, messages)
        if not result.success:
            raise RuntimeError(f"Style analysis LLM call failed: {result.error}")

        content = result.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        data = json.loads(content.strip())
        return cls(**{k: v for k, v in data.items() if k in cls.model_fields})
