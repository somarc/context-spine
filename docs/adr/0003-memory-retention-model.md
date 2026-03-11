# ADR 0003: Memory Retention Model

## Status

Accepted

## Context

Context Spine is valuable only if it keeps the project legible without burying the code in an unbounded archive of session narration.

The repository needs to preserve:

- architecture
- explicit system shape and boundaries
- current operating assumptions
- trusted evidence behind important decisions

The repository does not need to preserve every step of how the team arrived there.

## Decision

Split Context Spine artifacts into three classes:

### 1. Durable

Keep these in git as the long-lived shared project map:

- `docs/adr/`
- `docs/runbooks/`
- `meta/context-spine/spine-notes-*.md`
- curated `meta/context-spine/evidence-packs/`
- selected `.agent/diagrams/`

These should capture architecture, boundaries, contracts, invariants, and current operating shape.

### 2. Rolling

Keep these in git only while they remain useful for active continuity:

- `meta/context-spine/sessions/`
- `meta/context-spine/observations/`

These are short-horizon working memory. They should be periodically rolled up into durable notes, ADRs, runbooks, or curated evidence.

### 3. Generated / Local

Do not treat these as durable repo history:

- `meta/context-spine/.qmd/`
- `meta/context-spine/hot-memory-index.md`
- `meta/context-spine/memory-scorecard.md`

These are local retrieval or health artifacts and can be regenerated.

## Consequences

- the repo stays focused on current shared understanding instead of historical exhaust
- architecture and boundaries remain easy to find
- session and observation churn does not become permanent literature by default
- retrieval and score artifacts can be regenerated locally without polluting repo history
- teams must periodically condense rolling memory into durable structure
