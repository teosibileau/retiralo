"""Tests for scripts/bootstrap_env.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import bootstrap_env  # noqa: E402

runner = CliRunner()

VALID_ARGS = [
    "--agentmail-key",
    "am_test_key",
    "--kapso-key",
    "kapso_test_key",
    "--kapso-phone-number-id",
    "12345",
    "--whatsapp-to",
    "5491100000000",
    "--email-from",
    "Test@Example.com",
]


@pytest.fixture()
def env_path(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    monkeypatch.setattr(bootstrap_env, "ENV_PATH", path)
    return path


def test_creates_env_file(env_path):
    result = runner.invoke(bootstrap_env.app, VALID_ARGS)

    assert result.exit_code == 0
    assert env_path.exists()
    content = env_path.read_text()
    assert "AGENTMAIL_API_KEY=am_test_key\n" in content
    assert "KAPSO_API_KEY=kapso_test_key\n" in content
    assert "KAPSO_PHONE_NUMBER_ID=12345\n" in content
    assert "WHATSAPP_TO=5491100000000\n" in content
    assert "AGENTMAIL_INBOX_ID=\n" in content


def test_email_from_lowercased(env_path):
    result = runner.invoke(bootstrap_env.app, VALID_ARGS)

    assert result.exit_code == 0
    assert "EMAIL_FROM=test@example.com\n" in env_path.read_text()


def test_skips_if_env_exists(env_path):
    env_path.write_text("existing=true\n")

    result = runner.invoke(bootstrap_env.app, VALID_ARGS)

    assert result.exit_code == 0
    assert "nothing to do" in result.output
    assert env_path.read_text() == "existing=true\n"


def test_force_overwrites(env_path):
    env_path.write_text("existing=true\n")

    result = runner.invoke(bootstrap_env.app, ["--force", *VALID_ARGS])

    assert result.exit_code == 0
    content = env_path.read_text()
    assert "existing" not in content
    assert "AGENTMAIL_API_KEY=am_test_key\n" in content


def test_strips_whitespace(env_path):
    args = [
        "--agentmail-key",
        "  am_test_key  ",
        "--kapso-key",
        "  kapso_test_key  ",
        "--kapso-phone-number-id",
        "  12345  ",
        "--whatsapp-to",
        "  5491100000000  ",
        "--email-from",
        "  Test@Example.com  ",
    ]
    result = runner.invoke(bootstrap_env.app, args)

    assert result.exit_code == 0
    content = env_path.read_text()
    assert "AGENTMAIL_API_KEY=am_test_key\n" in content
    assert "EMAIL_FROM=test@example.com\n" in content


def test_missing_required_args():
    result = runner.invoke(bootstrap_env.app, [])

    assert result.exit_code != 0
