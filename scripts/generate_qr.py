#!/usr/bin/env python
"""Generate an Andreani QR code PNG from a tracking number.

Uses the andreani_qr library directly. Reads tracking from stdin or --tracking.

    echo 360002939006860 | poetry run scripts/generate_qr.py
    poetry run scripts/generate_qr.py --tracking 360002939006860

Outputs the path to the generated PNG file.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from andreani_qr.qr import QR, InvalidCodeError

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "state"

app = typer.Typer(add_completion=False, help=__doc__)


@app.command()
def main(
    tracking: str | None = typer.Option(
        None, help="Andreani tracking number. If omitted reads from stdin."
    ),
    output_dir: Path = typer.Option(
        OUTPUT_DIR, "-o", "--output-dir", help="Directory for the PNG."
    ),
) -> None:
    """Generate a QR PNG and print its path to stdout."""
    if tracking is None:
        tracking = sys.stdin.read().strip()
    if not tracking:
        typer.secho("no tracking number provided", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    try:
        qr = QR(tracking)
    except InvalidCodeError as e:
        typer.secho(f"invalid tracking number: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    output_dir.mkdir(parents=True, exist_ok=True)
    jpg_path = output_dir / f"{tracking}.jpg"
    img = qr.encode().convert("RGB")
    img.save(jpg_path, "JPEG")

    typer.echo(str(jpg_path))


if __name__ == "__main__":
    app()
