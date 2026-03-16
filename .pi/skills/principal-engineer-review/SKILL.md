---
name: principal-engineer-review
description: Assess a project's emerging shape with a principal-engineer lens. Use when the user wants architectural oversight, to judge whether work is solidifying into a sound system, to identify coupling or reliability drift, or to determine what decisions and artifacts should be made durable.
---

# Principal Engineer Review

## Overview

Use this skill to judge the forming shape of a project, not just the correctness of a diff. Focus on architecture, boundaries, reliability, evidence quality, and whether new understanding should be captured in durable memory.

This skill is not the final judge of whether a surface should exist at all.
When the question is partly "is this actually worth keeping?" rather than only "is this structurally sound?", pair this with `elon-doctrine`.

## When To Use

- asked to review project direction, system shape, or architectural drift
- backfilling memory from prior work and deciding what now matters
- auditing whether implementation is becoming harder to change, test, or operate
- deciding whether a finding belongs in a baseline note, ADR, runbook, diagram, or evidence pack

Do not use this as a substitute for normal bug-hunting code review when the user only wants line-level correctness.

## First Pass

1. Open the baseline note, latest session, and the most relevant ADR or runbook.
1. Read the touched code, tests, and command evidence before judging the docs.
1. Identify what changed in system shape, not just file contents.
1. Apply the rubric in `references/rubric.md`.
1. Separate concrete defects from architectural concerns and from memory obligations.
1. If the thing being reviewed may be ceremonial, ornamental, or low-value despite being well-structured, invoke `elon-doctrine` alongside this skill.

## Skill Composition

Use `principal-engineer-review` with adjacent skills when the review spans more than architecture:

- pair with `elon-doctrine`
  when you need a value judgment about whether the surface or workflow should exist at all
- pair with `memory-promotion`
  when the review implies a concrete durable artifact should be created or updated
- pair with `context-spine-maintenance`
  when doctor/score drift needs architectural interpretation rather than hygiene-only reporting

The contract is:

- `principal-engineer-review` judges system shape, boundaries, and durability implications
- companion skills judge worthiness, operating hygiene, or promotion target

## Output Contract

Return concise sections with direct file paths or `qmd://` references:

- `SUMMARY:`
- `FINDINGS:` severity-tagged concerns tied to likely cost or failure
- `RISKS:` what becomes expensive, fragile, or operationally unclear if unchanged
- `DECISIONS_NEEDED:` questions that need an explicit owner or ADR
- `MEMORY_UPDATES_REQUIRED:` exact durable artifact to create or update
- `EVIDENCE:` code, tests, logs, and commands that justify the review
- `NEXT_ACTIONS:` ordered actions, starting with the highest-leverage move

When possible, map memory updates to one of:

- baseline `spine-notes-*.md`
- `docs/adr/*.md`
- `docs/runbooks/*.md`
- `meta/context-spine/evidence-packs/`
- `.agent/diagrams/`

## Boundaries

- Prefer concrete architectural reasoning over generic style advice.
- Do not invent principles that are not supported by code, tests, docs, or evidence.
- If evidence is thin, say so explicitly and reduce confidence.
- Treat code, docs, and memory surfaces as separate truths that must be reconciled.

## References

- `references/rubric.md`
- `../../elon-doctrine/SKILL.md`
