"""Tests for authoringfw.writing.chunked — ChunkedChapterOrchestrator."""

import pytest
from unittest.mock import MagicMock, patch

from authoringfw.writing import (
    ChapterOrchestrator,
    ChapterTask,
    ChapterResult,
    ChunkedChapterOrchestrator,
    compute_max_tokens,
    compute_words_per_chunk,
)


# ── Helper ────────────────────────────────────────────────────────────────────

def _make_llm_result(content="Generated chapter text here", success=True):
    r = MagicMock()
    r.content = content
    r.success = success
    r.model = "gpt-4o"
    r.input_tokens = 200
    r.output_tokens = 800
    r.latency_ms = 1200
    return r


# ── compute_max_tokens ────────────────────────────────────────────────────────

def test_compute_max_tokens_minimum():
    """Short chapters should still get MIN_MAX_TOKENS."""
    assert compute_max_tokens(100) == 4000
    assert compute_max_tokens(1000) == 4000


def test_compute_max_tokens_scales_with_words():
    """Large chapters scale: target_words * 2."""
    assert compute_max_tokens(5000) == 10000
    assert compute_max_tokens(10000) == 20000


def test_compute_words_per_chunk():
    """Words per chunk = max_tokens / 1.5 - 200 safety."""
    result = compute_words_per_chunk(4096)
    assert 2400 < result < 2800  # ~2531


# ── ChunkedChapterOrchestrator: single-shot for short chapters ────────────────

def test_short_chapter_uses_single_shot():
    """Chapters under words_per_chunk threshold use single execute()."""
    orch = ChunkedChapterOrchestrator(model_max_tokens=4096)
    task = ChapterTask(
        chapter_title="Short Chapter",
        chapter_outline="A brief scene.",
        target_word_count=1000,
    )

    llm = _make_llm_result("Short chapter content.")
    with patch.object(ChapterOrchestrator, "execute", return_value=ChapterResult(
        content="Short chapter content.",
        action_code="chapter_writing",
        model="gpt-4o",
        success=True,
        chapter_title="Short Chapter",
        estimated_word_count=3,
    )) as mock_execute:
        result = orch.execute(task)

    assert mock_execute.called
    # The enriched task should have max_tokens in llm_overrides
    called_task = mock_execute.call_args[0][0]
    assert called_task.llm_overrides.get("max_tokens") == 4000  # min for 1000 words


def test_short_chapter_preserves_existing_overrides():
    """Existing llm_overrides (e.g. model) should be preserved."""
    orch = ChunkedChapterOrchestrator(model_max_tokens=4096)
    task = ChapterTask(
        chapter_title="Premium Chapter",
        chapter_outline="A scene.",
        target_word_count=1000,
        llm_overrides={"model": "openai:gpt-4o"},
    )

    with patch.object(ChapterOrchestrator, "execute", return_value=ChapterResult(
        content="Premium content.",
        action_code="chapter_writing",
        model="gpt-4o",
        success=True,
        chapter_title="Premium Chapter",
        estimated_word_count=2,
    )) as mock_execute:
        result = orch.execute(task)

    called_task = mock_execute.call_args[0][0]
    assert called_task.llm_overrides.get("model") == "openai:gpt-4o"
    assert called_task.llm_overrides.get("max_tokens") == 4000


# ── ChunkedChapterOrchestrator: chunked for long chapters ─────────────────────

def test_long_chapter_uses_chunked_generation():
    """Chapters over words_per_chunk should trigger multi-chunk."""
    orch = ChunkedChapterOrchestrator(model_max_tokens=4096)
    # 8000 words >> ~2500 words_per_chunk → should chunk
    task = ChapterTask(
        chapter_title="Long Chapter",
        chapter_outline="A very long detailed scene.",
        target_word_count=8000,
    )

    chunk_result = ChapterResult(
        content="Generated chunk content " * 300,
        action_code="chapter_writing",
        model="gpt-4o",
        input_tokens=200,
        output_tokens=800,
        latency_ms=1200,
        success=True,
        chapter_title="Long Chapter",
        estimated_word_count=600,
    )

    call_count = 0

    def mock_execute(t):
        nonlocal call_count
        call_count += 1
        return chunk_result

    with patch.object(ChapterOrchestrator, "execute", side_effect=mock_execute):
        result = orch.execute(task)

    # Should have called execute multiple times (chunked)
    assert call_count > 1
    assert isinstance(result, ChapterResult)
    assert result.success
    assert result.estimated_word_count > 0


def test_chunked_accumulates_tokens_and_latency():
    """Token counts and latency should be summed across chunks."""
    orch = ChunkedChapterOrchestrator(model_max_tokens=4096)
    task = ChapterTask(
        chapter_title="Long",
        chapter_outline="Scene.",
        target_word_count=8000,
    )

    chunk_result = ChapterResult(
        content="Chunk text.",
        action_code="chapter_writing",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=500,
        latency_ms=1000,
        success=True,
        chapter_title="Long",
        estimated_word_count=2,
    )

    with patch.object(ChapterOrchestrator, "execute", return_value=chunk_result):
        result = orch.execute(task)

    # Multiple chunks → accumulated metrics
    assert result.input_tokens >= 100
    assert result.output_tokens >= 500
    assert result.latency_ms >= 1000


# ── Graceful degradation ──────────────────────────────────────────────────────

def test_partial_content_on_mid_chunk_failure():
    """If a chunk fails after some succeed, return partial content."""
    from authoringfw.exceptions import OrchestrationError

    orch = ChunkedChapterOrchestrator(model_max_tokens=4096)
    task = ChapterTask(
        chapter_title="Failing",
        chapter_outline="Scene.",
        target_word_count=8000,
    )

    call_count = 0

    def mock_execute(t):
        nonlocal call_count
        call_count += 1
        if call_count > 1:
            raise OrchestrationError("LLM timeout", action_code="chapter_writing")
        return ChapterResult(
            content="First chunk content.",
            action_code="chapter_writing",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=500,
            latency_ms=1000,
            success=True,
            chapter_title="Failing",
            estimated_word_count=3,
        )

    with patch.object(ChapterOrchestrator, "execute", side_effect=mock_execute):
        result = orch.execute(task)

    assert result.success  # partial is still "success"
    assert "First chunk content." in result.content
    assert "abgebrochen" in result.content


# ── llm_overrides pass-through ────────────────────────────────────────────────

def test_llm_overrides_forwarded_to_content_task():
    """ContentTask.llm_overrides should exist and default to empty dict."""
    from authoringfw.types import ContentTask

    task = ContentTask(action_code="test")
    assert task.llm_overrides == {}

    task_with = ContentTask(
        action_code="test",
        llm_overrides={"max_tokens": 8000, "model": "openai:gpt-4o"},
    )
    assert task_with.llm_overrides == {"max_tokens": 8000, "model": "openai:gpt-4o"}


def test_chapter_task_supports_llm_overrides():
    """ChapterTask should support llm_overrides field."""
    task = ChapterTask(
        chapter_title="X",
        chapter_outline="Y",
        llm_overrides={"model": "openai:gpt-4o"},
    )
    assert task.llm_overrides == {"model": "openai:gpt-4o"}
