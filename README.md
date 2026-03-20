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
  <img alt="contract" src="https://img.shields.io/badge/contract-agent--native-0f766e?style=for-the-badge">
  <img alt="interface" src="https://img.shields.io/badge/interface-visual--first-b45309?style=for-the-badge">
  <img alt="skills" src="https://img.shields.io/badge/skills-context--spine_%7C_principal--engineer--review-374151?style=for-the-badge">
</p>

Most repos can run. Few can explain themselves.

`Context Spine` is a small memory substrate you add to a project so a person or agent can reopen the repo or workspace and quickly answer:

- what this repo or workspace is
- what matters now
- what changed
- what was actually verified
- where to look next

If you keep paying a "what were we doing?" tax every time a project goes cold, this is for that problem.

It is not a product scaffold and it is not a control plane. It is a file-backed memory layer that makes a repo or a non-git parent workspace legible again.

> Human wink: yes, there are a lot of docs in here. Most of the docs beyond the READMEs are really for agents, not for meatspace readers. If you are human, take the visual lane: open the explainers in `.agent/diagrams/`.

## Why People Install It

- Restarts get faster because the reading path is explicit.
- Handoffs get easier because decisions stop living only in chat or terminal scrollback.
- Agents get a better starting context, but humans still get a readable project.
- The truth gets tied back to code, docs, tests, and commands instead of vague recall.

## What You Get

- one baseline note that explains the repo or workspace in plain language
- one rolling session trail for current work
- one hot-memory index that says what to open first
- one place to connect decisions back to evidence
- one way to keep long-horizon deep notes outside the repo without losing them
- one visual reading surface for humans
- one explicit promote / invalidate path when project truth changes

The point is not "more notes." The point is less rediscovery.

## Human Shortcut

If you are human:

- read the README files
- open the visual explainers
- use the evidence trail only when you want to inspect the receipts

If you are an agent:

- the deeper runbooks, ADRs, session notes, and durable memory surfaces are your operating substrate

## Open These First

| Open this | Why it matters |
| --- | --- |
| `meta/context-spine/spine-notes-*.md` | Stable explanation of the repo and how to read it |
| `meta/context-spine/hot-memory-index.md` | Current working set |
| `meta/context-spine/sessions/` | Current thread of work and latest verified understanding |
| `source_of_truth` files named in the baseline | Code and docs the repo says to trust |
| `docs/adr/`, `docs/runbooks/`, `.agent/diagrams/` | Durable decisions, repeatable operations, and visual system shape |

That reading path is the product. The scripts and retrieval surfaces exist to keep it current.

## Project Space Modes

Context Spine should support three clear shapes:

- `embedded-repo`
  A repo owns a full local spine under `meta/context-spine/` plus the runtime scripts.
- `workspace-root`
  A parent workspace owns a full top-level spine under `meta/context-spine/` and coordinates child repos.
- `linked-child`
  A project keeps only a light-touch vertebra file, `.context-spine.json`, that points back to the parent workspace spine.

Those are the internal topology modes. The natural reading labels are:

- `meta spine`
  the broadest workspace intelligence over the whole subtree
- `project spine`
  a nested workspace intelligence layer for one major project space
- `repo spine`
  a repo that owns its own local Context Spine truth
- `repo vertebra`
  a light-touch child repo that points upward instead of carrying a full local spine

Use `workspace-root` when you need the parent spine to own cross-repo truth:

- active objective
- topology and canonical child repo list
- shared ADR index
- visual corpus
- replay timeline
- cross-repo working set

Keep code evidence, sessions, baselines, runbooks, and generated local memory in an `embedded-repo` child spine only when that repo truly needs local durable memory.

Set the parent workspace mode in `meta/context-spine/context-spine.json`:

```json
{
  "project_space": {
    "mode": "workspace",
    "child_repos": [],
    "scan_roots": ["."],
    "scan_depth": 2
  }
}
```

If the parent folder has no `.git`, that is valid in `workspace-root` mode.

Use `linked-child` when you want the touch on an existing project to stay minimal:

```json
{
  "version": 1,
  "mode": "linked-child",
  "workspace_root": "..",
  "project_id": "oak-chain-docs",
  "project_name": "Oak Chain Docs",
  "truth_policy": "external"
}
```

That file should live at the project root as `.context-spine.json`.

If you want Context Spine to write that contract for you instead of hand-authoring it:

```bash
python3 ./scripts/context-spine/upgrade.py \
  --target /path/to/child-repo \
  --adopt-mode linked-child
```

