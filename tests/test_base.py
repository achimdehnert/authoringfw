"""Tests for BaseContentOrchestrator (ADR-096 fixes I-096-01, I-096-02, I-096-04)."""

import pytest
from unittest.mock import MagicMock, patch

from authoringfw.base import BaseContentOrchestrator
from authoringfw.exceptions import ConfigurationError, OrchestrationError
from authoringfw.types import ContentResult, ContentTask


# ── Test doubles ──────────────────────────────────────────────────────────────

class MinimalOrchestrator(BaseContentOrchestrator):
    """Minimal concrete implementation for unit tests."""

    action_code = "test_action"

    def _build_messages(self, task: ContentTask) -> list[dict]:
        return [{"role": "user", "content": task.prompt_variables.get("text", "hello")}]

    def _map_result(self, llm_result, quality_level, task: ContentTask) -> ContentResult:
        return ContentResult(
            content=llm_result.content,
            action_code=self.action_code,
            quality_level=quality_level,
            model=llm_result.model,
            input_tokens=llm_result.input_tokens,
            output_tokens=llm_result.output_tokens,
            latency_ms=llm_result.latency_ms,
            success=llm_result.success,
        )


def _make_llm_result(content="Generated text", success=True):
    r = MagicMock()
    r.content = content
    r.success = success
    r.model = "gpt-4o"
    r.input_tokens = 100
    r.output_tokens = 50
    r.latency_ms = 300
    return r


def _make_task(**kwargs):
    return ContentTask(action_code="test_action", **kwargs)


# ── I-096-04: action_code as class variable ───────────────────────────────────

def test_should_raise_type_error_when_action_code_missing():
    with pytest.raises(TypeError, match="action_code"):
        class BrokenOrchestrator(BaseContentOrchestrator):
            def _build_messages(self, task): return []
            def _map_result(self, r, ql, task): return None


def test_should_accept_action_code_as_class_variable():
    assert MinimalOrchestrator.action_code == "test_action"
    assert MinimalOrchestrator().action_code == "test_action"


# ── I-096-01: ConfigurationError re-raised, not wrapped ──────────────────────

def test_should_reraise_configuration_error_from_get_action_config():
    orchestrator = MinimalOrchestrator()
    task = _make_task()

    with patch.object(
        orchestrator, "_get_action_config",
        side_effect=ConfigurationError("missing row", action_code="test_action")
    ):
        with pytest.raises(ConfigurationError, match="missing row"):
            orchestrator.execute(task)


def test_should_not_wrap_configuration_error_as_orchestration_error():
    orchestrator = MinimalOrchestrator()
    task = _make_task()

    with patch.object(
        orchestrator, "_get_action_config",
        side_effect=ConfigurationError("deploy defect")
    ):
        with pytest.raises(ConfigurationError):
            orchestrator.execute(task)
        # must NOT be caught by OrchestrationError handler
        try:
            orchestrator.execute(task)
        except OrchestrationError:
            pytest.fail("ConfigurationError was wrongly wrapped as OrchestrationError")
        except ConfigurationError:
            pass


def test_should_wrap_generic_error_as_orchestration_error():
    orchestrator = MinimalOrchestrator()
    task = _make_task()

    with patch.object(orchestrator, "_get_action_config", return_value={}):
        with patch.object(
            orchestrator, "_build_messages",
            side_effect=RuntimeError("unexpected")
        ):
            with pytest.raises(OrchestrationError, match="build request"):
                orchestrator.execute(task)


# ── I-096-02: quality_level passed explicitly to _map_result ─────────────────

def test_should_pass_quality_level_explicitly_to_map_result():
    received_ql = []

    class TrackingOrchestrator(BaseContentOrchestrator):
        action_code = "tracking"

        def _build_messages(self, task): return [{"role": "user", "content": "x"}]

        def _map_result(self, llm_result, quality_level, task):
            received_ql.append(quality_level)
            return ContentResult(
                content="ok", action_code=self.action_code, quality_level=quality_level,
            )

    orch = TrackingOrchestrator()
    task = ContentTask(action_code="tracking", quality_level=3)

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm", return_value=_make_llm_result()):
            orch.execute(task)

    assert received_ql == [3]


def test_should_resolve_quality_level_from_task_override():
    orch = MinimalOrchestrator()
    task = ContentTask(action_code="test_action", quality_level=5)
    config = {"default_quality_level": 2}

    resolved = orch._resolve_quality_level(task, config)
    assert resolved == 5  # task override wins


def test_should_resolve_quality_level_from_config_default():
    orch = MinimalOrchestrator()
    task = ContentTask(action_code="test_action")  # no quality_level
    config = {"default_quality_level": 2}

    resolved = orch._resolve_quality_level(task, config)
    assert resolved == 2


def test_should_resolve_quality_level_none_when_no_default():
    orch = MinimalOrchestrator()
    task = ContentTask(action_code="test_action")
    config = {}

    resolved = orch._resolve_quality_level(task, config)
    assert resolved is None


# ── execute() happy path ──────────────────────────────────────────────────────

def test_should_return_content_result_on_success():
    orch = MinimalOrchestrator()
    task = _make_task(prompt_variables={"text": "write something"})
    llm_result = _make_llm_result("Great text")

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm", return_value=llm_result):
            result = orch.execute(task)

    assert result.content == "Great text"
    assert result.action_code == "test_action"
    assert result.success is True


def test_should_call_pre_and_post_hooks():
    pre_called = []
    post_called = []

    class HookOrchestrator(BaseContentOrchestrator):
        action_code = "hooks"
        def _build_messages(self, task): return [{"role": "user", "content": "x"}]
        def _map_result(self, r, ql, task):
            return ContentResult(content="ok", action_code=self.action_code)
        def pre_execute(self, task): pre_called.append(True)
        def post_execute(self, task, result): post_called.append(True)

    orch = HookOrchestrator()
    task = ContentTask(action_code="hooks")

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm", return_value=_make_llm_result()):
            orch.execute(task)

    assert pre_called == [True]
    assert post_called == [True]
