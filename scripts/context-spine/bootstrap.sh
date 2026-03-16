#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
eval "$(python3 "$ROOT/scripts/context-spine/context-config.py" --repo-root "$ROOT" --format shell)"
MEM_ROOT="${CONTEXT_SPINE_ROOT:-$CONFIG_CONTEXT_SPINE_ROOT}"
COLLECTION="${CONTEXT_SPINE_COLLECTION:-$CONFIG_CONTEXT_SPINE_COLLECTION}"
DOCS_COLLECTION="${CONTEXT_SPINE_DOCS_COLLECTION:-$CONFIG_CONTEXT_SPINE_DOCS_COLLECTION}"
HOT_INDEX="$MEM_ROOT/hot-memory-index.md"
SESSIONS_DIR="$MEM_ROOT/sessions"
PACKAGE_JSON="$ROOT/package.json"

find_baseline_note() {
  local preferred_name="${CONTEXT_SPINE_BASELINE_PREFERRED:-$CONFIG_CONTEXT_SPINE_BASELINE_PREFERRED}"
  local preferred="$MEM_ROOT/$preferred_name"
  if [[ -f "$preferred" ]]; then
    echo "$preferred"
    return
  fi
  find "$MEM_ROOT" -maxdepth 1 -type f -name 'spine-notes-*.md' | sort | tail -n 1 || true
}

BASELINE_NOTE="$(find_baseline_note)"

preferred_session_cmd() {
  local project_name="${CONTEXT_SPINE_PROJECT:-$CONFIG_CONTEXT_SPINE_PROJECT}"
  if [[ -f "$PACKAGE_JSON" ]]; then
    echo "npm run context:session"
  else
    echo "python3 scripts/context-spine/mem-session.py --project $project_name"
  fi
}

file_age_days() {
  local path="$1"
  python3 - "$path" <<'PY'
import datetime as dt
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit(0)
mtime = dt.datetime.fromtimestamp(path.stat().st_mtime)
print((dt.datetime.now() - mtime).days)
PY
}

print_markdown_section() {
  local path="$1"
  local header="$2"
  awk -v header="$header" '
    $0 == header { capture=1; print; next }
    /^## / && capture { exit }
    capture { print }
  ' "$path"
}

print_hot_memory_preview() {
  if [[ ! -f "$HOT_INDEX" ]]; then
    echo "(no hot-memory index found at $HOT_INDEX)"
    return
  fi
  local generated_line=""
  generated_line="$(grep -m1 '^Generated:' "$HOT_INDEX" || true)"
  echo "File: $HOT_INDEX"
  if [[ -n "$generated_line" ]]; then
    echo "$generated_line"
  fi
  local section=""
  section="$(print_markdown_section "$HOT_INDEX" "## Start Here")"
  if [[ -n "$section" ]]; then
    echo
    printf '%s\n' "$section"
  fi
}

print_session_preview() {
  local session_path="$1"
  local summary=""
  local next_actions=""
  local current_state=""

  summary="$(print_markdown_section "$session_path" "## Summary")"
  next_actions="$(print_markdown_section "$session_path" "## Next Actions")"
  current_state="$(print_markdown_section "$session_path" "## Current State")"

  if [[ -n "$summary" ]]; then
    printf '%s\n' "$summary"
  elif [[ -n "$current_state" ]]; then
    printf '%s\n' "$current_state"
  fi

  if [[ -n "$next_actions" ]]; then
    echo
    printf '%s\n' "$next_actions"
  fi
}

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

LATEST_SESSION=""
if [[ -d "$SESSIONS_DIR" ]]; then
  LATEST_SESSION="$(ls -1 "$SESSIONS_DIR"/*-session.md 2>/dev/null | sort | tail -n 1 || true)"
fi

session_age=""
session_age_display=""
if [[ -n "$LATEST_SESSION" && -f "$LATEST_SESSION" ]]; then
  session_name="$(basename "$LATEST_SESSION")"
  session_date="${session_name:0:10}"
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
  if [[ -n "$session_age" ]]; then
    if [[ "$session_age" -lt 0 ]]; then
      session_age_display="future-dated vs local clock"
    else
      session_age_display="${session_age}d"
    fi
  fi
fi

hot_index_age=""
if [[ -f "$HOT_INDEX" ]]; then
  hot_index_age="$(file_age_days "$HOT_INDEX")"
fi

BOOTSTRAP_MODE="active"
if [[ -z "$BASELINE_NOTE" || ! -f "$HOT_INDEX" || ! -f "$LOCAL_INDEX_PATH" || -z "$LATEST_SESSION" ]]; then
  BOOTSTRAP_MODE="fresh"
elif [[ -n "$session_age" && "$session_age" -ge 2 ]]; then
  BOOTSTRAP_MODE="recovery"
elif [[ -n "$hot_index_age" && "$hot_index_age" -ge 2 ]]; then
  BOOTSTRAP_MODE="recovery"
fi

if [[ -d "$MEM_ROOT" ]]; then
  python3 "$ROOT/scripts/context-spine/hot-memory.py" --root "$MEM_ROOT" --collection "$COLLECTION" >/dev/null 2>&1 || true
fi

echo "===== CONTEXT SPINE ====="
echo "Root: $ROOT"
echo "Memory root: $MEM_ROOT"
echo "Collection: $COLLECTION"
echo "Mode: $BOOTSTRAP_MODE"
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
  echo "QMD collections: ensuring repo-local entries"
  bash "$ROOT/scripts/context-spine/init-qmd.sh" >/dev/null
  echo "Result: ready"
  if [[ -f "$PACKAGE_JSON" ]]; then
    echo "Lean path: npm run context:setup for first install, npm run context:refresh after note/doc changes."
  else
    echo "Lean path: bash ./scripts/context-spine/setup.sh for first install, bash ./scripts/context-spine/refresh.sh after note/doc changes."
  fi
