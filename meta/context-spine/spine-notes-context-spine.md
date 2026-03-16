---
title: Context Spine Baseline
aliases:
  - spine-notes-context-spine
tags:
  - context-spine
  - bootstrap
  - memory
domain: repo-bootstrap
type: spine-note
as_of: 2026-03-15
source_of_truth:
  - /Users/mhess/aem/aem-code/context-spine/README.md
  - /Users/mhess/aem/aem-code/context-spine/AGENTS.md
  - /Users/mhess/aem/aem-code/context-spine/package.json
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/bootstrap.sh
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/context_config.py
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/init-qmd.sh
---

# Context Spine Baseline

## Summary

As of 2026-03-15, this repository is the reusable boilerplate for bootstrapping repo-local memory, QMD-backed retrieval, evidence capture, explicit repo-local config, and verification surfaces in agent-assisted software projects.

## Current State

- Repo-local memory lives under `meta/context-spine/`.
- Bootstrap and session helpers live under `scripts/context-spine/`.
- `meta/context-spine/context-spine.json` is now the explicit contract for project name, memory root, baseline preference, QMD collections, query defaults, and gitignore mode.
- Preferred local entrypoints are `npm run context:init`, `npm run context:bootstrap`, `npm run context:doctor`, `npm run context:upgrade`, `npm run context:session`, `npm run context:score`, `npm run context:update`, `npm run context:embed`, and `npm run context:verify`.
- `meta/context-spine/hot-memory-index.md` should behave like a curated working set, not just a recent-files dump.
- QMD collections should at minimum include `context-spine-meta` for `meta/` and `project-docs` for `docs/`.
- The bootstrap flow should surface this note, the latest session note, recent visual explainers, and a quick QMD retrieval pass.
- Repo-local Codex skill sources live under `.pi/skills/`, including the core spine suite and companion review skills.
- The core spine suite now treats active-delivery recovery, invalidation, hydration, flow state, and metacognitive checks as first-class operating concerns.
- Existing project installs should have a dedicated upgrade path instead of assuming every change is a fresh drop-in.
- The upgrade path should copy missing config/runtime helpers safely but surface project-owned config differences for deliberate merge review.
- Session templates should capture branch, HEAD, worktree state, and the last meaningful verification command so agents restart from concrete execution state.
- The repo uses E.L.O.N. as a doctrine for evaluating whether memory features improve reality alignment or just add complexity.
- The runtime now carries stdlib tests for config loading, gitignore management, upgrade evaluation, hot-memory source resolution, and doctor config checks.

## Decisions

- Keep memory repo-local in this boilerplate instead of assuming a parent workspace.
- Treat `qmd` as the preferred retrieval layer, but keep bootstrap usable when `qmd` is absent or not yet initialized.
- Ship a canonical baseline durable note so agents have one high-signal artifact to open immediately.
- Prefer `npm run context:*` wrappers so bootstrap commands still work when executable bits are lost outside a normal git checkout.
- Make repo policy explicit in `context-spine.json` so bootstrap, doctor, score, upgrade, and gitignore surfaces stop inferring project shape independently.
- Keep principal-engineer oversight as an additive review skill under `.pi/skills/` instead of making it a hard dependency of the core loop.
- Keep Context Spine itself as the thinnest possible operating layer for current truth; if a memory feature drifts into ceremony, simplify or remove it.
- Add a doctor command that checks baseline integrity, session freshness, generated-aid freshness, docs authority, and visual surfaces.
- Add an additive-first upgrade command for older installs so the boilerplate can evolve without clobbering project-owned memory surfaces.
- Upgrade hot memory from raw recency into a working set tied to baseline source-of-truth files, canonical docs, and recent visual explainers.
- Back the runtime with a local unittest suite so adoption confidence comes from executable proof, not README promises.
- Keep E.L.O.N. explicit so future changes are judged by value, legibility, utility x impact, and reduced blind inference.

## Open Questions

- Should bootstrap eventually offer an explicit `--fresh` mode that runs `qmd update` and `qmd embed` automatically on first setup?
- Should QMD collection descriptions or contexts be seeded automatically to improve retrieval ranking out of the box?
- Should the doctor eventually compare roadmap, ADR, and evidence surfaces for project-truth drift, not just memory hygiene?
- Should `context:verify` eventually include an optional QMD smoke pass when the host machine already has QMD installed and indexed?

## Sources

- /Users/mhess/aem/aem-code/context-spine/README.md
- /Users/mhess/aem/aem-code/context-spine/AGENTS.md
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/bootstrap.sh
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/init-qmd.sh
- /Users/mhess/aem/aem-code/context-spine/docs/runbooks/session-start.md
