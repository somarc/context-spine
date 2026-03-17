<p align="center">
  <img src="./docs/assets/context-spine-logo.jpg" alt="Context Spine logo" width="340">
</p>

<p align="center">
  <strong>Context Spine</strong><br>
  Make a software project understandable again after time, handoff, or context loss.
</p>

<p align="center">
  <img alt="status" src="https://img.shields.io/badge/status-active-0f766e?style=for-the-badge">
  <img alt="memory" src="https://img.shields.io/badge/memory-repo--local-1d4ed8?style=for-the-badge">
  <img alt="retrieval" src="https://img.shields.io/badge/retrieval-QMD--first-7c3aed?style=for-the-badge">
  <img alt="skills" src="https://img.shields.io/badge/skills-context--spine_%7C_principal--engineer--review-374151?style=for-the-badge">
</p>

Most repos are easy to run and hard to re-understand.

`Context Spine` is the missing reading path for a software project. It adds a small memory system next to the code so a person or agent can answer the basic questions fast:

- what this repo is
- what matters right now
- what changed
- what was actually verified
- where to look next

If you have ever reopened a project and thought "I know we figured this out already, but where is the actual truth?", this is for that moment.

It is not a product scaffold. It is the working memory spine that sits next to the code and keeps the project legible under growth, handoff, and context resets.

## You Probably Want This If

- restarting a project after a week costs real time
- handoffs depend on one person explaining everything live
- the truth is split across code, docs, notes, and command output
- agents keep rediscovering context your team already had once

## You Probably Do Not Need This If

- the repo is short-lived and nobody will revisit it
- the system is small enough that a single README already keeps it legible
- you do not care about durable handoff, retrieval, or evidence trails

## What You Actually Get

- a baseline note that explains the repo in human terms
- session notes that let work resume without a recap meeting
- a hot-memory index that points to what to open first right now
- a generated memory-state JSON and HTML pair for machine query plus fast visual re-anchoring
- a native-style `context:query` / `context:rehydrate` pair that emits compact JSON packets for restart-safe memory access
- explicit `context:promote` / `context:invalidate` commands that make reconciliation durable instead of prompt-local
- recent command/run history surfaced next to memory so verification does not disappear into terminal scrollback
- optional high-signal events so meaningful edit bursts, retrieval passes, and decisions can be captured without logging everything
- retrieval plumbing so those notes stay searchable instead of forgotten
- a place to tie decisions back to code, tests, commands, and docs

The point is not "more notes." The point is a repo that can explain itself again.

## 60-Second Tour

| Open this | Why it matters |
| --- | --- |
| `meta/context-spine/spine-notes-*.md` | The stable explanation of what the repo is and how to read it |
| `meta/context-spine/sessions/` | The current thread of work and what changed recently |
| `meta/context-spine/hot-memory-index.md` | The working set for today, not just a file dump |
| `source_of_truth` files named in the baseline | The code and docs you should actually trust |
| `docs/adr/`, `docs/runbooks/`, `.agent/diagrams/` | Durable decisions, repeatable operations, and visual system shape |

That is the product. The scripts and QMD integration exist to keep that reading path current.

## First Useful Workflow

1. Run `npm run context:setup`.
2. Open the baseline note and `meta/context-spine/hot-memory-index.md`.
3. Create a session note with `npm run context:session` before meaningful work.
4. Refresh retrieval with `npm run context:refresh` after notes or docs change.

If that loop already sounds right, the rest of this README is mainly installation detail and extension points.

## Where It Helps

| Scenario | What they add | What they get |
| --- | --- | --- |
| Existing repo cleanup | `meta/context-spine/`, `scripts/context-spine/`, one baseline note | Faster restarts and cleaner handoffs |
| Agent-heavy repo | `.pi/skills/`, evidence packs, bounded delegation | Better retrieval and less prompt soup |
| Deep technical system | ADRs, runbooks, diagrams, durable notes | Architectural shape that stays legible |

If you only want the one-line version:

`Context Spine` turns "project knowledge" from vague memory into a set of files and entrypoints people can actually reopen and trust.

Generated aids stay deliberately lightweight: they are regenerated locally, validated, and promoted into place only when the new artifact is structurally sound. If regeneration fails, the active artifact stays in place as the last-known-good reading surface.

The goal is simple:

- lower the cost of getting a new project legible
- keep delivered behavior, documented intent, and trusted evidence connected
- make future sessions start from retrieval instead of rediscovery

## How It Changes Day To Day Work

Context Spine is for normal project work, not just agent workflows.

People use it to:

- onboard faster with one baseline note and one recent session note
- hand off work without a long recap call
- capture decisions with code, test, and command evidence
- keep operational knowledge and architecture understanding easy to retrieve
- give agents a better project memory when agents are part of the workflow

Read the plain-language guide in [docs/runbooks/how-to-use-context-spine.md](./docs/runbooks/how-to-use-context-spine.md).

## What It Includes

