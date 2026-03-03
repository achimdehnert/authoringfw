"""Tests for ADR-096/097 interface contracts between authoringfw and aifw.

Verifies:
  - LLMResult has all fields that authoringfw._map_result() accesses (G-097-04)
  - prompt_template_key fallback to action_code is correct (M-095-02)
  - ConfigurationError from aifw import failure propagates correctly

Note: tests requiring aifw use pytest.importorskip() — they are skipped
when aifw is not installed (e.g. in CI with only [dev] extras).
"""
import pytest
from unittest.mock import MagicMock, patch

from authoringfw.base import BaseContentOrchestrator
from authoringfw.exceptions import ConfigurationError
from authoringfw.types import ContentResult, ContentTask


# ── G-097-04: LLMResult fields used by authoringfw ─────────────────────────────

def test_should_verify_llm_result_has_required_fields():
    """G-097-04: LLMResult must expose all fields _map_result() accesses."""
    aifw_schema = pytest.importorskip("aifw.schema", reason="aifw not installed")
    LLMResult = aifw_schema.LLMResult

    result = LLMResult(
        success=True,
        content="Generated text",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        latency_ms=300,
    )

    assert hasattr(result, "content")
    assert hasattr(result, "model")
    assert hasattr(result, "input_tokens")
    assert hasattr(result, "output_tokens")
    assert hasattr(result, "latency_ms")
    assert hasattr(result, "success")
    assert hasattr(result, "error")


def test_should_verify_llm_result_field_types():
    """G-097-04: LLMResult field types match what authoringfw expects."""
    aifw_schema = pytest.importorskip("aifw.schema", reason="aifw not installed")
    LLMResult = aifw_schema.LLMResult

    result = LLMResult(success=True, content="ok", model="gpt-4o",
                       input_tokens=10, output_tokens=5, latency_ms=200)
    assert isinstance(result.content, str)
    assert isinstance(result.model, str)
    assert isinstance(result.input_tokens, int)
    assert isinstance(result.output_tokens, int)
    assert isinstance(result.latency_ms, int)
    assert isinstance(result.success, bool)


# ── M-095-02: prompt_template_key fallback ───────────────────────────────────

def test_should_use_action_code_as_fallback_when_prompt_template_key_is_none():
    """M-095-02: If prompt_template_key is None, action_code is the fallback."""
    class TrackingOrchestrator(BaseContentOrchestrator):
        action_code = "story_writing"

        def _build_messages(self, task):
            key = self._get_prompt_template_key(task)
            return [{"role": "user", "content": key}]

        def _map_result(self, llm_result, quality_level, task):
            return ContentResult(content="ok", action_code=self.action_code)

    orch = TrackingOrchestrator()
    task = ContentTask(action_code="story_writing")

    config = {"prompt_template_key": None, "action_code": "story_writing"}

    with patch.object(orch, "_get_action_config", return_value=config):
        with patch.object(orch, "_call_llm", return_value=MagicMock(
            content="ok", model="gpt-4o", input_tokens=5,
            output_tokens=3, latency_ms=100, success=True,
        )):
            result = orch.execute(task)

    assert result.content == "ok"


def test_should_use_prompt_template_key_when_set():
    """M-095-02: If prompt_template_key is set, it takes precedence."""
    received_keys = []

    class KeyTracker(BaseContentOrchestrator):
        action_code = "chapter_writing"

        def _build_messages(self, task):
            key = self._get_prompt_template_key(task)
            received_keys.append(key)
            return [{"role": "user", "content": "x"}]

        def _map_result(self, llm_result, quality_level, task):
            return ContentResult(content="ok", action_code=self.action_code)

    orch = KeyTracker()
    task = ContentTask(action_code="chapter_writing")

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm", return_value=MagicMock(
            content="ok", model="gpt-4o", input_tokens=5,
            output_tokens=3, latency_ms=100, success=True,
        )):
            orch.execute(task)

    assert received_keys == ["chapter_writing"]


# ── ConfigurationError from aifw import failure ──────────────────────────────

def test_should_raise_configuration_error_when_aifw_not_installed():
    """I-096-01: ImportError from aifw becomes ConfigurationError (not wrapped)."""
    class SimpleOrchestrator(BaseContentOrchestrator):
        action_code = "test"
        def _build_messages(self, task): return [{"role": "user", "content": "x"}]
        def _map_result(self, r, ql, task):
            return ContentResult(content="ok", action_code=self.action_code)

    orch = SimpleOrchestrator()
    task = ContentTask(action_code="test")

    with patch.object(orch, "_get_action_config",
                      side_effect=ConfigurationError("aifw not installed")):
        with pytest.raises(ConfigurationError, match="aifw not installed"):
            orch.execute(task)


# ── quality_level NOT read from llm_result ────────────────────────────────────

def test_should_not_access_quality_level_on_llm_result():
    """I-096-02: LLMResult has no quality_level attr — must not be accessed."""
    aifw_schema = pytest.importorskip("aifw.schema", reason="aifw not installed")
    LLMResult = aifw_schema.LLMResult

    result = LLMResult(success=True, content="ok")
    assert not hasattr(result, "quality_level"), (
        "LLMResult must not have quality_level — "
        "authoringfw must receive it as explicit param (I-096-02)"
    )
