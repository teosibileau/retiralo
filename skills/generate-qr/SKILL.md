---
name: generate-qr
description: Generate an Andreani QR code PNG from a tracking number using the andreani_qr library.
---

# generate-qr

Entry point: `${CLAUDE_PLUGIN_ROOT}/scripts/generate_qr.py` (Typer CLI).
Always invoke from the plugin root so poetry finds `pyproject.toml`.

## Usage

```sh
# From tracking number directly:
cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/generate_qr.py --tracking 360002939006860
```

## macOS libzbar path (READ THIS — known recurring failure)

On macOS, Homebrew installs libzbar to `/opt/homebrew/lib` (Apple Silicon)
or `/usr/local/lib` (Intel), which pyzbar's `ctypes.util.find_library`
does not search by default. The script then dies with
`ImportError: Unable to find zbar shared library`.

**`DYLD_FALLBACK_LIBRARY_PATH=... poetry run ...` DOES NOT WORK.** macOS
SIP strips `DYLD_*` env vars when poetry's launcher execs python, so the
var never reaches the process. Do not retry it; it has failed repeatedly.

**Always** run generate_qr.py by invoking the virtualenv's python
directly with the env var set:

```sh
cd ${CLAUDE_PLUGIN_ROOT} && DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib "$(poetry env info --path)/bin/python" scripts/generate_qr.py --tracking 360002939006860
```

If libzbar is missing entirely (`ls /opt/homebrew/lib/libzbar*` finds
nothing), install it with `brew install zbar` first.

Other scripts (poll_inbox, send_whatsapp) don't touch zbar; plain
`poetry run` is fine for them.

## Output

Prints the absolute path to the generated PNG on stdout (e.g.
`${CLAUDE_PLUGIN_ROOT}/state/360002939006860.png`). PNGs are saved to
`${CLAUDE_PLUGIN_ROOT}/state/` by default (override with `-o`).

## How the agent loop uses it

Receives the tracking number from `extract-tracking`, emits the PNG path for `send-whatsapp`.
