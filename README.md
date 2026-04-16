# Retiralo

A Claude Code agent that watches for MercadoLibre Andreani pickup emails, extracts the tracking number, generates the QR code, and sends it to your WhatsApp.

## How it works

1. You set up a Gmail filter to forward MercadoLibre pickup notifications to an [AgentMail](https://agentmail.to) inbox
2. The agent polls the inbox for new emails
3. It reads the email, extracts the Andreani tracking number, and composes a friendly caption
4. It generates the Andreani QR code using [andreani-qr](https://github.com/teosibileau/andreani-qr)
5. It uploads the QR and sends it to your WhatsApp via [Kapso](https://kapso.ai)

## Prerequisites

- [Claude Code](https://claude.ai/code) CLI or desktop app
- Python 3.12+
- [Poetry](https://python-poetry.org/)
- `libzbar` system library (macOS: `brew install zbar`, Ubuntu: `sudo apt-get install -y libzbar0`)
- A Gmail account with MercadoLibre purchase notifications
- An [AgentMail](https://agentmail.to) account ([docs](https://docs.agentmail.to))
- A [Kapso](https://kapso.ai) account with a connected WhatsApp number ([docs](https://docs.kapso.ai))

## Setup

Clone the repo and open it in Claude Code:

```sh
git clone https://github.com/teosibileau/retiralo.git
cd retiralo
```

Then tell Claude: **"set this up"**

The agent reads `CLAUDE.md` and walks you through setup step by step:

1. Installs system and Python dependencies
2. Asks for your AgentMail API key and creates an inbox
3. Guides you through Gmail forwarding setup
4. Asks for your Kapso API key and auto-detects your WhatsApp phone number
5. Writes `.env` with all collected values
6. Verifies the inbox is reachable

No credentials are hardcoded in the repo. Everything lives in `.env` (gitignored).

## Usage

Once setup is complete, tell the agent:

```
check for pickups
```

or

```
run retiralo
```

The agent will poll the inbox, process any unread pickup emails, and send QR codes to your WhatsApp.

## Project structure

```
CLAUDE.md              -> AGENT.md (symlink, loaded by Claude on startup)
AGENT.md               Agent instructions: setup flow + pipeline
skills/
  inbox-poll/          Poll AgentMail for unread matching emails
  extract-tracking/    Extract tracking number + compose caption (LLM-driven)
  generate-qr/         Generate Andreani QR code from tracking number
  send-whatsapp/       Upload + send image via Kapso WhatsApp API
scripts/
  bootstrap_env.py     Write .env from CLI flags
  setup_inbox.py       Create AgentMail inbox idempotently
  list_kapso_phones.py List connected WhatsApp numbers from Kapso
  poll_inbox.py        Find/show/mark-read emails in AgentMail
  generate_qr.py       Generate QR JPG using andreani-qr library
  send_whatsapp.py     Upload media + send via Kapso
tests/                 pytest tests for all scripts
```

## Third-party services

| Service                           | What it does                                 | Docs                                           |
| --------------------------------- | -------------------------------------------- | ---------------------------------------------- |
| [AgentMail](https://agentmail.to) | Receives forwarded emails from Gmail         | [docs.agentmail.to](https://docs.agentmail.to) |
| [Kapso](https://kapso.ai)         | Sends WhatsApp messages via Meta's Cloud API | [docs.kapso.ai](https://docs.kapso.ai)         |

## Development

```sh
poetry install
poetry run pytest -v
pre-commit install
pre-commit run --all-files
```

## License

MIT
