# retiralo — plugin source

This repo is a **Claude Code plugin**. It bundles a subagent
(`retiralo`), four task skills, a first-run setup skill, and the Python
scripts the skills invoke. Users install the plugin once and then
trigger the agent with "run retiralo" or "check for pickups".

Runtime behavior (pipeline, error handling, PII redaction) lives in
`agents/retiralo.md`. This file is for maintainers.

## Layout

```
.claude-plugin/
  plugin.json                  # plugin manifest (name, version, description, author)
  marketplace.json             # marketplace manifest — makes this repo installable
agents/retiralo.md             # subagent — pipeline, error handling, redaction
skills/
  setup/SKILL.md               # first-run setup (toolchain, AgentMail, Kapso, .env)
  inbox-poll/SKILL.md          # find unread / show body / mark read
  extract-tracking/SKILL.md    # tracking number + caption (agent does this directly)
  generate-qr/SKILL.md         # Andreani QR PNG from tracking number
  send-whatsapp/SKILL.md       # upload + send image via Kapso
scripts/                       # Python entrypoints used by skills
pyproject.toml                 # poetry project
```

The repo is **both** a plugin and its own single-plugin marketplace. The
marketplace is named `retiralo-marketplace`; the plugin inside it is
`retiralo` with `"source": "./"`.

All plugin-internal paths resolve against `${CLAUDE_PLUGIN_ROOT}`. Every
script invocation must run from the plugin root so poetry picks up
`pyproject.toml`:

```sh
cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/<name>.py ...
```

## Testing locally

Install from your working copy as a marketplace, then install the plugin
from it. Substitute the absolute path to your local clone:

```
/plugin marketplace add /absolute/path/to/retiralo
/plugin install retiralo@retiralo-marketplace
```

Claude Code treats the marketplace path as live, so edits are picked up
without reinstalling.

Verify:

- `/agents` lists `retiralo` (source: `plugin:retiralo`).
- Say "run retiralo". With no `.env`, the agent should invoke the setup
  skill. With `.env` present, it should run the pipeline.

Iteration loop:

- **Agent prompt** edits (`agents/retiralo.md`) — re-read on every
  invocation, no reload needed.
- **Skill / script** edits — run `/plugin reload retiralo`.
- **New agent / skill files** — run `/plugin reload retiralo` (or
  `/agents` for the agent-specific rescan).
- **`.claude-plugin/plugin.json` or `marketplace.json`** changes —
  run `/plugin marketplace update retiralo-marketplace`.
- **Python script** edits — take effect on the next subprocess call.

If cached state gets weird: `/plugin uninstall retiralo@retiralo-marketplace`,
`/plugin marketplace remove retiralo-marketplace`, then reinstall.

## Testing over SSH on another machine

Fastest feedback loop is a local-path install on the remote:

```sh
# on the remote host
git clone git@github.com:teosibileau/retiralo.git ~/retiralo
# inside Claude Code on that host
/plugin marketplace add ~/retiralo
/plugin install retiralo@retiralo-marketplace
```

Then iterate by pushing from your laptop and, on the remote:

```sh
cd ~/retiralo && git pull
# inside Claude Code
/plugin reload retiralo
# if plugin.json / marketplace.json changed:
/plugin marketplace update retiralo-marketplace
```

Alternative install source (for end users, not dev):

```
/plugin marketplace add teosibileau/retiralo
/plugin install retiralo@retiralo-marketplace
```

The local-path flow is recommended for development because `git pull`
plus `/plugin reload` is faster than resolving the remote each time.

## Distributing

Push the repo to `teosibileau/retiralo` on GitHub. End users install with:

```
/plugin marketplace add teosibileau/retiralo
/plugin install retiralo@retiralo-marketplace
```

Adding a second plugin later is a matter of appending to the `plugins`
array in `.claude-plugin/marketplace.json` — no structural change.

## What's intentionally absent

- No hooks (SessionStart, PreToolUse, etc.) — the agent runs on demand.
- No commands (slash commands) — the agent is the entry point.
