# Project Drop-In Runbook

## Goal

Attach Context Spine to an existing project without waiting for a large reorganization.

## Minimum Installation

Copy or vendor these paths into the target repository:

- `AGENTS.md`
- `meta/context-spine/`
- `scripts/context-spine/`
- `scripts/delegation/`
- optional `.pi/`

## Retrieval Wiring

Recommended QMD collections:

```bash
scripts/context-spine/init-qmd.sh
```

Optional manual equivalent:

```bash
qmd collection add /path/to/project/meta --name context-spine-meta --mask "**/*.md"
qmd collection add /path/to/project/docs --name project-docs --mask "**/*.md"
qmd collection add /path/to/external-vault --name project-vault --mask "**/*.md"
```

Use `bash ./scripts/context-spine/qmd-refresh.sh --embed` whenever durable notes or docs are added.

## Durable Knowledge

Keep long-horizon notes outside the repo when practical.

Recommended note types:

- hub notes
- execution baselines
- deep dives
- audits
- runbooks

## First Week Recommendation

- day 1: install the bootstrap and session tools
- day 2: create the first durable hub note
- day 3: log at least one observation per real work session
- day 4: add the first evidence pack from a delegated or bounded investigation
- day 5: review the memory scorecard and fix the weakest loop
