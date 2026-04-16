#!/usr/bin/env python
"""Send an Andreani QR image via WhatsApp using the Kapso API.

Uploads the image to WhatsApp's media storage, then sends it as a message.
No public URL needed.

    poetry run scripts/send_whatsapp.py --image state/360002939006860.png
    poetry run scripts/send_whatsapp.py --image state/360002939006860.png --caption "Tracking: 360002939006860"

Or piped from generate_qr.py (reads path from stdin):

    echo 360002939006860 | poetry run scripts/generate_qr.py | poetry run scripts/send_whatsapp.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
import typer
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
KAPSO_BASE = "https://api.kapso.ai/meta/whatsapp/v24.0"

app = typer.Typer(add_completion=False, help=__doc__)


def get_config() -> dict[str, str]:
    load_dotenv(ENV_PATH)
    keys = ["KAPSO_API_KEY", "KAPSO_PHONE_NUMBER_ID", "WHATSAPP_TO"]
    cfg = {k: os.getenv(k, "") for k in keys}
    missing = [k for k, v in cfg.items() if not v]
    if missing:
        typer.secho(
            f"Missing in .env: {', '.join(missing)}", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)
    return cfg


def upload_media(cfg: dict[str, str], image_path: Path) -> str:
    url = f"{KAPSO_BASE}/{cfg['KAPSO_PHONE_NUMBER_ID']}/media"
    with open(image_path, "rb") as f:
        resp = requests.post(
            url,
            headers={"X-API-Key": cfg["KAPSO_API_KEY"]},
            files={"file": (image_path.name, f, "image/jpeg")},
            data={"messaging_product": "whatsapp"},
        )
    resp.raise_for_status()
    media_id = resp.json().get("id")
    if not media_id:
        typer.secho(
            f"upload succeeded but no media id in response: {resp.text}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    return media_id


def send_image(cfg: dict[str, str], media_id: str, caption: str | None) -> dict:
    url = f"{KAPSO_BASE}/{cfg['KAPSO_PHONE_NUMBER_ID']}/messages"
    body: dict = {
        "messaging_product": "whatsapp",
        "to": cfg["WHATSAPP_TO"],
        "type": "image",
        "image": {"id": media_id},
    }
    if caption:
        body["image"]["caption"] = caption
    resp = requests.post(
        url,
        headers={
            "X-API-Key": cfg["KAPSO_API_KEY"],
            "Content-Type": "application/json",
        },
        json=body,
    )
    resp.raise_for_status()
    return resp.json()


@app.command()
def main(
    image: Path | None = typer.Option(
        None, help="Path to QR PNG. If omitted reads path from stdin."
    ),
    caption: str | None = typer.Option(None, help="Optional caption for the image."),
) -> None:
    """Upload a QR image to WhatsApp and send it."""
    if image is None:
        raw = sys.stdin.read().strip()
        if not raw:
            typer.secho("no image path provided", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
        image = Path(raw)

    if not image.exists():
        typer.secho(f"file not found: {image}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    cfg = get_config()

    typer.echo(f"uploading {image.name}...")
    media_id = upload_media(cfg, image)
    typer.echo(f"media_id: {media_id}")

    typer.echo(f"sending to {cfg['WHATSAPP_TO']}...")
    result = send_image(cfg, media_id, caption)
    typer.echo(f"sent: {result}")


if __name__ == "__main__":
    app()
