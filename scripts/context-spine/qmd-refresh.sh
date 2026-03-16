#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
eval "$(python3 "$ROOT/scripts/context-spine/context-config.py" --repo-root "$ROOT" --format shell)"
MEM_ROOT="${CONTEXT_SPINE_ROOT:-$CONFIG_CONTEXT_SPINE_ROOT}"
LOCAL_INDEX_DIR="$MEM_ROOT/.qmd"
LOCAL_INDEX_PATH="$LOCAL_INDEX_DIR/index.sqlite"
RUN_EMBED=0

if [[ "${1:-}" == "--embed" ]]; then
  RUN_EMBED=1
fi

if ! command -v qmd >/dev/null 2>&1; then
  echo "qmd not found in PATH" >&2
  exit 1
fi

mkdir -p "$LOCAL_INDEX_DIR"
export INDEX_PATH="$LOCAL_INDEX_PATH"

bash "$ROOT/scripts/context-spine/init-qmd.sh" >/dev/null
qmd update

if [[ "$RUN_EMBED" -eq 1 ]]; then
  qmd embed
fi
