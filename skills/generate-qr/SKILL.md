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

## macOS libzbar path

On macOS, Homebrew installs libzbar to `/opt/homebrew/lib` (Apple Silicon)
or `/usr/local/lib` (Intel), which pyzbar's `ctypes.util.find_library`
does not search by default. If the script exits with `ImportError: Unable
to find zbar shared library`, run it as:

```sh
cd ${CLAUDE_PLUGIN_ROOT} && DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib poetry run scripts/generate_qr.py --tracking 360002939006860
```

## Output

Prints the absolute path to the generated PNG on stdout (e.g.
`${CLAUDE_PLUGIN_ROOT}/state/360002939006860.png`). PNGs are saved to
`${CLAUDE_PLUGIN_ROOT}/state/` by default (override with `-o`).

## How the agent loop uses it

Receives the tracking number from `extract-tracking`, emits the PNG path for `send-whatsapp`.
