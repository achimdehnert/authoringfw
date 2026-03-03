"""Tests for authoringfw.research sub-domain."""

import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from authoringfw.research import ResearchOrchestrator, ResearchResult, ResearchTask


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_llm_result(content="Research findings here.", success=True):
    r = MagicMock()
    r.content = content
    r.success = success
    r.model = "gpt-4o"
    r.input_tokens = 150
    r.output_tokens = 400
    r.latency_ms = 800
    return r


@pytest.fixture
def research_task():
    return ResearchTask(
        topic="Mittelalterliche Burgarchitektur",
        output_format="structured",
        max_words=300,
    )


# ── ResearchTask validation ──────────────────────────────────────────────────

def test_should_create_research_task_with_defaults(research_task):
    assert research_task.action_code == "research_query"
    assert research_task.output_format == "structured"
    assert research_task.max_words == 300
    assert research_task.quality_level is None


def test_should_reject_max_words_below_minimum():
    with pytest.raises(ValidationError):
        ResearchTask(topic="x", max_words=10)


def test_should_reject_max_words_above_maximum():
    with pytest.raises(ValidationError):
        ResearchTask(topic="x", max_words=99999)


def test_should_be_frozen(research_task):
    with pytest.raises(Exception):
        research_task.topic = "Modified"


def test_should_accept_all_output_formats():
    for fmt in ("structured", "bullets", "prose"):
        task = ResearchTask(topic="x", output_format=fmt)
        assert task.output_format == fmt


# ── ResearchOrchestrator._build_messages ─────────────────────────────────────

def test_should_build_messages_with_system_and_user(research_task):
    orch = ResearchOrchestrator()
    messages = orch._build_messages(research_task)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_should_include_topic_in_user_message(research_task):
    orch = ResearchOrchestrator()
    messages = orch._build_messages(research_task)
    assert "Burgarchitektur" in messages[1]["content"]


def test_should_include_max_words_in_system_message(research_task):
    orch = ResearchOrchestrator()
    messages = orch._build_messages(research_task)
    assert "300" in messages[0]["content"]


def test_should_use_structured_format_instructions(research_task):
    orch = ResearchOrchestrator()
    messages = orch._build_messages(research_task)
    assert "Abschnitt" in messages[0]["content"]


def test_should_use_bullets_format_instructions():
    task = ResearchTask(topic="Drachen", output_format="bullets")
    orch = ResearchOrchestrator()
    messages = orch._build_messages(task)
    assert "Stichpunkt" in messages[0]["content"]


def test_should_use_prose_format_instructions():
    task = ResearchTask(topic="Drachen", output_format="prose")
    orch = ResearchOrchestrator()
    messages = orch._build_messages(task)
    assert "Prosa" in messages[0]["content"]


def test_should_include_context_in_user_message_when_provided():
    task = ResearchTask(
        topic="Magie",
        context="Bereits bekannt: Magie existiert in dieser Welt.",
    )
    orch = ResearchOrchestrator()
    messages = orch._build_messages(task)
    assert "Bereits bekannt" in messages[1]["content"]


def test_should_not_include_context_section_when_empty(research_task):
    orch = ResearchOrchestrator()
    messages = orch._build_messages(research_task)
    assert "Vorhandener Kontext" not in messages[1]["content"]


# ── ResearchOrchestrator._map_result ─────────────────────────────────────────

def test_should_map_result_to_research_result(research_task):
    orch = ResearchOrchestrator()
    llm = _make_llm_result("## Burgtore\nSchwere Holztore...")
    result = orch._map_result(llm, quality_level=3, task=research_task)

    assert isinstance(result, ResearchResult)
    assert result.action_code == "research_query"
    assert result.quality_level == 3
    assert result.topic == "Mittelalterliche Burgarchitektur"
    assert result.structured_findings == result.content


def test_should_return_empty_content_on_failure(research_task):
    orch = ResearchOrchestrator()
    llm = _make_llm_result(content="ignored", success=False)
    result = orch._map_result(llm, quality_level=None, task=research_task)
    assert result.content == ""
    assert result.structured_findings == ""


# ── ResearchOrchestrator full execute ──────────────────────────────────────────

def test_should_execute_and_return_research_result(research_task):
    orch = ResearchOrchestrator()
    llm = _make_llm_result("## Architektur\nBurgen hatten Zugbrücken...")

    with patch.object(orch, "_get_action_config", return_value={"default_quality_level": 2}):
        with patch.object(orch, "_call_llm", return_value=llm):
            result = orch.execute(research_task)

    assert isinstance(result, ResearchResult)
    assert result.action_code == "research_query"
    assert result.model == "gpt-4o"
    assert "Zugbrücken" in result.structured_findings


# ── Pipeline: Research → Chapter (ADR-096 §4.5) ──────────────────────────────

def test_should_inject_structured_findings_into_chapter_task():
    from authoringfw.writing import ChapterOrchestrator, ChapterTask

    research_orch = ResearchOrchestrator()
    research_llm = _make_llm_result("## Burgtore\nSchwere Eichenholztore mit Fallgatter.")

    with patch.object(research_orch, "_get_action_config", return_value={}):
        with patch.object(research_orch, "_call_llm", return_value=research_llm):
            research_result = research_orch.execute(ResearchTask(
                topic="Mittelalterliche Burgtore",
            ))

    chapter_task = ChapterTask(
        chapter_title="Das Tor der Burg",
        chapter_outline="Held betritt die Burg durch das massive Tor.",
        world_context=research_result.structured_findings,
    )
    chapter_orch = ChapterOrchestrator()
    messages = chapter_orch._build_messages(chapter_task)

    assert "Eichenholztore" in messages[0]["content"]
