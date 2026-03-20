#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
eval "$(python3 "$ROOT/scripts/context-spine/context-config.py" --repo-root "$ROOT" --format shell)"
PROJECT="${CONTEXT_SPINE_PROJECT:-$CONFIG_CONTEXT_SPINE_PROJECT}"
VAULT_NAME="${CONTEXT_SPINE_VAULT_COLLECTION:-$CONFIG_CONTEXT_SPINE_VAULT_COLLECTION}"
VAULT_ROOT="${CONTEXT_SPINE_VAULT_ROOT:-$CONFIG_CONTEXT_SPINE_VAULT_ROOT}"

if [[ -z "$VAULT_ROOT" ]]; then
  echo "External vault: disabled"
  exit 0
fi

mkdir -p \
  "$VAULT_ROOT/.obsidian" \
  "$VAULT_ROOT/00-inbox" \
  "$VAULT_ROOT/10-research" \
  "$VAULT_ROOT/20-architecture" \
  "$VAULT_ROOT/30-cross-repo" \
  "$VAULT_ROOT/90-heirlooms"

if [[ ! -f "$VAULT_ROOT/README.md" ]]; then
  cat > "$VAULT_ROOT/README.md" <<EOF
# ${PROJECT} Context Spine Vault

## Purpose

- hold long-horizon durable notes outside the repo checkout
- stay queryable through QMD alongside repo-local Context Spine memory
- promote shared operating truth back into the repo when it stops being just depth

## Layout

- \`00-inbox/\` for fast capture
- \`10-research/\` for deep investigations
- \`20-architecture/\` for system maps and mental models
- \`30-cross-repo/\` for workspace-level coordination notes
- \`90-heirlooms/\` for durable heuristics worth keeping

## Retrieval

- QMD collection: \`${VAULT_NAME}\`
- Vault root: \`${VAULT_ROOT}\`

Use Obsidian if you want a first-class linked-note UX.
Use the Obsidian CLI if you want command-line authoring and search once this vault is part of your normal note workflow.
EOF
fi

echo "External vault: ready"
echo "  collection: $VAULT_NAME"
echo "  root: $VAULT_ROOT"
if command -v obsidian >/dev/null 2>&1; then
  echo "  obsidian-cli: available"
else
  echo "  obsidian-cli: not found"
fi
