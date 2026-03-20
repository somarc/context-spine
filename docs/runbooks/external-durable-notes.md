# External Durable Notes

## Goal

Make the split between repo truth and long-horizon notes explicit.

The short version:

- keep shared project truth in the repo
- keep the deepest and longest-horizon notes wherever they can live well
- use QMD to recover both without pretending they are the same thing

## What Stays In The Repo

Use repo-local Context Spine surfaces for the things another engineer should be able to trust directly from the checkout:

- baseline notes
- ADRs
- runbooks
- evidence packs
- selected diagrams
- rolling sessions and observations

This is the shared operating map of the project.

## What Often Belongs Outside The Repo

Some notes are valuable, but too long-horizon, too personal, or too cross-cutting to belong in git history.

Good candidates for an external durable note system:

- deep research trails
- postmortem working notes
- execution baselines that span multiple repos
- design sketches and synthesis notes
- reusable operator heuristics
- long-lived learning notes

These are still real memory. They are just not always repo memory.

## Why Keep The Split

This split keeps Context Spine sharp:

- the repo stays legible instead of becoming a document dump
- shared truth stays easy to audit
- long-horizon notes stay durable without polluting repo history
- retrieval can still recover both layers when needed

## QMD's Job

QMD is not the persistence layer.

QMD is the retrieval fabric across persisted context.

That means:

- repo-local memory stays in repo files
- external durable notes stay in your note system
- QMD is what lets both show up in search and recovery

If QMD is available, it should feel like local search plus deep-context recall over the memory you already chose to keep.

## Obsidian And Obsidian CLI

Obsidian is a strong companion for the external durable-note layer because it is:

- linked
- searchable
- durable
- pleasant to use for long-form thinking

Obsidian CLI is optional.

Use it if you want command-line workflows for:

- creating or updating external notes
- searching a vault from the terminal
- automating note capture alongside repo work

Do not treat it as a core prerequisite for Context Spine.

Context Spine should remain valid even if a team uses:

- Obsidian
- plain markdown in another vault
- another linked note system entirely

## Recommended Working Model

1. Keep project truth in repo-owned Context Spine surfaces.
2. Keep deep, long-horizon notes outside the repo when they do not belong in git history.
3. Let QMD retrieve across both.
4. Promote only the parts that should become shared project truth.

## How To Add These Surfaces

Use this when you want external durable notes to augment the core spine instead
of compete with it.

### 1. Pick One External Durable-Note Home

Choose one place for long-horizon notes outside the repo.

The default Context Spine contract is now a project-scoped vault at:

- `~/vaults/<project>-context-spine`

Override `collections.vault_root` in `meta/context-spine/context-spine.json`
when a project needs a different home. Set `collections.vault_root` to `null`
only when you intentionally want no external durable-note layer.

- an Obsidian vault
- a plain markdown knowledge repo
- another linked note system with stable file paths

The main requirement is simple:

- notes stay durable
- notes stay searchable
- notes stay linkable

### 2. Keep The Core Spine In The Repo

Do not move the core reading path out of the project.

Keep these in the repo:

- baseline notes
- session notes
- ADRs
- runbooks
- evidence packs
- selected diagrams

This is the shared operating truth another engineer should be able to trust directly from the checkout.

### 3. Attach The External Layer To Retrieval

If you use QMD, add the external note root as another collection.

The default setup path already provisions the project-scoped vault and wires it
into repo-local QMD collections. Use the manual path only when you are binding a
different external root or repairing retrieval by hand.

Manual example:

```bash
qmd collection add /path/to/external-vault --name <project>-vault --mask "**/*.md"
```

If you want the repo-local config to carry that path, set the vault fields in `meta/context-spine/context-spine.json` and then rerun:

```bash
npm run context:setup
```

The outcome you want is:

- repo memory and external durable notes are both retrievable
- neither one pretends to replace the other

### 4. Use The External Layer For Depth, Not For Shared Operating Truth

Good augmentation surfaces:

- deep technical research
- exploratory design notes
- postmortem working notes
- multi-repo execution baselines
- reusable heuristics and mental models

Bad augmentation surfaces:

- the only copy of the repo baseline
- the only copy of critical runbooks
- operational truth that teammates need directly from the checkout

### 5. Link The Layers Deliberately

When external notes materially matter to the project:

- reference them from the repo baseline, session, or runbook
- add `qmd://` links when retrieval is available
- summarize the operationally important conclusion back into repo truth

This keeps recovery practical. A future operator should not need to rediscover the existence of the deeper note layer by accident.

### 6. Promote Shared Truth Back Into The Repo

When an external note stops being just depth and starts becoming shared operating truth, promote it.

Typical destinations:

- baseline note
- ADR
- runbook
- curated evidence pack
- visual explainer

External notes are allowed to stay richer than the repo copy. The repo only needs the part that should become shared truth.

### 7. Add Optional Tooling Only If It Helps

Obsidian CLI is a good optional companion if you want:

- command-line note creation
- scripted vault searches
- capture flows that pair repo work with external note updates

Context Spine provisions the vault on disk and keeps the contract tool-agnostic.
Obsidian CLI is the preferred operator surface when it is available, but the
vault remains valid plain-markdown storage even without it.

The safe rule is:

- QMD helps recover persisted context
- Obsidian CLI may help author persisted context
- Context Spine remains the substrate connecting both

## Minimal Augmentation Pattern

If you want the smallest useful add-on beyond the core spine:

1. keep the repo baseline and sessions in the repo
2. keep deep research notes in one external vault
3. add that vault to QMD
4. reference important external notes from the baseline or current session
5. promote only the shared operational conclusion back into repo truth

## Practical Test

Ask one question:

"If this note disappeared from the repo, would the project become harder to operate, or only harder to remember in depth?"

If it makes the project harder to operate, promote it into repo truth.

If it mainly preserves depth, synthesis, or long-horizon thinking, an external durable note system is often the better home.

## Sources

- [docs/adr/0003-memory-retention-model.md](../adr/0003-memory-retention-model.md)
- [docs/runbooks/project-drop-in.md](./project-drop-in.md)
- [docs/runbooks/prerequisites.md](./prerequisites.md)
- [meta/context-spine/spine-notes-context-spine.md](../../meta/context-spine/spine-notes-context-spine.md)
