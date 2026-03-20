---
name: visual-corpus-curator
description: Curate a corpus of dated technical captures and generate visual index, capture, compare, and trend views from normalized manifests. Use when the user wants immutable day-by-day snapshots, longitudinal progress tracking, multi-document visual aggregation, or a browsable visual atlas over ADRs, coverage reports, milestones, evidence packs, or project notes.
---

# Visual Corpus Curator

Use this skill to build a durable visual corpus, not a one-off explainer page.

This skill is for situations where the user no longer wants to hand-edit HTML
artifacts and instead wants:

- immutable captures
- normalized metadata
- generated visual pages
- date-based or milestone-based browsing
- comparison and trend views over time
- a coherent atlas instead of a pile of disconnected explainers

`visual-corpus-curator` owns the corpus model.
`visual-explainer` remains the rendering engine when that runtime skill is
available.

## When To Use

- daily or session-based progress captures
- coverage and test-progress atlases
- ADR libraries and decision timelines
- milestone or phase history views
- evidence-pack browsers
- explainers that have become disjointed over time and need curation
- any document corpus that should be browsable by date, scope, and comparison

Do not use this for a single standalone page. For that, use `visual-explainer`
or a normal `.agent/diagrams/` explainer.

## Core Model

Always separate three layers:

1. **source evidence**
   - docs, logs, git ranges, metrics, notes, ADRs, existing explainers
2. **normalized capture manifests**
   - machine-readable, stable, comparable
3. **generated views**
   - HTML index, capture, compare, and trend pages

Never treat generated HTML as the source of truth.
Never hand-edit generated HTML once the corpus model exists.

## Default Filesystem Shape

Unless the user already has a better structure, prefer:

```text
<workspace>/meta/visual-corpus/
  captures/
    <scope>/
      2026-03-20-<scope>.json
      2026-03-27-<scope>.json
  catalogs/
    <scope>.json
  generated/
    index.html
    <scope>/
      2026-03-20.html
      2026-03-27.html
      compare-2026-03-20-vs-2026-03-27.html
      trend.html
```

If the repo already has a date or milestone archive shape, adapt to it rather
than forcing this exact layout.

## First Pass

1. Determine the corpus scope.
   - module, repo, milestone, ADR family, evidence family, or project
2. Determine capture granularity.
   - day, session, week, milestone, or release
3. Inventory the source evidence.
   - docs, git ranges, metrics, test outputs, notes
4. Create or update capture manifests using the schema in
   `references/capture-schema.md`.
5. Refresh the catalog or index manifest.
6. Generate the required views using `visual-explainer` patterns.
7. Keep the manifests and generated pages in sync.

## Non-Negotiable Rules

- one capture should describe one bounded time slice or work slice
- captures are immutable snapshots except for factual correction
- if a capture is corrected, preserve the same identity and note the correction
- comparable metrics must keep a stable definition across captures
- if a metric changes meaning, mark it explicitly rather than pretending it is
  comparable
- every quantitative claim should point back to evidence
- generated HTML is disposable output; manifests are the durable contract

## Capture Design Rules

Good captures are:

- date-addressable
- scope-specific
- evidence-backed
- comparable to adjacent captures
- small enough to browse quickly

Bad captures are:

- giant rolling summaries that get edited forever
- prose-only snapshots with no structured fields
- captures that mix incompatible scopes or metric definitions
- captures with no recorded git range, source docs, or evidence links

## Required Capture Fields

At minimum, each capture should have:

- `id`
- `date`
- `scope`
- `headline`
- `summary`
- `sources`
- `git_range` when code change is relevant
- `metrics` or `checkpoints` when progress is quantitative
- `next_targets` or equivalent future-facing summary

See `references/capture-schema.md` for the full schema and examples.

## View Types

Use the view patterns in `references/view-models.md`.

Default view set:

1. **Capture page**
   - one page for one date or session
2. **Index page**
   - catalog of all captures for a scope
3. **Compare page**
   - side-by-side or delta view for two captures
4. **Trend page**
   - time-series view for one or more stable metrics

Do not start with every possible view. Build only the views the corpus can
truthfully support.

## Relationship To Context Spine

Use this skill when the visual surface has to become durable project memory
rather than a one-off diagram.

The contract is:

- `visual-corpus-curator` decides what the corpus is, what a capture contains,
  and what views should exist
- `context-spine` keeps the corpus aligned with repo-local memory, durable
  notes, and evidence-backed truth
- `memory-promotion` helps decide when a rolling note, evidence set, or diagram
  should become a normalized capture instead
- existing `.agent/diagrams/` explainers can be source evidence, but the
  curated corpus lives under `meta/visual-corpus/`

If you find yourself writing a long HTML page before the capture schema exists,
stop and build the manifest first.

## Good Default Workflow

For a new corpus:

1. create the capture directory structure
2. create the first normalized capture
3. create the scope catalog
4. generate one capture page
5. generate the scope index
6. only then add compare or trend views

For an existing corpus:

1. add a new capture
2. update the catalog
3. regenerate the affected index and trend pages
4. optionally generate a compare page against the previous capture

## Output Contract

When asked to use this skill, return:

- `CORPUS_SCOPE:`
- `CAPTURE_GRANULARITY:`
- `SOURCE_EVIDENCE:`
- `MANIFESTS_TO_CREATE_OR_UPDATE:`
- `VIEWS_TO_GENERATE:`
- `COMPARABILITY_WARNINGS:`
- `NEXT_ACTIONS:`

When generating artifacts, always report:

- exact manifest paths
- exact generated HTML paths
- what was inferred vs directly evidenced

## Companion Skills

- pair with `context-spine`
  when the corpus should become part of durable project memory
- pair with `memory-promotion`
  when deciding which rolling notes deserve promotion into captures
- pair with a runtime `visual-explainer`
  when rendering the final HTML pages
- pair with a runtime retrieval skill such as `qmd-retrieval`
  when you need to hydrate the corpus from existing notes or evidence

## References

- `references/capture-schema.md`
- `references/view-models.md`
- `../context-spine/SKILL.md`
- `../memory-promotion/SKILL.md`
- `../../../../docs/runbooks/visual-explainers.md`
- `../../../../docs/runbooks/memory-retention.md`
