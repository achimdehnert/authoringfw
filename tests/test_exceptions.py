"""Tests for authoringfw exception hierarchy."""

import pytest

from authoringfw.exceptions import (
    AuthoringFWError,
    ConfigurationError,
    OrchestrationError,
    TemplateNotFoundError,
)


def test_should_be_subclass_of_authoringfw_error():
    assert issubclass(OrchestrationError, AuthoringFWError)
    assert issubclass(ConfigurationError, AuthoringFWError)
    assert issubclass(TemplateNotFoundError, ConfigurationError)


def test_should_store_action_code_on_orchestration_error():
    exc = OrchestrationError("something failed", action_code="chapter_writing")
    assert exc.action_code == "chapter_writing"
    assert "something failed" in str(exc)


def test_should_store_action_code_on_configuration_error():
    exc = ConfigurationError("missing row", action_code="chapter_writing")
    assert exc.action_code == "chapter_writing"


def test_should_template_not_found_be_configuration_error():
    exc = TemplateNotFoundError("template missing", action_code="chapter_writing")
    assert isinstance(exc, ConfigurationError)
    assert isinstance(exc, AuthoringFWError)


def test_should_configuration_error_not_be_orchestration_error():
    exc = ConfigurationError("deploy defect")
    assert not isinstance(exc, OrchestrationError)


def test_should_preserve_cause_chain():
    original = ValueError("root cause")
    try:
        raise OrchestrationError("wrapped") from original
    except OrchestrationError as exc:
        assert exc.__cause__ is original
