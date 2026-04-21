---
name: inbox-poll
description: Find unread, authorized MercadoLibre pickup emails in the retiralo AgentMail inbox. Fetch full body. Mark as read.
---

# inbox-poll

Entry point: `${CLAUDE_PLUGIN_ROOT}/scripts/poll_inbox.py` (Typer CLI).
Always invoke from the plugin root so poetry finds `pyproject.toml`.

Security gate: only messages whose `from` contains `EMAIL_FROM` (set in `.env`)
are considered, so arbitrary senders to the AgentMail address are ignored.

## Commands

**Important:** the AgentMail `message_id` is an RFC Message-ID and includes the
literal `<` and `>` characters (e.g. `<CAGTiWNt...@mail.gmail.com>`). Pass it
to `show`/`mark-read` **exactly as returned by `find`** — including the angle
brackets — wrapped in **single quotes** so the shell does not interpret `<>`
as redirection or `+`/`@` specially. Do not strip the brackets and do not
substitute placeholder `<message_id>` syntax; use the real id verbatim.

```sh
# 1) Find unread matches (read-only). Outputs JSON array.
cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/poll_inbox.py find [--limit 50]

# 2) Fetch full text body of one message (downstream extract-tracking uses this).
cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/poll_inbox.py show '<CAGTiWNt...@mail.gmail.com>'

# 3) Mark one message as read (removes "unread" label — our done-state).
cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/poll_inbox.py mark-read '<CAGTiWNt...@mail.gmail.com>'

# Testing convenience: find + auto-mark-read in one call.
cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/poll_inbox.py find --mark-read
```

## Match rules

A message is a hit when all three hold:

- it has the `unread` label (server-side state, no local file needed)
- `from` contains `EMAIL_FROM`
- `subject` contains `Ya puedes retirar tu compra en Sucursal Andreani`

## find output shape

```json
[
  {
    "message_id": "<...@mail.gmail.com>",
    "thread_id": "...",
    "from": "Name <addr@example.com>",
    "subject": "Fwd: Ya puedes retirar ...",
    "timestamp": "2026-04-15T21:02:00+00:00"
  }
]
```

## How the agent loop uses it

1. `find` → JSON list of pending messages.
2. For each: `show <id>` → pass `text` to `extract-tracking` skill.
3. After the WhatsApp send succeeds: `mark-read <id>`.

Order matters: only mark read after the full pipeline succeeded, otherwise a
failure in a later skill would lose the message.
