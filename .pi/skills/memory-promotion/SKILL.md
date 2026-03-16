---
name: memory-promotion
description: Promote rolling memory into durable artifacts. Use when the user wants to decide whether sessions, observations, or recent work should become a baseline note, ADR, runbook, evidence pack, or diagram, or asks what should be made durable.
---

# Memory Promotion

## Overview

Use this skill when recent work exists, but it is not yet clear what deserves promotion into durable project memory.

This skill answers:

- what should stay rolling
- what should become durable
- where that durable knowledge should live

## Workflow

1. Read the latest baseline note, latest session, and the most relevant durable docs.
1. Review code, tests, commands, or evidence before promoting any claim.
1. Classify recent knowledge into one of:
   - keep in session only
   - promote into baseline `spine-notes-*.md`
   - promote into `docs/adr/`
   - promote into `docs/runbooks/`
   - promote into `meta/context-spine/evidence-packs/`
   - promote into `.agent/diagrams/`
1. Prefer the smallest durable surface that preserves the truth without duplication.
1. Explain why each promotion target is the right one.

## Promotion Rules

- architecture, boundaries, and stable models
  - baseline note or ADR
- repeatable operating procedure
  - runbook
- trusted result from a bounded investigation
  - evidence pack
- complex system shape or workflow that reads better visually
  - diagram
- temporary execution details or still-moving work
  - keep in session or observations

## Output Expectations

Return:

- current rolling inputs
- recommended promotions
- why they belong in those destinations
- exact file paths to create or update

## Boundaries

- Do not promote speculation without evidence.
- Do not copy the same truth into multiple durable surfaces unless there is a clear reason.
- Favor curation over accumulation.

## References

- `../../../../docs/runbooks/memory-retention.md`
- `../../../../docs/templates/durable-note-template.md`
- `../../../../docs/templates/session-summary-template.md`
