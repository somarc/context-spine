# Codex Skill Runbook

## Goal

Treat `context-spine` as a maintained Codex skill, not just a repo convention.

This runbook is optional and only matters if your team wants the workflow available as `$context-spine` inside Codex. The project itself should remain usable without it.

## Source Of Truth

- repo source: `.pi/skills/context-spine/`
- installed target: `${CODEX_HOME:-$HOME/.codex}/skills/context-spine`

## Commands

- validate the source: `npm run context:skill:validate`
- install or sync the skill: `npm run context:skill:install`

Direct shell equivalent:

```bash
bash ./scripts/context-spine/install-codex-skill.sh
```

## When To Run It

- after changing any file under `.pi/skills/context-spine/`
- after cloning the repo onto a new machine
- before relying on `$context-spine` in Codex

## Verification

After installation:

1. confirm the target folder exists under `$CODEX_HOME/skills/context-spine`
2. run the bundled inspector if needed: `python3 ~/.codex/skills/context-spine/scripts/inspect_repo.py --root <repo>`
3. invoke the skill explicitly with `$context-spine` in Codex when testing
