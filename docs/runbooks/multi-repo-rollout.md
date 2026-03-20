# Multi Repo Rollout

## Goal

Assess or safely advance Context Spine across a small set of local repositories or workspace roots without turning rollout into a heavy deployment system.

Use this when you have a handful of active repos and want one answer to:

- which repos or workspace roots are current
- which repos are drifting
- which repos need upgrade-safe scaffolding
- which repos need human merge review

## Primary Command

Use the repo wrapper:

```bash
npm run context:rollout -- --repos /path/to/repo-a /path/to/repo-b
```

Direct script equivalent:

```bash
python3 ./scripts/context-spine/rollout.py --repos /path/to/repo-a /path/to/repo-b
```

If one of those paths is a workspace root in `project_space.mode=workspace`, rollout expands it into the parent workspace plus its child repos, including light-touch `linked-child` repos discovered through `.context-spine.json`.

## Safe Additive Rollout

If you want the rollout pass to apply safe additive files while scanning:

```bash
npm run context:rollout -- --apply-safe --repos /path/to/repo-a /path/to/repo-b
```

This only applies low-risk additive files that the upgrade path already classifies as safe.

Project-owned files still stay in merge review.

## Outputs

By default the script writes:

- `meta/context-spine/rollout-report.md`

Optional JSON output:

```bash
npm run context:rollout -- --repos /path/to/repo-a /path/to/repo-b --json-out ./meta/context-spine/rollout-report.json
```

## Reading The Report

For each target, look at:

- `scope`
  - `repo-root`, `workspace-root`, or `child-repo`
- `project mode`
  - `repo`, `workspace`, or `linked-child`
- `doctor`
  - pass / warn / fail counts
- `upgrade mode`
  - `missing`, `partial`, `existing`, or `linked-child`
- `safe additive gaps`
  - missing low-risk scaffolding
- `merge-review gaps`
  - files that should not be overwritten silently
- `recommendation`
  - the next action for that target

## Recommended Order

Work in this order:

1. repos with doctor failures
2. repos with missing or partial installs
3. repos with merge-review drift
4. repos with only safe additive gaps
5. linked-child repos whose parent spine is already healthy
6. repos already current

## Boundaries

- This is for a small local fleet, not a company-wide rollout system.
- Do not treat `--apply-safe` as permission to overwrite project-owned files.
- Run `context:doctor` again inside any repo that you materially changed during the rollout.
