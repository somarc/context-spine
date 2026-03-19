---
name: context-spine
description: Recover current project truth, bootstrap durable repo-local memory, and tighten retrieval. Use when a user asks to recover context, align memory with live code or runtime evidence, set up or repair `meta/context-spine` workflows, create baseline or session notes, invalidate stale assumptions, or codify Context Spine itself as a reusable Codex skill.
---

# Context Spine

## Overview

Use this skill to recover current project truth, make it durable, and keep retrieval grounded in evidence rather than recall. Prefer repo-local memory, direct evidence from code/tests/commands, and supported retrieval adapters such as QMD only when they compress discovery better than raw local access.

> Context Spine is not valuable because it stores more notes. It is valuable when it becomes the thinnest possible operating layer for current truth. If you keep it lean, evidence-based, and invalidation-aware, it is a very strong tool. If it drifts into ceremony, it dies.

Optimize for useful truth under time pressure, not note accumulation.
Optimize for flow as well: hydrate from the deepest relevant sources, move only the needed signal upward, and expose where thinking is compressed, blocked, or inferential.

## First Pass

1. If the repo shape is unknown, inspect the repo-local Context Spine runtime first: prefer `npm run context:config` and `npm run context:bootstrap` when available; otherwise read `meta/context-spine/context-spine.json` and use `python3 scripts/context-spine/context-config.py --repo-root <repo> --format json`.
1. If `meta/context-spine/AGENTS.md` exists, open it before broad memory work; it is the repo-local subtree contract for how to read and update the memory layer.
1. If `meta/context-spine/SKILLS.md` exists, use it as the local routing map for bundled skills and native commands.
1. Detect workspace topology: primary repo, nested repos, planned repos, deployed surfaces, and external endpoints that currently matter.
1. Detect the operating mode: `active-delivery`, `existing`, `partial`, `missing`, `promotion`, or `skill-maintenance`.
1. Prefer repo-local wrappers over ad hoc shell when they exist.
1. Open only the smallest high-signal working set first: a baseline `spine-notes-*.md`, the latest session, `hot-memory-index.md`, and the most relevant ADR or runbook.
1. Treat retrieval engines as supporting adapters, not as the memory contract. QMD remains a supported retrieval surface; reach for it when you need cross-repo discovery, broad corpus sweep, or restart triage, but do not force the working set through retrieval when live repo evidence is already local and smaller.
1. If freshness, project pivots, or contradictory evidence matter, read `references/spine-of-time.md`.
1. If the problem feels information-dense, contradictory, or mentally slippery, read `references/flow-and-cognition.md`.
1. Re-anchor any proposed change in code, tests, or command output. Do not treat code, docs, notes, and evidence as interchangeable.

## Spine Of Time Rules

- Use the evidence ladder: runtime and command evidence, then code and tests, then docs and contracts, then durable notes, then inference.
- When new evidence contradicts durable memory, mark the old truth as superseded. Do not silently keep both live.
- Keep `active objective`, `critical path`, and `suspect assumptions` separate from long-lived architecture notes.
- Relative time words like `current`, `latest`, `today`, or `recent` should resolve to dated evidence whenever possible.

## Flow And Cognition Rules

- Hydrate from the lowest tier that can materially answer the question. Do not jump straight to durable notes when runtime, code, or commands are available.
- Identify dry segments explicitly when an important source was not sampled.
- Keep the flow column explicit:
  - source hydration
  - working-set compression
  - decision frame
  - user-facing summary
  - memory reconciliation
- Treat contradiction as a blockage, not as harmless ambiguity.
- Treat stale notes dominating retrieval as backflow.
- Treat unlabeled inference, wishful extrapolation, or missing uncertainty as metacognitive failure.

## Modes

### Active delivery

- Use this mode when the user is trying to ship, unblock, or prove something now.
- Build a compact working set, not a broad memory tour.
- Output:
  - active objective
  - authoritative surfaces
  - source hydration
  - critical path
  - flow state
  - stale or suspect assumptions
  - metacognitive check
  - immediate next action
- Prefer freshness and unblock value over completeness.
- Reconcile durable memory after implementation if the live truth changed.

### Existing Context Spine repo

- Prefer `npm run context:bootstrap`, `context:session`, `context:update`, and `context:score` when available.
- If you maintain a canonical Context Spine source checkout and need to move target repos forward, prefer `npm run context:upgrade:pull-and-rollout -- --target <repo>` or `--repos <repo-a> <repo-b> ...`.
- Fall back to direct `scripts/context-spine/*` entrypoints when wrappers do not exist.
- Use `context:init` for first install or collection repair, not as the default first move in an already-healthy repo.
- Use `context:embed` only when vector retrieval materially matters and the local runtime supports it; partial lexical hydration is degraded but still usable.
- If retrieval is stale or newly initialized, refresh it before broad file search.
- If the baseline note is missing, create it before expanding the rest of the memory layer.

### Partial repo

- Restore missing surfaces first.
- Fix path ambiguity and wrapper drift before writing more notes or prompts.
- Add a baseline `spine-notes-*.md`, align docs with the real commands, then rerun bootstrap.

### Installing Context Spine

- Add the required surfaces listed in `references/adoption.md`.
- Keep memory repo-local under `meta/context-spine/`.
- Use small scripts and explicit contracts instead of prompt-only glue.
- Add a baseline note and one session path before declaring the install complete.

### Promotion / reconciliation

- Use this mode when recent work changed project shape, invalidated assumptions, or exposed a gap between durable memory and live evidence.
- Capture what should be promoted, what should stay rolling, and what should be marked superseded.
- Pair with `memory-promotion` when the durable destination is unclear.

### Codex skill maintenance

- Treat `.pi/skills/context-spine/` as the repo source-of-truth when it exists.
- Install or sync it into `${CODEX_HOME:-$HOME/.codex}/skills/context-spine` with the repo install script when present.
- Validate the source and installed copies before closing the task.

## Output Expectations

- State the detected mode and topology explicitly.
- Make the agent contract visible: bootstrap, working set, direct evidence, and the durable artifact that would need repair if current memory is misleading.
- Make the human contract visible when helpful: visual explanation, evidence trail, and source-of-truth references instead of raw internal memory mechanics.
- Separate:
  - `ACTIVE_OBJECTIVE`
  - `AUTHORITATIVE_SURFACES`
  - `SOURCE_HYDRATION`
  - `FLOW_STATE`
  - `STALE_OR_SUSPECT_TRUTHS`
  - `COGNITIVE_FRAME`
  - `METACOGNITIVE_CHECK`
  - `WORKING_SET`
  - `NEXT_ACTIONS`
- Provide concrete file paths and commands, not generic advice.
- When you change the system, run the relevant bootstrap/update/validation commands and report the result.
- When durable memory is now misleading, say exactly which artifact should be updated or superseded.

## References

- `references/workflow.md`
- `references/adoption.md`
- `references/spine-of-time.md`
- `references/flow-and-cognition.md`
- `scripts/context-spine/context-config.py`
- `scripts/context-spine/bootstrap.sh`
- `scripts/context-spine/doctor.py`
