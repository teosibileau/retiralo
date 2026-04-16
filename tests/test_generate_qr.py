"""Tests for scripts/generate_qr.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import generate_qr  # noqa: E402

runner = CliRunner()

VALID_TRACKING = "360002939006860"
INVALID_TRACKING_SHORT = "36000293900"
INVALID_TRACKING_PREFIX = "999002939006860"


@pytest.fixture()
def output_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_qr, "OUTPUT_DIR", tmp_path)
    return tmp_path


@patch("generate_qr.QR")
def test_generates_jpg(mock_qr_cls, output_dir):
    mock_img = MagicMock()
    mock_qr_cls.return_value.encode.return_value.convert.return_value = mock_img

    result = runner.invoke(
        generate_qr.app, ["--tracking", VALID_TRACKING, "-o", str(output_dir)]
    )

    assert result.exit_code == 0
    expected_path = output_dir / f"{VALID_TRACKING}.jpg"
    assert str(expected_path) in result.output
    mock_img.save.assert_called_once_with(expected_path, "JPEG")


@patch("generate_qr.QR")
def test_creates_output_dir(mock_qr_cls, tmp_path):
    mock_qr_cls.return_value.encode.return_value.convert.return_value = MagicMock()
    nested = tmp_path / "nested" / "dir"

    result = runner.invoke(
        generate_qr.app, ["--tracking", VALID_TRACKING, "-o", str(nested)]
    )

    assert result.exit_code == 0
    assert nested.exists()


@patch("generate_qr.QR")
def test_invalid_tracking_number(mock_qr_cls, output_dir):
    from andreani_qr.qr import InvalidCodeError

    mock_qr_cls.side_effect = InvalidCodeError("Code must be 15 characters")

    result = runner.invoke(
        generate_qr.app, ["--tracking", INVALID_TRACKING_SHORT, "-o", str(output_dir)]
    )

    assert result.exit_code == 1


def test_no_tracking_provided(output_dir):
    result = runner.invoke(generate_qr.app, ["-o", str(output_dir)], input="")

    assert result.exit_code == 1


@patch("generate_qr.QR")
def test_converts_to_rgb_jpeg(mock_qr_cls, output_dir):
    mock_encode = MagicMock()
    mock_qr_cls.return_value.encode.return_value = mock_encode

    result = runner.invoke(
        generate_qr.app, ["--tracking", VALID_TRACKING, "-o", str(output_dir)]
    )

    assert result.exit_code == 0
    mock_encode.convert.assert_called_once_with("RGB")