- repo-local working memory under `meta/context-spine/`
- bootstrap and retrieval scripts under `scripts/context-spine/`
- a versioned runtime manifest under `scripts/context-spine/runtime-manifest.json`
- candidate-first promotion for generated aids so failed refreshes do not overwrite the active reading path
- evidence-pack discipline for delegated work under `scripts/delegation/`
- a generic agent constitution in [AGENTS.md](./AGENTS.md)
- a visual explainer surface under `.agent/diagrams/`
- starter ADRs, runbooks, and durable-note templates
- bundled Codex skill sources under [`.pi/skills/`](./.pi/skills/), including `context-spine` and `principal-engineer-review`
- optional extension points under `.pi/`
- structured run records under `meta/context-spine/runs/` for doctor, rollout, upgrade, and related maintenance commands
- structured machine-memory records under `meta/context-spine/records/` plus a generated `context:state` view

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

The shortest useful path uses the `npm run context:*` wrappers:

1. Read the prerequisites in [docs/runbooks/prerequisites.md](./docs/runbooks/prerequisites.md).
2. Run `npm run context:setup`.
3. Open the repo baseline `meta/context-spine/spine-notes-*.md` file.
4. Use [meta/context-spine/hot-memory-index.md](./meta/context-spine/hot-memory-index.md) as the current working set.
5. Create a session note with `npm run context:session`.
6. Refresh retrieval with `npm run context:refresh` when notes or docs change.
7. Validate the operating contract with `npm run context:verify`.
8. Generate the current machine and visual memory summary with `npm run context:state` when you want the layered state in one place.
9. Emit a restart packet with `npm run context:rehydrate` or the fuller runtime view with `npm run context:query` when an external runtime needs current memory without taking over orchestration.
10. Record durable reconciliation with `npm run context:promote` or `npm run context:invalidate` after you update the authoritative files.

Useful next steps:

- record observations with [scripts/context-spine/mem-log.py](./scripts/context-spine/mem-log.py)
- capture a meaningful event with `npm run context:event -- --type decision --summary "..."` when work outside the `context:*` wrappers materially changes understanding
- read or create a visual explainer when a subsystem is easier to absorb visually
- keep one durable external note per major deep dive, audit, or execution baseline
- set repo policy explicitly in [meta/context-spine/context-spine.json](./meta/context-spine/context-spine.json)
- optionally install or sync the bundled Codex skills with `npm run context:skill:install` if you want `$context-spine` or `$principal-engineer-review` available globally
- pick a git tracking policy with `npm run context:gitignore -- --mode tracked` or `npm run context:gitignore -- --mode local`
- if you are updating an older install in another repo, run `python3 ./scripts/context-spine/upgrade.py --target /path/to/project`
- use `npm run context:init`, `npm run context:update`, and `npm run context:embed` only when you want the low-level retrieval primitives directly

Direct-script equivalents remain available:

- `bash ./scripts/context-spine/setup.sh`
- `bash ./scripts/context-spine/init-qmd.sh`
- `bash ./scripts/context-spine/bootstrap.sh`
- `bash ./scripts/context-spine/refresh.sh`
- `python3 ./scripts/context-spine/doctor.py`
- `python3 ./scripts/context-spine/configure-gitignore.py --mode tracked`
- `python3 ./scripts/context-spine/rollout.py --repos /path/to/repo-a /path/to/repo-b`
- `python3 ./scripts/context-spine/upgrade.py --target /path/to/project`
- `python3 ./scripts/context-spine/mem-session.py`
- `python3 ./scripts/context-spine/mem-score.py`
- `python3 ./scripts/context-spine/query.py`
- `python3 ./scripts/context-spine/rehydrate.py`
- `python3 ./scripts/context-spine/promote.py`
- `python3 ./scripts/context-spine/invalidate.py`
- `bash ./scripts/context-spine/qmd-refresh.sh --embed`
- `bash ./scripts/context-spine/install-codex-skill.sh`

## Explicit Config

`meta/context-spine/context-spine.json` is the repo-local contract for how Context Spine behaves in a given project.

Use it to declare:

- project name
- memory root
- preferred baseline file
- QMD collection names and default queries
- managed gitignore mode

Inspect the resolved runtime view with:

```bash
npm run context:config
```

## Drop Into An Existing Project

Read [docs/runbooks/project-drop-in.md](./docs/runbooks/project-drop-in.md).

If the project already has an older Context Spine install, use [docs/runbooks/upgrade-existing-project.md](./docs/runbooks/upgrade-existing-project.md) instead of treating it like a first install. The upgrade path is additive-first: it can copy missing standalone runtime/doc surfaces, but it should keep project-owned baseline names and merge shared entrypoints deliberately.

The short version:

- copy or vendor `meta/context-spine/`, `scripts/context-spine/`, `scripts/delegation/`, and `AGENTS.md`
- choose a gitignore mode immediately
- run `npm run context:setup`
- keep repo-local memory in the project repo
- keep durable notes in an external linked vault
- connect both through QMD or an equivalent retrieval layer
- do not wait for “perfect docs” before starting the loop

For the human workflow after installation, read [docs/runbooks/how-to-use-context-spine.md](./docs/runbooks/how-to-use-context-spine.md).

