---
name: generate-qr
description: Generate an Andreani QR code PNG from a tracking number using the andreani_qr library.
---

# generate-qr

Entry point: `scripts/generate_qr.py` (Typer CLI).

## Usage

```sh
# From tracking number directly:
poetry run scripts/generate_qr.py --tracking 360002939006860

# Piped from extract-tracking:
poetry run scripts/extract_tracking.py --text "..." | poetry run scripts/generate_qr.py

# Full pipe from inbox:
poetry run scripts/poll_inbox.py show <id> | poetry run scripts/extract_tracking.py | poetry run scripts/generate_qr.py
```

## Output

Prints the absolute path to the generated PNG on stdout (e.g. `/path/to/state/360002939006860.png`).
PNGs are saved to `state/` by default (override with `-o`).

## How the agent loop uses it

Receives the tracking number from `extract-tracking`, emits the PNG path for `send-whatsapp`.
