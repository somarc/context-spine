# Visual Corpus

Use this directory when Context Spine explainers have become strong individually
but disjoint collectively.

The purpose of this surface is to curate accumulated explainers, evidence
packs, ADR visuals, or milestone visuals into a browsable atlas with
date-addressable captures and regenerated views.

## Contract

- `captures/`
  Immutable normalized manifests for one bounded time slice or work slice.
- `catalogs/`
  Scope-level indexes that define which captures belong together.
- `generated/`
  Regenerated HTML reading surfaces such as index, capture, compare, and trend
  pages.

## Source Of Truth

- manifests and catalogs are the durable contract
- generated HTML is disposable output
- every capture should point back to underlying evidence such as diagrams,
  notes, docs, git ranges, logs, or tests

## Typical Use

- curate `.agent/diagrams/` explainers into a project atlas
- build dated views of milestone or session progress
- compare adjacent explainers after a major refactor or decision shift
- expose trend views when a stable metric basis exists

Use the bundled `visual-corpus-curator` skill when creating or extending this
surface.
