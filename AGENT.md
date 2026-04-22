# retiralo — plugin source

This repo is a **Claude Code plugin** and its own single-plugin
**marketplace**. End users install it via the commands in `README.md`.
This file is for contributors and maintainers.

## Layout

```
.claude-plugin/
  plugin.json                  # plugin manifest
  marketplace.json             # marketplace manifest (makes this repo installable)
agents/retiralo.md             # subagent — pipeline, error handling, redaction
skills/
  setup/SKILL.md               # first-run setup (toolchain, AgentMail, Kapso, .env)
  inbox-poll/SKILL.md
  extract-tracking/SKILL.md
  generate-qr/SKILL.md
  send-whatsapp/SKILL.md
scripts/                       # Python entrypoints used by skills
pyproject.toml                 # poetry project
```

- Marketplace name: `retiralo-marketplace` (declared in `marketplace.json`).
- Plugin name: `retiralo` (declared in `plugin.json`), `source: "./"`.
- Runtime behavior (pipeline, error handling, PII redaction) lives in
  `agents/retiralo.md`.
- All plugin-internal paths resolve against `${CLAUDE_PLUGIN_ROOT}`.
  Scripts run from the plugin root so poetry finds `pyproject.toml`:
  ```sh
  cd ${CLAUDE_PLUGIN_ROOT} && poetry run scripts/<name>.py ...
  ```

## Local dev loop

Install from your local clone (works the same on any machine that has
the repo cloned — laptop, remote host over SSH, doesn't matter):

```
/plugin marketplace add /absolute/path/to/your/clone
/plugin install retiralo@retiralo-marketplace
```

Claude Code reads the files live, so edits propagate without
reinstalling. What each kind of edit needs:

| Edit                               | What to run                                       |
| ---------------------------------- | ------------------------------------------------- |
| `agents/retiralo.md` prompt        | nothing — re-read per invocation                  |
| Skill or script content            | `/plugin reload retiralo`                         |
| New agent / skill file             | `/plugin reload retiralo`                         |
| `plugin.json` / `marketplace.json` | `/plugin marketplace update retiralo-marketplace` |

If state gets weird: `/plugin uninstall retiralo@retiralo-marketplace`
and `/plugin marketplace remove retiralo-marketplace`, then reinstall.

**Two-session workflow** is practical: one session inside the repo for
editing, another session anywhere else with the plugin installed for
testing. Edits in session A are visible to session B after a reload.

## Publishing

Push the repo to `teosibileau/retiralo` on GitHub. End users then follow
`README.md`:

```
/plugin marketplace add teosibileau/retiralo
/plugin install retiralo@retiralo-marketplace
```

Adding a second plugin later means appending to the `plugins` array in
`.claude-plugin/marketplace.json` — no structural change.

## What's intentionally absent

- No hooks (SessionStart, PreToolUse, etc.) — the agent runs on demand.
- No slash commands — the agent is the entry point.
