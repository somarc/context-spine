# ADR 0001: Context Spine Purpose

## Status

Accepted

## Context

Most agent-assisted projects accumulate context in ad hoc ways:

- terminal history
- scattered notes
- issue trackers
- chat logs
- incomplete docs

That produces storage, not operating memory.

## Decision

Use a lightweight intelligence layer in every serious project:

- repo-local memory for short-horizon continuity
- retrieval across repo and vault surfaces
- durable linked notes for long-horizon understanding
- evidence packs for delegated work

## Consequences

- a new session can rehydrate quickly
- the project remains legible under context resets
- durable notes become grounded in code and evidence instead of narrative confidence
- the system stays extensible because the interfaces are explicit