## Memory Lifecycle

Context Spine does not mean “commit every thought forever.”

The intended split is:

- durable: architecture, boundaries, baseline notes, ADRs, runbooks, curated evidence, selected diagrams
- rolling: active session notes and observations
- generated/local: retrieval indexes, hot-memory indexes, scorecards

Git tracking is still a repo policy decision:

- `tracked`
  Commit durable and rolling Context Spine memory. Ignore only generated/local aids.
- `local`
  Keep `meta/context-spine/` out of git and promote anything worth sharing into committed docs, ADRs, or other project-owned surfaces.

Read the formal policy in [docs/adr/0003-memory-retention-model.md](./docs/adr/0003-memory-retention-model.md) and the operating rule in [docs/runbooks/memory-retention.md](./docs/runbooks/memory-retention.md).

## Durable Note Conventions

Default recommendation:

- `spine-notes-context-spine.md` for the current repo baseline
- `spine-notes-<topic>.md` for curated synthesis
- explicit `as_of` dates
- explicit `source_of_truth`
- a `Sources` section with direct paths or `qmd://` links

If a project already has a naming convention, keep it. The loop matters more than the prefix.

## Verification

Use one command to prove the runtime contract still holds:

```bash
npm run context:verify
```

That now runs the stdlib test suite, doctor, scorecard generation, and bundled skill validation through a single managed runtime entrypoint. The result is captured as one structured verification run with git state, diff summary, and per-step outcomes.

When work happens outside the managed `context:*` wrappers, prefer sparse event capture instead of session-note sprawl:

```bash
npm run context:event -- --type edit-burst --summary "Refined memory-state HTML and added event stream support" --files scripts/context-spine/memory-state.py,scripts/context-spine/memory_events.py
```

If you want to prove the installed Codex skill copies still match the repo source, run:

```bash
npm run context:skill:verify-installed
```

## Prerequisites

Run these exact checks first if you plan to use the README's `npm run ...` workflow:

```bash
git --version
python3 --version
bash --version
node --version
npm --version
command -v qmd && qmd status
```

If you want the direct-script path instead of `npm`, the shorter check is:

```bash
git --version
python3 --version
bash --version
command -v qmd && qmd status
```

If `qmd` is missing, install it with the official command:

```bash
npm install -g @tobilu/qmd
# or
bun install -g @tobilu/qmd
```

On macOS, QMD's official requirements also call for:

```bash
brew install sqlite
```

Source: [docs/runbooks/prerequisites.md](./docs/runbooks/prerequisites.md), [QMD Quick Start](https://github.com/tobi/qmd#quick-start), [QMD Installation](https://github.com/tobi/qmd#installation), and [QMD Requirements](https://github.com/tobi/qmd#requirements).

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

For the detailed `.pi/` model, read [docs/runbooks/pi-extension-points.md](./docs/runbooks/pi-extension-points.md).

## E.L.O.N.

Once you start adding memory surfaces, it is easy to add ceremony that feels smart but does not help. Context Spine uses a simple doctrine to push back on that:

- **Evidence over aspiration**
- **Legibility over lore**
- **Optimize for utility x impact**
- **No blind inference**

Read the full doctrine in [docs/runbooks/elon-doctrine.md](./docs/runbooks/elon-doctrine.md).

For the harder evolution guardrails, read [docs/adr/0005-context-spine-design-compass.md](./docs/adr/0005-context-spine-design-compass.md). It defines the non-negotiable invariants, anti-goals, and the bar a native Codex memory surface would need to clear before it should replace or absorb this model.

For the fuller architecture direction, read [docs/adr/0006-native-codex-memory-direction.md](./docs/adr/0006-native-codex-memory-direction.md). It lays out how Context Spine could become universally useful as a Codex memory surface without turning into a control plane or a black-box memory product.
That direction assumes the memory can become more native and agent-centric internally, while the human-facing contract becomes simpler: the system should visually explain itself well.

## Codex Skills

This repo ships project-owned Codex skill sources under [`.pi/skills/`](./.pi/skills/), including:

- `context-spine`
  - memory bootstrap and repair
- `principal-engineer-review`
  - architectural oversight
- `context-spine-maintenance`
  - maintenance loop orchestration
- `memory-promotion`
  - deciding what recent work should become durable
- `multi-repo-rollout`
  - batch assessment of local repo installs
- `elon-doctrine`
  - judging whether a change is genuinely valuable or just more complexity

These skills are optional. Context Spine should still make sense and provide value to people even if no agent is involved.

- validate them with `npm run context:skill:validate`
- install or sync them into Codex with `npm run context:skill:install`
- see [docs/runbooks/codex-skill.md](./docs/runbooks/codex-skill.md) for the maintenance loop

If you maintain several local repos, use `npm run context:rollout -- --repos ...` and read [docs/runbooks/multi-repo-rollout.md](./docs/runbooks/multi-repo-rollout.md).

## Repository Status

This repository is the bootstrap itself. It should stay lean, generic, and evidence-oriented.
