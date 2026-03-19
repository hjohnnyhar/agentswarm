"""Tests for Phase 03 Plan 01: run_reviewer() function in ceo.py."""
import os
import pytest
from unittest.mock import MagicMock, patch


def test_run_reviewer_importable():
    """run_reviewer can be imported from src.agents.ceo."""
    from src.agents.ceo import run_reviewer
    assert callable(run_reviewer)


def test_run_reviewer_signature():
    """run_reviewer accepts (ctx, config) and returns WorkflowContext."""
    import inspect
    from src.agents.ceo import run_reviewer
    sig = inspect.signature(run_reviewer)
    params = list(sig.parameters.keys())
    assert "ctx" in params, f"run_reviewer must have 'ctx' parameter, got {params}"
    assert "config" in params, f"run_reviewer must have 'config' parameter, got {params}"


def test_run_reviewer_approved(monkeypatch):
    """run_reviewer sets review_approved=True when Claude responds APPROVED."""
    from src.agents.ceo import run_reviewer
    from src.types import WorkflowContext
    from src.config import Config

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    ctx = WorkflowContext(
        topic="AI Safety",
        objectives="Ensure safe AI systems",
        research_output="Detailed research on AI safety mechanisms..." * 50,
    )
    config = Config()

    mock_message = MagicMock()
    mock_message.content = [MagicMock()]
    mock_message.content[0].text = "APPROVED\nThe white paper clearly meets executive standards."

    with patch("anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = mock_message

        result = run_reviewer(ctx, config)

    assert result.review_approved is True
    assert "The white paper clearly meets executive standards." in result.review_feedback


def test_run_reviewer_rejected(monkeypatch):
    """run_reviewer sets review_approved=False when Claude responds REJECTED."""
    from src.agents.ceo import run_reviewer
    from src.types import WorkflowContext
    from src.config import Config

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    ctx = WorkflowContext(
        topic="AI Safety",
        objectives="Ensure safe AI systems",
        research_output="Brief research",
    )
    config = Config()

    mock_message = MagicMock()
    mock_message.content = [MagicMock()]
    mock_message.content[0].text = "REJECTED\nThe document lacks sufficient depth on risk mitigation."

    with patch("anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = mock_message

        result = run_reviewer(ctx, config)

    assert result.review_approved is False
    assert "The document lacks sufficient depth" in result.review_feedback


def test_run_reviewer_uses_haiku_model(monkeypatch):
    """run_reviewer calls Claude with claude-haiku-4-5 model."""
    from src.agents.ceo import run_reviewer
    from src.types import WorkflowContext
    from src.config import Config

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    ctx = WorkflowContext(topic="test", objectives="obj", research_output="research")
    config = Config()

    mock_message = MagicMock()
    mock_message.content = [MagicMock()]
    mock_message.content[0].text = "APPROVED\nLooks good."

    with patch("anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = mock_message

        run_reviewer(ctx, config)

    call_kwargs = mock_client.messages.create.call_args
    assert call_kwargs.kwargs.get("model") == "claude-haiku-4-5" or \
           (call_kwargs.args and "claude-haiku-4-5" in str(call_kwargs.args)), \
           f"Expected claude-haiku-4-5, got: {call_kwargs}"


def test_run_reviewer_returns_ctx(monkeypatch):
    """run_reviewer returns the WorkflowContext object."""
    from src.agents.ceo import run_reviewer
    from src.types import WorkflowContext
    from src.config import Config

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    ctx = WorkflowContext(topic="test", objectives="obj", research_output="research")
    config = Config()

    mock_message = MagicMock()
    mock_message.content = [MagicMock()]
    mock_message.content[0].text = "APPROVED\nLooks good."

    with patch("anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = mock_message

        result = run_reviewer(ctx, config)

    assert isinstance(result, WorkflowContext)
