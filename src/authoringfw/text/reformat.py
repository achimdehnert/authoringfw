"""
TextReformatter — generic text transformation service.

Converts existing text into a different presentation format without
requiring domain-specific knowledge. Works with any LLM callable that
matches the simple ``(prompt: str) -> str`` signature.

Supported built-in target formats
----------------------------------
compact        One-paragraph executive overview, no headers.
bullets        Flat bullet list of key points, no headers.
structured     Sections with bold headers + bullet points per section.
narrative      Flowing prose, no bullets or markdown.
academic       Formal academic abstract style (Objective/Methods/Results/Conclusion).
qa             FAQ-style: question + short answer pairs.

Consumer can register custom formats via ``TextReformatter.register_format()``.

Design principles
-----------------
- No vendor lock-in: inject any ``(str) -> str`` callable.
- Sync-first; async wrapper provided via ``areformat()``.
- Pydantic v2 models for all I/O.
- Usable from iil-researchfw, bfagent, or any other package.

Example::

    from authoringfw.text import TextReformatter, ReformatTask

    reformat = TextReformatter(llm_fn=my_llm)
    result = reformat.reformat(ReformatTask(
        source_text=existing_summary,
        target_format="bullets",
        language="de",
    ))
    print(result.content)
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field

LLMFn = Callable[[str], str]
AsyncLLMFn = Callable[[str], "asyncio.Future[str]"]


# ---------------------------------------------------------------------------
# Format instructions registry
# ---------------------------------------------------------------------------

_FORMAT_INSTRUCTIONS: dict[str, str] = {
    "compact": (
        "Fasse den folgenden Text in einem einzigen, gut lesbaren Absatz zusammen. "
        "Keine Überschriften, keine Aufzählungen. Maximal 80 Wörter."
    ),
    "bullets": (
        "Extrahiere die wichtigsten Punkte als prägnante Stichpunkte. "
        "Format: jeder Punkt beginnt mit '- '. Keine Überschriften. Maximal 8 Punkte."
    ),
    "structured": (
        "Strukturiere den Text in thematische Abschnitte. "
        "Jeder Abschnitt beginnt mit einer fetten Überschrift **Titel** gefolgt "
        "von 2-4 Stichpunkten mit '- '. Keine Fließtextabsätze."
    ),
    "narrative": (
        "Schreibe den Text als flüssigen Fließtext ohne Markdown, ohne Aufzählungen "
        "und ohne Überschriften. Bewahre alle inhaltlichen Informationen."
    ),
    "academic": (
        "Forme den Text in einen wissenschaftlichen Abstract um. "
        "Format — gib NUR dieses Markdown aus:\n"
        "**Hintergrund**\n1-2 Sätze.\n\n"
        "**Methodik**\n1-2 Sätze.\n\n"
        "**Ergebnisse**\n2-3 Sätze oder Stichpunkte.\n\n"
        "**Schlussfolgerung**\n1-2 Sätze."
    ),
    "qa": (
        "Forme den Text in ein FAQ-Format um. "
        "Format:\n**Frage?**\nAntwort in 1-2 Sätzen.\n\n"
        "Erstelle 3-5 relevante Frage-Antwort-Paare."
    ),
}


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ReformatTask(BaseModel):
    """Input for TextReformatter."""

    model_config = ConfigDict(frozen=True)

    source_text: str = Field(description="Text to reformat")
    target_format: str = Field(
        default="bullets",
        description=(
            "Target format: compact | bullets | structured | narrative | "
            "academic | qa — or any registered custom format"
        ),
    )
    language: str = Field(
        default="de",
        description="Output language code (de, en, fr, …)",
    )
    max_tokens: int = Field(default=600, ge=50, le=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReformatResult(BaseModel):
    """Output from TextReformatter."""

    model_config = ConfigDict(frozen=True)

    content: str = Field(description="Reformatted text")
    target_format: str
    source_length: int = Field(description="Character count of source_text")
    success: bool = True
    error: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class TextReformatter:
    """
    Generic text transformation service.

    Inject any sync ``(prompt: str) -> str`` callable as ``llm_fn``.
    If no ``llm_fn`` is provided, a rule-based fallback is used for
    'bullets' and 'compact' — all other formats fall back to the source text.

    Usage::

        reformatter = TextReformatter(llm_fn=lambda p: my_llm(p))
        result = reformatter.reformat(ReformatTask(
            source_text="...",
            target_format="structured",
        ))
    """

    _registry: dict[str, str] = {}

    def __init__(self, llm_fn: LLMFn | None = None) -> None:
        self._llm_fn = llm_fn

    @classmethod
    def register_format(cls, name: str, instruction: str) -> None:
        """Register a custom reformat instruction under ``name``."""
        cls._registry[name] = instruction

    def _get_instruction(self, target_format: str, language: str) -> str:
        base = (
            self._registry.get(target_format)
            or _FORMAT_INSTRUCTIONS.get(target_format)
        )
        if not base:
            raise ValueError(
                f"Unknown target_format {target_format!r}. "
                f"Available: {list(_FORMAT_INSTRUCTIONS) + list(self._registry)}"
            )
        lang_suffix = (
            f" Schreibe auf Deutsch."
            if language == "de"
            else f" Write in {language}."
            if language != "de"
            else ""
        )
        return base + lang_suffix

    def _build_prompt(self, task: ReformatTask) -> str:
        instruction = self._get_instruction(task.target_format, task.language)
        return f"{instruction}\n\nText:\n{task.source_text[:6000]}"

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------

    def reformat(self, task: ReformatTask) -> ReformatResult:
        """Synchronously reformat ``task.source_text``."""
        if not task.source_text.strip():
            return ReformatResult(
                content="",
                target_format=task.target_format,
                source_length=0,
                success=False,
                error="source_text is empty",
            )
        if self._llm_fn is not None:
            return self._llm_reformat(task)
        return self._fallback_reformat(task)

    def _llm_reformat(self, task: ReformatTask) -> ReformatResult:
        assert self._llm_fn is not None
        try:
            prompt = self._build_prompt(task)
            content = self._llm_fn(prompt)
            return ReformatResult(
                content=content.strip(),
                target_format=task.target_format,
                source_length=len(task.source_text),
                metadata=task.metadata,
            )
        except Exception as exc:
            return ReformatResult(
                content=task.source_text,
                target_format=task.target_format,
                source_length=len(task.source_text),
                success=False,
                error=str(exc),
                metadata=task.metadata,
            )

    def _fallback_reformat(self, task: ReformatTask) -> ReformatResult:
        """Rule-based fallback when no LLM is available."""
        text = task.source_text
        if task.target_format == "bullets":
            content = _markdown_to_bullets(text)
        elif task.target_format == "compact":
            content = _markdown_to_compact(text)
        else:
            content = text
        return ReformatResult(
            content=content,
            target_format=task.target_format,
            source_length=len(text),
            metadata=task.metadata,
        )

    # ------------------------------------------------------------------
    # Async
    # ------------------------------------------------------------------

    async def areformat(self, task: ReformatTask) -> ReformatResult:
        """Async wrapper — runs sync reformat in executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.reformat, task)


# ---------------------------------------------------------------------------
# Rule-based fallback helpers
# ---------------------------------------------------------------------------

def _markdown_to_bullets(text: str) -> str:
    """Extract existing bullet lines or split sentences into bullets."""
    lines = text.splitlines()
    bullets = [
        line for line in lines
        if re.match(r"^\s*[-*•▸]\s+", line)
    ]
    if bullets:
        return "\n".join(bullets)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    return "\n".join(f"- {s}" for s in sentences[:8])


def _markdown_to_compact(text: str) -> str:
    """Strip markdown formatting and return first ~80 words."""
    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    clean = re.sub(r"^\s*[-*•▸]\s+", "", clean, flags=re.MULTILINE)
    clean = re.sub(r"\n+", " ", clean).strip()
    words = clean.split()
    return " ".join(words[:80]) + ("…" if len(words) > 80 else "")
