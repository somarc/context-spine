# Native Memory APIs

## Goal

Provide thin request/response memory APIs for external runtimes and local tools without turning Context Spine into a control plane.

The current command set is:

- `context:query`
- `context:rehydrate`
- `context:promote`
- `context:invalidate`

`query` and `rehydrate` are runtime-friendly because they emit machine-readable JSON and read from existing Context Spine memory surfaces.
`promote` and `invalidate` make reconciliation explicit by writing a file-backed trace plus a structured record and event.
None of them introduce a daemon, scheduler, worker bus, or hidden runtime-owned memory store.

## Commands

Preferred wrappers:

```bash
npm run context:query -- --mode active-delivery
npm run context:rehydrate -- --mode active-delivery
npm run context:promote -- --summary "Promoted ADR 0007" --kind adr --files docs/adr/0007-native-memory-apis-without-runtime-orchestration.md
npm run context:invalidate -- --summary "Superseded the old runtime-memory assumption" --subject "Runtime-owned global prompt memory as truth" --files docs/adr/0007-native-memory-apis-without-runtime-orchestration.md
```

Direct scripts:

```bash
python3 ./scripts/context-spine/query.py --mode active-delivery
python3 ./scripts/context-spine/rehydrate.py --mode active-delivery
python3 ./scripts/context-spine/promote.py --summary "Promoted ADR 0007" --kind adr --files docs/adr/0007-native-memory-apis-without-runtime-orchestration.md
python3 ./scripts/context-spine/invalidate.py --summary "Superseded old assumption" --subject "Runtime-owned global prompt memory as truth" --files docs/adr/0007-native-memory-apis-without-runtime-orchestration.md
```

Useful flags:

```bash
python3 ./scripts/context-spine/query.py --mode recovery --objective "Resume upgrade work"
python3 ./scripts/context-spine/rehydrate.py --mode active-delivery --limit 4
python3 ./scripts/context-spine/promote.py --summary "Promoted the runbook update" --kind runbook --files docs/runbooks/native-memory-apis.md --refs docs/adr/0007-native-memory-apis-without-runtime-orchestration.md
python3 ./scripts/context-spine/invalidate.py --summary "Invalidated stale bootstrap guidance" --subject "Old bootstrap assumption" --status superseded --replacement docs/runbooks/native-memory-apis.md --files docs/runbooks/native-memory-apis.md
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

`context:promote` and `context:invalidate` emit:

- updated durable file references, validated to stay inside the repo
- one structured machine record under `meta/context-spine/records/`
- one explicit high-signal event under `meta/context-spine/events/`
- one normal run record for observability

They do not edit the durable files for you. They record that you updated them and anchor the reconciliation trace to those files.

## Boundaries

- these commands summarize memory; they do not dispatch work
- they read file-backed truth and structured records; they do not create runtime-owned truth
- `promote` and `invalidate` require at least one repo file path so reconciliation stays attached to inspectable truth
- they may write normal run records for observability, but they do not require background processes
- if a caller needs worker orchestration, queues, tabs, cron, or webhook ownership, that belongs in an external runtime

## Why They Exist

The goal is to let a runtime ask:

- what matters right now
- which files are authoritative
- what recent evidence exists
- what is stale or risky

without scraping markdown ad hoc and without promoting Context Spine into a resident orchestration layer

The reconciliation half exists so the same runtime can also say:

- this durable surface was promoted
- this assumption was invalidated or superseded
- here are the files, evidence, and traces that justify that change
