"""
ChapterOrchestrator — generates a chapter from outline + narrative context.

action_code: 'chapter_writing'

Prompt strategy:
  - System: role + style notes + world context + character context
  - User: chapter title + outline + previous summary + word count target

The orchestrator is context-free (stateless). All context must be
provided in ChapterTask. Use ConsistencyChecker post-generation for
rule-based validation.
"""

from __future__ import annotations

from typing import Any

from authoringfw.base import BaseContentOrchestrator
from authoringfw.types import ContentTask
from authoringfw.writing.types import ChapterResult, ChapterTask


class ChapterOrchestrator(BaseContentOrchestrator):
    """
    Generates a chapter from a beat-sheet outline and narrative context.

    Usage::

        orchestrator = ChapterOrchestrator()
        result = orchestrator.execute(ChapterTask(
            chapter_title="Der erste Schritt",
            chapter_outline="Protagonist trifft den Mentor...",
        ))

    The execute() method is inherited from BaseContentOrchestrator.
    It calls _build_messages() → aifw.sync_completion() → _map_result().
    """

    action_code = "chapter_writing"  # I-096-04: class variable

    def _build_messages(
        self,
        task: ContentTask,
    ) -> list[dict[str, str]]:
        """
        Build the LLM message list for chapter generation.

        Accepts both ChapterTask (preferred) and generic ContentTask
        (uses prompt_variables fallback for each field).
        """
        if isinstance(task, ChapterTask):
            return self._messages_from_chapter_task(task)
        return self._messages_from_content_task(task)

    def _map_result(
        self,
        llm_result: Any,
        quality_level: int | None,  # I-096-02: explicit param
        task: ContentTask,
    ) -> ChapterResult:
        chapter_title = (
            task.chapter_title
            if isinstance(task, ChapterTask)
            else task.prompt_variables.get("chapter_title", "")
        )
        content = llm_result.content if llm_result.success else ""
        return ChapterResult(
            content=content,
            action_code=self.action_code,
            quality_level=quality_level,  # I-096-02
            model=getattr(llm_result, "model", ""),
            input_tokens=getattr(llm_result, "input_tokens", 0),
            output_tokens=getattr(llm_result, "output_tokens", 0),
            latency_ms=getattr(llm_result, "latency_ms", 0),
            success=getattr(llm_result, "success", True),
            metadata=task.metadata if isinstance(task, ChapterTask) else {},
            chapter_title=chapter_title,
            estimated_word_count=len(content.split()),
        )

    def _messages_from_chapter_task(
        self,
        task: ChapterTask,
    ) -> list[dict[str, str]]:
        system_parts = [
            "Du bist ein professioneller Autor. "
            "Schreibe den folgenden Buchkapitel als fortlaufenden Prosa-Text.",
        ]
        if task.style_notes:
            system_parts.append(f"Stil-Vorgaben: {task.style_notes}")
        if task.world_context:
            system_parts.append(f"Welt-Kontext:\n{task.world_context}")
        if task.character_context:
            system_parts.append(f"Charaktere:\n{task.character_context}")

        user_parts = [f"# Kapitel: {task.chapter_title}"]
        if task.previous_summary:
            user_parts.append(f"**Vorheriges Kapitel (Zusammenfassung):**\n{task.previous_summary}")
        user_parts.append(f"**Outline / Beat Sheet:**\n{task.chapter_outline}")
        user_parts.append(
            f"Schreibe ca. {task.target_word_count} Wörter. "
            "Beginne direkt mit dem Kapiteltext, ohne Titel-Wiederholung."
        )

        return [
            {"role": "system", "content": "\n\n".join(system_parts)},
            {"role": "user", "content": "\n\n".join(user_parts)},
        ]

    def _messages_from_content_task(
        self,
        task: ContentTask,
    ) -> list[dict[str, str]]:
        v = task.prompt_variables
        system = (
            "Du bist ein professioneller Autor. "
            "Schreibe den folgenden Buchkapitel als fortlaufenden Prosa-Text."
        )
        if v.get("style_notes"):
            system += f"\n\nStil-Vorgaben: {v['style_notes']}"
        if v.get("world_context"):
            system += f"\n\nWelt-Kontext:\n{v['world_context']}"
        if v.get("character_context"):
            system += f"\n\nCharaktere:\n{v['character_context']}"

        title = v.get("chapter_title", "Kapitel")
        outline = v.get("chapter_outline", "")
        previous = v.get("previous_summary", "")
        word_count = v.get("target_word_count", 2000)

        user_parts = [f"# Kapitel: {title}"]
        if previous:
            user_parts.append(f"**Vorheriges Kapitel:**\n{previous}")
        if outline:
            user_parts.append(f"**Outline:**\n{outline}")
        user_parts.append(f"Schreibe ca. {word_count} Wörter.")

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": "\n\n".join(user_parts)},
        ]
