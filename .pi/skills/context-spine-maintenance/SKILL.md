---
name: context-spine-maintenance
description: Run the Context Spine maintenance loop for a repo. Use when the user wants to audit or tighten repo-local memory, run doctor and score, refresh retrieval, interpret the maintenance results, or decide what to fix first in Context Spine.
---

# Context Spine Maintenance

## Overview

Use this skill for routine maintenance of an installed Context Spine.

This is not the install or upgrade skill. This is the operating loop that answers:

- is the memory spine healthy
- what is drifting
- what should be fixed first

## Workflow

1. Detect the repo shape and whether Context Spine is present.
1. Prefer repo-local wrappers when they exist.
1. Run the maintenance loop in this order:
   - `context:bootstrap`
   - `context:doctor`
   - `context:score`
1. If the repo is an older install or partial install, consider `context:upgrade` planning after the doctor pass.
1. Summarize findings as:
   - what is healthy
   - what is drifting
   - what should be fixed now
   - what can wait

## Output Expectations

- Report exact commands run.
- Distinguish deterministic tool findings from your own interpretation.
- Treat `doctor` as the hygiene source of truth and `score` as a secondary signal.
- Point back to concrete file paths when recommending changes.

## Boundaries

- Do not duplicate the logic of `doctor.py` or `upgrade.py` in prose.
- Do not invent memory problems that the repo evidence does not support.
- Use this skill for maintenance and prioritization, not for first-time installation.

## References

- `../../../../docs/runbooks/doctor.md`
- `../../../../docs/runbooks/upgrade-existing-project.md`
- `../../../../docs/runbooks/session-start.md`
