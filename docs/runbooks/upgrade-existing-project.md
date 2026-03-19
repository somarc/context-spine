# Upgrade An Existing Project

## Goal

Move an older Context Spine install forward without overwriting project-owned memory, docs, or custom wiring.

The upgrade path is intentionally split:

- `safe additive`
  Files that can be added if missing without taking authority away from the target project.
  In practice this includes new standalone runtime helpers and canonical docs.
- `merge review`
  Files that often need a human decision because the target repo may already have legitimate customizations.
  In practice this is the shared entrypoint layer: bootstrap, QMD wiring, session/score scripts, wrappers, and repo-specific runbooks.

Custom baseline names are valid.

If the target repo already has a project-owned `meta/context-spine/spine-notes-*.md` baseline, keep it.
Do not rename it to `spine-notes-context-spine.md` just to match the boilerplate repo.

## Fast Path

From the `context-spine` boilerplate repo:

```bash
python3 ./scripts/context-spine/upgrade.py --target /path/to/project
```

That writes a markdown report to:

```text
/path/to/project/meta/context-spine/upgrade-report.md
```

If you keep a maintained checkout of the boilerplate repo, the one-command path is:

```bash
npm run context:upgrade:pull-and-rollout -- --target /path/to/project --apply-safe
```

That does two things in order:

1. runs `git pull --ff-only` in the current Context Spine source checkout
2. runs `context:upgrade` against the target repo using that refreshed checkout as the source of truth

For several repos at once:

```bash
npm run context:upgrade:pull-and-rollout -- --repos /path/to/repo-a /path/to/repo-b --apply-safe
```

That switches to the rollout path automatically.

If you are invoking the wrapper from a vendored project copy instead of the maintained boilerplate checkout, point it at the canonical source repo explicitly:

```bash
python3 ./scripts/context-spine/pull-and-rollout.py \
  --source-root /path/to/context-spine \
  --target /path/to/project
```

## Apply Only The Low-Risk Pieces

If you want to scaffold only the safe additive files:

```bash
python3 ./scripts/context-spine/upgrade.py --target /path/to/project --apply-safe
```

The script will only create missing files from this set:

- authority docs such as `docs/README.md`, `docs/archive/README.md`, and `docs/drafts/README.md`
- the repo-local config surface `meta/context-spine/context-spine.json`
- canonical runbooks such as `doctor.md`, `how-to-use-context-spine.md`, `project-drop-in.md`, `upgrade-existing-project.md`, `elon-doctrine.md`, and related docs
- standalone runtime helpers such as `doctor.py`, `upgrade.py`, `hot-memory.py`, `rollout.py`, `qmd-quick.sh`, `mem-log.py`, `mem-search.py`, `context-config.py`, `context_config.py`, and Codex skill install helpers
- lean entrypoint helpers such as `setup.sh` and `refresh.sh`

It will not overwrite existing files.

## What Still Needs Human Review

These surfaces are called out for merge review rather than blind replacement:

- `.gitignore`
- `package.json`
- `scripts/context-spine/bootstrap.sh`
- `scripts/context-spine/init-qmd.sh`
- `scripts/context-spine/qmd-refresh.sh`
- `scripts/context-spine/mem-session.py`
- `scripts/context-spine/mem-score.py`
- `docs/runbooks/session-start.md`

Those files often carry repo-specific truth, commands, or reading paths.

## Recommended Upgrade Order

1. Run the upgrade report.
2. Pick the git tracking policy with `--gitignore-mode tracked` or `--gitignore-mode local`.
3. Apply the safe additive files if they are missing.
4. Review the shared entrypoint files one by one instead of overwriting project-owned behavior.
5. Add any new wrapper commands manually if the target repo uses `npm run context:*`, especially `context:setup` and `context:refresh`.
6. If you use `context:upgrade:pull-and-rollout`, keep the source checkout on the branch whose runtime you intend to propagate.
7. Merge `meta/context-spine/context-spine.json` deliberately if the target repo already has project-specific names or paths.
8. If the repo uses a custom baseline file name, keep it and merge the generic baseline detection changes into bootstrap and related docs.
9. Run `context:doctor` and `context:score` in the target repo after the merge.
10. If the target repo has the wrapper scripts, run `context:verify` so the upgrade is backed by tests and skill validation instead of file diff review alone.

## Gitignore Mode

The upgrade path supports a managed Context Spine block in `.gitignore`.

- `tracked`
  Commit durable and rolling memory. Ignore only generated/local Context Spine aids.
- `local`
  Ignore `meta/context-spine/` entirely and treat it as repo-local private memory.

Example:

```bash
python3 ./scripts/context-spine/upgrade.py --target /path/to/project --gitignore-mode local
```

This updates only the managed Context Spine block and leaves the rest of `.gitignore` alone.
If the repo already tracks `meta/context-spine/`, untrack it once with:
`git rm -r --cached meta/context-spine`

## Why This Is Safer

Older Context Spine installs usually fail in one of two ways:

- they are missing newer hygiene surfaces entirely
- they have project-owned customizations that should not be clobbered by a boilerplate sync

The common trap is treating a runtime upgrade like a full boilerplate replacement.
That works badly for repos that already have a legitimate baseline note name, project-specific session-start guidance, or wrapper commands tuned to local workflows.

This upgrade path keeps those two concerns separate.

## Output

The report tells you:

- detected repo mode
- missing safe additive files
- safe additive files applied
- merge-review files that are missing
- merge-review files that are present but diverged from the current boilerplate
- whether the explicit config file is missing or diverged
- additional notes such as dirty worktree status
