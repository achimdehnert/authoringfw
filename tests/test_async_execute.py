"""Tests for BaseContentOrchestrator.async_execute() — ADR-096 OQ-1.

All tests use pytest-asyncio. No real LLM calls — aifw is fully mocked.
Error-handling contract is identical to execute():
  - ConfigurationError propagates unchanged
  - All other failures become OrchestrationError
  - quality_level is explicit param to _map_result() (I-096-02)
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from authoringfw.base import BaseContentOrchestrator
from authoringfw.exceptions import ConfigurationError, OrchestrationError
from authoringfw.types import ContentResult, ContentTask


# ── Test doubles ──────────────────────────────────────────────────────────────────

class AsyncOrchestrator(BaseContentOrchestrator):
    """Minimal concrete orchestrator for async tests."""

    action_code = "async_test"

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
            metadata=task.metadata,
        )


def _make_llm_result(content="Async text", success=True):
    r = MagicMock()
    r.content = content
    r.success = success
    r.model = "gpt-4o"
    r.input_tokens = 50
    r.output_tokens = 100
    r.latency_ms = 200
    return r


def _make_task(**kwargs):
    return ContentTask(action_code="async_test", **kwargs)


# ── Happy path ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_should_return_content_result_async():
    """async_execute() returns ContentResult on success."""
    orch = AsyncOrchestrator()
    task = _make_task(prompt_variables={"text": "write async"})
    llm_result = _make_llm_result("Async content")

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm_async", new=AsyncMock(return_value=llm_result)):
            result = await orch.async_execute(task)

    assert result.content == "Async content"
    assert result.action_code == "async_test"
    assert result.success is True


@pytest.mark.asyncio
async def test_should_pass_quality_level_to_map_result_async():
    """I-096-02: quality_level passed explicitly, not read from llm_result."""
    received_ql = []

    class TrackingAsync(BaseContentOrchestrator):
        action_code = "tracking_async"

        def _build_messages(self, task): return [{"role": "user", "content": "x"}]

        def _map_result(self, llm_result, quality_level, task):
            received_ql.append(quality_level)
            return ContentResult(content="ok", action_code=self.action_code, quality_level=quality_level)

    orch = TrackingAsync()
    task = ContentTask(action_code="tracking_async", quality_level=7)

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm_async", new=AsyncMock(return_value=_make_llm_result())):
            await orch.async_execute(task)

    assert received_ql == [7]


@pytest.mark.asyncio
async def test_should_resolve_quality_level_from_config_in_async():
    """async_execute() resolves quality_level from config when task has none."""
    received_ql = []

    class TrackingAsync2(BaseContentOrchestrator):
        action_code = "tracking_async2"
        def _build_messages(self, task): return [{"role": "user", "content": "x"}]
        def _map_result(self, llm_result, quality_level, task):
            received_ql.append(quality_level)
            return ContentResult(content="ok", action_code=self.action_code)

    orch = TrackingAsync2()
    task = ContentTask(action_code="tracking_async2")  # no quality_level

    with patch.object(orch, "_get_action_config", return_value={"default_quality_level": 5}):
        with patch.object(orch, "_call_llm_async", new=AsyncMock(return_value=_make_llm_result())):
            await orch.async_execute(task)

    assert received_ql == [5]


# ── I-096-01: ConfigurationError propagates unchanged in async ───────────────────

@pytest.mark.asyncio
async def test_should_reraise_configuration_error_from_get_action_config_async():
    """ConfigurationError from _get_action_config must propagate (not wrapped)."""
    orch = AsyncOrchestrator()
    task = _make_task()

    with patch.object(
        orch, "_get_action_config",
        side_effect=ConfigurationError("missing row", action_code="async_test")
    ):
        with pytest.raises(ConfigurationError, match="missing row"):
            await orch.async_execute(task)


@pytest.mark.asyncio
async def test_should_not_wrap_configuration_error_as_orchestration_error_async():
    """ConfigurationError from LLM call must not be wrapped as OrchestrationError."""
    orch = AsyncOrchestrator()
    task = _make_task()

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(
            orch, "_call_llm_async",
            new=AsyncMock(side_effect=ConfigurationError("no model"))
        ):
            try:
                await orch.async_execute(task)
            except OrchestrationError:
                pytest.fail("ConfigurationError was wrongly wrapped as OrchestrationError")
            except ConfigurationError:
                pass  # expected


@pytest.mark.asyncio
async def test_should_wrap_generic_llm_error_as_orchestration_error_async():
    """Runtime LLM errors become OrchestrationError in async."""
    orch = AsyncOrchestrator()
    task = _make_task()

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(
            orch, "_call_llm_async",
            new=AsyncMock(side_effect=RuntimeError("network timeout"))
        ):
            with pytest.raises(OrchestrationError, match="Async LLM call failed"):
                await orch.async_execute(task)


@pytest.mark.asyncio
async def test_should_wrap_build_messages_error_as_orchestration_error_async():
    """RuntimeError in _build_messages becomes OrchestrationError."""
    orch = AsyncOrchestrator()
    task = _make_task()

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(
            orch, "_build_messages",
            side_effect=RuntimeError("template missing")
        ):
            with pytest.raises(OrchestrationError, match="build request"):
                await orch.async_execute(task)


# ── Async lifecycle hooks ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_should_call_async_pre_and_post_hooks():
    """pre_execute_async() and post_execute_async() are called in order."""
    pre_called = []
    post_called = []

    class HookedAsync(BaseContentOrchestrator):
        action_code = "hooked_async"
        def _build_messages(self, task): return [{"role": "user", "content": "x"}]
        def _map_result(self, r, ql, task):
            return ContentResult(content="ok", action_code=self.action_code)
        async def pre_execute_async(self, task): pre_called.append(True)
        async def post_execute_async(self, task, result): post_called.append(True)

    orch = HookedAsync()
    task = ContentTask(action_code="hooked_async")

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm_async", new=AsyncMock(return_value=_make_llm_result())):
            await orch.async_execute(task)

    assert pre_called == [True]
    assert post_called == [True]


@pytest.mark.asyncio
async def test_should_not_call_post_hook_on_failure():
    """post_execute_async() must NOT be called when LLM fails."""
    post_called = []

    class FailHookedAsync(BaseContentOrchestrator):
        action_code = "fail_hooked"
        def _build_messages(self, task): return [{"role": "user", "content": "x"}]
        def _map_result(self, r, ql, task):
            return ContentResult(content="ok", action_code=self.action_code)
        async def post_execute_async(self, task, result): post_called.append(True)

    orch = FailHookedAsync()
    task = ContentTask(action_code="fail_hooked")

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(
            orch, "_call_llm_async",
            new=AsyncMock(side_effect=RuntimeError("boom"))
        ):
            with pytest.raises(OrchestrationError):
                await orch.async_execute(task)

    assert post_called == []  # must NOT have been called


# ── _call_llm_async: aifw.completion() is called ───────────────────────────────

@pytest.mark.asyncio
async def test_should_call_aifw_async_completion():
    """_call_llm_async() delegates to aifw.service.completion()."""
    orch = AsyncOrchestrator()
    task = _make_task(quality_level=6, priority="balanced")
    config = {}
    captured = {}

    async def _fake_completion(**kwargs):
        captured.update(kwargs)
        return _make_llm_result()

    import sys
    fake_aifw_service = MagicMock()
    fake_aifw_service.completion = _fake_completion
    fake_aifw = MagicMock()
    fake_aifw.service = fake_aifw_service
    with patch.dict(sys.modules, {"aifw": fake_aifw, "aifw.service": fake_aifw_service}):
        result = await orch._call_llm_async(
            [{"role": "user", "content": "x"}],
            config,
            quality_level=6,
            task=task,
        )

    assert result is not None


@pytest.mark.asyncio
async def test_should_pass_quality_level_and_priority_to_async_llm():
    """_call_llm_async() forwards quality_level + priority to aifw."""
    orch = AsyncOrchestrator()
    task = _make_task(quality_level=8, priority="quality")
    captured = {}

    async def _fake_llm_async(msgs, cfg, quality_level, task):
        captured["quality_level"] = quality_level
        captured["priority"] = task.priority
        return _make_llm_result()

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm_async", side_effect=_fake_llm_async):
            await orch.async_execute(task)

    assert captured["quality_level"] == 8
    assert captured["priority"] == "quality"


# ── Parity with execute() ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_async_and_sync_produce_equivalent_results():
    """async_execute() and execute() produce identical ContentResult structure."""
    orch = AsyncOrchestrator()
    task = _make_task(prompt_variables={"text": "test"}, quality_level=4)
    llm_result = _make_llm_result("Content")

    with patch.object(orch, "_get_action_config", return_value={}):
        with patch.object(orch, "_call_llm", return_value=llm_result):
            sync_result = orch.execute(task)

        with patch.object(orch, "_call_llm_async", new=AsyncMock(return_value=llm_result)):
            async_result = await orch.async_execute(task)

    assert sync_result.content == async_result.content
    assert sync_result.action_code == async_result.action_code
    assert sync_result.quality_level == async_result.quality_level
    assert sync_result.model == async_result.model
