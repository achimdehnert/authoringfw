"""
BaseContentOrchestrator — abstract base class for all authoringfw orchestrators.

ADR-096 Phase 3 implementation. Three fixes applied:

  I-096-01: ConfigurationError is re-raised BEFORE the generic except block,
            so deployment defects are never silently wrapped as OrchestrationError.

  I-096-02: quality_level is passed explicitly to _map_result() as a parameter.
            It must not be read from llm_result (LLMResult has no quality_level attr).

  I-096-04: action_code is a class variable (str), not @property @abstractmethod.
            Subclasses simply assign: action_code = "chapter_writing".

Usage::

    class ChapterOrchestrator(BaseContentOrchestrator):
        action_code = "chapter_writing"

        def _build_messages(self, task: ContentTask) -> list[dict]:
            return [{"role": "user", "content": task.prompt_variables.get("text", "")}]

        def _map_result(self, llm_result, quality_level: int | None, task: ContentTask) -> ContentResult:
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
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from authoringfw.exceptions import ConfigurationError, OrchestrationError
from authoringfw.types import ContentResult, ContentTask


class BaseContentOrchestrator(ABC):
    """
    Abstract base for all content orchestration pipelines.

    Subclasses must:
      1. Set ``action_code`` as a class variable (str).
      2. Implement ``_build_messages()`` — builds the LLM message list.
      3. Implement ``_map_result()`` — maps LLMResult → ContentResult.

    Optionally override:
      - ``_get_prompt_template_key()`` — default returns ``action_code``.
      - ``pre_execute()`` / ``post_execute()`` hooks.
    """

    action_code: str = ""  # I-096-04: class variable, not @abstractmethod property

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "action_code", ""):
            raise TypeError(
                f"{cls.__name__} must define class variable 'action_code' (non-empty str). "
                "Example: action_code = \"chapter_writing\""
            )

    def execute(self, task: ContentTask) -> ContentResult:
        """
        Execute the orchestration pipeline synchronously.

        Raises:
            ConfigurationError: If AIActionType / config lookup fails (deployment defect).
            OrchestrationError: If the LLM call or result mapping fails at runtime.
        """
        self.pre_execute(task)
        try:
            # I-096-01: ConfigurationError bubbles up BEFORE the generic handler.
            # It must never be wrapped as OrchestrationError — it is a deploy defect.
            config = self._get_action_config(task)
            quality_level = self._resolve_quality_level(task, config)
            messages = self._build_messages(task)
        except ConfigurationError:
            raise  # I-096-01: re-raise without wrapping
        except Exception as exc:
            raise OrchestrationError(
                f"[{self.action_code}] Failed to build request: {exc}",
                action_code=self.action_code,
            ) from exc

        try:
            llm_result = self._call_llm(messages, config, quality_level, task)
        except ConfigurationError:
            raise  # I-096-01
        except Exception as exc:
            raise OrchestrationError(
                f"[{self.action_code}] LLM call failed: {exc}",
                action_code=self.action_code,
            ) from exc

        try:
            # I-096-02: quality_level passed explicitly, not read from llm_result
            result = self._map_result(llm_result, quality_level, task)
        except ConfigurationError:
            raise  # I-096-01
        except Exception as exc:
            raise OrchestrationError(
                f"[{self.action_code}] Result mapping failed: {exc}",
                action_code=self.action_code,
            ) from exc

        self.post_execute(task, result)
        return result

    # ── Hooks (optional override) ───────────────────────────────────────────

    def pre_execute(self, task: ContentTask) -> None:
        """Called before any processing. Override for logging, metrics, etc."""

    def post_execute(self, task: ContentTask, result: ContentResult) -> None:
        """Called after successful execution. Override for logging, caching, etc."""

    # ── Abstract methods (must implement) ──────────────────────────────────

    @abstractmethod
    def _build_messages(self, task: ContentTask) -> list[dict[str, str]]:
        """
        Build the LLM message list for this task.

        Returns:
            List of {"role": str, "content": str} dicts.
        """

    @abstractmethod
    def _map_result(
        self,
        llm_result: Any,
        quality_level: int | None,
        task: ContentTask,
    ) -> ContentResult:
        """
        Map a raw LLMResult to a typed ContentResult.

        Args:
            llm_result: The raw result from _call_llm() (LLMResult type from aifw).
            quality_level: The resolved quality level (I-096-02: explicit param).
            task: The original ContentTask (for metadata passthrough).
        """

    # ── Internal helpers ───────────────────────────────────────────────────

    def _get_prompt_template_key(self, task: ContentTask) -> str:
        """Returns the prompt template key. Default: action_code."""
        return self.action_code

    def _get_action_config(self, task: ContentTask) -> dict[str, Any]:
        """
        Fetch action config from aifw (get_action_config).

        Raises ConfigurationError if the action_code has no DB row.
        """
        try:
            from aifw.service import get_action_config  # type: ignore[import]
        except ImportError as exc:
            raise ConfigurationError(
                "aifw is required for BaseContentOrchestrator. "
                "Install with: pip install iil-aifw",
                action_code=self.action_code,
            ) from exc

        config = get_action_config(task.action_code)
        if config is None:
            raise ConfigurationError(
                f"No AIActionType row found for action_code='{task.action_code}'. "
                "Run: python manage.py check_aifw_config",
                action_code=task.action_code,
            )
        return config

    def _resolve_quality_level(
        self,
        task: ContentTask,
        config: dict[str, Any],
    ) -> int | None:
        """Resolve effective quality level: task override > config default > None."""
        if task.quality_level is not None:
            return task.quality_level
        return config.get("default_quality_level")

    def _call_llm(
        self,
        messages: list[dict[str, str]],
        config: dict[str, Any],
        quality_level: int | None,
        task: ContentTask,
    ) -> Any:
        """
        Call aifw sync_completion() with the resolved config.

        Raises ConfigurationError for missing action config.
        Raises OrchestrationError (via caller) for LLM failures.
        """
        try:
            from aifw.service import sync_completion  # type: ignore[import]
        except ImportError as exc:
            raise ConfigurationError(
                "aifw is required for BaseContentOrchestrator. "
                "Install with: pip install iil-aifw",
                action_code=self.action_code,
            ) from exc

        return sync_completion(
            action_code=task.action_code,
            messages=messages,
            quality_level=quality_level,
            priority=task.priority,
        )
