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
as_of: 2026-03-20
source_of_truth:
  - /Users/mhess/aem/aem-code/context-spine/README.md
  - /Users/mhess/aem/aem-code/context-spine/AGENTS.md
  - /Users/mhess/aem/aem-code/context-spine/package.json
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/bootstrap.sh
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/setup.sh
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/refresh.sh
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/context_config.py
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/project_space.py
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/init-qmd.sh
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/runtime-manifest.json
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/runtime_manifest.py
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/run_state.py
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/generated_artifact.py
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/memory_records.py
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/memory-state.py
  - /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/upgrade.py
  - /Users/mhess/aem/aem-code/context-spine/docs/adr/0005-context-spine-design-compass.md
  - /Users/mhess/aem/aem-code/context-spine/docs/adr/0006-native-codex-memory-direction.md
  - /Users/mhess/aem/aem-code/context-spine/docs/adr/0007-native-memory-apis-without-runtime-orchestration.md
  - /Users/mhess/aem/aem-code/context-spine/docs/runbooks/memory-state.md
  - /Users/mhess/aem/aem-code/context-spine/docs/runbooks/project-space-modes.md
  - /Users/mhess/aem/aem-code/context-spine/docs/runbooks/visual-explainers.md
  - /Users/mhess/aem/aem-code/context-spine/docs/runbooks/memory-retention.md
  - /Users/mhess/aem/aem-code/context-spine/meta/context-spine/SKILLS.md
  - /Users/mhess/aem/aem-code/context-spine/.pi/skills/context-spine/SKILL.md
  - /Users/mhess/aem/aem-code/context-spine/.pi/skills/memory-promotion/SKILL.md
  - /Users/mhess/aem/aem-code/context-spine/.pi/skills/visual-corpus-curator/SKILL.md
---

# Context Spine Baseline

## Summary

As of 2026-03-20, this repository is the reusable boilerplate for bootstrapping Context Spine across either a single repo or a non-git parent workspace, with retrieval-backed discovery, evidence capture, explicit local config, and verification surfaces in agent-assisted software projects.

## Current State

- Repo-local memory lives under `meta/context-spine/`.
- Bootstrap and session helpers live under `scripts/context-spine/`.
- `meta/context-spine/context-spine.json` is now the explicit contract for project name, memory root, baseline preference, QMD collections, query defaults, gitignore mode, and project-space topology.
- Preferred local entrypoints are `npm run context:setup`, `npm run context:bootstrap`, `npm run context:session`, `npm run context:refresh`, `npm run context:doctor`, and `npm run context:verify`.
- `context:setup` and `context:refresh` now default to lexical retrieval only; `context:embed` is the explicit vector-hydration path.
- Low-level retrieval primitives remain available as `npm run context:init`, `npm run context:update`, and `npm run context:embed` for cases where the repo needs direct control instead of the lean path.
- `meta/context-spine/hot-memory-index.md` should behave like a curated working set, not just a recent-files dump.
- QMD collections should at minimum include `context-spine-meta` for `meta/` and `project-docs` for `docs/`.
- The primary agent working set is baseline note, latest session, hot memory, and the named `source_of_truth` files; retrieval backends such as QMD remain supported surfaces, but they are not the core memory contract.
- Long-horizon deep notes may live outside the repo in a linked durable note system; QMD is the preferred retrieval fabric across repo truth and that external layer.
- The bootstrap flow should detect `fresh`, `recovery`, and `active` modes so normal sessions stay compact while first setup and stale recovery stay explicit.
- The runtime now supports both `repo` mode and `workspace` mode, so a non-git parent folder can own a top-level spine and coordinate child git repos.
- In workspace mode, the parent spine owns cross-repo truth and the parent hot-memory working set hydrates from child repo spines instead of treating the parent as an invalid repo.
- The topology model now also has a light-touch `linked-child` option, so a child repo can carry only a `.context-spine.json` vertebra contract instead of a full adjacent install.
- `context:upgrade` can now author that light-touch vertebra contract directly through `--adopt-mode linked-child --workspace-root ...`, so linked-child adoption is an explicit workflow instead of manual file editing.
- The intended memory model is hierarchical: higher folders should be more meta-aware of the whole subtree, while lower folders should own more localized truth and working memory.
- The `aem-code -> OAK -> child repo` shape is now the clearest concrete example of that hierarchy: top-level workspace intelligence, project-space intelligence, then repo-local vertebrae.
- Linked-child adoption now auto-discovers the nearest ancestor workspace spine, so the common nested-repo path does not require restating `--workspace-root`.
- Runtime surfaces now expose natural hierarchy labels directly: `meta spine`, `project spine`, `repo spine`, and `repo vertebra`.
- Repo-local Codex skill sources live under `.pi/skills/`, including the core spine suite and companion review skills.
- The core spine suite now treats active-delivery recovery, invalidation, hydration, flow state, and metacognitive checks as first-class operating concerns.
- Existing project installs should have a dedicated upgrade path instead of assuming every change is a fresh drop-in.
- The upgrade path should copy missing config/runtime helpers safely but surface project-owned config differences for deliberate merge review.
- Session templates should capture branch, HEAD, worktree state, and the last meaningful verification command so agents restart from concrete execution state.
- The repo uses E.L.O.N. as a doctrine for evaluating whether memory features improve reality alignment or just add complexity.
- The runtime now carries stdlib tests for config loading, gitignore management, upgrade evaluation, hot-memory source resolution, and doctor config checks.
- The runtime now has an explicit versioned manifest for shared boilerplate/runtime surfaces and compatibility metadata.
- Maintenance commands now emit run IDs and write structured JSON run records under `meta/context-spine/runs/`.
- Codex skill sync now validates source and installed digests instead of only checking syntax.
- Generated aids now publish through transient candidate artifacts and promote only after validation passes, so failed refreshes do not overwrite the active reading path.
- The repo now has an explicit design compass for future evolution: protect inspectability, memory-class separation, and simplicity, and reject moves toward prompt soup, control-plane behavior, or confidence theater.
- The repo now has a proposed native-memory direction: layered memory, automatic evidence capture, stronger structured schemas, first-class APIs, and less ceremony, while keeping file-level project truth intact.
- That native-memory direction now makes a sharper distinction between internal and external contracts: the memory may become native and agent-centric internally, but the human-facing output should visually explain what matters and why.
- The native-memory direction is now bounded more concretely: capture, query, promote, invalidate, and reconcile are allowed core API families, but runtime orchestration, agent dispatch, scheduling, and hidden prompt-owned project truth are not.
- The human-facing contract is now explicit: visual explanation, evidence trails, and source-of-truth references matter more than exposing retrieval internals.
- Beyond the README layer, the deeper docs are primarily agent-facing operating substrate; humans should usually prefer the visual explainer layer unless they want raw evidence or mechanics.
- Visual surfaces now split cleanly between standalone explainers under
  `.agent/diagrams/` and normalized, date-addressable corpora under
  `meta/visual-corpus/` when compare and trend views matter.