else
  echo "QMD: not found"
fi
echo

echo "===== START HERE ====="
if [[ "$BOOTSTRAP_MODE" == "fresh" ]]; then
  starters=(
    "$ROOT/README.md"
    "$BASELINE_NOTE"
    "$ROOT/docs/runbooks/project-drop-in.md"
    "$ROOT/docs/runbooks/session-start.md"
  )
else
  starters=(
    "$BASELINE_NOTE"
    "$HOT_INDEX"
    "$LATEST_SESSION"
    "$ROOT/docs/runbooks/session-start.md"
  )
fi
for starter in "${starters[@]}"; do
  if [[ -f "$starter" ]]; then
    echo "- $starter"
  fi
done
echo

if [[ -f "$HOT_INDEX" ]]; then
  echo "===== HOT MEMORY ====="
  print_hot_memory_preview
  echo
else
  echo "===== HOT MEMORY ====="
  echo "(no hot-memory index found at $HOT_INDEX)"
  echo
fi

if [[ -n "$LATEST_SESSION" && -f "$LATEST_SESSION" ]]; then
  echo "===== LATEST SESSION ====="
  if [[ -n "$session_age" ]]; then
    echo "FILE: $LATEST_SESSION (age: ${session_age_display})"
    if [[ "$session_age" -lt 0 ]]; then
      echo "NOTE: latest session summary is dated ahead of the local clock. Treat it as current."
    elif [[ "$session_age" -ge 2 ]]; then
      echo "NOTE: latest session summary is stale. Prefer creating a fresh one."
    fi
  else
    echo "FILE: $LATEST_SESSION"
  fi
  echo
  print_session_preview "$LATEST_SESSION"
  echo
else
  echo "===== LATEST SESSION ====="
  echo "(no session files found in $SESSIONS_DIR)"
  echo "TIP: create one with $(preferred_session_cmd)"
  echo
fi

if [[ "$BOOTSTRAP_MODE" == "recovery" && -x "$ROOT/scripts/context-spine/qmd-quick.sh" ]]; then
  CONTEXT_SPINE_QMD_APPEND=0 \
  CONTEXT_SPINE_QMD_QUERY_BOOTSTRAP="${CONTEXT_SPINE_QMD_QUERY_BOOTSTRAP:-$CONFIG_CONTEXT_SPINE_QMD_QUERY_BOOTSTRAP}" \
  CONTEXT_SPINE_QMD_QUERY="" \
  CONTEXT_SPINE_QMD_QUERY_EXTRA="" \
  CONTEXT_SPINE_QMD_QUERY_SKILLS="" \
  "$ROOT/scripts/context-spine/qmd-quick.sh"
elif [[ "$BOOTSTRAP_MODE" == "fresh" ]]; then
  echo "===== QMD QUICK SEARCH ====="
  echo "Fresh-repo signal: skip deep retrieval until after context:setup and the first session note."
  echo "Tip: run scripts/context-spine/qmd-quick.sh when the repo has real memory to search."
else
  echo "===== QMD QUICK SEARCH ====="
  echo "Active-session mode: skipped deep QMD triage to keep bootstrap short."
  echo "Tip: run scripts/context-spine/qmd-quick.sh when you need a broader retrieval pass."
fi

echo
echo "===== AGENT EXTENSIONS ====="
skill_count="0"
pi_status="not found"
ollama_status="not found"
tmux_status="not found"
if [[ -d "$ROOT/.pi/skills" ]]; then
  skill_count="$(find "$ROOT/.pi/skills" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')"
fi
if command -v pi >/dev/null 2>&1; then
  pi_status="available"
fi
if command -v ollama >/dev/null 2>&1; then
  ollama_status="available"
fi
if command -v tmux >/dev/null 2>&1; then
  tmux_status="available"
fi
echo "Local skills: $skill_count | Pi CLI: $pi_status | Ollama: $ollama_status | tmux: $tmux_status"

echo
echo "Quick start:"
if [[ -f "$PACKAGE_JSON" ]]; then
  echo "  npm run context:setup"
  echo "  npm run context:bootstrap"
  echo "  npm run context:session"
  echo "  npm run context:refresh"
  echo "  npm run context:verify"
  echo
  echo "Advanced:"
  echo "  npm run context:doctor"
  echo "  npm run context:score"
  echo "  npm run context:init"
  echo "  npm run context:update"
  echo "  npm run context:embed"
  echo "  npm run context:upgrade -- --target /path/to/project"
  echo "  npm run context:skill:validate"
  echo "  npm run context:skill:install"
else
  echo "  bash ./scripts/context-spine/setup.sh"
  echo "  bash ./scripts/context-spine/bootstrap.sh"
  echo "  python3 scripts/context-spine/mem-session.py"
  echo "  bash ./scripts/context-spine/refresh.sh"
  echo
  echo "Advanced:"
  echo "  python3 scripts/context-spine/doctor.py"
  echo "  python3 scripts/context-spine/mem-score.py"
  echo "  bash ./scripts/context-spine/init-qmd.sh"
  echo "  bash ./scripts/context-spine/qmd-refresh.sh --embed"
  echo "  python3 scripts/context-spine/upgrade.py --target /path/to/project"
  echo "  bash ./scripts/context-spine/install-codex-skill.sh --validate-only"
  echo "  bash ./scripts/context-spine/install-codex-skill.sh"
fi
echo "  python3 scripts/context-spine/mem-log.py --summary \"<what changed>\""
