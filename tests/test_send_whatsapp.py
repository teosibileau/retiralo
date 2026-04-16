"""Tests for scripts/send_whatsapp.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import send_whatsapp  # noqa: E402

runner = CliRunner()

ENV_CONTENT = (
    "KAPSO_API_KEY=test-kapso-key\n"
    "KAPSO_PHONE_NUMBER_ID=123456\n"
    "WHATSAPP_TO=5491100000000\n"
)


@pytest.fixture()
def env_path(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text(ENV_CONTENT)
    monkeypatch.setattr(send_whatsapp, "ENV_PATH", path)
    monkeypatch.setenv("KAPSO_API_KEY", "test-kapso-key")
    monkeypatch.setenv("KAPSO_PHONE_NUMBER_ID", "123456")
    monkeypatch.setenv("WHATSAPP_TO", "5491100000000")
    return path


@pytest.fixture()
def image_file(tmp_path):
    img = tmp_path / "test.jpg"
    img.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg")
    return img


def make_ok_response(json_data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = json_data or {}
    resp.raise_for_status = MagicMock()
    return resp


@patch("send_whatsapp.requests.post")
def test_uploads_and_sends(mock_post, env_path, image_file):
    upload_resp = make_ok_response({"id": "media-123"})
    send_resp = make_ok_response(
        {"messaging_product": "whatsapp", "messages": [{"id": "wamid.123"}]}
    )
    mock_post.side_effect = [upload_resp, send_resp]

    result = runner.invoke(send_whatsapp.app, ["--image", str(image_file)])

    assert result.exit_code == 0
    assert "media_id: media-123" in result.output
    assert "sending to 5491100000000" in result.output
    assert mock_post.call_count == 2


@patch("send_whatsapp.requests.post")
def test_sends_with_caption(mock_post, env_path, image_file):
    upload_resp = make_ok_response({"id": "media-123"})
    send_resp = make_ok_response({"messaging_product": "whatsapp"})
    mock_post.side_effect = [upload_resp, send_resp]

    result = runner.invoke(
        send_whatsapp.app, ["--image", str(image_file), "--caption", "Hello!"]
    )

    assert result.exit_code == 0
    send_call = mock_post.call_args_list[1]
    body = send_call.kwargs["json"]
    assert body["image"]["caption"] == "Hello!"


@patch("send_whatsapp.requests.post")
def test_sends_without_caption(mock_post, env_path, image_file):
    upload_resp = make_ok_response({"id": "media-123"})
    send_resp = make_ok_response({"messaging_product": "whatsapp"})
    mock_post.side_effect = [upload_resp, send_resp]

    result = runner.invoke(send_whatsapp.app, ["--image", str(image_file)])

    assert result.exit_code == 0
    send_call = mock_post.call_args_list[1]
    body = send_call.kwargs["json"]
    assert "caption" not in body["image"]


@patch("send_whatsapp.requests.post")
def test_upload_uses_correct_url_and_headers(mock_post, env_path, image_file):
    upload_resp = make_ok_response({"id": "media-123"})
    send_resp = make_ok_response({"messaging_product": "whatsapp"})
    mock_post.side_effect = [upload_resp, send_resp]

    runner.invoke(send_whatsapp.app, ["--image", str(image_file)])

    upload_call = mock_post.call_args_list[0]
    assert "123456/media" in upload_call.args[0]
    assert upload_call.kwargs["headers"]["X-API-Key"] == "test-kapso-key"


def test_fails_with_missing_image(env_path, tmp_path):
    result = runner.invoke(
        send_whatsapp.app, ["--image", str(tmp_path / "nonexistent.jpg")]
    )

    assert result.exit_code == 1


def test_fails_without_env_vars(tmp_path, monkeypatch, image_file):
    path = tmp_path / ".env"
    path.write_text("")
    monkeypatch.setattr(send_whatsapp, "ENV_PATH", path)
    monkeypatch.delenv("KAPSO_API_KEY", raising=False)
    monkeypatch.delenv("KAPSO_PHONE_NUMBER_ID", raising=False)
    monkeypatch.delenv("WHATSAPP_TO", raising=False)

    result = runner.invoke(send_whatsapp.app, ["--image", str(image_file)])

    assert result.exit_code == 1


def test_fails_with_no_image_provided(env_path):
    result = runner.invoke(send_whatsapp.app, [], input="")

    assert result.exit_code == 1
