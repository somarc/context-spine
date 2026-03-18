# ADR 0007: Native Memory APIs Without Runtime Orchestration

## Status

Accepted

## Context

ADR 0005 establishes that Context Spine must not become a control plane.
ADR 0006 proposes that Context Spine should evolve toward native-quality memory APIs for capture, query, promotion, invalidation, and reconciliation.

That direction is useful, but it still needs a sharper boundary.

PI-backed systems such as SLICC demonstrate why.
They are strong at live session continuity, automatic capture, worker delegation, and runtime-local memory.
They also show the failure mode Context Spine must avoid:

- project understanding drifts into runtime state instead of inspectable repo files
- orchestration concerns start to dominate memory concerns
- mutable prompt state and background runtime state become harder to audit than code, docs, and evidence

Context Spine should borrow native-memory discipline from systems like that without inheriting their runtime-platform responsibilities.

## Decision

Context Spine may implement native-style local memory APIs, but only as memory services.

The allowed core API families are:

- `capture`
  - record commands, tests, git state, diffs, tool events, generated artifacts, and other provenance into structured memory records
- `query`
  - rank and return memory across session, project, generated, and machine-capture layers with source references and uncertainty
- `promote`
  - turn working knowledge into durable project truth such as baselines, ADRs, runbooks, or evidence packs
- `invalidate`
  - mark assumptions, records, or summaries as stale, superseded, or contradicted
- `reconcile`
  - compare memory surfaces against code, docs, tests, and evidence and report drift explicitly

These APIs must obey the following rules.

### 1. Project Truth Stays File-Backed

Authoritative project understanding must continue to resolve to inspectable repo surfaces:

- `meta/context-spine/`
- `docs/adr/`
- `docs/runbooks/`
- `.agent/diagrams/`
- curated evidence packs and other durable note surfaces

Structured records and generated aids may support those surfaces, but they do not replace them.

### 2. The Core Must Remain Request/Response, Not Runtime-Owned

Context Spine may expose local commands, scripts, JSON outputs, and thin library APIs.
It must not require an always-on daemon, message bus, scheduler, or runtime supervisor for normal operation.

If a feature needs a resident orchestrator to make sense, it does not belong in the core memory system.

### 3. Automatic Capture Must Be Bounded And Inspectable

Automatic capture is allowed when it is tied to explicit commands, wrappers, editor hooks, or other inspectable entrypoints.

Automatic capture must write to inspectable records with provenance.
It must not silently rewrite durable truth surfaces or depend on hidden mutable state as the only source of memory.

### 4. Queries Must Retrieve Memory, Not Dispatch Work

`query` may rank, summarize, filter, correlate, and explain memory.
It may return source references, evidence, and uncertainty.

`query` may use QMD or other supported retrieval backends underneath.
Those backends remain supporting surfaces, not the definition of the memory contract and not a justification for runtime orchestration.

`query` must not:

- create or schedule workers
- route prompts
- trigger delegated execution
- own long-running agent coordination

Those are runtime concerns, not memory concerns.

### 5. Promotion And Invalidation Must Be Explicit

`promote` and `invalidate` must leave durable traces:

- updated files
- machine-readable records
- explicit supersession or invalidation events

They must not exist only as mutable in-memory prompt state.

### 6. Runtime Integrations Stay In Adapters

Agent runtimes may consume Context Spine through `.pi/`, `scripts/delegation/`, or external integrations.

Those adapters may:

- call capture and query APIs
- package evidence for delegated work
- rehydrate context for external runtimes

They must not redefine Context Spine itself as an agent orchestrator.

### 7. Layer Boundaries Stay Explicit

The system must keep session memory, project memory, and broader operator or organizational overlays separate.

A live session view is allowed.
A hidden mutable global prompt memory as the authoritative project store is not.

## Explicitly Out Of Scope

This ADR does not authorize Context Spine to add:

- cone and scoop style worker orchestration
- task queues, cron ownership, or webhook routing
- background daemons required for normal use
- runtime-owned global prompt memory as the authoritative store
- runtime-specific tool routing or sandbox policy engines
- autonomous delegation frameworks inside the core memory package

Those concerns may exist in external runtimes that use Context Spine, but not in Context Spine core.

## Consequences

- Context Spine can grow first-class memory APIs without becoming a runtime platform
- the repo keeps inspectable project truth while gaining stronger structured capture
- automatic capture becomes easier to justify because its storage contract stays explicit
- supported retrieval surfaces such as QMD can remain bundled without becoming the definition of the system
- PI-backed runtimes can use Context Spine as a memory substrate, but Context Spine does not need to imitate their orchestration model
- future proposals should be rejected if they add runtime coordination without materially improving truth, evidence, or drift resistance
