#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
eval "$(python3 "$ROOT/scripts/context-spine/context-config.py" --repo-root "$ROOT" --format shell)"
PACKAGE_JSON="$ROOT/package.json"
META_NAME="${CONTEXT_SPINE_COLLECTION:-$CONFIG_CONTEXT_SPINE_COLLECTION}"
DOCS_NAME="${CONTEXT_SPINE_DOCS_COLLECTION:-$CONFIG_CONTEXT_SPINE_DOCS_COLLECTION}"
SKILLS_NAME="${CONTEXT_SPINE_SKILLS_COLLECTION:-$CONFIG_CONTEXT_SPINE_SKILLS_COLLECTION}"
SKILLS_ROOT="${CONTEXT_SPINE_SKILLS_ROOT:-$CONFIG_CONTEXT_SPINE_SKILLS_ROOT}"
VAULT_NAME="${CONTEXT_SPINE_VAULT_COLLECTION:-$CONFIG_CONTEXT_SPINE_VAULT_COLLECTION}"
VAULT_ROOT="${CONTEXT_SPINE_VAULT_ROOT:-$CONFIG_CONTEXT_SPINE_VAULT_ROOT}"
MEM_ROOT="${CONTEXT_SPINE_ROOT:-$CONFIG_CONTEXT_SPINE_ROOT}"
LOCAL_INDEX_DIR="$MEM_ROOT/.qmd"
LOCAL_INDEX_PATH="$LOCAL_INDEX_DIR/index.sqlite"

if [[ -n "$VAULT_ROOT" && -x "$ROOT/scripts/context-spine/init-vault.sh" ]]; then
  bash "$ROOT/scripts/context-spine/init-vault.sh" >/dev/null
fi

if ! command -v qmd >/dev/null 2>&1; then
  echo "qmd not found in PATH" >&2
  exit 1
fi

if [[ -z "${INDEX_PATH:-}" ]]; then
  mkdir -p "$LOCAL_INDEX_DIR"
  export INDEX_PATH="$LOCAL_INDEX_PATH"
fi

collection_exists() {
  local name="$1"
  qmd collection list | grep -Eq "^${name} \\(qmd://"
}

collection_info() {
  python3 - "$LOCAL_INDEX_PATH" "$1" <<'PY'
import sqlite3
import sys
from pathlib import Path

db_path = Path(sys.argv[1])
name = sys.argv[2]
if not db_path.exists():
    raise SystemExit(0)
conn = sqlite3.connect(db_path)
try:
    row = conn.execute(
        "SELECT path, pattern FROM store_collections WHERE name = ?",
        (name,),
    ).fetchone()
finally:
    conn.close()
if row:
    print(f"{row[0]}\t{row[1]}")
PY
}

ensure_collection() {
  local path="$1"
  local name="$2"
  local mask="$3"
  local info=""
  local actual_path=""
  local actual_pattern=""
  if collection_exists "$name"; then
    info="$(collection_info "$name")"
    if [[ -n "$info" ]]; then
      actual_path="${info%%$'\t'*}"
      actual_pattern="${info#*$'\t'}"
      if [[ "$actual_path" == "$path" && "$actual_pattern" == "$mask" ]]; then
        echo "Collection already present: $name"
        return 0
      fi
    fi
    echo "Rebinding collection: $name -> $path ($mask)"
    qmd collection remove "$name" >/dev/null
  else
    echo "Adding collection: $name -> $path ($mask)"
  fi
  qmd collection add "$path" --name "$name" --mask "$mask"
}

ensure_collection "$ROOT/meta" "$META_NAME" "**/*.md"

if [[ -d "$ROOT/docs" ]]; then
  ensure_collection "$ROOT/docs" "$DOCS_NAME" "**/*.md"
fi

if [[ -n "$SKILLS_ROOT" && -d "$SKILLS_ROOT" ]]; then
  ensure_collection "$SKILLS_ROOT" "$SKILLS_NAME" "**/*.md"
fi

if [[ -n "$VAULT_ROOT" ]]; then
  ensure_collection "$VAULT_ROOT" "$VAULT_NAME" "**/*.md"
fi

echo
echo "Next steps:"
if [[ -f "$PACKAGE_JSON" ]]; then
  echo "  npm run context:setup"
  echo "  npm run context:refresh"
else
  echo "  bash ./scripts/context-spine/setup.sh"
  echo "  bash ./scripts/context-spine/refresh.sh"
fi
