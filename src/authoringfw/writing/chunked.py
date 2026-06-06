"""
ChunkedChapterOrchestrator — writes long chapters via multi-chunk generation.

Solves the token-limit problem for chapters with 5,000–10,000+ words:
  - Calculates dynamic max_tokens from target_word_count
  - Splits into N chunks when target exceeds single-call capacity
  - Each chunk gets continuity context (previous content excerpt)
  - Graceful degradation: partial content on mid-chunk failure

Pattern extracted from bfagent ChapterWriterHandler (legacy, not developed further)
and elevated to authoringfw as the SSoT for writing orchestration.

Usage::

    orch = ChunkedChapterOrchestrator()
    result = orch.execute(ChapterTask(
        chapter_title="Der erste Schritt",
        chapter_outline="Protagonist trifft Mentor...",
        target_word_count=8000,
    ))

The orchestrator automatically decides single-shot vs chunked based on
target_word_count and the configured token budget.
"""

from __future__ import annotations

import logging

from authoringfw.exceptions import ConfigurationError, OrchestrationError
from authoringfw.types import ContentResult, ContentTask
from authoringfw.writing.chapter import ChapterOrchestrator
from authoringfw.writing.types import ChapterResult, ChapterTask

logger = logging.getLogger(__name__)

# German text: ~1.3–1.5 tokens per word. We use 1.5 for safety margin.
TOKENS_PER_WORD = 1.5
# Minimum max_tokens for any call (even short chapters)
MIN_MAX_TOKENS = 4000
# Default model output token limit (conservative)
DEFAULT_MODEL_MAX_TOKENS = 4096
# Overlap: chars of previous content included in continuation prompts
CONTINUATION_CONTEXT_CHARS = 3000


def compute_max_tokens(target_words: int) -> int:
    """Compute dynamic max_tokens from target word count.

    Formula: max(MIN_MAX_TOKENS, target_words * 2)
    The 2x factor accounts for ~1.5 tokens/word + formatting overhead.
    """
    return max(MIN_MAX_TOKENS, int(target_words * 2))


def compute_words_per_chunk(max_tokens: int) -> int:
    """How many words fit in a single LLM call given max_tokens."""
    return int(max_tokens / TOKENS_PER_WORD) - 200  # safety margin


