# Project Drop-In Runbook

## Goal

Attach Context Spine to an existing project without waiting for a large reorganization.

The target can be:

- an embedded repo root
- a parent workspace root that coordinates child repos
- a light-touch linked child that keeps only a vertebra file

The target outcome is simple: a person joining the repo should be able to find the current baseline, the latest session, and the trusted operating docs without guessing.

If the target repo already has Context Spine surfaces, do not treat it like a first install. Use [upgrade-existing-project.md](./upgrade-existing-project.md) so you can add newer hygiene features without overwriting project-owned customizations.

## Choose The Shape First

Before copying files, decide whether this project should be:

- `embedded-repo`
  - full local Context Spine install
- `workspace-root`
  - full parent spine coordinating children
- `linked-child`
  - only `.context-spine.json`, with the parent workspace spine owning shared truth

If you want the smallest possible touch on an existing repo, choose `linked-child` and stop after creating the vertebra file.

Preferred command:

```bash
python3 ./scripts/context-spine/upgrade.py \
  --target /path/to/child-repo \
  --adopt-mode linked-child
```

See [project-space-modes.md](./project-space-modes.md) for the full comparison.

## Minimum Installation

For `embedded-repo` or `workspace-root`, copy or vendor these paths into the target repository:

- `AGENTS.md`
- `meta/context-spine/`
- `scripts/context-spine/`
- `scripts/delegation/`
- optional `.pi/`
- optional `.pi/skills/` if you want the repo to ship project-owned Codex skill sources too

If the target repo already has a `docs/` directory, add these authority surfaces too:

- `docs/README.md`
- `docs/archive/`
- `docs/drafts/`

Then set the repo-local contract in `meta/context-spine/context-spine.json` before people start relying on conventions:

- project name
- preferred baseline file
- QMD collection names
- gitignore mode
- project-space mode and child repo topology when the target is a parent workspace

## Fast Path

If the target repo includes `package.json`, the lean path is:

1. copy the required surfaces
2. choose the gitignore mode
3. run `npm run context:setup`
4. open the baseline note and hot-memory index

If the target repo does not use `npm`, run `bash ./scripts/context-spine/setup.sh` instead.

For a parent workspace root, set:

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

The parent workspace spine should own cross-repo truth, while each child repo can either keep its own repo-local spine or use a light-touch linked-child vertebra file.

For a light-touch linked child, create `.context-spine.json` at the project root:

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

That is enough to let the parent workspace spine classify and coordinate the child repo without vendoring the full runtime into the child.

## Git Tracking Mode

Choose the repo policy immediately after the drop-in:

- `tracked`
  Commit durable and rolling Context Spine memory. Use:
  `python3 ./scripts/context-spine/configure-gitignore.py --mode tracked`
- `local`
  Keep `meta/context-spine/` out of git and treat it as private repo-local working memory. Use:
  `python3 ./scripts/context-spine/configure-gitignore.py --mode local`

This only controls the managed Context Spine block in `.gitignore`.
It does not overwrite the rest of the repo's ignore rules.
If Context Spine files are already tracked, untrack them once with:
`git rm -r --cached meta/context-spine`

## Retrieval Wiring

Recommended QMD collections:

```bash
npm run context:setup
```

Optional manual equivalent:

```bash
qmd collection add /path/to/project/meta --name context-spine-meta --mask "**/*.md"
qmd collection add /path/to/project/docs --name project-docs --mask "**/*.md"
qmd collection add /path/to/external-vault --name project-vault --mask "**/*.md"
```

Use `npm run context:refresh` whenever durable notes or docs are added and you want lexical retrieval refreshed.
Use `npm run context:embed` when you want to attempt vector hydration explicitly.
Use `bash ./scripts/context-spine/qmd-refresh.sh --embed` only when you want the low-level direct script.

If the config names differ from the boilerplate defaults, keep `context-spine.json` authoritative and let the scripts read from it instead of hardcoding local variants.

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

Obsidian is a strong companion for this external layer, and Obsidian CLI is a useful optional adapter if you want command-line workflows around those notes. It is not required for a valid Context Spine install.

After the drop-in, classify memory immediately:

- durable: baseline notes, ADRs, runbooks, curated evidence, selected diagrams
- rolling: sessions and observations
- generated/local: `.qmd/`, hot-memory indexes, scorecards

If the repo is in `local` gitignore mode, treat `meta/context-spine/` as private working memory and promote anything that must be shared into committed docs or other durable surfaces.

Do not let the initial install imply that every future session artifact belongs in long-lived git history.

After installation, run `python3 ./scripts/context-spine/doctor.py` once so the repo starts with an explicit hygiene report instead of silent drift.
If the repo includes `package.json`, also run `npm run context:verify` once so the config, tests, bootstrap path, lexical retrieval, scorecard, and skill surfaces are validated together.

After installation, hand the team this reading order:

1. the baseline `spine-notes-*.md`
2. the latest session note
3. the session-start runbook
4. one visual explainer if the project is complex
