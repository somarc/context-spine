# Spine Of Time

Use this reference when the project is under delivery pressure, when the user asks for the latest or current truth, when durable notes may be stale, or when multi-repo topology makes old assumptions suspect.

## Goal

Context Spine should preserve useful truth over time, not merely accumulate notes.
It should also keep truth moving: fresh evidence should hydrate the working set, and durable memory should not obstruct the current objective.

## Thin Operating Layer Principle

> Context Spine is not valuable because it stores more notes. It is valuable when it becomes the thinnest possible operating layer for current truth. If you keep it lean, evidence-based, and invalidation-aware, it is a very strong tool. If it drifts into ceremony, it dies.

Use this as the governing test for any new memory surface, workflow, or skill change.

## Evidence Ladder

Use this precedence order when sources disagree:

1. runtime behavior and command output
1. code and tests
1. docs, contracts, and ADRs
1. durable notes and runbooks
1. inference

Lower layers can explain higher layers, but they should not overrule fresher evidence without an explicit reason.

## Topology Ledger

Always identify which surfaces matter right now:

- primary repo
- nested repos
- planned or not-yet-created repos
- deployed endpoints
- local dev endpoints
- external sources the workflow depends on

Do not let a single checkout pretend to be the whole system when the real work spans multiple surfaces.

## Active-Delivery Working Set

When the user needs delivery rather than archaeology, produce a compact working set:

- active objective
- authoritative surfaces
- source hydration
- critical path
- blockers
- stale or suspect assumptions
- flow state
- metacognitive check
- next irreversible action

This working set is the spine for the current moment. It is intentionally smaller than the full memory layer.

## Flow Discipline

- Hydrate from deep sources first when they are available.
- Keep the flow explicit from evidence to working set to user-facing summary.
- If contradictions exist, label them as a blockage and resolve or bound them.
- If stale notes or outdated diagrams dominate retrieval, treat that as backflow and correct it.
- If the working set is bloated, compress harder before presenting conclusions.

## Invalidation Protocol

When new evidence contradicts durable memory:

1. record the contradiction in the latest session or observation
1. identify the durable artifact that is now misleading
1. update it or mark it superseded explicitly
1. refresh retrieval so the old truth stops dominating search results

Do not silently overwrite a stable note if the change matters historically. Preserve lineage, but make the current truth unmistakable.

## Freshness Rules

- Prefer dated evidence over relative phrasing.
- If a claim depends on a command, endpoint, or deployment check, record which command or URL established it.
- If confidence is reduced because evidence is old or indirect, say so explicitly.
- If a repo, endpoint, or workflow surface is only inferred, label it as unresolved rather than letting it harden into truth.
- If a conclusion depends on unsampled sources, record the dryness explicitly.

## Promotion Discipline

- stable architecture and boundaries: baseline note or ADR
- repeatable operations: runbook
- bounded verified result: evidence pack
- still-moving execution details: session or observations
- contradicted durable truth: supersede or annotate the existing artifact

The goal is not to store more. The goal is to keep retrieval biased toward what is true now and still useful later.
