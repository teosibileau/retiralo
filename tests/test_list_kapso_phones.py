"""Tests for scripts/list_kapso_phones.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import list_kapso_phones  # noqa: E402

runner = CliRunner()


@pytest.fixture()
def fake_response():
    def _make(data=None, status_code=200):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = {"data": data or []}
        resp.raise_for_status = MagicMock()
        if status_code >= 400:
            from requests.exceptions import HTTPError

            resp.raise_for_status.side_effect = HTTPError(response=resp)
        return resp

    return _make


PRODUCTION_PHONE = {
    "phone_number_id": "1045069365361401",
    "name": "Locksleyland",
    "display_name": "Locksleyland",
    "display_phone_number": "+1 201-277-6063",
    "kind": "production",
}

SANDBOX_PHONE = {
    "phone_number_id": "597907523413541",
    "name": "Sandbox WhatsApp",
    "display_phone_number": None,
    "kind": "sandbox",
}


@patch("list_kapso_phones.requests.get")
def test_returns_production_phones(mock_get, fake_response):
    mock_get.return_value = fake_response(data=[PRODUCTION_PHONE])

    result = runner.invoke(list_kapso_phones.app, ["--kapso-key", "test-key"])

    assert result.exit_code == 0
    phones = json.loads(result.output)
    assert len(phones) == 1
    assert phones[0]["phone_number_id"] == "1045069365361401"
    assert phones[0]["name"] == "Locksleyland"
    assert phones[0]["number"] == "+1 201-277-6063"


@patch("list_kapso_phones.requests.get")
def test_filters_sandbox_phones(mock_get, fake_response):
    mock_get.return_value = fake_response(data=[PRODUCTION_PHONE, SANDBOX_PHONE])

    result = runner.invoke(list_kapso_phones.app, ["--kapso-key", "test-key"])

    assert result.exit_code == 0
    phones = json.loads(result.output)
    assert len(phones) == 1
    assert phones[0]["kind"] == "production"


@patch("list_kapso_phones.requests.get")
def test_empty_account(mock_get, fake_response):
    mock_get.return_value = fake_response(data=[])

    result = runner.invoke(list_kapso_phones.app, ["--kapso-key", "test-key"])

    assert result.exit_code == 0
    phones = json.loads(result.output)
    assert phones == []


@patch("list_kapso_phones.requests.get")
def test_passes_api_key_header(mock_get, fake_response):
    mock_get.return_value = fake_response(data=[])

    runner.invoke(list_kapso_phones.app, ["--kapso-key", "my-secret-key"])

    mock_get.assert_called_once_with(
        list_kapso_phones.KAPSO_PHONES_URL,
        headers={"X-API-Key": "my-secret-key"},
    )


@patch("list_kapso_phones.requests.get")
def test_fallback_for_missing_fields(mock_get, fake_response):
    phone_no_name = {
        "phone_number_id": "999",
        "display_phone_number": None,
        "kind": "production",
    }
    mock_get.return_value = fake_response(data=[phone_no_name])

    result = runner.invoke(list_kapso_phones.app, ["--kapso-key", "test-key"])

    assert result.exit_code == 0
    phones = json.loads(result.output)
    assert phones[0]["name"] == "unnamed"
    assert phones[0]["number"] == "no number"


def test_missing_required_key():
    result = runner.invoke(list_kapso_phones.app, [])

    assert result.exit_code != 0
