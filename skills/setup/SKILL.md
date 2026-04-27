---
name: setup
description: First-run setup for retiralo. Invoke when ${CLAUDE_PLUGIN_ROOT}/.env does not exist. Guides user through toolchain check, AgentMail inbox, Kapso/WhatsApp, and writes .env.
---

# setup

Run this **once**, before the first pipeline run. On every subsequent
invocation the agent's preflight check will skip this skill because
`.env` already exists.

All commands run from the plugin root. Prefix every `poetry` invocation
with `cd ${CLAUDE_PLUGIN_ROOT} &&` so poetry finds `pyproject.toml` and
the project virtualenv.

Walk the user through these steps **one at a time**. Wait for the user's
answer before advancing.

## Step 1: Check toolchain

Verify each tool is available by running `which` for each. If any are
missing, tell the user how to install them and wait before continuing:

- **pyenv** — `brew install pyenv` (macOS) or https://github.com/pyenv/pyenv#installation
- **Python 3.12+** — `pyenv install 3.12` then `pyenv local 3.12`
- **pipx** — `brew install pipx` (macOS) or `python -m pip install --user pipx`
- **poetry** — `pipx install poetry`
- **libzbar** — `brew install zbar` (macOS) or `sudo apt-get install -y libzbar0` (Ubuntu/Debian)

## Step 2: Install Python dependencies

```sh
cd ${CLAUDE_PLUGIN_ROOT} && poetry install
```

## Step 3: AgentMail

1. Ask: "Do you have an AgentMail API key? Sign up at https://agentmail.to if not."
2. Wait for the key.

## Step 4: Create inbox

```sh
cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/setup_inbox.py
```

Pass the key from Step 3. The script creates the inbox and writes
`AGENTMAIL_INBOX_ID` into `${CLAUDE_PLUGIN_ROOT}/.env`.

Tell the user the inbox email address and ask them to set up Gmail
forwarding to it:

- Filter from: `no-reply@mercadolibre.com.ar`
- Subject contains: `Ya puedes retirar tu compra en Sucursal Andreani`
- Forward to the inbox address

The agent matches messages whose `from` contains
`no-reply@mercadolibre.com.ar`, so direct sends from MercadoLibre and
forwarded copies that preserve the original sender both work.

## Step 5: Kapso / WhatsApp

1. Ask: "Do you have a Kapso account? Sign up at https://kapso.ai if not. Connect your WhatsApp number there."
2. Wait for confirmation.
3. Ask: "What's your Kapso API key?"
4. Wait for the key.
5. Run:
   ```sh
   cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/list_kapso_phones.py --kapso-key <key>
   ```
   Present the list to the user and ask them to pick one. If there's
   only one, auto-select it and confirm with the user. The selected id
   becomes `KAPSO_PHONE_NUMBER_ID`.
6. Ask: "What WhatsApp number should receive the QR codes? (E.164 without +, e.g. 5491136399521)"
7. Wait for the answer → this becomes `WHATSAPP_TO`.
8. Tell the user: "Meta blocks unsolicited business→user messages unless
   your Facebook Business is verified. If it isn't, send a WhatsApp
   message from WHATSAPP_TO to the Kapso-connected number before each
   run to open a 24-hour window — otherwise the QR send will fail."

## Step 6: Write .env

```sh
cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/bootstrap_env.py \
    --agentmail-key <key> \
    --kapso-key <key> \
    --kapso-phone-number-id <id> \
    --whatsapp-to <number>
```

Writes `${CLAUDE_PLUGIN_ROOT}/.env` non-interactively.

## Step 7: Verify

```sh
cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/poll_inbox.py find
```

Should return `[]` (no unread matches yet). If it errors instead, inspect
the message against the toolchain / credentials collected above. If it
returns `[]` cleanly, tell the user setup is complete and to forward a
test email to verify the Gmail filter.
