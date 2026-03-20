# Capture Schema

Use this schema for normalized visual corpus captures.

The schema is intentionally simple and extensible. Add fields only when they
create real comparability or retrieval value.

## Required Shape

```json
{
  "id": "2026-03-20-oak-segment-consensus",
  "date": "2026-03-20",
  "scope": "oak-segment-consensus",
  "headline": "Coverage push through startup seams",
  "summary": "Short human-readable summary of the capture",
  "sources": [
    {
      "type": "git",
      "value": "6c4e13d437..12e220d637"
    },
    {
      "type": "file",
      "value": "/abs/path/to/doc.md"
    }
  ]
}
```

## Preferred Extended Shape

```json
{
  "id": "2026-03-20-oak-segment-consensus",
  "date": "2026-03-20",
  "scope": "oak-segment-consensus",
  "title": "Coverage Progress",
  "headline": "Coverage push through startup seams",
  "summary": "Focused coverage and refactor sprint against stable HTTP and startup surfaces.",
  "git_range": "6c4e13d437..12e220d637",
  "metric_basis": "focused-suite-jacoco",
  "stats": {
    "commit_slices": 32,
    "test_files_touched": 47,
    "test_insertions": 8321
  },
  "checkpoints": [
    {
      "label": "config/startup",
      "instruction": 23.8,
      "branch": 15.1,
      "suite": "focused"
    },
    {
      "label": "startup seams",
      "instruction": 31.2,
      "branch": 24.5,
      "suite": "focused"
    }
  ],
  "waves": [
    {
      "name": "Config and startup footholds",
      "commits": ["c3553f2e4f", "4099ecfaa8"],
      "summary": "Created first reliable seams into config and startup orchestration."
    }
  ],
  "top_surfaces": [
    {
      "name": "RequestRouterTest",
      "delta": 1374,
      "kind": "test"
    }
  ],
  "next_targets": [
    "GlobalStoreServer startup decomposition",
    "Aeron-first startup cleanup"
  ],
  "sources": [
    {
      "type": "git",
      "value": "6c4e13d437..12e220d637"
    },
    {
      "type": "file",
      "value": "/abs/path/to/supporting-doc.md"
    }
  ]
}
```

## Field Guidance

### `id`

Make it:

- stable
- human-readable
- unique within the corpus

Preferred pattern:

`<date>-<scope>`

### `date`

Use ISO format:

`YYYY-MM-DD`

If a capture spans a milestone instead of one day, still anchor it to the date
it was produced and add milestone metadata separately.

### `scope`

Keep scope stable across comparable captures.

Examples:

- `oak-segment-consensus`
- `oak-chain-coverage`
- `adr-atlas`
- `startup-cleanup`

### `metric_basis`

This field is critical when metrics may not be comparable.

Examples:

- `focused-suite-jacoco`
- `full-module-jacoco`
- `manual-curated-progress`

If the metric basis changes between captures, mark it explicitly and surface a
warning in compare or trend views.

### `checkpoints`

Use this when the work has meaningful intermediate snapshots during one capture.

Each checkpoint should be:

- named
- ordered
- based on a stable metric definition

### `waves`

Use this when many commits belong to a smaller number of coherent moves.

This is the preferred way to avoid giant commit lists in the HTML.

### `sources`

Always include enough evidence to rebuild trust later.

Recommended source types:

- `git`
- `file`
- `log`
- `url`
- `note`

## Comparability Rules

Two captures are only directly comparable when:

- scope is the same
- metric basis is the same
- the measurement semantics are the same

If any of those fail, the compare view must call that out.

## Minimal Catalog Shape

Each scope should also have a small catalog file:

```json
{
  "scope": "oak-segment-consensus",
  "title": "Oak Segment Consensus Coverage Atlas",
  "captures": [
    "2026-03-20-oak-segment-consensus",
    "2026-03-27-oak-segment-consensus"
  ]
}
```
