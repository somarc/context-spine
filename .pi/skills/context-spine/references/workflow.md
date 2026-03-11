# Context Spine Workflow

## Modes

### Existing Context Spine repo

Use this mode when the repo already contains `meta/context-spine/` and `scripts/context-spine/`.

Preferred command order:

1. `npm run context:init`
2. `npm run context:update`
3. `npm run context:embed`
4. `npm run context:bootstrap`
5. `npm run context:session` if the latest session is missing or stale
6. `npm run context:score` after structural changes

Fallbacks when no `package.json` wrapper exists:

- `bash ./scripts/context-spine/init-qmd.sh`
- `bash ./scripts/context-spine/qmd-refresh.sh`
- `bash ./scripts/context-spine/qmd-refresh.sh --embed`
- `bash ./scripts/context-spine/bootstrap.sh`
- `python3 ./scripts/context-spine/mem-session.py --project <project-name>`
- `python3 ./scripts/context-spine/mem-score.py --root ./meta/context-spine`

High-signal reading order:

1. `meta/context-spine/spine-notes-*.md`
2. `meta/context-spine/sessions/*-session.md`
3. `meta/context-spine/hot-memory-index.md`
4. `docs/runbooks/session-start.md`
5. recent files under `.agent/diagrams/`

### Partial repo

Use this mode when only some surfaces exist.

Fix order:

1. re-establish the required surfaces
2. resolve path or wrapper ambiguity
3. add a baseline `spine-notes-*.md`
4. align docs with the real commands
5. refresh QMD and rerun bootstrap

### New install / drop-in

Use this mode when the repo has no Context Spine surfaces yet.

Install order:

1. add `meta/context-spine/`
2. add `scripts/context-spine/`
3. add `docs/adr/`, `docs/runbooks/`, and `.agent/diagrams/`
4. wire repo-local command wrappers
5. create one baseline note and one session template path
6. initialize retrieval

## Truth Discipline

- code is delivered behavior
- docs are intended behavior
- tests and command evidence are trusted behavior

When they disagree, reconcile the mismatch explicitly.

## Change Discipline

- Prefer small script and docs changes over large prompt-only rules.
- If you add a wrapper command, update the docs in the same change.
- If you add or change notes/runbooks, refresh retrieval before closing the task.
- If you install or modify the Codex skill, validate the source and installed copies.
