---
title: Context Spine Memory
owner: codex
---

# Context Spine Memory

This directory is the repo-local memory layer.

It exists for short-horizon continuity and evidence capture close to the codebase.

## Layout

- `observations/` — timestamped observations, decisions, and questions
- `sessions/` — one session summary per working session
- `evidence-packs/` — distilled outputs from delegated jobs or investigations
- `hot-memory-index.md` — recently touched memory artifacts
- `memory-scorecard.md` — memory quality metrics

## Usage

Create a session summary:

```bash
python3 scripts/context-spine/mem-session.py
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

Run a bootstrap pass:

```bash
scripts/context-spine/init-qmd.sh
scripts/context-spine/bootstrap.sh
```
