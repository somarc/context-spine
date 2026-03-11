# Visual Explainers

## Goal

Treat visual explainers as a first-class reading surface for complex project context.

## When To Use Them

Use a visual explainer when:

- a subsystem is easier to understand spatially than linearly
- a plan needs to be reviewed as a system rather than a list
- retrieved context is dense and cross-cutting
- a future session should be able to rehydrate quickly from one artifact

## Storage Convention

Store explainers under:

- `.agent/diagrams/`

Preferred format:

- self-contained HTML

## Pairing Rule

Every important explainer should point back to one of:

- a durable note
- a code path
- a test or command evidence trail

The explainer is not the source of truth. It is the reading surface.

## Bootstrap Integration

`scripts/context-spine/bootstrap.sh` surfaces recent explainers alongside hot memory so they become part of normal project startup.

## Minimum Standard

A strong explainer should answer:

- what the major layers are
- what the read loop is
- what the write loop is
- where the extension points are
- what the current risks or unknowns are
