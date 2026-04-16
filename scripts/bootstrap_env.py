#!/usr/bin/env python
"""Create .env if it does not exist yet.

Non-interactive (called by the agent with all values collected):

    poetry run scripts/bootstrap_env.py \
        --agentmail-key am_us_... \
        --kapso-key 7b43... \
        --kapso-phone-number-id 1045... \
        --whatsapp-to 5491... \
        --email-from you@gmail.com

Safe by default: skips if .env exists. Use --force to overwrite.
"""

from __future__ import annotations

from pathlib import Path

import typer

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"

app = typer.Typer(add_completion=False, help=__doc__)


@app.command()
def main(
    force: bool = typer.Option(False, "--force", help="Overwrite .env if it exists."),
    agentmail_key: str = typer.Option(
        ..., "--agentmail-key", help="AgentMail API key."
    ),
    kapso_key: str = typer.Option(..., "--kapso-key", help="Kapso API key."),
    kapso_phone_number_id: str = typer.Option(
        ..., "--kapso-phone-number-id", help="Kapso/Meta phone number id."
    ),
    whatsapp_to: str = typer.Option(
        ..., "--whatsapp-to", help="Destination number, E.164 without +."
    ),
    email_from: str = typer.Option(
        ..., "--email-from", help="Authorized forwarder address."
    ),
) -> None:
    """Write .env with the provided values."""
    if ENV_PATH.exists() and not force:
        typer.secho(
            f".env already exists at {ENV_PATH} — nothing to do.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=0)

    values = {
        "AGENTMAIL_API_KEY": agentmail_key.strip(),
        "KAPSO_API_KEY": kapso_key.strip(),
        "KAPSO_PHONE_NUMBER_ID": kapso_phone_number_id.strip(),
        "WHATSAPP_TO": whatsapp_to.strip(),
        "EMAIL_FROM": email_from.strip().lower(),
        "AGENTMAIL_INBOX_ID": "",
    }
    body = "".join(f"{k}={v}\n" for k, v in values.items())
    ENV_PATH.write_text(body)
    typer.secho(f"wrote {ENV_PATH}", fg=typer.colors.GREEN)
    typer.echo("keys: " + ", ".join(values.keys()))


if __name__ == "__main__":
    app()
