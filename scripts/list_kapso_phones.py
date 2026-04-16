#!/usr/bin/env python
"""List production phone numbers from a Kapso account.

poetry run scripts/list_kapso_phones.py --kapso-key 7b43...
"""

from __future__ import annotations

import json

import requests
import typer

KAPSO_PHONES_URL = "https://api.kapso.ai/platform/v1/whatsapp/phone_numbers"

app = typer.Typer(add_completion=False, help=__doc__)


@app.command()
def main(
    kapso_key: str = typer.Option(..., "--kapso-key", help="Kapso API key."),
) -> None:
    """Fetch and print connected WhatsApp phone numbers as JSON."""
    resp = requests.get(KAPSO_PHONES_URL, headers={"X-API-Key": kapso_key})
    resp.raise_for_status()

    phones = [
        {
            "phone_number_id": p["phone_number_id"],
            "name": p.get("name") or p.get("display_name") or "unnamed",
            "number": p.get("display_phone_number") or "no number",
            "kind": p.get("kind", "unknown"),
        }
        for p in resp.json().get("data", [])
        if p.get("kind") != "sandbox"
    ]

    typer.echo(json.dumps(phones, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
