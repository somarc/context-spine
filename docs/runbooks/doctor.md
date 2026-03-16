# Context Doctor

## Goal

Run a fast hygiene pass that answers a higher-value question than "do memory files exist?"

The doctor checks whether Context Spine still points at live project truth:

- the repo has an explicit `context-spine.json` contract and it still loads cleanly
- the baseline note still exists and its source paths still resolve
- the latest session note is current enough to match recent repo work
- generated aids such as hot memory and the scorecard are not stale
- docs have clear authority boundaries
- visual explainers still have a stable home

## Command

Preferred wrapper:

```bash
npm run context:doctor
```

Direct script:

```bash
python3 ./scripts/context-spine/doctor.py
```

Useful flags:

```bash
python3 ./scripts/context-spine/doctor.py --strict
python3 ./scripts/context-spine/doctor.py --out ./meta/context-spine/doctor-report.md
python3 ./scripts/context-spine/doctor.py --json-out ./meta/context-spine/doctor-report.json
```

## What It Checks

### Baseline note

- baseline `spine-notes-*.md` exists
- `source_of_truth` and `Sources` paths still point to real files when they are local paths

### Explicit config

- `meta/context-spine/context-spine.json` exists and parses cleanly
- the configured memory root agrees with the runtime invocation
- preferred baseline and primary QMD collection are not left implicit

### Latest session

- a session note exists
- the latest session is not older than the latest non-memory git change
- the latest session does not still contain obvious template placeholders
- dirty work outside memory surfaces is visible

### Generated aids

- `hot-memory-index.md` exists and is reasonably fresh
- `memory-scorecard.md` exists and is reasonably fresh

### Docs governance

- `docs/README.md` exists when the repo has docs
- `docs/archive/` exists for retired material
- `docs/drafts/` exists for work-in-progress material
- multiple roadmap-like docs at `docs/` root are called out

### Visual explainer surface

- `.agent/diagrams/` exists
- at least one HTML explainer exists

## Status Meanings

- `PASS`
  The check is healthy enough to trust for normal work.
- `WARN`
  The check is usable, but something is drifting or underspecified.
- `FAIL`
  The repo is missing a required memory surface or source path.

Warnings should be treated as real work, not cosmetic cleanup. They usually mean the project is getting harder to trust under handoff or context reset.

## Output

The command prints a concise terminal summary and writes a markdown report to:

```text
meta/context-spine/doctor-report.md
```

That report is a local generated aid. It should usually stay out of git history.

## When To Run It

Run the doctor:

- after adding or reshaping major docs
- before declaring a phase or milestone complete
- after a long burst of work where notes may have drifted
- before onboarding or handing the repo to another person
- whenever the repo feels "harder to trust" than it should

## Relationship To Other Commands

- `context:bootstrap`
  Starts a session from high-signal artifacts.
- `context:score`
  Measures retrieval habit quality.
- `context:doctor`
  Measures whether the memory surfaces still map cleanly to current project truth.
- `context:upgrade`
  Plans or applies safe additive upgrades for older Context Spine installs in other repos.
