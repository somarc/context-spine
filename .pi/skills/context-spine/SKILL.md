---
name: context-spine
description: Bootstrap, install, and improve Context Spine for repo-local working memory and retrieval. Use when a user asks to recover project context, set up or repair `meta/context-spine` workflows, create baseline or session notes, harden bootstrap/QMD flows, or codify Context Spine itself as a reusable Codex skill.
---

# Context Spine

## Overview

Use this skill to make project understanding durable and retrievable instead of relying on raw recall. Prefer repo-local memory, QMD-first retrieval, and command-backed evidence over prompt-only context.

## First Pass

1. If the repo shape is unknown, run `python3 scripts/inspect_repo.py --root <repo>`.
1. Detect the operating mode: `existing`, `partial`, `missing`, or skill-maintenance.
1. Prefer repo-local wrappers over ad hoc shell when they exist.
1. Open only the top 1-3 high-signal artifacts first: a baseline `spine-notes-*.md`, the latest session, `hot-memory-index.md`, and the most relevant runbook.
1. Re-anchor any proposed change in code, tests, or command output. Do not treat code, docs, notes, and evidence as interchangeable.

## Modes

### Existing Context Spine repo

- Prefer `npm run context:init`, `context:update`, `context:embed`, `context:bootstrap`, `context:session`, and `context:score` when available.
- Fall back to direct `scripts/context-spine/*` entrypoints when wrappers do not exist.
- If retrieval is stale or newly initialized, refresh it before broad file search.
- If the baseline note is missing, create it before expanding the rest of the memory layer.

### Partial repo

- Restore missing surfaces first.
- Fix path ambiguity and wrapper drift before writing more notes or prompts.
- Add a baseline `spine-notes-*.md`, align docs with the real commands, then rerun bootstrap.

### Installing Context Spine

- Add the required surfaces listed in `references/adoption.md`.
- Keep memory repo-local under `meta/context-spine/`.
- Use small scripts and explicit contracts instead of prompt-only glue.
- Add a baseline note and one session path before declaring the install complete.

### Codex skill maintenance

- Treat `.pi/skills/context-spine/` as the repo source-of-truth when it exists.
- Install or sync it into `${CODEX_HOME:-$HOME/.codex}/skills/context-spine` with the repo install script when present.
- Validate the source and installed copies before closing the task.

## Output Expectations

- State the detected mode explicitly.
- Provide concrete file paths and commands, not generic advice.
- When you change the system, run the relevant bootstrap/update/validation commands and report the result.

## References

- `references/workflow.md`
- `references/adoption.md`
- `scripts/inspect_repo.py`
