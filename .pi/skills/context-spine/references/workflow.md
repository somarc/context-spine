# Context Spine Workflow

## Modes

### Active delivery

Use this mode when the user is trying to ship, unblock, or prove something now.

Working set:

1. active objective
1. authoritative surfaces
1. source hydration
1. critical path
1. stale or suspect assumptions
1. flow state
1. metacognitive check
1. next irreversible action

Command bias:

- refresh retrieval if it is stale enough to mislead search
- inspect runtime endpoints, git status, and the smallest relevant code surfaces first
- open only 1-3 durable artifacts before acting

After the implementation move:

- update the latest session or observation
- if durable truth changed, mark the old artifact superseded or route to `memory-promotion`
- note any dryness, blockage, or backflow that should become a durable repair

### Existing Context Spine repo

Use this mode when the repo already contains `meta/context-spine/` and `scripts/context-spine/`.

Preferred command order:

1. `npm run context:bootstrap`
2. `npm run context:session` if the latest session is missing or stale
3. `npm run context:update` when notes/docs changed or retrieval is stale enough to mislead search
4. `npm run context:embed` only when vector retrieval materially matters and the local runtime supports it
5. `npm run context:score` after structural changes

Use `npm run context:init` only for first install or collection repair.

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

Use this evidence ladder:

1. runtime behavior and command evidence
1. code and tests
1. docs and contracts
1. durable notes and runbooks
1. inference

When they disagree, reconcile the mismatch explicitly.

## Retrieval Discipline

- Direct evidence outranks retrieval. If the relevant code, tests, docs, or command output are already local and bounded, read them directly.
- Use QMD or other supported retrieval adapters for cold-start discovery, cross-repo sweep, broad corpus triage, or human lookup.
- Do not force an agent through a retrieval backend merely because one exists; the memory contract is the working set plus evidence, not the index technology.
- Treat lexical-only retrieval as a degraded-but-usable state. Missing vector hydration is a capability gap, not automatic failure of the memory layer.

## Invalidation Discipline

When new evidence contradicts durable memory:

1. record the contradiction in the latest session or observation
1. identify which durable artifact is now misleading
1. update it or mark it superseded explicitly
1. refresh retrieval so stale truth does not dominate search

Do not present contradictory truths as equally current.

## Topology Discipline

Always identify:

- primary repo
- nested repos
- planned repos
- deployed surfaces
- local endpoints

Do not let a single local checkout stand in for the whole system when the work is multi-surface.

## Flow Discipline

- Hydrate from deep sources before leaning on summaries.
- Keep the path from evidence to decision visible enough that another operator can follow it.
- Bound the working set so it carries signal, not undifferentiated history.
- If contradictions remain unresolved, present them as a blockage with the next step to clear it.
- If stale memory is dominating search or planning, mark it as backflow and repair the durable artifact.

## Cognition And Metacognition

For non-trivial tasks, make these loops visible:

1. perceive
1. orient
1. decide
1. act
1. reconcile

Before closing, ask:

- what did I know directly
- what did I infer
- what changed
- what would mislead the next operator
- what durable artifact now needs repair

## Change Discipline

- Prefer small script and docs changes over large prompt-only rules.
- If you add a wrapper command, update the docs in the same change.
- If you add or change notes/runbooks, refresh retrieval before closing the task.
- If you install or modify the Codex skill, validate the source and installed copies.
