# ADR 0004: Generated Aid Promotion Model

## Status

Accepted

## Context

Context Spine is a memory surface, not a control plane.

Its generated aids are useful precisely because they are cheap to refresh:

- `hot-memory-index.md`
- `memory-scorecard.md`
- `doctor-report.*`
- `rollout-report.*`
- `upgrade-report.*`

Those aids should be self-healing and low-ceremony, but they should not be able to overwrite a working artifact with partial or invalid output.

OpenShell has a stronger discipline around live updates:

- some things are immutable after startup
- updates are validated before promotion
- failed reloads keep the last-known-good active state

Context Spine should borrow only the smallest part of that model that improves trust in generated aids.

## Decision

Generated aids use a candidate-first promotion flow:

1. render the new artifact as a transient candidate file
2. validate the candidate with a lightweight artifact-specific check
3. atomically promote the candidate into the active path only if validation passes
4. if validation fails, keep the active artifact untouched

This applies only to generated aids.

It does not apply to:

- baseline notes
- ADRs
- runbooks
- session notes
- observations
- other human-authored truth surfaces

The candidate file is an implementation detail, not a durable artifact class.
The active file remains the effective last-known-good artifact because failed candidate publication never replaces it.

## Consequences

- generated aids become safer to regenerate
- failed refreshes do not poison the active reading path
- Context Spine gains a clearer `candidate -> validate -> promote` discipline without becoming a runtime platform
- human-authored memory stays explicit and reviewable instead of being pushed behind an approval engine
- the repo avoids a larger policy system, daemon, or orchestration layer

## Out Of Scope

This ADR does not introduce:

- a policy engine
- a background service
- multi-step approval workflows
- runtime sandboxing
- automatic rewriting of durable truth surfaces

The point is narrow:

make generated aids safer, while keeping Context Spine small and legible.
