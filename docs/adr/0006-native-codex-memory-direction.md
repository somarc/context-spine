# ADR 0006: Native-Quality Codex Memory Direction

## Status

Proposed

## Context

Context Spine is already strong at one thing:

- making project memory explicit
- keeping it inspectable in normal repo files
- tying understanding back to code, docs, tests, and evidence

That makes it a good prototype for what a native Codex memory surface should believe.

It is not yet the shape a native memory surface should take.

Today, Context Spine is still:

- too manual in normal use
- too dependent on file conventions and wrapper scripts
- mostly scoped to one repo at a time
- lighter on structured schemas than a native system should be

If it is to become universally useful for Codex as a memory surface, it needs a clearer target architecture that improves utility without violating the design compass.

## Decision

Use the following architecture direction when evolving Context Spine toward a more native-quality Codex memory surface.

### 1. Make Visual Explanation The Primary Human Interface

If native memory is primarily for Codex, the human-facing requirement is not raw memory inspection.

The primary human contract should be:

- visual explanation
- visible evidence trails
- clear source-of-truth references
- understandable state transitions

Humans should not need to read internal memory records unless they want to.
The system should be able to render trustworthy visual explanations of:

- what it knows
- why it believes it
- what changed
- what is still uncertain

### 2. Keep File-Level Inspectability For Project Truth

Project memory must remain legible without a special runtime.

The durable truth layer should stay file-native:

- baseline notes
- ADRs
- runbooks
- curated evidence packs
- visual explainers

Native memory should not replace those project-truth files with hidden state.
It should index, interpret, and accelerate them.

The internal memory substrate may be more native, structured, or runtime-backed than the current repo file model as long as project truth still resolves back to inspectable source surfaces when needed.

### 2.5 Treat Retrieval Backends As Adapters, Not As The Memory Contract

Native memory for Codex should not be defined by any single retrieval backend.

QMD, BM25 indexes, vector stores, and embedding pipelines are supported accelerators for:

- cold-start discovery
- cross-repo lookup
- broad corpus sweep
- human search ergonomics

They are not the primary contract the agent should depend on.

When code, docs, tests, git state, and command evidence are already local and bounded, the agent should prefer those direct surfaces over mediated retrieval.

This means the system should remain meaningfully usable when retrieval is only partially hydrated:

- lexical retrieval working without vectors is degraded, not dead
- agent memory quality should not collapse because one embedding path is unavailable
- the durable reading path should still resolve through bootstrap, working-set files, and source-of-truth references

Retrieval engines should be replaceable implementation details around the memory layer, not the identity of the memory layer itself. QMD remains a supported retrieval surface within that boundary; it is not deprecated by this decision.

### 3. Add Explicit Layered Memory

Native-quality memory needs more than one layer.

Context Spine should conceptually separate:

1. **Session memory**
   - short-horizon working state for the current task, branch, commands, and open questions
2. **Project memory**
   - durable repo-local understanding: baselines, ADRs, runbooks, evidence, diagrams
3. **Operator or organizational memory**
   - reusable patterns, shared context, cross-repo heuristics, and external durable notes

The layers should be portable and queryable independently.
Project memory should remain repo-local by default.
Broader layers should attach through adapters, not by contaminating the repo core.

### 4. Shift From Manual Note Upkeep Toward Automatic Capture

To become universally useful, Context Spine must reduce normal-use ceremony.

Native memory should automatically capture high-value signals from:

- git state and diffs
- tests and verification commands
- command execution
- tool events
- generated reports
- explicit promotion decisions

The point is not to store every event forever.
The point is to reduce the manual burden of preserving evidence and short-horizon continuity.

Automatic capture should feed structured evidence and session layers, not silently rewrite durable truth.

### 5. Add First-Class APIs Alongside File Conventions

Context Spine currently works mainly through repo files and CLI wrappers.

A native-quality memory surface should also expose first-class APIs and runtime hooks for:

- capture
- query
- promotion
- invalidation
- reconciliation

The file layer remains legible project truth.
The API layer makes the system easier to integrate with Codex, tools, IDEs, CI, and agent runtimes.

