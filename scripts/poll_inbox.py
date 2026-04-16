#!/usr/bin/env python
"""Poll the retiralo AgentMail inbox for unread, authorized pickup emails.

Commands:
    find                    List matching unread messages as JSON.
    mark-read <message_id>  Remove the "unread" label (our done-state).
    show <message_id>       Fetch full message text for downstream skills.

A message is a match when all three hold:
  - the message is unread (agentmail "unread" label)
  - from contains EMAIL_FROM (authorized forwarder, security gate)
  - subject contains "Ya puedes retirar tu compra en Sucursal Andreani"

Read state is server-side in AgentMail — no local state file needed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import typer
from dotenv import load_dotenv
from agentmail import AgentMail

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

SUBJECT_CONTAINS = "Ya puedes retirar tu compra en Sucursal Andreani"
UNREAD_LABEL = "unread"

app = typer.Typer(
    add_completion=False,
    help=__doc__,
    invoke_without_command=True,
    no_args_is_help=False,
)


@app.callback()
def _default(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(find)


def get_ctx() -> tuple[AgentMail, str, str]:
    load_dotenv(ENV_PATH)
    api_key = os.getenv("AGENTMAIL_API_KEY")
    inbox_id = os.getenv("AGENTMAIL_INBOX_ID")
    email_from = (os.getenv("EMAIL_FROM") or "").lower()
    if not api_key or not inbox_id or not email_from:
        typer.secho(
            "AGENTMAIL_API_KEY, AGENTMAIL_INBOX_ID, or EMAIL_FROM missing in .env",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    return AgentMail(api_key=api_key), inbox_id, email_from


def matches(item: Any, email_from: str) -> bool:
    sender = (item.from_ or "").lower()
    subject = item.subject or ""
    return email_from in sender and SUBJECT_CONTAINS in subject


@app.command()
def find(
    limit: int = typer.Option(50, help="Max unread messages to scan."),
    mark_read: bool = typer.Option(
        False,
        "--mark-read",
        help="Also mark each returned message as read (testing only).",
    ),
) -> None:
    """Emit JSON array of unread matching messages."""
    client, inbox_id, email_from = get_ctx()
    resp = client.inboxes.messages.list(
        inbox_id=inbox_id, limit=limit, labels=[UNREAD_LABEL]
    )
    hits = []
    for m in resp.messages or []:
        if not matches(m, email_from):
            continue
        hits.append(
            {
                "message_id": m.message_id,
                "thread_id": m.thread_id,
                "from": m.from_,
                "subject": m.subject,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            }
        )
        if mark_read:
            client.inboxes.messages.update(
                inbox_id=inbox_id, message_id=m.message_id, remove_labels=[UNREAD_LABEL]
            )
    typer.echo(json.dumps(hits, indent=2, ensure_ascii=False))


@app.command("mark-read")
def mark_read(message_id: str) -> None:
    """Mark a message as read (removes the unread label)."""
    client, inbox_id, _ = get_ctx()
    client.inboxes.messages.update(
        inbox_id=inbox_id, message_id=message_id, remove_labels=[UNREAD_LABEL]
    )
    typer.echo(f"marked read: {message_id}")


@app.command()
def show(message_id: str) -> None:
    """Print a message's text body (for downstream extract-tracking skill)."""
    client, inbox_id, _ = get_ctx()
    msg = client.inboxes.messages.get(inbox_id=inbox_id, message_id=message_id)
    out = {
        "message_id": msg.message_id,
        "from": msg.from_,
        "subject": msg.subject,
        "text": msg.text,
    }
    typer.echo(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
