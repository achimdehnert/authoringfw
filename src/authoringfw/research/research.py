"""
ResearchOrchestrator — extracts structured research from a topic query.

action_code: 'research_query'

Output is designed to be injected directly into ChapterTask.world_context
for the Research → Writing pipeline (ADR-096 §4.5).
"""

from __future__ import annotations

from typing import Any

from authoringfw.base import BaseContentOrchestrator
from authoringfw.types import ContentTask
from authoringfw.research.types import ResearchResult, ResearchTask

_FORMAT_INSTRUCTIONS: dict[str, str] = {
    "structured": (
        "Antworte in klar gegliederten Abschnitten mit Überschriften. "
        "Jeder Abschnitt hat 2-4 Sätze. Keine Einleitung, kein Fazit."
    ),
    "bullets": (
        "Antworte als strukturierte Stichpunktliste. "
        "Jeder Punkt ist prägnant und eigenständig verständlich."
    ),
    "prose": (
        "Antworte als fließender Prosa-Text in einem klaren, sachlichen Stil."
    ),
}


class ResearchOrchestrator(BaseContentOrchestrator):
    """
    Extracts structured research from a topic query for use in writing pipelines.

    Usage::

        from authoringfw.research import ResearchOrchestrator, ResearchTask
        from authoringfw.writing import ChapterOrchestrator, ChapterTask

        research = ResearchOrchestrator().execute(ResearchTask(
            topic="Mittelalterliche Burgarchitektur",
            output_format="structured",
        ))
        chapter = ChapterOrchestrator().execute(ChapterTask(
            chapter_title="Die Burg",
            chapter_outline="Held betritt die Burg...",
            world_context=research.structured_findings,
        ))
    """

    action_code = "research_query"

    def _build_messages(
        self,
        task: ContentTask,
    ) -> list[dict[str, str]]:
        if isinstance(task, ResearchTask):
            return self._messages_from_research_task(task)
        return self._messages_from_content_task(task)

    def _map_result(
        self,
        llm_result: Any,
        quality_level: int | None,
        task: ContentTask,
    ) -> ResearchResult:
        content = llm_result.content if llm_result.success else ""
        topic = task.topic if isinstance(task, ResearchTask) else task.prompt_variables.get("topic", "")
        return ResearchResult(
            content=content,
            action_code=self.action_code,
            quality_level=quality_level,
            model=getattr(llm_result, "model", ""),
            input_tokens=getattr(llm_result, "input_tokens", 0),
            output_tokens=getattr(llm_result, "output_tokens", 0),
            latency_ms=getattr(llm_result, "latency_ms", 0),
            success=getattr(llm_result, "success", True),
            metadata=task.metadata if isinstance(task, ResearchTask) else {},
            structured_findings=content,
            topic=topic,
        )

    def _messages_from_research_task(
        self,
        task: ResearchTask,
    ) -> list[dict[str, str]]:
        fmt = _FORMAT_INSTRUCTIONS.get(task.output_format, _FORMAT_INSTRUCTIONS["structured"])
        system = (
            f"Du bist ein Recherche-Assistent für Buchautoren. {fmt} "
            f"Maximal {task.max_words} Wörter. Nur Fakten und Details, "
            "die direkt für das Schreiben von Prosa nützlich sind."
        )
        user_parts = [f"Recherchiere: {task.topic}"]
        if task.context:
            user_parts.append(f"Vorhandener Kontext:\n{task.context}")

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": "\n\n".join(user_parts)},
        ]

    def _messages_from_content_task(
        self,
        task: ContentTask,
    ) -> list[dict[str, str]]:
        v = task.prompt_variables
        topic = v.get("topic", "")
        fmt_key = v.get("output_format", "structured")
        max_words = v.get("max_words", 500)
        fmt = _FORMAT_INSTRUCTIONS.get(fmt_key, _FORMAT_INSTRUCTIONS["structured"])
        system = f"Du bist ein Recherche-Assistent für Buchautoren. {fmt} Maximal {max_words} Wörter."
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Recherchiere: {topic}"},
        ]
