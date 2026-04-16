"""Tests for scripts/setup_inbox.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import setup_inbox  # noqa: E402

runner = CliRunner()


@pytest.fixture()
def env_path(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    monkeypatch.setattr(setup_inbox, "ENV_PATH", path)
    return path


@pytest.fixture()
def fake_inbox():
    def _make(inbox_id="test123@agentmail.to", email="test123@agentmail.to"):
        inbox = MagicMock()
        inbox.inbox_id = inbox_id
        inbox.email = email
        return inbox

    return _make


def test_fails_without_api_key(env_path):
    env_path.write_text("AGENTMAIL_INBOX_ID=\n")

    result = runner.invoke(setup_inbox.app, [], catch_exceptions=False)

    assert result.exit_code == 1
    assert "AGENTMAIL_API_KEY not set" in result.stderr


@patch("setup_inbox.AgentMail")
def test_creates_inbox_and_updates_env(mock_agentmail_cls, env_path, fake_inbox):
    env_path.write_text("AGENTMAIL_API_KEY=am_test_key\nAGENTMAIL_INBOX_ID=\n")
    mock_agentmail_cls.return_value.inboxes.create.return_value = fake_inbox()

    result = runner.invoke(setup_inbox.app, [])

    assert result.exit_code == 0
    assert "inbox_id: test123@agentmail.to" in result.output
    assert "address:  test123@agentmail.to" in result.output
    content = env_path.read_text()
    assert "AGENTMAIL_INBOX_ID=test123@agentmail.to" in content


@patch("setup_inbox.AgentMail")
def test_upsert_replaces_existing_value(mock_agentmail_cls, env_path, fake_inbox):
    env_path.write_text(
        "AGENTMAIL_API_KEY=am_test_key\nAGENTMAIL_INBOX_ID=old@agentmail.to\n"
    )
    mock_agentmail_cls.return_value.inboxes.create.return_value = fake_inbox(
        inbox_id="new@agentmail.to", email="new@agentmail.to"
    )

    result = runner.invoke(setup_inbox.app, [])

    assert result.exit_code == 0
    content = env_path.read_text()
    assert "AGENTMAIL_INBOX_ID=new@agentmail.to" in content
    assert "old@agentmail.to" not in content


@patch("setup_inbox.AgentMail")
def test_upsert_appends_if_key_missing(mock_agentmail_cls, env_path, fake_inbox):
    env_path.write_text("AGENTMAIL_API_KEY=am_test_key\n")
    mock_agentmail_cls.return_value.inboxes.create.return_value = fake_inbox()

    result = runner.invoke(setup_inbox.app, [])

    assert result.exit_code == 0
    content = env_path.read_text()
    assert "AGENTMAIL_INBOX_ID=test123@agentmail.to" in content


@patch("setup_inbox.AgentMail")
def test_preserves_other_env_values(mock_agentmail_cls, env_path, fake_inbox):
    env_path.write_text(
        "AGENTMAIL_API_KEY=am_test_key\nKAPSO_API_KEY=kapso_key\nAGENTMAIL_INBOX_ID=\n"
    )
    mock_agentmail_cls.return_value.inboxes.create.return_value = fake_inbox()

    result = runner.invoke(setup_inbox.app, [])

    assert result.exit_code == 0
    content = env_path.read_text()
    assert "KAPSO_API_KEY=kapso_key" in content
    assert "AGENTMAIL_API_KEY=am_test_key" in content
    assert "AGENTMAIL_INBOX_ID=test123@agentmail.to" in content


@patch("setup_inbox.AgentMail")
def test_passes_client_id_and_display_name(mock_agentmail_cls, env_path, fake_inbox):
    env_path.write_text("AGENTMAIL_API_KEY=am_test_key\nAGENTMAIL_INBOX_ID=\n")
    mock_client = mock_agentmail_cls.return_value
    mock_client.inboxes.create.return_value = fake_inbox()

    result = runner.invoke(
        setup_inbox.app, ["--client-id", "custom-id", "--display-name", "custom-name"]
    )

    assert result.exit_code == 0
    call_kwargs = mock_client.inboxes.create.call_args
    request = call_kwargs.kwargs["request"]
    assert request.client_id == "custom-id"
    assert request.display_name == "custom-name"
