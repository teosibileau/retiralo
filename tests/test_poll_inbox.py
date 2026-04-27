"""Tests for scripts/poll_inbox.py."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import poll_inbox  # noqa: E402

runner = CliRunner()

ENV_CONTENT = "AGENTMAIL_API_KEY=am_test_key\nAGENTMAIL_INBOX_ID=test@agentmail.to\n"


@pytest.fixture()
def env_path(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text(ENV_CONTENT)
    monkeypatch.setattr(poll_inbox, "ENV_PATH", path)
    monkeypatch.setenv("AGENTMAIL_API_KEY", "am_test_key")
    monkeypatch.setenv("AGENTMAIL_INBOX_ID", "test@agentmail.to")
    return path


@pytest.fixture()
def fake_message():
    def _make(
        message_id="<msg1@mail.gmail.com>",
        thread_id="thread-1",
        from_="Mercado Libre <no-reply@mercadolibre.com.ar>",
        subject="Ya puedes retirar tu compra en Sucursal Andreani",
        timestamp=None,
        text="some body text",
    ):
        msg = MagicMock()
        msg.message_id = message_id
        msg.thread_id = thread_id
        msg.from_ = from_
        msg.subject = subject
        msg.timestamp = timestamp or datetime(
            2026, 4, 15, 21, 0, 0, tzinfo=timezone.utc
        )
        msg.text = text
        return msg

    return _make


@pytest.fixture()
def fake_list_response():
    def _make(messages=None):
        resp = MagicMock()
        resp.messages = messages
        return resp

    return _make


def test_fails_without_env_vars(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text("")
    monkeypatch.setattr(poll_inbox, "ENV_PATH", path)
    monkeypatch.delenv("AGENTMAIL_API_KEY", raising=False)
    monkeypatch.delenv("AGENTMAIL_INBOX_ID", raising=False)

    result = runner.invoke(poll_inbox.app, ["find"])

    assert result.exit_code == 1


@patch("poll_inbox.AgentMail")
def test_find_returns_matching_messages(
    mock_cls, env_path, fake_message, fake_list_response
):
    mock_cls.return_value.inboxes.messages.list.return_value = fake_list_response(
        messages=[fake_message()]
    )

    result = runner.invoke(poll_inbox.app, ["find"])

    assert result.exit_code == 0
    hits = json.loads(result.output)
    assert len(hits) == 1
    assert hits[0]["message_id"] == "<msg1@mail.gmail.com>"


@patch("poll_inbox.AgentMail")
def test_find_filters_wrong_sender(
    mock_cls, env_path, fake_message, fake_list_response
):
    mock_cls.return_value.inboxes.messages.list.return_value = fake_list_response(
        messages=[fake_message(from_="someone@else.com")]
    )

    result = runner.invoke(poll_inbox.app, ["find"])

    assert result.exit_code == 0
    hits = json.loads(result.output)
    assert len(hits) == 0


@patch("poll_inbox.AgentMail")
def test_find_filters_wrong_subject(
    mock_cls, env_path, fake_message, fake_list_response
):
    mock_cls.return_value.inboxes.messages.list.return_value = fake_list_response(
        messages=[fake_message(subject="Unrelated email")]
    )

    result = runner.invoke(poll_inbox.app, ["find"])

    assert result.exit_code == 0
    hits = json.loads(result.output)
    assert len(hits) == 0


@patch("poll_inbox.AgentMail")
def test_find_empty_inbox(mock_cls, env_path, fake_list_response):
    mock_cls.return_value.inboxes.messages.list.return_value = fake_list_response(
        messages=[]
    )

    result = runner.invoke(poll_inbox.app, ["find"])

    assert result.exit_code == 0
    hits = json.loads(result.output)
    assert hits == []


@patch("poll_inbox.AgentMail")
def test_find_with_mark_read(mock_cls, env_path, fake_message, fake_list_response):
    msg = fake_message()
    mock_client = mock_cls.return_value
    mock_client.inboxes.messages.list.return_value = fake_list_response(messages=[msg])

    result = runner.invoke(poll_inbox.app, ["find", "--mark-read"])

    assert result.exit_code == 0
    mock_client.inboxes.messages.update.assert_called_once_with(
        inbox_id="test@agentmail.to",
        message_id="<msg1@mail.gmail.com>",
        remove_labels=["unread"],
    )


@patch("poll_inbox.AgentMail")
def test_find_without_mark_read_does_not_update(
    mock_cls, env_path, fake_message, fake_list_response
):
    mock_client = mock_cls.return_value
    mock_client.inboxes.messages.list.return_value = fake_list_response(
        messages=[fake_message()]
    )

    result = runner.invoke(poll_inbox.app, ["find"])

    assert result.exit_code == 0
    mock_client.inboxes.messages.update.assert_not_called()


@patch("poll_inbox.AgentMail")
def test_mark_read_command(mock_cls, env_path):
    result = runner.invoke(poll_inbox.app, ["mark-read", "<msg1@mail.gmail.com>"])

    assert result.exit_code == 0
    assert "marked read" in result.output
    mock_cls.return_value.inboxes.messages.update.assert_called_once_with(
        inbox_id="test@agentmail.to",
        message_id="<msg1@mail.gmail.com>",
        remove_labels=["unread"],
    )


@patch("poll_inbox.AgentMail")
def test_show_command(mock_cls, env_path, fake_message):
    msg = fake_message(text="Tu DNI y este código de seguimiento: 360002939006860")
    mock_cls.return_value.inboxes.messages.get.return_value = msg

    result = runner.invoke(poll_inbox.app, ["show", "<msg1@mail.gmail.com>"])

    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["message_id"] == "<msg1@mail.gmail.com>"
    assert "360002939006860" in out["text"]


@patch("poll_inbox.AgentMail")
def test_find_sender_match_is_case_insensitive(
    mock_cls, env_path, fake_message, fake_list_response
):
    mock_cls.return_value.inboxes.messages.list.return_value = fake_list_response(
        messages=[fake_message(from_="Mercado Libre <NO-REPLY@MERCADOLIBRE.COM.AR>")]
    )

    result = runner.invoke(poll_inbox.app, ["find"])

    assert result.exit_code == 0
    hits = json.loads(result.output)
    assert len(hits) == 1
