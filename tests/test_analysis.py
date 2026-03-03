"""Tests for authoringfw.analysis sub-domain."""

import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from authoringfw.analysis import (
    AnalysisResult,
    AnalysisTask,
    PlotAnalysisOrchestrator,
    StyleAnalysisOrchestrator,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

SAMPLE_TEXT = (
    "Die Stadt lag im Morgendunst. Der Held schritt durch das Tor, "
    "müde und voller Hoffnung zugleich. Er hatte keine Ahnung, was ihn erwartete."
)


def _make_llm_result(content="Analysis output.", success=True):
    r = MagicMock()
    r.content = content
    r.success = success
    r.model = "gpt-4o"
    r.input_tokens = 200
    r.output_tokens = 350
    r.latency_ms = 600
    return r


@pytest.fixture
def style_task():
    return AnalysisTask(
        action_code="style_analysis",
        source_text=SAMPLE_TEXT,
        output_format="structured",
    )


@pytest.fixture
def plot_task():
    return AnalysisTask(
        action_code="plot_analysis",
        source_text=SAMPLE_TEXT,
        output_format="structured",
    )


# ── AnalysisTask validation ─────────────────────────────────────────────────

def test_should_create_analysis_task_with_defaults(style_task):
    assert style_task.action_code == "style_analysis"
    assert style_task.output_format == "structured"
    assert style_task.analysis_focus == ""
    assert style_task.quality_level is None


def test_should_be_frozen(style_task):
    with pytest.raises(Exception):
        style_task.source_text = "Modified"


def test_should_reject_quality_level_out_of_range():
    with pytest.raises(ValidationError):
        AnalysisTask(action_code="style_analysis", source_text="x", quality_level=10)


# ── AnalysisResult validation ────────────────────────────────────────────────

def test_should_create_analysis_result_with_defaults():
    result = AnalysisResult(content="ok", action_code="style_analysis")
    assert result.score is None
    assert result.findings == []


def test_should_reject_score_out_of_range():
    with pytest.raises(ValidationError):
        AnalysisResult(content="ok", action_code="style_analysis", score=1.5)


# ── StyleAnalysisOrchestrator._build_messages ────────────────────────────────

def test_should_build_style_messages(style_task):
    orch = StyleAnalysisOrchestrator()
    messages = orch._build_messages(style_task)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_should_include_source_text_in_user_message(style_task):
    orch = StyleAnalysisOrchestrator()
    messages = orch._build_messages(style_task)
    assert "Morgendunst" in messages[1]["content"]


def test_should_include_style_analysis_criteria_in_system(style_task):
    orch = StyleAnalysisOrchestrator()
    messages = orch._build_messages(style_task)
    assert "Stilkonsistenz" in messages[0]["content"]
    assert "Wortwahl" in messages[0]["content"]


def test_should_include_focus_when_provided():
    task = AnalysisTask(
        action_code="style_analysis",
        source_text=SAMPLE_TEXT,
        analysis_focus="Dialogführung",
    )
    orch = StyleAnalysisOrchestrator()
    messages = orch._build_messages(task)
    assert "Dialogführung" in messages[0]["content"]


def test_should_include_score_instruction_when_format_is_score():
    task = AnalysisTask(
        action_code="style_analysis",
        source_text=SAMPLE_TEXT,
        output_format="score",
    )
    orch = StyleAnalysisOrchestrator()
    messages = orch._build_messages(task)
    assert "SCORE:" in messages[0]["content"]


def test_should_truncate_long_source_text():
    task = AnalysisTask(
        action_code="style_analysis",
        source_text="x" * 20000,
    )
    orch = StyleAnalysisOrchestrator()
    messages = orch._build_messages(task)
    assert len(messages[1]["content"]) <= 8000


# ── StyleAnalysisOrchestrator._map_result ──────────────────────────────────

def test_should_extract_score_from_content(style_task):
    orch = StyleAnalysisOrchestrator()
    llm = _make_llm_result("Gute Qualität.\n\nSCORE: 0.85")
    result = orch._map_result(llm, quality_level=None, task=style_task)
    assert result.score == pytest.approx(0.85)


def test_should_return_none_score_when_not_present(style_task):
    orch = StyleAnalysisOrchestrator()
    llm = _make_llm_result("Kein Score hier.")
    result = orch._map_result(llm, quality_level=None, task=style_task)
    assert result.score is None


def test_should_clamp_score_to_valid_range(style_task):
    orch = StyleAnalysisOrchestrator()
    llm = _make_llm_result("SCORE: 1.5")
    result = orch._map_result(llm, quality_level=None, task=style_task)
    assert result.score == pytest.approx(1.0)


def test_should_extract_bullet_findings(style_task):
    orch = StyleAnalysisOrchestrator()
    llm = _make_llm_result("Analyse:\n- Guter Rhythmus\n- POV inkonsistent\n- Starke Einleitung")
    result = orch._map_result(llm, quality_level=None, task=style_task)
    assert len(result.findings) == 3
    assert "Guter Rhythmus" in result.findings


def test_should_return_empty_content_on_failure(style_task):
    orch = StyleAnalysisOrchestrator()
    llm = _make_llm_result(content="ignored", success=False)
    result = orch._map_result(llm, quality_level=None, task=style_task)
    assert result.content == ""
    assert result.findings == []


# ── StyleAnalysisOrchestrator full execute ───────────────────────────────────

def test_should_execute_style_analysis(style_task):
    orch = StyleAnalysisOrchestrator()
    llm = _make_llm_result("Sehr guter Stil.\n- Konsistenter Ton\n- Klare Struktur\nSCORE: 0.9")

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm", return_value=llm):
            result = orch.execute(style_task)

    assert isinstance(result, AnalysisResult)
    assert result.action_code == "style_analysis"
    assert result.score == pytest.approx(0.9)
    assert len(result.findings) >= 1


# ── PlotAnalysisOrchestrator._build_messages ────────────────────────────────

def test_should_build_plot_messages(plot_task):
    orch = PlotAnalysisOrchestrator()
    messages = orch._build_messages(plot_task)
    assert len(messages) == 2
    assert "Spannungskurve" in messages[0]["content"]
    assert "Charakterentwicklung" in messages[0]["content"]


def test_should_include_plot_focus_when_provided():
    task = AnalysisTask(
        action_code="plot_analysis",
        source_text=SAMPLE_TEXT,
        analysis_focus="Wendepunkte",
    )
    orch = PlotAnalysisOrchestrator()
    messages = orch._build_messages(task)
    assert "Wendepunkte" in messages[0]["content"]


# ── PlotAnalysisOrchestrator full execute ───────────────────────────────────

def test_should_execute_plot_analysis(plot_task):
    orch = PlotAnalysisOrchestrator()
    llm = _make_llm_result("Solide Spannungskurve.\n- Guter Einstieg\n- Schwaches Ende")

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm", return_value=llm):
            result = orch.execute(plot_task)

    assert isinstance(result, AnalysisResult)
    assert result.action_code == "plot_analysis"
    assert len(result.findings) == 2


# ── Cross-domain: Chapter → StyleAnalysis ───────────────────────────────────

def test_should_pipeline_chapter_into_style_analysis():
    from authoringfw.writing import ChapterOrchestrator, ChapterTask

    chapter_orch = ChapterOrchestrator()
    chapter_llm = MagicMock()
    chapter_llm.content = "Es war einmal ein Held der auszog das Fürchten zu lernen."
    chapter_llm.success = True
    chapter_llm.model = "gpt-4o"
    chapter_llm.input_tokens = 100
    chapter_llm.output_tokens = 200
    chapter_llm.latency_ms = 500

    with patch.object(chapter_orch, "_get_action_config", return_value={}):
        with patch.object(chapter_orch, "_call_llm", return_value=chapter_llm):
            chapter_result = chapter_orch.execute(ChapterTask(
                chapter_title="Kapitel 1",
                chapter_outline="Held bricht auf.",
            ))

    analysis_task = AnalysisTask(
        action_code="style_analysis",
        source_text=chapter_result.content,
        output_format="score",
    )
    orch = StyleAnalysisOrchestrator()
    messages = orch._build_messages(analysis_task)
    assert "Fürchten" in messages[1]["content"]
    assert "SCORE:" in messages[0]["content"]
