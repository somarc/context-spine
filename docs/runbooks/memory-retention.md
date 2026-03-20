# Memory Retention

## Goal

Keep the project map durable without letting working-memory exhaust take over the repository.

## The Rule

Context Spine stores three kinds of things:

1. durable structure
2. rolling working memory
3. generated local artifacts

Treat them differently.

Git tracking is a repo policy choice, not a hidden default.
Keep that choice explicit in `meta/context-spine/context-spine.json` and apply it through the managed `.gitignore` block.

- `tracked` mode
  Commit durable and rolling Context Spine memory.
- `local` mode
  Keep `meta/context-spine/` out of git and promote anything that matters into committed docs, ADRs, runbooks, or other durable project surfaces.

## Durable Structure

In `tracked` mode, keep these committed as the long-lived shared understanding of the project:

- `docs/adr/`
- `docs/runbooks/`
- `meta/context-spine/spine-notes-*.md`
- curated `meta/context-spine/evidence-packs/`
- selected `meta/visual-corpus/captures/` and `meta/visual-corpus/catalogs/`
- selected `.agent/diagrams/`

This is where architecture, boundaries, contracts, invariants, and operating shape belong.

## Rolling Working Memory

In `tracked` mode, keep these while they are still useful for active continuity:

- `meta/context-spine/sessions/`
- `meta/context-spine/observations/`

These are not the permanent archive of the project. They are the active trail of recent work.

When they stop being useful, do one of these:

- roll the important parts into a baseline note
- promote a stable decision into an ADR or runbook
- extract the trusted result into a curated evidence pack
- archive externally if the history matters but should not live in the repo
- delete the low-signal residue

## Generated / Local Artifacts

Treat these as local and regenerable:

- `meta/context-spine/.qmd/`
- `meta/context-spine/hot-memory-index.md`
- `meta/context-spine/memory-scorecard.md`
- `meta/visual-corpus/generated/`

They support retrieval and maintenance, but they are not durable project memory.

In `local` mode, the whole `meta/context-spine/` tree is local by policy.

## Review Cadence

Use this lightweight cadence:

### Per session

- update the current session note
- add an observation only if something non-trivial was learned

### Weekly

- check whether the baseline note still reflects the current architecture and boundaries
- roll repeated findings out of sessions into durable notes or runbooks

### Periodically

- prune or archive stale sessions and observations
- keep only the recent working trail in the repo

## Good Pressure Test

If a future teammate needs to understand the system, they should be able to do it from:

1. the baseline `spine-notes-*.md`
2. ADRs and runbooks
3. a small number of curated evidence packs and diagrams

They should not need to read months of session narration.

## Sources

- `docs/adr/0003-memory-retention-model.md`
- `meta/context-spine/README.md`
- `docs/runbooks/how-to-use-context-spine.md`
