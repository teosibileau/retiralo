---
name: extract-tracking
description: Extract the Andreani tracking number and compose an emoji-rich WhatsApp caption from a MercadoLibre pickup email body. No script — the agent does this directly.
---

# extract-tracking

This skill has no script. The agent reads the email body (from `poll_inbox.py show`) and produces two things:

1. **tracking** — the Andreani tracking number (15 digits starting with `36000`)
2. **caption** — an emoji-rich WhatsApp caption in Spanish

## How to extract

From the email text, find the line containing `código de seguimiento:` followed by a 15-digit number starting with `36000`. That is the tracking number.

Also extract:

- **Product description** — appears after "Llegaron" (e.g. "Pigtail Patchcord Fibra Óptica Sc/a... y 1 producto mas")
- **Pickup deadline** — appears after "Retirá tu compra en Sucursal Andreani hasta" (e.g. "el lunes 20 de abril")
- **Pickup address** — appears after "Sucursal Andreani %BREAK_LINE%" (e.g. "Ruta 40 4580, El Bolson (C.P. 8430), Río Negro")
- **Hours** — appears after the address, before "Ver en el mapa" (e.g. "Lunes a viernes de 8 a 18 hs. - Sábado de 8 a 13 hs.")

## Caption format

Build the caption using this template (use emoji liberally):

```
📦 *Retiralo!* {product description}

⏰ Tenés hasta el *{deadline}* para retirarlo

📍 Sucursal Andreani — {address}

🕐 {hours}

🔢 Seguimiento: {tracking number}

✅ Llevá tu DNI y mostrá este QR 👇
```

## Privacy

Never include the user's DNI in the caption. The email mentions "Tu DNI" as a requirement but does not contain the actual number.

## Output

Use the tracking number as input to `generate_qr.py` and the caption as `--caption` for `send_whatsapp.py`.
