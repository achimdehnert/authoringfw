"""
authoingfw exceptions.

All public exceptions raised by authoringfw. Consumers should catch
OrchestrationError for runtime failures and ConfigurationError for
setup/deployment defects (missing AIActionType rows etc.).
"""

from __future__ import annotations


class AuthoringFWError(Exception):
    """Base exception for all authoringfw errors."""


class OrchestrationError(AuthoringFWError):
    """
    Raised when an orchestration step fails at runtime.

    This covers LLM call failures, unexpected result shapes, and
    mid-pipeline errors. It wraps the original exception via __cause__.
    """

    def __init__(self, message: str, action_code: str = "") -> None:
        super().__init__(message)
        self.action_code = action_code


class ConfigurationError(AuthoringFWError):
    """
    Raised when authoringfw is misconfigured at deploy time.

    Examples: missing AIActionType row for action_code, invalid
    prompt_template_key, or required aifw settings not present.

    This is a deployment defect — do NOT catch generically. Let it
    propagate so CI/CD and ops tooling can surface it clearly.
    """

    def __init__(self, message: str, action_code: str = "") -> None:
        super().__init__(message)
        self.action_code = action_code


class TemplateNotFoundError(ConfigurationError):
    """
    Raised when the prompt template key cannot be resolved.

    Subclass of ConfigurationError — same propagation rules apply.
    """
