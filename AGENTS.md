# Context Spine Agent Constitution

This repository is a boilerplate intelligence layer for future projects.

## This Repo First

- run `npm run context:init` on first setup to register repo-local QMD collections
- run `npm run context:bootstrap` before broad repo-wide searching
- open `meta/context-spine/spine-notes-context-spine.md` first for the current baseline
- create a session note for meaningful work with `npm run context:session`
- if retrieval is newly initialized and results are sparse, run `npm run context:update` and then `npm run context:embed`

## Mission

- bootstrap working memory quickly
- keep code, docs, and evidence in sync
- make project understanding durable and retrievable
- support extensible local agent workflows without turning the repo into prompt soup

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

## Extensibility Rules

- add new agent adapters under `.pi/` or `scripts/delegation/`
- add project-specific retrieval or oracle integrations as adapters, not hard dependencies
- prefer small scripts and explicit contracts over large prompt-only systems
- do not hardcode personal paths or secrets into reusable tooling

## Safety

- never store secrets in repo-local memory
- treat logs and evidence packs as potentially sensitive
- keep external system assumptions configurable through environment variables
