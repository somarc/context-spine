---
name: memory-promotion
description: Promote or supersede project memory. Use when the user wants to decide whether sessions, observations, or recent work should become a baseline note, ADR, runbook, evidence pack, or diagram, or when existing durable memory may now be stale or misleading.
---

# Memory Promotion

## Overview

Use this skill when recent work exists, but it is not yet clear what deserves promotion into durable project memory.

This skill answers:

- what should stay rolling
- what should become durable
- what should be superseded
- where that durable knowledge should live
- which recurring flow or cognition failures should become durable repairs

## Workflow

1. Read the latest baseline note, latest session, and the most relevant durable docs.
1. Review code, tests, commands, or evidence before promoting any claim.
1. Note freshness and contradictions, not just content.
1. Check whether the work exposed a recurring hydration, flow, or metacognitive failure that should be captured as a reusable repair.
1. Classify recent knowledge into one of:
   - keep in session only
   - supersede an existing durable artifact
   - retire or stop trusting an existing durable artifact
   - promote into baseline `spine-notes-*.md`
   - promote into `docs/adr/`
   - promote into `docs/runbooks/`
   - promote into `meta/context-spine/evidence-packs/`
   - promote into `.agent/diagrams/`
   - promote into a skill reference or skill contract when the repair is about how the spine should think
1. Prefer the smallest durable surface that preserves the truth without duplication.
1. Explain why each promotion or supersession target is the right one.

## Promotion Rules

- architecture, boundaries, and stable models
  - baseline note or ADR
- repeatable operating procedure
  - runbook
- trusted result from a bounded investigation
  - evidence pack
- complex system shape or workflow that reads better visually
  - diagram
- contradicted durable truth
  - update the same durable artifact or annotate it as superseded nearby
- temporary execution details or still-moving work
  - keep in session or observations
- unresolved or weakly evidenced claims
  - keep rolling until the evidence is strong enough
- recurring hydration or reasoning repair
  - update the relevant skill or reference instead of scattering the fix across project notes

## Output Expectations

Return:

- current rolling inputs
- recommended promotions
- recommended supersessions or retirements
- flow or cognition repairs worth promoting
- why they belong in those destinations
- exact file paths to create or update
- freshness markers: what evidence or command made the recommendation trustworthy

## Boundaries

- Do not promote speculation without evidence.
- Do not copy the same truth into multiple durable surfaces unless there is a clear reason.
- Do not let obsolete truth remain unmarked if it will mislead later retrieval.
- Favor curation over accumulation.

## References

- `../../../../docs/runbooks/memory-retention.md`
- `../../../../docs/templates/durable-note-template.md`
- `../../../../docs/templates/session-summary-template.md`
- `../context-spine/references/flow-and-cognition.md`
