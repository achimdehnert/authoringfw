"""Tests for authoringfw.writing sub-domain."""

import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from authoringfw.writing import (
    ChapterOrchestrator,
    ChapterResult,
    ChapterTask,
    SummaryOrchestrator,
    SummaryResult,
    SummaryTask,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_llm_result(content="Chapter text here", success=True):
    r = MagicMock()
    r.content = content
    r.success = success
    r.model = "gpt-4o"
    r.input_tokens = 200
    r.output_tokens = 800
    r.latency_ms = 1200
    return r


@pytest.fixture
def chapter_task():
    return ChapterTask(
        chapter_title="Der erste Schritt",
        chapter_outline="Protagonist trifft Mentor. Mentor offenbart Geheimnis.",
        previous_summary="In Kapitel 1 erwachte die Magie.",
        style_notes="3. Person, Präteritum, atmosphärisch",
        target_word_count=500,
    )


@pytest.fixture
def summary_task():
    return SummaryTask(
        source_text="Ein langer Text über den Protagonisten der seine Reise beginnt...",
        summary_style="brief",
        max_words=50,
    )


# ── ChapterTask validation ────────────────────────────────────────────────────

def test_should_create_chapter_task_with_defaults(chapter_task):
    assert chapter_task.action_code == "chapter_writing"
    assert chapter_task.target_word_count == 500
    assert chapter_task.quality_level is None
    assert chapter_task.priority is None


def test_should_reject_word_count_below_minimum():
    with pytest.raises(ValidationError):
        ChapterTask(chapter_title="X", chapter_outline="Y", target_word_count=50)


def test_should_reject_word_count_above_maximum():
    with pytest.raises(ValidationError):
        ChapterTask(chapter_title="X", chapter_outline="Y", target_word_count=99999)


def test_should_reject_quality_level_out_of_range():
    with pytest.raises(ValidationError):
        ChapterTask(chapter_title="X", chapter_outline="Y", quality_level=10)


def test_should_be_frozen(chapter_task):
    with pytest.raises(Exception):
        chapter_task.chapter_title = "Modified"


# ── ChapterOrchestrator._build_messages ──────────────────────────────────────

def test_should_build_messages_with_system_and_user(chapter_task):
    orch = ChapterOrchestrator()
    messages = orch._build_messages(chapter_task)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_should_include_title_in_user_message(chapter_task):
    orch = ChapterOrchestrator()
    messages = orch._build_messages(chapter_task)
    assert "Der erste Schritt" in messages[1]["content"]


def test_should_include_outline_in_user_message(chapter_task):
    orch = ChapterOrchestrator()
    messages = orch._build_messages(chapter_task)
    assert "Mentor" in messages[1]["content"]


def test_should_include_previous_summary_when_provided(chapter_task):
    orch = ChapterOrchestrator()
    messages = orch._build_messages(chapter_task)
    assert "Kapitel 1" in messages[1]["content"]


def test_should_include_style_notes_in_system_message(chapter_task):
    orch = ChapterOrchestrator()
    messages = orch._build_messages(chapter_task)
    assert "atmosph" in messages[0]["content"]


def test_should_include_word_count_in_user_message(chapter_task):
    orch = ChapterOrchestrator()
    messages = orch._build_messages(chapter_task)
    assert "500" in messages[1]["content"]


def test_should_include_world_context_in_system_when_provided():
    task = ChapterTask(
        chapter_title="X",
        chapter_outline="Y",
        world_context="Fantasy world with dragons.",
    )
    orch = ChapterOrchestrator()
    messages = orch._build_messages(task)
    assert "Fantasy world" in messages[0]["content"]


# ── ChapterOrchestrator._map_result ──────────────────────────────────────────

def test_should_map_result_to_chapter_result(chapter_task):
    orch = ChapterOrchestrator()
    llm = _make_llm_result("Beautiful prose.")
    result = orch._map_result(llm, quality_level=3, task=chapter_task)

    assert isinstance(result, ChapterResult)
    assert result.content == "Beautiful prose."
    assert result.quality_level == 3
    assert result.chapter_title == "Der erste Schritt"
    assert result.estimated_word_count == 2  # "Beautiful prose."


def test_should_use_explicit_quality_level_not_from_llm_result(chapter_task):
    """I-096-02: quality_level must come from param, not llm_result."""
    orch = ChapterOrchestrator()
    llm = _make_llm_result()
    # llm_result has no quality_level attr — this must not raise
    result = orch._map_result(llm, quality_level=7, task=chapter_task)
    assert result.quality_level == 7


# ── ChapterOrchestrator full execute (mocked aifw) ───────────────────────────

def test_should_execute_and_return_chapter_result(chapter_task):
    orch = ChapterOrchestrator()
    llm = _make_llm_result("Once upon a time...")

    with patch.object(orch, "_get_action_config", return_value={"default_quality_level": 2}):
        with patch.object(orch, "_call_llm", return_value=llm):
            result = orch.execute(chapter_task)

    assert isinstance(result, ChapterResult)
    assert result.content == "Once upon a time..."
    assert result.action_code == "chapter_writing"
    assert result.model == "gpt-4o"


# ── SummaryTask validation ────────────────────────────────────────────────────

def test_should_create_summary_task_with_defaults(summary_task):
    assert summary_task.action_code == "summary_writing"
    assert summary_task.summary_style == "brief"
    assert summary_task.max_words == 50


def test_should_reject_max_words_below_minimum():
    with pytest.raises(ValidationError):
        SummaryTask(source_text="x", max_words=5)


# ── SummaryOrchestrator._build_messages ──────────────────────────────────────

def test_should_build_summary_messages(summary_task):
    orch = SummaryOrchestrator()
    messages = orch._build_messages(summary_task)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "50" in messages[0]["content"]


def test_should_use_correct_style_instruction_brief(summary_task):
    orch = SummaryOrchestrator()
    messages = orch._build_messages(summary_task)
    assert "1-3" in messages[0]["content"]


def test_should_use_correct_style_instruction_detailed():
    task = SummaryTask(source_text="long text", summary_style="detailed")
    orch = SummaryOrchestrator()
    messages = orch._build_messages(task)
    assert "detailliert" in messages[0]["content"]


def test_should_use_correct_style_instruction_narrative():
    task = SummaryTask(source_text="long text", summary_style="narrative")
    orch = SummaryOrchestrator()
    messages = orch._build_messages(task)
    assert "narrativ" in messages[0]["content"]


def test_should_truncate_long_source_text():
    task = SummaryTask(source_text="x" * 20000, summary_style="brief")
    orch = SummaryOrchestrator()
    messages = orch._build_messages(task)
    assert len(messages[1]["content"]) <= 12000


# ── SummaryOrchestrator full execute ─────────────────────────────────────────

def test_should_execute_summary_and_return_result(summary_task):
    orch = SummaryOrchestrator()
    llm = _make_llm_result("Held beginnt Reise.")

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm", return_value=llm):
            result = orch.execute(summary_task)

    assert isinstance(result, SummaryResult)
    assert result.content == "Held beginnt Reise."
    assert result.action_code == "summary_writing"


# ── Pipeline: Chapter → Summary → next Chapter ───────────────────────────────

def test_should_pipeline_summary_into_next_chapter():
    """ADR-096 §4.5: Research → Writing pipeline pattern."""
    chapter_orch = ChapterOrchestrator()
    summary_orch = SummaryOrchestrator()

    chapter_llm = _make_llm_result("Das war Kapitel 1...")
    summary_llm = _make_llm_result("Held trifft Mentor.")

    with patch.object(chapter_orch, "_get_action_config", return_value={}):
        with patch.object(chapter_orch, "_call_llm", return_value=chapter_llm):
            chapter_result = chapter_orch.execute(ChapterTask(
                chapter_title="Kapitel 1",
                chapter_outline="Held wird gerufen.",
            ))

    with patch.object(summary_orch, "_get_action_config", return_value={}):
        with patch.object(summary_orch, "_call_llm", return_value=summary_llm):
            summary_result = summary_orch.execute(SummaryTask(
                source_text=chapter_result.content,
            ))

    next_task = ChapterTask(
        chapter_title="Kapitel 2",
        chapter_outline="Held bricht auf.",
        previous_summary=summary_result.content,
    )
    assert next_task.previous_summary == "Held trifft Mentor."