class ChunkedChapterOrchestrator(ChapterOrchestrator):
    """
    ChapterOrchestrator with automatic chunked generation for long chapters.

    Inherits prompt building and result mapping from ChapterOrchestrator.
    Overrides execute() to split large chapters into multiple LLM calls.

    Token budget is computed dynamically from ChapterTask.target_word_count:
      - target_word_count <= words_per_chunk → single call (inherited)
      - target_word_count >  words_per_chunk → chunked generation

    Per-call overrides (model, max_tokens) can be set via
    ChapterTask.llm_overrides for premium quality tiers.
    """

    # Configurable via subclass or constructor
    model_max_tokens: int = DEFAULT_MODEL_MAX_TOKENS

    def __init__(self, model_max_tokens: int | None = None):
        if model_max_tokens is not None:
            self.model_max_tokens = model_max_tokens

    def execute(self, task: ContentTask) -> ContentResult:
        """Execute with automatic chunking for long chapters."""
        if not isinstance(task, ChapterTask):
            return super().execute(task)

        target_words = task.target_word_count
        dynamic_max_tokens = compute_max_tokens(target_words)
        words_per_chunk = compute_words_per_chunk(min(dynamic_max_tokens, self.model_max_tokens))

        if target_words <= words_per_chunk:
            # Single-shot: just set dynamic max_tokens and delegate
            enriched = self._enrich_task_with_tokens(task, dynamic_max_tokens)
            return super().execute(enriched)

        # Chunked generation
        return self._execute_chunked(task, dynamic_max_tokens, words_per_chunk)

    def _enrich_task_with_tokens(self, task: ChapterTask, max_tokens: int) -> ChapterTask:
        """Return a new ChapterTask with max_tokens set in llm_overrides."""
        overrides = dict(task.llm_overrides)
        overrides.setdefault("max_tokens", max_tokens)
        return task.model_copy(update={"llm_overrides": overrides})

    def _execute_chunked(
        self,
        task: ChapterTask,
        dynamic_max_tokens: int,
        words_per_chunk: int,
    ) -> ChapterResult:
        """Write a chapter in multiple chunks, concatenating results."""
        num_chunks = (task.target_word_count // words_per_chunk) + 1

        logger.info(
            "Chunked generation: %d words in %d chunks of ~%d words",
            task.target_word_count,
            num_chunks,
            words_per_chunk,
        )

        all_content: list[str] = []
        total_input_tokens = 0
        total_output_tokens = 0
        total_latency_ms = 0
        last_model = ""

        for chunk_num in range(num_chunks):
            is_first = chunk_num == 0
            is_last = chunk_num == num_chunks - 1

            # Build chunk-specific task with continuation context
            chunk_task = self._build_chunk_task(
                task,
                chunk_num=chunk_num,
                num_chunks=num_chunks,
                words_per_chunk=words_per_chunk,
                previous_content=all_content,
                is_first=is_first,
                is_last=is_last,
                max_tokens=dynamic_max_tokens,
            )

            try:
                result = super().execute(chunk_task)
            except (OrchestrationError, ConfigurationError) as exc:
                if all_content:
                    logger.warning(
                        "Chunk %d/%d failed, returning partial: %s",
                        chunk_num + 1,
                        num_chunks,
                        exc,
                    )
                    return self._build_partial_result(
                        task,
                        all_content,
                        total_input_tokens,
                        total_output_tokens,
                        total_latency_ms,
                        last_model,
                    )
                raise

            chunk_content = result.content.strip()
            all_content.append(chunk_content)
            total_input_tokens += result.input_tokens
            total_output_tokens += result.output_tokens
            total_latency_ms += result.latency_ms
            last_model = result.model

            logger.info(
                "Chunk %d/%d: %d words",
                chunk_num + 1,
                num_chunks,
                len(chunk_content.split()),
            )

        full_content = "\n\n".join(all_content)
        return ChapterResult(
            content=full_content,
            action_code=self.action_code,
            quality_level=task.quality_level,
            model=last_model,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            latency_ms=total_latency_ms,
            success=True,
            metadata=task.metadata,
            chapter_title=task.chapter_title,
            estimated_word_count=len(full_content.split()),
        )

    def _build_chunk_task(
        self,
        original: ChapterTask,
        *,
        chunk_num: int,
        num_chunks: int,
        words_per_chunk: int,
        previous_content: list[str],
        is_first: bool,
        is_last: bool,
        max_tokens: int,
    ) -> ChapterTask:
        """Build a ChapterTask for a specific chunk with continuation context."""
        if is_first:
            continuation = (
                f"Schreibe etwa {words_per_chunk} Wörter (Teil 1/{num_chunks}). "
                "Beginne mit einer fesselnden Eröffnung. "
                "ENDE NICHT — das Kapitel wird fortgesetzt."
            )
            outline = original.chapter_outline
        elif is_last:
            prev_text = "\n\n".join(previous_content[-2:])
            continuation = (
                f"BISHERIGER INHALT (Auszug):\n"
                f"{prev_text[-CONTINUATION_CONTEXT_CHARS:]}\n\n"
                f"Schreibe das ENDE des Kapitels ({words_per_chunk} Wörter, "
                f"Teil {chunk_num + 1}/{num_chunks}). "
                "Schließe das Kapitel befriedigend ab."
            )
            outline = continuation
        else:
            prev_text = "\n\n".join(previous_content[-2:])
            continuation = (
                f"BISHERIGER INHALT (Auszug):\n"
                f"{prev_text[-CONTINUATION_CONTEXT_CHARS:]}\n\n"
                f"Setze die Erzählung fort ({words_per_chunk} Wörter, "
                f"Teil {chunk_num + 1}/{num_chunks}). "
                "Führe die Handlung nahtlos weiter. ENDE NICHT."
            )
            outline = continuation

        overrides = dict(original.llm_overrides)
        overrides.setdefault("max_tokens", max_tokens)

        return ChapterTask(
            action_code=original.action_code,
            chapter_title=original.chapter_title,
            chapter_outline=outline,
            previous_summary=original.previous_summary if is_first else "",
            style_notes=original.style_notes,
            character_context=original.character_context,
            world_context=original.world_context,
            target_word_count=words_per_chunk,
            quality_level=original.quality_level,
            priority=original.priority,
            llm_overrides=overrides,
            metadata=original.metadata,
        )

    def _build_partial_result(
        self,
        task: ChapterTask,
        content_parts: list[str],
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        model: str,
    ) -> ChapterResult:
        """Build a ChapterResult from partial content (graceful degradation)."""
        partial = "\n\n".join(content_parts)
        partial += "\n\n[Generation vorzeitig abgebrochen]"
        return ChapterResult(
            content=partial,
            action_code=self.action_code,
            quality_level=task.quality_level,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            success=True,
            metadata=task.metadata,
            chapter_title=task.chapter_title,
            estimated_word_count=len(partial.split()),
        )
