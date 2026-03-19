# Context Spine Memory Agent Guide

## Scope

This subtree is the repo-local memory layer.

- Treat it as the synthesis and restart surface for the repo, not as a
  substitute for code, docs, tests, or command evidence.
- Prefer updating this subtree when the truth is about current project model,
  restart quality, durable evidence, or handoff quality.
- When code, docs, tests, and memory disagree, reconcile the disagreement
  explicitly instead of treating the sources as interchangeable.

## Reading Order

Open the smallest useful working set first:

1. `meta/context-spine/spine-notes-*.md`
2. `meta/context-spine/hot-memory-index.md` when present
3. the latest file under `meta/context-spine/sessions/`
4. the most relevant file under `meta/context-spine/observations/` or
   `meta/context-spine/evidence-packs/`
5. `docs/runbooks/native-memory-apis.md` when machine-readable contracts or
   subagent integration matter

## Surface Types

### Durable manual surfaces

- `spine-notes-*.md`
- `sessions/`
- `observations/`
- `evidence-packs/`

These are the main human-maintained memory surfaces.

### Generated aids

- `hot-memory-index.md`
- `doctor-report.md`
- `memory-scorecard.md`
- `rollout-report.md`
- `upgrade-report.md`
- `memory-state.json`
- `memory-state.html`

Do not hand-edit generated aids unless you are repairing the generator or
recovering from a failed run.

### Machine-written traces

- `records/`
- `events/`
- `runs/`

If these directories exist, write them through Context Spine scripts, not by
hand.

### Retrieval surfaces

- `context-spine.json`
- `.qmd/`

Do not edit `.qmd/` files directly.

## Native Command Spectrum

Run these from the repo root.

### Bootstrap and query

- `npm run context:bootstrap`
- `npm run context:query -- --mode active-delivery`
- `npm run context:rehydrate -- --mode active-delivery`

### Capture and working memory

- `npm run context:session`
- update session, observation, or evidence-pack files directly when the content
  is evidence-backed and bounded

### Reconciliation

- `npm run context:promote -- ...`
- `npm run context:invalidate -- ...`
- `npm run context:event -- --type ...`

Use reconciliation commands when durable truth changed. Keep file edits and
memory trace writes explicit.

### Maintenance and verification

- `npm run context:state`
- `npm run context:doctor`
- `npm run context:score`
- `npm run context:update`
- `npm run context:embed`
- `npm run context:refresh`
- `npm run context:verify`

## Delegation Contract

When subagents are involved:

- the parent agent runs `context:query` or `context:rehydrate` first
- subagents receive the compact packet plus a bounded objective and file scope
- subagents return evidence, findings, and candidate file changes
- the parent agent is the single writer for session notes, promotions,
  invalidations, and high-signal events

Do not let subagents create parallel durable memory without parent synthesis.

## Boundaries

- This subtree should stay lean: current truth, explicit evidence, and useful
  handoff surfaces. Avoid transcript accumulation.
- Treat the gitignore mode in `meta/context-spine/context-spine.json` as the
  policy source for which surfaces are shared versus local.
- Use `meta/context-spine/SKILLS.md` as the local routing map for which bundled
  skill or native command fits the job.
