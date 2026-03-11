#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MEM_ROOT="${CONTEXT_SPINE_ROOT:-$ROOT/meta/context-spine}"
COLLECTION="${CONTEXT_SPINE_COLLECTION:-context-spine-meta}"
HOT_INDEX="$MEM_ROOT/hot-memory-index.md"
SESSIONS_DIR="$MEM_ROOT/sessions"

LOCAL_INDEX_DIR="$MEM_ROOT/.qmd"
LOCAL_INDEX_PATH="$LOCAL_INDEX_DIR/index.sqlite"
if [[ -z "${INDEX_PATH:-}" ]]; then
  mkdir -p "$LOCAL_INDEX_DIR"
  if [[ ! -f "$LOCAL_INDEX_PATH" ]]; then
    GLOBAL_CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}"
    GLOBAL_INDEX_PATH="$GLOBAL_CACHE_DIR/qmd/index.sqlite"
    if [[ -f "$GLOBAL_INDEX_PATH" ]]; then
      for suffix in "" "-shm" "-wal"; do
        if [[ -f "$GLOBAL_INDEX_PATH$suffix" ]]; then
          cp "$GLOBAL_INDEX_PATH$suffix" "$LOCAL_INDEX_DIR/" 2>/dev/null || true
        fi
      done
    fi
  fi
  export INDEX_PATH="$LOCAL_INDEX_PATH"
fi

if [[ -d "$MEM_ROOT" ]]; then
  python3 "$ROOT/scripts/context-spine/hot-memory.py" --root "$MEM_ROOT" --collection "$COLLECTION" >/dev/null 2>&1 || true
fi

echo "===== CONTEXT SPINE ====="
echo "Root: $ROOT"
echo "Memory root: $MEM_ROOT"
echo "Collection: $COLLECTION"
echo

echo "===== PREREQUISITES ====="
if command -v git >/dev/null 2>&1; then
  echo "Git: available"
else
  echo "Git: not found"
fi
if command -v python3 >/dev/null 2>&1; then
  echo "Python3: available"
else
  echo "Python3: not found"
fi
if command -v qmd >/dev/null 2>&1; then
  echo "QMD: available"
else
  echo "QMD: not found"
fi
echo

if [[ -f "$HOT_INDEX" ]]; then
  echo "===== HOT MEMORY ====="
  cat "$HOT_INDEX"
  echo
else
  echo "===== HOT MEMORY ====="
  echo "(no hot-memory index found at $HOT_INDEX)"
  echo
fi

echo "===== RECENT VISUAL EXPLAINERS ====="
recent_explainers="$(find "$ROOT/.agent/diagrams" -maxdepth 1 -type f \( -name '*.html' -o -name '*.svg' -o -name '*.png' \) ! -name 'README.md' -print0 2>/dev/null | xargs -0 ls -1t 2>/dev/null | head -n 5 || true)"
if [[ -n "$recent_explainers" ]]; then
  while IFS= read -r explainer; do
    [[ -n "$explainer" ]] || continue
    if stat_output="$(stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$explainer" 2>/dev/null)"; then
      echo "- $stat_output - $explainer"
    else
      echo "- $explainer"
    fi
  done <<< "$recent_explainers"
else
  echo "- No visual explainers found in $ROOT/.agent/diagrams"
fi
echo

LATEST_SESSION=""
if [[ -d "$SESSIONS_DIR" ]]; then
  LATEST_SESSION="$(ls -1 "$SESSIONS_DIR"/*-session.md 2>/dev/null | sort | tail -n 1 || true)"
fi

if [[ -n "$LATEST_SESSION" && -f "$LATEST_SESSION" ]]; then
  session_name="$(basename "$LATEST_SESSION")"
  session_date="${session_name:0:10}"
  session_age=""
  if [[ "$session_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    session_age="$(python3 - <<PY
import datetime as dt
try:
    d = dt.date.fromisoformat("$session_date")
    print((dt.date.today() - d).days)
except Exception:
    print("")
PY
)"
  fi
  echo "===== LATEST SESSION ====="
  if [[ -n "$session_age" ]]; then
    echo "FILE: $LATEST_SESSION (age: ${session_age}d)"
    if [[ "$session_age" -ge 2 ]]; then
      echo "NOTE: latest session summary is stale. Prefer creating a fresh one."
    fi
  else
    echo "FILE: $LATEST_SESSION"
  fi
  echo
  cat "$LATEST_SESSION"
  echo
else
  echo "===== LATEST SESSION ====="
  echo "(no session files found in $SESSIONS_DIR)"
  echo
fi

if [[ -x "$ROOT/scripts/context-spine/qmd-quick.sh" ]]; then
  "$ROOT/scripts/context-spine/qmd-quick.sh"
else
  echo "===== QMD QUICK SEARCH ====="
  echo "(qmd-quick.sh missing)"
fi

echo
echo "===== AGENT EXTENSIONS ====="
if [[ -d "$ROOT/.pi/skills" ]]; then
  skill_count="$(find "$ROOT/.pi/skills" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')"
  echo "Local skills: $skill_count"
else
  echo "Local skills: none"
fi
if command -v pi >/dev/null 2>&1; then
  echo "Pi CLI: available"
else
  echo "Pi CLI: not found"
fi
if command -v ollama >/dev/null 2>&1; then
  echo "Ollama: available"
else
  echo "Ollama: not found"
fi
if command -v tmux >/dev/null 2>&1; then
  echo "tmux: available"
else
  echo "tmux: not found"
fi

echo
echo "Quick start:"
echo "  scripts/context-spine/init-qmd.sh"
echo "  python3 scripts/context-spine/mem-session.py"
echo "  python3 scripts/context-spine/mem-log.py --summary \"<what changed>\""
echo "  python3 scripts/context-spine/mem-score.py"
