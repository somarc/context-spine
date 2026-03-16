# Codex Skills Runbook

## Goal

Treat repo-local skills as maintained Codex skills, not just repo conventions.

This runbook is optional and only matters if your team wants the bundled workflows available inside Codex. The project itself should remain usable without them.

## Source Of Truth

- repo source: `.pi/skills/`
- installed target: `${CODEX_HOME:-$HOME/.codex}/skills/`

## Bundled Skills

- `context-spine`
  - bootstrap, repair, and working-memory recovery
- `principal-engineer-review`
  - structural review and durable-decision pressure
- `context-spine-maintenance`
  - run the maintenance loop and prioritize what to fix first
- `memory-promotion`
  - decide what rolling work should become durable memory
- `multi-repo-rollout`
  - assess or safely evolve Context Spine across several local repos
- `elon-doctrine`
  - judge whether a change improves real value, legibility, and inference quality

## Commands

- validate the sources: `npm run context:skill:validate`
- install or sync the skills: `npm run context:skill:install`
- assess several local repos: `npm run context:rollout -- --repos /path/to/repo-a /path/to/repo-b`

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
3. invoke the relevant skill explicitly in Codex when testing, for example:
   - `$context-spine`
   - `$principal-engineer-review`
   - `$context-spine-maintenance`
   - `$memory-promotion`
   - `$multi-repo-rollout`
   - `$elon-doctrine`
