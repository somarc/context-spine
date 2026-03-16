# Upgrade An Existing Project

## Goal

Move an older Context Spine install forward without overwriting project-owned memory, docs, or custom wiring.

The upgrade path is intentionally split:

- `safe additive`
  Files that can be added if missing without taking authority away from the target project.
- `merge review`
  Files that often need a human decision because the target repo may already have legitimate customizations.

## Fast Path

From the `context-spine` boilerplate repo:

```bash
python3 ./scripts/context-spine/upgrade.py --target /path/to/project
```

That writes a markdown report to:

```text
/path/to/project/meta/context-spine/upgrade-report.md
```

## Apply Only The Low-Risk Pieces

If you want to scaffold only the safe additive files:

```bash
python3 ./scripts/context-spine/upgrade.py --target /path/to/project --apply-safe
```

The script will only create missing files from this set:

- `docs/README.md`
- `docs/archive/README.md`
- `docs/drafts/README.md`
- `docs/runbooks/doctor.md`

It will not overwrite existing files.

## What Still Needs Human Review

These surfaces are called out for merge review rather than blind replacement:

- `.gitignore`
- `package.json`
- `scripts/context-spine/bootstrap.sh`
- `docs/runbooks/session-start.md`
- `docs/runbooks/how-to-use-context-spine.md`
- `docs/runbooks/project-drop-in.md`
- `meta/context-spine/spine-notes-context-spine.md`

Those files often carry repo-specific truth, commands, or reading paths.

## Recommended Upgrade Order

1. Run the upgrade report.
2. Apply the safe additive files if they are missing.
3. Review the merge-worthy files one by one.
4. Add any new wrapper commands manually if the target repo uses `npm run context:*`.
5. Run `context:doctor` in the target repo after the merge.

## Why This Is Safer

Older Context Spine installs usually fail in one of two ways:

- they are missing newer hygiene surfaces entirely
- they have project-owned customizations that should not be clobbered by a boilerplate sync

This upgrade path keeps those two concerns separate.

## Output

The report tells you:

- detected repo mode
- missing safe additive files
- safe additive files applied
- merge-review files that are missing
- merge-review files that are present but diverged from the current boilerplate
- additional notes such as dirty worktree status
