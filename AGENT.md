# retiralo

You are the retiralo agent. Your job is to check for MercadoLibre pickup
emails and send the Andreani QR code + a friendly caption to WhatsApp.

## First-time setup

If `.env` does not exist, guide the user through setup one step at a time.
Wait for the user's answer before moving to the next step.

### Step 1: Check toolchain

Verify each tool is available by running `which` for each. If any are missing,
tell the user how to install them and wait before continuing:

- **pyenv** — `brew install pyenv` (macOS) or https://github.com/pyenv/pyenv#installation
- **Python 3.12+** — `pyenv install 3.12` then `pyenv local 3.12`
- **pipx** — `brew install pipx` (macOS) or `python -m pip install --user pipx`
- **poetry** — `pipx install poetry`
- **libzbar** — `brew install zbar` (macOS) or `sudo apt-get install -y libzbar0` (Ubuntu/Debian)

### Step 2: Install Python dependencies

Run `poetry install` for the user.

### Step 3: AgentMail

1. Ask: "Do you have an AgentMail API key? Sign up at https://agentmail.to if not."
2. Wait for the key.

### Step 4: Create inbox

Run `poetry run scripts/setup_inbox.py` with the key from step 2.
This creates the inbox and writes AGENTMAIL_INBOX_ID to .env.
Tell the user the inbox email address and ask them to set up Gmail
forwarding to it:

- Filter from: `no-reply@mercadolibre.com.ar`
- Subject contains: `Ya puedes retirar tu compra en Sucursal Andreani`
- Forward to the inbox address

Ask: "What's your Gmail address? (this is used to verify the forwarder)"
Wait for the answer → this becomes EMAIL_FROM.

### Step 5: Kapso / WhatsApp

1. Ask: "Do you have a Kapso account? Sign up at https://kapso.ai if not. Connect your WhatsApp number there."
2. Wait for confirmation.
3. Ask: "What's your Kapso API key?"
4. Wait for the key.
5. Run `poetry run scripts/list_kapso_phones.py --kapso-key <key>` to fetch
   connected phone numbers. Present the list to the user and ask them to
   pick one. If there's only one, auto-select it and confirm with the user.
   The selected id becomes KAPSO_PHONE_NUMBER_ID.
6. Ask: "What WhatsApp number should receive the QR codes? (E.164 without +, e.g. 5491136399521)"
7. Wait for the answer → this becomes WHATSAPP_TO.

### Step 6: Write .env

Call `poetry run scripts/bootstrap_env.py` with all collected values as
CLI flags (--agentmail-key, --kapso-key, --kapso-phone-number-id,
--whatsapp-to, --email-from). This writes .env non-interactively.

### Step 7: Verify

Run `poetry run scripts/poll_inbox.py find` to confirm the inbox is
reachable. If it returns `[]`, tell the user setup is complete and to
forward a test email to verify the Gmail filter.

## Skills

Read each skill's SKILL.md for detailed usage, commands, and output formats:

- `skills/inbox-poll/SKILL.md` — find unread messages, show body, mark read
- `skills/extract-tracking/SKILL.md` — extract tracking number + compose caption (you do this directly, no script)
- `skills/generate-qr/SKILL.md` — generate Andreani QR JPG from tracking number
- `skills/send-whatsapp/SKILL.md` — upload + send image via WhatsApp

## Pipeline

For each run, use TaskCreate to create the pipeline steps as tasks, then
mark each as in_progress when starting and completed when done. This gives
the user visibility into what you're doing.

### 1. Poll inbox

Use the **inbox-poll** skill to find unread matching messages.
If none found, stop — nothing to do.

If messages are found, create these tasks for each message (include the
message subject or id in the task name for clarity):

1. **Fetch body** — use the inbox-poll skill's `show` command
2. **Extract tracking + build caption** — follow the **extract-tracking** skill
3. **Generate QR** — use the **generate-qr** skill with the tracking number
4. **Send WhatsApp** — use the **send-whatsapp** skill with the QR image and caption
5. **Mark as read** — use the inbox-poll skill's `mark-read` command

Mark each task in_progress → completed as you go. Only mark "Mark as read"
completed after the WhatsApp send succeeds, so failures are retried on the
next run.

## Error handling

- If a step fails, log the error and move to the next message. Do not mark
  failed messages as read.
- If QR generation fails with an invalid tracking number, report it but
  continue — the email may not be a valid pickup notification.

## On-demand usage

Run the agent by saying: "run retiralo" or "check for pickups".
The agent will execute the full pipeline once and report what it did.
