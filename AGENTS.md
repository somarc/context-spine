# Context Spine Agent Constitution

This repository is a boilerplate intelligence layer for future projects.

## This Repo First

- run `npm run context:init` on first setup to register repo-local QMD collections
- run `npm run context:bootstrap` before broad repo-wide searching
- open `meta/context-spine/spine-notes-context-spine.md` first for the current baseline
- create a session note for meaningful work with `npm run context:session`
- use `npm run context:verify` when you want one captured verification run instead of ad hoc test and maintenance scrollback
- use `npm run context:event -- --type ... --summary ...` only for high-signal boundaries, not as a general activity log
- run `npm run context:state` when you need a compact machine summary or a visual view of current memory layers
- run `npm run context:query` when you need a JSON runtime view of active objective, working set, and recent evidence
- run `npm run context:rehydrate` when you need the smaller restart packet for an external runtime or agent
- run `npm run context:promote` after you update durable files and want the promotion recorded as a record plus event
- run `npm run context:invalidate` after you mark an assumption or surface stale and want that invalidation recorded explicitly
- if retrieval is newly initialized and results are sparse, run `npm run context:update` and then `npm run context:embed`
- if you change `.pi/skills/`, run `npm run context:skill:install`

## Mission

- bootstrap working memory quickly
- keep code, docs, and evidence in sync
- make project understanding durable and retrievable
- support extensible local agent workflows without turning the repo into prompt soup

When evolving Context Spine itself, preserve the design compass in `docs/adr/0005-context-spine-design-compass.md`.

## Core Roles

- `Codex` is the primary orchestrator for implementation, verification, and final acceptance.
- delegated agents are bounded workers for retrieval, summarization, note drafting, and secondary review
- durable notes are not substitutes for code or tests; they are the synthesis layer

## Truth Model

- code captures delivered behavior
- docs capture intended behavior
- tests and command evidence capture what is actually trusted

When these disagree, reconcile them explicitly. Do not treat them as interchangeable.

## Context Spine Loop

### Read loop

- bootstrap recent memory
- run retrieval preflight
- open only high-signal artifacts
- re-anchor in live code and tests

### Write loop

- start from code, tests, logs, or commands
- synthesize the result into a durable note or evidence pack
- link it into the project graph
- refresh retrieval

## Required Surfaces

- `meta/context-spine/` for repo-local memory
- `scripts/context-spine/` for bootstrap and retrieval helpers
- `docs/adr/` for architecture decisions
- `docs/runbooks/` for repeatable operations
- `.agent/diagrams/` for visual explainers
- external durable notes for long-horizon project understanding

## Durable Note Rules

Recommended file pattern:

- `spine-notes-<topic>.md`

Required sections:

- `Summary`
- `Current State`
- `Decisions`
- `Open Questions`
- `Sources`

Prefer explicit `as_of` timestamps and `source_of_truth` fields in frontmatter.

## Visual Explainers

For complex systems, plans, audits, or retrieved context that is easier to understand visually:

- create or update a self-contained explainer under `.agent/diagrams/`
- pair it with a durable note or evidence source
- treat the explainer as a reading surface, not just presentation polish
- when explainers accumulate over time, curate them under `meta/visual-corpus/`
  as normalized captures plus generated index, compare, or trend views instead
  of letting them stay disjointed one-shot pages

If a user prefers to read context visually, the explainer path should be part of the normal workflow.

## Delegation Rules

Delegate only bounded work:

- retrieval and triage
- secondary review
- note drafting
- task curation
- evidence packaging

Keep implementation-critical edits under primary-agent review.

Delegated output should prefer this contract:

- `FILE_WRITTEN:`
- `DECISION:`
- `EVIDENCE:`
- `FILES:`
- `NEXT_ACTIONS:`

## Freshness Discipline

When retrieval quality matters:

- run `npm run context:update`
- run `npm run context:embed` when new documents need embeddings

When memory freshness matters:

- regenerate hot memory
- create a fresh session note if the latest summary is stale

## Retention Discipline

- keep architecture, boundaries, baseline notes, ADRs, and runbooks durable
- keep normalized visual-corpus manifests and catalogs durable when they become
  part of the reading path
- treat sessions and observations as rolling working memory, not permanent literature
- treat events as sparse machine-facing provenance for meaningful work boundaries, not a tail of everything the agent did
- roll stable conclusions into durable notes or evidence packs
- keep generated retrieval artifacts and generated corpus pages local and
  regenerable

## Extensibility Rules

- add new agent adapters under `.pi/` or `scripts/delegation/`
- add project-specific retrieval or oracle integrations as adapters, not hard dependencies
- prefer small scripts and explicit contracts over large prompt-only systems
- keep native memory APIs request/response only; do not turn Context Spine into a resident control plane
- do not hardcode personal paths or secrets into reusable tooling
- prefer composing skills over expanding one skill into a fake all-in-one oracle
- when a skill has a natural companion, say so explicitly inside the skill contract
- example: `elon-doctrine` should consider `principal-engineer-review` for system-shape questions, and `principal-engineer-review` should consider `elon-doctrine` for worthiness questions
- do not let new memory features violate the design compass invariants or push the repo toward its anti-goals

## Safety

- never store secrets in repo-local memory
- treat logs and evidence packs as potentially sensitive
- keep external system assumptions configurable through environment variables
