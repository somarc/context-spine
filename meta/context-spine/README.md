---
title: Context Spine Memory
owner: codex
---

# Context Spine Memory

This directory is the repo-local memory layer.

It exists for short-horizon continuity and evidence capture close to the codebase.

Git tracking policy is configured separately:

- `tracked` mode commits durable and rolling memory here
- `local` mode ignores this directory from git and treats it as private repo-local context

Use three lifecycles here:

- durable: baseline `spine-notes-*.md` and curated evidence
- rolling: sessions and observations
- generated/local: hot-memory indexes, scorecards, and `.qmd/`

The repo-local runtime contract lives in `context-spine.json`.

## Layout

- `AGENTS.md` — subtree agent guidance for this memory layer
- `SKILLS.md` — local skill and command map for Context Spine work
- `spine-notes-context-spine.md` — durable current workspace baseline note
- `observations/` — rolling observations, decisions, and questions
- `sessions/` — rolling session summaries for active continuity
- `evidence-packs/` — curated outputs from delegated jobs or investigations
- `hot-memory-index.md` — generated local reading aid
- `memory-scorecard.md` — generated local health metric

## Usage

Create a session summary:

```bash
npm run context:session
```

Append an observation:

```bash
python3 scripts/context-spine/mem-log.py \
  --summary "Closed the queue durability gap" \
  --type decision \
  --truth verified \
  --evidence "tests: queue-smoke,code: queue_manager.py"
```

Refresh hot memory:

```bash
python3 scripts/context-spine/hot-memory.py
```

Score memory quality:

```bash
python3 scripts/context-spine/mem-score.py
```

Inspect the resolved runtime config:

```bash
npm run context:config
```

Run the full verification loop:

```bash
npm run context:verify
```

Run a bootstrap pass:

```bash
npm run context:init
npm run context:bootstrap
```

Set the managed `.gitignore` mode:

```bash
npm run context:gitignore -- --mode tracked
# or
npm run context:gitignore -- --mode local
```

Retention policy:

- architecture and boundaries should be promoted into `spine-notes-*.md`, ADRs, or runbooks
- sessions and observations should be rolled up and pruned over time
- generated local artifacts can be regenerated and should not be treated as long-lived history
