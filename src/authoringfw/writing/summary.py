"""
SummaryOrchestrator — generates a brief/detailed/narrative summary of a text.

action_code: 'summary_writing'

Use case: after generating a chapter, summarise it for the next chapter's
'previous_summary' context. Keeps the running narrative context compact.
"""

from __future__ import annotations

from typing import Any

from authoringfw.base import BaseContentOrchestrator
from authoringfw.types import ContentTask
from authoringfw.writing.types import SummaryResult, SummaryTask

_STYLE_INSTRUCTIONS: dict[str, str] = {
    "brief": "Fasse den Text in 1-3 Sätzen zusammen. Nur die wichtigsten Ereignisse.",
    "detailed": (
        "Schreibe eine detaillierte Zusammenfassung mit allen wichtigen Ereignissen, "
        "Charakterentwicklungen und Wendepunkten."
    ),
    "narrative": (
        "Schreibe eine narrative Zusammenfassung im Stil eines Rückblicks. "
        "Bewahre die Atmosphäre und den Ton des Originals."
    ),
}


class SummaryOrchestrator(BaseContentOrchestrator):
    """
    Generates a summary of a given source text.

    Supports three styles: 'brief' (default), 'detailed', 'narrative'.

    Usage::

        orchestrator = SummaryOrchestrator()
        result = orchestrator.execute(SummaryTask(
            source_text=chapter_content,
            summary_style="brief",
            max_words=100,
        ))
        next_task = ChapterTask(
            ...,
            previous_summary=result.content,
        )
    """

    action_code = "summary_writing"  # I-096-04: class variable

    def _build_messages(
        self,
        task: ContentTask,
    ) -> list[dict[str, str]]:
        if isinstance(task, SummaryTask):
            return self._messages_from_summary_task(task)
        return self._messages_from_content_task(task)

    def _map_result(
        self,
        llm_result: Any,
        quality_level: int | None,  # I-096-02: explicit param
        task: ContentTask,
    ) -> SummaryResult:
        return SummaryResult(
            content=llm_result.content if llm_result.success else "",
            action_code=self.action_code,
            quality_level=quality_level,  # I-096-02
            model=getattr(llm_result, "model", ""),
            input_tokens=getattr(llm_result, "input_tokens", 0),
            output_tokens=getattr(llm_result, "output_tokens", 0),
            latency_ms=getattr(llm_result, "latency_ms", 0),
            success=getattr(llm_result, "success", True),
            metadata=task.metadata if isinstance(task, SummaryTask) else {},
        )

    def _messages_from_summary_task(
        self,
        task: SummaryTask,
    ) -> list[dict[str, str]]:
        style_instruction = _STYLE_INSTRUCTIONS.get(
            task.summary_style, _STYLE_INSTRUCTIONS["brief"]
        )
        system = (
            f"Du bist ein Assistent für Buchautoren. {style_instruction} "
            f"Maximal {task.max_words} Wörter. Antworte nur mit der Zusammenfassung, "
            "ohne Einleitung oder Erklärung."
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": task.source_text[:12000]},
        ]

    def _messages_from_content_task(
        self,
        task: ContentTask,
    ) -> list[dict[str, str]]:
        v = task.prompt_variables
        style = v.get("summary_style", "brief")
        max_words = v.get("max_words", 150)
        source = v.get("source_text", "")
        style_instruction = _STYLE_INSTRUCTIONS.get(style, _STYLE_INSTRUCTIONS["brief"])
        system = (
            f"Du bist ein Assistent für Buchautoren. {style_instruction} "
            f"Maximal {max_words} Wörter."
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": source[:12000]},
        ]
