# Codex Skills Runbook

## Goal

Treat repo-local skills as maintained Codex skills, not just repo conventions.
Keep the spine lean: it should behave like the thinnest possible operating layer for current truth, not like a note-accumulation ceremony.

This runbook is optional and only matters if your team wants the bundled workflows available inside Codex. The project itself should remain usable without them.

## Source Of Truth

- repo source: `.pi/skills/` by default, or the repo-local
  `collections.skills_root` configured in `meta/context-spine/context-spine.json`
- installed target: `${CODEX_HOME:-$HOME/.codex}/skills/`

## Bundled Skills

- `context-spine`
  - recover current project truth, hydrate from deep evidence, invalidate stale assumptions, and tighten retrieval
- `principal-engineer-review`
  - structural review and durable-decision pressure
- `context-spine-maintenance`
  - audit hygiene, flow, and alignment drift in repo-local memory
- `memory-promotion`
  - decide what rolling work, invalidations, and reasoning repairs should become durable memory
- `visual-corpus-curator`
  - turn repeated visual reporting into immutable captures, catalogs, compare pages, and trend views
- `multi-repo-rollout`
  - assess or safely evolve Context Spine across several local repos
- `elon-doctrine`
  - judge whether a change improves real value, legibility, and inference quality

## Commands

- validate the sources: `npm run context:skill:validate`
- install or sync the skills: `npm run context:skill:install`
- verify installed copies match repo source digests: `npm run context:skill:verify-installed`
- assess several local repos: `npm run context:rollout -- --repos /path/to/repo-a /path/to/repo-b`

Direct shell equivalent:

```bash
bash ./scripts/context-spine/install-codex-skill.sh
```

## When To Run It

- after changing any file under `.pi/skills/`
- after changing the configured local skill source path if the repo intentionally
  uses something other than `.pi/skills/`
- after cloning the repo onto a new machine
- before relying on a bundled skill in Codex
- when the spine feels dry, blocked, bloated, or overly inferential under delivery pressure

## Verification

After installation:

1. confirm the target folders exist under `$CODEX_HOME/skills/`
2. verify the runtime from the target repo itself, not from the installed skill copy:
   - `npm run context:config`
   - `npm run context:bootstrap`
   - `npm run context:doctor`
3. invoke the relevant skill explicitly in Codex when testing, for example:
   - `$context-spine`
   - `$principal-engineer-review`
   - `$context-spine-maintenance`
   - `$memory-promotion`
   - `$visual-corpus-curator`
   - `$multi-repo-rollout`
   - `$elon-doctrine`
