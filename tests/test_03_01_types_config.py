"""Tests for Phase 03 Plan 01: review_feedback field and gmail_app_password field."""
import os
import pytest


def test_workflow_context_has_review_feedback():
    """WorkflowContext has review_feedback str field defaulting to empty string."""
    from src.types import WorkflowContext
    ctx = WorkflowContext(topic="test")
    assert hasattr(ctx, "review_feedback"), "WorkflowContext must have review_feedback field"
    assert ctx.review_feedback == "", f"review_feedback should default to '', got {ctx.review_feedback!r}"
    assert isinstance(ctx.review_feedback, str), "review_feedback must be str"


def test_workflow_context_existing_fields_unchanged():
    """Existing WorkflowContext fields still work correctly."""
    from src.types import WorkflowContext
    ctx = WorkflowContext(topic="test", objectives="obj", research_output="research")
    assert ctx.topic == "test"
    assert ctx.objectives == "obj"
    assert ctx.research_output == "research"
    assert ctx.review_approved is False
    assert ctx.tasks == []


def test_config_has_gmail_app_password(monkeypatch):
    """Config has gmail_app_password field populated from GMAIL_APP_PASSWORD env var."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "my-app-password")
    from src.config import Config
    c = Config()
    assert hasattr(c, "gmail_app_password"), "Config must have gmail_app_password field"
    assert c.gmail_app_password == "my-app-password"


def test_config_gmail_app_password_defaults_empty(monkeypatch):
    """Config does not raise when GMAIL_APP_PASSWORD is absent."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    from src.config import Config
    c = Config()
    assert c.gmail_app_password == ""


def test_config_still_raises_on_missing_api_key(monkeypatch):
    """Config still raises EnvironmentError when ANTHROPIC_API_KEY is absent."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    from src.config import Config
    with pytest.raises(EnvironmentError):
        Config()
