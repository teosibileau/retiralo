---
name: send-whatsapp
description: Send an image (QR code) via WhatsApp using the Kapso API. Uploads to WhatsApp media storage first — no public URL needed.
---

# send-whatsapp

Entry point: `${CLAUDE_PLUGIN_ROOT}/scripts/send_whatsapp.py` (Typer CLI).
Always invoke from the plugin root so poetry finds `pyproject.toml`.

## Usage

```sh
cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/send_whatsapp.py \
    --image ${CLAUDE_PLUGIN_ROOT}/state/360002939006860.png \
    --caption "Retiralo: 360002939006860"
```

## How it works

1. Uploads the PNG to `POST /v24.0/{phoneNumberId}/media` → gets a `media_id`.
2. Sends the image message to `POST /v24.0/{phoneNumberId}/messages` referencing the `media_id`.

No third-party hosting or public URLs involved.

## Env vars required

- `KAPSO_API_KEY`
- `KAPSO_PHONE_NUMBER_ID`
- `WHATSAPP_TO`

## Meta business-initiation constraint

Kapso sends through Meta's WhatsApp Cloud API, which disallows unsolicited
business→user messages unless the Facebook Business is verified. Without
verification, the recipient must message the business number first to open
a 24-hour service window; sends outside that window will fail or require a
pre-approved template.

To avoid this: either complete Business Verification in Meta Business
Manager, or send any message from `WHATSAPP_TO` to the Kapso-connected
number before each run (the 24h window resets on every inbound message).
