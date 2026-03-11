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
as_of: 2026-03-11
source_of_truth:
  - /Users/mhess/aem/aem-code/context-spine/README.md
  - /Users/mhess/aem/aem-code/context-spine/AGENTS.md
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/bootstrap.sh
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/init-qmd.sh
---

# Context Spine Baseline

## Summary

As of 2026-03-11, this repository is the reusable boilerplate for bootstrapping repo-local memory, QMD-backed retrieval, evidence capture, and visual explainers in agent-assisted software projects.

## Current State

- Repo-local memory lives under `meta/context-spine/`.
- Bootstrap and session helpers live under `scripts/context-spine/`.
- Preferred local entrypoints are `npm run context:init`, `npm run context:bootstrap`, `npm run context:session`, `npm run context:score`, `npm run context:update`, and `npm run context:embed`.
- QMD collections should at minimum include `context-spine-meta` for `meta/` and `project-docs` for `docs/`.
- The bootstrap flow should surface this note, the latest session note, recent visual explainers, and a quick QMD retrieval pass.

## Decisions

- Keep memory repo-local in this boilerplate instead of assuming a parent workspace.
- Treat `qmd` as the preferred retrieval layer, but keep bootstrap usable when `qmd` is absent or not yet initialized.
- Ship a canonical baseline durable note so agents have one high-signal artifact to open immediately.
- Prefer `npm run context:*` wrappers so bootstrap commands still work when executable bits are lost outside a normal git checkout.

## Open Questions

- Should bootstrap eventually offer an explicit `--fresh` mode that runs `qmd update` and `qmd embed` automatically on first setup?
- Should QMD collection descriptions or contexts be seeded automatically to improve retrieval ranking out of the box?
- Should the boilerplate include a first-run doctor command for checking prerequisites and repo shape drift?

## Sources

- /Users/mhess/aem/aem-code/context-spine/README.md
- /Users/mhess/aem/aem-code/context-spine/AGENTS.md
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/bootstrap.sh
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/init-qmd.sh
- /Users/mhess/aem/aem-code/context-spine/docs/runbooks/session-start.md
