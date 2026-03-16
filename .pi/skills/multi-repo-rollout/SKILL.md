---
name: multi-repo-rollout
description: Assess or upgrade Context Spine across multiple local repos. Use when the user wants to check several projects, compare their Context Spine state, run doctor and upgrade planning in batch, or roll newer spine features out across a small set of local repos.
---

# Multi Repo Rollout

## Overview

Use this skill when Context Spine needs to be checked or evolved across several local repositories.

This skill is for a small fleet of local repos, not a massive deployment system.

## Workflow

1. Gather the target repo paths.
1. Run the rollout script when available.
1. For each repo, capture:
   - detected mode
   - doctor status
   - upgrade-safe gaps
   - merge-review gaps
1. Rank the repos by urgency:
   - broken or missing
   - partial
   - existing but drifting
   - current
1. Recommend the rollout order and next action for each repo.

## Preferred Command

Use:

```bash
python3 ./scripts/context-spine/rollout.py --repos <repo-a> <repo-b> ...
```

If the user wants safe additive upgrades applied, use:

```bash
python3 ./scripts/context-spine/rollout.py --apply-safe --repos <repo-a> <repo-b> ...
```

## Output Expectations

- Keep the report repo-by-repo and explicit.
- Separate `doctor` findings from `upgrade` findings.
- Highlight which repos need human merge review versus safe additive rollout.

## Boundaries

- Do not overwrite project-owned files silently.
- Treat this as a small-batch local rollout tool, not a generic deployment framework.
- Use the generated report as the artifact for the rollout decision.

## References

- `../../../../docs/runbooks/upgrade-existing-project.md`
- `../../../../docs/runbooks/doctor.md`
- `../../../../scripts/context-spine/rollout.py`