- Session, observation, and evidence helpers now emit machine-readable records under `meta/context-spine/records/` alongside the existing markdown surfaces.
- `context:state` now emits a machine-readable JSON summary plus a generated HTML explainer so the current memory layers can be consumed by Codex and read quickly by humans.
- The state surface now also summarizes recent run history so verification and maintenance commands become visible memory, not just terminal output.
- Run-state capture now records git branch/head, dirty-worktree counts, diff summaries, and managed verification step results automatically for Context Spine commands.
- A new sparse event layer now exists for meaningful edit bursts, retrieval passes, decisions, invalidations, context shifts, and automatic verification outcomes.
- `context:verify` now proves the core reopening path more directly by covering bootstrap, lexical retrieval, and an optional embed probe when QMD is present.
- `context:doctor` now reports retrieval state explicitly as lexical-ready, unavailable, or embed-warned instead of implying full retrieval health from general hygiene alone.
- `context:score` now measures broader spine strength across contract clarity, recovery surfaces, proof, retrieval readiness, and human legibility instead of just QMD-mention density.

## Decisions

- Keep Context Spine local to the project root, but allow that root to be either a single repo or a non-git parent workspace that coordinates child repos.
- Keep full adjacent installs optional rather than mandatory; a project may instead declare itself as a `linked-child` and defer shared Context Spine truth to the parent workspace spine.
- Treat `qmd` as the default supported retrieval surface, but keep the agent working path usable when `qmd` is absent, partially hydrated, or not yet initialized.
- Keep lexical retrieval in the safe default path and treat vector hydration as explicit acceleration rather than a hidden prerequisite.
- Treat external durable notes as a first-class companion layer, not as an awkward afterthought; Obsidian CLI is optional help for that layer, not a core dependency.
- Keep the human contract narrow: README plus visual explainers first, deeper docs second.
- Ship a canonical baseline durable note so agents have one high-signal artifact to open immediately.
- Prefer `npm run context:*` wrappers so bootstrap commands still work when executable bits are lost outside a normal git checkout.
- Make repo policy explicit in `context-spine.json` so bootstrap, doctor, score, upgrade, and gitignore surfaces stop inferring project shape independently.
- Make project-space mode explicit in `context-spine.json` so bootstrap, doctor, upgrade, and rollout can distinguish a repo root from a coordinating workspace root without relying on `.git` alone.
- Treat `.context-spine.json` as the explicit vertebra contract for light-touch child repos so rollout and doctor can classify them as intentional topology, not as broken installs.
- Keep linked-child adoption explicit through `context:upgrade` so the light-touch path stays inspectable, deliberate, and documented.
- Treat the filesystem hierarchy itself as the memory hierarchy: broader intelligence at higher layers, more concrete truth at lower layers.
- Prefer hierarchy discovery over repeated manual wiring; when a child repo already lives under a valid workspace spine, the runtime should discover that and use it.
- Let user-facing surfaces speak in natural scope labels first and internal topology labels second.
- Keep principal-engineer oversight as an additive review skill under `.pi/skills/` instead of making it a hard dependency of the core loop.
- Keep Context Spine itself as the thinnest possible operating layer for current truth; if a memory feature drifts into ceremony, simplify or remove it.
- Collapse first-use ceremony into one setup command and one refresh command so the default path is easier to adopt and easier to remember.
- Keep bootstrap compact in active-session mode and reserve deeper retrieval output for recovery cases.
- Add a doctor command that checks baseline integrity, session freshness, generated-aid freshness, docs authority, and visual surfaces.
- Add an additive-first upgrade command for older installs so the boilerplate can evolve without clobbering project-owned memory surfaces.
- Upgrade hot memory from raw recency into a working set tied to baseline source-of-truth files, canonical docs, and recent visual explainers.
- Back the runtime with a local unittest suite so adoption confidence comes from executable proof, not README promises.
- Keep E.L.O.N. explicit so future changes are judged by value, legibility, utility x impact, and reduced blind inference.
- Keep the runtime manifest as the shared contract for upgrade-safe runtime files instead of duplicating file lists across scripts.
- Keep revision-safety mechanics scoped to generated aids instead of extending them into human-authored truth surfaces.
- Use the design compass as the harder boundary for future "native memory" ambitions so Context Spine can improve without losing its purpose.
- Treat native-memory evolution as a dual-surface problem: human-readable file truth plus machine-usable structured capture, never one replacing the other.
- Keep native memory APIs scoped to memory services; if a future proposal needs a control plane, scheduler, worker bus, or runtime-owned prompt store, it belongs in an external adapter or runtime instead.
- Prefer direct evidence over retrieval when the relevant repo surfaces are already local and bounded; use retrieval primarily for discovery, sweep, and human lookup.
- Keep `context:state` as a thin generated summary of existing memory, not as a replacement for the baseline, ADRs, runbooks, or curated explainers.
- Keep one-off visual explainers and date-based visual corpora distinct:
  `.agent/diagrams/` is the standalone reading surface, while
  `meta/visual-corpus/` holds normalized capture manifests and catalogs.
