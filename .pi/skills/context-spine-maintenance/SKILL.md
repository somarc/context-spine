---
name: context-spine-maintenance
description: Audit Context Spine hygiene and alignment for a repo. Use when the user wants to tighten repo-local memory, run doctor and score, refresh retrieval, interpret maintenance results, detect durable-memory drift, or decide what to fix first in Context Spine.
---

# Context Spine Maintenance

## Overview

Use this skill for routine maintenance of an installed Context Spine.

This is not the install or upgrade skill. This is the operating loop that answers:

- is the memory spine healthy
- is the spine hydrated
- is evidence flowing cleanly
- what is drifting
- what is stale or misaligned
- what should be fixed first

## Workflow

1. Detect the repo shape and whether Context Spine is present.
1. Detect whether the repo is in active delivery or has recently changed direction; if so, expect alignment drift even when hygiene is green.
1. Prefer repo-local wrappers when they exist.
1. If retrieval is stale enough to mislead search, run `context:update` before the rest of the loop.
1. Run the maintenance loop in this order:
   - `context:bootstrap`
   - `context:doctor`
   - `context:score`
1. Compare the latest baseline, latest session, and key durable docs against current code, commands, and runtime evidence.
1. Classify drift as:
   - hygiene drift: missing surfaces, stale retrieval, wrapper drift, failed doctor checks
   - alignment drift: durable memory no longer matches the current objective, topology, or runtime truth
   - hydration drift: critical evidence tiers are not being sampled before conclusions are formed
   - flow drift: contradictions, stale backflow, or bloated working sets are preventing useful signal movement
   - metacognitive drift: inference, uncertainty, and confidence are not labeled clearly enough
1. If the repo is an older install or partial install, consider `context:upgrade` planning after the doctor pass.
1. Summarize findings as:
   - what is healthy
   - hygiene drift
   - alignment drift
   - flow health
   - invalidations needed
   - what should be fixed now
   - what can wait

## Output Expectations

- Report exact commands run.
- Distinguish deterministic tool findings from your own interpretation.
- Treat `doctor` as the hygiene source of truth and `score` as a secondary signal.
- Treat code, commands, and runtime evidence as the alignment source of truth when durable memory disagrees.
- Separate:
  - `HEALTHY`
  - `HYGIENE_FINDINGS`
  - `ALIGNMENT_FINDINGS`
  - `FLOW_HEALTH`
  - `COGNITIVE_FINDINGS`
  - `METACOGNITIVE_FINDINGS`
  - `INVALIDATIONS_NEEDED`
  - `FIX_NOW`
  - `CAN_WAIT`
- Point back to concrete file paths when recommending changes.

## Boundaries

- Do not duplicate the logic of `doctor.py` or `upgrade.py` in prose.
- Do not invent memory problems that the repo evidence does not support.
- Do not assume green maintenance means the spine is pointing at the right problem.
- Do not confuse more artifacts with better hydration or better flow.
- Use this skill for maintenance and prioritization, not for first-time installation.
- When alignment drift is the main issue, recommend `context-spine` or `memory-promotion` work instead of over-indexing on hygiene.

## References

- `../../../../docs/runbooks/doctor.md`
- `../../../../docs/runbooks/upgrade-existing-project.md`
- `../../../../docs/runbooks/session-start.md`
- `../context-spine/references/flow-and-cognition.md`
