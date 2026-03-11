# Project Drop-In Runbook

## Goal

Attach Context Spine to an existing project without waiting for a large reorganization.

The target outcome is simple: a person joining the repo should be able to find the current baseline, the latest session, and the trusted operating docs without guessing.

## Minimum Installation

Copy or vendor these paths into the target repository:

- `AGENTS.md`
- `meta/context-spine/`
- `scripts/context-spine/`
- `scripts/delegation/`
- optional `.pi/`
- optional `.pi/skills/context-spine/` if you want the repo to ship the Codex skill source too

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

If the repo ships the bundled skill source, install it into Codex with:

```bash
bash ./scripts/context-spine/install-codex-skill.sh
```

## Durable Knowledge

Keep long-horizon notes outside the repo when practical.

Recommended note types:

- hub notes
- execution baselines
- deep dives
- audits
- runbooks

After the drop-in, classify memory immediately:

- durable: baseline notes, ADRs, runbooks, curated evidence, selected diagrams
- rolling: sessions and observations
- generated/local: `.qmd/`, hot-memory indexes, scorecards

Do not let the initial install imply that every future session artifact belongs in long-lived git history.

## First Week Recommendation

- day 1: install the bootstrap and session tools
- day 2: create the first durable hub note
- day 3: log at least one observation per real work session
- day 4: add the first evidence pack from a delegated or bounded investigation
- day 5: review the memory scorecard and fix the weakest loop

After installation, hand the team this reading order:

1. the baseline `spine-notes-*.md`
2. the latest session note
3. the session-start runbook
4. one visual explainer if the project is complex
