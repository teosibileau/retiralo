#!/usr/bin/env python
"""Idempotently create the AgentMail inbox for retiralo and persist its id to .env.

Run once during setup:
    poetry run python scripts/setup_inbox.py

Re-running is safe: AgentMail uses client_id for idempotent creation, and this
script only rewrites AGENTMAIL_INBOX_ID in .env if it's missing or different.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import typer
from dotenv import load_dotenv
from agentmail import AgentMail
from agentmail.inboxes.types import CreateInboxRequest

CLIENT_ID = "retiralo-inbox-v1"
DISPLAY_NAME = "retiralo"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

app = typer.Typer(add_completion=False, help=__doc__)


def upsert_env(key: str, value: str) -> None:
    text = ENV_PATH.read_text()
    pattern = re.compile(rf"^{re.escape(key)}=.*$", re.MULTILINE)
    if pattern.search(text):
        new_text = pattern.sub(f"{key}={value}", text)
    else:
        new_text = text.rstrip() + f"\n{key}={value}\n"
    if new_text != text:
        ENV_PATH.write_text(new_text)


@app.command()
def main(
    client_id: str = typer.Option(
        CLIENT_ID, help="Idempotency key for AgentMail create."
    ),
    display_name: str = typer.Option(DISPLAY_NAME, help="Inbox display name."),
) -> None:
    """Create (or reuse) the retiralo inbox and persist AGENTMAIL_INBOX_ID in .env."""
    load_dotenv(ENV_PATH)
    api_key = os.getenv("AGENTMAIL_API_KEY")
    if not api_key:
        typer.secho("AGENTMAIL_API_KEY not set in .env", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    client = AgentMail(api_key=api_key)
    inbox = client.inboxes.create(
        request=CreateInboxRequest(client_id=client_id, display_name=display_name)
    )

    upsert_env("AGENTMAIL_INBOX_ID", inbox.inbox_id)

    typer.echo(f"inbox_id: {inbox.inbox_id}")
    typer.echo(f"address:  {inbox.email}")
    typer.echo(".env updated: AGENTMAIL_INBOX_ID")


if __name__ == "__main__":
    app()
