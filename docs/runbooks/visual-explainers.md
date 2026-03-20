# Visual Explainers

## Goal

Treat visual explainers as a first-class reading surface for complex project context.

## When To Use Them

Use a visual explainer when:

- a subsystem is easier to understand spatially than linearly
- a plan needs to be reviewed as a system rather than a list
- retrieved context is dense and cross-cutting
- a future session should be able to rehydrate quickly from one artifact

Use a visual corpus instead when:

- the visual surface needs immutable dated captures
- the reader needs compare or trend views over time
- the project wants a browsable atlas of ADRs, evidence packs, or progress
- the repo already has strong explainers, but they are becoming disjointed
- the HTML should be regenerated from normalized manifests instead of edited by
  hand

## Storage Convention

Store standalone explainers under:

- `.agent/diagrams/`

Preferred format:

- self-contained HTML

Store recurring corpora under:

- `meta/visual-corpus/`

Preferred shape:

- `captures/` for immutable manifests
- `catalogs/` for scope indexes
- `generated/` for regenerated HTML reading surfaces

## Pairing Rule

Every important explainer should point back to one of:

- a durable note
- a code path
- a test or command evidence trail

The explainer is not the source of truth. It is the reading surface.

For a visual corpus:

- manifests and catalogs are the durable contract
- generated HTML is the disposable reading surface
- the corpus should still point back to code, docs, or evidence

## Bootstrap Integration

`scripts/context-spine/bootstrap.sh` surfaces recent explainers alongside hot memory so they become part of normal project startup.

When the visual surface becomes a corpus rather than a single page, use the
bundled `visual-corpus-curator` skill to keep normalized manifests and
generated pages aligned.

## Minimum Standard

A strong explainer should answer:

- what the major layers are
- what the read loop is
- what the write loop is
- where the extension points are
- what the current risks or unknowns are
