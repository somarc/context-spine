# Memory State

## Goal

Export a machine-readable summary of the current Context Spine memory layers so Codex can consume project memory more natively than by scraping markdown alone.

This is not the durable project truth itself.
It is a generated machine-facing state surface that summarizes:

- session memory
- project memory
- machine record counts
- generated aid freshness

## Command

Preferred wrapper:

```bash
npm run context:state
```

Direct script:

```bash
python3 ./scripts/context-spine/memory-state.py
```

Useful flag:

```bash
python3 ./scripts/context-spine/memory-state.py --out ./meta/context-spine/memory-state.json
```

## What It Exports

The export now produces two companion surfaces:

- `meta/context-spine/memory-state.json`
- `meta/context-spine/memory-state.html`

The JSON and HTML surfaces include:

- latest session markdown surface
- latest baseline note
- counts for ADRs, runbooks, diagrams, and evidence packs
- record counts for session, observation, and evidence machine surfaces
- recent run history from commands like `context:doctor`, `context:score`, and `context:state`
- freshness snapshots for generated aids like hot memory and scorecards

The default output paths are:

```text
meta/context-spine/memory-state.json
meta/context-spine/memory-state.html
```

## Why It Exists

Context Spine still treats markdown and docs as the human-readable truth layer.

`context:state` adds a thinner machine layer next to that truth so Codex can:

- query current memory shape faster
- rank layers explicitly
- reconcile memory surfaces without inferring everything from prose
- render a visual explanation without inventing a separate manual artifact

## Boundaries

- `memory-state.json` is a generated aid, not a durable note
- `memory-state.html` is a generated visual reading surface, not a curated explainer
- it should not replace baselines, ADRs, runbooks, or evidence packs
- it should stay structurally simple and easy to regenerate
- if it becomes more important than the project-truth files it summarizes, the design has drifted