- Prefer enriching managed run capture over adding more manual notes when the missing truth is really command, test, git, or diff provenance.
- Keep the event stream sparse and high-signal; if it starts looking like shell history, remove or simplify it.
- Do not let maintenance surfaces claim strength from retrieval ritual alone; strength has to include the actual restart and proof path.

## Open Questions

- Should bootstrap eventually offer an explicit `--fresh` mode that runs `qmd update` and `qmd embed` automatically on first setup?
- Should QMD collection descriptions or contexts be seeded automatically to improve retrieval ranking out of the box?
- Should the doctor eventually compare roadmap, ADR, and evidence surfaces for project-truth drift, not just memory hygiene?

## Sources

- /Users/mhess/aem/aem-code/context-spine/README.md
- /Users/mhess/aem/aem-code/context-spine/AGENTS.md
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/bootstrap.sh
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/project_space.py
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/setup.sh
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/refresh.sh
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/doctor.py
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/mem-score.py
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/upgrade.py
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/verify.py
- /Users/mhess/aem/aem-code/context-spine/scripts/context-spine/init-qmd.sh
- /Users/mhess/aem/aem-code/context-spine/docs/runbooks/session-start.md
- /Users/mhess/aem/aem-code/context-spine/docs/runbooks/visual-explainers.md
- /Users/mhess/aem/aem-code/context-spine/docs/runbooks/memory-retention.md
- /Users/mhess/aem/aem-code/context-spine/docs/runbooks/project-space-modes.md
- /Users/mhess/aem/aem-code/context-spine/meta/context-spine/SKILLS.md
- /Users/mhess/aem/aem-code/context-spine/.pi/skills/context-spine/SKILL.md
- /Users/mhess/aem/aem-code/context-spine/.pi/skills/memory-promotion/SKILL.md
- /Users/mhess/aem/aem-code/context-spine/.pi/skills/visual-corpus-curator/SKILL.md
