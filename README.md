# Retiralo

A Claude Code plugin that watches for MercadoLibre Andreani pickup
emails, extracts the tracking number, generates the QR code, and sends
it to your WhatsApp.

## How it works

1. You set up a Gmail filter to forward MercadoLibre pickup notifications to an [AgentMail](https://agentmail.to) inbox.
2. The `retiralo` agent polls the inbox for new emails.
3. It reads the email, extracts the Andreani tracking number, and composes a friendly caption.
4. It generates the Andreani QR code using [andreani-qr](https://github.com/teosibileau/andreani-qr).
5. It uploads the QR and sends it to your WhatsApp via [Kapso](https://kapso.ai).

## Install

From Claude Code, register this repo as a marketplace and install the
plugin from it:

```
/plugin marketplace add teosibileau/retiralo
/plugin install retiralo@retiralo-marketplace
```

The first command registers the repo as a marketplace; the second
installs the plugin from it. Confirm it loaded:

```
/agents
```

`retiralo` should appear in the list.

## Prerequisites

The agent's setup skill installs the Python dependencies for you, but
the host needs these system tools first:

- [Claude Code](https://claude.ai/code) CLI or desktop app
- [pyenv](https://github.com/pyenv/pyenv) — Python version manager (Python 3.12+ required)
- [pipx](https://pipx.pypa.io/) — isolated CLI installs
- [Poetry](https://python-poetry.org/) (`pipx install poetry`)
- `libzbar` system library — macOS: `brew install zbar`; Ubuntu: `sudo apt-get install -y libzbar0`

You'll also need accounts with:

- Gmail (for the MercadoLibre notifications)
- [AgentMail](https://agentmail.to) ([docs](https://docs.agentmail.to))
- [Kapso](https://kapso.ai) with a connected WhatsApp number ([docs](https://docs.kapso.ai))

## First run

Say:

```
run retiralo
```

Because `.env` does not exist yet, the agent invokes the **setup** skill
and walks you through:

1. Toolchain check
2. `poetry install` of Python deps
3. AgentMail API key → inbox creation → Gmail forwarding filter
4. Kapso API key → WhatsApp phone number selection → destination number
5. `.env` written to the plugin root
6. Verification poll

## Usage

Once setup is complete, trigger a run any time with:

```
run retiralo
```

or

```
check for pickups
```

The agent polls the inbox, processes any unread pickup emails, and sends
QR codes to your WhatsApp. You'll see each step as a task so you know
what it's doing.

## The Meta / WhatsApp caveat

Kapso sends through Meta's WhatsApp Cloud API, which blocks unsolicited
business→user messages unless the Facebook Business is verified. If
yours isn't, send a WhatsApp message from your destination number to
the Kapso-connected number before each run to open a 24-hour service
window — otherwise the send will fail.

Complete Business Verification in Meta Business Manager to remove this
restriction.

## Third-party services

| Service                           | What it does                                 | Docs                                           |
| --------------------------------- | -------------------------------------------- | ---------------------------------------------- |
| [AgentMail](https://agentmail.to) | Receives forwarded emails from Gmail         | [docs.agentmail.to](https://docs.agentmail.to) |
| [Kapso](https://kapso.ai)         | Sends WhatsApp messages via Meta's Cloud API | [docs.kapso.ai](https://docs.kapso.ai)         |

## Development

See [`AGENT.md`](./AGENT.md) for the plugin layout, local-test install,
and publishing notes.

```sh
poetry install
poetry run pytest -v
pre-commit install
pre-commit run --all-files
```

## License

MIT
