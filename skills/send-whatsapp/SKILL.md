---
name: send-whatsapp
description: Send an image (QR code) via WhatsApp using the Kapso API. Uploads to WhatsApp media storage first — no public URL needed.
---

# send-whatsapp

Entry point: `scripts/send_whatsapp.py` (Typer CLI).

## Usage

```sh
# Direct:
poetry run scripts/send_whatsapp.py --image state/360002939006860.png --caption "Retiralo: 360002939006860"

# Piped from generate-qr (reads path from stdin):
echo 360002939006860 | poetry run scripts/generate_qr.py | poetry run scripts/send_whatsapp.py

# Full pipeline:
poetry run scripts/poll_inbox.py show <id> \
  | poetry run scripts/extract_tracking.py \
  | poetry run scripts/generate_qr.py \
  | poetry run scripts/send_whatsapp.py
```

## How it works

1. Uploads the PNG to `POST /v24.0/{phoneNumberId}/media` → gets a `media_id`.
2. Sends the image message to `POST /v24.0/{phoneNumberId}/messages` referencing the `media_id`.

No third-party hosting or public URLs involved.

## Env vars required

- `KAPSO_API_KEY`
- `KAPSO_PHONE_NUMBER_ID`
- `WHATSAPP_TO`
