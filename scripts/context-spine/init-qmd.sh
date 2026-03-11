#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
META_NAME="${CONTEXT_SPINE_COLLECTION:-context-spine-meta}"
DOCS_NAME="${CONTEXT_SPINE_DOCS_COLLECTION:-project-docs}"
VAULT_NAME="${CONTEXT_SPINE_VAULT_COLLECTION:-project-vault}"
VAULT_ROOT="${CONTEXT_SPINE_VAULT_ROOT:-}"
MEM_ROOT="${CONTEXT_SPINE_ROOT:-$ROOT/meta/context-spine}"
LOCAL_INDEX_DIR="$MEM_ROOT/.qmd"
LOCAL_INDEX_PATH="$LOCAL_INDEX_DIR/index.sqlite"

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

ensure_collection() {
  local path="$1"
  local name="$2"
  local mask="$3"
  if collection_exists "$name"; then
    echo "Collection already present: $name"
    return 0
  fi
  echo "Adding collection: $name -> $path ($mask)"
  qmd collection add "$path" --name "$name" --mask "$mask"
}

ensure_collection "$ROOT/meta" "$META_NAME" "**/*.md"

if [[ -d "$ROOT/docs" ]]; then
  ensure_collection "$ROOT/docs" "$DOCS_NAME" "**/*.md"
fi

if [[ -n "$VAULT_ROOT" ]]; then
  ensure_collection "$VAULT_ROOT" "$VAULT_NAME" "**/*.md"
fi

echo
echo "Next steps:"
echo "  npm run context:update"
echo "  npm run context:embed"
