#!/usr/bin/env python
"""Poll the retiralo AgentMail inbox for unread MercadoLibre pickup emails.

Commands:
    find                    List matching unread messages as JSON.
    mark-read <message_id>  Remove the "unread" label (our done-state).
    show <message_id>       Fetch full message text for downstream skills.

A message is a match when all three hold:
  - the message is unread (agentmail "unread" label)
  - from contains "no-reply@mercadolibre.com.ar" (the only authorized sender)
  - subject contains "Ya puedes retirar tu compra en Sucursal Andreani"

Read state is server-side in AgentMail — no local state file needed.
"""

from __future__ import annotations

import json
import os
import re
from html import unescape
from pathlib import Path
from typing import Any

import typer
from dotenv import load_dotenv
from agentmail import AgentMail

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

SENDER_CONTAINS = "no-reply@mercadolibre.com.ar"
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


def get_ctx() -> tuple[AgentMail, str]:
    load_dotenv(ENV_PATH)
    api_key = os.getenv("AGENTMAIL_API_KEY")
    inbox_id = os.getenv("AGENTMAIL_INBOX_ID")
    if not api_key or not inbox_id:
        typer.secho(
            "AGENTMAIL_API_KEY or AGENTMAIL_INBOX_ID missing in .env",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    return AgentMail(api_key=api_key), inbox_id


def matches(item: Any) -> bool:
    sender = (item.from_ or "").lower()
    subject = item.subject or ""
    return SENDER_CONTAINS in sender and SUBJECT_CONTAINS in subject


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
    client, inbox_id = get_ctx()
    resp = client.inboxes.messages.list(
        inbox_id=inbox_id, limit=limit, labels=[UNREAD_LABEL]
    )
    hits = []
    for m in resp.messages or []:
        if not matches(m):
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
    client, inbox_id = get_ctx()
    client.inboxes.messages.update(
        inbox_id=inbox_id, message_id=message_id, remove_labels=[UNREAD_LABEL]
    )
    typer.echo(f"marked read: {message_id}")


def html_to_text(html: str) -> str:
    """Strip HTML to plain text, preserving block-level breaks."""
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", html)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    return s.strip()


@app.command()
def show(message_id: str) -> None:
    """Print a message's text body (for downstream extract-tracking skill)."""
    client, inbox_id = get_ctx()
    msg = client.inboxes.messages.get(inbox_id=inbox_id, message_id=message_id)
    text = msg.text or msg.extracted_text or ""
    if not text and msg.html:
        text = html_to_text(msg.html)
    out = {
        "message_id": msg.message_id,
        "from": msg.from_,
        "subject": msg.subject,
        "text": text,
    }
    typer.echo(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
