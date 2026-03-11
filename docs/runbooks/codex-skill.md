# Codex Skills Runbook

## Goal

Treat repo-local skills as maintained Codex skills, not just repo conventions.

This runbook is optional and only matters if your team wants the bundled workflows available inside Codex. The project itself should remain usable without them.

## Source Of Truth

- repo source: `.pi/skills/`
- installed target: `${CODEX_HOME:-$HOME/.codex}/skills/`

## Commands

- validate the sources: `npm run context:skill:validate`
- install or sync the skills: `npm run context:skill:install`

Direct shell equivalent:

```bash
bash ./scripts/context-spine/install-codex-skill.sh
```

## When To Run It

- after changing any file under `.pi/skills/`
- after cloning the repo onto a new machine
- before relying on a bundled skill in Codex

## Verification

After installation:

1. confirm the target folders exist under `$CODEX_HOME/skills/`
2. run the bundled inspector if needed: `python3 ~/.codex/skills/context-spine/scripts/inspect_repo.py --root <repo>`
3. invoke the skill explicitly with `$context-spine` or `$principal-engineer-review` in Codex when testing