If the child repo already lives under a workspace spine, the command auto-discovers the nearest parent workspace. Pass `--workspace-root /path/to/workspace-root` only when you need to override that.

The command writes only the light-touch vertebra contract. It does not scaffold a full local spine into the child repo.

Do not treat `linked-child` as a broken install. It is an intentional light-touch contract: the parent workspace spine owns shared memory, while the child repo stays mostly untouched.

## Hierarchical Example

Context Spine gets more natural when you treat the folder hierarchy itself as a hierarchy of scoped intelligence.

Using the current local shape as an example:

```text
aem-code/                     # top-level workspace spine
  meta/context-spine/
  OAK/                        # project-level workspace spine
    meta/context-spine/
    oak-chain-docs/           # repo-level vertebra or embedded repo spine
      .context-spine.json
    oak-block-collection/     # another child repo
      .context-spine.json
```

Read it like this:

- `aem-code/`
  The `meta spine`. It knows the overall landscape, major active efforts, shared topology, and the relationship between project spaces.
- `aem-code/OAK/`
  The `project spine`. It knows OAK-specific objectives, working set, decisions, and the topology of the versioned subprojects that make up OAK.
- `aem-code/OAK/<repo>/`
  Either a `repo spine` or a `repo vertebra`. Each child repo either owns repo-local truth directly or carries a light-touch vertebra contract that points back to the parent project spine.

The important rule is that intelligence should broaden as you move up and become more concrete as you move down.

- lower layers own fine-grained code evidence and local working memory
- middle layers own project coordination and shared truth across related repos
- top layers own the most meta view of the whole project space

That is what makes the memory surface feel organic instead of bolted on. The hierarchy already exists in the filesystem; Context Spine is making that hierarchy legible.

If you want the deeper comparison, read [project-space-modes.md](./docs/runbooks/project-space-modes.md).

## Try It In 5 Minutes

1. Run `npm run context:setup`.
2. Open the baseline note and `meta/context-spine/hot-memory-index.md`.
3. Create a session note with `npm run context:session`.
4. Run `npm run context:verify` when you want one explicit proof pass.
5. Ask one simple question: would this have saved time on my last restart, handoff, or audit?

If `qmd` is not installed yet, setup still works. You just will not get the local search and deep-context retrieval layer until you add it.
If `qmd` is installed, the default setup path refreshes lexical retrieval only. Run `npm run context:embed` when you want to attempt vector hydration explicitly.

## Agent Contract, Human Contract

For the agent:

- bootstrap into the working set
- read the baseline, latest session, hot memory, and named source-of-truth files
- prefer direct evidence from code, docs, tests, and commands when those sources are already local
- use retrieval when discovery is the bottleneck, not by default
- promote or invalidate durable memory explicitly when the project model changes

For the human:

- read the READMEs first
- get a visual explanation of what matters
- see the evidence trail
- follow source-of-truth references when needed
- treat the deeper docs as agent-grade operating surfaces unless you actually want the raw machinery

QMD is supported and useful here, but it is not the identity of the system. Context Spine should still make sense when one retrieval backend is absent, stale, or only partially hydrated.

## What It Is

- a memory substrate you add into a repo
- native-style memory for agents
- a visual reading path for humans
- file-backed and inspectable
- request/response, not runtime-owned

## What It Is Not

- not a control plane
- not a daemon or scheduler
- not a replacement for code, docs, tests, or git history
- not a transcript archive
- not prompt soup

## Core Commands

| Command | Use it for |
| --- | --- |
| `npm run context:setup` | First-time setup, lexical retrieval refresh, and bootstrap |
| `npm run context:bootstrap` | Reopen the repo and recover the working set |
| `npm run context:session` | Start a fresh session note for meaningful work |
| `npm run context:refresh` | Refresh lexical retrieval after notes or docs change |
| `npm run context:update` | Run the low-level lexical retrieval refresh directly |
| `npm run context:embed` | Attempt vector hydration explicitly |
| `npm run context:verify` | Run one managed proof pass across tests, bootstrap, lexical retrieval, and optional embed probing |
| `npm run context:doctor` | Audit memory hygiene and reading-surface health |
| `npm run context:state` | Generate machine summary plus visual memory state |
| `npm run context:promote` | Record a durable promotion into project truth |
| `npm run context:invalidate` | Record that prior memory is now stale or superseded |
| `npm run context:upgrade:pull-and-rollout -- --target /path/to/repo` | Update this Context Spine checkout from git, then run upgrade or rollout against a repo or workspace root |

