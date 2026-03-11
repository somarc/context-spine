# Context Spine

`Context Spine` is a reusable memory bootstrap for agent-assisted software projects.

It is not a product scaffold. It is an intelligence layer: a small, extensible system for turning code, tests, commands, and notes into durable project memory.

The goal is simple:

- lower the cost of getting a new project legible
- keep delivered behavior, documented intent, and trusted evidence connected
- make future sessions start from retrieval instead of rediscovery

## What It Includes

- repo-local working memory under `meta/context-spine/`
- bootstrap and retrieval scripts under `scripts/context-spine/`
- evidence-pack discipline for delegated work under `scripts/delegation/`
- a generic agent constitution in [AGENTS.md](./AGENTS.md)
- a visual explainer surface under `.agent/diagrams/`
- starter ADRs, runbooks, and durable-note templates
- optional extension points under `.pi/`

## Core Model

Context Spine is built around five layers:

1. live project truth
2. repo-local working memory
3. retrieval fabric
4. durable linked knowledge
5. bounded delegation with evidence

The system works when two loops exist at the same time:

- `read loop`: bootstrap -> hot memory -> retrieval -> source code
- `write loop`: code/tests/evidence -> synthesis note -> backlinks -> re-index

## Recommended Repo Shape

```text
<project-root>/
  AGENTS.md
  meta/
    context-spine/
  scripts/
    context-spine/
    delegation/
  docs/
    adr/
    runbooks/
    templates/
  .agent/
    diagrams/
  .pi/
    skills/
    prompts/
```

## Quick Start

1. Read the prerequisites in [docs/runbooks/prerequisites.md](./docs/runbooks/prerequisites.md).
2. Initialize collections with [scripts/context-spine/init-qmd.sh](./scripts/context-spine/init-qmd.sh).
3. Run [scripts/context-spine/bootstrap.sh](./scripts/context-spine/bootstrap.sh).
4. Create a session note with [scripts/context-spine/mem-session.py](./scripts/context-spine/mem-session.py).
5. Record observations with [scripts/context-spine/mem-log.py](./scripts/context-spine/mem-log.py).
6. Read or create a visual explainer when a subsystem is easier to absorb visually.
7. Keep one durable external note per major deep dive, audit, or execution baseline.
8. Refresh retrieval with `qmd update` and `qmd embed`.

## Drop Into An Existing Project

Read [docs/runbooks/project-drop-in.md](./docs/runbooks/project-drop-in.md).

The short version:

- copy or vendor `meta/context-spine/`, `scripts/context-spine/`, `scripts/delegation/`, and `AGENTS.md`
- keep repo-local memory in the project repo
- keep durable notes in an external linked vault
- connect both through QMD or an equivalent retrieval layer
- do not wait for “perfect docs” before starting the loop

## Durable Note Conventions

Default recommendation:

- `spine-notes-<topic>.md` for curated synthesis
- explicit `as_of` dates
- explicit `source_of_truth`
- a `Sources` section with direct paths or `qmd://` links

If a project already has a naming convention, keep it. The loop matters more than the prefix.

## Prerequisites

Context Spine stands on top of other tools instead of re-implementing them.

Required or strongly recommended:

- Git
- a POSIX shell
- Python 3
- `qmd` for retrieval
- an external durable note layer

Optional but high-value:

- local agent runtime extensions under `.pi/`
- Ollama or another local model backend
- tmux for bounded parallel work
- visual explainers as a normal reading surface

Read the fuller list in [docs/runbooks/prerequisites.md](./docs/runbooks/prerequisites.md).

## Visual Reading Surface

Visual explainers are first-class in Context Spine, not decoration.

- store them under `.agent/diagrams/`
- pair them with durable notes or evidence
- let bootstrap surface recent explainers alongside hot memory

Read the workflow in [docs/runbooks/visual-explainers.md](./docs/runbooks/visual-explainers.md).

## Extensibility

Context Spine is meant to grow.

Recommended extension points:

- `.pi/skills/` for project-local skills
- `.pi/prompts/` for reusable prompt scaffolds
- `scripts/delegation/` for alternate delegate runtimes
- `docs/adr/` for architectural decisions
- `docs/runbooks/` for operational memory
- `.agent/diagrams/` for visual explainers

The rule is: extend by adding adapters and conventions, not by replacing the memory loop.

## Repository Status

This repository is the bootstrap itself. It should stay lean, generic, and evidence-oriented.