### 6. Use Stronger Structured Schemas Alongside Markdown

Markdown remains valuable because humans can read it directly.

But a native-quality system should pair markdown with stronger structured schemas for:

- session snapshots
- evidence records
- source-of-truth references
- generated artifact records
- promotion events
- invalidation or supersession events
- memory-layer references

Markdown should remain one important human reading surface, but not the only one.
Structured records should make retrieval, promotion, automation, and visual explanation more reliable.

### 7. Default To Less Ceremony In Normal Use

Context Spine should be more useful by removing upkeep, not by demanding more rituals.

The universal path should feel like:

- open repo
- Codex sees the layered memory and current session state
- recent evidence and git/test/tool history are already available
- project truth surfaces are clearly ranked
- promotion into durable memory happens deliberately, not by accident

The user should not need to remember a maintenance ritual before every useful session.

### 8. Keep Domain Knowledge In Overlays, Not In Core Memory

Context Spine should stay generic at the core.

That means:

- AEM
- EDS
- Cloud Manager
- DA
- AEP

should come in as overlays, skills, schemas, or retrieval adapters.

The core memory model should remain universal:

- resume work
- understand the project
- reconcile truth
- preserve evidence
- promote what matters

## Proposed Native Memory Shape

The target shape is a dual-surface system:

### Human surfaces

- markdown baselines
- ADRs
- runbooks
- evidence packs
- visual explainers
- curated generated aids

Visual explainers should become the preferred human-facing output when the memory state, architecture, or decision flow is easier to understand spatially than through prose.

### Machine surfaces

- session state records
- evidence records
- promotion records
- artifact records
- source reference index
- queryable memory-layer metadata

The machine surfaces should support the human surfaces, not replace them.

## Human Contract

If this direction succeeds, the user should not have to care whether the internal memory lives in:

- files
- indexes
- APIs
- embeddings
- runtime state

The user should reliably get:

- a visual explanation of what matters
- evidence-backed reasoning
- clear uncertainty
- source-of-truth links when needed

The user should also not need to care whether retrieval happens through:

- QMD
- lexical search
- vector search
- a future query API

Those are internal accelerators. The human-facing requirement is that the system explains itself visually and truthfully.

## Minimal API Families

If Context Spine evolves in this direction, the smallest useful API families would be:

- `capture`
  - record commands, tests, diffs, and tool events with provenance
- `query`
  - retrieve ranked memory across session, project, and broader layers
- `promote`
  - move working knowledge into durable project memory with evidence links
- `invalidate`
  - mark stale assumptions or superseded memory explicitly
- `reconcile`
  - compare current code/docs/evidence against memory surfaces and surface drift

These APIs could be implemented locally first through lightweight JSON records and thin wrappers before any larger runtime exists.

## Phased Direction

### Phase 1: Better Local Memory Discipline

Improve the current repo-local system without adding a runtime:

- add stronger schemas for evidence and promotion records
- auto-capture more signal from existing wrappers
- reduce manual upkeep in ordinary workflows
- keep generated aids safe and explicit

### Phase 2: First-Class Local Memory APIs

Add native-style interfaces while preserving file inspectability:

- local query and capture APIs
- structured memory exports
- better ranking across session and project memory
- explicit invalidation and supersession records

### Phase 3: Layered Memory Beyond A Single Repo

Add broader usefulness without polluting the repo core:

- user-level memory overlays
- organizational memory adapters
- cross-repo linking
- portability of memory references across contexts

## Non-Goals

This direction does not justify turning Context Spine into:

- a daemon-first system
- a hidden memory service
- a transcript archive
- a control plane
- an all-in-one agent runtime

If a future change requires those moves, it should be treated as a separate system, not as a quiet expansion of Context Spine.

## Consequences

- Context Spine gets a clearer path toward universal Codex usefulness
- the repo can improve without abandoning inspectability or evidence discipline
- future work can be judged against a concrete architecture instead of a vague "native memory" aspiration
- the system stays universal by strengthening the core memory model rather than hardcoding one domain
- the user-facing contract becomes simpler: Codex can own the memory internals as long as it can explain itself visually and truthfully
