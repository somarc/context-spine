# Native Memory APIs

## Goal

Provide thin request/response memory APIs for external runtimes and local tools without turning Context Spine into a control plane.

The first two commands are:

- `context:query`
- `context:rehydrate`

They are runtime-friendly because they emit machine-readable JSON and read from existing Context Spine memory surfaces.
They do not introduce a daemon, scheduler, worker bus, or hidden runtime-owned memory store.

## Commands

Preferred wrappers:

```bash
npm run context:query -- --mode active-delivery
npm run context:rehydrate -- --mode active-delivery
```

Direct scripts:

```bash
python3 ./scripts/context-spine/query.py --mode active-delivery
python3 ./scripts/context-spine/rehydrate.py --mode active-delivery
```

Useful flags:

```bash
python3 ./scripts/context-spine/query.py --mode recovery --objective "Resume upgrade work"
python3 ./scripts/context-spine/rehydrate.py --mode active-delivery --limit 4
```

## Output Contracts

`context:query` emits `context-spine.query.v1` with:

- git snapshot
- active objective
- authoritative surfaces
- source hydration
- working set
- recent machine context
- stale or suspect truths
- critical path and next actions
- metacognitive check

`context:rehydrate` emits `context-spine.rehydrate.v1` with a smaller restart packet for external runtimes.

## Boundaries

- these commands summarize memory; they do not dispatch work
- they read file-backed truth and structured records; they do not create runtime-owned truth
- they may write normal run records for observability, but they do not require background processes
- if a caller needs worker orchestration, queues, tabs, cron, or webhook ownership, that belongs in an external runtime

## Why They Exist

The goal is to let a runtime ask:

- what matters right now
- which files are authoritative
- what recent evidence exists
- what is stale or risky

without scraping markdown ad hoc and without promoting Context Spine into a resident orchestration layer
