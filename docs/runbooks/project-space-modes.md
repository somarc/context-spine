# Project Space Modes

## Goal

Choose the lightest Context Spine shape that still keeps project truth inspectable.

The key principle is simple:

- keep full local spines where local durable truth is worth the coupling
- use a parent workspace spine for cross-repo truth
- use a tiny vertebra file when a project should stay mostly untouched

Internal mode names are still `repo`, `workspace`, and `linked-child`.
The natural reading labels are:

- `meta spine`
- `project spine`
- `repo spine`
- `repo vertebra`

## The Three Modes

### 1. Embedded Repo

Use this when one repo should own its own full spine.

The repo carries:

- `meta/context-spine/`
- `scripts/context-spine/`
- optional docs and wrappers

This is the right choice when the repo needs its own:

- baseline
- sessions
- repo-local runbooks
- repo-local evidence
- generated aids

Config:

```json
{
  "project_space": {
    "mode": "repo"
  }
}
```

### 2. Workspace Root

Use this when a parent folder should coordinate several child repos.

The workspace root carries the full spine and owns:

- active objective
- topology
- canonical child repo list
- shared ADR index
- visual corpus
- replay timeline
- cross-repo working set

Config:

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

The parent folder does not need its own `.git`.

### 3. Linked Child

Use this when an existing project should stay light-touch.

The project root carries only `.context-spine.json`:

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

This means:

- shared Context Spine truth lives in the parent workspace spine
- the child repo is intentionally not a full local install
- rollout and doctor should classify it as linked, not missing

Preferred adoption path:

```bash
python3 ./scripts/context-spine/upgrade.py \
  --target /path/to/child-repo \
  --adopt-mode linked-child
```

If the child already lives under a workspace spine, the nearest parent workspace is discovered automatically. Pass `--workspace-root` only when you need to override that default.

That command writes only `.context-spine.json`. It does not scaffold the full `meta/context-spine/` and `scripts/context-spine/` surfaces into the child repo.

## Truth Policy

`truth_policy` answers how much Context Spine truth the child repo owns itself.

- `external`
  The child relies on the parent workspace spine for shared Context Spine truth.
- `hybrid`
  The child may later gain some repo-local durable surfaces while still pointing at the parent workspace.
- `embedded`
  The child is expected to graduate to a full local spine.

Use `external` as the default.

## Which Mode To Choose

Choose `embedded-repo` when:

- the repo needs committed local baselines, sessions, runbooks, or evidence
- the repo should remain understandable even when copied away from its parent workspace

Choose `workspace-root` when:

- multiple repos form one active project space
- the shared truth is more important than repo-by-repo duplication

Choose `linked-child` when:

- the project already exists and you want minimal touch
- adding scripts, gitignore rules, and local memory surfaces would create more friction than value
- the parent workspace already owns the real Context Spine reading path

## Hierarchical Example

The intended model is not just multi-repo. It is hierarchical memory.

Using the existing local structure as an example:

```text
aem-code/
  meta/context-spine/
  OAK/
    meta/context-spine/
    oak-chain-docs/
      .context-spine.json
    oak-block-collection/
      .context-spine.json
```

Interpret that hierarchy this way:

- `aem-code/` is the `meta spine`.
  It should carry the most meta-aware understanding of the whole subtree: which project spaces exist, how they relate, what is active, and what cross-project patterns matter.
- `OAK/` is the `project spine` inside that larger workspace.
  It should carry OAK-specific truth: active objective, topology of the OAK subprojects, shared ADRs, visual corpus, replay timeline, and cross-repo working set.
- each repo under `OAK/` is either a `repo spine` or a `repo vertebra`.
  It should either own repo-local truth as an embedded repo spine or stay light-touch through `.context-spine.json` and defer broader context upward.

This is the key design rule:

- broader scope lives higher in the tree
- more localized truth lives lower in the tree
- each layer should summarize and coordinate the layers beneath it rather than duplicating everything

That is what makes Context Spine suitable for large project spaces. It is not forcing an artificial memory hierarchy on top of the folders. It is formalizing the hierarchy that already exists.

## Operational Rule

Treat `linked-child` as a first-class topology, not as an incomplete install.

That means:

- doctor validates the vertebra contract and parent workspace spine
- rollout reports it as `linked-child`
- upgrade does not try to scaffold a full local spine by default

When you explicitly request `--adopt-mode linked-child`, upgrade writes the inspectable vertebra contract and then evaluates the child in linked-child mode.

## Boundaries

- Do not hide the link in runtime-only state. The vertebra file must be inspectable.
- Prefer relative `workspace_root` paths when the child lives under the parent workspace.
- Do not use `linked-child` if the repo needs to carry its own durable Context Spine truth in git.
