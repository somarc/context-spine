# Context Spine Skill Map

This file maps Context Spine jobs to the right bundled skill or native command.

It is a local reference surface, not an auto-trigger mechanism by itself. The
automatic subtree behavior belongs in `meta/context-spine/AGENTS.md`.

## Bundled Skills

- `context-spine`
  Use for recovering current truth, bootstrap, repair, alignment with live
  evidence, and understanding the overall Context Spine operating model.
- `context-spine-maintenance`
  Use for doctor, score, retrieval hygiene, drift classification, and deciding
  what to fix first.
- `memory-promotion`
  Use when the question is where stable knowledge should land: baseline note,
  ADR, runbook, evidence pack, or observation.
- `principal-engineer-review`
  Use when the issue is system shape, coupling, boundary drift, or whether the
  memory layer is staying useful.
- `elon-doctrine`
  Use when the question is whether a memory change makes the system more useful,
  legible, grounded, and worth keeping.
- `multi-repo-rollout`
  Use when Context Spine needs to be assessed or rolled out across several local
  repos instead of one.

## Native Command Spectrum

Run these from the repo root.

### Restart and active context

- `npm run context:bootstrap`
- `npm run context:query -- --mode active-delivery`
- `npm run context:rehydrate -- --mode active-delivery`
- `npm run context:state`

### Capture

- `npm run context:session`
- `python3 ./scripts/context-spine/mem-log.py ...`

### Reconciliation

- `npm run context:promote -- ...`
- `npm run context:invalidate -- ...`
- `npm run context:event -- --type ...`

### Maintenance

- `npm run context:doctor`
- `npm run context:score`
- `npm run context:update`
- `npm run context:embed`
- `npm run context:refresh`
- `npm run context:verify`
- `npm run context:rollout -- --repos ...`

## Selection Rules

- If the question is "what matters right now?" use `context:query`,
  `context:rehydrate`, `context:state`, or the `context-spine` skill.
- If the question is "is the memory layer healthy?" use
  `context-spine-maintenance`.
- If the question is "what should become durable?" use `memory-promotion`.
- If the question is "should this memory pattern exist at all?" use
  `elon-doctrine`.
- If the question is "is the system shape still sound?" use
  `principal-engineer-review`.
- If the question is "how do we apply this across several repos?" use
  `multi-repo-rollout`.

## Subagent Pattern

- `explorer` agents gather evidence, inspect relevant surfaces, and compare
  conflicting memory.
- `worker` agents handle narrow edits with explicit file boundaries.
- `awaiter` agents watch long-running verification, refresh, or rollout jobs.
- The parent agent should remain the single writer for durable Context Spine
  memory and reconciliation traces.