Advanced retrieval primitives remain available as `context:init`, `context:update`, and `context:embed` when you need direct control.

## Add It To An Existing Repo

1. Choose the project-space shape first:
   full embedded repo, parent workspace root, or linked child.
2. For a full embedded repo, copy or vendor `meta/context-spine/`, `scripts/context-spine/`, and `AGENTS.md`.
3. Run `npm run context:setup`.
4. Create one baseline note and start using session notes for meaningful work.
5. Use bootstrap as the default way to reopen the repo.

For the lightest possible touch on an existing child repo, prefer:

```bash
python3 ./scripts/context-spine/upgrade.py \
  --target /path/to/child-repo \
  --adopt-mode linked-child
```

Use [docs/runbooks/project-drop-in.md](./docs/runbooks/project-drop-in.md) for a fresh install and [docs/runbooks/upgrade-existing-project.md](./docs/runbooks/upgrade-existing-project.md) if the repo already has an older Context Spine.

## Retrieval and QMD

- QMD is the default supported retrieval surface.
- It is the local search and retrieval fabric over the context you persist in repo files and linked notes.
- It is most useful for discovery, broad search, cross-note lookup, and recovering deep project context without rereading everything manually.
- It does not define the memory contract.
- Durable truth still lives in files, notes, ADRs, runbooks, and evidence; QMD is what makes that persisted context easy to recover.
- Lexical retrieval is the safe default path through `npm run context:refresh` and `npm run context:update`.
- Embeddings are an explicit acceleration layer through `npm run context:embed`, not a prerequisite for the core spine.
- `npm run context:verify` proves the core path and probes embed capability without pretending vector hydration is guaranteed.

Prerequisites and install notes live in [docs/runbooks/prerequisites.md](./docs/runbooks/prerequisites.md).

## Deep Notes and External Memory

Context Spine persists shared project truth in the repo.

That usually means:

- baselines
- ADRs
- runbooks
- evidence packs
- selected diagrams
- rolling sessions and observations

But the deepest and longest-horizon notes do not always belong in git.

Use an external durable note system for:

- deep dives
- research trails
- execution baselines
- cross-repo heuristics
- operator memory that outlives one codebase

QMD is what lets those external notes still participate in recovery and search.

Obsidian is a strong companion for this, and Obsidian CLI is a useful optional adapter if you want command-line workflows around external notes. It is not a core prerequisite for Context Spine itself.

## Visual Reading Surface

Visual explainers are first-class here, not decoration.

- store them under `.agent/diagrams/`
- pair them with durable notes or evidence
- use them when the system shape is easier to understand spatially than through prose

For humans, this is usually the right layer.
For agents, the explainers are a complement to the deeper operating surfaces, not a replacement for them.

If you want the best single visual first read, open [context-spine-field-guide-2026-03-19.html](./.agent/diagrams/context-spine-field-guide-2026-03-19.html).

## Read Next

Start here:

- [docs/runbooks/how-to-use-context-spine.md](./docs/runbooks/how-to-use-context-spine.md)
- [docs/runbooks/external-durable-notes.md](./docs/runbooks/external-durable-notes.md)
- [docs/runbooks/project-drop-in.md](./docs/runbooks/project-drop-in.md)
- [docs/runbooks/project-space-modes.md](./docs/runbooks/project-space-modes.md)
- [docs/runbooks/prerequisites.md](./docs/runbooks/prerequisites.md)
- [docs/runbooks/visual-explainers.md](./docs/runbooks/visual-explainers.md)

If you want the design boundaries:

- [docs/adr/0005-context-spine-design-compass.md](./docs/adr/0005-context-spine-design-compass.md)
- [docs/adr/0006-native-codex-memory-direction.md](./docs/adr/0006-native-codex-memory-direction.md)
- [docs/adr/0007-native-memory-apis-without-runtime-orchestration.md](./docs/adr/0007-native-memory-apis-without-runtime-orchestration.md)

If you want the optional Codex extension layer:

- [docs/runbooks/codex-skill.md](./docs/runbooks/codex-skill.md)
- [docs/runbooks/pi-extension-points.md](./docs/runbooks/pi-extension-points.md)

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
  .agent/
    diagrams/
  .pi/
    skills/
    prompts/
```

## Repository Status

This repository is the bootstrap itself. It should stay lean, generic, evidence-oriented, and easy to drop into real projects.
